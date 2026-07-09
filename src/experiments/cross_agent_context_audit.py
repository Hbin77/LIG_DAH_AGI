from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/cross_agent_context_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/cross_agent_context_audit.md"

CLOSED_LOOP_EXPERIMENTS = [
    "E5_rule_aura_tsra_r",
    "E7_ml_aura_ml_tsra_r",
]
SAFETY_BOUNDARY = (
    "closed simulation cross-agent context audit only; no RF, exploit, or live network action"
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


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: float) -> str:
    return f"{value:.6g}"


def trace_time(trace: dict[str, Any]) -> float:
    return as_float(trace.get("time_sec"))


def selected_type(trace: dict[str, Any]) -> str:
    return str((trace.get("selected_action") or {}).get("type", ""))


def tool_count(traces: list[dict[str, Any]], tool_name: str) -> int:
    return sum(
        1
        for trace in traces
        for call in trace.get("tool_calls") or []
        if call.get("tool_name") == tool_name
    )


def tool_errors(traces: list[dict[str, Any]]) -> int:
    return sum(
        1
        for trace in traces
        for call in trace.get("tool_calls") or []
        if call.get("status") != "ok"
    )


def feedback_context(trace: dict[str, Any], key: str) -> dict[str, Any]:
    value = (trace.get("feedback") or {}).get(key)
    return value if isinstance(value, dict) else {}


def memory_context(trace: dict[str, Any], key: str) -> dict[str, Any]:
    memory = trace.get("memory") or {}
    belief = memory.get("belief_state") or {}
    value = belief.get(key)
    return value if isinstance(value, dict) else {}


def observation_has_keys(trace: dict[str, Any], keys: set[str]) -> bool:
    signals = ((trace.get("observation") or {}).get("signals") or {})
    return keys.issubset(signals)


def attack_time(event: dict[str, Any]) -> float:
    candidate = event.get("candidate") or {}
    return as_float(
        event.get("time_sec")
        or event.get("selected_at")
        or candidate.get("start_time")
    )


def first_trace_at_or_after(
    traces: list[dict[str, Any]],
    start: float,
    window_sec: float,
) -> dict[str, Any]:
    candidates = [
        trace
        for trace in traces
        if start <= trace_time(trace) <= start + window_sec
    ]
    return min(candidates, key=trace_time) if candidates else {}


def candidate_context_count(
    traces: list[dict[str, Any]],
    context_key: str,
) -> tuple[int, int, int]:
    total = 0
    with_context = 0
    used = 0
    used_key = context_key.replace("_context", "_context_used")
    for trace in traces:
        for candidate in trace.get("candidate_actions") or []:
            total += 1
            if isinstance(candidate.get(context_key), dict):
                with_context += 1
            if candidate.get(used_key) is True:
                used += 1
    return total, with_context, used


def event_related_context(event: dict[str, Any]) -> dict[str, Any]:
    details = event.get("details") or {}
    value = details.get("related_attack_context")
    return value if isinstance(value, dict) else {}


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


def collect_inputs() -> dict[str, dict[str, list[dict[str, Any]]]]:
    data: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for experiment in CLOSED_LOOP_EXPERIMENTS:
        exp_dir = ROOT / "outputs/experiments" / experiment
        data[experiment] = {
            "attacks": read_jsonl(exp_dir / "attack_events.jsonl"),
            "defenses": read_jsonl(exp_dir / "defense_events.jsonl"),
            "aura_traces": read_jsonl(exp_dir / "aura_decision_traces.jsonl"),
            "tsra_traces": read_jsonl(exp_dir / "tsra_r_decision_traces.jsonl"),
        }
    return data


