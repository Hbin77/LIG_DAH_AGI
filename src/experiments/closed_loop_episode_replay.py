from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENTS = [
    "E5_rule_aura_tsra_r",
    "E7_ml_aura_ml_tsra_r",
]
DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_RESPONSE_AUDIT = Path("outputs/report_tables/attack_defense_response_audit.csv")
DEFAULT_ALERTS = Path("outputs/report_tables/operator_alerts.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/closed_loop_episode_replay.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/closed_loop_episode_replay.md")

RESPONSE_WINDOW_SEC = 40.0
SAFETY_BOUNDARY = (
    "closed simulation closed-loop replay only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "episode_id",
    "attack_event_id",
    "attack_time_sec",
    "attack_agent",
    "attack_type",
    "target_link",
    "attack_reason",
    "expected_mission_impact",
    "attack_score",
    "response_status",
    "required_defenses",
    "covered_required_defenses",
    "first_required_response_latency_sec",
    "defense_chain",
    "operator_alert_chain",
    "start_mission_impact",
    "peak_mission_impact",
    "end_mission_impact",
    "peak_p95_critical_latency_sec",
    "peak_trusted_stale_exposure",
    "peak_priority_inversion_rate",
    "mission_impact_delta_start_to_end",
    "impact_reduction_from_peak",
    "outcome",
    "residual_risk",
    "safety_boundary",
]


def read_csv(path: Path) -> list[dict[str, str]]:
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
        return float(value)
    except (TypeError, ValueError):
        return default


