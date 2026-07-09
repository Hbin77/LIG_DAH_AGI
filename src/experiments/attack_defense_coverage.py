from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/attack_defense_coverage.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/attack_defense_coverage.md")

SAFETY_BOUNDARY = (
    "closed simulation coverage mapping only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "attack_capability",
    "attack_agents",
    "attack_evidence_count",
    "attack_observed_effect",
    "covered_by_defense_capabilities",
    "defense_agents",
    "defense_evidence_count",
    "coverage_logic",
    "coverage_status",
    "validation_gates",
    "battle_evidence",
    "residual_risk",
    "safety_boundary",
]


@dataclass(frozen=True)
class CoverageSpec:
    attack_capability: str
    defense_capabilities: tuple[str, ...]
    validation_gates: tuple[str, ...]
    coverage_logic: str
    battle_evidence: str
    residual_risk: str


COVERAGE_SPECS = [
    CoverageSpec(
        attack_capability="bandwidth_limit",
        defense_capabilities=("priority_reroute", "video_throttle", "pace_switch"),
        validation_gates=("G01", "G02", "G03", "G04", "G06", "G09"),
        coverage_logic=(
            "AURA reduces link capacity; TSRA-R protects critical traffic first, "
            "throttles optional video load, and can shift traffic to a bounded PACE fallback."
        ),
        battle_evidence="E5/E7 timeline shows attack events followed by defense events and metric snapshots.",
        residual_risk=(
            "Scalar mission impact can undervalue PACE switching and video throttling, "
            "so action ablation and gate metrics must be read with mission context."
        ),
    ),
    CoverageSpec(
        attack_capability="failover_chasing",
        defense_capabilities=("ml_attack_alert", "pace_switch", "adaptive_optional_action_gating"),
        validation_gates=("G02", "G03", "G04", "G08", "G09", "G10"),
        coverage_logic=(
            "AURA-ML follows the active fallback path; ML TSRA-R opens a reactive defense window, "
            "PACE switching bounds link degradation, and AdaptiveTSRA-R limits optional action overuse."
        ),
        battle_evidence="E7 timeline and metric gate G10 keep ML defense behavior distinct from E6.",
        residual_risk=(
            "The prototype models fallback behavior inside a simulator, not real PACE network control."
        ),
    ),
    CoverageSpec(
        attack_capability="queue_pressure",
        defense_capabilities=("priority_reroute", "video_throttle", "stale_badge"),
        validation_gates=("G01", "G02", "G03", "G04", "G05", "G06", "G07"),
        coverage_logic=(
            "AURA increases non-critical queue occupancy; TSRA-R reroutes critical messages, "
            "reduces optional video pressure, and marks stale COP data so it is not trusted as fresh."
        ),
        battle_evidence="E5/E7 battle timelines and incident summaries show queue pressure with defense response.",
        residual_risk=(
            "Queue pressure can still create residual latency during the response window before defenses take effect."
        ),
    ),
    CoverageSpec(
        attack_capability="stale_cop_induction",
        defense_capabilities=("stale_badge",),
        validation_gates=("G01", "G02", "G03", "G05", "G07"),
        coverage_logic=(
            "AURA degrades COP freshness; TSRA-R does not pretend stale data disappeared, "
            "but lowers trusted stale exposure by tagging stale COP observations."
        ),
        battle_evidence="Incident summary tracks attack-anchored windows with stale exposure and defense response.",
        residual_risk=(
            "Stale badge protects trust decisions but cannot recover missing sensor freshness by itself."
        ),
    ),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_rows(root: Path = Path(".")) -> list[dict[str, str]]:
    capability_rows = read_csv(root / "outputs/report_tables/agent_capability_matrix.csv")
    gate_rows = read_csv(root / "outputs/report_tables/metric_gate_summary.csv")
    capability_by_name = {row["capability"]: row for row in capability_rows if row.get("capability")}
    gate_by_id = {row["gate_id"]: row for row in gate_rows if row.get("gate_id")}

    rows = []
    for spec in COVERAGE_SPECS:
        attack = capability_by_name.get(spec.attack_capability, {})
        defenses = [capability_by_name.get(name, {}) for name in spec.defense_capabilities]
        missing_defenses = [
            name for name, row in zip(spec.defense_capabilities, defenses, strict=True) if not row
        ]
        gate_statuses = [
            f"{gate_id}:{gate_by_id.get(gate_id, {}).get('status', 'missing')}"
            for gate_id in spec.validation_gates
        ]
        failed_gates = [
            gate_id
            for gate_id in spec.validation_gates
            if gate_by_id.get(gate_id, {}).get("status") != "pass"
        ]
        status = (
            "covered"
            if attack and not missing_defenses and not failed_gates
            else "incomplete"
        )

        rows.append(
            {
                "attack_capability": spec.attack_capability,
                "attack_agents": attack.get("agent_family", "missing"),
                "attack_evidence_count": attack.get("evidence_count", "0"),
                "attack_observed_effect": attack.get("observed_effect", "missing attack capability evidence"),
                "covered_by_defense_capabilities": ", ".join(spec.defense_capabilities),
                "defense_agents": collect_agents(defenses),
                "defense_evidence_count": collect_evidence_counts(defenses),
                "coverage_logic": spec.coverage_logic,
                "coverage_status": status,
                "validation_gates": "; ".join(gate_statuses),
                "battle_evidence": spec.battle_evidence,
                "residual_risk": spec.residual_risk,
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def collect_agents(rows: list[dict[str, str]]) -> str:
    agents = []
    for row in rows:
        for agent in row.get("agent_family", "").split(","):
            agent = agent.strip()
            if agent and agent not in agents:
                agents.append(agent)
    return ", ".join(agents) if agents else "missing"


def collect_evidence_counts(rows: list[dict[str, str]]) -> str:
    parts = []
    for row in rows:
        capability = row.get("capability", "missing")
        evidence_count = row.get("evidence_count", "0")
        parts.append(f"{capability}={evidence_count}")
    return "; ".join(parts)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Attack-Defense Coverage",
        "",
        "This table maps each AURA attack capability to the TSRA-R defense capabilities that cover it.",
        "It is derived from the agent capability matrix and metric gate summary.",
        "",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| attack_capability | covered_by_defense_capabilities | coverage_status | validation_gates | residual_risk |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["attack_capability"]),
                    md(row["covered_by_defense_capabilities"]),
                    md(row["coverage_status"]),
                    md(row["validation_gates"]),
                    md(row["residual_risk"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['attack_capability']}",
                "",
                f"- Attack agents: {row['attack_agents']}",
                f"- Attack evidence count: {row['attack_evidence_count']}",
                f"- Attack observed effect: {row['attack_observed_effect']}",
                f"- Covered by defense capabilities: {row['covered_by_defense_capabilities']}",
                f"- Defense agents: {row['defense_agents']}",
                f"- Defense evidence count: {row['defense_evidence_count']}",
                f"- Coverage logic: {row['coverage_logic']}",
                f"- Coverage status: {row['coverage_status']}",
                f"- Validation gates: {row['validation_gates']}",
                f"- Battle evidence: {row['battle_evidence']}",
                f"- Residual risk: {row['residual_risk']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate attack-defense coverage mapping.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} coverage rows)")
    print(f"Wrote {args.output_md} ({len(rows)} coverage rows)")


if __name__ == "__main__":
    main()