def build_rows() -> list[dict[str, str]]:
    data = collect_inputs()
    aura_traces = [
        trace
        for experiment in CLOSED_LOOP_EXPERIMENTS
        for trace in data[experiment]["aura_traces"]
    ]
    tsra_traces = [
        trace
        for experiment in CLOSED_LOOP_EXPERIMENTS
        for trace in data[experiment]["tsra_traces"]
    ]
    attacks = [
        (experiment, attack)
        for experiment in CLOSED_LOOP_EXPERIMENTS
        for attack in data[experiment]["attacks"]
    ]
    defenses = [
        defense
        for experiment in CLOSED_LOOP_EXPERIMENTS
        for defense in data[experiment]["defenses"]
    ]

    aura_observation_context = sum(
        1
        for trace in aura_traces
        if observation_has_keys(
            trace,
            {
                "active_defense_actions",
                "recent_defense_actions",
                "last_defense_action",
            },
        )
    )
    tsra_observation_context = sum(
        1
        for trace in tsra_traces
        if observation_has_keys(
            trace,
            {
                "active_attack_count",
                "active_attack_types",
                "recent_attack_event_ids",
                "last_attack_type",
            },
        )
    )

    attack_tool_calls = tool_count(tsra_traces, "summarize_attack_context")
    defense_tool_calls = tool_count(aura_traces, "summarize_defense_context")
    all_tool_errors = tool_errors(aura_traces) + tool_errors(tsra_traces)
    tsra_feedback_context = sum(1 for trace in tsra_traces if feedback_context(trace, "attack_context"))
    aura_feedback_context = sum(1 for trace in aura_traces if feedback_context(trace, "defense_context"))
    tsra_memory_context = sum(1 for trace in tsra_traces if memory_context(trace, "attack_context"))
    aura_memory_context = sum(1 for trace in aura_traces if memory_context(trace, "defense_context"))
    attack_candidate_total, attack_candidate_context, attack_candidate_used = candidate_context_count(
        tsra_traces,
        "cross_agent_attack_context",
    )
    defense_candidate_total, defense_candidate_context, defense_candidate_used = candidate_context_count(
        aura_traces,
        "cross_agent_defense_context",
    )

    attack_handoffs = 0
    for experiment, attack in attacks:
        trace = first_trace_at_or_after(
            data[experiment]["tsra_traces"],
            attack_time(attack),
            5.0,
        )
        context = feedback_context(trace, "attack_context")
        recent_ids = set(context.get("recent_attack_event_ids") or [])
        if (
            attack.get("event_id") in recent_ids
            or as_float(context.get("active_attack_count")) > 0.0
        ):
            attack_handoffs += 1

    defense_context_seen_traces = sum(
        1
        for trace in aura_traces
        if feedback_context(trace, "defense_context").get("counter_defense_context_seen")
    )
    selected_attack_with_defense_context = sum(
        1
        for trace in aura_traces
        if selected_type(trace) == "attack_event"
        and feedback_context(trace, "defense_context").get("counter_defense_context_seen")
    )
    defense_context_after_first = 0
    for experiment in CLOSED_LOOP_EXPERIMENTS:
        experiment_defenses = data[experiment]["defenses"]
        if not experiment_defenses:
            continue
        first_defense = min(experiment_defenses, key=lambda event: as_float(event.get("time_sec")))
        after = [
            trace
            for trace in data[experiment]["aura_traces"]
            if trace_time(trace) >= as_float(first_defense.get("time_sec"))
        ]
        if any(
            feedback_context(trace, "defense_context").get("counter_defense_context_seen")
            for trace in after
        ):
            defense_context_after_first += 1

    related_context_events = sum(1 for event in defenses if event_related_context(event))
    active_related_events = sum(
        1
        for event in defenses
        if as_float(event_related_context(event).get("active_attack_count")) > 0.0
    )
    missing_related_context = len(defenses) - related_context_events
    aura_counter_candidates = [
        candidate
        for trace in aura_traces
        for candidate in trace.get("candidate_actions") or []
        if as_float(candidate.get("counter_defense_bonus")) > 0.0
    ]
    selected_counter_traces = [
        trace
        for trace in aura_traces
        if selected_type(trace) == "attack_event"
        and as_float(
            max(
                trace.get("candidate_actions") or [{}],
                key=lambda candidate: as_float(candidate.get("score")),
            ).get("counter_defense_bonus")
        )
        > 0.0
    ]
    counter_reasons = sorted(
        {
            str(candidate.get("counter_defense_reason", ""))
            for candidate in aura_counter_candidates
            if candidate.get("counter_defense_reason")
        }
    )
    tsra_attack_bonus_candidates = [
        candidate
        for trace in tsra_traces
        for candidate in trace.get("candidate_actions") or []
        if as_float(candidate.get("attack_context_bonus")) > 0.0
    ]
    tsra_attack_bonus_events = [
        event
        for event in defenses
        if as_float((event.get("details") or {}).get("attack_context_bonus")) > 0.0
    ]
    selected_defense_bonus_traces = [
        trace
        for trace in tsra_traces
        if selected_type(trace) == "defense_events"
        and any(
            as_float((event.get("details") or {}).get("attack_context_bonus")) > 0.0
            for event in (trace.get("selected_action") or {}).get("events") or []
        )
    ]
    defense_counter_reasons = sorted(
        {
            str(candidate.get("attack_context_score_reason", ""))
            for candidate in tsra_attack_bonus_candidates
            if candidate.get("attack_context_score_reason")
        }
    )
    multi_core_defense_traces = 0
    ordered_core_defense_traces = 0
    for trace in tsra_traces:
        if selected_type(trace) != "defense_events":
            continue
        core_events = [
            event
            for event in (trace.get("selected_action") or {}).get("events") or []
            if event.get("action") != "ml_attack_alert"
            and "defense_priority_score" in (event.get("details") or {})
        ]
        if len(core_events) <= 1:
            continue
        multi_core_defense_traces += 1
        scores = [
            as_float((event.get("details") or {}).get("defense_priority_score"))
            for event in core_events
        ]
        if scores == sorted(scores, reverse=True):
            ordered_core_defense_traces += 1

    return [
        row(
            check_id="XAG01",
            area="Shared observation context",
            requirement="AURA and TSRA-R observations should expose closed-loop opponent context fields.",
            evidence=[
                "outputs/experiments/*/aura_decision_traces.jsonl",
                "outputs/experiments/*/tsra_r_decision_traces.jsonl",
            ],
            observed=(
                f"aura_observation_context={aura_observation_context}/{len(aura_traces)}; "
                f"tsra_observation_context={tsra_observation_context}/{len(tsra_traces)}"
            ),
            ok=(
                bool(aura_traces)
                and bool(tsra_traces)
                and aura_observation_context == len(aura_traces)
                and tsra_observation_context == len(tsra_traces)
            ),
            interpretation="Both agents observe the same simulation clock plus opponent-context summaries.",
        ),
        row(
            check_id="XAG02",
            area="TSRA-R attack-context tool path",
            requirement="Every TSRA-R decision should call the attack-context tool and keep attack context in memory, feedback, and candidates.",
            evidence=["outputs/experiments/*/tsra_r_decision_traces.jsonl"],
            observed=(
                f"tsra_traces={len(tsra_traces)}; "
                f"summarize_attack_context={attack_tool_calls}; "
                f"feedback_attack_context={tsra_feedback_context}; "
                f"memory_attack_context={tsra_memory_context}; "
                f"candidate_attack_context={attack_candidate_context}/{attack_candidate_total}; "
                f"candidate_attack_context_used={attack_candidate_used}; "
                f"tool_errors={all_tool_errors}"
            ),
            ok=(
                bool(tsra_traces)
                and attack_tool_calls == len(tsra_traces)
                and tsra_feedback_context == len(tsra_traces)
                and tsra_memory_context == len(tsra_traces)
                and attack_candidate_context == attack_candidate_total
                and attack_candidate_used > 0
                and all_tool_errors == 0
            ),
            interpretation="TSRA-R is using AURA event context inside its agent loop, not only in downstream reports.",
        ),
        row(
            check_id="XAG03",
            area="Attack-to-defense handoff",
            requirement="Each AURA attack should be visible to the first TSRA-R decision in the immediate response window.",
            evidence=[
                "outputs/experiments/*/attack_events.jsonl",
                "outputs/experiments/*/tsra_r_decision_traces.jsonl",
            ],
            observed=(
                f"attack_handoffs={attack_handoffs}/{len(attacks)}; "
                f"response_window_sec=5"
            ),
            ok=bool(attacks) and attack_handoffs == len(attacks),
            interpretation="The defense agent receives attack context before it emits the response-window decisions.",
        ),
        row(
            check_id="XAG04",
            area="AURA defense-context tool path",
            requirement="Every AURA decision should call the defense-context tool and keep defense context in memory, feedback, and candidates.",
            evidence=["outputs/experiments/*/aura_decision_traces.jsonl"],
            observed=(
                f"aura_traces={len(aura_traces)}; "
                f"summarize_defense_context={defense_tool_calls}; "
                f"feedback_defense_context={aura_feedback_context}; "
                f"memory_defense_context={aura_memory_context}; "
                f"candidate_defense_context={defense_candidate_context}/{defense_candidate_total}; "
                f"candidate_defense_context_used={defense_candidate_used}; "
                f"selected_attack_with_defense_context={selected_attack_with_defense_context}"
            ),
            ok=(
                bool(aura_traces)
                and defense_tool_calls == len(aura_traces)
                and aura_feedback_context == len(aura_traces)
                and aura_memory_context == len(aura_traces)
                and defense_candidate_context == defense_candidate_total
                and defense_candidate_used > 0
                and selected_attack_with_defense_context > 0
            ),
            interpretation="AURA records the defender state that explains counter-defense choices such as failover chasing.",
        ),
        row(
            check_id="XAG05",
            area="Defense-to-attack handoff",
            requirement="After TSRA-R emits defenses, later AURA traces should carry active or recent defense context.",
            evidence=[
                "outputs/experiments/*/defense_events.jsonl",
                "outputs/experiments/*/aura_decision_traces.jsonl",
            ],
            observed=(
                f"experiments_with_post_defense_context={defense_context_after_first}/{len(CLOSED_LOOP_EXPERIMENTS)}; "
                f"defense_context_seen_traces={defense_context_seen_traces}; "
                f"selected_attack_with_defense_context={selected_attack_with_defense_context}"
            ),
            ok=(
                defense_context_after_first == len(CLOSED_LOOP_EXPERIMENTS)
                and defense_context_seen_traces > 0
                and selected_attack_with_defense_context > 0
            ),
            interpretation="The attack agent can see that TSRA-R has changed the battlefield before later attack selections.",
        ),
        row(
            check_id="XAG06",
            area="Event-level context consistency",
            requirement="Defense events emitted in closed-loop runs should carry related AURA attack context for auditability.",
            evidence=["outputs/experiments/*/defense_events.jsonl"],
            observed=(
                f"defense_events={len(defenses)}; "
                f"related_context_events={related_context_events}; "
                f"active_related_events={active_related_events}; "
                f"missing_related_context={missing_related_context}"
            ),
            ok=(
                bool(defenses)
                and related_context_events == len(defenses)
                and active_related_events > 0
                and missing_related_context == 0
            ),
            interpretation="Selected defense events retain the attack context that was visible during the decision.",
        ),
        row(
            check_id="XAG07",
            area="Context-to-policy score effect",
            requirement="AURA-ML should convert defender context into bounded counter-defense score adjustments.",
            evidence=["outputs/experiments/*/aura_decision_traces.jsonl"],
            observed=(
                f"counter_defense_bonus_candidates={len(aura_counter_candidates)}; "
                f"selected_counter_defense_bonus_traces={len(selected_counter_traces)}; "
                f"counter_defense_reasons={','.join(counter_reasons) if counter_reasons else 'none'}"
            ),
            ok=(
                len(aura_counter_candidates) > 0
                and len(selected_counter_traces) > 0
                and bool(counter_reasons)
            ),
            interpretation="AURA-ML does not merely log TSRA-R state; it uses that context as a bounded selection-score term.",
        ),
        row(
            check_id="XAG08",
            area="Attack-context defense priority effect",
            requirement="TSRA-R should convert AURA attack context into bounded defense priority scores and event ordering.",
            evidence=[
                "outputs/experiments/*/tsra_r_decision_traces.jsonl",
                "outputs/experiments/*/defense_events.jsonl",
            ],
            observed=(
                f"attack_context_bonus_candidates={len(tsra_attack_bonus_candidates)}; "
                f"attack_context_bonus_events={len(tsra_attack_bonus_events)}; "
                f"selected_defense_bonus_traces={len(selected_defense_bonus_traces)}; "
                f"ordered_core_defense_traces={ordered_core_defense_traces}/{multi_core_defense_traces}; "
                f"defense_counter_reasons={','.join(defense_counter_reasons) if defense_counter_reasons else 'none'}"
            ),
            ok=(
                len(tsra_attack_bonus_candidates) > 0
                and len(tsra_attack_bonus_events) > 0
                and len(selected_defense_bonus_traces) > 0
                and multi_core_defense_traces > 0
                and ordered_core_defense_traces == multi_core_defense_traces
                and bool(defense_counter_reasons)
            ),
            interpretation="TSRA-R does not merely log AURA state; it uses that context to score and order bounded defense actions.",
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
        "# Cross-Agent Context Audit",
        "",
        "This audit verifies that AURA and TSRA-R exchange opponent-context evidence through AgentRuntime observations, tool calls, memory, feedback, candidate rows, and emitted events.",
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
    parser = argparse.ArgumentParser(description="Audit AURA/TSRA-R cross-agent context flow.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any cross-agent context row fails.",
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
    failed = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {display_path(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.output_md)} ({len(rows)} rows)")
    if failed:
        print("Failed cross-agent context rows: " + ", ".join(row["check_id"] for row in failed))
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
