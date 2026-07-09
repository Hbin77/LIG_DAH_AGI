from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/competition_alignment_matrix.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/competition_alignment_matrix.md")

FIELDNAMES = [
    "alignment_id",
    "scoring_area",
    "competition_goal",
    "implemented_mechanism",
    "agent_or_component",
    "evidence_files",
    "evidence_status",
    "verification_notes",
    "next_gate",
]


@dataclass(frozen=True)
class ContentCheck:
    path: str
    phrase: str


@dataclass(frozen=True)
class RowCountCheck:
    path: str
    min_rows: int


@dataclass(frozen=True)
class AlignmentSpec:
    alignment_id: str
    scoring_area: str
    competition_goal: str
    implemented_mechanism: str
    agent_or_component: str
    evidence_files: list[str]
    next_gate: str
    content_checks: list[ContentCheck] = field(default_factory=list)
    row_checks: list[RowCountCheck] = field(default_factory=list)


ALIGNMENT_SPECS = [
    AlignmentSpec(
        alignment_id="A01",
        scoring_area="Defense mission grounding",
        competition_goal="Show a realistic defense mission environment instead of a generic IT scenario.",
        implemented_mechanism=(
            "Hybrid SATCOM disruption is modeled as C4ISR data-trust degradation: "
            "critical latency, stale COP, priority inversion, and trusted stale exposure."
        ),
        agent_or_component="MissionSimulator / scenario docs",
        evidence_files=[
            "docs/DAH2026_TSRA_v3_realistic_attack_rewrite.md",
            "src/simulator/mission_simulator.py",
            "outputs/figures/aura_tsra_architecture.png",
        ],
        next_gate="Any new feature must map to SATCOM, C4ISR, COP, PACE, or critical traffic.",
    ),
    AlignmentSpec(
        alignment_id="A02",
        scoring_area="Attack scenario",
        competition_goal="Make the attack technically concrete while staying inside a safe simulation boundary.",
        implemented_mechanism=(
            "AURA generates attack-effect candidates, estimates mission impact and detectability, "
            "then emits simulated AttackEvent records."
        ),
        agent_or_component="AURA",
        evidence_files=[
            "src/aura/candidate_generator.py",
            "src/aura/impact_estimator.py",
            "src/aura/rule_decision_engine.py",
            "outputs/report_tables/aura_coa_cards.csv",
        ],
        next_gate="Attack improvements must produce COA cards and never introduce live RF, exploit, or packet actions.",
        content_checks=[
            ContentCheck("outputs/report_tables/aura_coa_cards.csv", "Simulated effect only"),
            ContentCheck("outputs/report_tables/aura_coa_cards.csv", "no RF"),
        ],
        row_checks=[RowCountCheck("outputs/report_tables/aura_coa_cards.csv", 10)],
    ),
    AlignmentSpec(
        alignment_id="A03",
        scoring_area="Defense architecture",
        competition_goal="Tie detection, blocking, and recovery directly to the AURA attack effects.",
        implemented_mechanism=(
            "TSRA-R selects priority reroute, stale badge, video throttle, and PACE switch actions; "
            "ablation isolates which action protects which mission metric, and PACE transition audit "
            "explains fallback switching context."
        ),
        agent_or_component="TSRA-R",
        evidence_files=[
            "src/tsra_r/rule_defender.py",
            "src/tsra_r/ml_defender.py",
            "src/tsra_r/adaptive_defender.py",
            "src/experiments/pace_transition_audit.py",
            "outputs/batch/tsra_action_ablation_summary.csv",
            "outputs/report_tables/pace_transition_audit.csv",
        ],
        next_gate="Defense changes must be checked against mission impact plus at least one action-specific metric.",
        row_checks=[
            RowCountCheck("outputs/batch/tsra_action_ablation_summary.csv", 5),
            RowCountCheck("outputs/report_tables/pace_transition_audit.csv", 6),
        ],
    ),
    AlignmentSpec(
        alignment_id="A04",
        scoring_area="AI agent architecture",
        competition_goal="Show agent structure beyond direct Python policy calls.",
        implemented_mechanism=(
            "AgentRuntime wraps observe, memory summary, tool calls, candidate scoring, selected action, "
            "DecisionTrace, and feedback updates."
        ),
        agent_or_component="AgentRuntime / AgentMemory / ToolRegistry / DecisionTrace",
        evidence_files=[
            "src/agents/runtime.py",
            "src/agents/memory.py",
            "src/agents/tools.py",
            "src/agents/schema.py",
            "src/experiments/validate_event_contracts.py",
            "src/experiments/trace_quality_audit.py",
            "src/experiments/agent_loop_replay.py",
            "src/experiments/agent_interface_manifest.py",
            "src/experiments/agent_capability_matrix.py",
            "outputs/report_tables/agent_decision_trace_summary.csv",
            "outputs/report_tables/agent_contract_validation.csv",
            "outputs/report_tables/decision_trace_quality_audit.csv",
            "outputs/report_tables/agent_loop_replay.csv",
            "outputs/report_tables/agent_interface_manifest.csv",
            "outputs/report_tables/agent_capability_matrix.csv",
        ],
        next_gate=(
            "Agent changes must keep attack/defense interfaces and capabilities explicit."
        ),
        row_checks=[
            RowCountCheck("outputs/report_tables/agent_decision_trace_summary.csv", 200),
            RowCountCheck("outputs/report_tables/agent_contract_validation.csv", 49),
            RowCountCheck("outputs/report_tables/decision_trace_quality_audit.csv", 9),
            RowCountCheck("outputs/report_tables/agent_loop_replay.csv", 8),
            RowCountCheck("outputs/report_tables/agent_interface_manifest.csv", 4),
            RowCountCheck("outputs/report_tables/agent_capability_matrix.csv", 10),
        ],
    ),
    AlignmentSpec(
        alignment_id="A05",
        scoring_area="Attack-defense cooperation",
        competition_goal="Make the red and blue agents observable and explicitly connected by capability coverage.",
        implemented_mechanism=(
            "Battle timeline and incident summary merge AURA events, TSRA-R events, trace reasons, "
            "and metric movement for E5 and E7; attack-defense coverage maps each AURA capability "
            "to the TSRA-R capabilities and validation gates that cover it; response audit checks "
            "whether required defenses are active or emitted within the response window."
        ),
        agent_or_component="Battle timeline / Incident summary / Coverage / Response audit",
        evidence_files=[
            "src/experiments/battle_timeline.py",
            "src/experiments/incident_summary.py",
            "src/experiments/attack_defense_coverage.py",
            "src/experiments/attack_defense_response_audit.py",
            "outputs/report_tables/battle_timeline.csv",
            "outputs/report_tables/incident_summary.csv",
            "outputs/report_tables/attack_defense_coverage.csv",
            "outputs/report_tables/attack_defense_response_audit.csv",
        ],
        next_gate=(
            "New experiments must preserve attack events, defense events, trace reasons, metric snapshots, "
            "attack-to-defense capability coverage, and required response timing."
        ),
        content_checks=[
            ContentCheck("outputs/report_tables/battle_timeline.csv", "closed simulation"),
            ContentCheck("outputs/report_tables/incident_summary.csv", "closed simulation"),
            ContentCheck("outputs/report_tables/attack_defense_coverage.csv", "closed simulation"),
            ContentCheck("outputs/report_tables/attack_defense_response_audit.csv", "closed simulation"),
        ],
        row_checks=[
            RowCountCheck("outputs/report_tables/battle_timeline.csv", 40),
            RowCountCheck("outputs/report_tables/incident_summary.csv", 10),
            RowCountCheck("outputs/report_tables/attack_defense_coverage.csv", 4),
            RowCountCheck("outputs/report_tables/attack_defense_response_audit.csv", 10),
        ],
    ),
    AlignmentSpec(
        alignment_id="A06",
        scoring_area="ML contribution",
        competition_goal="Use ML where it changes a bounded agent decision, not as decoration.",
        implemented_mechanism=(
            "AURA uses impact prediction for candidate ranking; ML TSRA-R opens reactive defense windows "
            "from anomaly probability; GPU MPS training is kept as a separate scale experiment."
        ),
        agent_or_component="AURA ML / TSRA-R ML",
        evidence_files=[
            "src/ml/train_aura_impact_model.py",
            "src/ml/train_tsra_detector.py",
            "src/ml/train_aura_mps_mlp.py",
            "outputs/models/aura_impact_model_metrics.json",
            "outputs/models/tsra_detector_metrics.json",
            "outputs/models/aura_mps_mlp_metrics.json",
        ],
        next_gate="ML claims must state task, metric, model role, and whether the model changes closed-loop behavior.",
    ),
    AlignmentSpec(
        alignment_id="A07",
        scoring_area="Repeatable evidence",
        competition_goal="Avoid single-seed claims by keeping repeated experiments and resilience metrics.",
        implemented_mechanism=(
            "E1-E7 experiments are run as 30-seed batches with mission impact, latency, stale exposure, "
            "priority inversion, resilience gain summaries, and component-level mission impact decomposition."
        ),
        agent_or_component="Experiment runners",
        evidence_files=[
            "src/experiments/run_all.py",
            "src/experiments/run_batch.py",
            "src/experiments/metric_gate.py",
            "src/experiments/mission_impact_decomposition.py",
            "outputs/batch/repeated_experiment_summary.csv",
            "outputs/batch/resilience_gain_summary.csv",
            "outputs/report_tables/mission_impact_decomposition.csv",
            "outputs/report_tables/metric_gate_summary.csv",
        ],
        next_gate="Metric claims must pass metric_gate_summary and point to batch or dedicated experiments.",
        row_checks=[
            RowCountCheck("outputs/batch/repeated_experiment_summary.csv", 7),
            RowCountCheck("outputs/batch/resilience_gain_summary.csv", 4),
            RowCountCheck("outputs/report_tables/mission_impact_decomposition.csv", 35),
            RowCountCheck("outputs/report_tables/metric_gate_summary.csv", 11),
        ],
    ),
    AlignmentSpec(
        alignment_id="A08",
        scoring_area="Adaptive defense",
        competition_goal="Show memory-backed defense adaptation without changing the baseline experiments.",
        implemented_mechanism=(
            "AdaptiveTSRA-R keeps core defenses enabled and gates optional actions from recent AgentMemory evidence."
        ),
        agent_or_component="AdaptiveTSRA-R",
        evidence_files=[
            "src/tsra_r/adaptive_defender.py",
            "src/experiments/run_adaptive_memory.py",
            "outputs/batch/adaptive_memory_summary.csv",
            "outputs/figures/adaptive_memory_comparison.png",
        ],
        next_gate="Adaptive changes must be isolated from E1-E7 baseline and checked in adaptive_memory_summary.",
        row_checks=[RowCountCheck("outputs/batch/adaptive_memory_summary.csv", 2)],
    ),
    AlignmentSpec(
        alignment_id="A09",
        scoring_area="Safety boundary",
        competition_goal="Keep the prototype clearly separated from real-world offensive tooling.",
        implemented_mechanism=(
            "All attack outputs are simulated effects inside a local mission simulator; safety text is repeated "
            "in COA, timeline, incident, and package artifacts."
        ),
        agent_or_component="Safety guardrails",
        evidence_files=[
            "README.md",
            "outputs/report_tables/aura_coa_cards.csv",
            "outputs/report_tables/battle_timeline.csv",
            "outputs/report_tables/incident_summary.csv",
        ],
        next_gate="Reject any change that adds operational RF parameters, exploit code, or live network actions.",
        content_checks=[
            ContentCheck("README.md", "does not attack real SATCOM"),
            ContentCheck("outputs/report_tables/aura_coa_cards.csv", "no exploit"),
            ContentCheck("outputs/report_tables/incident_summary.csv", "no RF"),
        ],
    ),
    AlignmentSpec(
        alignment_id="A10",
        scoring_area="Team handoff and reproducibility",
        competition_goal="Make the shared branch reproducible for another teammate without using main for active work.",
        implemented_mechanism=(
            "README commands, package builder, manifest, final verifier, and process docs define the shared workflow."
        ),
        agent_or_component="README / packaging / QA scripts",
        evidence_files=[
            "README.md",
            "scripts/build_submission_package.py",
            "scripts/verify_submission_state.py",
            "docs/process/SUBMISSION_PACKAGE.md",
            "docs/process/GITHUB_WORKFLOW.md",
        ],
        next_gate="Before handoff, rebuild the package and run verify_submission_state on branch hbin.",
        content_checks=[
            ContentCheck("README.md", "Do not push directly to `main`"),
        ],
    ),
]


