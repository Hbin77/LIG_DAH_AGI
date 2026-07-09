# Competition Alignment Matrix

This matrix keeps the implementation tied to the DAH preliminary-round direction.
Each row maps a competition goal to concrete code, generated evidence, and the next development gate.

| alignment_id | scoring_area | agent_or_component | evidence_status | next_gate |
| --- | --- | --- | --- | --- |
| A01 | Defense mission grounding | MissionSimulator / scenario docs | verified | Any new feature must map to SATCOM, C4ISR, COP, PACE, or critical traffic. |
| A02 | Attack scenario | AURA | verified | Attack improvements must produce COA cards and never introduce live RF, exploit, or packet actions. |
| A03 | Defense architecture | TSRA-R | verified | Defense changes must be checked against mission impact plus at least one action-specific metric. |
| A04 | AI agent architecture | AgentRuntime / AgentMemory / ToolRegistry / DecisionTrace | verified | Agent changes must keep attack/defense interfaces and capabilities explicit. |
| A05 | Attack-defense cooperation | Battle timeline / Incident summary / Coverage / Response audit / Episode replay / Engagement scorecard / Collaboration graph | verified | New experiments must preserve attack events, defense events, trace reasons, metric snapshots, attack-to-defense capability coverage, and required response timing. |
| A06 | ML contribution | AURA ML / TSRA-R ML | verified | ML claims must state task, metric, model role, and whether the model changes closed-loop behavior. |
| A07 | Repeatable evidence | Experiment runners | verified | Metric claims must pass metric_gate_summary and point to batch or dedicated experiments. |
| A08 | Adaptive defense | AdaptiveTSRA-R | verified | Adaptive changes must be isolated from E1-E7 baseline and checked in adaptive_memory_summary. |
| A09 | Safety boundary | Safety guardrails | verified | Reject any change that adds operational RF parameters, exploit code, or live network actions. |
| A10 | Team handoff and reproducibility | README / packaging / QA scripts | verified | Before handoff, rebuild the package and run verify_submission_state on branch hbin. |

## Evidence Detail

### A01 Defense mission grounding

- Goal: Show a realistic defense mission environment instead of a generic IT scenario.
- Mechanism: Hybrid SATCOM disruption is modeled as C4ISR data-trust degradation: critical latency, stale COP, priority inversion, and trusted stale exposure.
- Evidence: docs/DAH2026_TSRA_v3_realistic_attack_rewrite.md | src/simulator/mission_simulator.py | outputs/figures/aura_tsra_architecture.png
- Status: verified
- Notes: all evidence files present
- Next gate: Any new feature must map to SATCOM, C4ISR, COP, PACE, or critical traffic.

### A02 Attack scenario

- Goal: Make the attack technically concrete while staying inside a safe simulation boundary.
- Mechanism: AURA generates attack-effect candidates, estimates mission impact and detectability, then emits simulated AttackEvent records.
- Evidence: src/aura/candidate_generator.py | src/aura/impact_estimator.py | src/aura/rule_decision_engine.py | outputs/report_tables/aura_coa_cards.csv
- Status: verified
- Notes: outputs/report_tables/aura_coa_cards.csv rows=15
- Next gate: Attack improvements must produce COA cards and never introduce live RF, exploit, or packet actions.

### A03 Defense architecture

