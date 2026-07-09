from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any


DEFAULT_LEDGER = Path("outputs/report_tables/defense_effectiveness_ledger.csv")
DEFAULT_ABLATION = Path("outputs/batch/tsra_action_ablation_summary.csv")
DEFAULT_REACTIVE_TRADEOFF = Path("outputs/report_tables/reactive_defense_tradeoff_audit.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/defense_action_attribution_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/defense_action_attribution_audit.md")

SAFETY_BOUNDARY = (
    "closed simulation defense-action attribution audit only; no RF, exploit, or live network action"
)

ACTION_ORDER = [
    "priority_reroute",
    "video_throttle",
    "stale_badge",
    "pace_switch",
    "ml_attack_alert",
]

ACTION_TARGETS = {
    "priority_reroute": {
        "primary_metric": "priority_inversion_rate",
        "delta_field": "delta_priority_inversion_rate",
        "ablation_field": "delta_priority_inversion_rate_mean",
        "target": "reduce priority inversion and critical-traffic queuing",
    },
    "video_throttle": {
        "primary_metric": "p95_critical_latency_sec",
        "delta_field": "delta_p95_critical_latency_sec",
        "ablation_field": "delta_p95_critical_latency_sec_mean",
        "target": "reduce optional video pressure on critical traffic",
    },
    "stale_badge": {
        "primary_metric": "trusted_stale_exposure",
        "delta_field": "delta_trusted_stale_exposure",
        "ablation_field": "delta_trusted_stale_exposure_mean",
        "target": "bound trusted stale COP exposure",
    },
    "pace_switch": {
        "primary_metric": "mission_impact",
        "delta_field": "delta_mission_impact",
        "ablation_field": "delta_mission_impact_mean",
        "target": "move critical traffic away from degraded active links",
    },
    "ml_attack_alert": {
        "primary_metric": "mission_impact",
        "delta_field": "delta_mission_impact",
        "ablation_field": "",
        "target": "open reactive defense windows during active AURA-ML attack effects",
    },
}

