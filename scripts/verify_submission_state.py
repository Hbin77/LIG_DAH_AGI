from __future__ import annotations

import argparse
import csv
import subprocess
import zipfile
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "outputs" / "package" / "DAH2026_source_LIG_DAH_AGI.zip"
MANIFEST_PATH = ROOT / "outputs" / "package" / "submission_manifest.md"

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "scripts/build_submission_package.py",
    "scripts/verify_submission_state.py",
    "docs/process/COMPETITION_DIRECTION.md",
    "docs/process/NEXT_DEVELOPMENT_QUEUE.md",
    "docs/process/DEVELOPMENT_LOG.md",
    "docs/process/FINAL_QA.md",
    "docs/process/SUBMISSION_PACKAGE.md",
    "src/agents/runtime.py",
    "src/aura/rule_decision_engine.py",
    "src/tsra_r/rule_defender.py",
    "src/tsra_r/adaptive_defender.py",
    "src/experiments/battle_timeline.py",
    "src/experiments/incident_summary.py",
    "src/experiments/operator_alerts.py",
    "src/experiments/defense_effectiveness_ledger.py",
    "src/experiments/closed_loop_episode_replay.py",
    "src/experiments/agent_collaboration_graph.py",
    "src/experiments/competition_alignment.py",
    "src/experiments/validate_event_contracts.py",
    "src/experiments/trace_quality_audit.py",
    "src/experiments/agent_loop_replay.py",
    "src/experiments/agent_memory_belief_audit.py",
    "src/experiments/agent_tool_usage_audit.py",
    "src/experiments/agent_interface_manifest.py",
    "src/experiments/agent_capability_matrix.py",
    "src/experiments/attack_defense_coverage.py",
    "src/experiments/attack_defense_response_audit.py",
    "src/experiments/pace_transition_audit.py",
    "src/experiments/mission_impact_decomposition.py",
    "src/experiments/metric_gate.py",
    "outputs/experiments/experiment_summary.csv",
    "outputs/batch/repeated_experiment_summary.csv",
    "outputs/batch/resilience_gain_summary.csv",
    "outputs/batch/tsra_action_ablation_summary.csv",
    "outputs/batch/adaptive_memory_summary.csv",
    "outputs/report_tables/agent_decision_trace_summary.csv",
    "outputs/report_tables/aura_coa_cards.csv",
    "outputs/report_tables/battle_timeline.csv",
    "outputs/report_tables/incident_summary.csv",
    "outputs/report_tables/operator_alerts.csv",
    "outputs/report_tables/operator_alerts.md",
    "outputs/report_tables/defense_effectiveness_ledger.csv",
    "outputs/report_tables/defense_effectiveness_ledger.md",
    "outputs/report_tables/closed_loop_episode_replay.csv",
    "outputs/report_tables/closed_loop_episode_replay.md",
    "outputs/report_tables/agent_collaboration_graph.csv",
    "outputs/report_tables/agent_collaboration_graph.md",
    "outputs/report_tables/agent_collaboration_graph.mmd",
    "outputs/report_tables/competition_alignment_matrix.csv",
    "outputs/report_tables/competition_alignment_matrix.md",
    "outputs/report_tables/agent_contract_validation.csv",
    "outputs/report_tables/agent_contract_validation.md",
    "outputs/report_tables/decision_trace_quality_audit.csv",
    "outputs/report_tables/decision_trace_quality_audit.md",
    "outputs/report_tables/agent_loop_replay.csv",
    "outputs/report_tables/agent_loop_replay.md",
    "outputs/report_tables/agent_memory_belief_audit.csv",
    "outputs/report_tables/agent_memory_belief_audit.md",
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
    "outputs/figures/aura_tsra_architecture.png",
    "outputs/figures/batch_resilience_gain.png",
    "outputs/figures/tsra_action_ablation.png",
    "outputs/figures/adaptive_memory_comparison.png",
    "outputs/models/aura_impact_model_metrics.json",
    "outputs/models/tsra_detector_metrics.json",
]

