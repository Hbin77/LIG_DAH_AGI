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

## Audit Agent Memory Belief State

```bash
python3 -m src.experiments.agent_memory_belief_audit
```

This writes:

- `outputs/report_tables/agent_memory_belief_audit.csv`
- `outputs/report_tables/agent_memory_belief_audit.md`

The audit verifies that AgentMemory is populated, changes across decisions, carries belief-state keys, and passes the previous selected action into the next decision loop.

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

- `outputs/package/DAH2026_source_LIG_DAH_AGI.zip`
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

## Verify External Package Link

After uploading `outputs/package/DAH2026_source_LIG_DAH_AGI.zip` to the submission cloud, verify that the public download link serves the same ZIP recorded in `outputs/package/submission_manifest.md`:

```bash
python3 scripts/verify_external_package_link.py "https://example.com/download/DAH2026_source_LIG_DAH_AGI.zip"
```

Local self-test against the current ZIP:

```bash
python3 scripts/verify_external_package_link.py \
  "file://$(pwd)/outputs/package/DAH2026_source_LIG_DAH_AGI.zip" \
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

## Full Reproduction

```bash
python3 -m src.ml.build_dataset --rows 3000
python3 -m src.ml.train_aura_impact_model
python3 -m src.ml.train_tsra_detector --rows 5000
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
python3 -m src.experiments.validate_event_contracts --fail-on-error
python3 -m src.experiments.trace_quality_audit --fail-on-error
python3 -m src.experiments.agent_loop_replay
python3 -m src.experiments.agent_decision_causality_audit
python3 -m src.experiments.agent_memory_belief_audit
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
python3 -m src.experiments.run_batch
python3 -m src.experiments.metric_gate --fail-on-error
python3 -m src.experiments.attack_defense_coverage
python3 -m src.experiments.attack_defense_response_audit
python3 -m src.experiments.closed_loop_episode_replay
python3 -m src.experiments.pace_transition_audit
python3 -m src.experiments.mission_impact_decomposition
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 -m src.experiments.agent_collaboration_graph
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/build_submission_package.py
python3 scripts/generate_release_handoff.py
python3 scripts/freeze_release_candidate.py
python3 scripts/verify_submission_state.py
```
