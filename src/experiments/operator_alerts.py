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
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/operator_alerts.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/operator_alerts.md")

SAFETY_BOUNDARY = (
    "closed simulation operator alert only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "time_sec",
    "event_id",
    "agent",
    "action",
    "severity",
    "operator_alert",
    "mission_rationale",
    "expected_operator_response",
    "active_link",
    "mission_impact",
    "p95_critical_latency_sec",
    "trusted_stale_exposure",
    "priority_inversion_rate",
    "related_attack_context",
    "decision_trace_reason",
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
    experiments: list[str] | None = None,
) -> list[dict[str, str]]:
    selected_experiments = experiments or DEFAULT_EXPERIMENTS
    rows: list[dict[str, str]] = []
    for experiment in selected_experiments:
        exp_dir = experiment_root / experiment
        defenses = load_jsonl(exp_dir / "defense_events.jsonl")
        attacks = load_jsonl(exp_dir / "attack_events.jsonl")
        metrics = load_jsonl(exp_dir / "metric_snapshots.jsonl")
        traces = load_jsonl(exp_dir / "tsra_r_decision_traces.jsonl")

        for defense in defenses:
            time_sec = as_float(defense.get("time_sec"))
            metric = nearest_by_time(metrics, time_sec, "time_sec")
            trace = nearest_by_time(traces, time_sec, "time_sec")
            action = str(defense.get("action") or "")
            details = defense.get("details") or {}
            alert = alert_for_action(action, details, metric)
            rows.append(
                {
                    "experiment": experiment,
                    "time_sec": format_float(time_sec),
                    "event_id": str(defense.get("event_id") or ""),
                    "agent": str(defense.get("agent") or ""),
                    "action": action,
                    "severity": alert["severity"],
                    "operator_alert": alert["operator_alert"],
                    "mission_rationale": alert["mission_rationale"],
                    "expected_operator_response": alert["expected_operator_response"],
                    "active_link": trace_active_link(trace),
                    "mission_impact": format_float(metric.get("mission_impact")),
                    "p95_critical_latency_sec": format_float(
                        metric.get("p95_critical_latency_sec")
                    ),
                    "trusted_stale_exposure": format_float(
                        metric.get("trusted_stale_exposure")
                    ),
                    "priority_inversion_rate": format_float(
                        metric.get("priority_inversion_rate")
                    ),
                    "related_attack_context": summarize_related_attacks(
                        attacks, time_sec
                    ),
                    "decision_trace_reason": str(trace.get("reason") or ""),
                    "safety_boundary": SAFETY_BOUNDARY,
                }
            )
    return rows


def nearest_by_time(
    rows: list[dict[str, Any]],
    time_sec: float,
    time_field: str,
) -> dict[str, Any]:
    if not rows:
        return {}
    exact = [
        row
        for row in rows
        if abs(as_float(row.get(time_field)) - time_sec) < 1e-9
    ]
    if exact:
        return exact[0]
    prior = [
        row
        for row in rows
        if as_float(row.get(time_field), default=-1.0) <= time_sec
    ]
    if prior:
        return max(prior, key=lambda row: as_float(row.get(time_field)))
    return min(rows, key=lambda row: abs(as_float(row.get(time_field)) - time_sec))


def trace_active_link(trace: dict[str, Any]) -> str:
    observation = trace.get("observation") or {}
    return str(observation.get("active_link") or "")


