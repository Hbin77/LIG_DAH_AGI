from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/pace_transition_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/pace_transition_audit.md")

EXPERIMENTS = ["E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"]
CONTEXT_WINDOW_SEC = 40.0
SAFETY_BOUNDARY = (
    "closed simulation PACE audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "pace_event_id",
    "time_sec",
    "from_link_inferred",
    "target_link",
    "reason",
    "move_critical",
    "until_sec",
    "active_attacks_at_switch",
    "near_future_attacks",
    "mission_impact_at_switch",
    "p95_critical_latency_sec_at_switch",
    "trusted_stale_exposure_at_switch",
    "priority_inversion_rate_at_switch",
    "recovery_instability_at_switch",
    "audit_status",
    "residual_risk",
    "safety_boundary",
]


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


def build_rows(root: Path = Path(".")) -> list[dict[str, str]]:
    rows = []
    for experiment in EXPERIMENTS:
        exp_dir = root / "outputs" / "experiments" / experiment
        defenses = read_jsonl(exp_dir / "defense_events.jsonl")
        attacks = read_jsonl(exp_dir / "attack_events.jsonl")
        metrics = read_jsonl(exp_dir / "metric_snapshots.jsonl")
        rows.extend(audit_experiment(experiment, defenses, attacks, metrics))
    return rows


def audit_experiment(
    experiment: str,
    defenses: list[dict[str, Any]],
    attacks: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rows = []
    current_link = "SATCOM"
    for event in defenses:
        action = event.get("action", "")
        if action != "pace_switch":
            continue
        time_sec = float(event.get("time_sec", 0.0))
        details = event.get("details", {})
        target = str(details.get("target_link", ""))
        metric = nearest_metric(metrics, time_sec)
        active_attacks = attacks_in_window(attacks, time_sec, include_active=True)
        future_attacks = attacks_in_window(attacks, time_sec, include_active=False)
        audit_status = status_for(current_link, target, details)
        rows.append(
            {
                "experiment": experiment,
                "pace_event_id": str(event.get("event_id", "")),
                "time_sec": fmt(time_sec),
                "from_link_inferred": current_link,
                "target_link": target,
                "reason": str(details.get("reason", "")),
                "move_critical": str(bool(details.get("move_critical", False))).lower(),
                "until_sec": fmt(float(details.get("until_sec", time_sec))),
                "active_attacks_at_switch": summarize_attacks(active_attacks),
                "near_future_attacks": summarize_attacks(future_attacks),
                "mission_impact_at_switch": metric_value(metric, "mission_impact"),
                "p95_critical_latency_sec_at_switch": metric_value(
                    metric, "p95_critical_latency_sec"
                ),
                "trusted_stale_exposure_at_switch": metric_value(
                    metric, "trusted_stale_exposure"
                ),
                "priority_inversion_rate_at_switch": metric_value(
                    metric, "priority_inversion_rate"
                ),
                "recovery_instability_at_switch": metric_value(
                    metric, "recovery_instability"
                ),
                "audit_status": audit_status,
                "residual_risk": residual_risk(details),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
        if target:
            current_link = target
    return rows


def nearest_metric(metrics: list[dict[str, Any]], time_sec: float) -> dict[str, Any]:
    if not metrics:
        return {}
    return min(metrics, key=lambda row: abs(float(row.get("time_sec", 0.0)) - time_sec))


def attacks_in_window(
    attacks: list[dict[str, Any]],
    time_sec: float,
    include_active: bool,
) -> list[dict[str, Any]]:
    rows = []
    for attack in attacks:
        candidate = attack.get("candidate", {})
        start = float(attack.get("selected_at", candidate.get("start_time", 0.0)))
        duration = float(candidate.get("duration_sec", 0.0))
        if include_active:
            if start <= time_sec <= start + duration:
                rows.append(attack)
        elif time_sec < start <= time_sec + CONTEXT_WINDOW_SEC:
            rows.append(attack)
    return rows


def summarize_attacks(attacks: list[dict[str, Any]]) -> str:
    if not attacks:
        return "none"
    parts = []
    for attack in attacks:
        candidate = attack.get("candidate", {})
        parts.append(
            f"{attack.get('event_id', '')}:{candidate.get('attack_type', '')}"
            f"@{fmt(float(attack.get('selected_at', 0.0)))}"
            f"->{candidate.get('target_link', '')}"
        )
    return "; ".join(parts)


def status_for(from_link: str, target: str, details: dict[str, Any]) -> str:
    if not target:
        return "missing_target"
    if target == from_link:
        return "self_transition"
    reason = str(details.get("reason", ""))
    if "SATCOM degraded" in reason and from_link == "SATCOM":
        return "satcom_to_fallback"
    if "fallback link degraded" in reason and from_link != "SATCOM":
        return "fallback_reselect"
    return "reason_link_mismatch"


def residual_risk(details: dict[str, Any]) -> str:
    reason = str(details.get("reason", ""))
    if "fallback link degraded" in reason:
        return (
            "fallback reselection closes the immediate failover-chasing gap but can increase "
            "recovery_instability through extra PACE transitions"
        )
    return "initial PACE switch protects SATCOM degradation but may expose fallback links to later chasing"


def metric_value(metric: dict[str, Any], key: str) -> str:
    if key not in metric:
        return "missing"
    return fmt(float(metric[key]))


def fmt(value: float) -> str:
    return f"{value:.6g}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# PACE Transition Audit",
        "",
        "This audit explains why each TSRA-R PACE transition happened and what attack context surrounded it.",
        "",
        f"Context window: {fmt(CONTEXT_WINDOW_SEC)} seconds",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| experiment | pace_event_id | time_sec | from_link_inferred | target_link | reason | audit_status | recovery_instability_at_switch |",
        "|---|---|---:|---|---|---|---|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["experiment"]),
                    md(row["pace_event_id"]),
                    md(row["time_sec"]),
                    md(row["from_link_inferred"]),
                    md(row["target_link"]),
                    md(row["reason"]),
                    md(row["audit_status"]),
                    md(row["recovery_instability_at_switch"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['experiment']} {row['pace_event_id']}",
                "",
                f"- Time: {row['time_sec']}",
                f"- Inferred transition: {row['from_link_inferred']} -> {row['target_link']}",
                f"- Reason: {row['reason']}",
                f"- Move critical traffic: {row['move_critical']}",
                f"- Active attacks at switch: {row['active_attacks_at_switch']}",
                f"- Near future attacks: {row['near_future_attacks']}",
                f"- Mission impact at switch: {row['mission_impact_at_switch']}",
                f"- P95 critical latency at switch: {row['p95_critical_latency_sec_at_switch']}",
                f"- Trusted stale exposure at switch: {row['trusted_stale_exposure_at_switch']}",
                f"- Priority inversion at switch: {row['priority_inversion_rate_at_switch']}",
                f"- Recovery instability at switch: {row['recovery_instability_at_switch']}",
                f"- Audit status: {row['audit_status']}",
                f"- Residual risk: {row['residual_risk']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PACE transition audit table.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} PACE transitions)")
    print(f"Wrote {args.output_md} ({len(rows)} PACE transitions)")


if __name__ == "__main__":
    main()
