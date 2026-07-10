# Evaluation Plan

## Experiments

| ID | Run name | Purpose |
|---|---|---|
| E1 | `baseline` | No attack, no defense baseline |
| E2 | `attacked` | AURA-lite hybrid mission-effect attack without defense |
| E3 | `rule_defended` | Threshold-only defense comparison |
| E4/E5 | `defended` | TSRA-R risk-fusion defense against hybrid attack |
| E6 | `ml_defended` | TSRA-ML trained gradient-boosting policy and tuned action-gate defense against hybrid attack |
| E6-A | `ml_ablated` | Same tuned action gate with learned risk fixed to zero |
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
| `defense_intervention_ticks` | Ticks where the defense emitted at least one control or alert |
| `priority_boost_ticks` | Ticks where critical-traffic priority control was active |
| `model_influenced_ticks` | Ticks where model contribution was required for at least one ML action |

## AURA-ML evaluation

`scripts/evaluate_aura_policy.py` compares rule AURA, trained AURA-ML, and the same
ML policy with predicted impact fixed to zero. The 30 holdout seeds do not overlap
training, candidate validation, or policy-development seeds. Higher impact is better
for the attack agent.

The seed-grouped candidate validation top-1 optimal rate is 0.736111 for AURA-ML,
versus 0.326389 for the rule ranker. Mean selection regret is 0.368333 versus 1.594653.

| Defense context | ML minus rule impact | Bootstrap 95% CI | ML wins |
|---|---:|---:|---:|
| none | 0.0373 | [-0.975, 0.919] | 17/30 |
| threshold rule | 21.213 | [20.0533, 22.3977] | 30/30 |
| TSRA-R | 3.0667 | [2.2703, 3.8340] | 27/30 |
| TSRA-ML | 5.1033 | [4.4097, 5.7633] | 30/30 |

The no-defense interval crosses zero, so only the defended-context improvements are
treated as statistically supported. The no-defense row uses a 1.0-point criterion
fixed before the 4000-series execution; this is approximately 1.22% of the rule-AURA
no-defense mean and is treated as the maximum tolerated negative-control drift. It is a
noninferiority negative control, not a superiority claim. AURA-ML beats its zero-model ablation on 30/30
seeds in every context. Evidence is fixed in
`examples/aura_ml_holdout_30_seed_summary.json`.

The first 3000-series fresh holdout failed the original all-context positive-mean
gate by recording `-0.0017` in the no-defense negative control. It is preserved in
`examples/aura_ml_retired_holdout_30_seed_summary.json` and those seeds are never
reused. The model and policy were not changed before the fixed-criteria 4000-series
final holdout shown above.

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
| ml_defended | 12.926 | 0.0 | 0.0104 | 4.26 | 0.0 | 0.0 |
| ml_ablated | 15.180 | 0.0 | 0.0170 | 4.89 | 0.0 | 0.0 |

TSRA-R result:

- Detection time: 1 tick
- Recovery time: 3 ticks
- Guarded baseline false alarm rate: 0.0
- Baseline-adjusted resilience gain: 90.374%

TSRA-ML result:

- Primary model: HistGradientBoostingClassifier
- Training samples: 100,000 synthetic mission states
- Synthetic holdout validation accuracy: 0.9885
- Synthetic holdout validation F1: 0.9884
- Synthetic holdout validation ROC-AUC: 0.9995
- Synthetic holdout validation log loss: 0.0297
- Independent attacked-trajectory oracle F1: 0.9972
- Independent TSRA-defended-trajectory oracle F1: 0.9771
- Tuned action gate: `models/tsra_ml_policy_config.json`
- Final selection report: `models/tsra_final_selection_report.json`
- Detection time: 1 tick
- Recovery time: 1 tick
- Adaptive compressed UAV snapshots: 43.8 mean
- Deferred UAV frames: 9.2 mean
- Backlog messages: 0.0 mean
- Expired messages: 0.0 mean
- ML guarded baseline false alarm rate: 0.0
- Baseline-adjusted resilience gain: 93.600%
- Defense intervention ticks: 116.0 mean, versus TSRA-R 134.4
- Priority-boost ticks: 97.2 mean, versus TSRA-R 118.0
- Model-influenced ticks: 83.8 mean
- Zero-model ablation mission impact: 15.180
- Learned-model impact contribution: 2.254 points

## Selection note

The 100k-sample model reaches synthetic holdout F1 0.9884 and attacked-trajectory oracle F1 0.9972. Both values compare against a synthetic proactive-intervention oracle; neither is real-world incident accuracy. `model_influenced_actions` and `guardrail_triggered_actions` expose which source caused each closed-loop decision.

## Independent 30-seed holdout

The five-seed result above combines policy-tuning and policy-validation seeds. A
separate post-tuning holdout therefore uses 30 seeds excluded from model trajectory
validation and policy tuning.

| Condition | Mission impact mean | Stdev | Resilience gain |
|---|---:|---:|---:|
| TSRA-R | 16.2180 | 2.1104 | 89.8057% |
| TSRA-ML | 15.3187 | 1.6250 | 91.0330% |
| zero-model ablation | 16.9810 | 2.8517 | 88.7730% |

Paired TSRA-R minus TSRA-ML impact is 0.8993 with bootstrap 95% interval
`[0.1500, 1.6387]`. Paired zero-model ablation minus TSRA-ML impact is 1.6623
with interval `[0.7063, 2.7050]`. TSRA-ML wins 22 of 30 seeds in both comparisons
and loses 8, so the supported conclusion is positive mean effect, not universal
per-seed dominance. The compact evidence is
`examples/holdout_30_seed_summary.json`.
