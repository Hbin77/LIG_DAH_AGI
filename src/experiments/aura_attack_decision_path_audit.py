from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/aura_attack_decision_path_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/aura_attack_decision_path_audit.md"

EXPERIMENTS = (
    "E3_rule_aura",
    "E4_rule_aura_basic_defense",
    "E5_rule_aura_tsra_r",
    "E6_ml_aura_tsra_r",
    "E7_ml_aura_ml_tsra_r",
)
SAFETY_BOUNDARY = (
    "closed simulation AURA attack decision-path audit only; no RF, exploit, or live network action"
)
ALLOWED_ATTACK_AGENTS = {"AURA", "AURA-ML"}
REQUIRED_ATTACK_TYPES = {"queue_pressure", "failover_chasing", "stale_cop_induction"}
REQUIRED_TARGET_LINKS = {"SATCOM", "LTE", "MESH"}
REQUIRED_IMPACT_FIELDS = {
    "mission_impact",
    "detectability_score",
    "p95_critical_latency_sec",
    "priority_inversion_rate",
    "stale_data_ratio",
}

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
        if value in ("", None, "missing", "not_applicable"):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def traces_with_experiment() -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    for experiment in EXPERIMENTS:
        path = ROOT / "outputs" / "experiments" / experiment / "aura_decision_traces.jsonl"
        rows.extend((experiment, trace) for trace in read_jsonl(path))
    return rows


def events_with_experiment() -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    for experiment in EXPERIMENTS:
        path = ROOT / "outputs" / "experiments" / experiment / "attack_events.jsonl"
        rows.extend((experiment, event) for event in read_jsonl(path))
    return rows


def selected_action(trace: dict[str, Any]) -> dict[str, Any]:
    return trace.get("selected_action") or {}


def selected_type(trace: dict[str, Any]) -> str:
    return str(selected_action(trace).get("type", ""))


def event_by_experiment_id(
    events: list[tuple[str, dict[str, Any]]],
) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (experiment, str(event.get("event_id", ""))): event
        for experiment, event in events
        if event.get("event_id")
    }


def best_candidate(trace: dict[str, Any]) -> dict[str, Any]:
    candidates = trace.get("candidate_actions") or []
    if not candidates:
        return {}
    return max(candidates, key=lambda candidate: as_float(candidate.get("score")))


