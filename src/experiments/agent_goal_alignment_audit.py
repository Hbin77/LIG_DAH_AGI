from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_goal_alignment_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_goal_alignment_audit.md")

TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
    "tsra_r_rule_delegate_traces.jsonl",
]

SAFETY_BOUNDARY = (
    "closed simulation agent goal-alignment audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "trace_id",
    "time_sec",
    "agent",
    "policy",
    "selected_type",
    "selected_actions",
    "observation_risk",
    "goal_signal",
    "alignment_basis",
    "goal_alignment_status",
    "issues",
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


def discover_traces(root: Path) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    if not root.exists():
        return rows
    for exp_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        for filename in TRACE_FILES:
            for trace in read_jsonl(exp_dir / filename):
                rows.append((exp_dir.name, trace))
    return rows


def collect_rows(experiment_root: Path) -> list[dict[str, str]]:
    rows = [
        audit_trace(experiment, trace)
        for experiment, trace in discover_traces(experiment_root)
    ]
    return sorted(
        rows,
        key=lambda row: (
            row["experiment"],
            float(row["time_sec"] or 0.0),
            row["agent"],
            row["trace_id"],
        ),
    )


def audit_trace(experiment: str, trace: dict[str, Any]) -> dict[str, str]:
    selected = trace.get("selected_action") or {}
    selected_type = str(selected.get("type") or "")
    agent = str(trace.get("agent") or "")
    if agent.startswith("AURA"):
        status, basis, signal, issues = audit_aura_goal(trace)
    elif agent.startswith("TSRA-R"):
        status, basis, signal, issues = audit_tsra_goal(trace)
    else:
        status = "fail"
        basis = "unknown agent family"
        signal = "none"
        issues = ["unsupported agent"]

    return {
        "experiment": experiment,
        "trace_id": str(trace.get("trace_id") or ""),
        "time_sec": format_value(trace.get("time_sec")),
        "agent": agent,
        "policy": str(trace.get("policy") or ""),
        "selected_type": selected_type,
        "selected_actions": ", ".join(selected_action_names(selected)) or "none",
        "observation_risk": summarize_observation_risk(trace),
        "goal_signal": signal,
        "alignment_basis": basis,
        "goal_alignment_status": status,
        "issues": " || ".join(issues),
        "safety_boundary": SAFETY_BOUNDARY,
    }


def audit_aura_goal(trace: dict[str, Any]) -> tuple[str, str, str, list[str]]:
    selected = trace.get("selected_action") or {}
    selected_type = selected.get("type")
    candidates = trace.get("candidate_actions") or []
    feedback = trace.get("feedback") or {}
    reason = str(trace.get("reason") or "")

    if selected_type == "no_op":
        accepted_markers = [
            "waiting for min_start_sec",
            "attack cooldown active",
            "max_events",
            "best candidate below attack threshold",
            "no candidate actions generated",
        ]
        ok = any(marker in reason for marker in accepted_markers)
        signal = f"reason={reason}; candidate_count={len(candidates)}"
        if "best candidate below attack threshold" in reason:
            signal += (
                f"; best_score={format_value(feedback.get('best_score'))}; "
                f"attack_threshold={format_value(feedback.get('attack_threshold'))}"
            )
        basis = "AURA withheld action because cadence, budget, or score gate blocked attack."
        issues = [] if ok else [f"unrecognized AURA no-op reason: {reason}"]
        return ("pass" if ok else "fail", basis, signal, issues)

    if selected_type != "attack_event":
        return "fail", "AURA selected unsupported action type.", "none", ["unsupported AURA selected type"]

    selected_action = str(selected.get("attack_type") or "")
    selected_target = str(selected.get("target_link") or "")
    selected_score = as_float(selected.get("score"))
    attack_threshold = as_float(feedback.get("attack_threshold"), default=0.12)
    scored = [candidate for candidate in candidates if "score" in candidate]
    top_score = max((as_float(candidate.get("score")) for candidate in scored), default=0.0)
    matched = [
        candidate
        for candidate in scored
        if str(candidate.get("action") or "") == selected_action
        and str(candidate.get("target_link") or "") == selected_target
    ]
    predicted_impact = as_float(matched[0].get("predicted_mission_impact")) if matched else 0.0
    detectability = as_float(matched[0].get("detectability_score")) if matched else 0.0

    issues = []
    if not matched:
        issues.append("selected attack not found in candidate list")
    if selected_score < attack_threshold:
        issues.append("selected attack score is below attack threshold")
    if selected_score < top_score - 1e-6:
        issues.append("selected attack is not the top goal score")
    if predicted_impact <= 0.0:
        issues.append("selected attack has no positive predicted mission impact")
    if detectability >= predicted_impact and selected_score <= 0.0:
        issues.append("detectability overwhelms predicted impact")

    signal = (
        f"selected_score={format_value(selected_score)}; top_score={format_value(top_score)}; "
        f"attack_threshold={format_value(attack_threshold)}; "
        f"predicted_mission_impact={format_value(predicted_impact)}; "
        f"detectability_score={format_value(detectability)}"
    )
    basis = (
        "AURA selected the highest mission-impact score above threshold while retaining "
        "the simulated-effect safety boundary."
    )
    return ("pass" if not issues else "fail", basis, signal, issues)


def audit_tsra_goal(trace: dict[str, Any]) -> tuple[str, str, str, list[str]]:
    selected = trace.get("selected_action") or {}
    selected_type = selected.get("type")
    candidates = trace.get("candidate_actions") or []
    feedback = trace.get("feedback") or {}
    reason = str(trace.get("reason") or "")
    signals = observation_signals(trace)
    selected_actions = selected_action_names(selected)

    if selected_type == "no_op":
        if str(trace.get("agent") or "") == "TSRA-R-ML":
            probability = probability_from_trace(trace)
            threshold = threshold_from_trace(trace)
            active_until = as_float(feedback.get("active_defense_until"))
            now = as_float(trace.get("time_sec"))
            active_window = active_until > now
            ok = probability < threshold or active_window or "detector opened or maintained" in reason
            signal = (
                f"probability={format_value(probability)}; threshold={format_value(threshold)}; "
                f"active_defense_until={format_value(active_until)}; active_window={active_window}; "
                f"reason={reason}"
            )
            basis = (
                "TSRA-R-ML withheld a new event when probability was below threshold or an "
                "already-open defense window was being maintained."
            )
            issues = [] if ok else ["ML defender no-op lacks below-threshold or active-window basis"]
            return ("pass" if ok else "fail", basis, signal, issues)

        ready_actions = [
            str(candidate.get("action") or "")
            for candidate in candidates
            if candidate.get("enabled") is not False
            and candidate.get("eligible") is True
            and candidate.get("ready") is True
        ]
        ok = not ready_actions
        signal = f"ready_goal_actions={', '.join(ready_actions) if ready_actions else 'none'}; reason={reason}"
        basis = "TSRA-R emitted no action because no enabled, eligible, ready defense action was present."
        issues = [] if ok else [f"ready defense actions were left unselected: {', '.join(ready_actions)}"]
        return ("pass" if ok else "fail", basis, signal, issues)

    if selected_type != "defense_events":
        return "fail", "TSRA-R selected unsupported action type.", "none", ["unsupported TSRA-R selected type"]

    issues = []
    action_basis = []
    for action in selected_actions:
        ok, basis = defense_action_aligned(action, trace, signals)
        action_basis.append(f"{action}: {basis}")
        if not ok:
            issues.append(f"{action} lacks matching observation/threshold condition")

    signal = (
        f"critical_pending={format_value(signals.get('critical_pending'))}; "
        f"video_queue_kb={format_value(signals.get('video_queue_kb'))}; "
        f"stale_data_ratio={format_value(signals.get('stale_data_ratio'))}; "
        f"total_queue_kb={format_value(signals.get('total_queue_kb'))}; "
        f"active_link={observation_active_link(trace)}; "
        f"probability={format_value(probability_from_trace(trace))}; "
        f"threshold={format_value(threshold_from_trace(trace))}"
    )
    basis = " | ".join(action_basis)
    return ("pass" if not issues else "fail", basis, signal, issues)


def defense_action_aligned(
    action: str,
    trace: dict[str, Any],
    signals: dict[str, Any],
) -> tuple[bool, str]:
    critical_pending = as_float(signals.get("critical_pending"))
    video_queue = as_float(signals.get("video_queue_kb"))
    stale_ratio = as_float(signals.get("stale_data_ratio"))
    if action == "priority_reroute":
        ok = critical_pending > 0 and video_queue > 500
        return ok, "critical_pending > 0 and video_queue_kb > 500"
    if action == "video_throttle":
        ok = video_queue > 1500
        return ok, "video_queue_kb > 1500"
    if action == "stale_badge":
        ok = stale_ratio > 0.25
        return ok, "stale_data_ratio > 0.25"
    if action == "pace_switch":
        ok = active_link_degraded(trace)
        return ok, "active link exceeds SATCOM/fallback degradation threshold"
    if action == "ml_attack_alert":
        probability = probability_from_trace(trace)
        threshold = threshold_from_trace(trace)
        ok = probability >= threshold
        return ok, "detector probability >= threshold"
    return False, "unknown defense action"


def active_link_degraded(trace: dict[str, Any]) -> bool:
    signals = observation_signals(trace)
    active_link = observation_active_link(trace)
    links = signals.get("links") or {}
    active = links.get(active_link) or {}
    latency_ms = as_float(active.get("latency_ms"))
    loss_rate = as_float(active.get("loss_rate"))
    total_queue_kb = as_float(signals.get("total_queue_kb"))
    if active_link == "SATCOM":
        return latency_ms > 1100 or loss_rate > 0.055 or total_queue_kb > 4500
    return latency_ms > 550 or loss_rate > 0.04 or total_queue_kb > 6500


def probability_from_trace(trace: dict[str, Any]) -> float:
    feedback = trace.get("feedback") or {}
    if "probability" in feedback:
        return as_float(feedback.get("probability"))
    for candidate in trace.get("candidate_actions") or []:
        if "probability" in candidate:
            return as_float(candidate.get("probability"))
    for call in trace.get("tool_calls") or []:
        if call.get("tool_name") == "predict_attack_probability":
            return as_float(call.get("output_summary"))
    return 0.0


def threshold_from_trace(trace: dict[str, Any]) -> float:
    feedback = trace.get("feedback") or {}
    if "threshold" in feedback:
        return as_float(feedback.get("threshold"))
    for candidate in trace.get("candidate_actions") or []:
        if "threshold" in candidate:
            return as_float(candidate.get("threshold"))
    return 0.75


def selected_action_names(selected: dict[str, Any]) -> list[str]:
    selected_type = selected.get("type")
    if selected_type == "attack_event":
        return [str(selected.get("attack_type") or "attack_event")]
    if selected_type == "defense_events":
        return [
            str(event.get("action"))
            for event in selected.get("events") or []
            if event.get("action")
        ]
    if selected_type == "no_op":
        return ["no_op"]
    return [str(selected_type or "unknown")]


def observation_signals(trace: dict[str, Any]) -> dict[str, Any]:
    observation = trace.get("observation") or {}
    return observation.get("signals") or {}


def observation_active_link(trace: dict[str, Any]) -> str:
    observation = trace.get("observation") or {}
    return str(observation.get("active_link") or "")


def summarize_observation_risk(trace: dict[str, Any]) -> str:
    signals = observation_signals(trace)
    return (
        f"active_link={observation_active_link(trace)}; "
        f"defense_mode={signals.get('defense_mode')}; "
        f"critical_pending={format_value(signals.get('critical_pending'))}; "
        f"video_queue_kb={format_value(signals.get('video_queue_kb'))}; "
        f"stale_data_ratio={format_value(signals.get('stale_data_ratio'))}; "
        f"p95_latency_sec={format_value(signals.get('recent_p95_critical_latency_sec'))}; "
        f"priority_inversion={format_value(signals.get('priority_inversion_rate'))}; "
        f"total_queue_kb={format_value(signals.get('total_queue_kb'))}"
    )


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def format_value(value: Any) -> str:
    if value in ("", None):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Goal Alignment Audit",
        "",
        "This audit checks whether AURA and TSRA-R decisions align with their stated attack or defense goals, not only whether the trace schema is valid.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'goal_alignment_status'))}",
        f"- Agents: {', '.join(sorted({row['agent'] for row in rows}))}",
        "",
        "## Goal Checks",
        "",
        "- AURA attack events must clear the attack threshold, match the top score, and carry positive predicted mission impact.",
        "- AURA no-op decisions must cite cadence, budget, candidate, or score-gate reasons.",
        "- TSRA-R defense events must match priority, video, stale-data, PACE, or ML-threshold conditions in the observation.",
        "- TSRA-R no-op decisions must have no ready rule action or must maintain a detector-controlled window.",
        "",
        "## Sample Failures",
        "",
    ]
    failures = [row for row in rows if row["goal_alignment_status"] != "pass"]
    if not failures:
        lines.append("None.")
    else:
        for row in failures[:20]:
            lines.append(
                f"- {row['experiment']} {row['trace_id']} {row['agent']} "
                f"{row['selected_actions']}: {row['issues']}"
            )
    lines.extend(["", "## Audit Table", ""])
    visible_fields = [
        "experiment",
        "time_sec",
        "agent",
        "selected_actions",
        "goal_signal",
        "goal_alignment_status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    path.write_text("\n".join(lines), encoding="utf-8")


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row[field]
        counts[value] = counts.get(value, 0) + 1
    return counts


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def markdown_row(values: list[str]) -> str:
    return "| " + " | ".join(values) + " |"


def markdown_cell(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit agent decisions against stated goals.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any goal-alignment row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["goal_alignment_status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} goal alignment rows)")
    print(f"Wrote {args.output_md} ({len(rows)} goal alignment rows)")
    if failed:
        print(f"Failed goal-alignment rows: {len(failed)}")
        for row in failed[:10]:
            print(f"- {row['experiment']} {row['trace_id']} {row['agent']}: {row['issues']}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
