from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENTS = [
    "E3_rule_aura",
    "E5_rule_aura_tsra_r",
    "E7_ml_aura_ml_tsra_r",
]
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/aura_coa_cards.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/aura_coa_cards.md")

FIELDNAMES = [
    "experiment",
    "event_id",
    "agent",
    "selected_at",
    "mission_phase",
    "active_link_at_decision",
    "attack_type",
    "target_link",
    "target_traffic_classes",
    "duration_sec",
    "simulated_effects",
    "expected_mission_impact",
    "expected_p95_critical_latency_sec",
    "expected_stale_data_ratio",
    "expected_priority_inversion_rate",
    "detectability_score",
    "attack_score",
    "selection_reason",
    "candidate_rank",
    "runner_up",
    "safety_boundary",
]

SAFETY_BOUNDARY = (
    "Simulated effect only: no RF transmission, no exploit, no real packet generation, "
    "no operational SATCOM parameters."
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def collect_cards(experiment_root: Path, experiments: list[str]) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for experiment in experiments:
        exp_dir = experiment_root / experiment
        attack_events = load_jsonl(exp_dir / "attack_events.jsonl")
        traces = load_jsonl(exp_dir / "aura_decision_traces.jsonl")
        trace_by_event = {
            trace.get("selected_action", {}).get("event_id"): trace
            for trace in traces
            if trace.get("selected_action", {}).get("type") == "attack_event"
        }
        for event in attack_events:
            if event.get("agent") == "fixed":
                continue
            cards.append(summarize_event(experiment, event, trace_by_event.get(event.get("event_id"))))
    return cards


def summarize_event(
    experiment: str,
    event: dict[str, Any],
    trace: dict[str, Any] | None,
) -> dict[str, str]:
    candidate = event.get("candidate") or {}
    expected = event.get("expected_impact") or {}
    observation = (trace or {}).get("observation") or {}
    candidates = (trace or {}).get("candidate_actions") or []
    rank, runner_up = rank_candidate(event, candidates)

    return {
        "experiment": experiment,
        "event_id": str(event.get("event_id", "")),
        "agent": str((trace or {}).get("agent") or event.get("agent", "")),
        "selected_at": format_float(event.get("selected_at")),
        "mission_phase": str(observation.get("mission_phase", "")),
        "active_link_at_decision": str(observation.get("active_link", "")),
        "attack_type": str(candidate.get("attack_type", "")),
        "target_link": str(candidate.get("target_link", "")),
        "target_traffic_classes": ", ".join(candidate.get("target_traffic_classes") or []),
        "duration_sec": format_float(candidate.get("duration_sec")),
        "simulated_effects": summarize_effects(candidate),
        "expected_mission_impact": format_float(expected.get("mission_impact")),
        "expected_p95_critical_latency_sec": format_float(expected.get("p95_critical_latency_sec")),
        "expected_stale_data_ratio": format_float(expected.get("stale_data_ratio")),
        "expected_priority_inversion_rate": format_float(expected.get("priority_inversion_rate")),
        "detectability_score": format_float(expected.get("detectability_score")),
        "attack_score": format_float(event.get("score")),
        "selection_reason": str(event.get("reason", "")),
        "candidate_rank": str(rank),
        "runner_up": runner_up,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def summarize_effects(candidate: dict[str, Any]) -> str:
    effects = []
    if float(candidate.get("latency_ms_add") or 0.0):
        effects.append(f"latency +{format_float(candidate.get('latency_ms_add'))}ms")
    if float(candidate.get("jitter_ms_add") or 0.0):
        effects.append(f"jitter +{format_float(candidate.get('jitter_ms_add'))}ms")
    if float(candidate.get("packet_loss_add") or 0.0):
        effects.append(f"loss +{format_float(candidate.get('packet_loss_add'))}")
    if candidate.get("bandwidth_limit_mbps") not in ("", None):
        effects.append(f"bandwidth cap {format_float(candidate.get('bandwidth_limit_mbps'))}Mbps")
    if candidate.get("queue_pressure"):
        effects.append("queue pressure enabled")
    return "; ".join(effects) if effects else "no additional simulated degradation"


def rank_candidate(event: dict[str, Any], candidates: list[dict[str, Any]]) -> tuple[int | str, str]:
    if not candidates:
        return "", ""
    ordered = sorted(candidates, key=lambda item: float(item.get("score") or 0.0), reverse=True)
    selected_type = (event.get("candidate") or {}).get("attack_type")
    selected_link = (event.get("candidate") or {}).get("target_link")
    rank: int | str = ""
    selected_score = float(event.get("score") or 0.0)
    for idx, candidate in enumerate(ordered, start=1):
        if candidate.get("action") == selected_type and candidate.get("target_link") == selected_link:
            rank = idx
            selected_score = float(candidate.get("score") or selected_score)
            break
    runner = next(
        (
            candidate
            for candidate in ordered
            if not (
                candidate.get("action") == selected_type
                and candidate.get("target_link") == selected_link
            )
        ),
        None,
    )
    if not runner:
        return rank, ""
    runner_score = float(runner.get("score") or 0.0)
    tie_note = " tied" if abs(runner_score - selected_score) < 1e-9 else ""
    return rank, (
        f"{runner.get('action')} on {runner.get('target_link')} "
        f"(score={format_float(runner.get('score'))}{tie_note}, "
        f"impact={format_float(runner.get('predicted_mission_impact'))})"
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# AURA COA Cards",
        "",
        "Each card describes a simulated attack-effect Course of Action selected by AURA.",
        "",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
    ]
    for idx, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"## COA-{idx:03d}: {row['experiment']} / {row['event_id']}",
                "",
                f"- Agent: {row['agent']}",
                f"- Time: {row['selected_at']} sec",
                f"- Mission phase: {row['mission_phase'] or 'unknown'}",
                f"- Active link at decision: {row['active_link_at_decision'] or 'unknown'}",
                f"- Attack type: `{row['attack_type']}`",
                f"- Target link: `{row['target_link']}`",
                f"- Target traffic classes: {row['target_traffic_classes'] or 'none'}",
                f"- Duration: {row['duration_sec']} sec",
                f"- Simulated effects: {row['simulated_effects']}",
                f"- Expected mission impact: {row['expected_mission_impact']}",
                f"- Expected p95 critical latency: {row['expected_p95_critical_latency_sec']} sec",
                f"- Expected stale data ratio: {row['expected_stale_data_ratio']}",
                f"- Expected priority inversion rate: {row['expected_priority_inversion_rate']}",
                f"- Detectability score: {row['detectability_score']}",
                f"- Attack score: {row['attack_score']}",
                f"- Candidate rank: {row['candidate_rank'] or 'unknown'}",
                f"- Runner-up: {row['runner_up'] or 'none'}",
                f"- Selection reason: {row['selection_reason']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def format_float(value: Any) -> str:
    if value in ("", None):
        return ""
    if isinstance(value, bool):
        return str(value)
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate safe AURA COA cards.")
    parser.add_argument(
        "--experiment-root",
        type=Path,
        default=Path("outputs/experiments"),
        help="Directory containing experiment subdirectories.",
    )
    parser.add_argument(
        "--experiments",
        nargs="*",
        default=DEFAULT_EXPERIMENTS,
        help="Experiment names to include.",
    )
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_cards(args.experiment_root, args.experiments)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} cards)")
    print(f"Wrote {args.output_md} ({len(rows)} cards)")


if __name__ == "__main__":
    main()
