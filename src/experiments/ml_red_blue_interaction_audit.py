from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
E7 = "E7_ml_aura_ml_tsra_r"

DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/ml_red_blue_interaction_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/ml_red_blue_interaction_audit.md"

AURA_TRACE_PATH = f"outputs/experiments/{E7}/aura_decision_traces.jsonl"
TSRA_TRACE_PATH = f"outputs/experiments/{E7}/tsra_r_decision_traces.jsonl"
ATTACK_PATH = f"outputs/experiments/{E7}/attack_events.jsonl"
DEFENSE_PATH = f"outputs/experiments/{E7}/defense_events.jsonl"
COORDINATION_PATH = "outputs/report_tables/agent_coordination_latency_audit.csv"

RESPONSE_WINDOW_SEC = 40.0
CORE_DEFENSE_ACTIONS = {"priority_reroute", "stale_badge", "video_throttle", "pace_switch"}
SAFETY_BOUNDARY = (
    "closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "attack_event_id",
    "attack_time_sec",
    "attack_type",
    "target_link",
    "aura_trace_id",
    "aura_candidate_count",
    "aura_selected_score",
    "aura_selection_link_status",
    "tsra_probability_at_attack",
    "tsra_active_window_before_attack",
    "first_above_threshold_latency_sec",
    "peak_probability_in_response_window",
    "first_ml_alert_latency_sec",
    "first_core_defense_latency_sec",
    "coordination_class",
    "impact_reduction_from_peak",
    "interaction_class",
    "interaction_status",
    "interaction_signal",
    "safety_boundary",
]


def read_jsonl(rel: str) -> list[dict[str, Any]]:
    path = ROOT / rel
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_csv(rel: str) -> list[dict[str, str]]:
    path = ROOT / rel
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None, "missing", "not_applicable"):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def attack_time(event: dict[str, Any]) -> float:
    candidate = event.get("candidate") or {}
    return as_float(
        event.get("time_sec")
        or event.get("selected_at")
        or candidate.get("start_time")
    )


def attack_type(event: dict[str, Any]) -> str:
    return str((event.get("candidate") or {}).get("attack_type", ""))


def target_link(event: dict[str, Any]) -> str:
    return str((event.get("candidate") or {}).get("target_link", ""))


def trace_time(trace: dict[str, Any]) -> float:
    return as_float(trace.get("time_sec"))


def probability(trace: dict[str, Any]) -> float:
    return as_float((trace.get("feedback") or {}).get("probability"))


def threshold(trace: dict[str, Any]) -> float:
    return as_float((trace.get("feedback") or {}).get("threshold"), 0.75)


def active_until(trace: dict[str, Any]) -> float:
    return as_float((trace.get("feedback") or {}).get("active_defense_until"))


def selected_action(trace: dict[str, Any]) -> dict[str, Any]:
    return trace.get("selected_action") or {}


def candidate_count(trace: dict[str, Any]) -> int:
    return len(trace.get("candidate_actions") or [])


def find_aura_trace(
    traces: list[dict[str, Any]],
    attack: dict[str, Any],
) -> dict[str, Any]:
    event_id = str(attack.get("event_id", ""))
    time_sec = attack_time(attack)
    for trace in traces:
        selected = selected_action(trace)
        if selected.get("event_id") == event_id:
            return trace
    for trace in traces:
        if trace_time(trace) == time_sec and selected_action(trace).get("type") == "attack_event":
            return trace
    return {}


def selection_link_status(trace: dict[str, Any], attack: dict[str, Any]) -> str:
    if not trace:
        return "missing_trace"
    selected = selected_action(trace)
    if selected.get("event_id") != attack.get("event_id"):
        return "event_id_mismatch"
    if selected.get("attack_type") != attack_type(attack):
        return "attack_type_mismatch"
    if selected.get("target_link") != target_link(attack):
        return "target_link_mismatch"
    if abs(as_float(selected.get("score")) - as_float(attack.get("score"))) > 1e-6:
        return "score_mismatch"
    return "linked"


def traces_in_window(
    traces: list[dict[str, Any]],
    start: float,
    end: float,
) -> list[dict[str, Any]]:
    return [trace for trace in traces if start <= trace_time(trace) <= end]


def first_trace_above_threshold(traces: list[dict[str, Any]]) -> dict[str, Any]:
    for trace in traces:
        if probability(trace) >= threshold(trace):
            return trace
    return {}