ZIP_REQUIRED_FILES = REQUIRED_FILES + [
    "outputs/package/submission_manifest.md",
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


def check_required_files() -> list[str]:
    checked = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        require(path.exists(), f"missing required file: {rel}")
        require(path.stat().st_size > 0, f"empty required file: {rel}")
        checked.append(rel)
    return checked


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
    require(len(trace_rows) >= 200, f"trace summary too small: {len(trace_rows)} rows")
    checks.append(f"agent_decision_trace_summary rows={len(trace_rows)}")

    contract_rows = read_csv("outputs/report_tables/agent_contract_validation.csv")
    require(len(contract_rows) == 49, f"expected 49 contract checks, got {len(contract_rows)}")
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
        "agent_cross_contract",
    }
    observed_contracts = {row["contract"] for row in contract_rows}
    require(
        required_contracts.issubset(observed_contracts),
        f"agent contract validation missing contracts: {sorted(required_contracts - observed_contracts)}",
    )
    checks.append("agent_contract_validation rows=49 pass")

    trace_quality_rows = read_csv("outputs/report_tables/decision_trace_quality_audit.csv")
    require(
        len(trace_quality_rows) == 9,
        f"expected 9 trace quality audit rows, got {len(trace_quality_rows)}",
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
    checks.append("decision_trace_quality_audit rows=9 pass")

    replay_rows = read_csv("outputs/report_tables/agent_loop_replay.csv")
    require(len(replay_rows) == 8, f"expected 8 agent loop replay rows, got {len(replay_rows)}")
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
    checks.append("agent_loop_replay rows=8 agents/cases=complete")

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

    tool_rows = read_csv("outputs/report_tables/agent_tool_usage_audit.csv")
    require(len(tool_rows) == 23, f"expected 23 agent tool audit rows, got {len(tool_rows)}")
    failed_tool_rows = [
        f"{row['experiment']}:{row['agent']}:{row['tool_name']}"
        for row in tool_rows
        if row.get("status") != "pass"
    ]
    require(not failed_tool_rows, f"failed agent tool audit rows: {failed_tool_rows[:8]}")
    expected_tools = {
        "estimate_candidate_effect",
        "estimate_detectability",
        "evaluate_defense_conditions",
        "generate_attack_candidates",
        "predict_attack_probability",
        "predict_candidate_impact",
        "select_fallback_link",
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
    checks.append("agent_tool_usage_audit rows=23 pass")

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
    checks.append("agent_interface_manifest rows=4 agents=attack/defense")

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
    require(len(pace_rows) == 6, f"expected 6 PACE transition audit rows, got {len(pace_rows)}")
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
        pace_status_counts == {"satcom_to_fallback": 2, "fallback_reselect": 4},
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
    checks.append("pace_transition_audit rows=6 status=2 initial/4 fallback")

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
    require(len(metric_gate_rows) == 11, f"expected 11 metric gate rows, got {len(metric_gate_rows)}")
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
    }
    observed_metric_gate_areas = {row["area"] for row in metric_gate_rows}
    require(
        required_metric_gate_areas.issubset(observed_metric_gate_areas),
        f"metric gate missing required areas: {sorted(required_metric_gate_areas - observed_metric_gate_areas)}",
    )
    checks.append("metric_gate_summary rows=11 pass")

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
    require(len(alert_rows) == 56, f"expected 56 operator alert rows, got {len(alert_rows)}")
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
    checks.append("operator_alerts rows=56 actions=5")

    ledger_rows = read_csv("outputs/report_tables/defense_effectiveness_ledger.csv")
    require(
        len(ledger_rows) == 56,
        f"expected 56 defense effectiveness ledger rows, got {len(ledger_rows)}",
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
    checks.append("defense_effectiveness_ledger rows=56 actions=5")

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

    collaboration_rows = read_csv("outputs/report_tables/agent_collaboration_graph.csv")
    require(
        len(collaboration_rows) == 15,
        f"expected 15 collaboration graph edges, got {len(collaboration_rows)}",
    )
    require(
        {row["edge_id"] for row in collaboration_rows}
        == {f"E{index:02d}" for index in range(1, 16)},
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
    checks.append("agent_collaboration_graph edges=15 verified")

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
        names = set(zf.namelist())
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
    require("zip_sha256" in manifest_text, "manifest missing zip_sha256")
    require("outputs/report_tables/battle_timeline.md" in manifest_text, "manifest missing battle timeline")
    require("outputs/report_tables/incident_summary.md" in manifest_text, "manifest missing incident summary")
    require("outputs/report_tables/operator_alerts.md" in manifest_text, "manifest missing operator alerts")
    require(
        "outputs/report_tables/defense_effectiveness_ledger.md" in manifest_text,
        "manifest missing defense effectiveness ledger",
    )
    require(
        "outputs/report_tables/closed_loop_episode_replay.md" in manifest_text,
        "manifest missing closed-loop episode replay",
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
        "outputs/report_tables/agent_loop_replay.md" in manifest_text,
        "manifest missing agent loop replay",
    )
    require(
        "outputs/report_tables/agent_memory_belief_audit.md" in manifest_text,
        "manifest missing agent memory belief audit",
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
    return [f"package_zip entries={len(names)}", "package exclusions=passed"]


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
            if line and not line.startswith("?? ") and "outputs/package/DAH2026_source_LIG_DAH_AGI.zip" not in line
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
    checks.extend(check_csv_outputs())
    checks.extend(check_zip())
    checks.extend(check_git_state(require_clean=args.require_clean))
    print("Submission state verification passed")
    for item in checks:
        print(f"- {item}")


if __name__ == "__main__":
    main()
