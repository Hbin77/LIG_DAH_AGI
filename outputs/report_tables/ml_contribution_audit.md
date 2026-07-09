# ML Contribution Audit

This audit verifies that ML contributes to bounded agent decisions inside the closed simulator.
Safety boundary: closed simulation ML contribution audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| M01 | AURA-ML model quality | pass | best_model=hist_gradient_boosting; mae=0.0112905; r2=0.988284; top1_action_match_rate=0.90411 | AURA-ML can use the tabular impact model for candidate ranking because both regression error and top-1 action agreement pass the closed-simulation threshold. |
| M02 | TSRA-R-ML detector quality | pass | best_model=random_forest; precision=0.995736; recall=0.934; f1=0.96388 | TSRA-R-ML has enough detector quality to justify thresholded reactive defense inside the simulator. |
| M03 | AURA-ML tool invocation | pass | experiments=E6_ml_aura_tsra_r,E7_ml_aura_ml_tsra_r; predict_candidate_impact_invocations=51; errors=0 | The ML impact model is part of the AURA-ML agent loop, not only an offline metric file. |
| M04 | TSRA-R-ML tool invocation | pass | experiments=E7_ml_aura_ml_tsra_r; predict_attack_probability_invocations=61; errors=0 | The ML detector participates in TSRA-R-ML decisions before defense events are selected. |
| M05 | Closed-loop ML separation | pass | g10_status=pass; abs_e7_minus_e6=0.0135924; e6_mission_impact_mean=0.14631989451820543; e7_mission_impact_mean=0.15991234400129442 | The ML defender path changes closed-loop behavior relative to rule TSRA-R, so E7 is not a duplicate experiment row. |
| M06 | E7 ML closed-loop actions | pass | attack_events=5; attack_types=failover_chasing,queue_pressure,stale_cop_induction; defense_events=30; ml_attack_alert_count=8; defense_actions=ml_attack_alert,pace_switch,priority_reroute,stale_badge,video_throttle | The ML-vs-ML episode contains actual ML-ranked attack choices and ML anomaly alerts. |
| M07 | Mac MPS scale experiment | pass | device=mps; train_samples_per_epoch=1000000; epochs=20; sample_passes=20000000; mps_r2=0.995122; mps_top1_action_match_rate=0.748667; histgb_top1_action_match_rate=0.90411 | The Mac GPU run demonstrates larger synthetic sample-pass throughput. The deployed closed-loop AURA selector remains the stronger top-1 tabular model unless future MPS top-1 evidence exceeds it. |

## Detail

### M01 AURA-ML model quality

- Requirement: Deployed AURA impact predictor must be accurate enough to rank simulated attack-effect candidates.
- Evidence: outputs/models/aura_impact_model_metrics.json
- Observed: best_model=hist_gradient_boosting; mae=0.0112905; r2=0.988284; top1_action_match_rate=0.90411
- Status: pass
- Interpretation: AURA-ML can use the tabular impact model for candidate ranking because both regression error and top-1 action agreement pass the closed-simulation threshold.
- Safety boundary: closed simulation ML contribution audit only; no RF, exploit, or live network action

### M02 TSRA-R-ML detector quality

- Requirement: Deployed TSRA-R detector must have high precision, recall, and F1 before it opens defense windows.
- Evidence: outputs/models/tsra_detector_metrics.json
- Observed: best_model=random_forest; precision=0.995736; recall=0.934; f1=0.96388
- Status: pass
- Interpretation: TSRA-R-ML has enough detector quality to justify thresholded reactive defense inside the simulator.
- Safety boundary: closed simulation ML contribution audit only; no RF, exploit, or live network action

### M03 AURA-ML tool invocation

- Requirement: AURA-ML must call the ML impact prediction tool inside DecisionTrace records.
- Evidence: outputs/report_tables/agent_tool_usage_audit.csv
- Observed: experiments=E6_ml_aura_tsra_r,E7_ml_aura_ml_tsra_r; predict_candidate_impact_invocations=51; errors=0
- Status: pass
- Interpretation: The ML impact model is part of the AURA-ML agent loop, not only an offline metric file.
- Safety boundary: closed simulation ML contribution audit only; no RF, exploit, or live network action

### M04 TSRA-R-ML tool invocation

- Requirement: TSRA-R-ML must call the ML anomaly-probability tool inside DecisionTrace records.
- Evidence: outputs/report_tables/agent_tool_usage_audit.csv
- Observed: experiments=E7_ml_aura_ml_tsra_r; predict_attack_probability_invocations=61; errors=0
- Status: pass
- Interpretation: The ML detector participates in TSRA-R-ML decisions before defense events are selected.
- Safety boundary: closed simulation ML contribution audit only; no RF, exploit, or live network action

### M05 Closed-loop ML separation

- Requirement: E7 must remain behaviorally distinct from E6 so ML TSRA-R is not a no-op copy.
- Evidence: outputs/report_tables/metric_gate_summary.csv | outputs/batch/repeated_experiment_summary.csv
- Observed: g10_status=pass; abs_e7_minus_e6=0.0135924; e6_mission_impact_mean=0.14631989451820543; e7_mission_impact_mean=0.15991234400129442
- Status: pass
- Interpretation: The ML defender path changes closed-loop behavior relative to rule TSRA-R, so E7 is not a duplicate experiment row.
- Safety boundary: closed simulation ML contribution audit only; no RF, exploit, or live network action

### M06 E7 ML closed-loop actions

- Requirement: E7 must include ML-selected attack diversity and ML-triggered defense actions.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl
- Observed: attack_events=5; attack_types=failover_chasing,queue_pressure,stale_cop_induction; defense_events=30; ml_attack_alert_count=8; defense_actions=ml_attack_alert,pace_switch,priority_reroute,stale_badge,video_throttle
- Status: pass
- Interpretation: The ML-vs-ML episode contains actual ML-ranked attack choices and ML anomaly alerts.
- Safety boundary: closed simulation ML contribution audit only; no RF, exploit, or live network action

### M07 Mac MPS scale experiment

- Requirement: GPU-scale metrics must be framed as sample-pass scale evidence, not as the deployed top-1 selector.
- Evidence: outputs/models/aura_mps_mlp_metrics.json
- Observed: device=mps; train_samples_per_epoch=1000000; epochs=20; sample_passes=20000000; mps_r2=0.995122; mps_top1_action_match_rate=0.748667; histgb_top1_action_match_rate=0.90411
- Status: pass
- Interpretation: The Mac GPU run demonstrates larger synthetic sample-pass throughput. The deployed closed-loop AURA selector remains the stronger top-1 tabular model unless future MPS top-1 evidence exceeds it.
- Safety boundary: closed simulation ML contribution audit only; no RF, exploit, or live network action
