# Evaluation Plan

## Experiments

| ID | Run name | Purpose |
|---|---|---|
| E1 | `baseline` | No attack, no defense baseline |
| E2 | `attacked` | AURA-lite hybrid mission-effect attack without defense |
| E3 | `rule_defended` | Threshold-only defense comparison |
| E4/E5 | `defended` | TSRA-R risk-fusion defense against hybrid attack |
| E6 | `ml_defended` | TSRA-ML trained ensemble and tuned action-gate defense against hybrid attack |
| FA | `guarded_baseline` | TSRA-R false alarm check under no attack |
| ML-FA | `ml_guarded_baseline` | TSRA-ML false alarm check under no attack |

## Metrics

| Metric | Meaning |
|---|---|
| `p95_critical_latency` | P95 delay of command, alert, and position messages |
| `stale_data_ratio` | Delivered messages exceeding freshness deadline |
| `priority_inversion_rate` | Critical messages delivered after lower-urgency traffic preemption |
| `backlog_messages` | Messages remaining in queue at simulation end |
| `expired_messages` | Backlog messages already stale at simulation end |
| `detection_time` | Ticks from first attack pulse to first alert |
| `recovery_time` | Ticks from first alert to first TSRA-R stable state |
| `false_alarm_rate` | Defense alert count per observed tick under no attack |
| `mission_impact_score` | Weighted mission impact score |
| `resilience_gain_percent` | Baseline-adjusted reduction from attacked to defended |

## Current multi-seed result

Command:

```bash
conda run -n base python -m src.tsra_agent.cli --scenario hybrid --ticks 180 --seeds 7,11,19,23,31 --output-dir outputs/final_check_best
```

Summary:

| Condition | Mission impact | Priority inversion | Stale ratio | P95 critical latency | Backlog | Expired |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 8.18 | 0.0 | 0.0 | 4.0 | 0.0 | 0.0 |
| attacked | 82.162 | 0.0629 | 0.236 | 9.8 | 53.0 | 49.0 |
| rule_defended | 61.228 | 0.0 | 0.1127 | 8.56 | 72.0 | 68.0 |
| defended | 15.306 | 0.0 | 0.0107 | 5.14 | 0.0 | 0.0 |
| ml_defended | 15.306 | 0.0 | 0.0107 | 5.14 | 0.0 | 0.0 |

TSRA-R result:

- Detection time: 1 tick
- Recovery time: 3 ticks
- Guarded baseline false alarm rate: 0.0
- Baseline-adjusted resilience gain: 90.374%

TSRA-ML result:

- Primary model: StandardScaler + soft-voting GradientBoosting/RandomForest
- Training samples: 100,000 synthetic mission states
- Validation accuracy: 0.9952
- Validation F1: 0.9956
- Validation ROC-AUC: 1.0
- Validation log loss: 0.0119
- Tuned action gate: `models/tsra_ml_policy_config.json`
- Final selection report: `models/tsra_final_selection_report.json`
- Detection time: 1 tick
- Recovery time: 2 ticks
- Adaptive compressed UAV snapshots: 41.4 mean
- Deferred UAV frames: 13.0 mean
- Backlog messages: 0.0 mean
- Expired messages: 0.0 mean
- ML guarded baseline false alarm rate: 0.0
- Baseline-adjusted resilience gain: 90.374%

## Selection note

The 100k-sample model improved validation F1 to 0.9956 and log loss to 0.0119, but mission-level gains still came mainly from the action layer: adaptive UAV snapshot compression, EDF scheduling, minimum-mode guardrails, and SATCOM return hysteresis.