- Goal: Tie detection, blocking, and recovery directly to the AURA attack effects.
- Mechanism: TSRA-R selects priority reroute, stale badge, video throttle, and PACE switch actions; ablation isolates which action protects which mission metric, and PACE transition audit explains fallback switching context; operator alerts translate DefenseEvent records into mission-readable response guidance; defense effectiveness ledger joins each DefenseEvent to local before/after mission metric movement; action attribution audit aggregates those windows by defense action and separates ablation-supported, local-metric, reactive-window, and bounded-tradeoff evidence.
- Evidence: src/tsra_r/rule_defender.py | src/tsra_r/ml_defender.py | src/tsra_r/adaptive_defender.py | src/experiments/pace_transition_audit.py | src/experiments/operator_alerts.py | src/experiments/defense_effectiveness_ledger.py | src/experiments/defense_action_attribution_audit.py | outputs/batch/tsra_action_ablation_summary.csv | outputs/report_tables/pace_transition_audit.csv | outputs/report_tables/operator_alerts.csv | outputs/report_tables/defense_effectiveness_ledger.csv | outputs/report_tables/defense_action_attribution_audit.csv
- Status: verified
- Notes: outputs/batch/tsra_action_ablation_summary.csv rows=5; outputs/report_tables/pace_transition_audit.csv rows=6; outputs/report_tables/operator_alerts.csv rows=56; outputs/report_tables/defense_effectiveness_ledger.csv rows=56; outputs/report_tables/defense_action_attribution_audit.csv rows=5
- Next gate: Defense changes must be checked against mission impact plus at least one action-specific metric.

### A04 AI agent architecture

- Goal: Show agent structure beyond direct Python policy calls.
- Mechanism: AgentRuntime wraps observe, memory summary, tool calls, candidate scoring, selected action, DecisionTrace, and feedback updates; memory belief audit verifies evolving belief state and previous-action carryover across decision loops; tool usage audit verifies actual tool invocations with input and output summaries; causality audit verifies selected actions against candidate, tool, and score/threshold evidence; margin audit records top-score, threshold, eligible-ready, and no-op decision support; goal-alignment audit checks that attack and defense decisions match their stated objectives and observed risks.
- Evidence: src/agents/runtime.py | src/agents/memory.py | src/agents/tools.py | src/agents/schema.py | src/experiments/validate_event_contracts.py | src/experiments/trace_quality_audit.py | src/experiments/agent_loop_replay.py | src/experiments/agent_decision_causality_audit.py | src/experiments/agent_decision_margin_audit.py | src/experiments/agent_goal_alignment_audit.py | src/experiments/agent_memory_belief_audit.py | src/experiments/agent_tool_usage_audit.py | src/experiments/agent_interface_manifest.py | src/experiments/agent_capability_matrix.py | outputs/report_tables/agent_decision_trace_summary.csv | outputs/report_tables/agent_contract_validation.csv | outputs/report_tables/decision_trace_quality_audit.csv | outputs/report_tables/agent_loop_replay.csv | outputs/report_tables/agent_decision_causality_audit.csv | outputs/report_tables/agent_decision_margin_audit.csv | outputs/report_tables/agent_goal_alignment_audit.csv | outputs/report_tables/agent_memory_belief_audit.csv | outputs/report_tables/agent_tool_usage_audit.csv | outputs/report_tables/agent_interface_manifest.csv | outputs/report_tables/agent_capability_matrix.csv
- Status: verified
- Notes: outputs/report_tables/agent_decision_trace_summary.csv rows=215; outputs/report_tables/agent_contract_validation.csv rows=49; outputs/report_tables/decision_trace_quality_audit.csv rows=9; outputs/report_tables/agent_loop_replay.csv rows=8; outputs/report_tables/agent_decision_causality_audit.csv rows=399; outputs/report_tables/agent_decision_margin_audit.csv rows=399; outputs/report_tables/agent_goal_alignment_audit.csv rows=399; outputs/report_tables/agent_memory_belief_audit.csv rows=9; outputs/report_tables/agent_tool_usage_audit.csv rows=23; outputs/report_tables/agent_interface_manifest.csv rows=4; outputs/report_tables/agent_capability_matrix.csv rows=10
- Next gate: Agent changes must keep attack/defense interfaces and capabilities explicit.

### A05 Attack-defense cooperation

