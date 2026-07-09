# ML Red-Blue Interaction Audit

This audit links each E7 AURA-ML attack selection to the TSRA-R-ML probability/window response, ML alert, core defense event, and coordination outcome.
Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 5
- Status counts: pass=5
- Interaction classes: active_window_bounded_refresh=2, active_window_immediate_core_defense=2, ml_triggered_after_attack=1

| attack_event_id | attack_type | target_link | aura_candidate_count | first_above_threshold_latency_sec | first_ml_alert_latency_sec | first_core_defense_latency_sec | interaction_class | interaction_status |
|---|---|---|---:|---:|---:|---:|---|---|
| ml-atk-00001 | queue_pressure | SATCOM | 4 | 20 | 20 | 20 | ml_triggered_after_attack | pass |
| ml-atk-00002 | failover_chasing | LTE | 6 | 0 | 20 | 5 | active_window_bounded_refresh | pass |
| ml-atk-00003 | queue_pressure | LTE | 6 | 0 | 20 | 0 | active_window_immediate_core_defense | pass |
| ml-atk-00004 | failover_chasing | MESH | 5 | 0 | 20 | 0 | active_window_immediate_core_defense | pass |
| ml-atk-00005 | failover_chasing | LTE | 5 | 0 | 20 | 10 | active_window_bounded_refresh | pass |

## Detail

### ml-atk-00001 queue_pressure

- AURA trace: aura-ml-trace-00007
- AURA selected score: 0.579505
- AURA selection link: linked
- TSRA probability at attack: 0.266695
- TSRA active window before attack: false
- Peak probability in response window: 0.958644
- Coordination class: ml_reactive_window
- Impact reduction from peak: 0.205612
- Interaction signal: aura_link=linked; aura_candidates=4; first_above_threshold_latency=20; first_ml_alert_latency=20; first_core_defense_latency=20; peak_probability=0.958644; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

### ml-atk-00002 failover_chasing

- AURA trace: aura-ml-trace-00012
- AURA selected score: 0.841793
- AURA selection link: linked
- TSRA probability at attack: 0.971653
- TSRA active window before attack: true
- Peak probability in response window: 0.974431
- Coordination class: prepositioned_defense
- Impact reduction from peak: 0.0213565
- Interaction signal: aura_link=linked; aura_candidates=6; first_above_threshold_latency=0; first_ml_alert_latency=20; first_core_defense_latency=5; peak_probability=0.974431; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

### ml-atk-00003 queue_pressure

- AURA trace: aura-ml-trace-00017
- AURA selected score: 0.918255
- AURA selection link: linked
- TSRA probability at attack: 0.969074
- TSRA active window before attack: true
- Peak probability in response window: 0.97963
- Coordination class: prepositioned_defense
- Impact reduction from peak: 0.05886
- Interaction signal: aura_link=linked; aura_candidates=6; first_above_threshold_latency=0; first_ml_alert_latency=20; first_core_defense_latency=0; peak_probability=0.97963; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

### ml-atk-00004 failover_chasing

- AURA trace: aura-ml-trace-00022
- AURA selected score: 0.745517
- AURA selection link: linked
- TSRA probability at attack: 0.93095
- TSRA active window before attack: true
- Peak probability in response window: 0.939345
- Coordination class: prepositioned_defense
- Impact reduction from peak: 0.0206573
- Interaction signal: aura_link=linked; aura_candidates=5; first_above_threshold_latency=0; first_ml_alert_latency=20; first_core_defense_latency=0; peak_probability=0.939345; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

### ml-atk-00005 failover_chasing

- AURA trace: aura-ml-trace-00027
- AURA selected score: 0.708246
- AURA selection link: linked
- TSRA probability at attack: 0.941744
- TSRA active window before attack: true
- Peak probability in response window: 0.963056
- Coordination class: prepositioned_defense
- Impact reduction from peak: 0.0367162
- Interaction signal: aura_link=linked; aura_candidates=5; first_above_threshold_latency=0; first_ml_alert_latency=20; first_core_defense_latency=10; peak_probability=0.963056; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action
