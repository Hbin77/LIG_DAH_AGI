from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/defense_priority_decision_path_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/defense_priority_decision_path_audit.md"
TRACE_GLOB = "outputs/experiments/*/tsra_r_decision_traces.jsonl"
SAFETY_BOUNDARY = (
    "closed simulation defense-priority decision-path audit only; no RF, exploit, or live network action"
)
CORE_ACTIONS = {"priority_reroute", "video_throttle", "stale_badge", "pace_switch"}

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
    rows = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def traces_with_experiment() -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(ROOT.glob(TRACE_GLOB)):
        experiment = path.parent.name
        rows.extend((experiment, trace) for trace in read_jsonl(path))
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


def selected_events(trace: dict[str, Any]) -> list[dict[str, Any]]:
    selected = trace.get("selected_action") or {}
    if selected.get("type") != "defense_events":
        return []
    return selected.get("events") or []


def selected_type(trace: dict[str, Any]) -> str:
    return str((trace.get("selected_action") or {}).get("type", ""))


def scored_candidates(rows: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    return [
        candidate
        for _, trace in rows
        for candidate in trace.get("candidate_actions") or []
        if "defense_base_score" in candidate
    ]


def priority_events(rows: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    return [
        event
        for _, trace in rows
        for event in selected_events(trace)
        if event.get("action") in CORE_ACTIONS
        and "defense_priority_score" in (event.get("details") or {})
    ]


def candidate_formula_ok(candidate: dict[str, Any]) -> bool:
    score = as_float(candidate.get("score"))
    base = as_float(candidate.get("defense_base_score"))
    bonus = as_float(candidate.get("attack_context_bonus"))
    return abs(score - (base + bonus)) <= 1e-6


def event_matches_candidate(event: dict[str, Any], candidate: dict[str, Any]) -> bool:
    details = event.get("details") or {}
    return (
        abs(as_float(details.get("defense_priority_score")) - as_float(candidate.get("score"))) <= 1e-6
        and abs(as_float(details.get("defense_base_score")) - as_float(candidate.get("defense_base_score"))) <= 1e-6
        and abs(as_float(details.get("attack_context_bonus")) - as_float(candidate.get("attack_context_bonus"))) <= 1e-6
        and str(details.get("attack_context_score_reason", ""))
        == str(candidate.get("attack_context_score_reason", ""))
    )


def ready_candidates(trace: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        candidate
        for candidate in trace.get("candidate_actions") or []
        if candidate.get("action") in CORE_ACTIONS
        and candidate.get("enabled") is True
        and candidate.get("eligible") is True
        and candidate.get("ready") is True
        and "defense_base_score" in candidate
    ]


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
    rows = traces_with_experiment()
    candidates = scored_candidates(rows)
    events = priority_events(rows)

    formula_matches = sum(1 for candidate in candidates if candidate_formula_ok(candidate))
    reason_count = sum(1 for candidate in candidates if candidate.get("attack_context_score_reason"))
    base_present = sum(1 for candidate in candidates if "defense_base_score" in candidate)

    max_score = max((as_float(candidate.get("score")) for candidate in candidates), default=0.0)
    max_bonus = max(
        (as_float(candidate.get("attack_context_bonus")) for candidate in candidates),
        default=0.0,
    )
    non_eligible_bonus = sum(
        1
        for candidate in candidates
        if not (candidate.get("enabled") is True and candidate.get("eligible") is True)
        and as_float(candidate.get("attack_context_bonus")) > 0.0
    )
    negative_scores = sum(1 for candidate in candidates if as_float(candidate.get("score")) < 0.0)
    over_bound_scores = sum(1 for candidate in candidates if as_float(candidate.get("score")) > 1.0)

    bonus_candidates = [
        candidate for candidate in candidates if as_float(candidate.get("attack_context_bonus")) > 0.0
    ]
    bonus_events = [
        event
        for event in events
        if as_float((event.get("details") or {}).get("attack_context_bonus")) > 0.0
    ]
    bonus_reasons = sorted(
        {
            str(candidate.get("attack_context_score_reason", ""))
            for candidate in bonus_candidates
            if candidate.get("attack_context_score_reason")
        }
    )

    checked_event_matches = 0
    event_match_failures = 0
    no_candidate_for_event = 0
    for _, trace in rows:
        candidate_by_action = {
            candidate.get("action"): candidate
            for candidate in trace.get("candidate_actions") or []
            if "defense_base_score" in candidate
        }
        if not candidate_by_action:
            continue
        for event in selected_events(trace):
            action = event.get("action")
            if action not in CORE_ACTIONS:
                continue
            details = event.get("details") or {}
            if "defense_priority_score" not in details:
                continue
            candidate = candidate_by_action.get(action)
            if not candidate:
                no_candidate_for_event += 1
                continue
            checked_event_matches += 1
            if not event_matches_candidate(event, candidate):
                event_match_failures += 1

    multi_core_traces = 0
    ordered_core_traces = 0
    for _, trace in rows:
        core_events = [
            event
            for event in selected_events(trace)
            if event.get("action") in CORE_ACTIONS
            and "defense_priority_score" in (event.get("details") or {})
        ]
        if len(core_events) <= 1:
            continue
        multi_core_traces += 1
        scores = [
            as_float((event.get("details") or {}).get("defense_priority_score"))
            for event in core_events
        ]
        if scores == sorted(scores, reverse=True):
            ordered_core_traces += 1

    no_op_traces = 0
    no_op_ready_violations = 0
    defense_event_traces = 0
    unselected_ready_actions = 0
    selected_without_ready = 0
    for _, trace in rows:
        if not any("defense_base_score" in candidate for candidate in trace.get("candidate_actions") or []):
            continue
        ready = {str(candidate.get("action")) for candidate in ready_candidates(trace)}
        selected = {
            str(event.get("action"))
            for event in selected_events(trace)
            if event.get("action") in CORE_ACTIONS
        }
        if selected_type(trace) == "no_op":
            no_op_traces += 1
            if ready:
                no_op_ready_violations += 1
        elif selected_type(trace) == "defense_events":
            defense_event_traces += 1
            unselected_ready_actions += len(ready - selected)
            selected_without_ready += len(selected - ready)

    return [
        row(
            check_id="DPR01",
            area="Candidate priority score contract",
            requirement="Every TSRA-R core defense candidate should expose a reproducible priority score formula.",
            evidence=[TRACE_GLOB],
            observed=(
                f"scored_candidates={len(candidates)}; base_score_present={base_present}; "
                f"formula_matches={formula_matches}; reason_count={reason_count}"
            ),
            ok=(
                len(candidates) > 0
                and base_present == len(candidates)
                and formula_matches == len(candidates)
                and reason_count == len(candidates)
            ),
            interpretation="TSRA-R candidate priority is explicit rather than implicit branch order.",
        ),
        row(
            check_id="DPR02",
            area="Bounded priority score inputs",
            requirement="Defense priority scores and attack-context bonuses should remain bounded and only apply to eligible actions.",
            evidence=[TRACE_GLOB],
            observed=(
                f"max_score={fmt(max_score)}; max_attack_context_bonus={fmt(max_bonus)}; "
                f"negative_scores={negative_scores}; over_bound_scores={over_bound_scores}; "
                f"non_eligible_bonus={non_eligible_bonus}"
            ),
            ok=(
                max_score <= 1.0
                and max_bonus <= 0.12
                and negative_scores == 0
                and over_bound_scores == 0
                and non_eligible_bonus == 0
            ),
            interpretation="The score term is bounded and cannot silently turn an ineligible defense into an emitted event.",
        ),
        row(
            check_id="DPR03",
            area="Attack-context priority bonus",
            requirement="AURA attack context should create bounded TSRA-R priority bonuses when the attack type matches the defense action.",
            evidence=[TRACE_GLOB],
            observed=(
                f"attack_context_bonus_candidates={len(bonus_candidates)}; "
                f"attack_context_bonus_events={len(bonus_events)}; "
                f"bonus_reasons={','.join(bonus_reasons) if bonus_reasons else 'none'}"
            ),
            ok=len(bonus_candidates) > 0 and len(bonus_events) > 0 and bool(bonus_reasons),
            interpretation="The defense agent uses attack context in its scoring path, not only in logs.",
        ),
        row(
            check_id="DPR04",
            area="Selected event score consistency",
            requirement="Selected Rule TSRA-R defense events should carry priority details matching their candidate row.",
            evidence=[TRACE_GLOB],
            observed=(
                f"checked_event_matches={checked_event_matches}; "
                f"event_match_failures={event_match_failures}; "
                f"no_candidate_for_event={no_candidate_for_event}"
            ),
            ok=checked_event_matches > 0 and event_match_failures == 0 and no_candidate_for_event == 0,
            interpretation="DefenseEvent details preserve the same priority evidence used in the decision trace.",
        ),
        row(
            check_id="DPR05",
            area="Core defense event ordering",
            requirement="When multiple core defenses are emitted in the same decision, their event order should follow priority score.",
            evidence=[TRACE_GLOB],
            observed=f"ordered_core_defense_traces={ordered_core_traces}/{multi_core_traces}",
            ok=multi_core_traces > 0 and ordered_core_traces == multi_core_traces,
            interpretation="The simulator receives same-tick core defenses in the order selected by the agent score.",
        ),
        row(
            check_id="DPR06",
            area="No-op and ready-action consistency",
            requirement="No-op traces should have no ready scored defense action, and selected events should not omit ready actions.",
            evidence=[TRACE_GLOB],
            observed=(
                f"no_op_traces={no_op_traces}; no_op_ready_violations={no_op_ready_violations}; "
                f"defense_event_traces={defense_event_traces}; "
                f"unselected_ready_actions={unselected_ready_actions}; "
                f"selected_without_ready={selected_without_ready}"
            ),
            ok=(
                no_op_traces > 0
                and defense_event_traces > 0
                and no_op_ready_violations == 0
                and unselected_ready_actions == 0
                and selected_without_ready == 0
            ),
            interpretation="Priority scoring refines defense ordering without weakening the existing eligibility and cooldown gates.",
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
        "# Defense Priority Decision Path Audit",
        "",
        "This audit verifies that TSRA-R defense priority scores are formula-backed, bounded, and connected to selected DefenseEvent ordering.",
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
    parser = argparse.ArgumentParser(description="Audit TSRA-R defense priority decision path.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit non-zero if any audit row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [item for item in rows if item["status"] != "pass"]
    if failed and args.fail_on_error:
        raise SystemExit(f"Defense priority decision path audit failed: {failed}")
    print(f"Wrote {args.output_csv.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {args.output_md.relative_to(ROOT)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