def peak_probability_trace(traces: list[dict[str, Any]]) -> dict[str, Any]:
    if not traces:
        return {}
    return max(traces, key=probability)


def first_defense_event(
    defenses: list[dict[str, Any]],
    *,
    start: float,
    end: float,
    action_filter: set[str],
) -> dict[str, Any]:
    events = [
        event
        for event in defenses
        if start <= as_float(event.get("time_sec")) <= end
        and str(event.get("action", "")) in action_filter
    ]
    return min(events, key=lambda event: as_float(event.get("time_sec"))) if events else {}


def active_window_before_attack(
    traces: list[dict[str, Any]],
    attack_time_sec: float,
) -> bool:
    previous = [
        trace
        for trace in traces
        if trace_time(trace) <= attack_time_sec and active_until(trace) > attack_time_sec
    ]
    return bool(previous)


def coordination_by_attack() -> dict[str, dict[str, str]]:
    return {
        row.get("attack_event_id", ""): row
        for row in read_csv(COORDINATION_PATH)
        if row.get("experiment") == E7
    }


def classify_interaction(
    *,
    active_before: bool,
    first_above_latency: float | None,
    first_core_latency: float | None,
) -> str:
    if not active_before and first_above_latency is not None and first_above_latency > 0:
        return "ml_triggered_after_attack"
    if active_before and first_core_latency == 0.0:
        return "active_window_immediate_core_defense"
    if active_before:
        return "active_window_bounded_refresh"
    return "bounded_ml_interaction"


def interaction_status(
    *,
    aura_link_status: str,
    aura_candidate_count: int,
    active_before: bool,
    first_above_latency: float | None,
    peak_probability: float,
    first_alert_latency: float | None,
    first_core_latency: float | None,
    coordination: dict[str, str],
) -> tuple[str, list[str]]:
    issues = []
    if aura_link_status != "linked":
        issues.append(f"aura_link_status={aura_link_status}")
    if aura_candidate_count <= 0:
        issues.append("no_aura_candidates")
    if first_above_latency is None or first_above_latency > RESPONSE_WINDOW_SEC:
        issues.append("no_probability_threshold_crossing_in_window")
    if peak_probability < 0.75:
        issues.append("peak_probability_below_threshold")
    active_window_refresh_supported = (
        active_before
        and first_above_latency is not None
        and first_above_latency <= RESPONSE_WINDOW_SEC
        and first_core_latency == 0.0
    )
    if (
        not active_window_refresh_supported
        and (first_alert_latency is None or first_alert_latency > RESPONSE_WINDOW_SEC)
    ):
        issues.append("ml_alert_missing_or_late")
    if first_core_latency is None or first_core_latency > RESPONSE_WINDOW_SEC:
        issues.append("core_defense_missing_or_late")
    if coordination.get("coordination_status") != "pass":
        issues.append("coordination_not_pass")
    if as_float(coordination.get("impact_reduction_from_peak")) <= 0.0:
        issues.append("no_positive_impact_reduction")
    return ("pass" if not issues else "fail", issues)


