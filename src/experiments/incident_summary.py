from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("outputs/report_tables/battle_timeline.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/incident_summary.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/incident_summary.md")

FIELDNAMES = [
    "experiment",
    "incident_id",
    "start_time_sec",
    "end_time_sec",
    "mission_phase",
    "active_link",
    "attack_summary",
    "aura_decision_reason",
    "defense_response",
    "tsra_r_decision_reason",
    "start_mission_impact",
    "peak_mission_impact",
    "end_mission_impact",
    "peak_p95_critical_latency_sec",
    "peak_trusted_stale_exposure",
    "peak_priority_inversion_rate",
    "residual_risk",
    "outcome",
    "safety_boundary",
]


def read_timeline(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def collect_incidents(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    incidents: list[dict[str, str]] = []
    experiments = sorted({row["experiment"] for row in rows})
    for experiment in experiments:
        experiment_rows = sorted(
            [row for row in rows if row["experiment"] == experiment],
            key=lambda row: as_float(row["time_sec"]),
        )
        attack_indices = [
            idx for idx, row in enumerate(experiment_rows) if row.get("attack_events")
        ]
        for incident_number, attack_idx in enumerate(attack_indices, start=1):
            next_attack_idx = (
                attack_indices[incident_number]
                if incident_number < len(attack_indices)
                else len(experiment_rows)
            )
            window = experiment_rows[attack_idx:next_attack_idx]
            if not window:
                continue
            attack_row = experiment_rows[attack_idx]
            incidents.append(build_incident(experiment, incident_number, attack_row, window))
    return incidents


def build_incident(
    experiment: str,
    incident_number: int,
    attack_row: dict[str, str],
    window: list[dict[str, str]],
) -> dict[str, str]:
    start_impact = as_float(attack_row.get("mission_impact"))
    impact_values = [as_float(row.get("mission_impact")) for row in window]
    latency_values = [as_float(row.get("p95_critical_latency_sec")) for row in window]
    trusted_stale_values = [as_float(row.get("trusted_stale_exposure")) for row in window]
    inversion_values = [as_float(row.get("priority_inversion_rate")) for row in window]

    peak_impact = max(impact_values) if impact_values else 0.0
    end_impact = impact_values[-1] if impact_values else start_impact
    peak_latency = max(latency_values) if latency_values else 0.0
    peak_trusted_stale = max(trusted_stale_values) if trusted_stale_values else 0.0
    peak_inversion = max(inversion_values) if inversion_values else 0.0

    defense_rows = [row for row in window if row.get("defense_events")]
    phase = first_non_empty([row.get("mission_phase", "") for row in window])
    active_link = first_non_empty([row.get("active_link", "") for row in window])
    risk = residual_risk(peak_latency, peak_trusted_stale, peak_inversion, end_impact)

    return {
        "experiment": experiment,
        "incident_id": f"{experiment}-inc-{incident_number:02d}",
        "start_time_sec": format_float(as_float(attack_row.get("time_sec"))),
        "end_time_sec": format_float(as_float(window[-1].get("time_sec"))),
        "mission_phase": phase,
        "active_link": active_link,
        "attack_summary": attack_row.get("attack_events", ""),
        "aura_decision_reason": extract_reason(attack_row.get("aura_decision", "")),
        "defense_response": summarize_defense_response(defense_rows),
        "tsra_r_decision_reason": summarize_tsra_reasons(defense_rows),
        "start_mission_impact": format_float(start_impact),
        "peak_mission_impact": format_float(peak_impact),
        "end_mission_impact": format_float(end_impact),
        "peak_p95_critical_latency_sec": format_float(peak_latency),
        "peak_trusted_stale_exposure": format_float(peak_trusted_stale),
        "peak_priority_inversion_rate": format_float(peak_inversion),
        "residual_risk": risk,
        "outcome": outcome_label(start_impact, peak_impact, end_impact, defense_rows),
        "safety_boundary": "closed simulation incident summary only; no RF, exploit, or live network action",
    }


def summarize_defense_response(defense_rows: list[dict[str, str]]) -> str:
    responses = []
    for row in defense_rows:
        time_sec = row.get("time_sec", "")
        events = row.get("defense_events", "")
        if events:
            responses.append(f"t={time_sec}: {events}")
    return " || ".join(responses) if responses else "no defense event inside incident window"


def summarize_tsra_reasons(defense_rows: list[dict[str, str]]) -> str:
    reasons = []
    for row in defense_rows:
        reason = extract_reason(row.get("tsra_r_decision", ""))
        if reason and reason not in reasons:
            reasons.append(reason)
    return " || ".join(reasons)


def residual_risk(
    peak_latency: float,
    peak_trusted_stale: float,
    peak_inversion: float,
    end_impact: float,
) -> str:
    risks = []
    if peak_latency >= 10:
        risks.append("critical latency spike")
    elif peak_latency >= 3:
        risks.append("moderate latency pressure")
    if peak_trusted_stale >= 0.25:
        risks.append("trusted stale exposure")
    if peak_inversion >= 0.2:
        risks.append("priority inversion pressure")
    if end_impact >= 0.2:
        risks.append("residual mission impact")
    return ", ".join(risks) if risks else "low residual risk after response"


def outcome_label(
    start_impact: float,
    peak_impact: float,
    end_impact: float,
    defense_rows: list[dict[str, str]],
) -> str:
    if not defense_rows:
        return "attack observed; no defense event in incident window"
    if end_impact <= start_impact * 0.8:
        return "contained with measurable impact reduction"
    if end_impact <= peak_impact * 0.8:
        return "stabilized after peak degradation"
    if end_impact <= start_impact + 0.03:
        return "held near initial impact"
    return "degradation persisted after response"


def extract_reason(text: str) -> str:
    marker = "reason="
    if marker not in text:
        return ""
    return text.split(marker, 1)[1].split(" || ", 1)[0].strip()


def first_non_empty(values: list[str]) -> str:
    for value in values:
        if value:
            return value
    return ""


def as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def format_float(value: float) -> str:
    return f"{value:.6g}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    visible_fields = [
        "experiment",
        "incident_id",
        "start_time_sec",
        "end_time_sec",
        "attack_summary",
        "defense_response",
        "peak_mission_impact",
        "residual_risk",
        "outcome",
    ]
    lines = [
        "# Incident Summary",
        "",
        "This table condenses the battle timeline into incident windows anchored on AURA attack events.",
        "",
        markdown_row(visible_fields),
        markdown_row(["---"] * len(visible_fields)),
    ]
    for row in rows:
        lines.append(markdown_row([markdown_cell(row.get(field, "")) for field in visible_fields]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value) for value in values) + " |"


def markdown_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate incident-level summaries from the AURA/TSRA-R battle timeline."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    timeline_rows = read_timeline(args.input)
    incidents = collect_incidents(timeline_rows)
    write_csv(args.output_csv, incidents)
    write_markdown(args.output_md, incidents)
    print(f"Wrote {args.output_csv} ({len(incidents)} incidents)")
    print(f"Wrote {args.output_md} ({len(incidents)} incidents)")


if __name__ == "__main__":
    main()
