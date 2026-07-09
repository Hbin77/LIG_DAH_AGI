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
4. docs/DAH2026_TSRA_v3_realistic_attack_rewrite.md
5. docs/agents/AGENT_RUNTIME.md
6. docs/agents/AURA_ATTACK_AGENT.md
7. docs/agents/TSRA_R_DEFENSE_AGENT.md
8. docs/Implementation_Report.md
9. docs/Report_Ready_Summary.md
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

## Full Reproduction

```bash
python3 -m src.ml.build_dataset --rows 3000
python3 -m src.ml.train_aura_impact_model
python3 -m src.ml.train_tsra_detector --rows 5000
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
python3 -m src.experiments.run_batch
```
