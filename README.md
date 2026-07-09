# DAH 2026 TSRA/AURA Prototype

This repository contains a closed simulation prototype for the DAH 2026 preliminary scenario:

`Hybrid SATCOM Disruption 기반 C4ISR 데이터 신뢰성 붕괴 시나리오와 AI 기반 능동 방어 에이전트`

The code does not attack real SATCOM, RF, or network equipment. AURA only emits simulated attack-effect events inside the local mission simulator.

## Branch Policy

This repository is prepared for team collaboration.

All active development work is pushed to the `hbin` branch.

Do not push directly to `main`.

The `main` branch is kept as the protected/default branch. The `hbin` branch is the shared working branch for code, experiments, and documentation.

See:

- `docs/process/COMPETITION_DIRECTION.md`
- `docs/process/NEXT_DEVELOPMENT_QUEUE.md`
- `docs/process/GITHUB_WORKFLOW.md`
- `docs/process/DEVELOPMENT_LOG.md`

## Agent Documents

The attack and defense agents are documented separately.

- Agent runtime: `docs/agents/AGENT_RUNTIME.md`
- Attack agent: `docs/agents/AURA_ATTACK_AGENT.md`
- Defense agent: `docs/agents/TSRA_R_DEFENSE_AGENT.md`

Read order:

```text
1. docs/Requirements.md
2. docs/process/COMPETITION_DIRECTION.md
3. docs/process/NEXT_DEVELOPMENT_QUEUE.md
4. docs/process/SUBMISSION_PACKAGE.md
5. docs/process/FINAL_QA.md
6. docs/DAH2026_TSRA_v3_realistic_attack_rewrite.md
7. docs/agents/AGENT_RUNTIME.md
8. docs/agents/AURA_ATTACK_AGENT.md
9. docs/agents/TSRA_R_DEFENSE_AGENT.md
10. docs/Implementation_Report.md
11. docs/Report_Ready_Summary.md
```

## Components

- `src/agents/`: shared Agent Runtime, Memory, Tool Registry, and DecisionTrace schemas
- `src/simulator/`: C4ISR/SATCOM message, queue, link, and COP freshness simulator
- `src/aura/`: AURA red-team attack-effect selection agent
- `src/tsra_r/`: TSRA-R blue-team defense agent
- `src/ml/`: ML dataset generation and model training
- `src/experiments/`: E1-E7 experiment runner
- `outputs/`: generated logs, datasets, models, summaries, and figures
- `docs/`: scenario and planning documents

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Run Baseline Experiments

```bash
python3 -m src.experiments.run_all
```

This writes:

- `outputs/experiments/experiment_summary.csv`
- `outputs/experiments/*/mission_events.jsonl`
- `outputs/experiments/*/attack_events.jsonl`
- `outputs/experiments/*/defense_events.jsonl`
- `outputs/experiments/*/aura_decision_traces.jsonl`
- `outputs/experiments/*/tsra_r_decision_traces.jsonl`
- `outputs/figures/mission_impact.png`
- `outputs/figures/critical_latency.png`
- `outputs/figures/priority_inversion.png`
- `outputs/figures/stale_data_ratio.png`
- `outputs/figures/trusted_stale_exposure.png`
- `outputs/figures/E3_rule_aura_timeline.png`
- `outputs/figures/E5_rule_aura_tsra_r_timeline.png`
- `outputs/figures/E7_ml_aura_ml_tsra_r_timeline.png`
- `outputs/figures/aura_tsra_architecture.png`
- `outputs/report_tables/E5_rule_aura_tsra_r_event_timeline.md`
- `outputs/report_tables/ml_model_comparison.md`

## Summarize Agent Decision Traces

```bash
python3 -m src.experiments.trace_summary
```

This writes:

- `outputs/report_tables/agent_decision_trace_summary.csv`
- `outputs/report_tables/agent_decision_trace_summary.md`

The summary combines AURA and TSRA-R `DecisionTrace` logs into one time-ordered table with selected action, top candidate, score/probability, tool calls, and reason.

## Generate Battle Timeline

```bash
python3 -m src.experiments.battle_timeline
```

This writes:

- `outputs/report_tables/battle_timeline.csv`
- `outputs/report_tables/battle_timeline.md`

The battle timeline merges AURA attack events, TSRA-R defense events, DecisionTrace reasons, and metric snapshots for E5 and E7 on the same event-time axis.

