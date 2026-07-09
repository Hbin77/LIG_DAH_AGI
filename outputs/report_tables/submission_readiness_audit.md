# Submission Readiness Audit

This audit checks whether the shared hbin branch has enough reproducible evidence for teammate handoff and final packaging.

Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

| check_id | area | status | observed | handoff_value |
|---|---|---|---|---|
| R01 | Branch policy | pass | origin/main=True; origin/hbin=True; readme_no_main_push=True; workflow_mentions_hbin=True | A teammate can clone the repo and know that active work is on hbin while main stays protected. |
| R02 | Reproduction commands | pass | python3 -m src.ml.build_dataset=yes, python3 -m src.experiments.run_all=yes, python3 -m src.experiments.agent_runtime_invariant_audit=yes, python3 -m src.experiments.agent_decision_causality_audit=yes, python3 -m src.experiments.agent_decision_margin_audit=yes, python3 -m src.experiments.agent_goal_alignment_audit --fail-on-error=yes, python3 -m src.experiments.agent_decision_feedback_audit --fail-on-error=yes, python3 -m src.experiments.agent_memory_influence_audit --fail-on-error=yes, python3 -m src.experiments.defense_action_attribution_audit --fail-on-error=yes, python3 -m src.experiments.mission_thread_summary --fail-on-error=yes, python3 -m src.experiments.safety_boundary_audit=yes, python3 -m src.experiments.run_batch=yes, python3 scripts/build_submission_package.py=yes, python3 scripts/verify_submission_state.py=yes, python3 -m src.experiments.ml_contribution_audit --fail-on-error=yes, python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error=yes, python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error=yes, python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error=yes, python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error=yes, python3 -m src.experiments.reactive_defense_tradeoff_audit --fail-on-error=yes, python3 -m src.experiments.run_ml_threshold_sweep=yes, python3 -m src.experiments.tsra_detector_calibration_audit --fail-on-error=yes, python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error=yes, python3 -m src.experiments.reproduction_order_audit --fail-on-error=yes; reproduction_order_rows=13 | The next developer can rebuild the same evidence without reverse-engineering command order. |
| R03 | Agent runtime structure | pass | runtime_files_present=True; interface_rows=4; runtime_invariant_rows=9 | The agent claim is backed by code modules and generated interface evidence. |
| R04 | Attack and defense separation | pass | agent_files_present=True; capability_rows=10; coverage_rows=4; response_rows=10 | Attack-side and defense-side work can be assigned separately without losing interface coverage. |
| R05 | Decision evidence | pass | trace=215, contract=49, quality=9, runtime=9, loop=8, causality=399, margin=399, goal_alignment=399, feedback=66, memory=9, memory_influence=6, tool=23 | Agent decisions remain explainable by generated evidence, not only by source code. |
| R06 | Closed-loop evidence | pass | battle=49, incident=10, alerts=56, ledger=56, attribution=5, episode=10, coordination_latency=10, stress=6, mission_thread=10, scorecard=10 | The red/blue loop can be reviewed as mission threads, stress scenarios, episodes, coordination latencies, actions, alerts, metric movement, and action-level attribution. |
| R07 | Metric and ML evidence | pass | repeated=7, resilience=4, ablation=5, adaptive=2, decomposition=35, gates=11, ml_contribution=7, ml_attack_path=6, ml_defense_path=6, ml_interaction=5, reactive_tradeoff=7, threshold_sweep=5, detector_calibration=6; model_metric_files=3 | Quantitative and ML-agent claims are backed by batch, ablation, adaptive, gate, model metric, ML contribution, ML attack decision-path, ML defense decision-path, ML red-blue interaction, reactive tradeoff, threshold tuning, and detector calibration artifacts. |
| R08 | Package inputs | pass | package_inputs_present=True; existing_manifest_has_zip_sha256=True; zip_ignored=True | The source ZIP can be regenerated locally without committing the binary ZIP file. |
| R09 | Safety boundary | pass | readme_sim_boundary=True; safety_audit_rows=5; coa_no_rf=True; coa_no_exploit=True; incident_closed_sim=True; graph_closed_sim=True | The project remains a simulated mission-impact prototype, not operational offensive tooling. |
| R10 | Team handoff docs | pass | process_docs_present=True; next_queue_has_p42=True; forbidden_team_phrases=0 | A teammate can continue from the queue and logs without inheriting personal-only wording. |

## Detail

### R01 Branch policy

- Requirement: Keep main preserved and use hbin as the shared development branch.
- Evidence: README.md | docs/process/GITHUB_WORKFLOW.md | git ls-remote origin main hbin
- Observed: origin/main=True; origin/hbin=True; readme_no_main_push=True; workflow_mentions_hbin=True
- Status: pass
- Handoff value: A teammate can clone the repo and know that active work is on hbin while main stays protected.
- Next gate: Final verifier must be run from branch hbin before any handoff.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R02 Reproduction commands

