from __future__ import annotations

import argparse
import csv
import hashlib
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "outputs" / "package" / "DAH2026_소스코드_LIG_DAH_AGI.zip"
MANIFEST_PATH = ROOT / "outputs" / "package" / "submission_manifest.md"
EXPECTED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "scripts/build_submission_package.py",
    "scripts/freeze_release_candidate.py",
    "scripts/generate_release_handoff.py",
    "scripts/verify_submission_state.py",
    "scripts/verify_external_package_link.py",
    ".github/workflows/quality.yml",
    "tests/test_agent_regression.py",
    "docs/process/COMPETITION_DIRECTION.md",
    "docs/process/NEXT_DEVELOPMENT_QUEUE.md",
    "docs/process/DEVELOPMENT_LOG.md",
    "docs/process/FINAL_QA.md",
    "docs/process/SUBMISSION_PACKAGE.md",
    "docs/process/TEAM_HANDOFF.md",
    "src/agents/runtime.py",
    "src/aura/rule_decision_engine.py",
    "src/tsra_r/rule_defender.py",
    "src/tsra_r/adaptive_defender.py",
    "src/experiments/aura_attack_decision_path_audit.py",
    "src/experiments/cross_agent_context_audit.py",
    "src/experiments/defense_priority_decision_path_audit.py",
    "src/experiments/adaptive_defense_decision_path_audit.py",
    "src/experiments/run_ml_threshold_sweep.py",
    "src/experiments/battle_timeline.py",
    "src/experiments/incident_summary.py",
    "src/experiments/operator_alerts.py",
    "src/experiments/defense_effectiveness_ledger.py",
    "src/experiments/defense_action_attribution_audit.py",
    "src/experiments/closed_loop_episode_replay.py",
    "src/experiments/agent_coordination_latency_audit.py",
    "src/experiments/agent_stress_scenario_audit.py",
    "src/experiments/mission_thread_summary.py",
    "src/experiments/agent_engagement_scorecard.py",
    "src/experiments/agent_collaboration_graph.py",
    "src/experiments/competition_alignment.py",
    "src/experiments/validate_event_contracts.py",
    "src/experiments/trace_quality_audit.py",
    "src/experiments/agent_quality_gate_audit.py",
    "src/experiments/team_handoff_audit.py",
    "src/experiments/agent_runtime_invariant_audit.py",
    "src/experiments/agent_loop_replay.py",
    "src/experiments/agent_decision_causality_audit.py",
    "src/experiments/agent_decision_margin_audit.py",
    "src/experiments/agent_goal_alignment_audit.py",
    "src/experiments/agent_decision_feedback_audit.py",
    "src/experiments/agent_memory_belief_audit.py",
    "src/experiments/agent_memory_influence_audit.py",
    "src/experiments/agent_tool_usage_audit.py",
    "src/experiments/agent_interface_manifest.py",
    "src/experiments/agent_capability_matrix.py",
    "src/experiments/attack_defense_coverage.py",
    "src/experiments/attack_defense_response_audit.py",
    "src/experiments/pace_transition_audit.py",
    "src/experiments/mission_impact_decomposition.py",
    "src/experiments/metric_gate.py",
    "src/experiments/ml_contribution_audit.py",
    "src/experiments/ml_attack_decision_path_audit.py",
    "src/experiments/ml_defense_decision_path_audit.py",
    "src/experiments/ml_red_blue_interaction_audit.py",
    "src/experiments/reactive_defense_tradeoff_audit.py",
    "src/experiments/tsra_detector_calibration_audit.py",
    "src/experiments/safety_boundary_audit.py",
    "src/experiments/reproduction_order_audit.py",
    "src/experiments/submission_readiness_audit.py",
    "outputs/experiments/experiment_summary.csv",
    "outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_rule_delegate_traces.jsonl",
    "outputs/batch/repeated_experiment_summary.csv",
    "outputs/batch/resilience_gain_summary.csv",
    "outputs/batch/tsra_action_ablation_summary.csv",
    "outputs/batch/adaptive_memory_summary.csv",
    "outputs/report_tables/cross_agent_context_audit.csv",
    "outputs/report_tables/cross_agent_context_audit.md",
    "outputs/report_tables/defense_priority_decision_path_audit.csv",
    "outputs/report_tables/defense_priority_decision_path_audit.md",
    "outputs/report_tables/adaptive_defense_decision_path_audit.csv",
    "outputs/report_tables/adaptive_defense_decision_path_audit.md",
    "outputs/batch/ml_threshold_sweep_raw.csv",
    "outputs/batch/ml_threshold_sweep_summary.csv",
    "outputs/report_tables/agent_decision_trace_summary.csv",
    "outputs/report_tables/aura_coa_cards.csv",
    "outputs/report_tables/battle_timeline.csv",
    "outputs/report_tables/incident_summary.csv",
    "outputs/report_tables/operator_alerts.csv",
    "outputs/report_tables/operator_alerts.md",
    "outputs/report_tables/defense_effectiveness_ledger.csv",
    "outputs/report_tables/defense_effectiveness_ledger.md",
    "outputs/report_tables/defense_action_attribution_audit.csv",
    "outputs/report_tables/defense_action_attribution_audit.md",
    "outputs/report_tables/closed_loop_episode_replay.csv",
    "outputs/report_tables/closed_loop_episode_replay.md",
    "outputs/report_tables/agent_coordination_latency_audit.csv",
    "outputs/report_tables/agent_coordination_latency_audit.md",
    "outputs/report_tables/agent_stress_scenario_audit.csv",
    "outputs/report_tables/agent_stress_scenario_audit.md",
    "outputs/report_tables/mission_thread_summary.csv",
    "outputs/report_tables/mission_thread_summary.md",
    "outputs/report_tables/agent_engagement_scorecard.csv",
    "outputs/report_tables/agent_engagement_scorecard.md",
    "outputs/report_tables/agent_collaboration_graph.csv",
    "outputs/report_tables/agent_collaboration_graph.md",
    "outputs/report_tables/agent_collaboration_graph.mmd",
    "outputs/report_tables/competition_alignment_matrix.csv",
    "outputs/report_tables/competition_alignment_matrix.md",
    "outputs/report_tables/agent_contract_validation.csv",
    "outputs/report_tables/agent_contract_validation.md",
    "outputs/report_tables/decision_trace_quality_audit.csv",
    "outputs/report_tables/decision_trace_quality_audit.md",
    "outputs/report_tables/agent_quality_gate_audit.csv",
    "outputs/report_tables/agent_quality_gate_audit.md",
    "outputs/report_tables/team_handoff_audit.csv",
    "outputs/report_tables/team_handoff_audit.md",
    "outputs/report_tables/agent_runtime_invariant_audit.csv",
    "outputs/report_tables/agent_runtime_invariant_audit.md",
    "outputs/report_tables/agent_loop_replay.csv",
    "outputs/report_tables/agent_loop_replay.md",
    "outputs/report_tables/agent_decision_causality_audit.csv",
    "outputs/report_tables/agent_decision_causality_audit.md",
    "outputs/report_tables/agent_decision_margin_audit.csv",
    "outputs/report_tables/agent_decision_margin_audit.md",
    "outputs/report_tables/agent_goal_alignment_audit.csv",
    "outputs/report_tables/agent_goal_alignment_audit.md",
    "outputs/report_tables/agent_decision_feedback_audit.csv",
    "outputs/report_tables/agent_decision_feedback_audit.md",
    "outputs/report_tables/agent_memory_belief_audit.csv",
    "outputs/report_tables/agent_memory_belief_audit.md",
    "outputs/report_tables/agent_memory_influence_audit.csv",
    "outputs/report_tables/agent_memory_influence_audit.md",
    "outputs/report_tables/aura_attack_decision_path_audit.csv",
    "outputs/report_tables/aura_attack_decision_path_audit.md",
    "outputs/report_tables/agent_tool_usage_audit.csv",
    "outputs/report_tables/agent_tool_usage_audit.md",
    "outputs/report_tables/agent_interface_manifest.csv",
    "outputs/report_tables/agent_interface_manifest.md",
    "outputs/report_tables/agent_capability_matrix.csv",
    "outputs/report_tables/agent_capability_matrix.md",
    "outputs/report_tables/attack_defense_coverage.csv",
    "outputs/report_tables/attack_defense_coverage.md",
    "outputs/report_tables/attack_defense_response_audit.csv",
    "outputs/report_tables/attack_defense_response_audit.md",
    "outputs/report_tables/pace_transition_audit.csv",
    "outputs/report_tables/pace_transition_audit.md",
    "outputs/report_tables/mission_impact_decomposition.csv",
    "outputs/report_tables/mission_impact_decomposition.md",
    "outputs/report_tables/metric_gate_summary.csv",
    "outputs/report_tables/metric_gate_summary.md",
    "outputs/report_tables/ml_contribution_audit.csv",
    "outputs/report_tables/ml_contribution_audit.md",
    "outputs/report_tables/ml_attack_decision_path_audit.csv",
    "outputs/report_tables/ml_attack_decision_path_audit.md",
    "outputs/report_tables/ml_defense_decision_path_audit.csv",
    "outputs/report_tables/ml_defense_decision_path_audit.md",
    "outputs/report_tables/ml_red_blue_interaction_audit.csv",
    "outputs/report_tables/ml_red_blue_interaction_audit.md",
    "outputs/report_tables/reactive_defense_tradeoff_audit.csv",
    "outputs/report_tables/reactive_defense_tradeoff_audit.md",
    "outputs/report_tables/ml_threshold_sweep.csv",
    "outputs/report_tables/ml_threshold_sweep.md",
    "outputs/report_tables/tsra_detector_calibration_audit.csv",
    "outputs/report_tables/tsra_detector_calibration_audit.md",
    "outputs/report_tables/tsra_detector_calibration_bins.csv",
    "outputs/report_tables/safety_boundary_audit.csv",
    "outputs/report_tables/safety_boundary_audit.md",
    "outputs/report_tables/reproduction_order_audit.csv",
    "outputs/report_tables/reproduction_order_audit.md",
    "outputs/report_tables/submission_readiness_audit.csv",
    "outputs/report_tables/submission_readiness_audit.md",
    "outputs/figures/aura_tsra_architecture.png",
    "outputs/figures/batch_resilience_gain.png",
    "outputs/figures/tsra_action_ablation.png",
    "outputs/figures/adaptive_memory_comparison.png",
    "outputs/models/aura_impact_model_metrics.json",
    "outputs/models/tsra_detector_metrics.json",
    "outputs/models/aura_mps_mlp_metrics.json",
]

ZIP_REQUIRED_FILES = REQUIRED_FILES + [
    "outputs/package/submission_manifest.md",
]

REPO_ONLY_REQUIRED_FILES = [
    "outputs/package/release_handoff.md",
]


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def observed_value(row: dict[str, str], key: str) -> str:
    match = re.search(rf"(?:^|[;,\s]){re.escape(key)}=([^;,]+)", row.get("observed", ""))
    return match.group(1).strip() if match else ""


def observed_int(row: dict[str, str], key: str) -> int:
    value = observed_value(row, key)
    if "/" in value:
        value = value.split("/", 1)[0]
    try:
        return int(float(value))
    except ValueError:
        return 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest_value(manifest_text: str, key: str) -> str:
    match = re.search(rf"^- {re.escape(key)}: `?([^`\n]+)`?$", manifest_text, re.MULTILINE)
    require(match is not None, f"manifest missing {key}")
    return match.group(1).strip()


def manifest_int(manifest_text: str, key: str) -> int:
    value = manifest_value(manifest_text, key)
    try:
        return int(value)
    except ValueError as exc:
        raise AssertionError(f"manifest {key} is not an integer: {value}") from exc


def manifest_file_list(manifest_text: str) -> set[str]:
    marker = "## 포함 파일"
    require(marker in manifest_text, "manifest missing included-file section")
    section = manifest_text.split(marker, 1)[1]
    return set(re.findall(r"^- `([^`]+)`$", section, flags=re.MULTILINE))


def check_required_files() -> list[str]:
    checked = []
    for rel in [*REQUIRED_FILES, *REPO_ONLY_REQUIRED_FILES]:
        path = ROOT / rel
        require(path.exists(), f"missing required file: {rel}")
        require(path.stat().st_size > 0, f"empty required file: {rel}")
        checked.append(rel)
    return checked


