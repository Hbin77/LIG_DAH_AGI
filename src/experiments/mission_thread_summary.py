from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


DEFAULT_EPISODES = Path("outputs/report_tables/closed_loop_episode_replay.csv")
DEFAULT_SCORECARD = Path("outputs/report_tables/agent_engagement_scorecard.csv")
DEFAULT_ATTRIBUTION = Path("outputs/report_tables/defense_action_attribution_audit.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/mission_thread_summary.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/mission_thread_summary.md")

SAFETY_BOUNDARY = (
    "closed simulation mission-thread summary only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "thread_id",
    "experiment",
    "attack_event_id",
    "attack_time_sec",
    "attack_type",
    "target_link",
    "attack_decision_signal",
    "response_signal",
    "attribution_signal",
    "metric_signal",
    "operator_signal_count",
    "residual_risk",
    "thread_status",
    "interpretation",
    "safety_boundary",
]


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
        return ""


def split_actions(value: str) -> list[str]:
    actions = []
    for item in value.split(","):
        action = item.strip()
        if action and action not in actions:
            actions.append(action)
    return actions


def count_alerts(chain: str) -> int:
    if not chain or chain == "none":
        return 0
    return len([part for part in chain.split("||") if part.strip()])


def build_rows(
    *,
    episodes_path: Path = DEFAULT_EPISODES,
    scorecard_path: Path = DEFAULT_SCORECARD,
    attribution_path: Path = DEFAULT_ATTRIBUTION,
) -> list[dict[str, str]]:
    episodes = read_csv(episodes_path)
    scorecard_by_episode = {
        row.get("episode_id", ""): row
        for row in read_csv(scorecard_path)
        if row.get("episode_id")
    }
    attribution_by_action = {
        row.get("action", ""): row
        for row in read_csv(attribution_path)
        if row.get("action")
    }
    rows = []
    for index, episode in enumerate(episodes, start=1):
        scorecard = scorecard_by_episode.get(episode.get("episode_id", ""), {})
        defense_actions = split_actions(scorecard.get("defense_actions_in_window", ""))
        attribution_signal = render_attribution(defense_actions, attribution_by_action)
        attribution_ok = all(
            attribution_by_action.get(action, {}).get("attribution_status") == "pass"
            for action in defense_actions
        )
        response_ok = episode.get("response_status") == "complete"
        scorecard_ok = scorecard.get("scorecard_status") == "pass"
        operator_count = count_alerts(episode.get("operator_alert_chain", ""))
        impact_reduction = as_float(episode.get("impact_reduction_from_peak"))
        status = "pass" if response_ok and scorecard_ok and attribution_ok else "fail"
        rows.append(
            {
                "thread_id": f"thread-{index:02d}",
                "experiment": episode.get("experiment", ""),
                "attack_event_id": episode.get("attack_event_id", ""),
                "attack_time_sec": episode.get("attack_time_sec", ""),
                "attack_type": episode.get("attack_type", ""),
                "target_link": episode.get("target_link", ""),
                "attack_decision_signal": (
                    f"agent={episode.get('attack_agent', '')}; "
                    f"score={episode.get('attack_score', '')}; "
                    f"expected_impact={episode.get('expected_mission_impact', '')}; "
                    f"selection_margin={scorecard.get('attack_selection_margin', '')}; "
                    f"threshold_margin={scorecard.get('attack_threshold_margin', '')}"
                ),
                "response_signal": (
                    f"status={episode.get('response_status', '')}; "
                    f"first_required_latency_sec={episode.get('first_required_response_latency_sec', '')}; "
                    f"covered_required={episode.get('covered_required_defenses', '')}; "
                    f"defense_event_count={scorecard.get('defense_event_count_in_window', '')}; "
                    f"actions={', '.join(defense_actions)}"
                ),
                "attribution_signal": attribution_signal,
                "metric_signal": (
                    f"start={episode.get('start_mission_impact', '')}; "
                    f"peak={episode.get('peak_mission_impact', '')}; "
                    f"end={episode.get('end_mission_impact', '')}; "
                    f"reduction_from_peak={episode.get('impact_reduction_from_peak', '')}; "
                    f"outcome={episode.get('outcome', '')}"
                ),
                "operator_signal_count": str(operator_count),
                "residual_risk": episode.get("residual_risk", ""),
                "thread_status": status,
                "interpretation": interpret_thread(
                    episode=episode,
                    scorecard=scorecard,
                    attribution_ok=attribution_ok,
                    operator_count=operator_count,
                    impact_reduction=impact_reduction,
                ),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def render_attribution(
    defense_actions: list[str],
    attribution_by_action: dict[str, dict[str, str]],
) -> str:
    if not defense_actions:
        return "none"
    parts = []
    for action in defense_actions:
        attribution = attribution_by_action.get(action, {})
        parts.append(
            f"{action}:class={attribution.get('attribution_class', 'missing')},"
            f"status={attribution.get('attribution_status', 'missing')},"
            f"primary={attribution.get('primary_metric', '')},"
            f"delta={attribution.get('primary_metric_delta_mean', '')}"
        )
    return " || ".join(parts)


def interpret_thread(
    *,
    episode: dict[str, str],
    scorecard: dict[str, str],
    attribution_ok: bool,
    operator_count: int,
    impact_reduction: float,
) -> str:
    response = episode.get("response_status", "")
    outcome = episode.get("outcome", "")
    defense_count = scorecard.get("defense_event_count_in_window", "")
    if response == "complete" and attribution_ok and impact_reduction > 0:
        return (
            f"Attack, defense response, operator alerts, action attribution, and metric movement "
            f"form one complete mission thread; defense_events={defense_count}, "
            f"operator_alerts={operator_count}, outcome={outcome}."
        )
    if response == "complete" and attribution_ok:
        return (
            f"Response and attribution are complete, but scalar mission-impact reduction is limited; "
            f"read residual risk and local action metrics with outcome={outcome}."
        )
    return "Mission thread is incomplete or missing attribution evidence."


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Mission Thread Summary",
        "",
        "This summary joins each attack episode to decision evidence, response coverage, defense-action attribution, operator alerts, metric movement, and residual risk.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Mission threads: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'thread_status'))}",
        f"- Experiments: {', '.join(sorted({row['experiment'] for row in rows}))}",
        "",
        "## Thread Table",
        "",
    ]
    visible_fields = [
        "thread_id",
        "experiment",
        "attack_event_id",
        "attack_type",
        "response_signal",
        "metric_signal",
        "thread_status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['thread_id']} {row['experiment']} {row['attack_event_id']}",
                "",
                f"- Attack: {row['attack_type']} target={row['target_link']} at t={row['attack_time_sec']}",
                f"- Attack decision: {row['attack_decision_signal']}",
                f"- Response: {row['response_signal']}",
                f"- Attribution: {row['attribution_signal']}",
                f"- Metrics: {row['metric_signal']}",
                f"- Operator alert count: {row['operator_signal_count']}",
                f"- Residual risk: {row['residual_risk']}",
                f"- Status: {row['thread_status']}",
                f"- Interpretation: {row['interpretation']}",
                "",
            ]
        )
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
    parser = argparse.ArgumentParser(description="Build a mission-thread summary table.")
    parser.add_argument("--episodes", type=Path, default=DEFAULT_EPISODES)
    parser.add_argument("--scorecard", type=Path, default=DEFAULT_SCORECARD)
    parser.add_argument("--attribution", type=Path, default=DEFAULT_ATTRIBUTION)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any mission thread fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(
        episodes_path=args.episodes,
        scorecard_path=args.scorecard,
        attribution_path=args.attribution,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["thread_status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} mission threads)")
    print(f"Wrote {args.output_md} ({len(rows)} mission threads)")
    if failed:
        print(f"Failed mission threads: {', '.join(row['thread_id'] for row in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