def alert_for_action(
    action: str,
    details: dict[str, Any],
    metric: dict[str, Any],
) -> dict[str, str]:
    mission_impact = as_float(metric.get("mission_impact"))
    trusted_stale = as_float(metric.get("trusted_stale_exposure"))
    priority_inversion = as_float(metric.get("priority_inversion_rate"))
    severity = base_severity(action, details, mission_impact, trusted_stale, priority_inversion)

    if action == "ml_attack_alert":
        probability = format_float(details.get("probability"))
        threshold = format_float(details.get("threshold"))
        return {
            "severity": severity,
            "operator_alert": (
                f"ML detector flags attack-like degradation probability={probability} "
                f"above threshold={threshold}."
            ),
            "mission_rationale": (
                "Open the reactive defense window so TSRA-R can apply bounded routing, "
                "freshness, and PACE actions only when attack evidence is present."
            ),
            "expected_operator_response": (
                "Monitor the next defense window and confirm that alerts, commands, and "
                "coordinates remain prioritized."
            ),
        }
    if action == "priority_reroute":
        return {
            "severity": severity,
            "operator_alert": "Critical traffic is waiting behind lower-priority load.",
            "mission_rationale": (
                "Priority reroute protects air-defense alerts, commands, and coordinates "
                "from video or telemetry queue pressure."
            ),
            "expected_operator_response": (
                "Accept critical-traffic preemption and monitor P95 critical latency."
            ),
        }
    if action == "video_throttle":
        return {
            "severity": severity,
            "operator_alert": "Video traffic is being reduced to protect critical capacity.",
            "mission_rationale": (
                "Temporary video reduction preserves bandwidth for mission-critical "
                "messages during degraded SATCOM/PACE conditions."
            ),
            "expected_operator_response": (
                "Expect lower video fidelity while checking that alert and command "
                "delivery remains stable."
            ),
        }
    if action == "stale_badge":
        stale_ratio = format_float(details.get("stale_ratio"))
        return {
            "severity": severity,
            "operator_alert": f"COP stale confidence badge active; stale_ratio={stale_ratio}.",
            "mission_rationale": (
                "Stale badge reduces the risk that old COP objects are trusted as current "
                "battlefield state."
            ),
            "expected_operator_response": (
                "Treat stale objects as degraded confidence and avoid decisions that rely "
                "only on those objects."
            ),
        }
    if action == "pace_switch":
        target = str(details.get("target_link") or "fallback")
        reason = str(details.get("reason") or "link degraded")
        return {
            "severity": severity,
            "operator_alert": f"PACE switch selected target={target}; reason={reason}.",
            "mission_rationale": (
                "PACE switching moves critical traffic away from the degraded active link "
                "while preserving a bounded recovery path."
            ),
            "expected_operator_response": (
                "Track fallback stability and watch for recovery churn or follow-on "
                "failover chasing."
            ),
        }
    return {
        "severity": severity,
        "operator_alert": f"TSRA-R emitted defense action {action}.",
        "mission_rationale": "Defense event was selected by the TSRA-R closed-loop policy.",
        "expected_operator_response": "Review the linked trace reason and metric snapshot.",
    }


def base_severity(
    action: str,
    details: dict[str, Any],
    mission_impact: float,
    trusted_stale: float,
    priority_inversion: float,
) -> str:
    if action in {"pace_switch", "ml_attack_alert"}:
        return "high"
    if action == "priority_reroute" and (
        priority_inversion >= 0.05 or mission_impact >= 0.15
    ):
        return "high"
    if action == "stale_badge" and trusted_stale >= 0.15:
        return "high"
    if action == "video_throttle" and mission_impact >= 0.15:
        return "medium"
    if action == "stale_badge" and as_float(details.get("stale_ratio")) >= 0.4:
        return "medium"
    return "medium"


def summarize_related_attacks(attacks: list[dict[str, Any]], time_sec: float) -> str:
    related = []
    for attack in attacks:
        candidate = attack.get("candidate") or {}
        selected_at = as_float(attack.get("selected_at"))
        start_time = as_float(candidate.get("start_time"), selected_at)
        duration = as_float(candidate.get("duration_sec"))
        end_time = start_time + duration
        if start_time <= time_sec <= end_time:
            status = "active"
        elif 0 < time_sec - selected_at <= 40:
            status = "recent"
        elif 0 <= selected_at - time_sec <= 40:
            status = "near_future"
        else:
            continue
        related.append(
            compact(
                [
                    status,
                    str(attack.get("event_id") or ""),
                    str(candidate.get("attack_type") or ""),
                    f"target={candidate.get('target_link')}",
                ]
            )
        )
    return " || ".join(related) if related else "none"


def compact(parts: list[str]) -> str:
    return "; ".join(part for part in parts if part)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Operator Alerts",
        "",
        "This table translates TSRA-R defense events into closed-simulation operator alerts.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
    ]
    for experiment in ordered_values(rows, "experiment"):
        subset = [row for row in rows if row["experiment"] == experiment]
        severity_counts = count_values(subset, "severity")
        action_counts = count_values(subset, "action")
        lines.extend(
            [
                f"### {experiment}",
                "",
                f"- Alert count: {len(subset)}",
                f"- Severity: {format_counts(severity_counts)}",
                f"- Actions: {format_counts(action_counts)}",
                "",
            ]
        )

    visible_fields = [
        "experiment",
        "time_sec",
        "event_id",
        "action",
        "severity",
        "operator_alert",
        "mission_rationale",
        "related_attack_context",
    ]
    lines.extend(
        [
            "## Alert Table",
            "",
            markdown_row(visible_fields),
            markdown_row(["---"] * len(visible_fields)),
        ]
    )
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    parser = argparse.ArgumentParser(description="Generate TSRA-R operator alerts.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--experiments", nargs="*", default=DEFAULT_EXPERIMENTS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root, args.experiments)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} alerts)")
    print(f"Wrote {args.output_md} ({len(rows)} alerts)")


if __name__ == "__main__":
    main()