def format_float(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def collect_rows(
    experiment_root: Path = DEFAULT_EXPERIMENT_ROOT,
    response_audit_path: Path = DEFAULT_RESPONSE_AUDIT,
    alerts_path: Path = DEFAULT_ALERTS,
    experiments: list[str] | None = None,
    response_window_sec: float = RESPONSE_WINDOW_SEC,
) -> list[dict[str, str]]:
    selected_experiments = experiments or DEFAULT_EXPERIMENTS
    response_rows = [
        row
        for row in read_csv(response_audit_path)
        if row["experiment"] in selected_experiments
    ]
    alert_rows = read_csv(alerts_path)
    output_rows: list[dict[str, str]] = []

    for experiment in selected_experiments:
        exp_dir = experiment_root / experiment
        attacks = {
            row["event_id"]: row for row in read_jsonl(exp_dir / "attack_events.jsonl")
        }
        metrics = read_jsonl(exp_dir / "metric_snapshots.jsonl")
        experiment_responses = [
            row for row in response_rows if row["experiment"] == experiment
        ]
        for episode_index, response in enumerate(experiment_responses, start=1):
            attack_id = response["attack_event_id"]
            attack = attacks.get(attack_id, {})
            attack_time = as_float(response["attack_time_sec"])
            end_time = attack_time + response_window_sec
            metric_window = metrics_between(metrics, attack_time, end_time)
            start_metric = nearest_metric(metrics, attack_time)
            end_metric = nearest_metric(metrics, end_time)
            peak_metric = peak_metric_row(metric_window)
            alerts = alerts_between(alert_rows, experiment, attack_time, end_time)
            output_rows.append(
                build_episode_row(
                    experiment=experiment,
                    episode_index=episode_index,
                    response=response,
                    attack=attack,
                    attack_time=attack_time,
                    start_metric=start_metric,
                    peak_metric=peak_metric,
                    end_metric=end_metric,
                    metric_window=metric_window,
                    alerts=alerts,
                )
            )
    return output_rows


def metrics_between(
    metrics: list[dict[str, Any]],
    start_time: float,
    end_time: float,
) -> list[dict[str, Any]]:
    return [
        row
        for row in metrics
        if start_time <= as_float(row.get("time_sec")) <= end_time
    ]


def nearest_metric(metrics: list[dict[str, Any]], time_sec: float) -> dict[str, Any]:
    if not metrics:
        return {}
    prior = [row for row in metrics if as_float(row.get("time_sec")) <= time_sec]
    if prior:
        return max(prior, key=lambda row: as_float(row.get("time_sec")))
    return min(metrics, key=lambda row: abs(as_float(row.get("time_sec")) - time_sec))


def peak_metric_row(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    if not metrics:
        return {}
    return max(metrics, key=lambda row: as_float(row.get("mission_impact")))


def alerts_between(
    alerts: list[dict[str, str]],
    experiment: str,
    start_time: float,
    end_time: float,
) -> list[dict[str, str]]:
    return [
        row
        for row in alerts
        if row["experiment"] == experiment
        and start_time <= as_float(row["time_sec"]) <= end_time
    ]


def build_episode_row(
    experiment: str,
    episode_index: int,
    response: dict[str, str],
    attack: dict[str, Any],
    attack_time: float,
    start_metric: dict[str, Any],
    peak_metric: dict[str, Any],
    end_metric: dict[str, Any],
    metric_window: list[dict[str, Any]],
    alerts: list[dict[str, str]],
) -> dict[str, str]:
    candidate = attack.get("candidate") or {}
    expected = attack.get("expected_impact") or {}
    start_impact = as_float(start_metric.get("mission_impact"))
    peak_impact = as_float(peak_metric.get("mission_impact"))
    end_impact = as_float(end_metric.get("mission_impact"))
    impact_delta = end_impact - start_impact
    reduction_from_peak = peak_impact - end_impact
    return {
        "experiment": experiment,
        "episode_id": f"{experiment}-episode-{episode_index:02d}",
        "attack_event_id": response["attack_event_id"],
        "attack_time_sec": format_float(attack_time),
        "attack_agent": str(attack.get("agent") or response.get("attack_agent") or ""),
        "attack_type": str(candidate.get("attack_type") or response.get("attack_capability") or ""),
        "target_link": str(candidate.get("target_link") or response.get("target_link") or ""),
        "attack_reason": str(attack.get("reason") or candidate.get("reason") or ""),
        "expected_mission_impact": format_float(expected.get("mission_impact")),
        "attack_score": format_float(attack.get("score")),
        "response_status": response["response_status"],
        "required_defenses": response["required_runtime_defenses"],
        "covered_required_defenses": response["covered_required_defenses"],
        "first_required_response_latency_sec": response[
            "first_required_response_latency_sec"
        ],
        "defense_chain": summarize_defense_chain(response),
        "operator_alert_chain": summarize_alerts(alerts),
        "start_mission_impact": format_float(start_impact),
        "peak_mission_impact": format_float(peak_impact),
        "end_mission_impact": format_float(end_impact),
        "peak_p95_critical_latency_sec": format_float(
            peak_value(metric_window, "p95_critical_latency_sec")
        ),
        "peak_trusted_stale_exposure": format_float(
            peak_value(metric_window, "trusted_stale_exposure")
        ),
        "peak_priority_inversion_rate": format_float(
            peak_value(metric_window, "priority_inversion_rate")
        ),
        "mission_impact_delta_start_to_end": format_float(impact_delta),
        "impact_reduction_from_peak": format_float(reduction_from_peak),
        "outcome": outcome_label(response["response_status"], start_impact, peak_impact, end_impact),
        "residual_risk": response["residual_risk"],
        "safety_boundary": SAFETY_BOUNDARY,
    }


def summarize_defense_chain(response: dict[str, str]) -> str:
    parts = []
    if response["active_defenses_at_attack"] != "none":
        parts.append(f"active={response['active_defenses_at_attack']}")
    if response["response_defenses_after_attack"] != "none":
        parts.append(f"response={response['response_defenses_after_attack']}")
    return " | ".join(parts) if parts else "none"


def summarize_alerts(alerts: list[dict[str, str]]) -> str:
    if not alerts:
        return "none"
    parts = []
    for alert in alerts:
        parts.append(
            compact(
                [
                    f"t={alert['time_sec']}",
                    alert["event_id"],
                    alert["action"],
                    f"severity={alert['severity']}",
                    alert["operator_alert"],
                ]
            )
        )
    return " || ".join(parts)


def compact(parts: list[str]) -> str:
    return "; ".join(part for part in parts if part)


def peak_value(metrics: list[dict[str, Any]], key: str) -> float:
    return max([as_float(metric.get(key)) for metric in metrics] or [0.0])


def outcome_label(
    response_status: str,
    start_impact: float,
    peak_impact: float,
    end_impact: float,
) -> str:
    if response_status != "complete":
        return "incomplete response coverage"
    if peak_impact - end_impact >= 0.05:
        return "contained after peak degradation"
    if end_impact <= start_impact + 0.03:
        return "held near attack-time impact"
    return "covered with residual mission impact"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Closed-Loop Episode Replay",
        "",
        "This table connects each defended AURA attack event to TSRA-R responses, operator alerts, and mission metric movement.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
    ]
    for experiment in ordered_values(rows, "experiment"):
        subset = [row for row in rows if row["experiment"] == experiment]
        outcomes = count_values(subset, "outcome")
        lines.extend(
            [
                f"### {experiment}",
                "",
                f"- Episodes: {len(subset)}",
                f"- Outcomes: {format_counts(outcomes)}",
                "",
            ]
        )

    visible_fields = [
        "experiment",
        "episode_id",
        "attack_event_id",
        "attack_type",
        "target_link",
        "response_status",
        "first_required_response_latency_sec",
        "peak_mission_impact",
        "end_mission_impact",
        "outcome",
    ]
    lines.extend(
        [
            "## Episode Table",
            "",
            markdown_row(visible_fields),
            markdown_row(["---"] * len(visible_fields)),
        ]
    )
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))

    lines.extend(["", "## Episode Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['episode_id']}",
                "",
                f"- Attack: {row['attack_event_id']} {row['attack_type']} target={row['target_link']}",
                f"- Attack reason: {row['attack_reason']}",
                f"- Expected mission impact: {row['expected_mission_impact']}",
                f"- Response status: {row['response_status']}",
                f"- Required defenses: {row['required_defenses']}",
                f"- Covered required defenses: {row['covered_required_defenses']}",
                f"- First required response latency: {row['first_required_response_latency_sec']}",
                f"- Defense chain: {row['defense_chain']}",
                f"- Operator alerts: {row['operator_alert_chain']}",
                f"- Mission impact: start={row['start_mission_impact']}, peak={row['peak_mission_impact']}, end={row['end_mission_impact']}",
                f"- Peak latency/stale/inversion: {row['peak_p95_critical_latency_sec']} / {row['peak_trusted_stale_exposure']} / {row['peak_priority_inversion_rate']}",
                f"- Outcome: {row['outcome']}",
                f"- Residual risk: {row['residual_risk']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def ordered_values(rows: list[dict[str, str]], field: str) -> list[str]:
    values = []
    for row in rows:
        value = row[field]
        if value not in values:
            values.append(value)
    return values


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row[field]] = counts.get(row[field], 0) + 1
    return counts


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def markdown_row(values: list[str]) -> str:
    return "| " + " | ".join(values) + " |"


def markdown_cell(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate closed-loop attack/defense episode replay.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--response-audit", type=Path, default=DEFAULT_RESPONSE_AUDIT)
    parser.add_argument("--alerts", type=Path, default=DEFAULT_ALERTS)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--experiments", nargs="*", default=DEFAULT_EXPERIMENTS)
    parser.add_argument("--response-window-sec", type=float, default=RESPONSE_WINDOW_SEC)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(
        experiment_root=args.experiment_root,
        response_audit_path=args.response_audit,
        alerts_path=args.alerts,
        experiments=args.experiments,
        response_window_sec=args.response_window_sec,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} closed-loop episodes)")
    print(f"Wrote {args.output_md} ({len(rows)} closed-loop episodes)")


if __name__ == "__main__":
    main()
