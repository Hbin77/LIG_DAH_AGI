from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
E7 = "E7_ml_aura_ml_tsra_r"
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/ml_defense_decision_path_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/ml_defense_decision_path_audit.md"

TRACE_PATH = f"outputs/experiments/{E7}/tsra_r_decision_traces.jsonl"
DEFENSE_PATH = f"outputs/experiments/{E7}/defense_events.jsonl"
ATTACK_PATH = f"outputs/experiments/{E7}/attack_events.jsonl"
COORDINATION_PATH = "outputs/report_tables/agent_coordination_latency_audit.csv"

SAFETY_BOUNDARY = (
    "closed simulation ML defense decision-path audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "area",
    "requirement",
    "evidence",
    "observed",
    "status",
    "interpretation",
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


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value in ("", None, "missing", "not_applicable"):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def selected_type(trace: dict[str, Any]) -> str:
    selected = trace.get("selected_action") or {}
    return str(selected.get("type", ""))


def tool_names(trace: dict[str, Any]) -> list[str]:
    return [
        str(call.get("tool_name", ""))
        for call in trace.get("tool_calls") or []
        if isinstance(call, dict)
    ]


def has_tool(trace: dict[str, Any], tool_name: str) -> bool:
    return tool_name in tool_names(trace)


def probability(trace: dict[str, Any]) -> float:
    return as_float((trace.get("feedback") or {}).get("probability"))


def threshold(trace: dict[str, Any]) -> float:
    return as_float((trace.get("feedback") or {}).get("threshold"), 0.75)


def event_count(trace: dict[str, Any]) -> int:
    return as_int((trace.get("feedback") or {}).get("event_count"))


def active_until(trace: dict[str, Any]) -> float:
    return as_float((trace.get("feedback") or {}).get("active_defense_until"))


def opened_window(trace: dict[str, Any]) -> bool:
    return bool((trace.get("feedback") or {}).get("opened_window"))


def trace_time(trace: dict[str, Any]) -> float:
    return as_float(trace.get("time_sec"))


def attack_time(event: dict[str, Any]) -> float:
    candidate = event.get("candidate") or {}
    return as_float(
        event.get("time_sec")
        or event.get("selected_at")
        or candidate.get("start_time")
    )


def defense_actions_at(defenses: list[dict[str, Any]], time_sec: float) -> list[str]:
    actions = [
        str(event.get("action", ""))
        for event in defenses
        if as_float(event.get("time_sec")) == time_sec
    ]
    return sorted(actions)


def action_counts(defenses: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(event.get("action", "")) for event in defenses)


def alert_gaps(alerts: list[dict[str, Any]]) -> list[float]:
    times = sorted(as_float(event.get("time_sec")) for event in alerts)
    return [b - a for a, b in zip(times, times[1:])]


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def row(
    *,
    check_id: str,
    area: str,
    requirement: str,
    evidence: list[str],
    observed: str,
    ok: bool,
    interpretation: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "requirement": requirement,
        "evidence": " | ".join(evidence),
        "observed": observed,
        "status": "pass" if ok else "fail",
        "interpretation": interpretation,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def build_rows() -> list[dict[str, str]]:
    traces = read_jsonl(TRACE_PATH)
    defenses = read_jsonl(DEFENSE_PATH)
    attacks = read_jsonl(ATTACK_PATH)
    coordination_rows = read_csv(COORDINATION_PATH)

    first_attack_time = min((attack_time(event) for event in attacks), default=0.0)
    threshold_traces = [trace for trace in traces if probability(trace) >= threshold(trace)]
    first_threshold_trace = threshold_traces[0] if threshold_traces else {}
    first_threshold_time = trace_time(first_threshold_trace) if first_threshold_trace else None
    current_threshold = threshold(first_threshold_trace) if first_threshold_trace else 0.75

    pre_threshold_traces = [
        trace
        for trace in traces
        if first_threshold_time is not None and trace_time(trace) < first_threshold_time
    ]
    pre_threshold_defenses = [
        event
        for event in defenses
        if first_threshold_time is not None and as_float(event.get("time_sec")) < first_threshold_time
    ]
    pre_threshold_max_probability = max(
        (probability(trace) for trace in pre_threshold_traces),
        default=0.0,
    )
    pre_threshold_noop_count = sum(
        1
        for trace in pre_threshold_traces
        if probability(trace) < threshold(trace)
        and selected_type(trace) == "no_op"
        and event_count(trace) == 0
    )
    pre_threshold_guard_traces = [
        trace
        for trace in pre_threshold_traces
        if (trace.get("feedback") or {}).get("early_guard_triggered") is True
    ]
    pre_threshold_guard_event_count = sum(
        event_count(trace) for trace in pre_threshold_guard_traces
    )
    pre_threshold_ml_alerts = [
        event
        for event in pre_threshold_defenses
        if event.get("action") == "ml_attack_alert"
    ]

    first_threshold_actions = (
        defense_actions_at(defenses, first_threshold_time)
        if first_threshold_time is not None
        else []
    )
    first_response_latency = (
        first_threshold_time - first_attack_time
        if first_threshold_time is not None
        else None
    )

    above_no_event = [
        trace
        for trace in threshold_traces
        if opened_window(trace) and event_count(trace) == 0
    ]
    above_event = [
        trace
        for trace in threshold_traces
        if opened_window(trace) and event_count(trace) > 0
    ]
    alerts = [event for event in defenses if event.get("action") == "ml_attack_alert"]
    gaps = alert_gaps(alerts)
    min_alert_gap = min(gaps, default=0.0)
    all_alerts_above_threshold = all(
        as_float((event.get("details") or {}).get("probability")) >= as_float(
            (event.get("details") or {}).get("threshold"),
            current_threshold,
        )
        for event in alerts
    )

    counts = action_counts(defenses)
    core_actions = ["priority_reroute", "stale_badge", "video_throttle", "pace_switch"]

    rule_tool_name = "execute_rule_defense_actions"
    active_window_traces = [
        trace for trace in traces if active_until(trace) > trace_time(trace)
    ]
    rule_tool_traces = [trace for trace in traces if has_tool(trace, rule_tool_name)]
    selected_defense_traces = [
        trace for trace in traces if selected_type(trace) == "defense_events"
    ]
    selected_defense_traces_with_rule_tool = [
        trace for trace in selected_defense_traces if has_tool(trace, rule_tool_name)
    ]
    rule_tool_calls = [
        call
        for trace in traces
        for call in trace.get("tool_calls") or []
        if isinstance(call, dict) and call.get("tool_name") == rule_tool_name
    ]
    rule_tool_error_count = sum(
        1 for call in rule_tool_calls if call.get("status") != "ok"
    )
    rule_tool_output_count = sum(
        1 for call in rule_tool_calls if "output_summary" in call
    )

    memory_mismatches = 0
    for trace in traces:
        feedback_until = active_until(trace)
        memory_until = as_float(
            ((trace.get("memory") or {}).get("belief_state") or {}).get("active_defense_until")
        )
        if abs(feedback_until - memory_until) > 1e-9:
            memory_mismatches += 1
    threshold_windows = [active_until(trace) for trace in threshold_traces]
    threshold_window_nondecreasing = all(
        b >= a for a, b in zip(threshold_windows, threshold_windows[1:])
    )

    e7_coordination = [
        item for item in coordination_rows if item.get("experiment") == E7
    ]
    ml_reactive_rows = [
        item
        for item in e7_coordination
        if item.get("coordination_class") == "ml_reactive_window"
    ]
    max_reactive_latency = max(
        (
            as_float(item.get("first_defense_latency_sec"))
            for item in ml_reactive_rows
        ),
        default=0.0,
    )
    min_reactive_reduction = min(
        (
            as_float(item.get("impact_reduction_from_peak"))
            for item in ml_reactive_rows
        ),
        default=0.0,
    )

    return [
        row(
            check_id="MDP01",
            area="Pre-threshold guard discipline",
            requirement=(
                "TSRA-R-ML should stay quiet below threshold except for trace-backed early mission-pressure "
                "guard actions, and it should not emit ML attack alerts before the detector threshold."
            ),
            evidence=[TRACE_PATH, DEFENSE_PATH],
            observed=(
                f"trace_count={len(traces)}; first_threshold_time={fmt(first_threshold_time)}; "
                f"pre_threshold_traces={len(pre_threshold_traces)}; "
                f"pre_threshold_noop_count={pre_threshold_noop_count}; "
                f"pre_threshold_defense_events={len(pre_threshold_defenses)}; "
                f"pre_threshold_guard_traces={len(pre_threshold_guard_traces)}; "
                f"pre_threshold_guard_event_count={pre_threshold_guard_event_count}; "
                f"pre_threshold_ml_alerts={len(pre_threshold_ml_alerts)}; "
                f"pre_threshold_max_probability={fmt(pre_threshold_max_probability)}; "
                f"threshold={fmt(current_threshold)}"
            ),
            ok=(
                bool(traces)
                and first_threshold_time is not None
                and len(pre_threshold_traces)
                == pre_threshold_noop_count + len(pre_threshold_guard_traces)
                and len(pre_threshold_defenses) == pre_threshold_guard_event_count
                and not pre_threshold_ml_alerts
                and pre_threshold_max_probability < current_threshold
            ),
            interpretation=(
                "The ML defender remains reactive: below-threshold actions are limited to an explicit "
                "mission-pressure guard, while attack alerts still wait for detector confidence."
            ),
        ),
        row(
            check_id="MDP02",
            area="Threshold-to-window transition",
            requirement="The first above-threshold detector decision must open a defense window and emit a same-time ML alert.",
            evidence=[TRACE_PATH, DEFENSE_PATH, ATTACK_PATH],
            observed=(
                f"first_attack_time={fmt(first_attack_time)}; "
                f"first_threshold_time={fmt(first_threshold_time)}; "
                f"first_response_latency_sec={fmt(first_response_latency)}; "
                f"first_probability={fmt(probability(first_threshold_trace))}; "
                f"threshold={fmt(current_threshold)}; "
                f"opened_window={bool_text(opened_window(first_threshold_trace))}; "
                f"event_count={event_count(first_threshold_trace)}; "
                f"same_time_actions={','.join(first_threshold_actions)}"
            ),
            ok=(
                first_threshold_time is not None
                and probability(first_threshold_trace) >= current_threshold
                and opened_window(first_threshold_trace)
                and event_count(first_threshold_trace) > 0
                and "ml_attack_alert" in first_threshold_actions
                and first_response_latency is not None
                and first_response_latency <= 40.0
            ),
            interpretation=(
                "The detector threshold is wired to an actual defense-window transition, not only "
                "to an offline probability score."
            ),
        ),
        row(
            check_id="MDP03",
            area="Alert cooldown and window refresh",
            requirement="Repeated high-confidence decisions should refresh the window while limiting alert spam.",
            evidence=[TRACE_PATH, DEFENSE_PATH],
            observed=(
                f"threshold_traces={len(threshold_traces)}; "
                f"above_threshold_event_traces={len(above_event)}; "
                f"above_threshold_no_event_refresh_traces={len(above_no_event)}; "
                f"ml_attack_alerts={len(alerts)}; min_alert_gap_sec={fmt(min_alert_gap)}; "
                f"all_alert_probabilities_above_threshold={bool_text(all_alerts_above_threshold)}"
            ),
            ok=(
                len(threshold_traces) > 0
                and len(above_event) > 0
                and len(above_no_event) > 0
                and len(alerts) >= 5
                and min_alert_gap >= 25.0
                and all_alerts_above_threshold
            ),
            interpretation=(
                "No-op traces above threshold are not dead code; they represent cooldown-bounded "
                "window refresh decisions."
            ),
        ),
        row(
            check_id="MDP04",
            area="Core defense fanout",
            requirement="The ML-opened window must enable core TSRA-R actions beyond the alert itself.",
            evidence=[DEFENSE_PATH],
            observed=(
                f"defense_events={len(defenses)}; "
                f"ml_attack_alert={counts['ml_attack_alert']}; "
                f"priority_reroute={counts['priority_reroute']}; "
                f"stale_badge={counts['stale_badge']}; "
                f"video_throttle={counts['video_throttle']}; "
                f"pace_switch={counts['pace_switch']}"
            ),
            ok=bool(defenses) and all(counts[action] > 0 for action in core_actions),
            interpretation=(
                "The ML detector opens the gate; the defense agent still executes mission-aware "
                "TSRA-R actions inside that window."
            ),
        ),
        row(
            check_id="MDP05",
            area="Rule-defense tool execution",
            requirement="When TSRA-R-ML has an active defense window, it must execute bounded rule-defense actions as a recorded runtime tool call.",
            evidence=[TRACE_PATH],
            observed=(
                f"trace_count={len(traces)}; "
                f"active_window_traces={len(active_window_traces)}; "
                f"rule_tool_traces={len(rule_tool_traces)}; "
                f"selected_defense_traces={len(selected_defense_traces)}; "
                f"selected_defense_traces_with_rule_tool={len(selected_defense_traces_with_rule_tool)}; "
                f"rule_tool_invocations={len(rule_tool_calls)}; "
                f"rule_tool_error_count={rule_tool_error_count}; "
                f"rule_tool_output_count={rule_tool_output_count}; "
                f"tool_name={rule_tool_name}"
            ),
            ok=(
                bool(traces)
                and len(active_window_traces) > 0
                and len(rule_tool_traces) == len(active_window_traces)
                and len(selected_defense_traces_with_rule_tool) == len(selected_defense_traces)
                and len(rule_tool_calls) == len(rule_tool_traces)
                and rule_tool_error_count == 0
                and rule_tool_output_count == len(rule_tool_calls)
            ),
            interpretation=(
                "The ML defender does not hide rule-action fanout behind an untraced method call; "
                "the delegation appears in TSRA-R-ML DecisionTrace tool calls."
            ),
        ),
        row(
            check_id="MDP06",
            area="Memory continuity",
            requirement="Active defense window memory should match trace feedback and extend monotonically on above-threshold decisions.",
            evidence=[TRACE_PATH],
            observed=(
                f"memory_mismatches={memory_mismatches}; "
                f"threshold_window_nondecreasing={bool_text(threshold_window_nondecreasing)}; "
                f"first_active_until={fmt(threshold_windows[0] if threshold_windows else None)}; "
                f"last_active_until={fmt(threshold_windows[-1] if threshold_windows else None)}"
            ),
            ok=(
                bool(threshold_windows)
                and memory_mismatches == 0
                and threshold_window_nondecreasing
                and threshold_windows[-1] > threshold_windows[0]
            ),
            interpretation=(
                "The window is agent memory, not a stateless if-branch; trace feedback and memory "
                "stay aligned across the E7 run."
            ),
        ),
        row(
            check_id="MDP07",
            area="Closed-loop coordination effect",
            requirement="At least one ML-reactive episode should connect the ML defense window to bounded response latency and positive post-peak reduction.",
            evidence=[COORDINATION_PATH],
            observed=(
                f"e7_coordination_rows={len(e7_coordination)}; "
                f"ml_reactive_rows={len(ml_reactive_rows)}; "
                f"max_ml_reactive_defense_latency_sec={fmt(max_reactive_latency)}; "
                f"min_ml_reactive_impact_reduction_from_peak={fmt(min_reactive_reduction)}"
            ),
            ok=(
                len(e7_coordination) == 5
                and len(ml_reactive_rows) >= 1
                and all(item.get("coordination_status") == "pass" for item in e7_coordination)
                and max_reactive_latency <= 40.0
                and min_reactive_reduction > 0.0
            ),
            interpretation=(
                "The ML decision path reaches closed-loop evidence: response latency is bounded and "
                "post-peak mission impact decreases."
            ),
        ),
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ML Defense Decision Path Audit",
        "",
        "This audit traces the E7 TSRA-R-ML path from detector probability to defense-window behavior and closed-loop effect.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| check_id | area | status | observed | interpretation |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(item["check_id"]),
                    md(item["area"]),
                    md(item["status"]),
                    md(item["observed"]),
                    md(item["interpretation"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for item in rows:
        lines.extend(
            [
                f"### {item['check_id']} {item['area']}",
                "",
                f"- Requirement: {item['requirement']}",
                f"- Evidence: {item['evidence']}",
                f"- Observed: {item['observed']}",
                f"- Status: {item['status']}",
                f"- Interpretation: {item['interpretation']}",
                f"- Safety boundary: {item['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit E7 ML defense decision path.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any ML defense path row fails.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [item for item in rows if item["status"] != "pass"]
    print(f"Wrote {display_path(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.output_md)} ({len(rows)} rows)")
    if failed:
        print(f"Failed ML defense decision path rows: {', '.join(item['check_id'] for item in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