- Goal: Make the red and blue agents observable and explicitly connected by capability coverage.
- Mechanism: Battle timeline and incident summary merge AURA events, TSRA-R events, trace reasons, and metric movement for E5 and E7; attack-defense coverage maps each AURA capability to the TSRA-R capabilities and validation gates that cover it; response audit checks whether required defenses are active or emitted within the response window; the collaboration graph summarizes the closed-loop agent cooperation evidence; episode replay joins attack, defense, alert, and metric movement per attack event; the defense effectiveness ledger adds event-level response-to-metric movement evidence; engagement scorecard joins attack decision margin, defense response, and mission-impact movement per attack; defense action attribution summarizes which defense actions have direct ablation support, local metric support, reactive-window support, or bounded tradeoff behavior.
- Evidence: src/experiments/battle_timeline.py | src/experiments/incident_summary.py | src/experiments/closed_loop_episode_replay.py | src/experiments/agent_engagement_scorecard.py | src/experiments/defense_effectiveness_ledger.py | src/experiments/defense_action_attribution_audit.py | src/experiments/agent_collaboration_graph.py | src/experiments/attack_defense_coverage.py | src/experiments/attack_defense_response_audit.py | outputs/report_tables/battle_timeline.csv | outputs/report_tables/incident_summary.csv | outputs/report_tables/closed_loop_episode_replay.csv | outputs/report_tables/agent_engagement_scorecard.csv | outputs/report_tables/defense_effectiveness_ledger.csv | outputs/report_tables/defense_action_attribution_audit.csv | outputs/report_tables/agent_collaboration_graph.csv | outputs/report_tables/attack_defense_coverage.csv | outputs/report_tables/attack_defense_response_audit.csv
- Status: verified
- Notes: outputs/report_tables/battle_timeline.csv rows=49; outputs/report_tables/incident_summary.csv rows=10; outputs/report_tables/closed_loop_episode_replay.csv rows=10; outputs/report_tables/agent_engagement_scorecard.csv rows=10; outputs/report_tables/defense_effectiveness_ledger.csv rows=56; outputs/report_tables/defense_action_attribution_audit.csv rows=5; outputs/report_tables/agent_collaboration_graph.csv rows=17; outputs/report_tables/attack_defense_coverage.csv rows=4; outputs/report_tables/attack_defense_response_audit.csv rows=10
- Next gate: New experiments must preserve attack events, defense events, trace reasons, metric snapshots, attack-to-defense capability coverage, and required response timing.

### A06 ML contribution

- Goal: Use ML where it changes a bounded agent decision, not as decoration.
- Mechanism: AURA uses impact prediction for candidate ranking; ML TSRA-R opens reactive defense windows from anomaly probability; ML contribution audit ties model quality, tool invocation, E6/E7 closed-loop separation, E7 ML actions, and Mac MPS sample-pass scale evidence together; reactive defense tradeoff audit explains E7's pre-attack suppression, alert overlap, first-response cost, and bounded mission-impact tradeoff versus E6; threshold sweep makes the anomaly threshold a measured tuning parameter instead of a hidden constant; detector calibration audit checks Brier/ECE, threshold precision, and class probability separation.
- Evidence: src/ml/train_aura_impact_model.py | src/ml/train_tsra_detector.py | src/ml/train_aura_mps_mlp.py | src/experiments/run_ml_threshold_sweep.py | src/experiments/ml_contribution_audit.py | src/experiments/reactive_defense_tradeoff_audit.py | src/experiments/tsra_detector_calibration_audit.py | outputs/models/aura_impact_model_metrics.json | outputs/models/tsra_detector_metrics.json | outputs/models/aura_mps_mlp_metrics.json | outputs/report_tables/ml_contribution_audit.csv | outputs/report_tables/ml_contribution_audit.md | outputs/report_tables/reactive_defense_tradeoff_audit.csv | outputs/report_tables/reactive_defense_tradeoff_audit.md | outputs/batch/ml_threshold_sweep_summary.csv | outputs/report_tables/ml_threshold_sweep.csv | outputs/report_tables/ml_threshold_sweep.md | outputs/report_tables/tsra_detector_calibration_audit.csv | outputs/report_tables/tsra_detector_calibration_audit.md | outputs/report_tables/tsra_detector_calibration_bins.csv | outputs/report_tables/agent_tool_usage_audit.csv | outputs/report_tables/metric_gate_summary.csv
- Status: verified
- Notes: outputs/report_tables/ml_contribution_audit.csv rows=7; outputs/report_tables/reactive_defense_tradeoff_audit.csv rows=7; outputs/batch/ml_threshold_sweep_summary.csv rows=5; outputs/report_tables/tsra_detector_calibration_audit.csv rows=6
- Next gate: ML claims must state task, metric, model role, and whether the model changes closed-loop behavior.

