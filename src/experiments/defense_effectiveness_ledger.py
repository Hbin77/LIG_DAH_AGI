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
DEFAULT_OPERATOR_ALERTS = Path("outputs/report_tables/operator_alerts.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/defense_effectiveness_ledger.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/defense_effectiveness_ledger.md")
DEFAULT_WINDOW_SEC = 30.0

SAFETY_BOUNDARY = (
    "closed simulation defense-effect ledger only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "time_sec",
    "event_id",
    "agent",
    "action",
    "severity",
    "effect_window_sec",
    "active_link",
    "operator_alert",
    "related_attack_context",
    "before_mission_impact",
    "after_mission_impact",
    "delta_mission_impact",
    "peak_mission_impact_in_window",
    "before_p95_critical_latency_sec",
    "after_p95_critical_latency_sec",
    "delta_p95_critical_latency_sec",
    "before_trusted_stale_exposure",
    "after_trusted_stale_exposure",
    "delta_trusted_stale_exposure",
    "before_priority_inversion_rate",
    "after_priority_inversion_rate",
    "delta_priority_inversion_rate",
    "observed_effect",
    "interpretation",
    "safety_boundary",
]


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
    experiment_root: Path = DEFAULT_EXPERIMENT_ROOT,
    operator_alert_path: Path = DEFAULT_OPERATOR_ALERTS,
    experiments: list[str] | None = None,
    window_sec: float = DEFAULT_WINDOW_SEC,
) -> list[dict[str, str]]:
    selected_experiments = experiments or DEFAULT_EXPERIMENTS
    alert_index = index_alerts(read_csv(operator_alert_path))
    rows: list[dict[str, str]] = []

    for experiment in selected_experiments:
        exp_dir = experiment_root / experiment
        defenses = load_jsonl(exp_dir / "defense_events.jsonl")
        metrics = load_jsonl(exp_dir / "metric_snapshots.jsonl")

        for defense in defenses:
            time_sec = as_float(defense.get("time_sec"))
            action = str(defense.get("action") or "")
            event_id = str(defense.get("event_id") or "")
            before = metric_at_or_before(metrics, time_sec)
            after_time = min(time_sec + window_sec, max_metric_time(metrics))
            after = metric_at_or_before(metrics, after_time)
            window_metrics = metrics_between(metrics, time_sec, after_time)
            alert = alert_index.get((experiment, event_id), {})

            delta_impact = delta(after, before, "mission_impact")
            delta_latency = delta(after, before, "p95_critical_latency_sec")
            delta_stale = delta(after, before, "trusted_stale_exposure")
            delta_priority = delta(after, before, "priority_inversion_rate")
            observed_effect = classify_effect(
                action,
                delta_impact,
                delta_latency,
                delta_stale,
                delta_priority,
            )

            rows.append(
                {
                    "experiment": experiment,
                    "time_sec": format_float(time_sec),
                    "event_id": event_id,
                    "agent": str(defense.get("agent") or ""),
                    "action": action,
                    "severity": alert.get("severity", ""),
                    "effect_window_sec": format_float(window_sec),
                    "active_link": alert.get("active_link", ""),
                    "operator_alert": alert.get("operator_alert", ""),
                    "related_attack_context": alert.get("related_attack_context", ""),
                    "before_mission_impact": format_metric(before, "mission_impact"),
                    "after_mission_impact": format_metric(after, "mission_impact"),
                    "delta_mission_impact": format_float(delta_impact),
                    "peak_mission_impact_in_window": format_float(
                        peak_metric(window_metrics, "mission_impact")
                    ),
                    "before_p95_critical_latency_sec": format_metric(
                        before, "p95_critical_latency_sec"
                    ),
                    "after_p95_critical_latency_sec": format_metric(
                        after, "p95_critical_latency_sec"
                    ),
                    "delta_p95_critical_latency_sec": format_float(delta_latency),
                    "before_trusted_stale_exposure": format_metric(
                        before, "trusted_stale_exposure"
                    ),
                    "after_trusted_stale_exposure": format_metric(
                        after, "trusted_stale_exposure"
                    ),
                    "delta_trusted_stale_exposure": format_float(delta_stale),
                    "before_priority_inversion_rate": format_metric(
                        before, "priority_inversion_rate"
                    ),
                    "after_priority_inversion_rate": format_metric(
                        after, "priority_inversion_rate"
                    ),
                    "delta_priority_inversion_rate": format_float(delta_priority),
                    "observed_effect": observed_effect,
                    "interpretation": interpret_action(
                        action,
                        observed_effect,
                        delta_impact,
                        delta_latency,
                        delta_stale,
                        delta_priority,
                    ),
                    "safety_boundary": SAFETY_BOUNDARY,
                }
            )
    return rows


def index_alerts(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row.get("experiment", ""), row.get("event_id", "")): row
        for row in rows
        if row.get("experiment") and row.get("event_id")
    }


def metric_at_or_before(metrics: list[dict[str, Any]], time_sec: float) -> dict[str, Any]:
    if not metrics:
        return {}
    prior = [
        metric
        for metric in metrics
        if as_float(metric.get("time_sec"), default=-1.0) <= time_sec
    ]
    if prior:
        return max(prior, key=lambda metric: as_float(metric.get("time_sec")))
    return min(metrics, key=lambda metric: abs(as_float(metric.get("time_sec")) - time_sec))


