# Agent Coordination Latency Audit

This audit checks whether attack, defense, operator alert, and metric feedback are time-linked inside the defended E5/E7 closed-loop episodes.
Safety boundary: closed simulation coordination-latency audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 10
- Status counts: pass=10
- Classes: ml_reactive_window=1, prepositioned_defense=9

## Audit Table

| experiment | attack_event_id | attack_type | required_response_latency_sec | first_operator_alert_latency_sec | impact_reduction_from_peak | coordination_class | coordination_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E5_rule_aura_tsra_r | atk-00001 | queue_pressure | 0 | 5 | 0.0626556 | prepositioned_defense | pass |
| E5_rule_aura_tsra_r | atk-00002 | queue_pressure | 0 | 15 | 0.0194333 | prepositioned_defense | pass |
| E5_rule_aura_tsra_r | atk-00003 | queue_pressure | 0 | 10 | 0.0021496 | prepositioned_defense | pass |
| E5_rule_aura_tsra_r | atk-00004 | queue_pressure | 0 | 30 | 0.0395898 | prepositioned_defense | pass |
| E5_rule_aura_tsra_r | atk-00005 | queue_pressure | 0 | 5 | 0.00214269 | prepositioned_defense | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00001 | queue_pressure | 10 | 10 | 0.251649 | ml_reactive_window | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00002 | failover_chasing | 0 | 20 | 0.025868 | prepositioned_defense | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00003 | failover_chasing | 0 | 0 | 0.00132496 | prepositioned_defense | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00004 | queue_pressure | 0 | 10 | 0.0375459 | prepositioned_defense | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00005 | failover_chasing | 0 | 0 | 0.00163987 | prepositioned_defense | pass |

## Detail

### E5_rule_aura_tsra_r E5_rule_aura_tsra_r-episode-01 atk-00001

- Attack: AURA queue_pressure at t=60
- Response latency: required=0, first_defense=0
- Operator alert latency: 5
- Metric peak latency: 0
- Impact reduction from peak: 0.0626556
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=5; metric_peak_latency=0; impact_reduction_from_peak=0.0626556; issues=none

### E5_rule_aura_tsra_r E5_rule_aura_tsra_r-episode-02 atk-00002

- Attack: AURA queue_pressure at t=110
- Response latency: required=0, first_defense=0
- Operator alert latency: 15
- Metric peak latency: 0
- Impact reduction from peak: 0.0194333
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=15; metric_peak_latency=0; impact_reduction_from_peak=0.0194333; issues=none

### E5_rule_aura_tsra_r E5_rule_aura_tsra_r-episode-03 atk-00003

- Attack: AURA queue_pressure at t=160
- Response latency: required=0, first_defense=0
- Operator alert latency: 10
- Metric peak latency: 15
- Impact reduction from peak: 0.0021496
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=10; metric_peak_latency=15; impact_reduction_from_peak=0.0021496; issues=none

### E5_rule_aura_tsra_r E5_rule_aura_tsra_r-episode-04 atk-00004

- Attack: AURA queue_pressure at t=210
- Response latency: required=0, first_defense=0
- Operator alert latency: 30
- Metric peak latency: 0
- Impact reduction from peak: 0.0395898
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=30; metric_peak_latency=0; impact_reduction_from_peak=0.0395898; issues=none

### E5_rule_aura_tsra_r E5_rule_aura_tsra_r-episode-05 atk-00005

- Attack: AURA queue_pressure at t=260
- Response latency: required=0, first_defense=0
- Operator alert latency: 5
- Metric peak latency: 5
- Impact reduction from peak: 0.00214269
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=5; metric_peak_latency=5; impact_reduction_from_peak=0.00214269; issues=none

### E7_ml_aura_ml_tsra_r E7_ml_aura_ml_tsra_r-episode-01 ml-atk-00001

- Attack: AURA queue_pressure at t=60
- Response latency: required=10, first_defense=10
- Operator alert latency: 10
- Metric peak latency: 5
- Impact reduction from peak: 0.251649
- Coordination class: ml_reactive_window
- Status: pass
- Signal: required_response_latency=10; first_defense_latency=10; first_operator_alert_latency=10; metric_peak_latency=5; impact_reduction_from_peak=0.251649; issues=none

### E7_ml_aura_ml_tsra_r E7_ml_aura_ml_tsra_r-episode-02 ml-atk-00002

- Attack: AURA failover_chasing at t=110
- Response latency: required=0, first_defense=0
- Operator alert latency: 20
- Metric peak latency: 20
- Impact reduction from peak: 0.025868
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=20; metric_peak_latency=20; impact_reduction_from_peak=0.025868; issues=none

### E7_ml_aura_ml_tsra_r E7_ml_aura_ml_tsra_r-episode-03 ml-atk-00003

- Attack: AURA failover_chasing at t=160
- Response latency: required=0, first_defense=0
- Operator alert latency: 0
- Metric peak latency: 30
- Impact reduction from peak: 0.00132496
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=0; metric_peak_latency=30; impact_reduction_from_peak=0.00132496; issues=none

### E7_ml_aura_ml_tsra_r E7_ml_aura_ml_tsra_r-episode-04 ml-atk-00004

- Attack: AURA queue_pressure at t=210
- Response latency: required=0, first_defense=0
- Operator alert latency: 10
- Metric peak latency: 0
- Impact reduction from peak: 0.0375459
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=10; metric_peak_latency=0; impact_reduction_from_peak=0.0375459; issues=none

### E7_ml_aura_ml_tsra_r E7_ml_aura_ml_tsra_r-episode-05 ml-atk-00005

- Attack: AURA failover_chasing at t=260
- Response latency: required=0, first_defense=0
- Operator alert latency: 0
- Metric peak latency: 10
- Impact reduction from peak: 0.00163987
- Coordination class: prepositioned_defense
- Status: pass
- Signal: required_response_latency=0; first_defense_latency=0; first_operator_alert_latency=0; metric_peak_latency=10; impact_reduction_from_peak=0.00163987; issues=none