def check_regression_tests() -> list[str]:
    result = subprocess.run(
        ["python3", "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(
        result.returncode == 0,
        "agent regression tests failed: "
        + (result.stdout.strip() or result.stderr.strip() or "no output"),
    )
    output = "\n".join(
        part for part in [result.stdout.strip(), result.stderr.strip()] if part
    )
    match = re.search(r"Ran\s+(\d+)\s+tests?", output)
    test_count = int(match.group(1)) if match else 0
    require(
        test_count >= 7,
        f"expected at least 7 agent regression tests, got {test_count}",
    )
    return [f"agent_regression_tests={test_count} pass"]


def check_csv_outputs() -> list[str]:
    checks = []

    experiment_rows = read_csv("outputs/experiments/experiment_summary.csv")
    experiments = {row["experiment"] for row in experiment_rows}
    require(
        {"E1_baseline", "E3_rule_aura", "E5_rule_aura_tsra_r"}.issubset(experiments),
        f"experiment_summary missing baseline/core experiments: {sorted(experiments)}",
    )
    checks.append(f"experiment_summary rows={len(experiment_rows)}")

    repeated_rows = read_csv("outputs/batch/repeated_experiment_summary.csv")
    require(len(repeated_rows) >= 5, "repeated_experiment_summary has too few rows")
    checks.append(f"repeated_experiment_summary rows={len(repeated_rows)}")

    resilience_rows = read_csv("outputs/batch/resilience_gain_summary.csv")
    require(len(resilience_rows) >= 1, "resilience_gain_summary is empty")
    checks.append(f"resilience_gain_summary rows={len(resilience_rows)}")

    ablation_rows = read_csv("outputs/batch/tsra_action_ablation_summary.csv")
    require(len(ablation_rows) == 5, f"expected 5 TSRA ablation rows, got {len(ablation_rows)}")
    checks.append("tsra_action_ablation_summary rows=5")

    adaptive_rows = read_csv("outputs/batch/adaptive_memory_summary.csv")
    adaptive_conditions = {row["condition"] for row in adaptive_rows}
    require(
        adaptive_conditions == {"full_tsra_r", "adaptive_tsra_r"},
        f"unexpected adaptive conditions: {sorted(adaptive_conditions)}",
    )
    checks.append("adaptive_memory_summary conditions=full/adaptive")

    trace_rows = read_csv("outputs/report_tables/agent_decision_trace_summary.csv")
    require(len(trace_rows) == 262, f"expected 262 trace summary rows, got {len(trace_rows)}")
    e7_delegate_summary_rows = [
        row
        for row in trace_rows
        if row["experiment"] == "E7_ml_aura_ml_tsra_r"
        and row.get("trace_file") == "tsra_r_rule_delegate_traces.jsonl"
        and row["agent"] == "TSRA-R"
        and row["policy"] == "rule_defense_full"
    ]
    require(
        len(e7_delegate_summary_rows) == 47,
        f"trace summary expected 47 E7 delegate rows, got {len(e7_delegate_summary_rows)}",
    )
    require(
        any(row["selected_action"] != "no_op" for row in e7_delegate_summary_rows),
        "trace summary E7 delegate rows never select a defense action",
    )
    require(
        all(row.get("trace_id") for row in e7_delegate_summary_rows),
        "trace summary E7 delegate rows missing trace ids",
    )
    checks.append("agent_decision_trace_summary rows=262 sidecar=47 pass")

    contract_rows = read_csv("outputs/report_tables/agent_contract_validation.csv")
    require(len(contract_rows) == 50, f"expected 50 contract checks, got {len(contract_rows)}")
    failed_contracts = [
        f"{row['experiment']}:{row['contract']}"
        for row in contract_rows
        if row.get("status") != "pass"
    ]
    require(not failed_contracts, f"failed agent contracts: {failed_contracts[:8]}")
    required_contracts = {
        "attack_event_schema",
        "defense_event_schema",
        "metric_snapshot_schema",
        "mission_event_schema",
        "aura_decision_trace_schema",
        "tsra-r_decision_trace_schema",
        "tsra-r_rule_delegate_trace_schema",
        "agent_cross_contract",
    }
    observed_contracts = {row["contract"] for row in contract_rows}
    require(
        required_contracts.issubset(observed_contracts),
        f"agent contract validation missing contracts: {sorted(required_contracts - observed_contracts)}",
    )
    require(
        any(
            row["experiment"] == "E7_ml_aura_ml_tsra_r"
            and row["contract"] == "tsra-r_rule_delegate_trace_schema"
            and row["status"] == "pass"
            and int(float(row["checked_rows"])) == 47
            for row in contract_rows
        ),
        "agent contract validation missing E7 rule delegate trace schema",
    )
    require(
        any(
            row["experiment"] == "E7_ml_aura_ml_tsra_r"
            and row["contract"] == "agent_cross_contract"
            and "tsra_r_rule_delegate_traces.jsonl" in row["required_files"]
            and row["status"] == "pass"
            for row in contract_rows
        ),
        "agent cross-contract missing E7 rule delegate trace file",
    )
    checks.append("agent_contract_validation rows=50 pass")

    trace_quality_rows = read_csv("outputs/report_tables/decision_trace_quality_audit.csv")
    require(
        len(trace_quality_rows) == 10,
        f"expected 10 trace quality audit rows, got {len(trace_quality_rows)}",
    )
    failed_trace_quality = [
        f"{row['experiment']}:{row['agent']}:{row['policy']}"
        for row in trace_quality_rows
        if row.get("status") != "pass"
    ]
    require(not failed_trace_quality, f"failed trace quality rows: {failed_trace_quality[:8]}")
    require(
        any(row["agent"].startswith("AURA") for row in trace_quality_rows),
        "trace quality audit has no AURA rows",
    )
    require(
        any(row["agent"].startswith("TSRA-R") for row in trace_quality_rows),
        "trace quality audit has no TSRA-R rows",
    )
    require(
        all(float(row["reason_coverage"]) == 1.0 for row in trace_quality_rows),
        "trace quality audit has incomplete reason coverage",
    )
    require(
        any(
            row["experiment"] == "E7_ml_aura_ml_tsra_r"
            and row["agent"] == "TSRA-R"
            and row["policy"] == "rule_defense_full"
            and int(float(row["trace_count"])) == 47
            for row in trace_quality_rows
        ),
        "trace quality audit missing E7 TSRA-R rule delegate traces",
    )
    checks.append("decision_trace_quality_audit rows=10 pass")

    quality_gate_rows = read_csv("outputs/report_tables/agent_quality_gate_audit.csv")
    require(
        len(quality_gate_rows) == 6,
        f"expected 6 agent quality gate audit rows, got {len(quality_gate_rows)}",
    )
    failed_quality_gate = [
        f"{row['check_id']}:{row['area']}"
        for row in quality_gate_rows
        if row.get("status") != "pass"
    ]
    require(not failed_quality_gate, f"failed agent quality gate rows: {failed_quality_gate[:8]}")
    required_quality_gate_areas = {
        "unit_regression_execution",
        "unit_regression_scope",
        "final_verifier_integration",
        "hbin_workflow_gate",
        "readme_reproduction_gate",
        "package_inclusion_gate",
    }
    observed_quality_gate_areas = {row["area"] for row in quality_gate_rows}
    require(
        observed_quality_gate_areas == required_quality_gate_areas,
        f"agent quality gate missing areas: {sorted(required_quality_gate_areas - observed_quality_gate_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in quality_gate_rows),
        "agent quality gate audit missing safety boundary",
    )
    checks.append("agent_quality_gate_audit rows=6 pass")

    team_handoff_rows = read_csv("outputs/report_tables/team_handoff_audit.csv")
    require(
        len(team_handoff_rows) == 7,
        f"expected 7 team handoff audit rows, got {len(team_handoff_rows)}",
    )
    failed_team_handoff = [
        f"{row['check_id']}:{row['area']}"
        for row in team_handoff_rows
        if row.get("status") != "pass"
    ]
    require(not failed_team_handoff, f"failed team handoff rows: {failed_team_handoff[:8]}")
    required_team_handoff_areas = {
        "handoff_document_structure",
        "role_lane_contract",
        "branch_policy",
        "minimum_gate_commands",
        "decision_record_contract",
        "package_and_readiness_integration",
        "safety_boundary",
    }
    observed_team_handoff_areas = {row["area"] for row in team_handoff_rows}
    require(
        observed_team_handoff_areas == required_team_handoff_areas,
        f"team handoff audit missing areas: {sorted(required_team_handoff_areas - observed_team_handoff_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in team_handoff_rows),
        "team handoff audit missing safety boundary",
    )
    checks.append("team_handoff_audit rows=7 pass")

    runtime_rows = read_csv("outputs/report_tables/agent_runtime_invariant_audit.csv")
    require(
        len(runtime_rows) == 10,
        f"expected 10 runtime invariant audit rows, got {len(runtime_rows)}",
    )
    failed_runtime_rows = [
        f"{row['experiment']}:{row['agent']}:{row['policy']}"
        for row in runtime_rows
        if row.get("status") != "pass"
    ]
    require(not failed_runtime_rows, f"failed runtime invariant rows: {failed_runtime_rows[:8]}")
    runtime_agents = {row["agent"] for row in runtime_rows}
    require(
        {"AURA", "AURA-ML", "TSRA-R", "TSRA-R-ML"}.issubset(runtime_agents),
        f"runtime invariant audit missing agents: {sorted({'AURA', 'AURA-ML', 'TSRA-R', 'TSRA-R-ML'} - runtime_agents)}",
    )
    require(
        all(row["trace_id_unique"] == "true" for row in runtime_rows),
        "runtime invariant audit has duplicate trace ids",
    )
    require(
        all(row["trace_id_sequence_ok"] == "true" for row in runtime_rows),
        "runtime invariant audit has non-contiguous trace ids",
    )
    require(
        all(row["time_monotonic"] == "true" for row in runtime_rows),
        "runtime invariant audit has non-monotonic time",
    )
    require(
        all(row["observation_count_expected"] == "true" for row in runtime_rows),
        "runtime invariant audit has unexpected observation_count",
    )
    require(
        all(row["decision_count_expected"] == "true" for row in runtime_rows),
        "runtime invariant audit has unexpected decision_count",
    )
    require(
        all(float(row["last_selected_chain_match_rate"]) == 1.0 for row in runtime_rows),
        "runtime invariant audit has broken last-selected chain",
    )
    require(
        all(int(float(row["tool_error_count"])) == 0 for row in runtime_rows),
        "runtime invariant audit contains tool errors",
    )
    require(
        all(int(float(row["selected_event_count"])) > 0 for row in runtime_rows),
        "runtime invariant audit has rows without selected events",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in runtime_rows),
        "runtime invariant audit missing safety boundary",
    )
    require(
        any(
            row["experiment"] == "E7_ml_aura_ml_tsra_r"
            and row["trace_file"] == "tsra_r_rule_delegate_traces.jsonl"
            and row["agent"] == "TSRA-R"
            and row["policy"] == "rule_defense_full"
            and int(float(row["trace_count"])) == 47
            and int(float(row["tool_invocation_count"])) > 0
            and int(float(row["selected_event_count"])) > 0
            for row in runtime_rows
        ),
        "runtime invariant audit missing E7 TSRA-R rule delegate trace file",
    )
    checks.append("agent_runtime_invariant_audit rows=10 pass")

    replay_rows = read_csv("outputs/report_tables/agent_loop_replay.csv")
    require(len(replay_rows) == 10, f"expected 10 agent loop replay rows, got {len(replay_rows)}")
    replay_agents = {row["agent"] for row in replay_rows}
    require(
        {"AURA", "AURA-ML", "TSRA-R", "TSRA-R-ML"}.issubset(replay_agents),
        f"agent loop replay missing agents: {sorted({'AURA', 'AURA-ML', 'TSRA-R', 'TSRA-R-ML'} - replay_agents)}",
    )
    replay_cases = {row["loop_case"] for row in replay_rows}
    require(
        replay_cases == {"no_op", "action"},
        f"agent loop replay missing no_op/action cases: {sorted(replay_cases)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in replay_rows),
        "agent loop replay missing safety boundary",
    )
    require(
        all(row["observe"] and row["memory"] and row["selected_action"] and row["reason"] for row in replay_rows),
        "agent loop replay has incomplete loop summaries",
    )
    require(
        any(
            row["experiment"] == "E7_ml_aura_ml_tsra_r"
            and row["agent"] == "TSRA-R"
            and row["policy"] == "rule_defense_full"
            and row.get("trace_file") == "tsra_r_rule_delegate_traces.jsonl"
            and row["loop_case"] == "no_op"
            for row in replay_rows
        ),
        "agent loop replay missing E7 rule delegate no-op representative",
    )
    require(
        any(
            row["experiment"] == "E7_ml_aura_ml_tsra_r"
            and row["agent"] == "TSRA-R"
            and row["policy"] == "rule_defense_full"
            and row.get("trace_file") == "tsra_r_rule_delegate_traces.jsonl"
            and row["loop_case"] == "action"
            for row in replay_rows
        ),
        "agent loop replay missing E7 rule delegate action representative",
    )
    checks.append("agent_loop_replay rows=10 agents/cases/sidecar=complete")

    causality_rows = read_csv("outputs/report_tables/agent_decision_causality_audit.csv")
    require(
        len(causality_rows) == 446,
        f"expected 446 decision causality rows, got {len(causality_rows)}",
    )
    failed_causality = [
        f"{row['experiment']}:{row['trace_id']}:{row['agent']}"
        for row in causality_rows
        if row.get("causal_status") != "pass"
    ]
    require(not failed_causality, f"failed decision causality rows: {failed_causality[:8]}")
    require(
        {"AURA", "AURA-ML", "TSRA-R", "TSRA-R-ML"}.issubset({row["agent"] for row in causality_rows}),
        "decision causality audit missing attack/defense agent variants",
    )
    require(
        {"no_op", "attack_event", "defense_events"}.issubset({row["selected_type"] for row in causality_rows}),
        "decision causality audit missing selected action types",
    )
    require(
        all(row["candidate_support"] == "pass" for row in causality_rows),
        "decision causality audit has candidate support failures",
    )
    require(
        all(row["tool_support"] == "pass" for row in causality_rows),
        "decision causality audit has tool support failures",
    )
    require(
        all(row["score_or_threshold_support"] == "pass" for row in causality_rows),
        "decision causality audit has score/threshold support failures",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in causality_rows),
        "decision causality audit missing safety boundary",
    )
    e7_delegate_causality = [
        row
        for row in causality_rows
        if row["experiment"] == "E7_ml_aura_ml_tsra_r"
        and row["agent"] == "TSRA-R"
        and row["policy"] == "rule_defense_full"
    ]
    require(
        len(e7_delegate_causality) == 47,
        f"decision causality audit expected 47 E7 delegate rows, got {len(e7_delegate_causality)}",
    )
    require(
        all(
            row["candidate_support"] == "pass"
            and row["tool_support"] == "pass"
            and row["score_or_threshold_support"] == "pass"
            for row in e7_delegate_causality
        ),
        "decision causality audit has E7 delegate support failures",
    )
    checks.append("agent_decision_causality_audit rows=446 pass")

    margin_rows = read_csv("outputs/report_tables/agent_decision_margin_audit.csv")
    require(
        len(margin_rows) == 446,
        f"expected 446 decision margin rows, got {len(margin_rows)}",
    )
    failed_margin = [
        f"{row['experiment']}:{row['trace_id']}:{row['agent']}"
        for row in margin_rows
        if row.get("margin_status") != "pass"
    ]
    require(not failed_margin, f"failed decision margin rows: {failed_margin[:8]}")
    require(
        {"AURA", "AURA-ML", "TSRA-R", "TSRA-R-ML"}.issubset({row["agent"] for row in margin_rows}),
        "decision margin audit missing attack/defense agent variants",
    )
    require(
        {"no_op", "attack_event", "defense_events"}.issubset({row["selected_type"] for row in margin_rows}),
        "decision margin audit missing selected action types",
    )
    require(
        any(row["selection_margin"] not in ("", None) for row in margin_rows),
        "decision margin audit has no selection margin evidence",
    )
    require(
        any(row["threshold_margin"] not in ("", None) for row in margin_rows),
        "decision margin audit has no threshold margin evidence",
    )
    require(
        any(row["no_op_basis"] not in ("", None) for row in margin_rows),
        "decision margin audit has no no-op basis evidence",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in margin_rows),
        "decision margin audit missing safety boundary",
    )
    e7_delegate_margins = [
        row
        for row in margin_rows
        if row["experiment"] == "E7_ml_aura_ml_tsra_r"
        and row["agent"] == "TSRA-R"
        and row["policy"] == "rule_defense_full"
    ]
    require(
        len(e7_delegate_margins) == 47,
        f"decision margin audit expected 47 E7 delegate rows, got {len(e7_delegate_margins)}",
    )
    require(
        all(row["margin_status"] == "pass" for row in e7_delegate_margins),
        "decision margin audit has E7 delegate failures",
    )
    checks.append("agent_decision_margin_audit rows=446 pass")

    goal_rows = read_csv("outputs/report_tables/agent_goal_alignment_audit.csv")
    require(
        len(goal_rows) == 446,
        f"expected 446 goal alignment rows, got {len(goal_rows)}",
    )
    failed_goal_rows = [
        f"{row['experiment']}:{row['trace_id']}:{row['agent']}"
        for row in goal_rows
        if row.get("goal_alignment_status") != "pass"
    ]
    require(not failed_goal_rows, f"failed goal alignment rows: {failed_goal_rows[:8]}")
    require(
        {"AURA", "AURA-ML", "TSRA-R", "TSRA-R-ML"}.issubset({row["agent"] for row in goal_rows}),
        "goal alignment audit missing attack/defense agent variants",
    )
    require(
        {"no_op", "attack_event", "defense_events"}.issubset({row["selected_type"] for row in goal_rows}),
        "goal alignment audit missing selected action types",
    )
    require(
        any("predicted_mission_impact=" in row["goal_signal"] for row in goal_rows),
        "goal alignment audit missing AURA mission-impact signal",
    )
    require(
        any("probability=" in row["goal_signal"] and "threshold=" in row["goal_signal"] for row in goal_rows),
        "goal alignment audit missing TSRA-R-ML probability/threshold signal",
    )
    require(
        any("critical_pending=" in row["goal_signal"] for row in goal_rows),
        "goal alignment audit missing TSRA-R observation-risk signal",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in goal_rows),
        "goal alignment audit missing safety boundary",
    )
    e7_delegate_goals = [
        row
        for row in goal_rows
        if row["experiment"] == "E7_ml_aura_ml_tsra_r"
        and row["agent"] == "TSRA-R"
        and row["policy"] == "rule_defense_full"
    ]
    require(
        len(e7_delegate_goals) == 47,
        f"goal alignment audit expected 47 E7 delegate rows, got {len(e7_delegate_goals)}",
    )
    require(
        all(row["goal_alignment_status"] == "pass" for row in e7_delegate_goals),
        "goal alignment audit has E7 delegate failures",
    )
    checks.append("agent_goal_alignment_audit rows=446 pass")

    feedback_rows = read_csv("outputs/report_tables/agent_decision_feedback_audit.csv")
    require(
        len(feedback_rows) >= 60,
        f"expected at least 60 decision feedback rows, got {len(feedback_rows)}",
    )
    failed_feedback_rows = [
        f"{row['experiment']}:{row['selected_event_id']}:{row['action']}"
        for row in feedback_rows
        if row.get("feedback_status") != "pass"
    ]
    require(not failed_feedback_rows, f"failed decision feedback rows: {failed_feedback_rows[:8]}")
    feedback_experiments = {row["experiment"] for row in feedback_rows}
    require(
        feedback_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"decision feedback audit has unexpected experiments: {sorted(feedback_experiments)}",
    )
    feedback_types = {row["selected_event_type"] for row in feedback_rows}
    require(
        feedback_types == {"attack_event", "defense_event"},
        f"decision feedback audit missing attack/defense event types: {sorted(feedback_types)}",
    )
    require(
        sum(1 for row in feedback_rows if row["selected_event_type"] == "attack_event") == 10,
        "decision feedback audit must include 10 selected attack events",
    )
    require(
        sum(1 for row in feedback_rows if row["selected_event_type"] == "defense_event") >= 50,
        "decision feedback audit must include at least 50 selected defense events",
    )
    required_feedback_classes = {
        "attack_contained_by_defense",
        "attack_pressure_observed",
        "defense_bounded_or_lagged",
        "defense_held",
        "defense_improved",
        "ml_window_triggered",
    }
    observed_feedback_classes = {row["feedback_class"] for row in feedback_rows}
    require(
        required_feedback_classes.issubset(observed_feedback_classes),
        f"decision feedback audit missing feedback classes: {sorted(required_feedback_classes - observed_feedback_classes)}",
    )
    require(
        all(row["event_link_status"] == "linked" for row in feedback_rows),
        "decision feedback audit has unlinked selected events",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in feedback_rows),
        "decision feedback audit missing safety boundary",
    )
    checks.append(f"agent_decision_feedback_audit rows={len(feedback_rows)} pass")

    memory_rows = read_csv("outputs/report_tables/agent_memory_belief_audit.csv")
    require(
        len(memory_rows) == 9,
        f"expected 9 agent memory audit rows, got {len(memory_rows)}",
    )
    failed_memory_rows = [
        f"{row['experiment']}:{row['agent']}:{row['policy']}"
        for row in memory_rows
        if row.get("status") != "pass"
    ]
    require(not failed_memory_rows, f"failed agent memory audit rows: {failed_memory_rows[:8]}")
    memory_agents = {row["agent"] for row in memory_rows}
    require(
        {"AURA", "AURA-ML", "TSRA-R", "TSRA-R-ML"}.issubset(memory_agents),
        f"agent memory audit missing agents: {sorted({'AURA', 'AURA-ML', 'TSRA-R', 'TSRA-R-ML'} - memory_agents)}",
    )
    require(
        all(float(row["memory_coverage"]) == 1.0 for row in memory_rows),
        "agent memory audit has incomplete memory coverage",
    )
    require(
        all(row["observation_count_nondecreasing"] == "true" for row in memory_rows),
        "agent memory audit has non-monotonic observation_count",
    )
    require(
        all(row["decision_count_nondecreasing"] == "true" for row in memory_rows),
        "agent memory audit has non-monotonic decision_count",
    )
    require(
        all(float(row["last_selected_chain_match_rate"]) == 1.0 for row in memory_rows),
        "agent memory audit has broken last-selected chain",
    )
    require(
        all(row["changing_belief_keys"] != "none" for row in memory_rows),
        "agent memory audit has static belief state",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in memory_rows),
        "agent memory audit missing safety boundary",
    )
    checks.append("agent_memory_belief_audit rows=9 pass")

    memory_influence_rows = read_csv("outputs/report_tables/agent_memory_influence_audit.csv")
    require(
        len(memory_influence_rows) == 6,
        f"expected 6 agent memory influence rows, got {len(memory_influence_rows)}",
    )
    failed_memory_influence = [
        f"{row['check_id']}:{row['area']}"
        for row in memory_influence_rows
        if row.get("influence_status") != "pass"
    ]
    require(
        not failed_memory_influence,
        f"failed agent memory influence rows: {failed_memory_influence[:8]}",
    )
    required_memory_influence_areas = {
        "AURA cadence memory",
        "AURA-ML cadence memory",
        "TSRA-R action cooldown memory",
        "TSRA-R-ML active defense window memory",
        "Adaptive TSRA-R memory policy",
        "Memory chain integrity",
    }
    observed_memory_influence_areas = {row["area"] for row in memory_influence_rows}
    require(
        observed_memory_influence_areas == required_memory_influence_areas,
        f"agent memory influence audit has unexpected areas: {sorted(observed_memory_influence_areas)}",
    )
    require(
        any(
            "cooldown_noops=48" in row["observed"]
            and "max_event_noops=12" in row["observed"]
            for row in memory_influence_rows
            if row["check_id"] == "MI01"
        ),
        "memory influence audit missing AURA cadence evidence",
    )
    require(
        any(
            "eligible_not_ready=" in row["observed"]
            and "emitted_events=" in row["observed"]
            for row in memory_influence_rows
            if row["check_id"] == "MI03"
        ),
        "memory influence audit missing TSRA-R cooldown evidence",
    )
    require(
        any(
            observed_int(row, "opened_windows") >= 35
            and observed_int(row, "active_window_noops") >= 20
            for row in memory_influence_rows
            if row["check_id"] == "MI04"
        ),
        "memory influence audit missing ML active-window evidence",
    )
    require(
        any(
            float(observed_value(row, "delta_mission_impact_mean")) < 0.0
            and float(observed_value(row, "delta_defense_count_mean")) < 0.0
            for row in memory_influence_rows
            if row["check_id"] == "MI05"
        ),
        "memory influence audit missing adaptive memory effect evidence",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in memory_influence_rows),
        "agent memory influence audit missing safety boundary",
    )
    checks.append("agent_memory_influence_audit rows=6 pass")

    aura_attack_path_rows = read_csv("outputs/report_tables/aura_attack_decision_path_audit.csv")
    require(
        len(aura_attack_path_rows) == 6,
        f"expected 6 AURA attack decision path rows, got {len(aura_attack_path_rows)}",
    )
    failed_aura_attack_path_rows = [
        f"{row['check_id']}:{row['area']}"
        for row in aura_attack_path_rows
        if row.get("status") != "pass"
    ]
    require(
        not failed_aura_attack_path_rows,
        f"failed AURA attack decision path rows: {failed_aura_attack_path_rows[:8]}",
    )
    required_aura_attack_path_areas = {
        "Candidate score contract",
        "Candidate scoring toolchain",
        "Top-score selection and event link",
        "No-op and cadence gate discipline",
        "AttackEvent payload consistency",
        "Tactical and defense-context coverage",
    }
    observed_aura_attack_path_areas = {row["area"] for row in aura_attack_path_rows}
    require(
        observed_aura_attack_path_areas == required_aura_attack_path_areas,
        f"AURA attack path audit has unexpected areas: {sorted(observed_aura_attack_path_areas)}",
    )
    require(
        any(
            observed_int(row, "candidate_total") >= 120
            and observed_int(row, "rule_candidates") > 0
            and observed_int(row, "ml_candidates") > 0
            and observed_int(row, "base_formula_matches") == observed_int(row, "candidate_total")
            and observed_int(row, "selection_formula_matches") == observed_int(row, "candidate_total")
            for row in aura_attack_path_rows
            if row["check_id"] == "AAP01"
        ),
        "AURA attack path audit missing candidate score formula evidence",
    )
    require(
        any(
            observed_int(row, "candidate_traces") == 25
            and observed_int(row, "generated_candidate_total")
            == observed_int(row, "candidate_total")
            and observed_int(row, "generated_candidate_payload_matches") == 25
            and observed_int(row, "generated_candidate_payload_mismatches") == 0
            and observed_int(row, "estimate_candidate_effect") == observed_int(row, "candidate_total")
            and observed_int(row, "estimate_detectability") == observed_int(row, "candidate_total")
            and observed_int(row, "predict_candidate_impact") == 51
            and observed_int(row, "tool_errors") == 0
            and observed_int(row, "all_trace_tool_errors") == 0
            for row in aura_attack_path_rows
            if row["check_id"] == "AAP02"
        ),
        "AURA attack path audit missing toolchain evidence",
    )
    require(
        any(
            observed_int(row, "attack_trace_count") == 25
            and observed_int(row, "attack_event_count") == 25
            and observed_int(row, "selected_matches_top_candidate") == 25
            and observed_int(row, "linked_attack_events") == 25
            and observed_int(row, "score_event_matches") == 25
            and observed_int(row, "event_agent_matches_trace") == 25
            and observed_int(row, "threshold_passes") == 25
            for row in aura_attack_path_rows
            if row["check_id"] == "AAP03"
        ),
        "AURA attack path audit missing selected-event linkage evidence",
    )
    require(
        any(
            observed_int(row, "pre_start_attack_events") == 0
            and float(observed_value(row, "min_attack_gap_sec")) >= 45.0
            and observed_int(row, "cooldown_gap_violations") == 0
            and observed_int(row, "event_budget_violations") == 0
            and observed_int(row, "no_op_threshold_violations") == 0
            for row in aura_attack_path_rows
            if row["check_id"] == "AAP04"
        ),
        "AURA attack path audit missing no-op/cadence gate evidence",
    )
    require(
        any(
            observed_int(row, "event_payloads") == 25
            and observed_int(row, "impact_field_matches") == 25
            and observed_int(row, "event_score_formula_matches") == 25
            and observed_int(row, "allowed_agent_events") == 25
            and observed_int(row, "rule_agent_events") == 15
            and observed_int(row, "ml_agent_events") == 10
            for row in aura_attack_path_rows
            if row["check_id"] == "AAP05"
        ),
        "AURA attack path audit missing AttackEvent payload or agent identity evidence",
    )
    require(
        any(
            "failover_chasing" in row["observed"]
            and "queue_pressure" in row["observed"]
            and "stale_cop_induction" in row["observed"]
            and "target_links=LTE,MESH,SATCOM" in row["observed"]
            and observed_int(row, "defense_context_candidates") >= 120
            and observed_int(row, "selected_with_defense_context") > 0
            and observed_int(row, "objective_bonus_candidates") > 0
            and observed_int(row, "counter_defense_bonus_candidates") > 0
            and observed_int(row, "summarize_defense_context") == 155
            for row in aura_attack_path_rows
            if row["check_id"] == "AAP06"
        ),
        "AURA attack path audit missing tactic/context coverage evidence",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in aura_attack_path_rows),
        "AURA attack path audit missing safety boundary",
    )
    checks.append("aura_attack_decision_path_audit rows=6 pass")

    adaptive_path_rows = read_csv("outputs/report_tables/adaptive_defense_decision_path_audit.csv")
    require(
        len(adaptive_path_rows) == 6,
        f"expected 6 adaptive defense decision path rows, got {len(adaptive_path_rows)}",
    )
    failed_adaptive_path_rows = [
        f"{row['check_id']}:{row['area']}"
        for row in adaptive_path_rows
        if row.get("status") != "pass"
    ]
    require(
        not failed_adaptive_path_rows,
        f"failed adaptive defense decision path rows: {failed_adaptive_path_rows[:8]}",
    )
    required_adaptive_path_areas = {
        "Batch-level adaptive effect",
        "Adaptive policy tool path",
        "Core defense preservation",
        "Video throttle memory gate",
        "PACE switch memory gate",
        "Gate-to-event consistency",
    }
    observed_adaptive_path_areas = {row["area"] for row in adaptive_path_rows}
    require(
        observed_adaptive_path_areas == required_adaptive_path_areas,
        f"adaptive defense path audit has unexpected areas: {sorted(observed_adaptive_path_areas)}",
    )
    require(
        any(
            float(observed_value(row, "mission_improvement")) >= 0.02
            and float(observed_value(row, "defense_count_reduction")) >= 2.0
            and float(observed_value(row, "video_throttle_reduction")) >= 2.0
            for row in adaptive_path_rows
            if row["check_id"] == "ADP01"
        ),
        "adaptive defense path audit missing batch-level effect evidence",
    )
    require(
        any(
            observed_int(row, "trace_files") >= 30
            and observed_int(row, "trace_count") >= 1830
            and observed_int(row, "update_adaptive_action_policy") == observed_int(row, "trace_count")
            and observed_int(row, "candidate_total") == observed_int(row, "trace_count") * 4
            and observed_int(row, "tool_errors") == 0
            for row in adaptive_path_rows
            if row["check_id"] == "ADP02"
        ),
        "adaptive defense path audit missing tool-path evidence",
    )
    require(
        any(
            observed_int(row, "video_held") > observed_int(row, "video_enabled")
            and observed_int(row, "video_eligible_held") > 0
            and observed_int(row, "video_gate_reasons") == observed_int(row, "video_candidates")
            for row in adaptive_path_rows
            if row["check_id"] == "ADP04"
        ),
        "adaptive defense path audit missing video gate evidence",
    )
    require(
        any(
            observed_int(row, "pace_held") > observed_int(row, "pace_enabled")
            and observed_int(row, "pace_eligible_held") > 0
            and observed_int(row, "pace_gate_reasons") == observed_int(row, "pace_candidates")
            for row in adaptive_path_rows
            if row["check_id"] == "ADP05"
        ),
        "adaptive defense path audit missing PACE gate evidence",
    )
    require(
        any(
            observed_int(row, "emission_gate_violations") == 0
            and observed_int(row, "memory_evidence_candidates") >= 7000
            and observed_int(row, "selected_optional_events") > 0
            for row in adaptive_path_rows
            if row["check_id"] == "ADP06"
        ),
        "adaptive defense path audit missing gate-to-event consistency evidence",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in adaptive_path_rows),
        "adaptive defense path audit missing safety boundary",
    )
    checks.append("adaptive_defense_decision_path_audit rows=6 pass")

    cross_agent_rows = read_csv("outputs/report_tables/cross_agent_context_audit.csv")
    require(
        len(cross_agent_rows) == 8,
        f"expected 8 cross-agent context audit rows, got {len(cross_agent_rows)}",
    )
    failed_cross_agent_rows = [
        f"{row['check_id']}:{row['area']}"
        for row in cross_agent_rows
        if row.get("status") != "pass"
    ]
    require(
        not failed_cross_agent_rows,
        f"failed cross-agent context audit rows: {failed_cross_agent_rows[:8]}",
    )
    require(
        {row["area"] for row in cross_agent_rows}
        == {
            "Shared observation context",
            "TSRA-R attack-context tool path",
            "Attack-to-defense handoff",
            "AURA defense-context tool path",
            "Defense-to-attack handoff",
            "Event-level context consistency",
            "Context-to-policy score effect",
            "Attack-context defense priority effect",
        },
        "cross-agent context audit has unexpected areas",
    )
    require(
        any(
            observed_int(row, "aura_observation_context") >= 60
            and observed_int(row, "tsra_observation_context") >= 120
            for row in cross_agent_rows
            if row["check_id"] == "XAG01"
        ),
        "cross-agent audit missing shared observation context evidence",
    )
    require(
        any(
            observed_int(row, "summarize_attack_context") == observed_int(row, "tsra_traces")
            and observed_int(row, "feedback_attack_context") == observed_int(row, "tsra_traces")
            and observed_int(row, "candidate_attack_context_used") > 0
            and observed_int(row, "tool_errors") == 0
            for row in cross_agent_rows
            if row["check_id"] == "XAG02"
        ),
        "cross-agent audit missing TSRA-R attack-context tool evidence",
    )
    require(
        any(
            observed_int(row, "attack_handoffs") >= 10
            for row in cross_agent_rows
            if row["check_id"] == "XAG03"
        ),
        "cross-agent audit missing attack-to-defense handoff evidence",
    )
    require(
        any(
            observed_int(row, "summarize_defense_context") == observed_int(row, "aura_traces")
            and observed_int(row, "feedback_defense_context") == observed_int(row, "aura_traces")
            and observed_int(row, "candidate_defense_context_used") > 0
            and observed_int(row, "selected_attack_with_defense_context") > 0
            for row in cross_agent_rows
            if row["check_id"] == "XAG04"
        ),
        "cross-agent audit missing AURA defense-context tool evidence",
    )
    require(
        any(
            observed_int(row, "experiments_with_post_defense_context") >= 2
            and observed_int(row, "defense_context_seen_traces") > 0
            for row in cross_agent_rows
            if row["check_id"] == "XAG05"
        ),
        "cross-agent audit missing defense-to-attack handoff evidence",
    )
    require(
        any(
            observed_int(row, "related_context_events") == observed_int(row, "defense_events")
            and observed_int(row, "active_related_events") > 0
            and observed_int(row, "missing_related_context") == 0
            for row in cross_agent_rows
            if row["check_id"] == "XAG06"
        ),
        "cross-agent audit missing event-level context evidence",
    )
    require(
        any(
            observed_int(row, "counter_defense_bonus_candidates") > 0
            and observed_int(row, "selected_counter_defense_bonus_traces") > 0
            and "counter_" in row["observed"]
            for row in cross_agent_rows
            if row["check_id"] == "XAG07"
        ),
        "cross-agent audit missing context-to-policy score evidence",
    )
    require(
        any(
            observed_int(row, "attack_context_bonus_candidates") > 0
            and observed_int(row, "attack_context_bonus_events") > 0
            and observed_int(row, "selected_defense_bonus_traces") > 0
            and "ordered_core_defense_traces=" in row["observed"]
            and "counter_" in row["observed"]
            for row in cross_agent_rows
            if row["check_id"] == "XAG08"
        ),
        "cross-agent audit missing attack-context defense priority evidence",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in cross_agent_rows),
        "cross-agent context audit missing safety boundary",
    )
    checks.append("cross_agent_context_audit rows=8 pass")

    defense_priority_rows = read_csv("outputs/report_tables/defense_priority_decision_path_audit.csv")
    require(
        len(defense_priority_rows) == 6,
        f"expected 6 defense priority decision path rows, got {len(defense_priority_rows)}",
    )
    failed_defense_priority_rows = [
        f"{row['check_id']}:{row['area']}"
        for row in defense_priority_rows
        if row.get("status") != "pass"
    ]
    require(
        not failed_defense_priority_rows,
        f"failed defense priority decision path rows: {failed_defense_priority_rows[:8]}",
    )
    required_defense_priority_areas = {
        "Candidate priority score contract",
        "Bounded priority score inputs",
        "Attack-context priority bonus",
        "Selected event score consistency",
        "Core defense event ordering",
        "No-op and ready-action consistency",
    }
    observed_defense_priority_areas = {row["area"] for row in defense_priority_rows}
    require(
        observed_defense_priority_areas == required_defense_priority_areas,
        f"defense priority path audit has unexpected areas: {sorted(observed_defense_priority_areas)}",
    )
    require(
        any(
            observed_int(row, "scored_candidates") >= 600
            and observed_int(row, "formula_matches") == observed_int(row, "scored_candidates")
            and observed_int(row, "reason_count") == observed_int(row, "scored_candidates")
            for row in defense_priority_rows
            if row["check_id"] == "DPR01"
        ),
        "defense priority path audit missing formula contract evidence",
    )
    require(
        any(
            observed_int(row, "negative_scores") == 0
            and observed_int(row, "over_bound_scores") == 0
            and observed_int(row, "non_eligible_bonus") == 0
            and float(observed_value(row, "max_attack_context_bonus")) <= 0.12
            for row in defense_priority_rows
            if row["check_id"] == "DPR02"
        ),
        "defense priority path audit missing bounded-score evidence",
    )
    require(
        any(
            observed_int(row, "attack_context_bonus_candidates") > 0
            and observed_int(row, "attack_context_bonus_events") > 0
            and "counter_" in row["observed"]
            for row in defense_priority_rows
            if row["check_id"] == "DPR03"
        ),
        "defense priority path audit missing attack-context bonus evidence",
    )
    require(
        any(
            observed_int(row, "checked_event_matches") > 0
            and observed_int(row, "event_match_failures") == 0
            and observed_int(row, "no_candidate_for_event") == 0
            for row in defense_priority_rows
            if row["check_id"] == "DPR04"
        ),
        "defense priority path audit missing selected-event consistency evidence",
    )
    require(
        any(
            "ordered_core_defense_traces=12/12" in row["observed"]
            for row in defense_priority_rows
            if row["check_id"] == "DPR05"
        ),
        "defense priority path audit missing core event ordering evidence",
    )
    require(
        any(
            observed_int(row, "no_op_ready_violations") == 0
            and observed_int(row, "unselected_ready_actions") == 0
            and observed_int(row, "selected_without_ready") == 0
            and observed_int(row, "missing_condition_tool_traces") == 0
            and observed_int(row, "condition_candidate_checks") == observed_int(row, "condition_candidate_matches")
            and observed_int(row, "condition_candidate_mismatches") == 0
            and observed_int(row, "pace_reason_matches") > 0
            and observed_int(row, "pace_reason_mismatches") == 0
            for row in defense_priority_rows
            if row["check_id"] == "DPR06"
        ),
        "defense priority path audit missing no-op/ready consistency evidence",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in defense_priority_rows),
        "defense priority path audit missing safety boundary",
    )
    checks.append("defense_priority_decision_path_audit rows=6 pass")

    tool_rows = read_csv("outputs/report_tables/agent_tool_usage_audit.csv")
    require(len(tool_rows) == 37, f"expected 37 agent tool audit rows, got {len(tool_rows)}")
    failed_tool_rows = [
        f"{row['experiment']}:{row['agent']}:{row['tool_name']}"
        for row in tool_rows
        if row.get("status") != "pass"
    ]
    require(not failed_tool_rows, f"failed agent tool audit rows: {failed_tool_rows[:8]}")
    expected_tools = {
        "estimate_candidate_effect",
        "estimate_detectability",
        "execute_rule_defense_actions",
        "evaluate_defense_conditions",
        "generate_attack_candidates",
        "assess_mission_risk_guard",
        "predict_attack_probability",
        "predict_candidate_impact",
        "select_fallback_link",
        "summarize_attack_context",
        "summarize_defense_context",
    }
    observed_tools = {row["tool_name"] for row in tool_rows}
    require(
        expected_tools.issubset(observed_tools),
        f"agent tool audit missing tools: {sorted(expected_tools - observed_tools)}",
    )
    require(
        {"AURA", "AURA-ML", "TSRA-R", "TSRA-R-ML"}.issubset({row["agent"] for row in tool_rows}),
        "agent tool audit missing attack/defense agent variants",
    )
    require(
        all(int(float(row["invocation_count"])) > 0 for row in tool_rows),
        "agent tool audit has zero invocation row",
    )
    require(
        all(int(float(row["error_count"])) == 0 for row in tool_rows),
        "agent tool audit contains tool errors",
    )
    require(
        all(float(row["input_summary_coverage"]) == 1.0 for row in tool_rows),
        "agent tool audit has incomplete input summaries",
    )
    require(
        all(float(row["output_summary_coverage"]) == 1.0 for row in tool_rows),
        "agent tool audit has incomplete output summaries",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in tool_rows),
        "agent tool audit missing safety boundary",
    )
    e7_delegate_tools = {
        row["tool_name"]
        for row in tool_rows
        if row["experiment"] == "E7_ml_aura_ml_tsra_r"
        and row["agent"] == "TSRA-R"
        and row["policy"] == "rule_defense_full"
    }
    expected_delegate_tools = {
        "evaluate_defense_conditions",
        "select_fallback_link",
        "summarize_attack_context",
    }
    require(
        expected_delegate_tools.issubset(e7_delegate_tools),
        f"agent tool audit missing E7 delegate tools: {sorted(expected_delegate_tools - e7_delegate_tools)}",
    )
    checks.append("agent_tool_usage_audit rows=37 pass")

    interface_rows = read_csv("outputs/report_tables/agent_interface_manifest.csv")
    require(len(interface_rows) == 4, f"expected 4 agent interface rows, got {len(interface_rows)}")
    interface_agents = {row["agent"] for row in interface_rows}
    require(
        interface_agents == {"AURA", "AURA-ML", "TSRA-R", "TSRA-R-ML"},
        f"unexpected agent interface agents: {sorted(interface_agents)}",
    )
    sides = {row["agent"]: row["side"] for row in interface_rows}
    require(sides["AURA"] == "attack" and sides["AURA-ML"] == "attack", "AURA agents must be attack side")
    require(sides["TSRA-R"] == "defense" and sides["TSRA-R-ML"] == "defense", "TSRA-R agents must be defense side")
    require(
        all(row["tool_contract"] and row["tool_contract"] != "none" for row in interface_rows),
        "agent interface manifest missing tool contracts",
    )
    require(
        all(int(float(row["non_noop_count"])) > 0 for row in interface_rows),
        "agent interface manifest has agent without non-no-op decision",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in interface_rows),
        "agent interface manifest missing safety boundary",
    )
    tsra_interface_row = next(row for row in interface_rows if row["agent"] == "TSRA-R")
    require(
        "E7_ml_aura_ml_tsra_r" in tsra_interface_row["evidence_experiments"],
        "agent interface manifest TSRA-R row missing E7 rule delegate evidence",
    )
    require(
        int(float(tsra_interface_row["trace_count"])) == 108,
        f"expected TSRA-R interface trace_count 108, got {tsra_interface_row['trace_count']}",
    )
    require(
        int(float(tsra_interface_row["non_noop_count"])) == 35,
        f"expected TSRA-R interface non_noop_count 35, got {tsra_interface_row['non_noop_count']}",
    )
    checks.append("agent_interface_manifest rows=4 agents=attack/defense sidecar=present")

    capability_rows = read_csv("outputs/report_tables/agent_capability_matrix.csv")
    require(len(capability_rows) == 10, f"expected 10 capability rows, got {len(capability_rows)}")
    capability_sides = {row["side"] for row in capability_rows}
    require(capability_sides == {"attack", "defense"}, f"unexpected capability sides: {sorted(capability_sides)}")
    capabilities = {row["capability"] for row in capability_rows}
    required_capabilities = {
        "queue_pressure",
        "priority_reroute",
        "stale_badge",
        "ml_attack_alert",
        "adaptive_optional_action_gating",
    }
    require(
        required_capabilities.issubset(capabilities),
        f"capability matrix missing required capabilities: {sorted(required_capabilities - capabilities)}",
    )
    require(
        all(row["validation_gate"] for row in capability_rows),
        "capability matrix has rows without validation gates",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in capability_rows),
        "capability matrix missing safety boundary",
    )
    checks.append("agent_capability_matrix rows=10 attack/defense")

    coverage_rows = read_csv("outputs/report_tables/attack_defense_coverage.csv")
    require(len(coverage_rows) == 4, f"expected 4 attack-defense coverage rows, got {len(coverage_rows)}")
    coverage_attacks = {row["attack_capability"] for row in coverage_rows}
    required_coverage_attacks = {
        "bandwidth_limit",
        "failover_chasing",
        "queue_pressure",
        "stale_cop_induction",
    }
    require(
        coverage_attacks == required_coverage_attacks,
        f"unexpected attack-defense coverage attacks: {sorted(coverage_attacks)}",
    )
    require(
        all(row["coverage_status"] == "covered" for row in coverage_rows),
        "attack-defense coverage has incomplete rows",
    )
    require(
        all(row["covered_by_defense_capabilities"] for row in coverage_rows),
        "attack-defense coverage missing defense capability mappings",
    )
    require(
        all(
            ":pass" in row["validation_gates"] and ":missing" not in row["validation_gates"]
            for row in coverage_rows
        ),
        "attack-defense coverage missing passing validation gates",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in coverage_rows),
        "attack-defense coverage missing safety boundary",
    )
    checks.append("attack_defense_coverage rows=4 covered")

    response_audit_rows = read_csv("outputs/report_tables/attack_defense_response_audit.csv")
    require(
        len(response_audit_rows) == 10,
        f"expected 10 attack-defense response audit rows, got {len(response_audit_rows)}",
    )
    response_experiments = {row["experiment"] for row in response_audit_rows}
    require(
        response_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected response audit experiments: {sorted(response_experiments)}",
    )
    missed_required = [
        row["attack_event_id"]
        for row in response_audit_rows
        if row.get("response_status") == "missed_required"
        or row.get("missing_required_defenses") not in {"", "none"}
    ]
    require(not missed_required, f"attack-defense response audit missed required responses: {missed_required[:8]}")
    require(
        all(
            row["response_status"] in {"complete", "required_covered_support_partial"}
            for row in response_audit_rows
        ),
        "attack-defense response audit has unexpected response status",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in response_audit_rows),
        "attack-defense response audit missing safety boundary",
    )
    checks.append("attack_defense_response_audit rows=10 no missed required")

    pace_rows = read_csv("outputs/report_tables/pace_transition_audit.csv")
    require(len(pace_rows) == 4, f"expected 4 PACE transition audit rows, got {len(pace_rows)}")
    pace_experiments = {row["experiment"] for row in pace_rows}
    require(
        pace_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected PACE audit experiments: {sorted(pace_experiments)}",
    )
    pace_status_counts = {
        status: sum(1 for row in pace_rows if row.get("audit_status") == status)
        for status in {"satcom_to_fallback", "fallback_reselect"}
    }
    require(
        pace_status_counts == {"satcom_to_fallback": 2, "fallback_reselect": 2},
        f"unexpected PACE audit status counts: {pace_status_counts}",
    )
    require(
        all(row["target_link"] != row["from_link_inferred"] for row in pace_rows),
        "PACE audit contains self transition",
    )
    require(
        all(row["move_critical"] == "true" for row in pace_rows),
        "PACE audit contains transition without critical traffic movement",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in pace_rows),
        "PACE transition audit missing safety boundary",
    )
    checks.append("pace_transition_audit rows=4 status=2 initial/2 fallback")

    decomposition_rows = read_csv("outputs/report_tables/mission_impact_decomposition.csv")
    require(
        len(decomposition_rows) == 35,
        f"expected 35 mission impact decomposition rows, got {len(decomposition_rows)}",
    )
    decomposition_experiments = {row["experiment"] for row in decomposition_rows}
    require(
        decomposition_experiments
        == {
            "E1_baseline",
            "E2_fixed_attack",
            "E3_rule_aura",
            "E4_rule_aura_basic_defense",
            "E5_rule_aura_tsra_r",
            "E6_ml_aura_tsra_r",
            "E7_ml_aura_ml_tsra_r",
        },
        f"unexpected decomposition experiments: {sorted(decomposition_experiments)}",
    )
    decomposition_components = {row["component"] for row in decomposition_rows}
    require(
        decomposition_components
        == {
            "critical_latency",
            "trusted_stale_exposure",
            "priority_inversion",
            "kill_chain_delay",
            "recovery_instability",
        },
        f"unexpected decomposition components: {sorted(decomposition_components)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in decomposition_rows),
        "mission impact decomposition missing safety boundary",
    )
    require(
        any(
            row["experiment"] == "E5_rule_aura_tsra_r"
            and row["component"] == "recovery_instability"
            and float(row["weighted_contribution"]) > 0.0
            for row in decomposition_rows
        ),
        "mission impact decomposition missing E5 recovery contribution",
    )
    checks.append("mission_impact_decomposition rows=35 components=5")

    metric_gate_rows = read_csv("outputs/report_tables/metric_gate_summary.csv")
    require(len(metric_gate_rows) == 12, f"expected 12 metric gate rows, got {len(metric_gate_rows)}")
    failed_metric_gates = [
        f"{row['gate_id']}:{row['area']}"
        for row in metric_gate_rows
        if row.get("status") != "pass"
    ]
    require(not failed_metric_gates, f"failed metric gates: {failed_metric_gates[:8]}")
    required_metric_gate_areas = {
        "AURA attack effectiveness",
        "TSRA-R resilience",
        "Priority reroute ablation",
        "Adaptive memory improvement",
        "ML defender separation",
        "PACE reselection discipline",
    }
    observed_metric_gate_areas = {row["area"] for row in metric_gate_rows}
    require(
        required_metric_gate_areas.issubset(observed_metric_gate_areas),
        f"metric gate missing required areas: {sorted(required_metric_gate_areas - observed_metric_gate_areas)}",
    )
    checks.append("metric_gate_summary rows=12 pass")

    ml_rows = read_csv("outputs/report_tables/ml_contribution_audit.csv")
    require(len(ml_rows) == 7, f"expected 7 ML contribution rows, got {len(ml_rows)}")
    failed_ml_rows = [
        f"{row['check_id']}:{row['area']}"
        for row in ml_rows
        if row.get("status") != "pass"
    ]
    require(not failed_ml_rows, f"failed ML contribution rows: {failed_ml_rows[:8]}")
    required_ml_areas = {
        "AURA-ML model quality",
        "TSRA-R-ML detector quality",
        "AURA-ML tool invocation",
        "TSRA-R-ML tool invocation",
        "Closed-loop ML separation",
        "E7 ML closed-loop actions",
        "Mac MPS scale experiment",
    }
    observed_ml_areas = {row["area"] for row in ml_rows}
    require(
        required_ml_areas == observed_ml_areas,
        f"ML contribution audit has unexpected areas: {sorted(observed_ml_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in ml_rows),
        "ML contribution audit missing safety boundary",
    )
    require(
        any(
            "predict_candidate_impact_invocations=" in row["observed"]
            and "errors=0" in row["observed"]
            for row in ml_rows
            if row["check_id"] == "M03"
        ),
        "ML contribution audit missing AURA-ML tool invocation evidence",
    )
    require(
        any(
            "predict_attack_probability_invocations=" in row["observed"]
            and "errors=0" in row["observed"]
            for row in ml_rows
            if row["check_id"] == "M04"
        ),
        "ML contribution audit missing TSRA-R-ML tool invocation evidence",
    )
    require(
        any(
            "abs_e7_minus_e6=" in row["observed"]
            for row in ml_rows
            if row["check_id"] == "M05"
        ),
        "ML contribution audit missing E6/E7 separation evidence",
    )
    require(
        any(
            "sample_passes=20000000" in row["observed"]
            and "histgb_top1_action_match_rate=" in row["observed"]
            for row in ml_rows
            if row["check_id"] == "M07"
        ),
        "ML contribution audit missing MPS sample-pass and top-1 comparison evidence",
    )
    checks.append("ml_contribution_audit rows=7 pass")

    ml_attack_path_rows = read_csv("outputs/report_tables/ml_attack_decision_path_audit.csv")
    require(
        len(ml_attack_path_rows) == 6,
        f"expected 6 ML attack decision path rows, got {len(ml_attack_path_rows)}",
    )
    failed_ml_attack_path_rows = [
        f"{row['check_id']}:{row['area']}"
        for row in ml_attack_path_rows
        if row.get("status") != "pass"
    ]
    require(
        not failed_ml_attack_path_rows,
        f"failed ML attack path rows: {failed_ml_attack_path_rows[:8]}",
    )
    required_ml_attack_path_areas = {
        "Pre-start no-op gate",
        "Candidate scoring toolchain",
        "Top-score selection link",
        "Detectability-adjusted score",
        "Cadence and event budget gate",
        "Closed-loop attack feedback",
    }
    observed_ml_attack_path_areas = {row["area"] for row in ml_attack_path_rows}
    require(
        required_ml_attack_path_areas == observed_ml_attack_path_areas,
        f"ML attack path audit has unexpected areas: {sorted(observed_ml_attack_path_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in ml_attack_path_rows),
        "ML attack path audit missing safety boundary",
    )
    require(
        any(
            "pre_start_noop_count=6" in row["observed"]
            and "pre_start_attack_events=0" in row["observed"]
            for row in ml_attack_path_rows
            if row["check_id"] == "MAP01"
        ),
        "ML attack path audit missing pre-start no-op evidence",
    )
    require(
        any(
            observed_int(row, "candidate_total") >= 25
            and observed_int(row, "generated_candidate_total")
            == observed_int(row, "candidate_total")
            and observed_int(row, "generated_candidate_payload_matches") == 5
            and observed_int(row, "generated_candidate_payload_mismatches") == 0
            and observed_int(row, "predict_candidate_impact") == observed_int(row, "candidate_total")
            and observed_int(row, "estimate_candidate_effect") == observed_int(row, "candidate_total")
            and observed_int(row, "estimate_detectability") == observed_int(row, "candidate_total")
            and observed_int(row, "tool_errors") == 0
            for row in ml_attack_path_rows
            if row["check_id"] == "MAP02"
        ),
        "ML attack path audit missing candidate toolchain evidence",
    )
    require(
        any(
            "selected_matches_top_candidate=5" in row["observed"]
            and "score_event_matches=5" in row["observed"]
            and "payload_selected_matches=5" in row["observed"]
            for row in ml_attack_path_rows
            if row["check_id"] == "MAP03"
        ),
        "ML attack path audit missing top-score selection evidence",
    )
    require(
        any(
            observed_int(row, "candidate_total") >= 25
            and observed_int(row, "score_formula_matches") == observed_int(row, "candidate_total")
            and observed_int(row, "selection_score_formula_matches") == observed_int(row, "candidate_total")
            and observed_int(row, "selected_objective_bonus_count") >= 1
            and observed_int(row, "selected_counter_defense_bonus_count") >= 1
            for row in ml_attack_path_rows
            if row["check_id"] == "MAP04"
        ),
        "ML attack path audit missing objective/counter-defense-aware score evidence",
    )
    require(
        any(
            "cooldown_noops=16" in row["observed"]
            and "max_event_noops=4" in row["observed"]
            and "min_attack_gap_sec=50" in row["observed"]
            for row in ml_attack_path_rows
            if row["check_id"] == "MAP05"
        ),
        "ML attack path audit missing cadence/event budget evidence",
    )
    require(
        any(
            "queue_pressure" in row["observed"]
            and "failover_chasing" in row["observed"]
            and "stale_cop_induction" in row["observed"]
            and "complete_responses=5" in row["observed"]
            and "positive_reductions=5" in row["observed"]
            for row in ml_attack_path_rows
            if row["check_id"] == "MAP06"
        ),
        "ML attack path audit missing multi-tactic closed-loop evidence",
    )
    checks.append("ml_attack_decision_path_audit rows=6 pass")

    ml_path_rows = read_csv("outputs/report_tables/ml_defense_decision_path_audit.csv")
    require(
        len(ml_path_rows) == 8,
        f"expected 8 ML defense decision path rows, got {len(ml_path_rows)}",
    )
    failed_ml_path_rows = [
        f"{row['check_id']}:{row['area']}"
        for row in ml_path_rows
        if row.get("status") != "pass"
    ]
    require(not failed_ml_path_rows, f"failed ML defense path rows: {failed_ml_path_rows[:8]}")
    required_ml_path_areas = {
        "Pre-threshold guard discipline",
        "Threshold-to-window transition",
        "Alert cooldown and window refresh",
        "Core defense fanout",
        "Rule-defense tool execution",
        "Memory continuity",
        "Closed-loop coordination effect",
        "Candidate-feedback parity",
    }
    observed_ml_path_areas = {row["area"] for row in ml_path_rows}
    require(
        required_ml_path_areas == observed_ml_path_areas,
        f"ML defense path audit has unexpected areas: {sorted(observed_ml_path_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in ml_path_rows),
        "ML defense path audit missing safety boundary",
    )
    require(
        any(
            observed_int(row, "pre_threshold_guard_traces") >= 1
            and observed_int(row, "pre_threshold_guard_event_count")
            == observed_int(row, "pre_threshold_defense_events")
            and observed_int(row, "pre_threshold_ml_alerts") == 0
            for row in ml_path_rows
            if row["check_id"] == "MDP01"
        ),
        "ML defense path audit missing pre-threshold guard evidence",
    )
    require(
        any(
            "first_response_latency_sec=20" in row["observed"]
            and "same_time_actions=ml_attack_alert" in row["observed"]
            for row in ml_path_rows
            if row["check_id"] == "MDP02"
        ),
        "ML defense path audit missing threshold-to-window evidence",
    )
    require(
        any(
            observed_int(row, "above_threshold_no_event_refresh_traces") >= 15
            and "min_alert_gap_sec=25" in row["observed"]
            for row in ml_path_rows
            if row["check_id"] == "MDP03"
        ),
        "ML defense path audit missing cooldown refresh evidence",
    )
    require(
        any(
            observed_int(row, "active_window_traces") > 0
            and observed_int(row, "rule_tool_traces")
            == observed_int(row, "active_window_traces")
            and observed_int(row, "delegate_trace_count")
            == observed_int(row, "active_window_traces")
            and observed_int(row, "selected_defense_traces_with_rule_tool")
            == observed_int(row, "selected_defense_traces")
            and observed_int(row, "rule_tool_error_count") == 0
            and observed_int(row, "rule_tool_event_pairs") > 0
            and observed_int(row, "rule_tool_event_pairs")
            == observed_int(row, "selected_rule_event_pairs")
            and observed_int(row, "rule_tool_event_pairs")
            == observed_int(row, "delegate_rule_event_pairs")
            and observed_int(row, "rule_tool_selected_event_mismatches") == 0
            and observed_int(row, "active_window_delegate_misses") == 0
            and observed_int(row, "rule_tool_delegate_event_mismatches") == 0
            and "tool_name=execute_rule_defense_actions" in row["observed"]
            for row in ml_path_rows
            if row["check_id"] == "MDP05"
        ),
        "ML defense path audit missing rule-defense tool execution evidence",
    )
    require(
        any(
            "memory_mismatches=0" in row["observed"]
            and "threshold_window_nondecreasing=true" in row["observed"]
            for row in ml_path_rows
            if row["check_id"] == "MDP06"
        ),
        "ML defense path audit missing memory continuity evidence",
    )
    require(
        any(
            observed_int(row, "open_window_candidate_traces") == 61
            and observed_int(row, "missing_or_duplicate_candidates") == 0
            and observed_int(row, "candidate_feedback_checks") == observed_int(row, "candidate_feedback_matches")
            and observed_int(row, "candidate_feedback_mismatches") == 0
            for row in ml_path_rows
            if row["check_id"] == "MDP08"
        ),
        "ML defense path audit missing candidate-feedback parity evidence",
    )
    checks.append("ml_defense_decision_path_audit rows=8 pass")

    ml_interaction_rows = read_csv("outputs/report_tables/ml_red_blue_interaction_audit.csv")
    require(
        len(ml_interaction_rows) == 5,
        f"expected 5 ML red-blue interaction rows, got {len(ml_interaction_rows)}",
    )
    failed_ml_interactions = [
        f"{row['attack_event_id']}:{row['interaction_class']}"
        for row in ml_interaction_rows
        if row.get("interaction_status") != "pass"
    ]
    require(not failed_ml_interactions, f"failed ML red-blue interactions: {failed_ml_interactions[:8]}")
    require(
        {row["experiment"] for row in ml_interaction_rows} == {"E7_ml_aura_ml_tsra_r"},
        "ML red-blue interaction audit must only cover E7 ML-vs-ML episodes",
    )
    interaction_classes = {row["interaction_class"] for row in ml_interaction_rows}
    require(
        {
            "ml_triggered_after_attack",
            "active_window_immediate_core_defense",
            "active_window_bounded_refresh",
        }.issubset(interaction_classes),
        f"ML red-blue interaction audit missing interaction classes: {sorted(interaction_classes)}",
    )
    require(
        all(row["aura_selection_link_status"] == "linked" for row in ml_interaction_rows),
        "ML red-blue interaction audit has unlinked AURA selections",
    )
    require(
        all(float(row["aura_candidate_count"]) > 0 for row in ml_interaction_rows),
        "ML red-blue interaction audit has rows without AURA candidates",
    )
    require(
        all(float(row["first_above_threshold_latency_sec"]) <= 20.0 for row in ml_interaction_rows),
        "ML red-blue interaction audit has slow threshold crossing",
    )
    require(
        all(
            row["first_ml_alert_latency_sec"] == ""
            or float(row["first_ml_alert_latency_sec"]) <= 20.0
            for row in ml_interaction_rows
        ),
        "ML red-blue interaction audit has slow ML alert latency",
    )
    require(
        all(float(row["first_core_defense_latency_sec"]) <= 20.0 for row in ml_interaction_rows),
        "ML red-blue interaction audit has slow core defense response",
    )
    require(
        all(float(row["peak_probability_in_response_window"]) >= 0.75 for row in ml_interaction_rows),
        "ML red-blue interaction audit has below-threshold peak probability",
    )
    require(
        all(float(row["impact_reduction_from_peak"]) > 0.0 for row in ml_interaction_rows),
        "ML red-blue interaction audit has no positive post-peak reduction",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in ml_interaction_rows),
        "ML red-blue interaction audit missing safety boundary",
    )
    checks.append("ml_red_blue_interaction_audit rows=5 pass")

    tradeoff_rows = read_csv("outputs/report_tables/reactive_defense_tradeoff_audit.csv")
    require(
        len(tradeoff_rows) == 7,
        f"expected 7 reactive defense tradeoff rows, got {len(tradeoff_rows)}",
    )
    failed_tradeoff_rows = [
        f"{row['check_id']}:{row['area']}"
        for row in tradeoff_rows
        if row.get("status") != "pass"
    ]
    require(not failed_tradeoff_rows, f"failed reactive defense tradeoff rows: {failed_tradeoff_rows[:8]}")
    required_tradeoff_areas = {
        "Policy separation",
        "Pre-attack defense suppression",
        "First-response latency cost",
        "ML alert attack overlap",
        "Core defense preservation",
        "Bounded impact tradeoff",
        "Detector threshold evidence",
    }
    observed_tradeoff_areas = {row["area"] for row in tradeoff_rows}
    require(
        required_tradeoff_areas == observed_tradeoff_areas,
        f"reactive defense tradeoff audit has unexpected areas: {sorted(observed_tradeoff_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in tradeoff_rows),
        "reactive defense tradeoff audit missing safety boundary",
    )
    require(
        any(
            "e6_pre_first_defense_events=2" in row["observed"]
            and "e7_pre_first_defense_events=0" in row["observed"]
            for row in tradeoff_rows
            if row["check_id"] == "RDT02"
        ),
        "reactive defense tradeoff audit missing pre-attack suppression evidence",
    )
    require(
        any(
            observed_int(row, "ml_attack_alerts") >= 5
            and observed_int(row, "active_attack_overlap") == observed_int(row, "ml_attack_alerts")
            for row in tradeoff_rows
            if row["check_id"] == "RDT04"
        ),
        "reactive defense tradeoff audit missing alert overlap evidence",
    )
    require(
        any(
            observed_int(row, "e7_core_defense_events") >= 20
            and "core_action_coverage=4/4" in row["observed"]
            and "priority_reroute:" in row["observed"]
            and "stale_badge:" in row["observed"]
            and "video_throttle:" in row["observed"]
            and "pace_switch:" in row["observed"]
            for row in tradeoff_rows
            if row["check_id"] == "RDT05"
        ),
        "reactive defense tradeoff audit missing core action coverage evidence",
    )
    require(
        any(
            0.005 <= float(observed_value(row, "e7_minus_e6")) <= 0.02
            for row in tradeoff_rows
            if row["check_id"] == "RDT06"
        ),
        "reactive defense tradeoff audit missing bounded impact tradeoff evidence",
    )
    checks.append("reactive_defense_tradeoff_audit rows=7 pass")

    threshold_raw_rows = read_csv("outputs/batch/ml_threshold_sweep_raw.csv")
    threshold_summary_rows = read_csv("outputs/batch/ml_threshold_sweep_summary.csv")
    threshold_report_rows = read_csv("outputs/report_tables/ml_threshold_sweep.csv")
    require(
        len(threshold_raw_rows) == 50,
        f"expected 50 ML threshold sweep raw rows, got {len(threshold_raw_rows)}",
    )
    require(
        len(threshold_summary_rows) == 5,
        f"expected 5 ML threshold sweep summary rows, got {len(threshold_summary_rows)}",
    )
    require(
        threshold_report_rows == threshold_summary_rows,
        "ML threshold sweep report CSV differs from batch summary",
    )
    required_thresholds = {"0.55", "0.65", "0.75", "0.85", "0.95"}
    observed_thresholds = {row["threshold"] for row in threshold_summary_rows}
    require(
        observed_thresholds == required_thresholds,
        f"ML threshold sweep has unexpected thresholds: {sorted(observed_thresholds)}",
    )
    by_threshold = {row["threshold"]: row for row in threshold_summary_rows}
    require(
        by_threshold["0.75"]["tuning_status"] == "usable",
        "ML threshold sweep baseline 0.75 is not usable",
    )
    require(
        by_threshold["0.95"]["tuning_status"] == "watch",
        "ML threshold sweep high threshold 0.95 should be watch",
    )
    require(
        float(by_threshold["0.95"]["ml_alert_count_mean"])
        < float(by_threshold["0.75"]["ml_alert_count_mean"])
        and float(by_threshold["0.95"]["opened_window_count_mean"])
        < float(by_threshold["0.75"]["opened_window_count_mean"]),
        "ML threshold sweep does not show high-threshold alert/window cost",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in threshold_summary_rows),
        "ML threshold sweep summary missing safety boundary",
    )
    checks.append("ml_threshold_sweep rows=5 raw=50 status=usable/watch")

    calibration_rows = read_csv("outputs/report_tables/tsra_detector_calibration_audit.csv")
    calibration_bins = read_csv("outputs/report_tables/tsra_detector_calibration_bins.csv")
    require(
        len(calibration_rows) == 6,
        f"expected 6 TSRA detector calibration audit rows, got {len(calibration_rows)}",
    )
    require(
        len(calibration_bins) == 10,
        f"expected 10 TSRA detector calibration bins, got {len(calibration_bins)}",
    )
    failed_calibration = [
        f"{row['check_id']}:{row['area']}"
        for row in calibration_rows
        if row.get("status") != "pass"
    ]
    require(not failed_calibration, f"failed TSRA detector calibration rows: {failed_calibration[:8]}")
    required_calibration_areas = {
        "Holdout coverage",
        "Probability calibration",
        "Baseline threshold quality",
        "Threshold sensitivity",
        "Class probability separation",
        "Closed-loop threshold consistency",
    }
    observed_calibration_areas = {row["area"] for row in calibration_rows}
    require(
        observed_calibration_areas == required_calibration_areas,
        f"TSRA detector calibration audit has unexpected areas: {sorted(observed_calibration_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in calibration_rows),
        "TSRA detector calibration audit missing safety boundary",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in calibration_bins),
        "TSRA detector calibration bins missing safety boundary",
    )
    require(
        any(
            "brier_score=0.0351619" in row["observed"]
            and "expected_calibration_error=0.093589" in row["observed"]
            for row in calibration_rows
            if row["check_id"] == "CAL02"
        ),
        "TSRA detector calibration audit missing Brier/ECE evidence",
    )
    require(
        any(
            "threshold=0.75" in row["observed"]
            and "precision=1" in row["observed"]
            and "false_positive_rate=0" in row["observed"]
            for row in calibration_rows
            if row["check_id"] == "CAL03"
        ),
        "TSRA detector calibration audit missing baseline threshold precision evidence",
    )
    require(
        any(
            "sweep_0.75_status=usable" in row["observed"]
            and "sweep_0.95_status=watch" in row["observed"]
            for row in calibration_rows
            if row["check_id"] == "CAL06"
        ),
        "TSRA detector calibration audit missing closed-loop sweep consistency evidence",
    )
    checks.append("tsra_detector_calibration_audit rows=6 bins=10 pass")

    safety_rows = read_csv("outputs/report_tables/safety_boundary_audit.csv")
    require(len(safety_rows) == 5, f"expected 5 safety boundary rows, got {len(safety_rows)}")
    failed_safety = [
        f"{row['check_id']}:{row['area']}"
        for row in safety_rows
        if row.get("status") != "pass"
    ]
    require(not failed_safety, f"failed safety boundary rows: {failed_safety[:8]}")
    required_safety_areas = {
        "Operational core source",
        "Automation exceptions",
        "Attack-effect schema",
        "Safety-boundary text",
        "Submission package safety",
    }
    observed_safety_areas = {row["area"] for row in safety_rows}
    require(
        required_safety_areas == observed_safety_areas,
        f"safety boundary audit has unexpected areas: {sorted(observed_safety_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in safety_rows),
        "safety boundary audit missing closed simulation text",
    )
    require(
        any(
            "network_hits=0" in row["observed"]
            for row in safety_rows
            if row["check_id"] == "S01"
        ),
        "safety boundary audit does not prove operational core network_hits=0",
    )
    require(
        any(
            "unexpected_network_hits=0" in row["observed"]
            for row in safety_rows
            if row["check_id"] == "S02"
        ),
        "safety boundary audit does not prove automation network exceptions are allowlisted",
    )
    require(
        any(
            "excluded_artifact_hits=0" in row["observed"]
            for row in safety_rows
            if row["check_id"] == "S05"
        ),
        "safety boundary audit does not prove package exclusion status",
    )
    checks.append("safety_boundary_audit rows=5 pass")

    reproduction_order_rows = read_csv("outputs/report_tables/reproduction_order_audit.csv")
    require(
        len(reproduction_order_rows) == 18,
        f"expected 18 reproduction order rows, got {len(reproduction_order_rows)}",
    )
    failed_reproduction_order = [
        f"{row['check_id']}:{row['order_status']}:{row['output_status']}"
        for row in reproduction_order_rows
        if row.get("status") != "pass"
    ]
    require(
        not failed_reproduction_order,
        f"failed reproduction order rows: {failed_reproduction_order[:8]}",
    )
    require(
        {row["check_id"] for row in reproduction_order_rows}
        == {f"RO{index:02d}" for index in range(1, 19)},
        "reproduction order audit check ids are incomplete",
    )
    require(
        all(row["order_status"] == "pass" for row in reproduction_order_rows),
        "reproduction order audit contains ordering failures",
    )
    require(
        all(row["output_status"] == "pass" for row in reproduction_order_rows),
        "reproduction order audit contains missing output failures",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in reproduction_order_rows),
        "reproduction order audit missing safety boundary",
    )
    require(
        any(
            row["check_id"] == "RO11"
            and "ml_attack_decision_path_audit" in row["required_before"]
            and "ml_defense_decision_path_audit" in row["required_before"]
            for row in reproduction_order_rows
        ),
        "reproduction order audit missing ML red-blue path prerequisites",
    )
    require(
        any(
            row["check_id"] == "RO06"
            and "run_all" in row["required_before"]
            for row in reproduction_order_rows
        ),
        "reproduction order audit missing cross-agent context prerequisite",
    )
    require(
        any(
            row["check_id"] == "RO07"
            and "run_all" in row["required_before"]
            and "cross_agent_context_audit" in row["required_before"]
            for row in reproduction_order_rows
        ),
        "reproduction order audit missing AURA attack path prerequisites",
    )
    require(
        any(
            row["check_id"] == "RO08"
            and "run_all" in row["required_before"]
            and "cross_agent_context_audit" in row["required_before"]
            for row in reproduction_order_rows
        ),
        "reproduction order audit missing defense priority path prerequisites",
    )
    require(
        any(
            row["check_id"] == "RO12"
            and "run_adaptive_memory" in row["required_before"]
            for row in reproduction_order_rows
        ),
        "reproduction order audit missing adaptive defense path prerequisite",
    )
    require(
        any(
            row["check_id"] == "RO14"
            and "agent_stress_scenario_audit" in row["required_before"]
            and "reproduction_order_audit" in row["required_before"]
            for row in reproduction_order_rows
        ),
        "reproduction order audit missing stress prerequisite for alignment",
    )
    require(
        any(
            row["check_id"] == "RO15"
            and "submission_readiness_audit" in row["required_before"]
            and "competition_alignment" in row["required_before"]
            for row in reproduction_order_rows
        ),
        "reproduction order audit missing package prerequisites",
    )
    require(
        any(
            row["check_id"] == "RO18"
            and "unittest discover" in row["required_before"]
            and "agent_quality_gate_audit" in row["required_before"]
            for row in reproduction_order_rows
        ),
        "reproduction order audit missing team handoff prerequisites",
    )
    checks.append("reproduction_order_audit rows=18 pass")

    readiness_rows = read_csv("outputs/report_tables/submission_readiness_audit.csv")
    require(
        len(readiness_rows) == 10,
        f"expected 10 submission readiness rows, got {len(readiness_rows)}",
    )
    failed_readiness = [
        f"{row['check_id']}:{row['area']}"
        for row in readiness_rows
        if row.get("status") != "pass"
    ]
    require(not failed_readiness, f"failed submission readiness rows: {failed_readiness[:8]}")
    required_readiness_areas = {
        "Branch policy",
        "Reproduction commands",
        "Agent runtime structure",
        "Attack and defense separation",
        "Decision evidence",
        "Closed-loop evidence",
        "Metric and ML evidence",
        "Package inputs",
        "Safety boundary",
        "Team handoff docs",
    }
    observed_readiness_areas = {row["area"] for row in readiness_rows}
    require(
        required_readiness_areas == observed_readiness_areas,
        f"submission readiness audit has unexpected areas: {sorted(observed_readiness_areas)}",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in readiness_rows),
        "submission readiness audit missing safety boundary",
    )
    checks.append("submission_readiness_audit rows=10 pass")

    coa_rows = read_csv("outputs/report_tables/aura_coa_cards.csv")
    require(len(coa_rows) >= 10, f"COA cards too small: {len(coa_rows)} rows")
    require(
        all(has_safety_boundary(row.get("safety_boundary", "")) for row in coa_rows),
        "AURA COA cards missing simulation safety boundary",
    )
    checks.append(f"aura_coa_cards rows={len(coa_rows)}")

    battle_rows = read_csv("outputs/report_tables/battle_timeline.csv")
    battle_experiments = {row["experiment"] for row in battle_rows}
    require(
        battle_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected battle timeline experiments: {sorted(battle_experiments)}",
    )
    for experiment in battle_experiments:
        subset = [row for row in battle_rows if row["experiment"] == experiment]
        require(any(row["attack_events"] for row in subset), f"{experiment} has no attack events")
        require(any(row["defense_events"] for row in subset), f"{experiment} has no defense events")
    require(
        all("closed simulation" in row["safety_boundary"] for row in battle_rows),
        "battle timeline missing safety boundary",
    )
    checks.append(f"battle_timeline rows={len(battle_rows)}")

    incident_rows = read_csv("outputs/report_tables/incident_summary.csv")
    incident_experiments = {row["experiment"] for row in incident_rows}
    require(
        incident_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected incident summary experiments: {sorted(incident_experiments)}",
    )
    for experiment in incident_experiments:
        subset = [row for row in incident_rows if row["experiment"] == experiment]
        require(3 <= len(subset) <= 5, f"{experiment} should have 3-5 incidents, got {len(subset)}")
        require(all(row["attack_summary"] for row in subset), f"{experiment} incident missing attack summary")
        require(all(row["defense_response"] for row in subset), f"{experiment} incident missing defense response")
    require(
        all("closed simulation" in row["safety_boundary"] for row in incident_rows),
        "incident summary missing safety boundary",
    )
    checks.append(f"incident_summary rows={len(incident_rows)}")

    alert_rows = read_csv("outputs/report_tables/operator_alerts.csv")
    require(len(alert_rows) >= 50, f"expected at least 50 operator alert rows, got {len(alert_rows)}")
    alert_experiments = {row["experiment"] for row in alert_rows}
    require(
        alert_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected operator alert experiments: {sorted(alert_experiments)}",
    )
    alert_actions = {row["action"] for row in alert_rows}
    required_alert_actions = {
        "ml_attack_alert",
        "pace_switch",
        "priority_reroute",
        "stale_badge",
        "video_throttle",
    }
    require(
        required_alert_actions.issubset(alert_actions),
        f"operator alerts missing actions: {sorted(required_alert_actions - alert_actions)}",
    )
    require(
        {"high", "medium"}.issubset({row["severity"] for row in alert_rows}),
        "operator alerts missing severity mix",
    )
    require(
        all(row["operator_alert"] and row["mission_rationale"] for row in alert_rows),
        "operator alerts missing alert text or rationale",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in alert_rows),
        "operator alerts missing safety boundary",
    )
    checks.append(f"operator_alerts rows={len(alert_rows)} actions=5")

    ledger_rows = read_csv("outputs/report_tables/defense_effectiveness_ledger.csv")
    require(
        len(ledger_rows) >= 50,
        f"expected at least 50 defense effectiveness ledger rows, got {len(ledger_rows)}",
    )
    ledger_experiments = {row["experiment"] for row in ledger_rows}
    require(
        ledger_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected defense effectiveness ledger experiments: {sorted(ledger_experiments)}",
    )
    ledger_actions = {row["action"] for row in ledger_rows}
    require(
        required_alert_actions.issubset(ledger_actions),
        f"defense effectiveness ledger missing actions: {sorted(required_alert_actions - ledger_actions)}",
    )
    allowed_effects = {"improved", "held", "degraded_or_delayed"}
    observed_effects = {row["observed_effect"] for row in ledger_rows}
    require(
        observed_effects.issubset(allowed_effects) and {"improved", "held"}.issubset(observed_effects),
        f"unexpected defense effectiveness labels: {sorted(observed_effects)}",
    )
    require(
        all(row["operator_alert"] and row["related_attack_context"] for row in ledger_rows),
        "defense effectiveness ledger missing alert or attack context",
    )
    require(
        all(row["interpretation"] and row["delta_mission_impact"] for row in ledger_rows),
        "defense effectiveness ledger missing interpretation or metric deltas",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in ledger_rows),
        "defense effectiveness ledger missing safety boundary",
    )
    checks.append(f"defense_effectiveness_ledger rows={len(ledger_rows)} actions=5")

    attribution_rows = read_csv("outputs/report_tables/defense_action_attribution_audit.csv")
    require(
        len(attribution_rows) == 5,
        f"expected 5 defense action attribution rows, got {len(attribution_rows)}",
    )
    attribution_actions = {row["action"] for row in attribution_rows}
    require(
        attribution_actions == required_alert_actions,
        f"defense action attribution missing actions: {sorted(required_alert_actions - attribution_actions)}",
    )
    failed_attribution = [
        row["action"]
        for row in attribution_rows
        if row.get("attribution_status") != "pass"
    ]
    require(not failed_attribution, f"failed defense action attribution rows: {failed_attribution}")
    required_attribution_classes = {
        "ablation_supported",
        "bounded_tradeoff_supported",
        "local_metric_supported",
        "reactive_window_supported",
    }
    observed_attribution_classes = {row["attribution_class"] for row in attribution_rows}
    require(
        required_attribution_classes.issubset(observed_attribution_classes),
        f"defense action attribution missing classes: {sorted(required_attribution_classes - observed_attribution_classes)}",
    )
    by_action = {row["action"]: row for row in attribution_rows}
    require(
        float(by_action["priority_reroute"]["ablation_delta_value"]) >= 0.40,
        "priority_reroute attribution missing ablation priority-inversion evidence",
    )
    require(
        float(by_action["stale_badge"]["ablation_delta_value"]) >= 0.35,
        "stale_badge attribution missing trusted stale ablation evidence",
    )
    alert_overlap_evidence = by_action["ml_attack_alert"]["reactive_overlap_evidence"]
    alert_match = re.search(r"ml_attack_alerts=(\d+)", alert_overlap_evidence)
    overlap_match = re.search(r"active_attack_overlap=(\d+)", alert_overlap_evidence)
    alert_count = int(alert_match.group(1)) if alert_match else 0
    overlap_count = int(overlap_match.group(1)) if overlap_match else -1
    require(
        alert_count >= 5 and overlap_count == alert_count,
        "ml_attack_alert attribution missing active attack overlap evidence",
    )
    require(
        all(float(row["improved_or_held_rate"]) >= 0.66 for row in attribution_rows),
        "defense action attribution has weak improved/held rate",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in attribution_rows),
        "defense action attribution missing safety boundary",
    )
    checks.append("defense_action_attribution_audit rows=5 pass")

    episode_rows = read_csv("outputs/report_tables/closed_loop_episode_replay.csv")
    require(
        len(episode_rows) == 10,
        f"expected 10 closed-loop episode rows, got {len(episode_rows)}",
    )
    episode_experiments = {row["experiment"] for row in episode_rows}
    require(
        episode_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected closed-loop episode experiments: {sorted(episode_experiments)}",
    )
    require(
        all(row["response_status"] == "complete" for row in episode_rows),
        "closed-loop episode replay has incomplete response status",
    )
    require(
        {"queue_pressure", "failover_chasing"}.issubset(
            {row["attack_type"] for row in episode_rows}
        ),
        "closed-loop episode replay missing attack types",
    )
    require(
        all(row["defense_chain"] != "none" for row in episode_rows),
        "closed-loop episode replay missing defense chains",
    )
    require(
        all(row["operator_alert_chain"] != "none" for row in episode_rows),
        "closed-loop episode replay missing operator alert chains",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in episode_rows),
        "closed-loop episode replay missing safety boundary",
    )
    checks.append("closed_loop_episode_replay rows=10 complete")

    coordination_rows = read_csv("outputs/report_tables/agent_coordination_latency_audit.csv")
    require(
        len(coordination_rows) == 10,
        f"expected 10 coordination latency rows, got {len(coordination_rows)}",
    )
    require(
        {row["experiment"] for row in coordination_rows}
        == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        "coordination latency audit missing E5/E7 experiments",
    )
    failed_coordination = [
        f"{row['experiment']}:{row['attack_event_id']}"
        for row in coordination_rows
        if row.get("coordination_status") != "pass"
    ]
    require(not failed_coordination, f"failed coordination latency rows: {failed_coordination[:8]}")
    require(
        sum(1 for row in coordination_rows if row["experiment"] == "E5_rule_aura_tsra_r") == 5,
        "coordination latency audit must include 5 E5 rows",
    )
    require(
        sum(1 for row in coordination_rows if row["experiment"] == "E7_ml_aura_ml_tsra_r") == 5,
        "coordination latency audit must include 5 E7 rows",
    )
    require(
        {"prepositioned_defense", "ml_reactive_window"}.issubset(
            {row["coordination_class"] for row in coordination_rows}
        ),
        "coordination latency audit missing prepositioned or ML reactive classes",
    )
    require(
        all(float(row["first_operator_alert_latency_sec"]) <= 40.0 for row in coordination_rows),
        "coordination latency audit has alert latency outside response window",
    )
    require(
        all(float(row["impact_reduction_from_peak"]) > 0.0 for row in coordination_rows),
        "coordination latency audit has no positive post-peak reduction",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in coordination_rows),
        "coordination latency audit missing safety boundary",
    )
    checks.append("agent_coordination_latency_audit rows=10 pass")

    stress_rows = read_csv("outputs/report_tables/agent_stress_scenario_audit.csv")
    require(len(stress_rows) == 6, f"expected 6 agent stress rows, got {len(stress_rows)}")
    failed_stress_rows = [
        f"{row['check_id']}:{row['scenario_id']}:{row['defender_variant']}"
        for row in stress_rows
        if row.get("status") != "pass"
    ]
    require(not failed_stress_rows, f"failed agent stress rows: {failed_stress_rows[:8]}")
    expected_stress_scenarios = {
        "stress_air_defense_queue_saturation",
        "stress_stale_cop_latency_chain",
        "stress_pace_failover_pressure",
    }
    expected_stress_variants = {"tsra_r_full", "tsra_r_ml"}
    observed_stress_scenarios = {row["scenario_id"] for row in stress_rows}
    observed_stress_variants = {row["defender_variant"] for row in stress_rows}
    require(
        observed_stress_scenarios == expected_stress_scenarios,
        f"unexpected stress scenarios: {sorted(observed_stress_scenarios)}",
    )
    require(
        observed_stress_variants == expected_stress_variants,
        f"unexpected stress defender variants: {sorted(observed_stress_variants)}",
    )
    require(
        all(int(float(row["seed_count"])) == 5 for row in stress_rows),
        "stress audit must aggregate 5 seeds per row",
    )
    require(
        all(row["seed_range"] == "2607-2611" for row in stress_rows),
        "stress audit has unexpected seed range",
    )
    require(
        all(float(row["defended_mission_impact_mean"]) <= 0.25 for row in stress_rows),
        "stress audit has defended mission impact mean above ceiling",
    )
    require(
        all(float(row["defended_mission_impact_max"]) <= 0.40 for row in stress_rows),
        "stress audit has defended mission impact max above stress ceiling",
    )
    require(
        all(float(row["mission_impact_reduction_mean"]) > 0.0 for row in stress_rows),
        "stress audit has non-positive mission impact reduction mean",
    )
    require(
        all(float(row["p95_reduction_sec_mean"]) > 0.0 for row in stress_rows),
        "stress audit has non-positive P95 reduction",
    )
    require(
        all(float(row["trusted_stale_reduction_mean"]) > 0.0 for row in stress_rows),
        "stress audit has non-positive trusted stale reduction",
    )
    require(
        all(float(row["priority_inversion_reduction_mean"]) > 0.0 for row in stress_rows),
        "stress audit has non-positive priority inversion reduction",
    )
    require(
        all(float(row["defense_count_mean"]) > 0.0 for row in stress_rows),
        "stress audit has rows without defense events",
    )
    require(
        all(
            float(row["resilience_gain_mean"]) >= 0.75
            for row in stress_rows
            if row["defender_variant"] == "tsra_r_full"
        ),
        "full TSRA-R mean stress resilience below threshold",
    )
    require(
        all(
            float(row["resilience_gain_mean"]) >= 0.65
            for row in stress_rows
            if row["defender_variant"] == "tsra_r_ml"
        ),
        "ML TSRA-R mean stress resilience below threshold",
    )
    require(
        all(
            float(row["resilience_gain_min"]) >= 0.70
            for row in stress_rows
            if row["defender_variant"] == "tsra_r_full"
        ),
        "full TSRA-R minimum stress resilience below threshold",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in stress_rows),
        "agent stress scenario audit missing safety boundary",
    )
    checks.append("agent_stress_scenario_audit rows=6 seeds=5 pass")

    mission_thread_rows = read_csv("outputs/report_tables/mission_thread_summary.csv")
    require(
        len(mission_thread_rows) == 10,
        f"expected 10 mission thread rows, got {len(mission_thread_rows)}",
    )
    require(
        {row["experiment"] for row in mission_thread_rows}
        == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        "mission thread summary missing E5/E7 experiments",
    )
    require(
        all(row["thread_status"] == "pass" for row in mission_thread_rows),
        "mission thread summary has non-pass rows",
    )
    require(
        {"queue_pressure", "failover_chasing"}.issubset(
            {row["attack_type"] for row in mission_thread_rows}
        ),
        "mission thread summary missing attack types",
    )
    require(
        all("status=complete" in row["response_signal"] for row in mission_thread_rows),
        "mission thread summary has incomplete response signals",
    )
    require(
        all("status=pass" in row["attribution_signal"] for row in mission_thread_rows),
        "mission thread summary missing passing attribution signals",
    )
    require(
        all(int(float(row["operator_signal_count"])) >= 2 for row in mission_thread_rows),
        "mission thread summary has weak operator alert linkage",
    )
    require(
        all("reduction_from_peak=" in row["metric_signal"] for row in mission_thread_rows),
        "mission thread summary missing metric movement",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in mission_thread_rows),
        "mission thread summary missing safety boundary",
    )
    checks.append("mission_thread_summary rows=10 pass")

    engagement_rows = read_csv("outputs/report_tables/agent_engagement_scorecard.csv")
    require(
        len(engagement_rows) == 10,
        f"expected 10 agent engagement scorecard rows, got {len(engagement_rows)}",
    )
    engagement_experiments = {row["experiment"] for row in engagement_rows}
    require(
        engagement_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected engagement scorecard experiments: {sorted(engagement_experiments)}",
    )
    require(
        all(row["scorecard_status"] == "pass" for row in engagement_rows),
        "agent engagement scorecard has non-pass rows",
    )
    require(
        all(row["attack_selection_margin"] for row in engagement_rows),
        "agent engagement scorecard missing attack selection margins",
    )
    require(
        all(row["attack_threshold_margin"] for row in engagement_rows),
        "agent engagement scorecard missing attack threshold margins",
    )
    require(
        all(int(float(row["defense_event_count_in_window"])) > 0 for row in engagement_rows),
        "agent engagement scorecard has rows without defense events",
    )
    require(
        all(row["impact_reduction_from_peak"] for row in engagement_rows),
        "agent engagement scorecard missing impact reduction values",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in engagement_rows),
        "agent engagement scorecard missing safety boundary",
    )
    checks.append("agent_engagement_scorecard rows=10 pass")

    collaboration_rows = read_csv("outputs/report_tables/agent_collaboration_graph.csv")
    require(
        len(collaboration_rows) == 17,
        f"expected 17 collaboration graph edges, got {len(collaboration_rows)}",
    )
    require(
        {row["edge_id"] for row in collaboration_rows}
        == {f"E{index:02d}" for index in range(1, 18)},
        "agent collaboration graph edge ids are incomplete",
    )
    require(
        all(row["validation_status"] == "verified" for row in collaboration_rows),
        "agent collaboration graph has incomplete edges",
    )
    collaboration_sources = {row["source"] for row in collaboration_rows}
    collaboration_targets = {row["target"] for row in collaboration_rows}
    require(
        {"AURA/AURA-ML", "TSRA-R/TSRA-R-ML", "Mission Metrics"}.issubset(
            collaboration_sources | collaboration_targets
        ),
        "agent collaboration graph missing core agent/metric nodes",
    )
    require(
        all("closed simulation" in row["safety_boundary"] for row in collaboration_rows),
        "agent collaboration graph missing safety boundary",
    )
    collaboration_mmd = (ROOT / "outputs/report_tables/agent_collaboration_graph.mmd").read_text(
        encoding="utf-8"
    )
    require("flowchart LR" in collaboration_mmd, "agent collaboration Mermaid graph missing flowchart")
    require("AURA" in collaboration_mmd and "TSRA-R" in collaboration_mmd, "Mermaid graph missing agents")
    checks.append("agent_collaboration_graph edges=17 verified")

    alignment_rows = read_csv("outputs/report_tables/competition_alignment_matrix.csv")
    require(len(alignment_rows) == 10, f"expected 10 alignment rows, got {len(alignment_rows)}")
    incomplete_alignment = [
        row["alignment_id"]
        for row in alignment_rows
        if row.get("evidence_status") != "verified"
    ]
    require(not incomplete_alignment, f"incomplete alignment rows: {incomplete_alignment}")
    required_alignment_areas = {
        "Attack scenario",
        "Defense architecture",
        "AI agent architecture",
        "Attack-defense cooperation",
        "Safety boundary",
    }
    observed_alignment_areas = {row["scoring_area"] for row in alignment_rows}
    require(
        required_alignment_areas.issubset(observed_alignment_areas),
        f"alignment matrix missing required areas: {sorted(required_alignment_areas - observed_alignment_areas)}",
    )
    checks.append("competition_alignment_matrix rows=10 verified")

    return checks