## Generate Incident Summary

```bash
python3 -m src.experiments.incident_summary
```

This writes:

- `outputs/report_tables/incident_summary.csv`
- `outputs/report_tables/incident_summary.md`

The incident summary condenses the battle timeline into attack-anchored incident windows with defense response, mission impact movement, residual risk, outcome, and safety boundary.

## Generate Operator Alerts

```bash
python3 -m src.experiments.operator_alerts
```

This writes:

- `outputs/report_tables/operator_alerts.csv`
- `outputs/report_tables/operator_alerts.md`

The alert table translates TSRA-R `DefenseEvent` records into closed-simulation operator alerts with severity, mission rationale, expected operator response, related attack context, and metric snapshot.

## Generate Defense Effectiveness Ledger

```bash
python3 -m src.experiments.defense_effectiveness_ledger
```

This writes:

- `outputs/report_tables/defense_effectiveness_ledger.csv`
- `outputs/report_tables/defense_effectiveness_ledger.md`

The ledger joins each TSRA-R `DefenseEvent` to local mission metric movement before and after the response window. Run it after `operator_alerts` has been generated.

## Audit Defense Action Attribution

```bash
python3 -m src.experiments.defense_action_attribution_audit --fail-on-error
```

This writes:

- `outputs/report_tables/defense_action_attribution_audit.csv`
- `outputs/report_tables/defense_action_attribution_audit.md`

The audit aggregates the defense effectiveness ledger by action and links local metric movement to ablation or reactive-window evidence. It separates direct ablation-supported actions from local metric and bounded-tradeoff actions instead of claiming every defense action lowers the scalar mission-impact score by itself.

## Validate Agent Event Contracts

```bash
python3 -m src.experiments.validate_event_contracts --fail-on-error
```

This writes:

- `outputs/report_tables/agent_contract_validation.csv`
- `outputs/report_tables/agent_contract_validation.md`

The validator checks AURA attack events, TSRA-R defense events, mission events, metric snapshots, DecisionTrace logs, and cross-log relationships for the shared simulator contract.

## Audit DecisionTrace Quality

```bash
python3 -m src.experiments.trace_quality_audit --fail-on-error
```

This writes:

- `outputs/report_tables/decision_trace_quality_audit.csv`
- `outputs/report_tables/decision_trace_quality_audit.md`

The audit checks whether each active AURA/TSRA-R policy has complete reason, observation, memory, feedback, selected action, tool/candidate evaluation, and non-no-op event evidence.

## Audit Agent Runtime Invariants

```bash
python3 -m src.experiments.agent_runtime_invariant_audit --fail-on-error
```

This writes:

- `outputs/report_tables/agent_runtime_invariant_audit.csv`
- `outputs/report_tables/agent_runtime_invariant_audit.md`

The audit checks runtime-level invariants across `DecisionTrace` logs: trace id sequence, monotonic time, memory count progression, previous-action chaining, tool error count, candidate evidence, and selected event coverage.

## Generate Agent Loop Replay

```bash
python3 -m src.experiments.agent_loop_replay
```

This writes:

- `outputs/report_tables/agent_loop_replay.csv`
- `outputs/report_tables/agent_loop_replay.md`

The replay reconstructs representative observe-memory-tool-candidate-decision-feedback loops for AURA, AURA-ML, TSRA-R, and TSRA-R-ML.

## Audit Agent Decision Causality

```bash
python3 -m src.experiments.agent_decision_causality_audit
```

This writes:

- `outputs/report_tables/agent_decision_causality_audit.csv`
- `outputs/report_tables/agent_decision_causality_audit.md`

The audit verifies that selected actions are supported by candidate actions, tool calls, and score or threshold evidence inside `DecisionTrace` records.

## Audit Agent Decision Margin

```bash
python3 -m src.experiments.agent_decision_margin_audit
```

This writes:

- `outputs/report_tables/agent_decision_margin_audit.csv`
- `outputs/report_tables/agent_decision_margin_audit.md`

The audit records top-score margins, threshold margins, eligible/ready defense counts, and no-op basis so each agent action has quantitative decision support.

## Audit Agent Goal Alignment

```bash
python3 -m src.experiments.agent_goal_alignment_audit --fail-on-error
```

This writes:

- `outputs/report_tables/agent_goal_alignment_audit.csv`
- `outputs/report_tables/agent_goal_alignment_audit.md`

