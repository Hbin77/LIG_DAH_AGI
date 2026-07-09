from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


DEFAULT_EPISODES = Path("outputs/report_tables/closed_loop_episode_replay.csv")
DEFAULT_MARGIN_AUDIT = Path("outputs/report_tables/agent_decision_margin_audit.csv")
DEFAULT_DEFENSE_LEDGER = Path("outputs/report_tables/defense_effectiveness_ledger.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_engagement_scorecard.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_engagement_scorecard.md")

SAFETY_BOUNDARY = (
    "closed simulation agent-engagement scorecard only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "episode_id",
    "attack_event_id",
    "attack_time_sec",
    "attack_agent",
    "attack_type",
    "target_link",
    "attack_decision_basis",
    "attack_selection_margin",
    "attack_threshold_margin",
    "response_status",
    "first_required_response_latency_sec",
    "covered_required_defenses",
    "defense_event_count_in_window",
    "improved_defense_events",
    "held_defense_events",
    "degraded_or_delayed_defense_events",
    "defense_actions_in_window",
    "start_mission_impact",
    "peak_mission_impact",
    "end_mission_impact",
    "impact_reduction_from_peak",
    "outcome",
    "scorecard_status",
    "scorecard_notes",
    "safety_boundary",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_float(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def collect_rows(
    episodes_path: Path = DEFAULT_EPISODES,
    margin_path: Path = DEFAULT_MARGIN_AUDIT,
    ledger_path: Path = DEFAULT_DEFENSE_LEDGER,
) -> list[dict[str, str]]:
    episodes = read_csv(episodes_path)
    margin_rows = read_csv(margin_path)
    ledger_rows = read_csv(ledger_path)
    output_rows = []
    for episode in episodes:
        output_rows.append(
            build_scorecard_row(
                episode=episode,
                margin=find_attack_margin(episode, margin_rows),
                ledger_window=ledger_for_episode(episode, ledger_rows),
            )
        )
    return output_rows


def find_attack_margin(
    episode: dict[str, str],
    margin_rows: list[dict[str, str]],
) -> dict[str, str]:
    attack_time = as_float(episode.get("attack_time_sec"))
    attack_agent = episode.get("attack_agent", "")
    attack_type = episode.get("attack_type", "")
    experiment = episode.get("experiment", "")
    candidates = [
        row
        for row in margin_rows
        if row.get("experiment") == experiment
        and agents_match(row.get("agent", ""), attack_agent)
        and row.get("selected_type") == "attack_event"
        and row.get("selected_actions") == attack_type
        and abs(as_float(row.get("time_sec")) - attack_time) <= 1e-6
    ]
    return candidates[0] if candidates else {}


def agents_match(margin_agent: str, episode_agent: str) -> bool:
    if margin_agent == episode_agent:
        return True
    if margin_agent.startswith("AURA") and episode_agent.startswith("AURA"):
        return True
    return False


def ledger_for_episode(
    episode: dict[str, str],
    ledger_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    experiment = episode.get("experiment", "")
    start_time = as_float(episode.get("attack_time_sec"))
    window = 40.0
    try:
        window = max(window, as_float(episode.get("first_required_response_latency_sec")) + 1.0)
    except (TypeError, ValueError):
        pass
    end_time = start_time + window
    return [
        row
        for row in ledger_rows
        if row.get("experiment") == experiment
        and start_time <= as_float(row.get("time_sec")) <= end_time
    ]


def build_scorecard_row(
    *,
    episode: dict[str, str],
    margin: dict[str, str],
    ledger_window: list[dict[str, str]],
) -> dict[str, str]:
    effect_counts = count_by(ledger_window, "observed_effect")
    actions = sorted({row.get("action", "") for row in ledger_window if row.get("action")})
    margin_present = bool(margin)
    response_complete = episode.get("response_status") == "complete"
    outcome = episode.get("outcome", "")
    uncontained = "uncontained" in outcome.lower() or "missing" in episode.get("response_status", "")
    has_metric_result = bool(episode.get("impact_reduction_from_peak"))
    status = "pass" if margin_present and response_complete and has_metric_result and not uncontained else "review"
    notes = []
    if not margin_present:
        notes.append("missing attack decision margin row")
    if not response_complete:
        notes.append(f"response_status={episode.get('response_status')}")
    if not has_metric_result:
        notes.append("missing impact reduction metric")
    if uncontained:
        notes.append(f"outcome={outcome}")
    if not notes:
        notes.append("attack choice, defense response, and metric movement are linked")

    return {
        "experiment": episode.get("experiment", ""),
        "episode_id": episode.get("episode_id", ""),
        "attack_event_id": episode.get("attack_event_id", ""),
        "attack_time_sec": episode.get("attack_time_sec", ""),
        "attack_agent": episode.get("attack_agent", ""),
        "attack_type": episode.get("attack_type", ""),
        "target_link": episode.get("target_link", ""),
        "attack_decision_basis": margin.get("decision_basis", ""),
        "attack_selection_margin": margin.get("selection_margin", ""),
        "attack_threshold_margin": margin.get("threshold_margin", ""),
        "response_status": episode.get("response_status", ""),
        "first_required_response_latency_sec": episode.get("first_required_response_latency_sec", ""),
        "covered_required_defenses": episode.get("covered_required_defenses", ""),
        "defense_event_count_in_window": str(len(ledger_window)),
        "improved_defense_events": str(effect_counts.get("improved", 0)),
        "held_defense_events": str(effect_counts.get("held", 0)),
        "degraded_or_delayed_defense_events": str(effect_counts.get("degraded_or_delayed", 0)),
        "defense_actions_in_window": ", ".join(actions) if actions else "none",
        "start_mission_impact": episode.get("start_mission_impact", ""),
        "peak_mission_impact": episode.get("peak_mission_impact", ""),
        "end_mission_impact": episode.get("end_mission_impact", ""),
        "impact_reduction_from_peak": episode.get("impact_reduction_from_peak", ""),
        "outcome": outcome,
        "scorecard_status": status,
        "scorecard_notes": " || ".join(notes),
        "safety_boundary": SAFETY_BOUNDARY,
    }


def count_by(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(field, "")
        counts[value] = counts.get(value, 0) + 1
    return counts


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Engagement Scorecard",
        "",
        "This scorecard links each AURA attack decision margin to the TSRA-R response chain and mission-impact movement.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Scorecard rows: {len(rows)}",
        f"- Status counts: {format_counts(count_by(rows, 'scorecard_status'))}",
        f"- Experiments: {', '.join(sorted({row['experiment'] for row in rows}))}",
        "",
        "## Engagement Rows",
        "",
    ]
    visible_fields = [
        "experiment",
        "attack_event_id",
        "attack_type",
        "attack_selection_margin",
        "attack_threshold_margin",
        "response_status",
        "defense_event_count_in_window",
        "impact_reduction_from_peak",
        "scorecard_status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    lines.extend(["", "## Notes", ""])
    for row in rows:
        lines.append(
            "- "
            f"{row['experiment']} {row['attack_event_id']}: "
            f"{row['scorecard_notes']}; actions={row['defense_actions_in_window']}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def markdown_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value) for value in values) + " |"


def markdown_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an attack-to-defense engagement scorecard.")
    parser.add_argument("--episodes", type=Path, default=DEFAULT_EPISODES)
    parser.add_argument("--margin-audit", type=Path, default=DEFAULT_MARGIN_AUDIT)
    parser.add_argument("--defense-ledger", type=Path, default=DEFAULT_DEFENSE_LEDGER)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.episodes, args.margin_audit, args.defense_ledger)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} scorecard rows)")
    print(f"Wrote {args.output_md} ({len(rows)} scorecard rows)")


if __name__ == "__main__":
    main()
