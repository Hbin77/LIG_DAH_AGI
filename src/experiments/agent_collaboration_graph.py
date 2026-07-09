from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_collaboration_graph.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_collaboration_graph.md")
DEFAULT_OUTPUT_MMD = Path("outputs/report_tables/agent_collaboration_graph.mmd")

SAFETY_BOUNDARY = (
    "closed simulation collaboration graph only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "edge_id",
    "source",
    "target",
    "interaction",
    "primary_evidence",
    "evidence_count",
    "validation_status",
    "purpose",
    "safety_boundary",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count_agent(rows: list[dict[str, str]], prefix: str) -> int:
    return sum(1 for row in rows if row.get("agent", "").startswith(prefix))


def count_status(rows: list[dict[str, str]], field: str, value: str) -> int:
    return sum(1 for row in rows if row.get(field) == value)


def evidence_counts(root: Path = Path(".")) -> dict[str, int]:
    trace_rows = read_csv(root / "outputs/report_tables/agent_decision_trace_summary.csv")
    coverage_rows = read_csv(root / "outputs/report_tables/attack_defense_coverage.csv")
    response_rows = read_csv(root / "outputs/report_tables/attack_defense_response_audit.csv")
    gate_rows = read_csv(root / "outputs/report_tables/metric_gate_summary.csv")
    return {
        "agent_interfaces": len(
            read_csv(root / "outputs/report_tables/agent_interface_manifest.csv")
        ),
        "agent_memory_audit_rows": len(
            read_csv(root / "outputs/report_tables/agent_memory_belief_audit.csv")
        ),
        "agent_tool_audit_rows": len(
            read_csv(root / "outputs/report_tables/agent_tool_usage_audit.csv")
        ),
        "submission_readiness_rows": len(
            read_csv(root / "outputs/report_tables/submission_readiness_audit.csv")
        ),
        "decision_causality_rows": len(
            read_csv(root / "outputs/report_tables/agent_decision_causality_audit.csv")
        ),
        "aura_traces": count_agent(trace_rows, "AURA"),
        "tsra_traces": count_agent(trace_rows, "TSRA-R"),
        "trace_rows": len(trace_rows),
        "aura_coa_cards": len(read_csv(root / "outputs/report_tables/aura_coa_cards.csv")),
        "coverage_rows": len(coverage_rows),
        "covered_rows": count_status(coverage_rows, "coverage_status", "covered"),
        "response_rows": len(response_rows),
        "complete_responses": count_status(response_rows, "response_status", "complete"),
        "battle_timeline_rows": len(
            read_csv(root / "outputs/report_tables/battle_timeline.csv")
        ),
        "operator_alerts": len(read_csv(root / "outputs/report_tables/operator_alerts.csv")),
        "defense_ledger_rows": len(
            read_csv(root / "outputs/report_tables/defense_effectiveness_ledger.csv")
        ),
        "closed_loop_episodes": len(
            read_csv(root / "outputs/report_tables/closed_loop_episode_replay.csv")
        ),
        "mission_decomposition_rows": len(
            read_csv(root / "outputs/report_tables/mission_impact_decomposition.csv")
        ),
        "metric_gates": len(gate_rows),
        "passing_metric_gates": count_status(gate_rows, "status", "pass"),
    }


def build_rows(root: Path = Path(".")) -> list[dict[str, str]]:
    counts = evidence_counts(root)
    specs = [
        (
            "E01",
            "AgentRuntime",
            "AURA/AURA-ML",
            "DecisionTrace runtime wraps observe, memory, tools, candidates, selected action, and feedback",
            "outputs/report_tables/agent_interface_manifest.csv",
            counts["agent_interfaces"],
            counts["agent_interfaces"] == 4,
            "Proves attack agents are not just direct function calls.",
        ),
        (
            "E02",
            "AURA/AURA-ML",
            "MissionSimulator",
            "AttackEvent simulated effects are emitted into the closed mission environment",
            "outputs/report_tables/aura_coa_cards.csv",
            counts["aura_coa_cards"],
            counts["aura_coa_cards"] >= 10,
            "Connects red-team decisions to simulator-visible attack effects.",
        ),
        (
            "E03",
            "MissionSimulator",
            "TSRA-R/TSRA-R-ML",
            "MissionState and metric signals are observed by defense agents",
            "outputs/report_tables/agent_decision_trace_summary.csv",
            counts["tsra_traces"],
            counts["tsra_traces"] >= 100,
            "Shows blue-team decisions are driven by runtime observations.",
        ),
        (
            "E04",
            "TSRA-R/TSRA-R-ML",
            "MissionSimulator",
            "DefenseEvent records feed bounded mitigation back into the simulator",
            "outputs/report_tables/operator_alerts.csv",
            counts["operator_alerts"],
            counts["operator_alerts"] >= 50,
            "Connects defense decisions to simulator-visible response actions.",
        ),
        (
            "E05",
            "MissionSimulator",
            "Mission Metrics",
            "MetricSnapshot and battle timeline expose mission impact movement",
            "outputs/report_tables/battle_timeline.csv",
            counts["battle_timeline_rows"],
            counts["battle_timeline_rows"] >= 40,
            "Keeps the red/blue loop tied to measurable mission effects.",
        ),
        (
            "E06",
            "Mission Metrics",
            "AURA/AURA-ML",
            "Metric feedback appears in AURA DecisionTrace rows",
            "outputs/report_tables/agent_decision_trace_summary.csv",
            counts["aura_traces"],
            counts["aura_traces"] >= 80,
            "Shows attack choices can be interpreted through observed mission state and feedback.",
        ),
        (
            "E07",
            "Mission Metrics",
            "TSRA-R/TSRA-R-ML",
            "Metric feedback appears in TSRA-R DecisionTrace rows",
            "outputs/report_tables/agent_decision_trace_summary.csv",
            counts["tsra_traces"],
            counts["tsra_traces"] >= 100,
            "Shows defense choices can be interpreted through observed mission state and feedback.",
        ),
        (
            "E08",
            "AURA Capabilities",
            "TSRA-R Capabilities",
            "Attack-defense coverage maps each attack capability to defense capabilities",
            "outputs/report_tables/attack_defense_coverage.csv",
            counts["coverage_rows"],
            counts["coverage_rows"] == 4 and counts["covered_rows"] == 4,
            "Makes red/blue responsibilities explicit for separate team development.",
        ),
        (
            "E09",
            "AttackEvent",
            "DefenseEvent",
            "Response audit verifies required defenses are active or timely",
            "outputs/report_tables/attack_defense_response_audit.csv",
            counts["response_rows"],
            counts["response_rows"] == 10 and counts["complete_responses"] == 10,
            "Prevents static mappings from replacing actual event-time response evidence.",
        ),
        (
            "E10",
            "DefenseEvent",
            "Operator Alerts",
            "Defense events are translated into operator-facing mission rationale",
            "outputs/report_tables/operator_alerts.csv",
            counts["operator_alerts"],
            counts["operator_alerts"] == 56,
            "Turns TSRA-R output into human-readable response guidance.",
        ),
        (
            "E11",
            "Mission Metrics",
            "Verifier/Package",
            "Metric gates and mission decomposition are included in final verification",
            "outputs/report_tables/metric_gate_summary.csv | outputs/report_tables/mission_impact_decomposition.csv",
            counts["passing_metric_gates"] + counts["mission_decomposition_rows"],
            counts["passing_metric_gates"] == 11 and counts["mission_decomposition_rows"] == 35,
            "Keeps scalar claims backed by gates and component-level evidence.",
        ),
        (
            "E12",
            "Attack/Defense/Alert Evidence",
            "Closed-Loop Episode Replay",
            "Each attack episode is joined to response coverage, operator alerts, and metric movement",
            "outputs/report_tables/closed_loop_episode_replay.csv",
            counts["closed_loop_episodes"],
            counts["closed_loop_episodes"] == 10,
            "Shows attack, defense, alert, and metric progression in one reviewable episode record.",
        ),
        (
            "E13",
            "DefenseEvent",
            "Defense Effectiveness Ledger",
            "Each TSRA-R defense event is joined to local metric movement before and after response",
            "outputs/report_tables/defense_effectiveness_ledger.csv",
            counts["defense_ledger_rows"],
            counts["defense_ledger_rows"] == 56,
            "Turns defensive actions into event-level effectiveness evidence.",
        ),
        (
            "E14",
            "AgentMemory",
            "Verifier/Package",
            "Memory and belief-state audit verifies evolving memory plus previous-action carryover",
            "outputs/report_tables/agent_memory_belief_audit.csv",
            counts["agent_memory_audit_rows"],
            counts["agent_memory_audit_rows"] == 9,
            "Proves memory is active loop state, not just a static trace field.",
        ),
        (
            "E15",
            "AgentTool",
            "Verifier/Package",
            "Tool usage audit verifies tool invocation, input summaries, and output summaries",
            "outputs/report_tables/agent_tool_usage_audit.csv",
            counts["agent_tool_audit_rows"],
            counts["agent_tool_audit_rows"] == 24,
            "Proves tools are invoked inside agent decision loops.",
        ),
        (
            "E16",
            "DecisionTrace",
            "Verifier/Package",
            "Decision causality audit verifies selected actions against candidates, tools, and score evidence",
            "outputs/report_tables/agent_decision_causality_audit.csv",
            counts["decision_causality_rows"],
            counts["decision_causality_rows"] == 399,
            "Proves selected actions are grounded in recorded decision evidence.",
        ),
        (
            "E17",
            "Submission Readiness Audit",
            "Verifier/Package",
            "Readiness audit verifies branch policy, reproduction commands, agent evidence, package inputs, and handoff docs",
            "outputs/report_tables/submission_readiness_audit.csv",
            counts["submission_readiness_rows"],
            counts["submission_readiness_rows"] == 10,
            "Connects teammate handoff and packaging readiness to the same evidence bundle.",
        ),
    ]
    rows = []
    for edge_id, source, target, interaction, evidence, evidence_count, ok, purpose in specs:
        rows.append(
            {
                "edge_id": edge_id,
                "source": source,
                "target": target,
                "interaction": interaction,
                "primary_evidence": evidence,
                "evidence_count": str(evidence_count),
                "validation_status": "verified" if ok else "incomplete",
                "purpose": purpose,
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def mermaid_graph(rows: list[dict[str, str]]) -> str:
    by_edge = {row["edge_id"]: row for row in rows}
    line = lambda edge_id: edge_label(by_edge[edge_id])
    return "\n".join(
        [
            "flowchart LR",
            "  Runtime[AgentRuntime\\nMemory / Tools / DecisionTrace]",
            "  Memory[AgentMemory\\nBelief state / previous action]",
            "  Tools[AgentTool / ToolRegistry\\nInput and output summaries]",
            "  Trace[DecisionTrace\\nCandidates / tools / selected action]",
            "  Aura[AURA / AURA-ML\\nAttack agents]",
            "  Sim[MissionSimulator\\nC4ISR / SATCOM environment]",
            "  Tsra[TSRA-R / TSRA-R-ML\\nDefense agents]",
            "  Metrics[Mission Metrics\\nImpact / resilience / decomposition]",
            "  Alerts[Operator Alerts\\nMission-readable defense guidance]",
            "  Ledger[Defense Effectiveness Ledger\\nDefense action -> metric movement]",
            "  Coverage[Capability Coverage\\nAttack to defense mapping]",
            "  Replay[Closed-Loop Episode Replay\\nAttack / defense / alert / metric episode]",
            "  Readiness[Submission Readiness Audit\\nBranch / package / handoff gates]",
            "  Verifier[Verifier / Package\\nReproducible evidence bundle]",
            f"  Runtime -->|{line('E01')}| Aura",
            f"  Runtime -->|memory state| Memory",
            f"  Runtime -->|tool registry| Tools",
            f"  Runtime -->|decision records| Trace",
            f"  Aura -->|{line('E02')}| Sim",
            f"  Sim -->|{line('E03')}| Tsra",
            f"  Tsra -->|{line('E04')}| Sim",
            f"  Sim -->|{line('E05')}| Metrics",
            f"  Metrics -->|{line('E06')}| Aura",
            f"  Metrics -->|{line('E07')}| Tsra",
            f"  Aura -->|{line('E08')}| Coverage",
            f"  Coverage -->|{line('E09')}| Tsra",
            f"  Tsra -->|{line('E10')}| Alerts",
            f"  Metrics -->|{line('E11')}| Verifier",
            f"  Sim -->|{line('E12')}| Replay",
            f"  Tsra -->|{line('E13')}| Ledger",
            f"  Metrics -->|local before/after| Ledger",
            f"  Memory -->|{line('E14')}| Verifier",
            f"  Tools -->|{line('E15')}| Verifier",
            f"  Trace -->|{line('E16')}| Verifier",
            f"  Readiness -->|{line('E17')}| Verifier",
            f"  Tsra -->|response evidence| Replay",
            f"  Alerts -->|alert evidence| Replay",
            f"  Replay -->|episode evidence| Verifier",
            f"  Ledger -->|effectiveness evidence| Verifier",
            f"  Alerts -->|operator evidence| Verifier",
            f"  Coverage -->|coverage evidence| Verifier",
        ]
    )


def edge_label(row: dict[str, str]) -> str:
    return f"{row['edge_id']} {row['evidence_count']} {row['validation_status']}"


def write_mmd(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(mermaid_graph(rows) + "\n", encoding="utf-8")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Collaboration Graph",
        "",
        "This graph summarizes how the attack agent, simulator, defense agent, operator alerts, and metric verifier cooperate inside the closed simulation.",
        "",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "```mermaid",
        mermaid_graph(rows),
        "```",
        "",
        "## Edge Evidence",
        "",
        "| edge_id | source | target | evidence_count | validation_status | primary_evidence | purpose |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["edge_id"]),
                    md(row["source"]),
                    md(row["target"]),
                    md(row["evidence_count"]),
                    md(row["validation_status"]),
                    md(row["primary_evidence"]),
                    md(row["purpose"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Interaction Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['edge_id']} {row['source']} -> {row['target']}",
                "",
                f"- Interaction: {row['interaction']}",
                f"- Evidence: {row['primary_evidence']}",
                f"- Evidence count: {row['evidence_count']}",
                f"- Validation status: {row['validation_status']}",
                f"- Purpose: {row['purpose']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the AURA/TSRA-R collaboration graph.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-mmd", type=Path, default=DEFAULT_OUTPUT_MMD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    write_mmd(args.output_mmd, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} collaboration edges)")
    print(f"Wrote {args.output_md} ({len(rows)} collaboration edges)")
    print(f"Wrote {args.output_mmd} ({len(rows)} collaboration edges)")


if __name__ == "__main__":
    main()
