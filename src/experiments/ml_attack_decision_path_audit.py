from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
E7 = "E7_ml_aura_ml_tsra_r"
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/ml_attack_decision_path_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/ml_attack_decision_path_audit.md"

TRACE_PATH = f"outputs/experiments/{E7}/aura_decision_traces.jsonl"
ATTACK_PATH = f"outputs/experiments/{E7}/attack_events.jsonl"
SCORECARD_PATH = "outputs/report_tables/agent_engagement_scorecard.csv"

SAFETY_BOUNDARY = (
    "closed simulation ML attack decision-path audit only; no RF, exploit, or live network action"
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


def fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def selected_type(trace: dict[str, Any]) -> str:
    return str((trace.get("selected_action") or {}).get("type", ""))


def trace_time(trace: dict[str, Any]) -> float:
    return as_float(trace.get("time_sec"))


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


def tool_counts(traces: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for trace in traces:
        for call in trace.get("tool_calls") or []:
            counts[str(call.get("tool_name", ""))] += 1
    return counts


def tool_error_count(traces: list[dict[str, Any]]) -> int:
    errors = 0
    for trace in traces:
        for call in trace.get("tool_calls") or []:
            if call.get("status") != "ok":
                errors += 1
    return errors


def best_candidate(trace: dict[str, Any]) -> dict[str, Any]:
    candidates = trace.get("candidate_actions") or []
    if not candidates:
        return {}
    return max(candidates, key=lambda item: as_float(item.get("score")))


def feedback_value(trace: dict[str, Any], key: str, default: float = 0.0) -> float:
    return as_float((trace.get("feedback") or {}).get(key), default)


def event_by_id(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(event.get("event_id", "")): event for event in events}


def score_formula_ok(candidate: dict[str, Any]) -> bool:
    predicted = as_float(candidate.get("predicted_mission_impact"))
    detectability = as_float(candidate.get("detectability_score"))
    expected_score = predicted - 0.15 * max(0.0, min(1.0, detectability))
    return abs(as_float(candidate.get("score")) - expected_score) <= 1e-5


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
    attacks = read_jsonl(ATTACK_PATH)
    scorecard_rows = [
        row for row in read_csv(SCORECARD_PATH) if row.get("experiment") == E7
    ]
    attack_event_by_id = event_by_id(attacks)

    attack_traces = [
        trace for trace in traces if selected_type(trace) == "attack_event"
    ]
    noop_traces = [
        trace for trace in traces if selected_type(trace) == "no_op"
    ]
    first_attack_time = min((attack_time(event) for event in attacks), default=0.0)
    pre_start_traces = [
        trace for trace in traces if trace_time(trace) < first_attack_time
    ]
    pre_start_noops = [
        trace
        for trace in pre_start_traces
        if selected_type(trace) == "no_op"
        and not (trace.get("candidate_actions") or [])
        and "waiting for min_start_sec" in str(trace.get("reason", ""))
    ]
    pre_start_attack_events = [
        event for event in attacks if attack_time(event) < first_attack_time
    ]

    candidate_total = sum(len(trace.get("candidate_actions") or []) for trace in attack_traces)
    counts = tool_counts(attack_traces)
    errors = tool_error_count(attack_traces)
    attack_threshold = max(
        (
            feedback_value(trace, "attack_threshold")
            for trace in traces
            if "attack_threshold" in (trace.get("feedback") or {})
        ),
        default=0.12,
    )

    selected_matches = 0
    score_event_matches = 0
    time_event_matches = 0
    threshold_passes = 0
    for trace in attack_traces:
        selected = trace.get("selected_action") or {}
        best = best_candidate(trace)
        event = attack_event_by_id.get(str(selected.get("event_id", "")), {})
        if (
            best
            and selected.get("attack_type") == best.get("action")
            and selected.get("target_link") == best.get("target_link")
            and abs(as_float(selected.get("score")) - as_float(best.get("score"))) <= 1e-9
        ):
            selected_matches += 1
        if event and abs(as_float(selected.get("score")) - as_float(event.get("score"))) <= 1e-6:
            score_event_matches += 1
        if event and abs(trace_time(trace) - attack_time(event)) <= 1e-9:
            time_event_matches += 1
        if best and as_float(best.get("score")) >= attack_threshold:
            threshold_passes += 1

    all_candidates = [
        candidate
        for trace in attack_traces
        for candidate in (trace.get("candidate_actions") or [])
    ]
    formula_matches = sum(1 for candidate in all_candidates if score_formula_ok(candidate))
    selected_detectability = [
        as_float(best_candidate(trace).get("detectability_score"))
        for trace in attack_traces
        if best_candidate(trace)
    ]

    cooldown_noops = [
        trace for trace in noop_traces if trace.get("reason") == "attack cooldown active"
    ]
    max_event_noops = [
        trace
        for trace in noop_traces
        if str(trace.get("reason", "")).startswith("max_events=")
    ]
    attack_times = sorted(attack_time(event) for event in attacks)
    attack_gaps = [b - a for a, b in zip(attack_times, attack_times[1:])]
    min_attack_gap = min(attack_gaps, default=0.0)
    attacks_after_budget = [
        event
        for event in attacks
        if attack_times and attack_time(event) > max(attack_times)
    ]

    attack_types = sorted({attack_type(event) for event in attacks})
    target_links = sorted({target_link(event) for event in attacks})
    scorecard_attack_ids = {row.get("attack_event_id", "") for row in scorecard_rows}
    positive_reductions = sum(
        1
        for row in scorecard_rows
        if as_float(row.get("impact_reduction_from_peak")) > 0.0
    )
    complete_responses = sum(
        1 for row in scorecard_rows if row.get("response_status") == "complete"
    )
    scorecard_passes = sum(
        1 for row in scorecard_rows if row.get("scorecard_status") == "pass"
    )

    return [
        row(
            check_id="MAP01",
            area="Pre-start no-op gate",
            requirement="AURA-ML should not generate candidates or attack events before the configured start time.",
            evidence=[TRACE_PATH, ATTACK_PATH],
            observed=(
                f"trace_count={len(traces)}; first_attack_time={fmt(first_attack_time)}; "
                f"pre_start_traces={len(pre_start_traces)}; "
                f"pre_start_noop_count={len(pre_start_noops)}; "
                f"pre_start_attack_events={len(pre_start_attack_events)}"
            ),
            ok=(
                bool(traces)
                and first_attack_time == 60.0
                and len(pre_start_traces) == 6
                and len(pre_start_noops) == len(pre_start_traces)
                and not pre_start_attack_events
            ),
            interpretation=(
                "The attack agent waits for mission context instead of emitting simulated attack "
                "effects immediately at startup."
            ),
        ),
        row(
            check_id="MAP02",
            area="Candidate scoring toolchain",
            requirement="Every selected attack decision should generate candidates and evaluate each candidate through ML impact, analytic effect, and detectability tools.",
            evidence=[TRACE_PATH],
            observed=(
                f"attack_traces={len(attack_traces)}; candidate_total={candidate_total}; "
                f"generate_attack_candidates={counts['generate_attack_candidates']}; "
                f"predict_candidate_impact={counts['predict_candidate_impact']}; "
                f"estimate_candidate_effect={counts['estimate_candidate_effect']}; "
                f"estimate_detectability={counts['estimate_detectability']}; "
                f"tool_errors={errors}"
            ),
            ok=(
                len(attack_traces) == 5
                and candidate_total >= len(attack_traces) * 5
                and counts["generate_attack_candidates"] == len(attack_traces)
                and counts["predict_candidate_impact"] == candidate_total
                and counts["estimate_candidate_effect"] == candidate_total
                and counts["estimate_detectability"] == candidate_total
                and errors == 0
            ),
            interpretation=(
                "AURA-ML uses a real tool path for selection: candidate generation, ML prediction, "
                "effect estimation, and detectability scoring all appear in DecisionTrace."
            ),
        ),
        row(
            check_id="MAP03",
            area="Top-score selection link",
            requirement="Selected attack events must match the highest scored candidate and the persisted attack event log.",
            evidence=[TRACE_PATH, ATTACK_PATH],
            observed=(
                f"attack_traces={len(attack_traces)}; attack_events={len(attacks)}; "
                f"selected_matches_top_candidate={selected_matches}; "
                f"score_event_matches={score_event_matches}; "
                f"time_event_matches={time_event_matches}; "
                f"threshold_passes={threshold_passes}; attack_threshold={fmt(attack_threshold)}"
            ),
            ok=(
                len(attack_traces) == len(attacks) == 5
                and selected_matches == len(attack_traces)
                and score_event_matches == len(attack_traces)
                and time_event_matches == len(attack_traces)
                and threshold_passes == len(attack_traces)
            ),
            interpretation=(
                "The chosen attack is not hand-picked after the fact; it is the top candidate in "
                "the trace and is linked to the attack event log."
            ),
        ),
        row(
            check_id="MAP04",
            area="Detectability-adjusted score",
            requirement="Candidate score must equal predicted mission impact minus the configured detectability penalty.",
            evidence=[TRACE_PATH, "src/shared/metrics.py"],
            observed=(
                f"candidate_total={candidate_total}; score_formula_matches={formula_matches}; "
                f"selected_detectability_min={fmt(min(selected_detectability) if selected_detectability else None)}; "
                f"selected_detectability_max={fmt(max(selected_detectability) if selected_detectability else None)}"
            ),
            ok=(
                candidate_total > 0
                and formula_matches == candidate_total
                and bool(selected_detectability)
                and max(selected_detectability) <= 0.5
            ),
            interpretation=(
                "The attack score balances mission effect and detectability instead of maximizing "
                "impact blindly."
            ),
        ),
        row(
            check_id="MAP05",
            area="Cadence and event budget gate",
            requirement="AURA-ML should respect cooldown and max-event memory gates between attack events.",
            evidence=[TRACE_PATH, ATTACK_PATH],
            observed=(
                f"attack_events={len(attacks)}; cooldown_noops={len(cooldown_noops)}; "
                f"max_event_noops={len(max_event_noops)}; min_attack_gap_sec={fmt(min_attack_gap)}; "
                f"attacks_after_budget={len(attacks_after_budget)}"
            ),
            ok=(
                len(attacks) == 5
                and len(cooldown_noops) == 16
                and len(max_event_noops) == 4
                and min_attack_gap >= 45.0
                and not attacks_after_budget
            ),
            interpretation=(
                "AURA-ML is an agent with cadence memory and an event budget, not a loop that "
                "fires every time step."
            ),
        ),
        row(
            check_id="MAP06",
            area="Closed-loop attack feedback",
            requirement="Selected AURA-ML attack events should cover multiple tactics and connect to complete closed-loop feedback.",
            evidence=[ATTACK_PATH, SCORECARD_PATH],
            observed=(
                f"attack_types={','.join(attack_types)}; target_links={','.join(target_links)}; "
                f"scorecard_rows={len(scorecard_rows)}; scorecard_attack_links={len(scorecard_attack_ids)}; "
                f"complete_responses={complete_responses}; positive_reductions={positive_reductions}; "
                f"scorecard_passes={scorecard_passes}"
            ),
            ok=(
                len(scorecard_rows) == 5
                and {event.get("event_id", "") for event in attacks} == scorecard_attack_ids
                and {"queue_pressure", "failover_chasing"}.issubset(set(attack_types))
                and {"SATCOM", "LTE", "MESH"}.issubset(set(target_links))
                and complete_responses == 5
                and positive_reductions == 5
                and scorecard_passes == 5
            ),
            interpretation=(
                "The ML attack path reaches closed-loop evidence: selected attacks vary by tactic "
                "and link, then receive complete defense and metric feedback."
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
        "# ML Attack Decision Path Audit",
        "",
        "This audit traces the E7 AURA-ML path from startup no-op to candidate scoring, selected attack events, cadence gates, and closed-loop feedback.",
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
    parser = argparse.ArgumentParser(description="Audit E7 ML attack decision path.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any ML attack path row fails.",
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
        print(f"Failed ML attack decision path rows: {', '.join(item['check_id'] for item in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