def collect_rows() -> list[dict[str, str]]:
    attacks = read_jsonl(ATTACK_PATH)
    aura_traces = read_jsonl(AURA_TRACE_PATH)
    tsra_traces = read_jsonl(TSRA_TRACE_PATH)
    defenses = read_jsonl(DEFENSE_PATH)
    coordination = coordination_by_attack()

    rows = []
    for attack in attacks:
        event_id = str(attack.get("event_id", ""))
        time_sec = attack_time(attack)
        end = time_sec + RESPONSE_WINDOW_SEC
        aura_trace = find_aura_trace(aura_traces, attack)
        aura_link_status = selection_link_status(aura_trace, attack)
        window_traces = traces_in_window(tsra_traces, time_sec, end)
        above_trace = first_trace_above_threshold(window_traces)
        peak_trace = peak_probability_trace(window_traces)
        alert_event = first_defense_event(
            defenses,
            start=time_sec,
            end=end,
            action_filter={"ml_attack_alert"},
        )
        core_event = first_defense_event(
            defenses,
            start=time_sec,
            end=end,
            action_filter=CORE_DEFENSE_ACTIONS,
        )
        active_before = active_window_before_attack(tsra_traces, time_sec)
        first_above_latency = (
            trace_time(above_trace) - time_sec if above_trace else None
        )
        first_alert_latency = (
            as_float(alert_event.get("time_sec")) - time_sec if alert_event else None
        )
        first_core_latency = (
            as_float(core_event.get("time_sec")) - time_sec if core_event else None
        )
        coord = coordination.get(event_id, {})
        status, issues = interaction_status(
            aura_link_status=aura_link_status,
            aura_candidate_count=candidate_count(aura_trace),
            active_before=active_before,
            first_above_latency=first_above_latency,
            peak_probability=probability(peak_trace),
            first_alert_latency=first_alert_latency,
            first_core_latency=first_core_latency,
            coordination=coord,
        )
        interaction_class = classify_interaction(
            active_before=active_before,
            first_above_latency=first_above_latency,
            first_core_latency=first_core_latency,
        )
        rows.append(
            {
                "experiment": E7,
                "attack_event_id": event_id,
                "attack_time_sec": fmt(time_sec),
                "attack_type": attack_type(attack),
                "target_link": target_link(attack),
                "aura_trace_id": str(aura_trace.get("trace_id", "")),
                "aura_candidate_count": str(candidate_count(aura_trace)),
                "aura_selected_score": fmt((selected_action(aura_trace)).get("score")),
                "aura_selection_link_status": aura_link_status,
                "tsra_probability_at_attack": fmt(probability(window_traces[0]) if window_traces else None),
                "tsra_active_window_before_attack": bool_text(active_before),
                "first_above_threshold_latency_sec": fmt(first_above_latency),
                "peak_probability_in_response_window": fmt(probability(peak_trace)),
                "first_ml_alert_latency_sec": fmt(first_alert_latency),
                "first_core_defense_latency_sec": fmt(first_core_latency),
                "coordination_class": coord.get("coordination_class", ""),
                "impact_reduction_from_peak": coord.get("impact_reduction_from_peak", ""),
                "interaction_class": interaction_class,
                "interaction_status": status,
                "interaction_signal": (
                    f"aura_link={aura_link_status}; "
                    f"aura_candidates={candidate_count(aura_trace)}; "
                    f"first_above_threshold_latency={fmt(first_above_latency)}; "
                    f"first_ml_alert_latency={fmt(first_alert_latency)}; "
                    f"first_core_defense_latency={fmt(first_core_latency)}; "
                    f"peak_probability={fmt(probability(peak_trace))}; "
                    f"issues={','.join(issues) if issues else 'none'}"
                ),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = count_values(rows, "interaction_status")
    class_counts = count_values(rows, "interaction_class")
    lines = [
        "# ML Red-Blue Interaction Audit",
        "",
        "This audit links each E7 AURA-ML attack selection to the TSRA-R-ML probability/window response, ML alert, core defense event, and coordination outcome.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {render_counts(status_counts)}",
        f"- Interaction classes: {render_counts(class_counts)}",
        "",
        "| attack_event_id | attack_type | target_link | aura_candidate_count | first_above_threshold_latency_sec | first_ml_alert_latency_sec | first_core_defense_latency_sec | interaction_class | interaction_status |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["attack_event_id"]),
                    md(row["attack_type"]),
                    md(row["target_link"]),
                    row["aura_candidate_count"],
                    row["first_above_threshold_latency_sec"],
                    row["first_ml_alert_latency_sec"],
                    row["first_core_defense_latency_sec"],
                    md(row["interaction_class"]),
                    md(row["interaction_status"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['attack_event_id']} {row['attack_type']}",
                "",
                f"- AURA trace: {row['aura_trace_id']}",
                f"- AURA selected score: {row['aura_selected_score']}",
                f"- AURA selection link: {row['aura_selection_link_status']}",
                f"- TSRA probability at attack: {row['tsra_probability_at_attack']}",
                f"- TSRA active window before attack: {row['tsra_active_window_before_attack']}",
                f"- Peak probability in response window: {row['peak_probability_in_response_window']}",
                f"- Coordination class: {row['coordination_class']}",
                f"- Impact reduction from peak: {row['impact_reduction_from_peak']}",
                f"- Interaction signal: {row['interaction_signal']}",
                f"- Status: {row['interaction_status']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get(field, "")
        counts[key] = counts.get(key, 0) + 1
    return counts


def render_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit E7 ML red-blue interaction path.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any ML interaction row fails.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    args = parse_args()
    rows = collect_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["interaction_status"] != "pass"]
    print(f"Wrote {display_path(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.output_md)} ({len(rows)} rows)")
    if failed:
        print(
            "Failed ML red-blue interaction rows: "
            + ", ".join(row["attack_event_id"] for row in failed)
        )
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
