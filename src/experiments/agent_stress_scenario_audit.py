from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.shared.schemas import AttackCandidate, AttackEvent
from src.simulator.mission_simulator import MissionSimulator
from src.tsra_r.ml_defender import MLTSRAR
from src.tsra_r.rule_defender import RuleTSRAR


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/agent_stress_scenario_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/agent_stress_scenario_audit.md"
DEFAULT_TEMP_ROOT = ROOT / "outputs/tmp_agent_stress_scenario"
MODEL_PATH = ROOT / "outputs/models/tsra_detector.pkl"

SAFETY_BOUNDARY = (
    "closed simulation stress-scenario audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "scenario_id",
    "scenario_goal",
    "defender_variant",
    "attack_profile",
    "attack_only_mission_impact",
    "defended_mission_impact",
    "mission_impact_reduction",
    "resilience_gain",
    "p95_reduction_sec",
    "trusted_stale_reduction",
    "priority_inversion_reduction",
    "attack_count",
    "defense_count",
    "required_gain",
    "required_impact_ceiling",
    "status",
    "interpretation",
    "safety_boundary",
]


@dataclass(frozen=True)
class StressAttackSpec:
    event_id: str
    attack_type: str
    target_link: str
    start_time: float
    duration_sec: float
    latency_ms_add: float
    jitter_ms_add: float
    packet_loss_add: float
    bandwidth_limit_mbps: float
    queue_pressure: bool


@dataclass(frozen=True)
class StressScenario:
    scenario_id: str
    goal: str
    attacks: tuple[StressAttackSpec, ...]


SCENARIOS = [
    StressScenario(
        scenario_id="stress_air_defense_queue_saturation",
        goal="Stress air-defense watch with SATCOM queue pressure and video saturation.",
        attacks=(
            StressAttackSpec(
                event_id="stress-atk-001",
                attack_type="queue_pressure",
                target_link="SATCOM",
                start_time=85.0,
                duration_sec=120.0,
                latency_ms_add=900.0,
                jitter_ms_add=180.0,
                packet_loss_add=0.04,
                bandwidth_limit_mbps=1.1,
                queue_pressure=True,
            ),
        ),
    ),
    StressScenario(
        scenario_id="stress_stale_cop_latency_chain",
        goal="Stress COP freshness and critical-window latency across two mission phases.",
        attacks=(
            StressAttackSpec(
                event_id="stress-atk-101",
                attack_type="stale_cop_induction",
                target_link="SATCOM",
                start_time=70.0,
                duration_sec=95.0,
                latency_ms_add=1000.0,
                jitter_ms_add=220.0,
                packet_loss_add=0.06,
                bandwidth_limit_mbps=1.2,
                queue_pressure=False,
            ),
            StressAttackSpec(
                event_id="stress-atk-102",
                attack_type="critical_window_degradation",
                target_link="SATCOM",
                start_time=185.0,
                duration_sec=75.0,
                latency_ms_add=700.0,
                jitter_ms_add=160.0,
                packet_loss_add=0.03,
                bandwidth_limit_mbps=1.4,
                queue_pressure=False,
            ),
        ),
    ),
    StressScenario(
        scenario_id="stress_pace_failover_pressure",
        goal="Stress PACE switching under SATCOM pressure followed by LTE pressure.",
        attacks=(
            StressAttackSpec(
                event_id="stress-atk-201",
                attack_type="failover_chasing",
                target_link="SATCOM",
                start_time=90.0,
                duration_sec=80.0,
                latency_ms_add=800.0,
                jitter_ms_add=180.0,
                packet_loss_add=0.04,
                bandwidth_limit_mbps=1.1,
                queue_pressure=True,
            ),
            StressAttackSpec(
                event_id="stress-atk-202",
                attack_type="failover_chasing",
                target_link="LTE",
                start_time=165.0,
                duration_sec=85.0,
                latency_ms_add=500.0,
                jitter_ms_add=140.0,
                packet_loss_add=0.05,
                bandwidth_limit_mbps=0.9,
                queue_pressure=True,
            ),
        ),
    ),
]