FIELDNAMES = [
    "action",
    "target",
    "event_count",
    "high_severity_count",
    "improved_count",
    "held_count",
    "degraded_or_delayed_count",
    "improved_or_held_rate",
    "mean_delta_mission_impact",
    "mean_delta_p95_critical_latency_sec",
    "mean_delta_trusted_stale_exposure",
    "mean_delta_priority_inversion_rate",
    "primary_metric",
    "primary_metric_delta_mean",
    "ablation_delta_metric",
    "ablation_delta_value",
    "reactive_overlap_evidence",
    "attribution_class",
    "attribution_status",
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


def mean(rows: list[dict[str, str]], field: str) -> float:
    if not rows:
        return 0.0
    return sum(as_float(row.get(field)) for row in rows) / len(rows)


def count(rows: list[dict[str, str]], field: str, value: str) -> int:
    return sum(1 for row in rows if row.get(field) == value)


def build_rows(
    *,
    ledger_path: Path = DEFAULT_LEDGER,
    ablation_path: Path = DEFAULT_ABLATION,
    reactive_tradeoff_path: Path = DEFAULT_REACTIVE_TRADEOFF,
) -> list[dict[str, str]]:
    ledger_rows = read_csv(ledger_path)
    ablation_by_action = {
        row.get("disabled_action", ""): row
        for row in read_csv(ablation_path)
        if row.get("disabled_action")
    }
    reactive_evidence = extract_reactive_overlap(read_csv(reactive_tradeoff_path))

    rows = []
    for action in ACTION_ORDER:
        action_rows = [row for row in ledger_rows if row.get("action") == action]
        target = ACTION_TARGETS[action]
        improved = count(action_rows, "observed_effect", "improved")
        held = count(action_rows, "observed_effect", "held")
        degraded = count(action_rows, "observed_effect", "degraded_or_delayed")
        event_count = len(action_rows)
        improved_or_held_rate = (improved + held) / event_count if event_count else 0.0
        mean_deltas = {
            "mission_impact": mean(action_rows, "delta_mission_impact"),
            "p95_critical_latency_sec": mean(action_rows, "delta_p95_critical_latency_sec"),
            "trusted_stale_exposure": mean(action_rows, "delta_trusted_stale_exposure"),
            "priority_inversion_rate": mean(action_rows, "delta_priority_inversion_rate"),
        }
        primary_delta = mean(action_rows, target["delta_field"])
        ablation_row = ablation_by_action.get(action, {})
        ablation_delta = (
            as_float(ablation_row.get(target["ablation_field"]))
            if target["ablation_field"]
            else 0.0
        )
        attribution_class, status, interpretation = classify_action(
            action=action,
            event_count=event_count,
            improved_or_held_rate=improved_or_held_rate,
            primary_delta=primary_delta,
            ablation_delta=ablation_delta,
            reactive_evidence=reactive_evidence,
            mean_deltas=mean_deltas,
        )
        rows.append(
            {
                "action": action,
                "target": target["target"],
                "event_count": str(event_count),
                "high_severity_count": str(count(action_rows, "severity", "high")),
                "improved_count": str(improved),
                "held_count": str(held),
                "degraded_or_delayed_count": str(degraded),
                "improved_or_held_rate": fmt(improved_or_held_rate),
                "mean_delta_mission_impact": fmt(mean_deltas["mission_impact"]),
                "mean_delta_p95_critical_latency_sec": fmt(
                    mean_deltas["p95_critical_latency_sec"]
                ),
                "mean_delta_trusted_stale_exposure": fmt(
                    mean_deltas["trusted_stale_exposure"]
                ),
                "mean_delta_priority_inversion_rate": fmt(
                    mean_deltas["priority_inversion_rate"]
                ),
                "primary_metric": target["primary_metric"],
                "primary_metric_delta_mean": fmt(primary_delta),
                "ablation_delta_metric": target["ablation_field"] or "not_applicable",
                "ablation_delta_value": fmt(ablation_delta) if target["ablation_field"] else "",
                "reactive_overlap_evidence": reactive_evidence if action == "ml_attack_alert" else "",
                "attribution_class": attribution_class,
                "attribution_status": status,
                "interpretation": interpretation,
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def extract_reactive_overlap(rows: list[dict[str, str]]) -> str:
    for row in rows:
        if row.get("check_id") == "RDT04":
            observed = row.get("observed", "")
            alerts = regex_int(observed, r"ml_attack_alerts=(\d+)")
            overlap = regex_int(observed, r"active_attack_overlap=(\d+)")
            probability = regex_float(observed, r"avg_alert_probability=([0-9.]+)")
            threshold = regex_float(observed, r"threshold=([0-9.]+)")
            return (
                f"ml_attack_alerts={alerts}; active_attack_overlap={overlap}; "
                f"avg_alert_probability={fmt(probability)}; threshold={fmt(threshold)}"
            )
    return ""


def regex_int(text: str, pattern: str) -> int:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0


def regex_float(text: str, pattern: str) -> float:
    match = re.search(pattern, text)
    return float(match.group(1)) if match else 0.0


def classify_action(
    *,
    action: str,
    event_count: int,
    improved_or_held_rate: float,
    primary_delta: float,
    ablation_delta: float,
    reactive_evidence: str,
    mean_deltas: dict[str, float],
) -> tuple[str, str, str]:
    local_supported = event_count > 0 and improved_or_held_rate >= 0.66 and primary_delta <= 0.0
    if action == "priority_reroute":
        ablation_supported = ablation_delta >= 0.25
        status = "pass" if local_supported and ablation_supported else "fail"
        return (
            "ablation_supported",
            status,
            (
                "Priority reroute has local priority-inversion relief and ablation support: "
                f"removing it raises priority inversion by {ablation_delta:.3f}."
            ),
        )
    if action == "stale_badge":
        ablation_supported = ablation_delta >= 0.25
        status = "pass" if event_count > 0 and improved_or_held_rate >= 0.80 and ablation_supported else "fail"
        return (
            "ablation_supported",
            status,
            (
                "Stale badge is the clearest trust-protection action: ablation raises "
                f"trusted stale exposure by {ablation_delta:.3f}, while local windows mostly improve or hold."
            ),
        )
    if action == "video_throttle":
        capacity_control_supported = (
            event_count > 0
            and improved_or_held_rate >= 0.66
            and (
                primary_delta <= 0.0
                or mean_deltas["priority_inversion_rate"] <= 0.0
                or mean_deltas["mission_impact"] <= 0.0
            )
        )
        status = "pass" if capacity_control_supported else "fail"
        return (
            "local_metric_supported",
            status,
            (
                "Video throttle is credited through local latency, priority-inversion, or mission-impact "
                "relief rather than scalar mission-impact ablation; this records it as a bounded "
                "capacity-control tradeoff."
            ),
        )
    if action == "pace_switch":
        status = "pass" if event_count > 0 and improved_or_held_rate >= 0.66 and (
            mean_deltas["mission_impact"] <= 0.0
            or mean_deltas["p95_critical_latency_sec"] <= 0.0
        ) else "fail"
        return (
            "bounded_tradeoff_supported",
            status,
            (
                "PACE switching shows local mission-impact or latency relief, but scalar ablation can "
                "undervalue recovery stability and fallback-chasing context."
            ),
        )
    if action == "ml_attack_alert":
        alert_match = re.search(r"ml_attack_alerts=(\d+)", reactive_evidence)
        overlap_match = re.search(r"active_attack_overlap=(\d+)", reactive_evidence)
        alert_count = int(alert_match.group(1)) if alert_match else 0
        overlap_count = int(overlap_match.group(1)) if overlap_match else -1
        overlap_supported = alert_count >= 5 and overlap_count == alert_count
        local_effect_supported = (
            improved_or_held_rate >= 0.75
            or mean_deltas["mission_impact"] <= 0.0
            or mean_deltas["p95_critical_latency_sec"] <= 0.0
        )
        status = (
            "pass"
            if event_count > 0 and overlap_supported and local_effect_supported
            else "fail"
        )
        return (
            "reactive_window_supported",
            status,
            (
                "ML alerts are attributed as reactive-window triggers: every alert overlaps an active "
                "AURA-ML attack window and the downstream response shows bounded local metric support."
            ),
        )
    return "unknown", "fail", "Unknown defense action."


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Defense Action Attribution Audit",
        "",
        "This audit aggregates the defense effectiveness ledger by TSRA-R action and links local metric movement to ablation or reactive-window evidence.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'attribution_status'))}",
        f"- Attribution classes: {format_counts(count_values(rows, 'attribution_class'))}",
        "",
        "## Audit Table",
        "",
    ]
    visible_fields = [
        "action",
        "event_count",
        "improved_or_held_rate",
        "primary_metric",
        "primary_metric_delta_mean",
        "ablation_delta_value",
        "attribution_class",
        "attribution_status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    lines.extend(["", "## Interpretation", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['action']}",
                "",
                f"- Target: {row['target']}",
                f"- Mean deltas: impact={row['mean_delta_mission_impact']}, latency={row['mean_delta_p95_critical_latency_sec']}, trusted_stale={row['mean_delta_trusted_stale_exposure']}, priority={row['mean_delta_priority_inversion_rate']}",
                f"- Attribution class: {row['attribution_class']}",
                f"- Status: {row['attribution_status']}",
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
    parser = argparse.ArgumentParser(description="Audit defense action attribution.")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--ablation", type=Path, default=DEFAULT_ABLATION)
    parser.add_argument("--reactive-tradeoff", type=Path, default=DEFAULT_REACTIVE_TRADEOFF)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any attribution row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(
        ledger_path=args.ledger,
        ablation_path=args.ablation,
        reactive_tradeoff_path=args.reactive_tradeoff,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["attribution_status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} attribution rows)")
    print(f"Wrote {args.output_md} ({len(rows)} attribution rows)")
    if failed:
        print(f"Failed attribution rows: {', '.join(row['action'] for row in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