The audit verifies that AURA decisions align with the mission-impact attack objective and that TSRA-R decisions align with observed priority, stale-data, video-load, PACE, or ML-threshold defense conditions.

## Audit Agent Decision Feedback

```bash
python3 -m src.experiments.agent_decision_feedback_audit --fail-on-error
```

This writes:

- `outputs/report_tables/agent_decision_feedback_audit.csv`
- `outputs/report_tables/agent_decision_feedback_audit.md`

The audit links selected E5/E7 `DecisionTrace` attack and defense events to event logs, metric feedback, closed-loop outcomes, and defense action attribution.

## Audit Agent Memory Belief State

```bash
python3 -m src.experiments.agent_memory_belief_audit
```

This writes:

- `outputs/report_tables/agent_memory_belief_audit.csv`
- `outputs/report_tables/agent_memory_belief_audit.md`

The audit verifies that AgentMemory is populated, changes across decisions, carries belief-state keys, and passes the previous selected action into the next decision loop.

## Audit Agent Memory Influence

```bash
python3 -m src.experiments.agent_memory_influence_audit --fail-on-error
```

This writes:

- `outputs/report_tables/agent_memory_influence_audit.csv`
- `outputs/report_tables/agent_memory_influence_audit.md`

The audit verifies that memory acts as a decision gate: AURA cadence and event-budget control, TSRA-R action cooldowns, TSRA-R-ML active defense windows, and adaptive TSRA-R memory policy effects.

## Audit Cross-Agent Context Flow

```bash
python3 -m src.experiments.cross_agent_context_audit --fail-on-error
```

This writes:

- `outputs/report_tables/cross_agent_context_audit.csv`
- `outputs/report_tables/cross_agent_context_audit.md`

The audit verifies that AURA carries TSRA-R defense context and TSRA-R carries AURA attack context through observations, tool calls, AgentMemory, DecisionTrace feedback, candidate rows, and emitted defense event details. It also checks that AURA-ML converts defender context into a bounded counter-defense selection-score term, and that TSRA-R converts attack context into bounded defense-priority scores and ordered core defense events instead of only logging it.

## Audit AURA Attack Decision Path

```bash
python3 -m src.experiments.aura_attack_decision_path_audit --fail-on-error
```

This writes:

- `outputs/report_tables/aura_attack_decision_path_audit.csv`
- `outputs/report_tables/aura_attack_decision_path_audit.md`

The audit verifies that AURA and AURA-ML candidate scores follow their formulas, scoring tools run once per candidate, selected attacks match the top-scored candidate and persisted `AttackEvent`, cadence/no-op gates hold, `AURA-ML` events keep the correct agent label, and tactical plus defense-context coverage remains visible.

## Audit Defense Priority Decision Path

```bash
python3 -m src.experiments.defense_priority_decision_path_audit --fail-on-error
```

This writes:

- `outputs/report_tables/defense_priority_decision_path_audit.csv`
- `outputs/report_tables/defense_priority_decision_path_audit.md`

The audit verifies that TSRA-R candidate priority scores follow `score = defense_base_score + attack_context_bonus`, stay bounded, match emitted `DefenseEvent.details`, preserve same-tick core event ordering, and do not emit a defense action unless the matching candidate was eligible and ready.

## Audit Agent Tool Usage

```bash
python3 -m src.experiments.agent_tool_usage_audit
```

This writes:

- `outputs/report_tables/agent_tool_usage_audit.csv`
- `outputs/report_tables/agent_tool_usage_audit.md`

The audit verifies that AURA and TSRA-R tools are actually invoked inside `DecisionTrace` records with input summaries, output summaries, and pass/fail status.

## Generate Agent Interface Manifest

```bash
python3 -m src.experiments.agent_interface_manifest
```

This writes:

- `outputs/report_tables/agent_interface_manifest.csv`
- `outputs/report_tables/agent_interface_manifest.md`

The manifest lists each active attack/defense agent's goal, policies, input contract, memory contract, tool contract, candidate actions, selected actions, and event outputs.

## Generate Agent Capability Matrix

```bash
python3 -m src.experiments.agent_capability_matrix
```

This writes:

- `outputs/report_tables/agent_capability_matrix.csv`
- `outputs/report_tables/agent_capability_matrix.md`