def make_attack_event(spec: StressAttackSpec) -> AttackEvent:
    candidate = AttackCandidate(
        attack_type=spec.attack_type,
        target_link=spec.target_link,
        target_traffic_classes=["all"],
        start_time=spec.start_time,
        duration_sec=spec.duration_sec,
        latency_ms_add=spec.latency_ms_add,
        jitter_ms_add=spec.jitter_ms_add,
        packet_loss_add=spec.packet_loss_add,
        bandwidth_limit_mbps=spec.bandwidth_limit_mbps,
        queue_pressure=spec.queue_pressure,
        reason="closed simulation stress scenario fixture",
    )
    return AttackEvent(
        event_id=spec.event_id,
        selected_at=spec.start_time,
        candidate=candidate,
        expected_impact={},
        reason=candidate.reason,
        score=0.0,
        agent="stress_fixture",
    )


def make_attacks(scenario: StressScenario) -> list[AttackEvent]:
    return [make_attack_event(spec) for spec in scenario.attacks]


def run_variant(
    *,
    scenario: StressScenario,
    variant: str,
    defender: Any | None,
    temp_root: Path,
) -> dict[str, float]:
    sim = MissionSimulator(
        duration_sec=300,
        seed=2607,
        output_dir=temp_root / scenario.scenario_id / variant,
    )
    return sim.run(defender=defender, fixed_attacks=make_attacks(scenario))


def collect_rows(temp_root: Path = DEFAULT_TEMP_ROOT) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for scenario in SCENARIOS:
        attack_only = run_variant(
            scenario=scenario,
            variant="attack_only",
            defender=None,
            temp_root=temp_root,
        )
        defended_variants: list[tuple[str, Any, float, float]] = [
            ("tsra_r_full", RuleTSRAR(mode="full"), 0.75, 0.25),
        ]
        defended_variants.append(
            ("tsra_r_ml", MLTSRAR(model_path=MODEL_PATH), 0.70, 0.25)
        )
        for variant, defender, required_gain, required_impact_ceiling in defended_variants:
            defended = run_variant(
                scenario=scenario,
                variant=variant,
                defender=defender,
                temp_root=temp_root,
            )
            rows.append(
                build_row(
                    check_id=f"AS{len(rows) + 1:02d}",
                    scenario=scenario,
                    variant=variant,
                    attack_only=attack_only,
                    defended=defended,
                    required_gain=required_gain,
                    required_impact_ceiling=required_impact_ceiling,
                )
            )
    return rows


def build_row(
    *,
    check_id: str,
    scenario: StressScenario,
    variant: str,
    attack_only: dict[str, float],
    defended: dict[str, float],
    required_gain: float,
    required_impact_ceiling: float,
) -> dict[str, str]:
    attack_impact = float(attack_only["mission_impact"])
    defended_impact = float(defended["mission_impact"])
    reduction = attack_impact - defended_impact
    gain = reduction / max(attack_impact, 1e-9)
    p95_reduction = (
        float(attack_only["p95_critical_latency_sec"])
        - float(defended["p95_critical_latency_sec"])
    )
    stale_reduction = (
        float(attack_only["trusted_stale_exposure"])
        - float(defended["trusted_stale_exposure"])
    )
    inversion_reduction = (
        float(attack_only["priority_inversion_rate"])
        - float(defended["priority_inversion_rate"])
    )
    defense_count = float(defended["defense_count"])
    status = (
        "pass"
        if gain >= required_gain
        and defended_impact <= required_impact_ceiling
        and p95_reduction > 0.0
        and stale_reduction > 0.0
        and inversion_reduction > 0.0
        and defense_count > 0.0
        else "fail"
    )
    return {
        "check_id": check_id,
        "scenario_id": scenario.scenario_id,
        "scenario_goal": scenario.goal,
        "defender_variant": variant,
        "attack_profile": attack_profile(scenario),
        "attack_only_mission_impact": fmt(attack_impact),
        "defended_mission_impact": fmt(defended_impact),
        "mission_impact_reduction": fmt(reduction),
        "resilience_gain": fmt(gain),
        "p95_reduction_sec": fmt(p95_reduction),
        "trusted_stale_reduction": fmt(stale_reduction),
        "priority_inversion_reduction": fmt(inversion_reduction),
        "attack_count": fmt(defended["attack_count"]),
        "defense_count": fmt(defense_count),
        "required_gain": fmt(required_gain),
        "required_impact_ceiling": fmt(required_impact_ceiling),
        "status": status,
        "interpretation": interpretation(
            variant=variant,
            scenario=scenario,
            gain=gain,
            defended_impact=defended_impact,
            p95_reduction=p95_reduction,
            stale_reduction=stale_reduction,
            inversion_reduction=inversion_reduction,
        ),
        "safety_boundary": SAFETY_BOUNDARY,
    }