def metrics_between(
    metrics: list[dict[str, Any]],
    start_sec: float,
    end_sec: float,
) -> list[dict[str, Any]]:
    return [
        metric
        for metric in metrics
        if start_sec <= as_float(metric.get("time_sec")) <= end_sec
    ]


def max_metric_time(metrics: list[dict[str, Any]]) -> float:
    if not metrics:
        return 0.0
    return max(as_float(metric.get("time_sec")) for metric in metrics)


def delta(
    after: dict[str, Any],
    before: dict[str, Any],
    field: str,
) -> float:
    return as_float(after.get(field)) - as_float(before.get(field))


def format_metric(metric: dict[str, Any], field: str) -> str:
    if not metric:
        return ""
    return format_float(metric.get(field))


def peak_metric(metrics: list[dict[str, Any]], field: str) -> float:
    if not metrics:
        return 0.0
    return max(as_float(metric.get(field)) for metric in metrics)


def classify_effect(
    action: str,
    delta_impact: float,
    delta_latency: float,
    delta_stale: float,
    delta_priority: float,
) -> str:
    if action == "stale_badge" and delta_stale <= -0.03:
        return "improved"
    if action == "priority_reroute" and (delta_priority <= -0.03 or delta_latency <= -1.0):
        return "improved"
    if action == "video_throttle" and (delta_latency <= -1.0 or delta_priority <= -0.03):
        return "improved"
    if action == "pace_switch" and delta_impact <= -0.03:
        return "improved"
    if action == "ml_attack_alert" and delta_impact <= 0.03:
        return "held"
    if delta_impact <= -0.03:
        return "improved"
    if delta_impact >= 0.03:
        return "degraded_or_delayed"
    return "held"


def interpret_action(
    action: str,
    observed_effect: str,
    delta_impact: float,
    delta_latency: float,
    delta_stale: float,
    delta_priority: float,
) -> str:
    deltas = (
        f"impact_delta={delta_impact:.3f}, latency_delta={delta_latency:.3f}, "
        f"trusted_stale_delta={delta_stale:.3f}, priority_delta={delta_priority:.3f}"
    )
    if action == "ml_attack_alert":
        return (
            "ML detector opened or refreshed the reactive defense window; local metric "
            f"effect is indirect through following TSRA-R actions ({observed_effect}; {deltas})."
        )
    if action == "stale_badge":
        return (
            "Stale badge is credited when trusted stale exposure falls or stays bounded; "
            f"raw stale objects may remain in the simulation ({observed_effect}; {deltas})."
        )
    if action == "priority_reroute":
        return (
            "Priority reroute is credited through lower priority inversion or critical "
            f"latency pressure ({observed_effect}; {deltas})."
        )
    if action == "video_throttle":
        return (
            "Video throttle is credited when capacity pressure on critical traffic eases; "
            f"mission impact can lag by one window ({observed_effect}; {deltas})."
        )
    if action == "pace_switch":
        return (
            "PACE switch is credited when link recovery reduces mission impact while "
            f"accepting possible fallback churn ({observed_effect}; {deltas})."
        )
    return f"Defense action local effect over the configured window ({observed_effect}; {deltas})."


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Defense Effectiveness Ledger",
        "",
        "This ledger joins each TSRA-R DefenseEvent to local mission-metric movement before and after the response window.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
    ]
    for experiment in ordered_values(rows, "experiment"):
        subset = [row for row in rows if row["experiment"] == experiment]
        lines.extend(
            [
                f"### {experiment}",
                "",
                f"- Ledger rows: {len(subset)}",
                f"- Actions: {format_counts(count_values(subset, 'action'))}",
                f"- Observed effects: {format_counts(count_values(subset, 'observed_effect'))}",
                "",
            ]
        )

    visible_fields = [
        "experiment",
        "time_sec",
        "event_id",
        "action",
        "observed_effect",
        "delta_mission_impact",
        "delta_p95_critical_latency_sec",
        "delta_trusted_stale_exposure",
        "delta_priority_inversion_rate",
        "related_attack_context",
    ]
    lines.extend(
        [
            "## Ledger Table",
            "",
            markdown_row(visible_fields),
            markdown_row(["---"] * len(visible_fields)),
        ]
    )
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    lines.extend(
        [
            "",
            "## Interpretation Rule",
            "",
            "- Negative mission impact, critical latency, trusted stale exposure, or priority inversion deltas are local improvement signals.",
            "- `held` means TSRA-R kept the local window bounded rather than visibly reducing the scalar metric in that 30-second slice.",
            "- `degraded_or_delayed` means the response occurred while mission impact was still rising or the response effect lagged the window.",
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
    parser = argparse.ArgumentParser(description="Generate TSRA-R defense effectiveness ledger.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--operator-alerts", type=Path, default=DEFAULT_OPERATOR_ALERTS)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--experiments", nargs="*", default=DEFAULT_EXPERIMENTS)
    parser.add_argument("--window-sec", type=float, default=DEFAULT_WINDOW_SEC)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(
        args.experiment_root,
        args.operator_alerts,
        args.experiments,
        args.window_sec,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} ledger rows)")
    print(f"Wrote {args.output_md} ({len(rows)} ledger rows)")


if __name__ == "__main__":
    main()
