from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_ADAPTIVE_SUMMARY = Path("outputs/batch/adaptive_memory_summary.csv")
DEFAULT_MEMORY_AUDIT = Path("outputs/report_tables/agent_memory_belief_audit.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_memory_influence_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_memory_influence_audit.md")

SAFETY_BOUNDARY = (
    "closed simulation memory-influence audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "area",
    "mechanism",
    "evidence_files",
    "observed",
    "influence_status",
    "interpretation",
    "safety_boundary",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


def collect_rows(
    *,
    experiment_root: Path = DEFAULT_EXPERIMENT_ROOT,
    adaptive_summary_path: Path = DEFAULT_ADAPTIVE_SUMMARY,
    memory_audit_path: Path = DEFAULT_MEMORY_AUDIT,
) -> list[dict[str, str]]:
    aura_stats = cadence_stats(experiment_root, "AURA")
    aura_ml_stats = cadence_stats(experiment_root, "AURA-ML")
    tsra_stats = tsra_cooldown_stats(experiment_root)
    ml_window_stats = ml_window_stats_for_e7(experiment_root)
    adaptive_stats = adaptive_memory_stats(adaptive_summary_path)
    chain_stats = memory_chain_stats(memory_audit_path)

    rows = [
        row(
            check_id="MI01",
            area="AURA cadence memory",
            mechanism="AURA stores attack cadence and event budget state, then uses cooldown and max-event gates before selecting another simulated attack effect.",
            evidence_files="outputs/experiments/*/aura_decision_traces.jsonl",
            observed=(
                f"traces={aura_stats['trace_count']}; selected_attacks={aura_stats['selected_count']}; "
                f"cooldown_noops={aura_stats['cooldown_noop_count']}; "
                f"max_event_noops={aura_stats['max_event_noop_count']}; "
                f"belief_rows={aura_stats['belief_rows']}"
            ),
            ok=(
                aura_stats["selected_count"] > 0
                and aura_stats["cooldown_noop_count"] > 0
                and aura_stats["max_event_noop_count"] > 0
                and aura_stats["belief_rows"] > 0
            ),
            interpretation="Rule AURA is not stateless; prior attack timing and event budget suppress later actions.",
        ),
        row(
            check_id="MI02",
            area="AURA-ML cadence memory",
            mechanism="AURA-ML uses the same cadence memory gates while ranking candidates with the learned impact predictor.",
            evidence_files="outputs/experiments/*/aura_decision_traces.jsonl",
            observed=(
                f"traces={aura_ml_stats['trace_count']}; selected_attacks={aura_ml_stats['selected_count']}; "
                f"cooldown_noops={aura_ml_stats['cooldown_noop_count']}; "
                f"max_event_noops={aura_ml_stats['max_event_noop_count']}; "
                f"belief_rows={aura_ml_stats['belief_rows']}"
            ),
            ok=(
                aura_ml_stats["selected_count"] > 0
                and aura_ml_stats["cooldown_noop_count"] > 0
                and aura_ml_stats["max_event_noop_count"] > 0
                and aura_ml_stats["belief_rows"] > 0
            ),
            interpretation="ML ranking is bounded by memory-backed cadence and event-budget controls.",
        ),
        row(
            check_id="MI03",
            area="TSRA-R action cooldown memory",
            mechanism="TSRA-R stores action cooldowns in memory and blocks eligible actions until their cooldowns are ready.",
            evidence_files="outputs/experiments/*/tsra_r_decision_traces.jsonl",
            observed=(
                f"eligible_not_ready={format_counts(tsra_stats['eligible_not_ready'])}; "
                f"eligible_ready={format_counts(tsra_stats['eligible_ready'])}; "
                f"emitted_events={format_counts(tsra_stats['events'])}"
            ),
            ok=(
                sum(tsra_stats["eligible_not_ready"].values()) > 0
                and tsra_stats["eligible_ready"] == tsra_stats["events"]
                and {"priority_reroute", "video_throttle", "stale_badge", "pace_switch"}.issubset(
                    set(tsra_stats["eligible_not_ready"])
                )
            ),
            interpretation="Rule TSRA-R memory directly gates repeated defensive actions instead of emitting every eligible action every tick.",
        ),
        row(
            check_id="MI04",
            area="TSRA-R-ML active defense window memory",
            mechanism="TSRA-R-ML stores active_defense_until and last probability so a detector hit opens or maintains a bounded defense window.",
            evidence_files="outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl",
            observed=(
                f"opened_windows={ml_window_stats['opened_windows']}; "
                f"active_window_traces={ml_window_stats['active_window_traces']}; "
                f"active_window_noops={ml_window_stats['active_window_noops']}; "
                f"below_threshold_no_window={ml_window_stats['below_threshold_no_window']}"
            ),
            ok=(
                ml_window_stats["opened_windows"] > 0
                and ml_window_stats["active_window_traces"] >= ml_window_stats["opened_windows"]
                and ml_window_stats["active_window_noops"] > 0
                and ml_window_stats["below_threshold_no_window"] > 0
            ),
            interpretation="The ML defender uses memory to maintain a reactive window and to avoid unnecessary action when probability is below threshold outside the window.",
        ),
        row(
            check_id="MI05",
            area="Adaptive TSRA-R memory policy",
            mechanism="Adaptive TSRA-R uses recent memory windows to gate optional defenses and is compared against full TSRA-R over the repeated adaptive-memory experiment.",
            evidence_files="outputs/batch/adaptive_memory_summary.csv",
            observed=(
                f"delta_mission_impact_mean={fmt(adaptive_stats['delta_mission_impact_mean'])}; "
                f"delta_defense_count_mean={fmt(adaptive_stats['delta_defense_count_mean'])}; "
                f"delta_video_throttle_count_mean={fmt(adaptive_stats['delta_video_throttle_count_mean'])}; "
                f"delta_pace_switch_count_mean={fmt(adaptive_stats['delta_pace_switch_count_mean'])}"
            ),
            ok=(
                adaptive_stats["delta_mission_impact_mean"] < 0.0
                and adaptive_stats["delta_defense_count_mean"] < 0.0
                and adaptive_stats["delta_video_throttle_count_mean"] < 0.0
                and adaptive_stats["delta_pace_switch_count_mean"] < 0.0
            ),
            interpretation="Memory gating reduces average mission impact while also reducing optional defense load.",
        ),
        row(
            check_id="MI06",
            area="Memory chain integrity",
            mechanism="AgentMemory carries the previous selected action into the next DecisionTrace memory summary.",
            evidence_files="outputs/report_tables/agent_memory_belief_audit.csv",
            observed=(
                f"rows={chain_stats['rows']}; pass_rows={chain_stats['pass_rows']}; "
                f"min_last_selected_chain_match_rate={fmt(chain_stats['min_chain_rate'])}"
            ),
            ok=(
                chain_stats["rows"] == 9
                and chain_stats["pass_rows"] == 9
                and chain_stats["min_chain_rate"] == 1.0
            ),
            interpretation="The runtime memory chain is complete before higher-level memory influence claims are made.",
        ),
    ]
    return rows


def cadence_stats(experiment_root: Path, agent_name: str) -> dict[str, int]:
    stats = {
        "trace_count": 0,
        "selected_count": 0,
        "cooldown_noop_count": 0,
        "max_event_noop_count": 0,
        "belief_rows": 0,
    }
    for trace_path in sorted(experiment_root.glob("*/aura_decision_traces.jsonl")):
        for trace in read_jsonl(trace_path):
            if trace.get("agent") != agent_name:
                continue
            stats["trace_count"] += 1
            selected = trace.get("selected_action") or {}
            reason = str(trace.get("reason") or "")
            belief = (trace.get("memory") or {}).get("belief_state") or {}
            if selected.get("type") == "attack_event":
                stats["selected_count"] += 1
            if "attack cooldown active" in reason:
                stats["cooldown_noop_count"] += 1
            if "max_events" in reason:
                stats["max_event_noop_count"] += 1
            if {"event_count", "last_attack_time", "last_attack_type"}.issubset(belief):
                stats["belief_rows"] += 1
    return stats


def tsra_cooldown_stats(experiment_root: Path) -> dict[str, dict[str, int]]:
    stats = {
        "eligible_not_ready": {},
        "eligible_ready": {},
        "events": {},
    }
    for trace_path in sorted(experiment_root.glob("*/tsra_r_decision_traces.jsonl")):
        for trace in read_jsonl(trace_path):
            if trace.get("agent") != "TSRA-R":
                continue
            for candidate in trace.get("candidate_actions") or []:
                action = str(candidate.get("action") or "")
                if candidate.get("eligible") is True and candidate.get("ready") is False:
                    increment(stats["eligible_not_ready"], action)
                if candidate.get("eligible") is True and candidate.get("ready") is True:
                    increment(stats["eligible_ready"], action)
            for event in (trace.get("selected_action") or {}).get("events") or []:
                increment(stats["events"], str(event.get("action") or ""))
    return stats


def ml_window_stats_for_e7(experiment_root: Path) -> dict[str, int]:
    stats = {
        "opened_windows": 0,
        "active_window_traces": 0,
        "active_window_noops": 0,
        "below_threshold_no_window": 0,
    }
    trace_path = experiment_root / "E7_ml_aura_ml_tsra_r" / "tsra_r_decision_traces.jsonl"
    for trace in read_jsonl(trace_path):
        if trace.get("agent") != "TSRA-R-ML":
            continue
        feedback = trace.get("feedback") or {}
        time_sec = as_float(trace.get("time_sec"))
        probability = as_float(feedback.get("probability"))
        threshold = as_float(feedback.get("threshold"))
        active_until = as_float(feedback.get("active_defense_until"))
        active_window = time_sec < active_until
        if feedback.get("opened_window") is True:
            stats["opened_windows"] += 1
        if active_window:
            stats["active_window_traces"] += 1
        if active_window and (trace.get("selected_action") or {}).get("type") == "no_op":
            stats["active_window_noops"] += 1
        if probability < threshold and not active_window:
            stats["below_threshold_no_window"] += 1
    return stats


def adaptive_memory_stats(path: Path) -> dict[str, float]:
    by_condition = {row["condition"]: row for row in read_csv(path)}
    full = by_condition.get("full_tsra_r", {})
    adaptive = by_condition.get("adaptive_tsra_r", {})
    fields = [
        "mission_impact_mean",
        "defense_count_mean",
        "video_throttle_count_mean",
        "pace_switch_count_mean",
    ]
    stats: dict[str, float] = {}
    for field in fields:
        stats[f"delta_{field}"] = as_float(adaptive.get(field)) - as_float(full.get(field))
    return stats


def memory_chain_stats(path: Path) -> dict[str, float]:
    rows = read_csv(path)
    pass_rows = [row for row in rows if row.get("status") == "pass"]
    rates = [as_float(row.get("last_selected_chain_match_rate")) for row in rows]
    return {
        "rows": float(len(rows)),
        "pass_rows": float(len(pass_rows)),
        "min_chain_rate": min(rates) if rates else 0.0,
    }


def row(
    *,
    check_id: str,
    area: str,
    mechanism: str,
    evidence_files: str,
    observed: str,
    ok: bool,
    interpretation: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "mechanism": mechanism,
        "evidence_files": evidence_files,
        "observed": observed,
        "influence_status": "pass" if ok else "fail",
        "interpretation": interpretation,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def increment(counts: dict[str, int], key: str) -> None:
    counts[key] = counts.get(key, 0) + 1


def format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Memory Influence Audit",
        "",
        "This audit checks whether AgentMemory influences bounded agent decisions instead of acting only as passive trace storage.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_status_counts(rows)}",
        "",
        "## Audit Table",
        "",
    ]
    visible_fields = ["check_id", "area", "observed", "influence_status"]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for audit_row in rows:
        lines.append(markdown_row([markdown_cell(audit_row[field]) for field in visible_fields]))
    lines.extend(["", "## Detail", ""])
    for audit_row in rows:
        lines.extend(
            [
                f"### {audit_row['check_id']} {audit_row['area']}",
                "",
                f"- Mechanism: {audit_row['mechanism']}",
                f"- Evidence: {audit_row['evidence_files']}",
                f"- Observed: {audit_row['observed']}",
                f"- Status: {audit_row['influence_status']}",
                f"- Interpretation: {audit_row['interpretation']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def format_status_counts(rows: list[dict[str, str]]) -> str:
    counts: dict[str, int] = {}
    for audit_row in rows:
        increment(counts, audit_row["influence_status"])
    return format_counts(counts)


def markdown_row(values: list[str]) -> str:
    return "| " + " | ".join(values) + " |"


def markdown_cell(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit whether AgentMemory influences decisions.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--adaptive-summary", type=Path, default=DEFAULT_ADAPTIVE_SUMMARY)
    parser.add_argument("--memory-audit", type=Path, default=DEFAULT_MEMORY_AUDIT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any memory influence check fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(
        experiment_root=args.experiment_root,
        adaptive_summary_path=args.adaptive_summary,
        memory_audit_path=args.memory_audit,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["influence_status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} rows)")
    print(f"Wrote {args.output_md} ({len(rows)} rows)")
    if failed:
        print(f"Failed memory influence rows: {', '.join(row['check_id'] for row in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
