# Competition Alignment Matrix

This matrix keeps the implementation tied to the DAH preliminary-round direction.
Each row maps a competition goal to concrete code, generated evidence, and the next development gate.

| alignment_id | scoring_area | agent_or_component | evidence_status | next_gate |
| --- | --- | --- | --- | --- |
| A01 | Defense mission grounding | MissionSimulator / scenario docs | verified | Any new feature must map to SATCOM, C4ISR, COP, PACE, or critical traffic. |
| A02 | Attack scenario | AURA | verified | Attack improvements must produce COA cards and never introduce live RF, exploit, or packet actions. |
| A03 | Defense architecture | TSRA-R | verified | Defense changes must be checked against mission impact plus at least one action-specific metric. |
| A04 | AI agent architecture | AgentRuntime / AgentMemory / ToolRegistry / DecisionTrace | verified | Agent changes must leave DecisionTrace evidence and pass event/trace contract validation. |
| A05 | Attack-defense cooperation | Battle timeline / Incident summary | verified | New experiments must preserve attack events, defense events, trace reasons, and metric snapshots. |
| A06 | ML contribution | AURA ML / TSRA-R ML | verified | ML claims must state task, metric, model role, and whether the model changes closed-loop behavior. |
| A07 | Repeatable evidence | Experiment runners | verified | Metric claims must point to batch CSV or a dedicated ablation/adaptive experiment. |
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
- Mechanism: TSRA-R selects priority reroute, stale badge, video throttle, and PACE switch actions; ablation isolates which action protects which mission metric.
- Evidence: src/tsra_r/rule_defender.py | src/tsra_r/ml_defender.py | src/tsra_r/adaptive_defender.py | outputs/batch/tsra_action_ablation_summary.csv
- Status: verified
- Notes: outputs/batch/tsra_action_ablation_summary.csv rows=5
- Next gate: Defense changes must be checked against mission impact plus at least one action-specific metric.

### A04 AI agent architecture

- Goal: Show agent structure beyond direct Python policy calls.
- Mechanism: AgentRuntime wraps observe, memory summary, tool calls, candidate scoring, selected action, DecisionTrace, and feedback updates.
- Evidence: src/agents/runtime.py | src/agents/memory.py | src/agents/tools.py | src/agents/schema.py | src/experiments/validate_event_contracts.py | outputs/report_tables/agent_decision_trace_summary.csv | outputs/report_tables/agent_contract_validation.csv
- Status: verified
- Notes: outputs/report_tables/agent_decision_trace_summary.csv rows=215; outputs/report_tables/agent_contract_validation.csv rows=49
- Next gate: Agent changes must leave DecisionTrace evidence and pass event/trace contract validation.

### A05 Attack-defense cooperation

- Goal: Make the red and blue agents observable on one shared event timeline.
- Mechanism: Battle timeline and incident summary merge AURA events, TSRA-R events, trace reasons, and metric movement for E5 and E7.
- Evidence: src/experiments/battle_timeline.py | src/experiments/incident_summary.py | outputs/report_tables/battle_timeline.csv | outputs/report_tables/incident_summary.csv
- Status: verified
- Notes: outputs/report_tables/battle_timeline.csv rows=46; outputs/report_tables/incident_summary.csv rows=10
- Next gate: New experiments must preserve attack events, defense events, trace reasons, and metric snapshots.

### A06 ML contribution

- Goal: Use ML where it changes a bounded agent decision, not as decoration.
- Mechanism: AURA uses impact prediction for candidate ranking; ML TSRA-R opens reactive defense windows from anomaly probability; GPU MPS training is kept as a separate scale experiment.
- Evidence: src/ml/train_aura_impact_model.py | src/ml/train_tsra_detector.py | src/ml/train_aura_mps_mlp.py | outputs/models/aura_impact_model_metrics.json | outputs/models/tsra_detector_metrics.json | outputs/models/aura_mps_mlp_metrics.json
- Status: verified
- Notes: all evidence files present
- Next gate: ML claims must state task, metric, model role, and whether the model changes closed-loop behavior.

### A07 Repeatable evidence

- Goal: Avoid single-seed claims by keeping repeated experiments and resilience metrics.
- Mechanism: E1-E7 experiments are run as 30-seed batches with mission impact, latency, stale exposure, priority inversion, and resilience gain summaries.
- Evidence: src/experiments/run_all.py | src/experiments/run_batch.py | outputs/batch/repeated_experiment_summary.csv | outputs/batch/resilience_gain_summary.csv
- Status: verified
- Notes: outputs/batch/repeated_experiment_summary.csv rows=7; outputs/batch/resilience_gain_summary.csv rows=4
- Next gate: Metric claims must point to batch CSV or a dedicated ablation/adaptive experiment.

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
- Evidence: README.md | outputs/report_tables/aura_coa_cards.csv | outputs/report_tables/battle_timeline.csv | outputs/report_tables/incident_summary.csv
- Status: verified
- Notes: all evidence files present
- Next gate: Reject any change that adds operational RF parameters, exploit code, or live network actions.

### A10 Team handoff and reproducibility

- Goal: Make the shared branch reproducible for another teammate without using main for active work.
- Mechanism: README commands, package builder, manifest, final verifier, and process docs define the shared workflow.
- Evidence: README.md | scripts/build_submission_package.py | scripts/verify_submission_state.py | docs/process/SUBMISSION_PACKAGE.md | docs/process/GITHUB_WORKFLOW.md
- Status: verified
- Notes: all evidence files present
- Next gate: Before handoff, rebuild the package and run verify_submission_state on branch hbin.