The matrix maps AURA/TSRA-R capabilities to runtime actions, decision sources, evidence counts, observed effects, and validation gates.

## Audit Safety Boundary

```bash
python3 -m src.experiments.safety_boundary_audit --fail-on-error
```

This writes:

- `outputs/report_tables/safety_boundary_audit.csv`
- `outputs/report_tables/safety_boundary_audit.md`

The audit checks that operational core code does not import or call live-network or shell primitives, that automation exceptions are allowlisted, that AURA remains a simulated attack-effect agent, and that package exclusion policy is present.

## Generate AURA COA Cards

```bash
python3 -m src.experiments.aura_coa_cards
```

This writes:

- `outputs/report_tables/aura_coa_cards.csv`
- `outputs/report_tables/aura_coa_cards.md`

Each COA card describes one AURA-selected simulated attack effect with target link, traffic class, expected mission impact, detectability, runner-up candidate, selection reason, and explicit safety boundary.

## Run TSRA-R Action Ablation

```bash
python3 -m src.experiments.run_tsra_ablation
```

This writes:

- `outputs/batch/tsra_action_ablation_raw.csv`
- `outputs/batch/tsra_action_ablation_summary.csv`
- `outputs/figures/tsra_action_ablation.png`

The ablation compares full TSRA-R against variants with one defensive action disabled: `priority_reroute`, `video_throttle`, `stale_badge`, or `pace_switch`.

## Run Adaptive Memory Comparison

```bash
python3 -m src.experiments.run_adaptive_memory
```

This writes:

- `outputs/batch/adaptive_memory_raw.csv`
- `outputs/batch/adaptive_memory_summary.csv`
- `outputs/figures/adaptive_memory_comparison.png`

The comparison keeps baseline E1-E7 behavior unchanged and runs a separate `AdaptiveTSRAR` mode where AgentMemory gates optional defense actions. Core actions, `priority_reroute` and `stale_badge`, stay enabled; `video_throttle` and `pace_switch` require repeated memory evidence before activation.

## Audit Adaptive Defense Decision Path

```bash
python3 -m src.experiments.adaptive_defense_decision_path_audit --fail-on-error
```

This writes:

- `outputs/report_tables/adaptive_defense_decision_path_audit.csv`
- `outputs/report_tables/adaptive_defense_decision_path_audit.md`

The audit follows Adaptive TSRA-R from AgentMemory policy tool calls to candidate-level core/optional action gates, emitted defense events, and batch-level mission impact improvement.

## Run 30-Seed Repeated Experiments

```bash
python3 -m src.experiments.run_batch
```

This writes:

- `outputs/batch/repeated_experiment_raw.csv`
- `outputs/batch/repeated_experiment_summary.csv`
- `outputs/batch/resilience_gain_summary.csv`
- `outputs/figures/batch_mission_impact_errorbar.png`
- `outputs/figures/batch_critical_latency_errorbar.png`
- `outputs/figures/batch_trusted_stale_errorbar.png`
- `outputs/figures/batch_priority_inversion_errorbar.png`
- `outputs/figures/batch_resilience_gain.png`

## Check Metric Gates

```bash
python3 -m src.experiments.metric_gate --fail-on-error
```

This writes:

- `outputs/report_tables/metric_gate_summary.csv`
- `outputs/report_tables/metric_gate_summary.md`

The gate checks whether the generated metrics still support the intended AURA/TSRA-R direction: AURA impact, TSRA-R resilience, action ablation value, adaptive memory improvement, ML defender separation, and repeated-run stability.

## Audit ML Contribution

```bash
python3 -m src.experiments.ml_contribution_audit --fail-on-error
```

This writes:

- `outputs/report_tables/ml_contribution_audit.csv`
- `outputs/report_tables/ml_contribution_audit.md`

The audit verifies that ML is used inside bounded agent decisions: AURA-ML model quality, TSRA-R-ML detector quality, ML tool invocations in DecisionTrace, E6/E7 closed-loop separation, E7 ML action evidence, and the Mac MPS scale experiment framing. TSRA-R-ML also records a mission-risk guard tool that can open an early pre-threshold defense window under severe mission pressure, or extend an already opened window when residual COP, queue, or link risk remains near expiry.

## Audit ML Attack Decision Path

```bash
python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error
```

This writes:

- `outputs/report_tables/ml_attack_decision_path_audit.csv`
- `outputs/report_tables/ml_attack_decision_path_audit.md`

The audit follows the E7 AURA-ML path from startup no-op to candidate generation, ML impact prediction, detectability-adjusted base scoring, bounded objective-aware and counter-defense-aware selection, cadence gating, event budget, and closed-loop attack feedback. It also checks that selected attacks cover `queue_pressure`, `failover_chasing`, and `stale_cop_induction` inside the closed simulation.

## Audit ML Defense Decision Path

```bash
python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error
```

This writes:

- `outputs/report_tables/ml_defense_decision_path_audit.csv`
- `outputs/report_tables/ml_defense_decision_path_audit.md`

The audit follows the E7 TSRA-R-ML path from anomaly probability to pre-threshold mission guard, threshold crossing, defense-window opening, alert cooldown, core TSRA-R fanout, memory continuity, and closed-loop coordination effect.

## Audit ML Red-Blue Interaction

```bash
python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error
```

This writes:

- `outputs/report_tables/ml_red_blue_interaction_audit.csv`
- `outputs/report_tables/ml_red_blue_interaction_audit.md`

The audit links each E7 AURA-ML attack selection to the TSRA-R-ML probability/window response, ML alert or already-active ML window, core defense event, and coordination outcome in the same response window.

## Audit Reactive Defense Tradeoff

```bash
python3 -m src.experiments.reactive_defense_tradeoff_audit --fail-on-error
```

This writes:

- `outputs/report_tables/reactive_defense_tradeoff_audit.csv`
- `outputs/report_tables/reactive_defense_tradeoff_audit.md`

The audit explains E7 as a reactive ML-defense tradeoff: it suppresses pre-attack defense events, exposes first-response latency, verifies ML alerts against active attack windows, preserves core TSRA-R actions, and bounds the mission-impact cost versus E6.

## Run ML Threshold Sweep

```bash
python3 -m src.experiments.run_ml_threshold_sweep
```

This writes:

- `outputs/batch/ml_threshold_sweep_raw.csv`
- `outputs/batch/ml_threshold_sweep_summary.csv`
- `outputs/report_tables/ml_threshold_sweep.csv`
- `outputs/report_tables/ml_threshold_sweep.md`

The sweep runs TSRA-R-ML thresholds `0.55`, `0.65`, `0.75`, `0.85`, and `0.95` across 10 deterministic seeds. It records mission impact, alert timing, no-op behavior, and watch/usable status so the anomaly threshold is a measured tuning parameter rather than a hidden constant.

## Audit TSRA-R Detector Calibration

```bash
python3 -m src.experiments.tsra_detector_calibration_audit --fail-on-error
```

This writes:

- `outputs/report_tables/tsra_detector_calibration_audit.csv`
- `outputs/report_tables/tsra_detector_calibration_audit.md`
- `outputs/report_tables/tsra_detector_calibration_bins.csv`

The audit evaluates TSRA-R-ML detector probabilities on an independent deterministic holdout set. It records Brier score, expected calibration error, threshold precision/recall, probability separation, and consistency with the closed-loop threshold sweep.

## Generate Attack-Defense Coverage

```bash
python3 -m src.experiments.attack_defense_coverage
```

This writes:

- `outputs/report_tables/attack_defense_coverage.csv`
- `outputs/report_tables/attack_defense_coverage.md`

The coverage table maps each AURA attack capability to the TSRA-R defense capabilities and validation gates that cover it. Run it after `agent_capability_matrix` and `metric_gate_summary` have been generated.

## Audit Attack-Defense Responses

```bash
python3 -m src.experiments.attack_defense_response_audit
```

This writes:

- `outputs/report_tables/attack_defense_response_audit.csv`
- `outputs/report_tables/attack_defense_response_audit.md`

The response audit checks E5/E7 attack events against active or timely TSRA-R defenses. It distinguishes missed required defenses from support-partial residual risk.

## Generate Closed-Loop Episode Replay

```bash
python3 -m src.experiments.closed_loop_episode_replay
```

This writes:

- `outputs/report_tables/closed_loop_episode_replay.csv`
- `outputs/report_tables/closed_loop_episode_replay.md`

The replay joins each defended attack event to response coverage, defense chains, operator alerts, and mission metric movement. Run it after `attack_defense_response_audit`, `operator_alerts`, and `defense_effectiveness_ledger` have been generated.

