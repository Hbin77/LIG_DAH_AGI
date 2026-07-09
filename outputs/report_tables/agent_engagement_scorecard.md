# Agent Engagement Scorecard

This scorecard links each AURA attack decision margin to the TSRA-R response chain and mission-impact movement.
Safety boundary: closed simulation agent-engagement scorecard only; no RF, exploit, or live network action

## Summary

- Scorecard rows: 10
- Status counts: pass=10
- Experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r

## Engagement Rows

| experiment | attack_event_id | attack_type | attack_selection_margin | attack_threshold_margin | response_status | defense_event_count_in_window | impact_reduction_from_peak | scorecard_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E5_rule_aura_tsra_r | atk-00001 | queue_pressure | 0.109464 | 0.423691 | complete | 5 | 0.0626556 | pass |
| E5_rule_aura_tsra_r | atk-00002 | queue_pressure | 0.001674 | 0.796763 | complete | 3 | 0.0194333 | pass |
| E5_rule_aura_tsra_r | atk-00003 | queue_pressure | 0.081359 | 0.8575 | complete | 5 | 0.0021496 | pass |
| E5_rule_aura_tsra_r | atk-00004 | queue_pressure | 0.056345 | 0.8275 | complete | 2 | 0.0395898 | pass |
| E5_rule_aura_tsra_r | atk-00005 | queue_pressure | 0.045006 | 0.7835 | complete | 4 | 0.00214269 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00001 | queue_pressure | 0.072803 | 0.459505 | complete | 5 | 0.251649 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00002 | failover_chasing | 0.101344 | 0.721848 | complete | 4 | 0.025868 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00003 | failover_chasing | 0.1252 | 0.697403 | complete | 3 | 0.00132496 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00004 | queue_pressure | 0.165075 | 0.659372 | complete | 5 | 0.0375459 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00005 | stale_cop_induction | 0.150585 | 0.659393 | complete | 7 | 0.00176331 | pass |

## Notes

- E5_rule_aura_tsra_r atk-00001: attack choice, defense response, and metric movement are linked; actions=pace_switch, priority_reroute, stale_badge, video_throttle
- E5_rule_aura_tsra_r atk-00002: attack choice, defense response, and metric movement are linked; actions=priority_reroute, stale_badge, video_throttle
- E5_rule_aura_tsra_r atk-00003: attack choice, defense response, and metric movement are linked; actions=priority_reroute, stale_badge, video_throttle
- E5_rule_aura_tsra_r atk-00004: attack choice, defense response, and metric movement are linked; actions=priority_reroute, video_throttle
- E5_rule_aura_tsra_r atk-00005: attack choice, defense response, and metric movement are linked; actions=priority_reroute, stale_badge, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00001: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00002: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, pace_switch, priority_reroute, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00003: attack choice, defense response, and metric movement are linked; actions=priority_reroute, stale_badge
- E7_ml_aura_ml_tsra_r ml-atk-00004: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, priority_reroute, stale_badge, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00005: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
