from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/attack_defense_response_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/attack_defense_response_audit.md")

SAFETY_BOUNDARY = (
    "closed simulation response audit only; no RF, exploit, or live network action"
)

RESPONSE_WINDOW_SEC = 40.0

EXPERIMENTS = [
    "E5_rule_aura_tsra_r",
    "E7_ml_aura_ml_tsra_r",
]

FIELDNAMES = [
    "experiment",
    "attack_event_id",
    "attack_time_sec",
    "attack_capability",
    "attack_agent",
    "target_link",
    "required_runtime_defenses",
    "support_defenses",
    "active_defenses_at_attack",
    "response_defenses_after_attack",
    "covered_required_defenses",
    "missing_required_defenses",
    "missing_support_defenses",
    "first_required_response_latency_sec",
    "response_window_sec",
    "response_status",
    "audit_basis",
    "residual_risk",
    "safety_boundary",
]


@dataclass(frozen=True)
class ResponseSpec:
    required_runtime_defenses: tuple[str, ...]
    support_defenses: tuple[str, ...]
    residual_risk: str


RESPONSE_SPECS = {
    "bandwidth_limit": ResponseSpec(
        required_runtime_defenses=("priority_reroute",),
        support_defenses=("video_throttle", "pace_switch"),
        residual_risk="Capacity defense can still leave transient latency before optional load shedding catches up.",
    ),
    "failover_chasing": ResponseSpec(
        required_runtime_defenses=("ml_attack_alert",),
        support_defenses=("pace_switch", "priority_reroute"),
        residual_risk=(
            "Failover chasing is detected by the ML defense window; PACE support may already be active "
            "or may expire before a later attack window."
        ),
    ),
    "queue_pressure": ResponseSpec(
        required_runtime_defenses=("priority_reroute", "stale_badge"),
        support_defenses=("video_throttle",),
        residual_risk="Queue pressure can still create residual latency until reroute and throttling take effect.",
    ),
    "stale_cop_induction": ResponseSpec(
        required_runtime_defenses=("stale_badge",),
        support_defenses=(),
        residual_risk="Stale badge reduces trusted stale exposure but cannot recreate missing freshness.",
    ),
}


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


def build_rows(root: Path = Path("."), response_window_sec: float = RESPONSE_WINDOW_SEC) -> list[dict[str, str]]:
    rows = []
    for experiment in EXPERIMENTS:
        experiment_root = root / "outputs" / "experiments" / experiment
        attacks = read_jsonl(experiment_root / "attack_events.jsonl")
        defenses = read_jsonl(experiment_root / "defense_events.jsonl")
        rows.extend(audit_experiment(experiment, attacks, defenses, response_window_sec))
    return rows