def tool_counts(traces: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for trace in traces:
        for call in trace.get("tool_calls") or []:
            counts[str(call.get("tool_name", ""))] += 1
    return counts


def tool_error_count(traces: list[dict[str, Any]]) -> int:
    return sum(
        1
        for trace in traces
        for call in trace.get("tool_calls") or []
        if call.get("status") != "ok"
    )


def candidate_identity_from_generated(candidate: dict[str, Any]) -> tuple:
    return (
        str(candidate.get("attack_type", "")),
        str(candidate.get("target_link", "")),
        tuple(candidate.get("target_traffic_classes") or []),
        as_float(candidate.get("start_time")),
        as_float(candidate.get("duration_sec")),
        as_float(candidate.get("latency_ms_add")),
        as_float(candidate.get("jitter_ms_add")),
        as_float(candidate.get("packet_loss_add")),
        candidate.get("bandwidth_limit_mbps"),
        bool(candidate.get("queue_pressure")),
    )


def candidate_identity_from_action(candidate: dict[str, Any]) -> tuple:
    return (
        str(candidate.get("action", "")),
        str(candidate.get("target_link", "")),
        tuple(candidate.get("target_traffic_classes") or []),
        as_float(candidate.get("start_time")),
        as_float(candidate.get("duration_sec")),
        as_float(candidate.get("latency_ms_add")),
        as_float(candidate.get("jitter_ms_add")),
        as_float(candidate.get("packet_loss_add")),
        candidate.get("bandwidth_limit_mbps"),
        bool(candidate.get("queue_pressure")),
    )


def generated_candidates(trace: dict[str, Any]) -> list[dict[str, Any]]:
    calls = [
        call
        for call in trace.get("tool_calls") or []
        if call.get("tool_name") == "generate_attack_candidates"
    ]
    if len(calls) != 1:
        return []
    output = calls[0].get("output_summary")
    return output if isinstance(output, list) else []


def base_score_formula_ok(candidate: dict[str, Any]) -> bool:
    predicted = as_float(candidate.get("predicted_mission_impact"))
    detectability = clamp(as_float(candidate.get("detectability_score")))
    expected = predicted - 0.15 * detectability
    score_field = "base_attack_score" if "base_attack_score" in candidate else "score"
    return abs(as_float(candidate.get(score_field)) - expected) <= 1e-5


def selection_score_formula_ok(candidate: dict[str, Any]) -> bool:
    if "base_attack_score" not in candidate:
        return base_score_formula_ok(candidate)
    base_score = as_float(candidate.get("base_attack_score"))
    objective_bonus = as_float(candidate.get("objective_bonus"))
    counter_bonus = as_float(candidate.get("counter_defense_bonus"))
    repeated_penalty = as_float(candidate.get("repeated_tactic_penalty"))
    expected = base_score + objective_bonus + counter_bonus - repeated_penalty
    return abs(as_float(candidate.get("score")) - expected) <= 1e-5


def event_score_formula_ok(event: dict[str, Any]) -> bool:
    expected = event.get("expected_impact") or {}
    mission_impact = as_float(expected.get("mission_impact"))
    detectability = clamp(as_float(expected.get("detectability_score")))
    base_score = mission_impact - 0.15 * detectability
    if "base_attack_score" in expected:
        selection_score = as_float(expected.get("selection_score"))
        return (
            abs(as_float(expected.get("base_attack_score")) - base_score) <= 1e-5
            and abs(as_float(event.get("score")) - selection_score) <= 1e-5
        )
    return abs(as_float(event.get("score")) - base_score) <= 1e-5


def attack_time(event: dict[str, Any]) -> float:
    candidate = event.get("candidate") or {}
    return as_float(event.get("selected_at") or candidate.get("start_time"))


def trace_threshold(trace: dict[str, Any]) -> float:
    return as_float((trace.get("feedback") or {}).get("attack_threshold"), 0.12)


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
    traces = traces_with_experiment()
    events = events_with_experiment()
    events_by_id = event_by_experiment_id(events)

    attack_traces = [
        (experiment, trace)
        for experiment, trace in traces
        if selected_type(trace) == "attack_event"
    ]
    noop_traces = [
        (experiment, trace)
        for experiment, trace in traces
        if selected_type(trace) == "no_op"
    ]
    candidate_traces = [
        trace for _, trace in traces if trace.get("candidate_actions")
    ]
    candidates = [
        candidate
        for _, trace in traces
        for candidate in trace.get("candidate_actions") or []
    ]
    rule_candidates = [candidate for candidate in candidates if "base_attack_score" not in candidate]
    ml_candidates = [candidate for candidate in candidates if "base_attack_score" in candidate]
    base_formula_matches = sum(1 for candidate in candidates if base_score_formula_ok(candidate))
    selection_formula_matches = sum(
        1 for candidate in candidates if selection_score_formula_ok(candidate)
    )

    candidate_tool_counts = tool_counts(candidate_traces)
    candidate_tool_errors = tool_error_count(candidate_traces)
    all_tool_counts = tool_counts([trace for _, trace in traces])
    all_tool_errors = tool_error_count([trace for _, trace in traces])
    generated_candidate_total = 0
    generated_candidate_payload_matches = 0
    generated_candidate_payload_mismatches = 0
    for trace in candidate_traces:
        generated = generated_candidates(trace)
        generated_candidate_total += len(generated)
        generated_identities = [
            candidate_identity_from_generated(candidate) for candidate in generated
        ]
        action_identities = [
            candidate_identity_from_action(candidate)
            for candidate in trace.get("candidate_actions") or []
        ]
        if generated_identities and generated_identities == action_identities:
            generated_candidate_payload_matches += 1
        else:
            generated_candidate_payload_mismatches += 1

    selected_matches_top = 0
    linked_attack_events = 0
    score_event_matches = 0
    type_link_event_matches = 0
    event_time_matches = 0
    threshold_passes = 0
    event_agent_matches_trace = 0
    for experiment, trace in attack_traces:
        selected = selected_action(trace)
        best = best_candidate(trace)
        event = events_by_id.get((experiment, str(selected.get("event_id", ""))), {})
        if (
            best
            and selected.get("attack_type") == best.get("action")
            and selected.get("target_link") == best.get("target_link")
            and abs(as_float(selected.get("score")) - as_float(best.get("score"))) <= 1e-6
        ):
            selected_matches_top += 1
        if event:
            linked_attack_events += 1
            candidate = event.get("candidate") or {}
            if abs(as_float(event.get("score")) - as_float(selected.get("score"))) <= 1e-6:
                score_event_matches += 1
            if (
                candidate.get("attack_type") == selected.get("attack_type")
                and candidate.get("target_link") == selected.get("target_link")
            ):
                type_link_event_matches += 1
            if abs(as_float(event.get("selected_at")) - as_float(trace.get("time_sec"))) <= 1e-6:
                event_time_matches += 1
            if str(event.get("agent", "")) == str(trace.get("agent", "")):
                event_agent_matches_trace += 1
        if as_float(selected.get("score")) >= trace_threshold(trace):
            threshold_passes += 1

    pre_start_noops = sum(
        1 for _, trace in noop_traces if "waiting for min_start_sec" in str(trace.get("reason", ""))
    )
    cooldown_noops = sum(
        1 for _, trace in noop_traces if "cooldown" in str(trace.get("reason", ""))
    )
    max_event_noops = sum(
        1 for _, trace in noop_traces if "max_events" in str(trace.get("reason", ""))
    )
    below_threshold_noops = sum(
        1 for _, trace in noop_traces if "below attack threshold" in str(trace.get("reason", ""))
    )
    no_candidate_noops = sum(
        1 for _, trace in noop_traces if "no candidate actions generated" in str(trace.get("reason", ""))
    )
    no_op_threshold_violations = 0
    for _, trace in noop_traces:
        best = best_candidate(trace)
        if best and as_float(best.get("score")) >= trace_threshold(trace):
            no_op_threshold_violations += 1

    event_counts_by_experiment = Counter(experiment for experiment, _ in events)
    event_budget_violations = sum(
        1 for experiment in EXPERIMENTS if event_counts_by_experiment[experiment] > 5
    )
    pre_start_attack_events = sum(1 for _, event in events if attack_time(event) < 60.0)
    attack_gaps = []
    for experiment in EXPERIMENTS:
        times = sorted(attack_time(event) for exp, event in events if exp == experiment)
        attack_gaps.extend(later - earlier for earlier, later in zip(times, times[1:]))
    min_attack_gap = min(attack_gaps, default=0.0)
    cooldown_gap_violations = sum(1 for gap in attack_gaps if gap < 45.0)

    impact_field_matches = sum(
        1
        for _, event in events
        if REQUIRED_IMPACT_FIELDS.issubset((event.get("expected_impact") or {}).keys())
    )
    event_score_formula_matches = sum(1 for _, event in events if event_score_formula_ok(event))
    selected_at_matches_candidate = sum(
        1
        for _, event in events
        if abs(as_float(event.get("selected_at")) - as_float((event.get("candidate") or {}).get("start_time"))) <= 1e-6
    )
    allowed_agent_events = sum(
        1 for _, event in events if str(event.get("agent", "")) in ALLOWED_ATTACK_AGENTS
    )
    allowed_attack_type_events = sum(
        1
        for _, event in events
        if str((event.get("candidate") or {}).get("attack_type", ""))
        in {
            "link_degradation",
            "bandwidth_limit",
            "queue_pressure",
            "critical_window_degradation",
            "stale_cop_induction",
            "failover_chasing",
        }
    )

    attack_types = {
        str((event.get("candidate") or {}).get("attack_type", ""))
        for _, event in events
    }
    target_links = {
        str((event.get("candidate") or {}).get("target_link", ""))
        for _, event in events
    }
    defense_context_candidates = sum(
        1 for candidate in candidates if candidate.get("cross_agent_defense_context")
    )
    defense_context_used_candidates = sum(
        1 for candidate in candidates if candidate.get("cross_agent_defense_context_used")
    )
    selected_with_defense_context = 0
    for _, trace in attack_traces:
        selected = selected_action(trace)
        for candidate in trace.get("candidate_actions") or []:
            if (
                candidate.get("action") == selected.get("attack_type")
                and candidate.get("target_link") == selected.get("target_link")
                and candidate.get("cross_agent_defense_context_used")
            ):
                selected_with_defense_context += 1
                break
    objective_bonus_candidates = sum(
        1 for candidate in candidates if as_float(candidate.get("objective_bonus")) > 0.0
    )
    counter_defense_bonus_candidates = sum(
        1 for candidate in candidates if as_float(candidate.get("counter_defense_bonus")) > 0.0
    )
    ml_agent_events = sum(1 for _, event in events if event.get("agent") == "AURA-ML")
    rule_agent_events = sum(1 for _, event in events if event.get("agent") == "AURA")

    return [
        row(
            check_id="AAP01",
            area="Candidate score contract",
            requirement=(
                "Every AURA candidate should expose a reproducible attack score formula; "
                "AURA-ML should additionally expose the bounded selection-score formula."
            ),
            evidence=["outputs/experiments/*/aura_decision_traces.jsonl"],
            observed=(
                f"candidate_total={len(candidates)}; rule_candidates={len(rule_candidates)}; "
                f"ml_candidates={len(ml_candidates)}; base_formula_matches={base_formula_matches}; "
                f"selection_formula_matches={selection_formula_matches}"
            ),
            ok=(
                len(candidates) >= 100
                and base_formula_matches == len(candidates)
                and selection_formula_matches == len(candidates)
                and len(rule_candidates) > 0
                and len(ml_candidates) > 0
            ),
            interpretation=(
                "AURA candidate ranking is formula-backed instead of relying on implicit branch order."
            ),
        ),
        row(
            check_id="AAP02",
            area="Candidate scoring toolchain",
            requirement=(
                "Candidate-generating traces should call candidate generation once, estimate effect "
                "and detectability for each candidate, and call ML prediction for each ML candidate."
            ),
            evidence=["outputs/experiments/*/aura_decision_traces.jsonl"],
            observed=(
                f"candidate_traces={len(candidate_traces)}; candidate_total={len(candidates)}; "
                f"generated_candidate_total={generated_candidate_total}; "
                f"generated_candidate_payload_matches={generated_candidate_payload_matches}; "
                f"generated_candidate_payload_mismatches={generated_candidate_payload_mismatches}; "
                f"generate_attack_candidates={candidate_tool_counts['generate_attack_candidates']}; "
                f"estimate_candidate_effect={candidate_tool_counts['estimate_candidate_effect']}; "
                f"estimate_detectability={candidate_tool_counts['estimate_detectability']}; "
                f"predict_candidate_impact={candidate_tool_counts['predict_candidate_impact']}; "
                f"tool_errors={candidate_tool_errors}; all_trace_tool_errors={all_tool_errors}"
            ),
            ok=(
                len(candidate_traces) == len(attack_traces)
                and generated_candidate_total == len(candidates)
                and generated_candidate_payload_matches == len(candidate_traces)
                and generated_candidate_payload_mismatches == 0
                and candidate_tool_counts["generate_attack_candidates"] == len(candidate_traces)
                and candidate_tool_counts["estimate_candidate_effect"] == len(candidates)
                and candidate_tool_counts["estimate_detectability"] == len(candidates)
                and candidate_tool_counts["predict_candidate_impact"] == len(ml_candidates)
                and candidate_tool_errors == 0
                and all_tool_errors == 0
            ),
            interpretation=(
                "AURA uses AgentRuntime tools for generation and scoring rather than hidden inline state, "
                "and generated candidate payloads match the candidate_actions that are actually scored."
            ),
        ),
        row(
            check_id="AAP03",
            area="Top-score selection and event link",
            requirement=(
                "Selected attack events should match the highest-scored candidate and the persisted "
                "AttackEvent log by id, score, type, link, time, and agent."
            ),
            evidence=[
                "outputs/experiments/*/aura_decision_traces.jsonl",
                "outputs/experiments/*/attack_events.jsonl",
            ],
            observed=(
                f"attack_trace_count={len(attack_traces)}; attack_event_count={len(events)}; "
                f"selected_matches_top_candidate={selected_matches_top}; "
                f"linked_attack_events={linked_attack_events}; score_event_matches={score_event_matches}; "
                f"type_link_event_matches={type_link_event_matches}; event_time_matches={event_time_matches}; "
                f"event_agent_matches_trace={event_agent_matches_trace}; threshold_passes={threshold_passes}"
            ),
            ok=(
                len(attack_traces) == len(events) == 25
                and selected_matches_top == len(attack_traces)
                and linked_attack_events == len(attack_traces)
                and score_event_matches == len(attack_traces)
                and type_link_event_matches == len(attack_traces)
                and event_time_matches == len(attack_traces)
                and event_agent_matches_trace == len(attack_traces)
                and threshold_passes == len(attack_traces)
            ),
            interpretation=(
                "AURA selected actions are directly traceable to event logs and threshold support."
            ),
        ),
        row(
            check_id="AAP04",
            area="No-op and cadence gate discipline",
            requirement=(
                "AURA should avoid pre-start attacks, respect cooldown gaps and max-event budget, "
                "and never choose no-op while a candidate is above threshold."
            ),
            evidence=[
                "outputs/experiments/*/aura_decision_traces.jsonl",
                "outputs/experiments/*/attack_events.jsonl",
            ],
            observed=(
                f"noop_traces={len(noop_traces)}; pre_start_noops={pre_start_noops}; "
                f"cooldown_noops={cooldown_noops}; max_event_noops={max_event_noops}; "
                f"below_threshold_noops={below_threshold_noops}; no_candidate_noops={no_candidate_noops}; "
                f"pre_start_attack_events={pre_start_attack_events}; min_attack_gap_sec={fmt(min_attack_gap)}; "
                f"cooldown_gap_violations={cooldown_gap_violations}; event_budget_violations={event_budget_violations}; "
                f"no_op_threshold_violations={no_op_threshold_violations}"
            ),
            ok=(
                pre_start_noops > 0
                and cooldown_noops > 0
                and max_event_noops > 0
                and pre_start_attack_events == 0
                and min_attack_gap >= 45.0
                and cooldown_gap_violations == 0
                and event_budget_violations == 0
                and no_op_threshold_violations == 0
            ),
            interpretation=(
                "AURA is an agent with start, cadence, threshold, and event-budget gates, not an always-fire loop."
            ),
        ),
        row(
            check_id="AAP05",
            area="AttackEvent payload consistency",
            requirement=(
                "Persisted AttackEvent payloads should carry mission-impact fields, score formula evidence, "
                "valid agent labels, valid attack types, and candidate start-time consistency."
            ),
            evidence=["outputs/experiments/*/attack_events.jsonl"],
            observed=(
                f"event_payloads={len(events)}; impact_field_matches={impact_field_matches}; "
                f"event_score_formula_matches={event_score_formula_matches}; "
                f"selected_at_matches_candidate={selected_at_matches_candidate}; "
                f"allowed_agent_events={allowed_agent_events}; allowed_attack_type_events={allowed_attack_type_events}; "
                f"rule_agent_events={rule_agent_events}; ml_agent_events={ml_agent_events}"
            ),
            ok=(
                len(events) == 25
                and impact_field_matches == len(events)
                and event_score_formula_matches == len(events)
                and selected_at_matches_candidate == len(events)
                and allowed_agent_events == len(events)
                and allowed_attack_type_events == len(events)
                and rule_agent_events == 15
                and ml_agent_events == 10
            ),
            interpretation=(
                "AttackEvent logs preserve the same decision evidence and agent identity used by traces."
            ),
        ),
        row(
            check_id="AAP06",
            area="Tactical and defense-context coverage",
            requirement=(
                "AURA should cover multiple simulated tactics and links, carry defense context into "
                "candidate rows, and expose bounded objective/counter-defense score evidence."
            ),
            evidence=[
                "outputs/experiments/*/aura_decision_traces.jsonl",
                "outputs/experiments/*/attack_events.jsonl",
            ],
            observed=(
                f"attack_types={','.join(sorted(attack_types))}; "
                f"target_links={','.join(sorted(target_links))}; "
                f"defense_context_candidates={defense_context_candidates}; "
                f"defense_context_used_candidates={defense_context_used_candidates}; "
                f"selected_with_defense_context={selected_with_defense_context}; "
                f"objective_bonus_candidates={objective_bonus_candidates}; "
                f"counter_defense_bonus_candidates={counter_defense_bonus_candidates}; "
                f"summarize_defense_context={all_tool_counts['summarize_defense_context']}"
            ),
            ok=(
                REQUIRED_ATTACK_TYPES.issubset(attack_types)
                and REQUIRED_TARGET_LINKS.issubset(target_links)
                and defense_context_candidates == len(candidates)
                and defense_context_used_candidates > 0
                and selected_with_defense_context > 0
                and objective_bonus_candidates > 0
                and counter_defense_bonus_candidates > 0
                and all_tool_counts["summarize_defense_context"] == len(traces)
            ),
            interpretation=(
                "AURA/AURA-ML expose mission-tactic coverage and use TSRA-R context as bounded score evidence."
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
        "# AURA Attack Decision Path Audit",
        "",
        "This audit verifies that AURA and AURA-ML candidate scoring, selected actions, AttackEvent payloads, cadence gates, and defense-context score terms stay connected.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| check_id | area | status | observed | interpretation |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            f"| {item['check_id']} | {item['area']} | {item['status']} | "
            f"{item['observed']} | {item['interpretation']} |"
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
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit AURA attack decision path.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--fail-on-error", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {args.output_md.relative_to(ROOT)} ({len(rows)} rows)")
    if args.fail_on_error:
        failed = [item for item in rows if item["status"] != "pass"]
        if failed:
            raise SystemExit(
                "AURA attack decision path audit failed: "
                + ", ".join(f"{item['check_id']}:{item['area']}" for item in failed)
            )


if __name__ == "__main__":
    main()