- Requirement: README must contain the end-to-end commands needed to regenerate core evidence, and the command order audit must pass.
- Evidence: README.md | outputs/report_tables/reproduction_order_audit.csv
- Observed: python3 -m src.ml.build_dataset=yes, python3 -m src.experiments.run_all=yes, python3 -m src.experiments.agent_runtime_invariant_audit=yes, python3 -m src.experiments.agent_decision_causality_audit=yes, python3 -m src.experiments.agent_decision_margin_audit=yes, python3 -m src.experiments.agent_goal_alignment_audit --fail-on-error=yes, python3 -m src.experiments.agent_decision_feedback_audit --fail-on-error=yes, python3 -m src.experiments.agent_memory_influence_audit --fail-on-error=yes, python3 -m src.experiments.defense_action_attribution_audit --fail-on-error=yes, python3 -m src.experiments.mission_thread_summary --fail-on-error=yes, python3 -m src.experiments.safety_boundary_audit=yes, python3 -m src.experiments.run_batch=yes, python3 scripts/build_submission_package.py=yes, python3 scripts/verify_submission_state.py=yes, python3 -m src.experiments.ml_contribution_audit --fail-on-error=yes, python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error=yes, python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error=yes, python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error=yes, python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error=yes, python3 -m src.experiments.reactive_defense_tradeoff_audit --fail-on-error=yes, python3 -m src.experiments.run_ml_threshold_sweep=yes, python3 -m src.experiments.tsra_detector_calibration_audit --fail-on-error=yes, python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error=yes, python3 -m src.experiments.reproduction_order_audit --fail-on-error=yes; reproduction_order_rows=13
- Status: pass
- Handoff value: The next developer can rebuild the same evidence without reverse-engineering command order.
- Next gate: Any new experiment generator must be added to the Full Reproduction block.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R03 Agent runtime structure

- Requirement: Agent Runtime, Memory, Tool, and DecisionTrace assets must be present and evidenced.
- Evidence: src/agents/runtime.py | src/agents/memory.py | src/agents/tools.py | src/agents/schema.py | docs/agents/AGENT_RUNTIME.md | outputs/report_tables/agent_interface_manifest.csv
- Observed: runtime_files_present=True; interface_rows=4; runtime_invariant_rows=9
- Status: pass
- Handoff value: The agent claim is backed by code modules and generated interface evidence.
- Next gate: Runtime changes must regenerate runtime invariant, interface, memory, tool, and causality audits.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R04 Attack and defense separation

- Requirement: AURA and TSRA-R must be independently inspectable with capability coverage between them.
- Evidence: src/aura/rule_decision_engine.py | src/aura/candidate_generator.py | src/aura/impact_estimator.py | src/tsra_r/rule_defender.py | src/tsra_r/ml_defender.py | src/tsra_r/adaptive_defender.py | docs/agents/AURA_ATTACK_AGENT.md | docs/agents/TSRA_R_DEFENSE_AGENT.md | outputs/report_tables/agent_capability_matrix.csv | outputs/report_tables/attack_defense_coverage.csv | outputs/report_tables/attack_defense_response_audit.csv
- Observed: agent_files_present=True; capability_rows=10; coverage_rows=4; response_rows=10
- Status: pass
- Handoff value: Attack-side and defense-side work can be assigned separately without losing interface coverage.
- Next gate: New attack capability must declare the matching defense capability and response audit gate.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R05 Decision evidence

- Requirement: DecisionTrace, contract, causality, margin, goal alignment, feedback, memory, memory influence, and tool evidence must all be generated.
- Evidence: outputs/report_tables/agent_decision_trace_summary.csv | outputs/report_tables/agent_contract_validation.csv | outputs/report_tables/decision_trace_quality_audit.csv | outputs/report_tables/agent_runtime_invariant_audit.csv | outputs/report_tables/agent_loop_replay.csv | outputs/report_tables/agent_decision_causality_audit.csv | outputs/report_tables/agent_decision_margin_audit.csv | outputs/report_tables/agent_goal_alignment_audit.csv | outputs/report_tables/agent_decision_feedback_audit.csv | outputs/report_tables/agent_memory_belief_audit.csv | outputs/report_tables/agent_memory_influence_audit.csv | outputs/report_tables/agent_tool_usage_audit.csv
- Observed: trace=215, contract=49, quality=9, runtime=9, loop=8, causality=399, margin=399, goal_alignment=399, feedback=66, memory=9, memory_influence=6, tool=23
- Status: pass
- Handoff value: Agent decisions remain explainable by generated evidence, not only by source code.
- Next gate: Policy changes must keep causality, margin, goal alignment, memory, and tool evidence passing final verification.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R06 Closed-loop evidence

