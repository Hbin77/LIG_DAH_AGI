# ML Red-Blue Interaction Audit

This audit links each E7 AURA-ML attack selection to the TSRA-R-ML probability/window response, ML alert, core defense event, and coordination outcome.
Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 5
- Status counts: pass=5
- Interaction classes: active_window_bounded_refresh=2, active_window_immediate_core_defense=2, ml_triggered_after_attack=1

| attack_event_id | attack_type | target_link | aura_candidate_count | first_above_threshold_latency_sec | first_ml_alert_latency_sec | first_core_defense_latency_sec | interaction_class | interaction_status |
|---|---|---|---:|---:|---:|---:|---|---|
| ml-atk-00001 | queue_pressure | SATCOM | 4 | 20 | 20 | 10 | ml_triggered_after_attack | pass |
| ml-atk-00002 | failover_chasing | LTE | 6 | 0 | 20 | 20 | active_window_bounded_refresh | pass |
| ml-atk-00003 | failover_chasing | MESH | 5 | 0 |  | 0 | active_window_immediate_core_defense | pass |
| ml-atk-00004 | queue_pressure | MESH | 5 | 10 | 10 | 10 | active_window_bounded_refresh | pass |
| ml-atk-00005 | stale_cop_induction | MESH | 6 | 0 | 10 | 0 | active_window_immediate_core_defense | pass |

## Detail

### ml-atk-00001 queue_pressure

- AURA trace: aura-ml-trace-00007
- AURA selected score: 0.579505
- AURA selection link: linked
- TSRA probability at attack: 0.266695
- TSRA active window before attack: false
- Peak probability in response window: 0.960033
- Coordination class: ml_reactive_window
- Impact reduction from peak: 0.251649
- Interaction signal: aura_link=linked; aura_candidates=4; first_above_threshold_latency=20; first_ml_alert_latency=20; first_core_defense_latency=10; peak_probability=0.960033; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

### ml-atk-00002 failover_chasing

- AURA trace: aura-ml-trace-00012
- AURA selected score: 0.761848
- AURA selection link: linked
- TSRA probability at attack: 0.972533
- TSRA active window before attack: true
- Peak probability in response window: 0.972533
- Coordination class: prepositioned_defense
- Impact reduction from peak: 0.025868
- Interaction signal: aura_link=linked; aura_candidates=6; first_above_threshold_latency=0; first_ml_alert_latency=20; first_core_defense_latency=20; peak_probability=0.972533; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

### ml-atk-00003 failover_chasing

- AURA trace: aura-ml-trace-00017
- AURA selected score: 0.737403
- AURA selection link: linked
- TSRA probability at attack: 0.916883
- TSRA active window before attack: true
- Peak probability in response window: 0.921799
- Coordination class: prepositioned_defense
- Impact reduction from peak: 0.00132496
- Interaction signal: aura_link=linked; aura_candidates=5; first_above_threshold_latency=0; first_ml_alert_latency=; first_core_defense_latency=0; peak_probability=0.921799; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

### ml-atk-00004 queue_pressure

- AURA trace: aura-ml-trace-00022
- AURA selected score: 0.739372
- AURA selection link: linked
- TSRA probability at attack: 0.394108
- TSRA active window before attack: true
- Peak probability in response window: 0.943578
- Coordination class: prepositioned_defense
- Impact reduction from peak: 0.0375459
- Interaction signal: aura_link=linked; aura_candidates=5; first_above_threshold_latency=10; first_ml_alert_latency=10; first_core_defense_latency=10; peak_probability=0.943578; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action

### ml-atk-00005 stale_cop_induction

- AURA trace: aura-ml-trace-00027
- AURA selected score: 0.779393
- AURA selection link: linked
- TSRA probability at attack: 0.928007
- TSRA active window before attack: true
- Peak probability in response window: 0.9331
- Coordination class: prepositioned_defense
- Impact reduction from peak: 0.00176331
- Interaction signal: aura_link=linked; aura_candidates=6; first_above_threshold_latency=0; first_ml_alert_latency=10; first_core_defense_latency=0; peak_probability=0.9331; issues=none
- Status: pass
- Safety boundary: closed simulation ML red-blue interaction audit only; no RF, exploit, or live network action