## Audit Agent Coordination Latency

```bash
python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error
```

This writes:

- `outputs/report_tables/agent_coordination_latency_audit.csv`
- `outputs/report_tables/agent_coordination_latency_audit.md`

The audit checks whether each E5/E7 attack episode is time-linked to a defense response, operator alert, metric peak, and post-peak impact reduction inside the response window.

## Generate Mission Thread Summary

```bash
python3 -m src.experiments.mission_thread_summary --fail-on-error
```

This writes:

- `outputs/report_tables/mission_thread_summary.csv`
- `outputs/report_tables/mission_thread_summary.md`

The mission thread summary joins each attack episode to attack decision evidence, response coverage, defense-action attribution, operator alert count, metric movement, outcome, and residual risk. Run it after `closed_loop_episode_replay`, `agent_engagement_scorecard`, and `defense_action_attribution_audit` have been generated.

## Build Agent Engagement Scorecard

```bash
python3 -m src.experiments.agent_engagement_scorecard
```

This writes:

- `outputs/report_tables/agent_engagement_scorecard.csv`
- `outputs/report_tables/agent_engagement_scorecard.md`

The scorecard links each AURA attack decision margin to the TSRA-R response chain and mission-impact movement for the defended E5/E7 episodes.

## Audit PACE Transitions

```bash
python3 -m src.experiments.pace_transition_audit
```

This writes:

- `outputs/report_tables/pace_transition_audit.csv`
- `outputs/report_tables/pace_transition_audit.md`

The PACE audit explains each TSRA-R `pace_switch` event with inferred source/target links, active or near-future attacks, metric snapshot context, and residual risk.

## Decompose Mission Impact

```bash
python3 -m src.experiments.mission_impact_decomposition
```

This writes:

- `outputs/report_tables/mission_impact_decomposition.csv`
- `outputs/report_tables/mission_impact_decomposition.md`

The decomposition breaks repeated-run Mission Impact into critical latency, trusted stale exposure, priority inversion, kill-chain delay, and recovery instability. It uses `trusted_stale_exposure` for the stale component because TSRA-R may reduce operator trust risk without removing every stale COP object.

## Generate Agent Collaboration Graph

```bash
python3 -m src.experiments.agent_collaboration_graph
```

This writes:

- `outputs/report_tables/agent_collaboration_graph.csv`
- `outputs/report_tables/agent_collaboration_graph.md`
- `outputs/report_tables/agent_collaboration_graph.mmd`

The graph summarizes how AgentRuntime, AURA/AURA-ML, MissionSimulator, TSRA-R/TSRA-R-ML, Operator Alerts, Defense Effectiveness Ledger, Mission Metrics, and the verifier/package cooperate inside the closed simulation. Run it after trace summary, COA cards, coverage, response audit, operator alerts, defense effectiveness ledger, metric gates, and mission decomposition have been generated.

## Generate Competition Alignment Matrix

```bash
python3 -m src.experiments.competition_alignment --fail-on-incomplete
```

This writes:

- `outputs/report_tables/competition_alignment_matrix.csv`
- `outputs/report_tables/competition_alignment_matrix.md`

The matrix maps DAH preliminary-round goals to concrete code, generated evidence, safety boundaries, and the next development gate. Run it after the core experiment summaries, COA cards, battle timeline, incident summary, ablation, adaptive memory, and batch outputs have been generated.

## Train AURA Impact Predictor

```bash
python3 -m src.ml.build_dataset --rows 3000
python3 -m src.ml.train_aura_impact_model
```

Outputs:

- `outputs/datasets/aura_candidate_dataset.csv`
- `outputs/models/aura_impact_model.pkl`
- `outputs/models/aura_impact_model_metrics.json`

## Train TSRA-R Anomaly Detector

```bash
python3 -m src.ml.train_tsra_detector --rows 5000
```

Outputs:

- `outputs/datasets/tsra_detection_dataset.csv`
- `outputs/models/tsra_detector.pkl`
- `outputs/models/tsra_detector_metrics.json`

## Optional Mac GPU-Scale AURA MLP

The main prototype uses scikit-learn CPU models because the tabular datasets are small. To demonstrate Apple Silicon GPU scaling, an optional PyTorch MPS experiment trains a larger neural impact predictor on online-generated synthetic attack candidates.

Create the GPU environment:

```bash
python3 -m venv .venv-gpu
.venv-gpu/bin/python -m pip install --upgrade pip
.venv-gpu/bin/python -m pip install torch matplotlib
```

Check MPS:

```bash
.venv-gpu/bin/python - <<'PY'
import torch
print(torch.__version__)
print(torch.backends.mps.is_available())
PY
```

Run the GPU-scale training:

```bash
.venv-gpu/bin/python -m src.ml.train_aura_mps_mlp \
  --device mps \
  --samples 1000000 \
  --epochs 20 \
  --batch-size 32768 \
  --eval-samples 120000 \
  --top1-groups 1500
```

Outputs:

- `outputs/models/aura_mps_mlp.pt`
- `outputs/models/aura_mps_mlp_metrics.json`
- `outputs/figures/aura_mps_mlp_training_loss.png`

## Build Source Package

```bash
python3 scripts/build_submission_package.py
```

This writes:

- `outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip`
- `outputs/package/submission_manifest.md`

The package includes code, docs, curated CSV summaries, figures, report tables, and model metric JSON files. It excludes regenerated temporary logs, seed-level batch directories, synthetic datasets, Python caches, and model binaries such as `.pkl` or `.pt`. ZIP entries are path-sorted with fixed metadata so repeated builds from the same payload produce a stable SHA-256.

## Generate Release Handoff

```bash
python3 scripts/generate_release_handoff.py
```

This writes:

- `outputs/package/release_handoff.md`

The handoff is intentionally repo-side only and not embedded inside the submission ZIP. It records the ZIP SHA-256, byte count, entry count, branch rule, Git sync checks, local freeze commands, and the external-link verification command. It does not embed the current commit SHA because a tracked file cannot stably contain the hash of the commit that contains itself.

## Freeze Release Candidate

```bash
python3 scripts/freeze_release_candidate.py --require-clean
```

This runs the final local freeze sequence in order: build the package, regenerate the release handoff, verify submission state, and run the local `file://` package-link self-test. Use `--require-clean` after committing generated files.

## Verify Submission State

```bash
python3 scripts/verify_submission_state.py
```

This checks required files, core CSV row counts, safety-boundary text, package contents, manifest ZIP SHA-256/byte-count/file-count integrity, deterministic ZIP metadata, ZIP payload parity with the current worktree, repo-only release handoff currency, ZIP exclusion rules, and `origin/main` plus `origin/hbin` branch presence.

## Audit Reproduction Order

```bash
python3 -m src.experiments.reproduction_order_audit --fail-on-error
```

Outputs:

- `outputs/report_tables/reproduction_order_audit.csv`
- `outputs/report_tables/reproduction_order_audit.md`

This checks that the README `Full Reproduction` block runs generated evidence in dependency order. It prevents downstream audits from silently reading stale files created by an earlier run.

## Audit Agent Stress Scenarios

```bash
python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error
```

Outputs:

- `outputs/report_tables/agent_stress_scenario_audit.csv`
- `outputs/report_tables/agent_stress_scenario_audit.md`

This runs closed-simulation air-defense, stale-COP, and PACE pressure stress fixtures across five seeds, then compares TSRA-R and TSRA-R-ML aggregate outcomes against attack-only outcomes. The stress table also records TSRA-R-ML mission-guard trigger counts so residual-risk window extensions are visible rather than hidden in code.

## Verify External Package Link

After uploading `outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip` to the submission cloud, verify that the public download link serves the same ZIP recorded in `outputs/package/submission_manifest.md`:

```bash
python3 scripts/verify_external_package_link.py "https://example.com/download/DAH2026_소스코드_LIG_DAH_AGI.zip"
```

Local self-test against the current ZIP:

```bash
python3 scripts/verify_external_package_link.py \
  "file://$(pwd)/outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip" \
  --allow-file-url
```

This compares downloaded bytes, SHA-256, ZIP entry count, and optional `Content-Length` against the local manifest. Do not put login-only or credential-embedded URLs in this command.

## Submission Readiness Audit

```bash
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
```

Outputs:

- `outputs/report_tables/submission_readiness_audit.csv`
- `outputs/report_tables/submission_readiness_audit.md`

This checks branch policy, reproduction commands, agent evidence, closed-loop evidence, package inputs, safety-boundary text, and team handoff docs before the package is rebuilt.

## Agent Regression Tests