- Requirement: Attack, defense, alerts, effectiveness, action attribution, coordination latency, stress scenario, mission thread, replay, and collaboration evidence must be present.
- Evidence: outputs/report_tables/battle_timeline.csv | outputs/report_tables/incident_summary.csv | outputs/report_tables/operator_alerts.csv | outputs/report_tables/defense_effectiveness_ledger.csv | outputs/report_tables/defense_action_attribution_audit.csv | outputs/report_tables/closed_loop_episode_replay.csv | outputs/report_tables/agent_coordination_latency_audit.csv | outputs/report_tables/agent_stress_scenario_audit.csv | outputs/report_tables/mission_thread_summary.csv | outputs/report_tables/agent_engagement_scorecard.csv | src/experiments/agent_collaboration_graph.py
- Observed: battle=49, incident=10, alerts=56, ledger=56, attribution=5, episode=10, coordination_latency=10, stress=6, mission_thread=10, scorecard=10
- Status: pass
- Handoff value: The red/blue loop can be reviewed as mission threads, stress scenarios, episodes, coordination latencies, actions, alerts, metric movement, and action-level attribution.
- Next gate: New closed-loop outputs must connect attack event, defense event, and metric evidence.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R07 Metric and ML evidence

- Requirement: Repeated metrics, action ablation, adaptive memory, decomposition, gates, ML contribution, ML attack path, ML defense path, ML red-blue interaction, reactive tradeoff, threshold tuning, detector calibration, and ML metrics must exist.
- Evidence: outputs/batch/repeated_experiment_summary.csv | outputs/batch/resilience_gain_summary.csv | outputs/batch/tsra_action_ablation_summary.csv | outputs/batch/adaptive_memory_summary.csv | outputs/batch/ml_threshold_sweep_summary.csv | outputs/report_tables/mission_impact_decomposition.csv | outputs/report_tables/metric_gate_summary.csv | outputs/report_tables/ml_contribution_audit.csv | outputs/report_tables/ml_attack_decision_path_audit.csv | outputs/report_tables/ml_defense_decision_path_audit.csv | outputs/report_tables/ml_red_blue_interaction_audit.csv | outputs/report_tables/reactive_defense_tradeoff_audit.csv | outputs/report_tables/ml_threshold_sweep.csv | outputs/report_tables/tsra_detector_calibration_audit.csv | outputs/models/aura_impact_model_metrics.json | outputs/models/tsra_detector_metrics.json | outputs/models/aura_mps_mlp_metrics.json
- Observed: repeated=7, resilience=4, ablation=5, adaptive=2, decomposition=35, gates=11, ml_contribution=7, ml_attack_path=6, ml_defense_path=6, ml_interaction=5, reactive_tradeoff=7, threshold_sweep=5, detector_calibration=6; model_metric_files=3
- Status: pass
- Handoff value: Quantitative and ML-agent claims are backed by batch, ablation, adaptive, gate, model metric, ML contribution, ML attack decision-path, ML defense decision-path, ML red-blue interaction, reactive tradeoff, threshold tuning, and detector calibration artifacts.
- Next gate: Metric or ML-agent changes must update metric gates, ML contribution audit, ML attack path audit, ML defense path audit, ML red-blue interaction audit, reactive tradeoff audit, threshold sweep, detector calibration, and package manifest before push.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R08 Package inputs

- Requirement: Package builder, freeze script, final verifier, external-link verifier, and Git ignore rules must be present before packaging.
- Evidence: scripts/build_submission_package.py | scripts/freeze_release_candidate.py | scripts/generate_release_handoff.py | scripts/verify_submission_state.py | scripts/verify_external_package_link.py | src/experiments/reproduction_order_audit.py | .gitignore
- Observed: package_inputs_present=True; existing_manifest_has_zip_sha256=True; zip_ignored=True
- Status: pass
- Handoff value: The source ZIP can be regenerated locally without committing the binary ZIP file.
- Next gate: Run build_submission_package.py and verify_submission_state.py after adding any source, doc, table, or figure artifact.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R09 Safety boundary

- Requirement: Core user-facing artifacts must state the closed simulation boundary.
- Evidence: README.md | outputs/report_tables/safety_boundary_audit.csv | outputs/report_tables/aura_coa_cards.csv | outputs/report_tables/incident_summary.csv | outputs/report_tables/agent_collaboration_graph.csv
- Observed: readme_sim_boundary=True; safety_audit_rows=5; coa_no_rf=True; coa_no_exploit=True; incident_closed_sim=True; graph_closed_sim=True
- Status: pass
- Handoff value: The project remains a simulated mission-impact prototype, not operational offensive tooling.
- Next gate: Reject changes that add RF parameters, exploit steps, or live packet/network actions.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action

### R10 Team handoff docs

- Requirement: Process docs must preserve the team workflow and avoid personal-only wording.
- Evidence: docs/process/GITHUB_WORKFLOW.md | docs/process/COMPETITION_DIRECTION.md | docs/process/NEXT_DEVELOPMENT_QUEUE.md | docs/process/DEVELOPMENT_LOG.md | docs/process/FINAL_QA.md | docs/process/SUBMISSION_PACKAGE.md
- Observed: process_docs_present=True; next_queue_has_p42=True; forbidden_team_phrases=0
- Status: pass
- Handoff value: A teammate can continue from the queue and logs without inheriting personal-only wording.
- Next gate: Each substantial change must update the queue, development log, verifier, and hbin branch.
- Safety boundary: closed simulation readiness audit only; no RF, exploit, or live network action