def has_safety_boundary(text: str) -> bool:
    normalized = text.lower()
    return (
        ("closed simulation" in normalized or "simulated effect" in normalized)
        and "no rf" in normalized
        and ("no exploit" in normalized or "no real packet" in normalized)
    )


def check_zip() -> list[str]:
    require(ZIP_PATH.exists(), f"missing package ZIP: {ZIP_PATH.relative_to(ROOT)}")
    require(MANIFEST_PATH.exists(), f"missing package manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        infos = zf.infolist()
        name_list = [info.filename for info in infos]
    names = set(name_list)
    require(len(name_list) == len(names), "package ZIP contains duplicate paths")
    require(name_list == sorted(name_list), "package ZIP entries are not path-sorted")
    non_deterministic_entries = [
        info.filename
        for info in infos
        if info.date_time != EXPECTED_ZIP_TIMESTAMP
        or info.compress_type != zipfile.ZIP_DEFLATED
    ]
    require(
        not non_deterministic_entries,
        f"package ZIP has non-deterministic metadata: {non_deterministic_entries[:8]}",
    )
    for rel in ZIP_REQUIRED_FILES:
        require(rel in names, f"package ZIP missing {rel}")

    excluded_checks: dict[str, Callable[[str], bool]] = {
        "__pycache__": lambda name: "__pycache__" in name,
        "*.pyc": lambda name: name.endswith(".pyc"),
        "outputs/tmp*": lambda name: name.startswith("outputs/tmp"),
        "outputs/datasets/": lambda name: name.startswith("outputs/datasets/"),
        "*.pkl": lambda name: name.endswith(".pkl"),
        "*.pt": lambda name: name.endswith(".pt"),
        "outputs/batch/seed_*": lambda name: name.startswith("outputs/batch/seed_"),
    }
    for label, predicate in excluded_checks.items():
        hits = [name for name in names if predicate(name)]
        require(not hits, f"package ZIP contains excluded {label}: {hits[:3]}")

    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    manifest_zip_path = manifest_value(manifest_text, "zip_path")
    manifest_payload_count = manifest_int(manifest_text, "payload_file_count")
    manifest_zip_file_count = manifest_int(manifest_text, "zip_file_count")
    manifest_zip_bytes = manifest_int(manifest_text, "zip_bytes")
    manifest_zip_sha256 = manifest_value(manifest_text, "zip_sha256")
    manifest_files = manifest_file_list(manifest_text)
    expected_zip_files = manifest_files | {"outputs/package/submission_manifest.md"}
    require(
        manifest_zip_path == ZIP_PATH.relative_to(ROOT).as_posix(),
        f"manifest zip_path mismatch: {manifest_zip_path}",
    )
    require(
        manifest_payload_count == len(manifest_files),
        f"manifest payload_file_count mismatch: {manifest_payload_count} != {len(manifest_files)}",
    )
    require(
        manifest_zip_file_count == len(names),
        f"manifest zip_file_count mismatch: {manifest_zip_file_count} != {len(names)}",
    )
    require(
        manifest_payload_count + 1 == manifest_zip_file_count,
        "manifest payload_file_count and zip_file_count are inconsistent",
    )
    require(
        manifest_zip_bytes == ZIP_PATH.stat().st_size,
        f"manifest zip_bytes mismatch: {manifest_zip_bytes} != {ZIP_PATH.stat().st_size}",
    )
    actual_zip_sha256 = sha256_file(ZIP_PATH)
    require(
        manifest_zip_sha256 == actual_zip_sha256,
        f"manifest zip_sha256 mismatch: {manifest_zip_sha256} != {actual_zip_sha256}",
    )
    require(
        expected_zip_files == names,
        "manifest included-file list does not match package ZIP contents",
    )
    require(
        "outputs/package/release_handoff.md" not in names,
        "release handoff is repo-side only and must not be embedded in the package ZIP",
    )
    handoff_text = (ROOT / "outputs/package/release_handoff.md").read_text(encoding="utf-8")
    require(
        manifest_zip_sha256 in handoff_text,
        "release handoff missing current zip_sha256",
    )
    require(
        str(manifest_zip_bytes) in handoff_text,
        "release handoff missing current zip_bytes",
    )
    require(
        str(manifest_zip_file_count) in handoff_text,
        "release handoff missing current zip_file_count",
    )
    require(
        "not embedded inside the submission ZIP" in handoff_text,
        "release handoff missing repo-side/non-embedded boundary",
    )
    require(
        "- generated_branch: `hbin`" in handoff_text,
        "release handoff missing generated_branch hbin",
    )
    require(
        "Commit SHA is intentionally verified by command after final push" in handoff_text,
        "release handoff missing Git commit verification boundary",
    )
    require(
        "git ls-remote --heads origin main hbin" in handoff_text,
        "release handoff missing remote branch verification command",
    )
    require(
        "python3 scripts/freeze_release_candidate.py --require-clean" in handoff_text,
        "release handoff missing freeze release command",
    )
    require(
        "package_zip_metadata=deterministic" in handoff_text,
        "release handoff missing deterministic ZIP metadata check",
    )
    stale_payload_files = []
    with zipfile.ZipFile(ZIP_PATH) as zf:
        for rel in sorted(manifest_files):
            local_path = ROOT / rel
            require(local_path.exists(), f"manifest payload missing from worktree: {rel}")
            if sha256_file(local_path) != sha256_bytes(zf.read(rel)):
                stale_payload_files.append(rel)
    require(
        not stale_payload_files,
        f"package ZIP payload differs from worktree files: {stale_payload_files[:8]}",
    )
    require("tests/test_agent_regression.py" in manifest_text, "manifest missing agent regression tests")
    require(".github/workflows/quality.yml" in manifest_text, "manifest missing hbin quality workflow")
    require(
        "outputs/report_tables/agent_quality_gate_audit.md" in manifest_text,
        "manifest missing agent quality gate audit",
    )
    require("docs/process/TEAM_HANDOFF.md" in manifest_text, "manifest missing team handoff guide")
    require(
        "outputs/report_tables/team_handoff_audit.md" in manifest_text,
        "manifest missing team handoff audit",
    )
    require("outputs/report_tables/battle_timeline.md" in manifest_text, "manifest missing battle timeline")
    require("outputs/report_tables/incident_summary.md" in manifest_text, "manifest missing incident summary")
    require("outputs/report_tables/operator_alerts.md" in manifest_text, "manifest missing operator alerts")
    require(
        "outputs/report_tables/defense_effectiveness_ledger.md" in manifest_text,
        "manifest missing defense effectiveness ledger",
    )
    require(
        "outputs/report_tables/defense_action_attribution_audit.md" in manifest_text,
        "manifest missing defense action attribution audit",
    )
    require(
        "outputs/report_tables/closed_loop_episode_replay.md" in manifest_text,
        "manifest missing closed-loop episode replay",
    )
    require(
        "outputs/report_tables/agent_coordination_latency_audit.md" in manifest_text,
        "manifest missing agent coordination latency audit",
    )
    require(
        "outputs/report_tables/agent_stress_scenario_audit.md" in manifest_text,
        "manifest missing agent stress scenario audit",
    )
    require(
        "outputs/report_tables/mission_thread_summary.md" in manifest_text,
        "manifest missing mission thread summary",
    )
    require(
        "outputs/report_tables/agent_engagement_scorecard.md" in manifest_text,
        "manifest missing agent engagement scorecard",
    )
    require(
        "outputs/report_tables/agent_collaboration_graph.md" in manifest_text,
        "manifest missing agent collaboration graph",
    )
    require(
        "outputs/report_tables/agent_collaboration_graph.mmd" in manifest_text,
        "manifest missing agent collaboration Mermaid graph",
    )
    require(
        "outputs/report_tables/competition_alignment_matrix.md" in manifest_text,
        "manifest missing competition alignment matrix",
    )
    require(
        "outputs/report_tables/agent_contract_validation.md" in manifest_text,
        "manifest missing agent contract validation",
    )
    require(
        "outputs/report_tables/decision_trace_quality_audit.md" in manifest_text,
        "manifest missing decision trace quality audit",
    )
    require(
        "outputs/report_tables/agent_runtime_invariant_audit.md" in manifest_text,
        "manifest missing agent runtime invariant audit",
    )
    require(
        "outputs/report_tables/agent_loop_replay.md" in manifest_text,
        "manifest missing agent loop replay",
    )
    require(
        "outputs/report_tables/agent_decision_causality_audit.md" in manifest_text,
        "manifest missing agent decision causality audit",
    )
    require(
        "outputs/report_tables/agent_decision_margin_audit.md" in manifest_text,
        "manifest missing agent decision margin audit",
    )
    require(
        "outputs/report_tables/agent_goal_alignment_audit.md" in manifest_text,
        "manifest missing agent goal alignment audit",
    )
    require(
        "outputs/report_tables/agent_decision_feedback_audit.md" in manifest_text,
        "manifest missing agent decision feedback audit",
    )
    require(
        "outputs/report_tables/agent_memory_belief_audit.md" in manifest_text,
        "manifest missing agent memory belief audit",
    )
    require(
        "outputs/report_tables/agent_memory_influence_audit.md" in manifest_text,
        "manifest missing agent memory influence audit",
    )
    require(
        "outputs/report_tables/aura_attack_decision_path_audit.md" in manifest_text,
        "manifest missing AURA attack decision path audit",
    )
    require(
        "outputs/report_tables/cross_agent_context_audit.md" in manifest_text,
        "manifest missing cross-agent context audit",
    )
    require(
        "outputs/report_tables/defense_priority_decision_path_audit.md" in manifest_text,
        "manifest missing defense priority decision path audit",
    )
    require(
        "outputs/report_tables/agent_tool_usage_audit.md" in manifest_text,
        "manifest missing agent tool usage audit",
    )
    require(
        "outputs/report_tables/agent_interface_manifest.md" in manifest_text,
        "manifest missing agent interface manifest",
    )
    require(
        "outputs/report_tables/agent_capability_matrix.md" in manifest_text,
        "manifest missing agent capability matrix",
    )
    require(
        "outputs/report_tables/attack_defense_coverage.md" in manifest_text,
        "manifest missing attack-defense coverage",
    )
    require(
        "outputs/report_tables/attack_defense_response_audit.md" in manifest_text,
        "manifest missing attack-defense response audit",
    )
    require(
        "outputs/report_tables/pace_transition_audit.md" in manifest_text,
        "manifest missing PACE transition audit",
    )
    require(
        "outputs/report_tables/mission_impact_decomposition.md" in manifest_text,
        "manifest missing mission impact decomposition",
    )
    require(
        "outputs/report_tables/metric_gate_summary.md" in manifest_text,
        "manifest missing metric gate summary",
    )
    require(
        "outputs/report_tables/ml_contribution_audit.md" in manifest_text,
        "manifest missing ML contribution audit",
    )
    require(
        "outputs/report_tables/ml_attack_decision_path_audit.md" in manifest_text,
        "manifest missing ML attack decision path audit",
    )
    require(
        "outputs/report_tables/ml_defense_decision_path_audit.md" in manifest_text,
        "manifest missing ML defense decision path audit",
    )
    require(
        "outputs/report_tables/ml_red_blue_interaction_audit.md" in manifest_text,
        "manifest missing ML red-blue interaction audit",
    )
    require(
        "outputs/report_tables/reactive_defense_tradeoff_audit.md" in manifest_text,
        "manifest missing reactive defense tradeoff audit",
    )
    require(
        "outputs/batch/ml_threshold_sweep_summary.csv" in manifest_text,
        "manifest missing ML threshold sweep summary",
    )
    require(
        "outputs/report_tables/ml_threshold_sweep.md" in manifest_text,
        "manifest missing ML threshold sweep report",
    )
    require(
        "outputs/report_tables/tsra_detector_calibration_audit.md" in manifest_text,
        "manifest missing TSRA detector calibration audit",
    )
    require(
        "outputs/report_tables/tsra_detector_calibration_bins.csv" in manifest_text,
        "manifest missing TSRA detector calibration bins",
    )
    require(
        "outputs/report_tables/safety_boundary_audit.md" in manifest_text,
        "manifest missing safety boundary audit",
    )
    require(
        "outputs/report_tables/reproduction_order_audit.md" in manifest_text,
        "manifest missing reproduction order audit",
    )
    require(
        "outputs/report_tables/submission_readiness_audit.md" in manifest_text,
        "manifest missing submission readiness audit",
    )
    return [
        f"package_zip entries={len(names)}",
        "package_manifest_integrity=passed",
        "package_zip_metadata=deterministic",
        "release_handoff=repo-only/current",
        "package exclusions=passed",
    ]


def check_git_state(require_clean: bool) -> list[str]:
    checks = []
    branch = run(["git", "branch", "--show-current"])
    require(branch == "hbin", f"expected branch hbin, got {branch}")
    checks.append("branch=hbin")

    refs = run(["git", "ls-remote", "--heads", "origin", "main", "hbin"])
    require("refs/heads/main" in refs, "origin/main is missing")
    require("refs/heads/hbin" in refs, "origin/hbin is missing")
    checks.append("origin main/hbin refs=present")

    if require_clean:
        status = run(["git", "status", "--short"])
        tracked_dirty = [
            line
            for line in status.splitlines()
            if line and not line.startswith("?? ") and "outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip" not in line
        ]
        require(not tracked_dirty, f"tracked working tree is dirty: {tracked_dirty[:8]}")
        checks.append("tracked_worktree=clean")
    return checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify final DAH submission state.")
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Fail when tracked files have uncommitted changes.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checks = []
    checks.extend(check_required_files())
    checks.extend(check_regression_tests())
    checks.extend(check_csv_outputs())
    checks.extend(check_zip())
    checks.extend(check_git_state(require_clean=args.require_clean))
    print("Submission state verification passed")
    for item in checks:
        print(f"- {item}")


if __name__ == "__main__":
    main()