```bash
python3 -m unittest discover -s tests
```

The regression tests are fast code-level checks for the agent core. They lock the AgentRuntime memory/tool/DecisionTrace chain, the AURA-ML attack event identity and selection-score formula, and the TSRA-R defense priority ordering plus cooldown no-op gate. GitHub Actions runs the same gate on `hbin` pushes through `.github/workflows/quality.yml`.

## Agent Quality Gate Audit

```bash
python3 -m src.experiments.agent_quality_gate_audit --fail-on-error
```

Outputs:

- `outputs/report_tables/agent_quality_gate_audit.csv`
- `outputs/report_tables/agent_quality_gate_audit.md`

This audit verifies that the fast agent-core regression tests, `hbin` quality workflow, README reproduction order, final verifier, and submission package are all wired together.

## Team Handoff Audit

```bash
python3 -m src.experiments.team_handoff_audit --fail-on-error
```

Outputs:

- `outputs/report_tables/team_handoff_audit.csv`
- `outputs/report_tables/team_handoff_audit.md`

This audit verifies that `docs/process/TEAM_HANDOFF.md` gives branch rules, attack/defense/ML/QA/integration role lanes, minimum gate commands, decision-record rules, and the closed-simulation safety boundary.

## Full Reproduction

```bash
python3 -m src.ml.build_dataset --rows 3000
python3 -m src.ml.train_aura_impact_model
python3 -m src.ml.train_tsra_detector --rows 5000
python3 -m unittest discover -s tests
python3 -m src.experiments.agent_quality_gate_audit --fail-on-error
python3 -m src.experiments.team_handoff_audit --fail-on-error
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
python3 -m src.experiments.validate_event_contracts --fail-on-error
python3 -m src.experiments.trace_quality_audit --fail-on-error
python3 -m src.experiments.agent_runtime_invariant_audit --fail-on-error
python3 -m src.experiments.agent_loop_replay
python3 -m src.experiments.agent_decision_causality_audit
python3 -m src.experiments.agent_decision_margin_audit
python3 -m src.experiments.agent_goal_alignment_audit --fail-on-error
python3 -m src.experiments.agent_decision_feedback_audit --fail-on-error
python3 -m src.experiments.agent_memory_belief_audit
python3 -m src.experiments.agent_memory_influence_audit --fail-on-error
python3 -m src.experiments.cross_agent_context_audit --fail-on-error
python3 -m src.experiments.aura_attack_decision_path_audit --fail-on-error
python3 -m src.experiments.defense_priority_decision_path_audit --fail-on-error
python3 -m src.experiments.agent_tool_usage_audit
python3 -m src.experiments.agent_interface_manifest
python3 -m src.experiments.agent_capability_matrix
python3 -m src.experiments.battle_timeline
python3 -m src.experiments.incident_summary
python3 -m src.experiments.operator_alerts
python3 -m src.experiments.defense_effectiveness_ledger
python3 -m src.experiments.aura_coa_cards
python3 -m src.experiments.run_tsra_ablation
python3 -m src.experiments.run_adaptive_memory
python3 -m src.experiments.adaptive_defense_decision_path_audit --fail-on-error
python3 -m src.experiments.run_batch
python3 -m src.experiments.metric_gate --fail-on-error
python3 -m src.experiments.reactive_defense_tradeoff_audit --fail-on-error
python3 -m src.experiments.defense_action_attribution_audit --fail-on-error
python3 -m src.experiments.run_ml_threshold_sweep
python3 -m src.experiments.tsra_detector_calibration_audit --fail-on-error
python3 -m src.experiments.attack_defense_coverage
python3 -m src.experiments.attack_defense_response_audit
python3 -m src.experiments.closed_loop_episode_replay
python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error
python3 -m src.experiments.agent_engagement_scorecard
python3 -m src.experiments.mission_thread_summary --fail-on-error
python3 -m src.experiments.pace_transition_audit
python3 -m src.experiments.mission_impact_decomposition
python3 -m src.experiments.ml_contribution_audit --fail-on-error
python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error
python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error
python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error
python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error
python3 -m src.experiments.safety_boundary_audit --fail-on-error
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 -m src.experiments.agent_collaboration_graph
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/build_submission_package.py
python3 scripts/generate_release_handoff.py
python3 scripts/freeze_release_candidate.py
python3 scripts/verify_submission_state.py
```
