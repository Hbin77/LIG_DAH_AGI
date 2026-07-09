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
| E5_rule_aura_tsra_r | atk-00003 | queue_pressure | 0.051469 | 0.8275 | complete | 4 | 0.00546539 | pass |
| E5_rule_aura_tsra_r | atk-00004 | queue_pressure | 0.057984 | 0.8275 | complete | 3 | 0.0201095 | pass |
| E5_rule_aura_tsra_r | atk-00005 | queue_pressure | 0.046724 | 0.7835 | complete | 3 | 0.00119899 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00001 | queue_pressure | 0.072803 | 0.459505 | complete | 5 | 0.205612 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00002 | failover_chasing | 0.018343 | 0.721793 | complete | 6 | 0.0213565 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00003 | queue_pressure | 0.09985 | 0.798255 | complete | 6 | 0.05886 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00004 | failover_chasing | 0.046648 | 0.625517 | complete | 7 | 0.0205729 | pass |
| E7_ml_aura_ml_tsra_r | ml-atk-00005 | failover_chasing | 0.048348 | 0.624854 | complete | 4 | 0.00262202 | pass |

## Notes

- E5_rule_aura_tsra_r atk-00001: attack choice, defense response, and metric movement are linked; actions=pace_switch, priority_reroute, stale_badge, video_throttle
- E5_rule_aura_tsra_r atk-00002: attack choice, defense response, and metric movement are linked; actions=priority_reroute, stale_badge, video_throttle
- E5_rule_aura_tsra_r atk-00003: attack choice, defense response, and metric movement are linked; actions=priority_reroute, stale_badge, video_throttle
- E5_rule_aura_tsra_r atk-00004: attack choice, defense response, and metric movement are linked; actions=pace_switch, priority_reroute, video_throttle
- E5_rule_aura_tsra_r atk-00005: attack choice, defense response, and metric movement are linked; actions=stale_badge, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00001: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00002: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, priority_reroute, stale_badge, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00003: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00004: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- E7_ml_aura_ml_tsra_r ml-atk-00005: attack choice, defense response, and metric movement are linked; actions=ml_attack_alert, stale_badge, video_throttle