def attack_profile(scenario: StressScenario) -> str:
    parts = []
    for spec in scenario.attacks:
        queue = "queue_pressure" if spec.queue_pressure else "no_queue_pressure"
        parts.append(
            f"{spec.event_id}:{spec.attack_type}@{spec.target_link}"
            f"/t={fmt(spec.start_time)}-{fmt(spec.start_time + spec.duration_sec)}"
            f"/bw={fmt(spec.bandwidth_limit_mbps)}"
            f"/lat+={fmt(spec.latency_ms_add)}"
            f"/loss+={fmt(spec.packet_loss_add)}"
            f"/{queue}"
        )
    return "; ".join(parts)


def interpretation(
    *,
    variant: str,
    scenario: StressScenario,
    gain: float,
    defended_impact: float,
    p95_reduction: float,
    stale_reduction: float,
    inversion_reduction: float,
) -> str:
    return (
        f"{variant} preserved stress resilience in {scenario.scenario_id}: "
        f"gain={fmt(gain)}, defended_impact={fmt(defended_impact)}, "
        f"p95_reduction_sec={fmt(p95_reduction)}, "
        f"trusted_stale_reduction={fmt(stale_reduction)}, "
        f"priority_inversion_reduction={fmt(inversion_reduction)}."
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
        "# Agent Stress Scenario Audit",
        "",
        "This audit runs closed-simulation stress fixtures and compares defended outcomes against attack-only outcomes.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'status'))}",
        "",
        "| check_id | scenario_id | defender_variant | resilience_gain | defended_mission_impact | status |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["check_id"]),
                    md(row["scenario_id"]),
                    md(row["defender_variant"]),
                    md(row["resilience_gain"]),
                    md(row["defended_mission_impact"]),
                    md(row["status"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['check_id']} {row['scenario_id']} {row['defender_variant']}",
                "",
                f"- Goal: {row['scenario_goal']}",
                f"- Attack profile: {row['attack_profile']}",
                f"- Attack-only mission impact: {row['attack_only_mission_impact']}",
                f"- Defended mission impact: {row['defended_mission_impact']}",
                f"- Mission impact reduction: {row['mission_impact_reduction']}",
                f"- Resilience gain: {row['resilience_gain']}",
                f"- P95 reduction sec: {row['p95_reduction_sec']}",
                f"- Trusted stale reduction: {row['trusted_stale_reduction']}",
                f"- Priority inversion reduction: {row['priority_inversion_reduction']}",
                f"- Defense count: {row['defense_count']}",
                f"- Status: {row['status']}",
                f"- Interpretation: {row['interpretation']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get(field, "")
        counts[key] = counts.get(key, 0) + 1
    return counts


def format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def fmt(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{numeric:.6g}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run closed-simulation agent stress scenario audit.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--temp-root", type=Path, default=DEFAULT_TEMP_ROOT)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any stress-scenario row fails.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    args = parse_args()
    rows = collect_rows(temp_root=args.temp_root)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {display_path(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.output_md)} ({len(rows)} rows)")
    if failed:
        print("Failed stress rows: " + ", ".join(row["check_id"] for row in failed))
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