def audit_experiment(
    experiment: str,
    attacks: list[dict[str, Any]],
    defenses: list[dict[str, Any]],
    response_window_sec: float,
) -> list[dict[str, str]]:
    output_rows = []
    for attack in attacks:
        candidate = attack.get("candidate", {})
        attack_capability = candidate.get("attack_type", "unknown")
        attack_time = float(attack.get("selected_at", candidate.get("start_time", 0.0)))
        spec = RESPONSE_SPECS.get(
            attack_capability,
            ResponseSpec(
                required_runtime_defenses=(),
                support_defenses=(),
                residual_risk="No response audit spec exists for this attack capability.",
            ),
        )

        active = active_defenses(defenses, attack_time)
        future = future_defenses(defenses, attack_time, response_window_sec)
        active_actions = {event.get("action", "") for event in active}
        future_actions = {event.get("action", "") for event in future}
        covered_actions = active_actions | future_actions

        required = set(spec.required_runtime_defenses)
        support = set(spec.support_defenses)
        covered_required = sorted(required & covered_actions)
        missing_required = sorted(required - covered_actions)
        missing_support = sorted(support - covered_actions)
        response_status = status_for(missing_required, missing_support, required)
        first_latency = first_required_latency(
            defenses=defenses,
            attack_time=attack_time,
            required_actions=required,
            response_window_sec=response_window_sec,
        )

        output_rows.append(
            {
                "experiment": experiment,
                "attack_event_id": str(attack.get("event_id", "")),
                "attack_time_sec": format_float(attack_time),
                "attack_capability": attack_capability,
                "attack_agent": str(attack.get("agent", "")),
                "target_link": str(candidate.get("target_link", "")),
                "required_runtime_defenses": ", ".join(spec.required_runtime_defenses),
                "support_defenses": ", ".join(spec.support_defenses) if spec.support_defenses else "none",
                "active_defenses_at_attack": summarize_events(active),
                "response_defenses_after_attack": summarize_events(future),
                "covered_required_defenses": ", ".join(covered_required) if covered_required else "none",
                "missing_required_defenses": ", ".join(missing_required) if missing_required else "none",
                "missing_support_defenses": ", ".join(missing_support) if missing_support else "none",
                "first_required_response_latency_sec": first_latency,
                "response_window_sec": format_float(response_window_sec),
                "response_status": response_status,
                "audit_basis": (
                    "defense is counted if active at attack time through details.until_sec "
                    "or emitted within the response window"
                ),
                "residual_risk": spec.residual_risk,
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return output_rows


def active_defenses(defenses: list[dict[str, Any]], attack_time: float) -> list[dict[str, Any]]:
    active = []
    for event in defenses:
        time_sec = float(event.get("time_sec", 0.0))
        until_sec = float(event.get("details", {}).get("until_sec", time_sec))
        if time_sec <= attack_time <= until_sec:
            active.append(event)
    return active


def future_defenses(
    defenses: list[dict[str, Any]],
    attack_time: float,
    response_window_sec: float,
) -> list[dict[str, Any]]:
    end_time = attack_time + response_window_sec
    return [
        event
        for event in defenses
        if attack_time < float(event.get("time_sec", 0.0)) <= end_time
    ]


def first_required_latency(
    defenses: list[dict[str, Any]],
    attack_time: float,
    required_actions: set[str],
    response_window_sec: float,
) -> str:
    if not required_actions:
        return "not_applicable"
    active_actions = {event.get("action", "") for event in active_defenses(defenses, attack_time)}
    if required_actions & active_actions:
        return "0"
    latencies = []
    for event in future_defenses(defenses, attack_time, response_window_sec):
        if event.get("action") in required_actions:
            latencies.append(float(event.get("time_sec", 0.0)) - attack_time)
    if not latencies:
        return "missing"
    return format_float(min(latencies))


def status_for(missing_required: list[str], missing_support: list[str], required: set[str]) -> str:
    if not required:
        return "no_spec"
    if missing_required:
        return "missed_required"
    if missing_support:
        return "required_covered_support_partial"
    return "complete"


def summarize_events(events: list[dict[str, Any]]) -> str:
    if not events:
        return "none"
    parts = []
    for event in events:
        action = event.get("action", "")
        time_sec = format_float(float(event.get("time_sec", 0.0)))
        until_sec = event.get("details", {}).get("until_sec")
        if until_sec is None:
            parts.append(f"{action}@{time_sec}")
        else:
            parts.append(f"{action}@{time_sec}-until-{format_float(float(until_sec))}")
    return "; ".join(parts)


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
    lines = [
        "# Attack-Defense Response Audit",
        "",
        "This audit checks whether defended AURA attack events have active or timely TSRA-R responses.",
        "",
        f"Response window: {format_float(RESPONSE_WINDOW_SEC)} seconds",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| experiment | attack_event_id | attack_capability | response_status | first_required_response_latency_sec | missing_required_defenses | missing_support_defenses |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["experiment"]),
                    md(row["attack_event_id"]),
                    md(row["attack_capability"]),
                    md(row["response_status"]),
                    md(row["first_required_response_latency_sec"]),
                    md(row["missing_required_defenses"]),
                    md(row["missing_support_defenses"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['experiment']} {row['attack_event_id']}",
                "",
                f"- Attack time: {row['attack_time_sec']}",
                f"- Attack capability: {row['attack_capability']}",
                f"- Attack agent: {row['attack_agent']}",
                f"- Target link: {row['target_link']}",
                f"- Required runtime defenses: {row['required_runtime_defenses']}",
                f"- Support defenses: {row['support_defenses']}",
                f"- Active defenses at attack: {row['active_defenses_at_attack']}",
                f"- Response defenses after attack: {row['response_defenses_after_attack']}",
                f"- Covered required defenses: {row['covered_required_defenses']}",
                f"- Missing required defenses: {row['missing_required_defenses']}",
                f"- Missing support defenses: {row['missing_support_defenses']}",
                f"- First required response latency sec: {row['first_required_response_latency_sec']}",
                f"- Response status: {row['response_status']}",
                f"- Audit basis: {row['audit_basis']}",
                f"- Residual risk: {row['residual_risk']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit timely TSRA-R responses to AURA attack events.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--response-window-sec", type=float, default=RESPONSE_WINDOW_SEC)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(response_window_sec=args.response_window_sec)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    missed = [row for row in rows if row["response_status"] == "missed_required"]
    print(f"Wrote {args.output_csv} ({len(rows)} response rows)")
    print(f"Wrote {args.output_md} ({len(rows)} response rows)")
    if missed:
        print(f"Missed required responses: {len(missed)}")


if __name__ == "__main__":
    main()