### A07 Repeatable evidence

- Goal: Avoid single-seed claims by keeping repeated experiments and resilience metrics.
- Mechanism: E1-E7 experiments are run as 30-seed batches with mission impact, latency, stale exposure, priority inversion, resilience gain summaries, and component-level mission impact decomposition.
- Evidence: src/experiments/run_all.py | src/experiments/run_batch.py | src/experiments/metric_gate.py | src/experiments/mission_impact_decomposition.py | outputs/batch/repeated_experiment_summary.csv | outputs/batch/resilience_gain_summary.csv | outputs/report_tables/mission_impact_decomposition.csv | outputs/report_tables/metric_gate_summary.csv
- Status: verified
- Notes: outputs/batch/repeated_experiment_summary.csv rows=7; outputs/batch/resilience_gain_summary.csv rows=4; outputs/report_tables/mission_impact_decomposition.csv rows=35; outputs/report_tables/metric_gate_summary.csv rows=11
- Next gate: Metric claims must pass metric_gate_summary and point to batch or dedicated experiments.

### A08 Adaptive defense

- Goal: Show memory-backed defense adaptation without changing the baseline experiments.
- Mechanism: AdaptiveTSRA-R keeps core defenses enabled and gates optional actions from recent AgentMemory evidence.
- Evidence: src/tsra_r/adaptive_defender.py | src/experiments/run_adaptive_memory.py | outputs/batch/adaptive_memory_summary.csv | outputs/figures/adaptive_memory_comparison.png
- Status: verified
- Notes: outputs/batch/adaptive_memory_summary.csv rows=2
- Next gate: Adaptive changes must be isolated from E1-E7 baseline and checked in adaptive_memory_summary.

### A09 Safety boundary

- Goal: Keep the prototype clearly separated from real-world offensive tooling.
- Mechanism: All attack outputs are simulated effects inside a local mission simulator; safety text is repeated in COA, timeline, incident, and package artifacts.
- Evidence: README.md | outputs/report_tables/safety_boundary_audit.csv | outputs/report_tables/aura_coa_cards.csv | outputs/report_tables/battle_timeline.csv | outputs/report_tables/incident_summary.csv
- Status: verified
- Notes: outputs/report_tables/safety_boundary_audit.csv rows=5
- Next gate: Reject any change that adds operational RF parameters, exploit code, or live network actions.

### A10 Team handoff and reproducibility

- Goal: Make the shared branch reproducible for another teammate without using main for active work.
- Mechanism: README commands, package builder, manifest, final verifier, submission readiness audit, and process docs define the shared workflow.
- Evidence: README.md | scripts/build_submission_package.py | scripts/verify_submission_state.py | src/experiments/submission_readiness_audit.py | docs/process/SUBMISSION_PACKAGE.md | docs/process/GITHUB_WORKFLOW.md | outputs/report_tables/submission_readiness_audit.csv
- Status: verified
- Notes: outputs/report_tables/submission_readiness_audit.csv rows=10
- Next gate: Before handoff, rebuild the package and run verify_submission_state on branch hbin.
