from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/submission_readiness_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/submission_readiness_audit.md"

SAFETY_BOUNDARY = (
    "closed simulation readiness audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "area",
    "requirement",
    "evidence",
    "observed",
    "status",
    "handoff_value",
    "next_gate",
    "safety_boundary",
]


def path_exists(rel: str) -> bool:
    path = ROOT / rel
    return path.exists() and path.stat().st_size > 0


def read_text(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def count_csv_rows(rel: str) -> int:
    path = ROOT / rel
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def git_remote_refs() -> str:
    result = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", "main", "hbin"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def all_files_present(paths: list[str]) -> bool:
    return all(path_exists(path) for path in paths)


def row(
    *,
    check_id: str,
    area: str,
    requirement: str,
    evidence: list[str],
    observed: str,
    ok: bool,
    handoff_value: str,
    next_gate: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "requirement": requirement,
        "evidence": " | ".join(evidence),
        "observed": observed,
        "status": "pass" if ok else "fail",
        "handoff_value": handoff_value,
        "next_gate": next_gate,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def build_rows() -> list[dict[str, str]]:
    refs = git_remote_refs()
    readme = read_text("README.md")
    github_workflow = read_text("docs/process/GITHUB_WORKFLOW.md")
    manifest = read_text("outputs/package/submission_manifest.md")

    runtime_files = [
        "src/agents/runtime.py",
        "src/agents/memory.py",
        "src/agents/tools.py",
        "src/agents/schema.py",
        "docs/agents/AGENT_RUNTIME.md",
    ]
    attack_defense_files = [
        "src/aura/rule_decision_engine.py",
        "src/aura/candidate_generator.py",
        "src/aura/impact_estimator.py",
        "src/tsra_r/rule_defender.py",
        "src/tsra_r/ml_defender.py",
        "src/tsra_r/adaptive_defender.py",
        "docs/agents/AURA_ATTACK_AGENT.md",
        "docs/agents/TSRA_R_DEFENSE_AGENT.md",
    ]
    process_docs = [
        "docs/process/GITHUB_WORKFLOW.md",
        "docs/process/COMPETITION_DIRECTION.md",
        "docs/process/NEXT_DEVELOPMENT_QUEUE.md",
        "docs/process/DEVELOPMENT_LOG.md",
        "docs/process/FINAL_QA.md",
        "docs/process/SUBMISSION_PACKAGE.md",
    ]

    decision_counts = {
        "trace": count_csv_rows("outputs/report_tables/agent_decision_trace_summary.csv"),
        "contract": count_csv_rows("outputs/report_tables/agent_contract_validation.csv"),
        "quality": count_csv_rows("outputs/report_tables/decision_trace_quality_audit.csv"),
        "loop": count_csv_rows("outputs/report_tables/agent_loop_replay.csv"),
        "causality": count_csv_rows("outputs/report_tables/agent_decision_causality_audit.csv"),
        "memory": count_csv_rows("outputs/report_tables/agent_memory_belief_audit.csv"),
        "tool": count_csv_rows("outputs/report_tables/agent_tool_usage_audit.csv"),
    }
    closed_loop_counts = {
        "battle": count_csv_rows("outputs/report_tables/battle_timeline.csv"),
        "incident": count_csv_rows("outputs/report_tables/incident_summary.csv"),
        "alerts": count_csv_rows("outputs/report_tables/operator_alerts.csv"),
        "ledger": count_csv_rows("outputs/report_tables/defense_effectiveness_ledger.csv"),
        "episode": count_csv_rows("outputs/report_tables/closed_loop_episode_replay.csv"),
    }
    metric_counts = {
        "repeated": count_csv_rows("outputs/batch/repeated_experiment_summary.csv"),
        "resilience": count_csv_rows("outputs/batch/resilience_gain_summary.csv"),
        "ablation": count_csv_rows("outputs/batch/tsra_action_ablation_summary.csv"),
        "adaptive": count_csv_rows("outputs/batch/adaptive_memory_summary.csv"),
        "decomposition": count_csv_rows("outputs/report_tables/mission_impact_decomposition.csv"),
        "gates": count_csv_rows("outputs/report_tables/metric_gate_summary.csv"),
    }

    package_inputs = [
        "scripts/build_submission_package.py",
        "scripts/verify_submission_state.py",
        "outputs/package/submission_manifest.md",
        ".gitignore",
    ]
    model_metrics = [
        "outputs/models/aura_impact_model_metrics.json",
        "outputs/models/tsra_detector_metrics.json",
        "outputs/models/aura_mps_mlp_metrics.json",
    ]
    reproduction_commands = [
        "python3 -m src.ml.build_dataset",
        "python3 -m src.experiments.run_all",
        "python3 -m src.experiments.agent_decision_causality_audit",
        "python3 -m src.experiments.run_batch",
        "python3 scripts/build_submission_package.py",
        "python3 scripts/verify_submission_state.py",
    ]
    forbidden_team_phrases = ["나 혼자", "solo work", "one-person"]
    docs_text = "\n".join(read_text(path) for path in ["README.md", *process_docs])

    rows = [
        row(
            check_id="R01",
            area="Branch policy",
            requirement="Keep main preserved and use hbin as the shared development branch.",
            evidence=["README.md", "docs/process/GITHUB_WORKFLOW.md", "git ls-remote origin main hbin"],
            observed=(
                f"origin/main={'refs/heads/main' in refs}; "
                f"origin/hbin={'refs/heads/hbin' in refs}; "
                f"readme_no_main_push={'Do not push directly to `main`' in readme}; "
                f"workflow_mentions_hbin={'hbin' in github_workflow}"
            ),
            ok=(
                "refs/heads/main" in refs
                and "refs/heads/hbin" in refs
                and "Do not push directly to `main`" in readme
                and "hbin" in github_workflow
            ),
            handoff_value="A teammate can clone the repo and know that active work is on hbin while main stays protected.",
            next_gate="Final verifier must be run from branch hbin before any handoff.",
        ),
        row(
            check_id="R02",
            area="Reproduction commands",
            requirement="README must contain the end-to-end commands needed to regenerate core evidence.",
            evidence=["README.md"],
            observed=", ".join(
                f"{command}={'yes' if command in readme else 'no'}"
                for command in reproduction_commands
            ),
            ok=all(command in readme for command in reproduction_commands),
            handoff_value="The next developer can rebuild the same evidence without reverse-engineering command order.",
            next_gate="Any new experiment generator must be added to the Full Reproduction block.",
        ),
        row(
            check_id="R03",
            area="Agent runtime structure",
            requirement="Agent Runtime, Memory, Tool, and DecisionTrace assets must be present and evidenced.",
            evidence=[*runtime_files, "outputs/report_tables/agent_interface_manifest.csv"],
            observed=(
                f"runtime_files_present={all_files_present(runtime_files)}; "
                f"interface_rows={count_csv_rows('outputs/report_tables/agent_interface_manifest.csv')}"
            ),
            ok=all_files_present(runtime_files)
            and count_csv_rows("outputs/report_tables/agent_interface_manifest.csv") == 4,
            handoff_value="The agent claim is backed by code modules and generated interface evidence.",
            next_gate="Runtime changes must regenerate interface, memory, tool, and causality audits.",
        ),
        row(
            check_id="R04",
            area="Attack and defense separation",
            requirement="AURA and TSRA-R must be independently inspectable with capability coverage between them.",
            evidence=[
                *attack_defense_files,
                "outputs/report_tables/agent_capability_matrix.csv",
                "outputs/report_tables/attack_defense_coverage.csv",
                "outputs/report_tables/attack_defense_response_audit.csv",
            ],
            observed=(
                f"agent_files_present={all_files_present(attack_defense_files)}; "
                f"capability_rows={count_csv_rows('outputs/report_tables/agent_capability_matrix.csv')}; "
                f"coverage_rows={count_csv_rows('outputs/report_tables/attack_defense_coverage.csv')}; "
                f"response_rows={count_csv_rows('outputs/report_tables/attack_defense_response_audit.csv')}"
            ),
            ok=all_files_present(attack_defense_files)
            and count_csv_rows("outputs/report_tables/agent_capability_matrix.csv") == 10
            and count_csv_rows("outputs/report_tables/attack_defense_coverage.csv") == 4
            and count_csv_rows("outputs/report_tables/attack_defense_response_audit.csv") == 10,
            handoff_value="Attack-side and defense-side work can be assigned separately without losing interface coverage.",
            next_gate="New attack capability must declare the matching defense capability and response audit gate.",
        ),
        row(
            check_id="R05",
            area="Decision evidence",
            requirement="DecisionTrace, contract, memory, tool, and causality evidence must all be generated.",
            evidence=[
                "outputs/report_tables/agent_decision_trace_summary.csv",
                "outputs/report_tables/agent_contract_validation.csv",
                "outputs/report_tables/decision_trace_quality_audit.csv",
                "outputs/report_tables/agent_loop_replay.csv",
                "outputs/report_tables/agent_decision_causality_audit.csv",
                "outputs/report_tables/agent_memory_belief_audit.csv",
                "outputs/report_tables/agent_tool_usage_audit.csv",
            ],
            observed=", ".join(f"{key}={value}" for key, value in decision_counts.items()),
            ok=(
                decision_counts["trace"] >= 200
                and decision_counts["contract"] == 49
                and decision_counts["quality"] == 9
                and decision_counts["loop"] == 8
                and decision_counts["causality"] == 399
                and decision_counts["memory"] == 9
                and decision_counts["tool"] == 23
            ),
            handoff_value="Agent decisions remain explainable by generated evidence, not only by source code.",
            next_gate="Policy changes must keep all decision evidence rows passing final verification.",
        ),
        row(
            check_id="R06",
            area="Closed-loop evidence",
            requirement="Attack, defense, alerts, effectiveness, replay, and collaboration evidence must be present.",
            evidence=[
                "outputs/report_tables/battle_timeline.csv",
                "outputs/report_tables/incident_summary.csv",
                "outputs/report_tables/operator_alerts.csv",
                "outputs/report_tables/defense_effectiveness_ledger.csv",
                "outputs/report_tables/closed_loop_episode_replay.csv",
                "src/experiments/agent_collaboration_graph.py",
            ],
            observed=", ".join(f"{key}={value}" for key, value in closed_loop_counts.items()),
            ok=(
                closed_loop_counts["battle"] >= 40
                and closed_loop_counts["incident"] == 10
                and closed_loop_counts["alerts"] == 56
                and closed_loop_counts["ledger"] == 56
                and closed_loop_counts["episode"] == 10
                and path_exists("src/experiments/agent_collaboration_graph.py")
            ),
            handoff_value="The red/blue loop can be reviewed as episodes, actions, alerts, and metric movement.",
            next_gate="New closed-loop outputs must connect attack event, defense event, and metric evidence.",
        ),
        row(
            check_id="R07",
            area="Metric and ML evidence",
            requirement="Repeated metrics, action ablation, adaptive memory, decomposition, gates, and ML metrics must exist.",
            evidence=[
                "outputs/batch/repeated_experiment_summary.csv",
                "outputs/batch/resilience_gain_summary.csv",
                "outputs/batch/tsra_action_ablation_summary.csv",
                "outputs/batch/adaptive_memory_summary.csv",
                "outputs/report_tables/mission_impact_decomposition.csv",
                "outputs/report_tables/metric_gate_summary.csv",
                *model_metrics,
            ],
            observed=(
                ", ".join(f"{key}={value}" for key, value in metric_counts.items())
                + f"; model_metric_files={sum(1 for path in model_metrics if path_exists(path))}"
            ),
            ok=(
                metric_counts["repeated"] >= 7
                and metric_counts["resilience"] >= 4
                and metric_counts["ablation"] == 5
                and metric_counts["adaptive"] == 2
                and metric_counts["decomposition"] == 35
                and metric_counts["gates"] == 11
                and all_files_present(model_metrics)
            ),
            handoff_value="Quantitative claims are backed by batch, ablation, adaptive, gate, and model metric artifacts.",
            next_gate="Metric changes must update metric gates and package manifest before push.",
        ),
        row(
            check_id="R08",
            area="Package inputs",
            requirement="Package builder, final verifier, manifest, and Git ignore rules must be present.",
            evidence=package_inputs,
            observed=(
                f"package_inputs_present={all_files_present(package_inputs)}; "
                f"manifest_has_zip_sha256={'zip_sha256' in manifest}; "
                f"zip_ignored={'outputs/package/*.zip' in read_text('.gitignore')}"
            ),
            ok=all_files_present(package_inputs)
            and "zip_sha256" in manifest
            and "outputs/package/*.zip" in read_text(".gitignore"),
            handoff_value="The source ZIP can be regenerated locally without committing the binary ZIP file.",
            next_gate="Run build_submission_package.py after adding any source, doc, table, or figure artifact.",
        ),
        row(
            check_id="R09",
            area="Safety boundary",
            requirement="Core user-facing artifacts must state the closed simulation boundary.",
            evidence=[
                "README.md",
                "outputs/report_tables/aura_coa_cards.csv",
                "outputs/report_tables/incident_summary.csv",
                "outputs/report_tables/agent_collaboration_graph.csv",
            ],
            observed=(
                f"readme_sim_boundary={'does not attack real SATCOM' in readme}; "
                f"coa_no_rf={'no RF' in read_text('outputs/report_tables/aura_coa_cards.csv')}; "
                f"coa_no_exploit={'no exploit' in read_text('outputs/report_tables/aura_coa_cards.csv')}; "
                f"incident_closed_sim={'closed simulation' in read_text('outputs/report_tables/incident_summary.csv')}; "
                f"graph_closed_sim={'closed simulation' in read_text('outputs/report_tables/agent_collaboration_graph.csv')}"
            ),
            ok=(
                "does not attack real SATCOM" in readme
                and "no RF" in read_text("outputs/report_tables/aura_coa_cards.csv")
                and "no exploit" in read_text("outputs/report_tables/aura_coa_cards.csv")
                and "closed simulation" in read_text("outputs/report_tables/incident_summary.csv")
                and "closed simulation" in read_text("outputs/report_tables/agent_collaboration_graph.csv")
            ),
            handoff_value="The project remains a simulated mission-impact prototype, not operational offensive tooling.",
            next_gate="Reject changes that add RF parameters, exploit steps, or live packet/network actions.",
        ),
        row(
            check_id="R10",
            area="Team handoff docs",
            requirement="Process docs must preserve the team workflow and avoid one-person framing.",
            evidence=process_docs,
            observed=(
                f"process_docs_present={all_files_present(process_docs)}; "
                f"next_queue_has_p26={'P26' in read_text('docs/process/NEXT_DEVELOPMENT_QUEUE.md')}; "
                f"forbidden_team_phrases={sum(docs_text.count(phrase) for phrase in forbidden_team_phrases)}"
            ),
            ok=all_files_present(process_docs)
            and "P26" in read_text("docs/process/NEXT_DEVELOPMENT_QUEUE.md")
            and sum(docs_text.count(phrase) for phrase in forbidden_team_phrases) == 0,
            handoff_value="A teammate can continue from the queue and logs without inheriting personal-only wording.",
            next_gate="Each substantial change must update the queue, development log, verifier, and hbin branch.",
        ),
    ]
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Submission Readiness Audit",
        "",
        "This audit checks whether the shared hbin branch has enough reproducible evidence for teammate handoff and final packaging.",
        "",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| check_id | area | status | observed | handoff_value |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(item["check_id"]),
                    md(item["area"]),
                    md(item["status"]),
                    md(item["observed"]),
                    md(item["handoff_value"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for item in rows:
        lines.extend(
            [
                f"### {item['check_id']} {item['area']}",
                "",
                f"- Requirement: {item['requirement']}",
                f"- Evidence: {item['evidence']}",
                f"- Observed: {item['observed']}",
                f"- Status: {item['status']}",
                f"- Handoff value: {item['handoff_value']}",
                f"- Next gate: {item['next_gate']}",
                f"- Safety boundary: {item['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the submission readiness audit.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-incomplete",
        action="store_true",
        help="Exit with a non-zero status if any readiness row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [item for item in rows if item["status"] != "pass"]
    print(f"Wrote {args.output_csv.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {args.output_md.relative_to(ROOT)} ({len(rows)} rows)")
    if failed:
        print(f"Failed readiness rows: {', '.join(item['check_id'] for item in failed)}")
        if args.fail_on_incomplete:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
