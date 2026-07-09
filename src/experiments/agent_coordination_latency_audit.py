from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_RESPONSE_AUDIT = Path("outputs/report_tables/attack_defense_response_audit.csv")
DEFAULT_EPISODE_REPLAY = Path("outputs/report_tables/closed_loop_episode_replay.csv")
DEFAULT_ALERTS = Path("outputs/report_tables/operator_alerts.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_coordination_latency_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_coordination_latency_audit.md")

RESPONSE_WINDOW_SEC = 40.0
SAFETY_BOUNDARY = (
    "closed simulation coordination-latency audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "episode_id",
    "attack_event_id",
    "attack_time_sec",
    "attack_type",
    "attack_agent",
    "required_response_latency_sec",
    "first_defense_latency_sec",
    "first_operator_alert_latency_sec",
    "metric_peak_latency_sec",
    "impact_reduction_from_peak",
    "response_status",
    "coordination_class",
    "coordination_status",
    "coordination_signal",
    "safety_boundary",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


def fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def collect_rows(
    *,
    experiment_root: Path = DEFAULT_EXPERIMENT_ROOT,
    response_audit_path: Path = DEFAULT_RESPONSE_AUDIT,
    episode_replay_path: Path = DEFAULT_EPISODE_REPLAY,
    alerts_path: Path = DEFAULT_ALERTS,
    response_window_sec: float = RESPONSE_WINDOW_SEC,
) -> list[dict[str, str]]:
    response_by_attack = {
        (row.get("experiment", ""), row.get("attack_event_id", "")): row
        for row in read_csv(response_audit_path)
    }
    alerts = read_csv(alerts_path)
    rows = []
    for episode in read_csv(episode_replay_path):
        experiment = episode.get("experiment", "")
        attack_id = episode.get("attack_event_id", "")
        response = response_by_attack.get((experiment, attack_id), {})
        attack_time = as_float(episode.get("attack_time_sec"))
        metrics = read_jsonl(experiment_root / experiment / "metric_snapshots.jsonl")
        metric_peak_time = peak_metric_time(metrics, attack_time, attack_time + response_window_sec)
        metric_peak_latency = metric_peak_time - attack_time if metric_peak_time is not None else None
        alert_latency = first_alert_latency(alerts, experiment, attack_time, response_window_sec)
        first_defense_latency = first_defense_latency_from_response(response, attack_time)
        required_latency = episode.get("first_required_response_latency_sec", "")
        reduction = as_float(episode.get("impact_reduction_from_peak"))
        status, issues = coordination_status(
            response_status=episode.get("response_status", ""),
            required_latency=required_latency,
            first_defense_latency=first_defense_latency,
            alert_latency=alert_latency,
            reduction=reduction,
            response_window_sec=response_window_sec,
        )
        rows.append(
            {
                "experiment": experiment,
                "episode_id": episode.get("episode_id", ""),
                "attack_event_id": attack_id,
                "attack_time_sec": episode.get("attack_time_sec", ""),
                "attack_type": episode.get("attack_type", ""),
                "attack_agent": episode.get("attack_agent", ""),
                "required_response_latency_sec": required_latency,
                "first_defense_latency_sec": fmt(first_defense_latency),
                "first_operator_alert_latency_sec": fmt(alert_latency),
                "metric_peak_latency_sec": fmt(metric_peak_latency),
                "impact_reduction_from_peak": episode.get("impact_reduction_from_peak", ""),
                "response_status": episode.get("response_status", ""),
                "coordination_class": classify_coordination(
                    required_latency=required_latency,
                    first_defense_latency=first_defense_latency,
                    alert_latency=alert_latency,
                    episode=episode,
                    response=response,
                ),
                "coordination_status": status,
                "coordination_signal": render_signal(
                    required_latency=required_latency,
                    first_defense_latency=first_defense_latency,
                    alert_latency=alert_latency,
                    metric_peak_latency=metric_peak_latency,
                    reduction=reduction,
                    issues=issues,
                ),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def first_defense_latency_from_response(response: dict[str, str], attack_time: float) -> float | None:
    if not response:
        return None
    if response.get("active_defenses_at_attack", "none") != "none":
        return 0.0
    times = event_times(response.get("response_defenses_after_attack", ""))
    future = [time for time in times if time >= attack_time]
    if not future:
        return None
    return min(future) - attack_time


def first_alert_latency(
    alerts: list[dict[str, str]],
    experiment: str,
    attack_time: float,
    response_window_sec: float,
) -> float | None:
    end_time = attack_time + response_window_sec
    times = [
        as_float(row.get("time_sec"))
        for row in alerts
        if row.get("experiment") == experiment
        and attack_time <= as_float(row.get("time_sec")) <= end_time
    ]
    if not times:
        return None
    return min(times) - attack_time


def peak_metric_time(
    metrics: list[dict[str, Any]],
    start_time: float,
    end_time: float,
) -> float | None:
    window = [
        row
        for row in metrics
        if start_time <= as_float(row.get("time_sec")) <= end_time
    ]
    if not window:
        return None
    peak = max(window, key=lambda row: as_float(row.get("mission_impact")))
    return as_float(peak.get("time_sec"))


def event_times(value: str) -> list[float]:
    if not value or value == "none":
        return []
    return [float(match) for match in re.findall(r"@([0-9]+(?:\.[0-9]+)?)(?:-until|;|$)", value)]


def coordination_status(
    *,
    response_status: str,
    required_latency: str,
    first_defense_latency: float | None,
    alert_latency: float | None,
    reduction: float,
    response_window_sec: float,
) -> tuple[str, list[str]]:
    issues = []
    required = as_float(required_latency, default=response_window_sec + 1)
    if response_status != "complete":
        issues.append(f"response_status={response_status}")
    if required > response_window_sec:
        issues.append(f"required_response_latency>{fmt(response_window_sec)}")
    if first_defense_latency is None or first_defense_latency > response_window_sec:
        issues.append("first_defense_missing_or_late")
    if alert_latency is None or alert_latency > response_window_sec:
        issues.append("operator_alert_missing_or_late")
    if reduction <= 0.0:
        issues.append("no_positive_reduction_from_peak")
    return ("pass" if not issues else "fail", issues)


def classify_coordination(
    *,
    required_latency: str,
    first_defense_latency: float | None,
    alert_latency: float | None,
    episode: dict[str, str],
    response: dict[str, str],
) -> str:
    required = as_float(required_latency)
    response_chain = response.get("response_defenses_after_attack", "")
    if (
        "ml_attack_alert" in response_chain
        or episode.get("attack_event_id", "").startswith("ml-atk")
    ) and required > 0.0:
        return "ml_reactive_window"
    if required == 0.0 and first_defense_latency == 0.0:
        return "prepositioned_defense"
    if alert_latency is not None and alert_latency <= 10.0:
        return "rapid_operator_handoff"
    return "bounded_response"


def render_signal(
    *,
    required_latency: str,
    first_defense_latency: float | None,
    alert_latency: float | None,
    metric_peak_latency: float | None,
    reduction: float,
    issues: list[str],
) -> str:
    return (
        f"required_response_latency={required_latency}; "
        f"first_defense_latency={fmt(first_defense_latency)}; "
        f"first_operator_alert_latency={fmt(alert_latency)}; "
        f"metric_peak_latency={fmt(metric_peak_latency)}; "
        f"impact_reduction_from_peak={fmt(reduction)}; "
        f"issues={', '.join(issues) if issues else 'none'}"
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
        "# Agent Coordination Latency Audit",
        "",
        "This audit checks whether attack, defense, operator alert, and metric feedback are time-linked inside the defended E5/E7 closed-loop episodes.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'coordination_status'))}",
        f"- Classes: {format_counts(count_values(rows, 'coordination_class'))}",
        "",
        "## Audit Table",
        "",
    ]
    visible_fields = [
        "experiment",
        "attack_event_id",
        "attack_type",
        "required_response_latency_sec",
        "first_operator_alert_latency_sec",
        "impact_reduction_from_peak",
        "coordination_class",
        "coordination_status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['experiment']} {row['episode_id']} {row['attack_event_id']}",
                "",
                f"- Attack: {row['attack_agent']} {row['attack_type']} at t={row['attack_time_sec']}",
                f"- Response latency: required={row['required_response_latency_sec']}, first_defense={row['first_defense_latency_sec']}",
                f"- Operator alert latency: {row['first_operator_alert_latency_sec']}",
                f"- Metric peak latency: {row['metric_peak_latency_sec']}",
                f"- Impact reduction from peak: {row['impact_reduction_from_peak']}",
                f"- Coordination class: {row['coordination_class']}",
                f"- Status: {row['coordination_status']}",
                f"- Signal: {row['coordination_signal']}",
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
    parser = argparse.ArgumentParser(description="Audit AURA/TSRA-R coordination latencies.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--response-audit", type=Path, default=DEFAULT_RESPONSE_AUDIT)
    parser.add_argument("--episode-replay", type=Path, default=DEFAULT_EPISODE_REPLAY)
    parser.add_argument("--alerts", type=Path, default=DEFAULT_ALERTS)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--response-window-sec", type=float, default=RESPONSE_WINDOW_SEC)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any coordination row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(
        experiment_root=args.experiment_root,
        response_audit_path=args.response_audit,
        episode_replay_path=args.episode_replay,
        alerts_path=args.alerts,
        response_window_sec=args.response_window_sec,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["coordination_status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} rows)")
    print(f"Wrote {args.output_md} ({len(rows)} rows)")
    if failed:
        print(f"Failed coordination rows: {', '.join(row['attack_event_id'] for row in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