def count_csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


def check_spec(spec: AlignmentSpec) -> tuple[str, str]:
    notes = []
    failures = []

    for rel in spec.evidence_files:
        path = Path(rel)
        if not path.exists():
            failures.append(f"missing:{rel}")
            continue
        if path.stat().st_size <= 0:
            failures.append(f"empty:{rel}")

    for check in spec.content_checks:
        path = Path(check.path)
        if not path.exists():
            failures.append(f"missing:{check.path}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if check.phrase not in text:
            failures.append(f"phrase-missing:{check.path}:{check.phrase}")

    for check in spec.row_checks:
        path = Path(check.path)
        if not path.exists():
            failures.append(f"missing:{check.path}")
            continue
        row_count = count_csv_rows(path)
        notes.append(f"{check.path} rows={row_count}")
        if row_count < check.min_rows:
            failures.append(f"too-few-rows:{check.path}:{row_count}<{check.min_rows}")

    status = "verified" if not failures else "incomplete"
    if failures:
        notes.extend(failures)
    elif not notes:
        notes.append("all evidence files present")
    return status, "; ".join(notes)


def build_rows() -> list[dict[str, str]]:
    rows = []
    for spec in ALIGNMENT_SPECS:
        status, notes = check_spec(spec)
        rows.append(
            {
                "alignment_id": spec.alignment_id,
                "scoring_area": spec.scoring_area,
                "competition_goal": spec.competition_goal,
                "implemented_mechanism": spec.implemented_mechanism,
                "agent_or_component": spec.agent_or_component,
                "evidence_files": " | ".join(spec.evidence_files),
                "evidence_status": status,
                "verification_notes": notes,
                "next_gate": spec.next_gate,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    visible_fields = [
        "alignment_id",
        "scoring_area",
        "agent_or_component",
        "evidence_status",
        "next_gate",
    ]
    lines = [
        "# Competition Alignment Matrix",
        "",
        "This matrix keeps the implementation tied to the DAH preliminary-round direction.",
        "Each row maps a competition goal to concrete code, generated evidence, and the next development gate.",
        "",
        markdown_row(visible_fields),
        markdown_row(["---"] * len(visible_fields)),
    ]
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    lines.extend(
        [
            "",
            "## Evidence Detail",
            "",
        ]
    )
    for row in rows:
        lines.extend(
            [
                f"### {row['alignment_id']} {row['scoring_area']}",
                "",
                f"- Goal: {row['competition_goal']}",
                f"- Mechanism: {row['implemented_mechanism']}",
                f"- Evidence: {row['evidence_files']}",
                f"- Status: {row['evidence_status']}",
                f"- Notes: {row['verification_notes']}",
                f"- Next gate: {row['next_gate']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_row(values: list[str]) -> str:
    return "| " + " | ".join(values) + " |"


def markdown_cell(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the DAH competition alignment matrix.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-incomplete",
        action="store_true",
        help="Exit with a non-zero status if any alignment row is incomplete.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    incomplete = [row for row in rows if row["evidence_status"] != "verified"]
    print(f"Wrote {args.output_csv} ({len(rows)} rows)")
    print(f"Wrote {args.output_md} ({len(rows)} rows)")
    if incomplete:
        print(f"Incomplete alignment rows: {', '.join(row['alignment_id'] for row in incomplete)}")
        if args.fail_on_incomplete:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
