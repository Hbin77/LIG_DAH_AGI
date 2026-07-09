# Defense Effectiveness Ledger

This ledger joins each TSRA-R DefenseEvent to local mission-metric movement before and after the response window.
Safety boundary: closed simulation defense-effect ledger only; no RF, exploit, or live network action

## Summary

### E5_rule_aura_tsra_r

- Ledger rows: 22
- Actions: pace_switch=1, priority_reroute=6, stale_badge=8, video_throttle=7
- Observed effects: degraded_or_delayed=3, held=11, improved=8

### E7_ml_aura_ml_tsra_r

- Ledger rows: 30
- Actions: ml_attack_alert=8, pace_switch=3, priority_reroute=6, stale_badge=7, video_throttle=6
- Observed effects: degraded_or_delayed=6, held=15, improved=9

## Ledger Table

| experiment | time_sec | event_id | action | observed_effect | delta_mission_impact | delta_p95_critical_latency_sec | delta_trusted_stale_exposure | delta_priority_inversion_rate | related_attack_context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E5_rule_aura_tsra_r | 20 | def-00001 | stale_badge | held | 0.0193396 | 0 | 0 | 0.0386792 | near_future; atk-00001; queue_pressure; target=SATCOM |
| E5_rule_aura_tsra_r | 50 | def-00002 | stale_badge | held | -0.00717296 | 1.2 | 0 | -0.0636792 | near_future; atk-00001; queue_pressure; target=SATCOM |
| E5_rule_aura_tsra_r | 65 | def-00003 | priority_reroute | improved | -0.054479 | 1.1 | -0.0625 | -0.0882081 | active; atk-00001; queue_pressure; target=SATCOM |
| E5_rule_aura_tsra_r | 65 | def-00004 | video_throttle | improved | -0.054479 | 1.1 | -0.0625 | -0.0882081 | active; atk-00001; queue_pressure; target=SATCOM |
| E5_rule_aura_tsra_r | 75 | def-00005 | pace_switch | improved | -0.0686333 | -0.6 | -0.0625 | -0.0605167 | active; atk-00001; queue_pressure; target=SATCOM \|\| near_future; atk-00002; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 80 | def-00006 | stale_badge | improved | -0.0650655 | -0.8 | -0.0625 | -0.0507143 | active; atk-00001; queue_pressure; target=SATCOM \|\| near_future; atk-00002; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 100 | def-00007 | video_throttle | improved | -0.023975 | -1 | 0 | -0.0346167 | active; atk-00001; queue_pressure; target=SATCOM \|\| near_future; atk-00002; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 125 | def-00008 | priority_reroute | held | -0.00891563 | 0 | 0 | -0.0178313 | active; atk-00001; queue_pressure; target=SATCOM \|\| active; atk-00002; queue_pressure; target=LTE \|\| near_future; atk-00003; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 135 | def-00009 | video_throttle | held | 0.0274619 | 0 | 0.0625 | -0.0138263 | active; atk-00001; queue_pressure; target=SATCOM \|\| active; atk-00002; queue_pressure; target=LTE \|\| near_future; atk-00003; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 140 | def-00010 | stale_badge | degraded_or_delayed | 0.0311704 | 0.45 | 0.0625 | -0.0124092 | active; atk-00001; queue_pressure; target=SATCOM \|\| active; atk-00002; queue_pressure; target=LTE \|\| near_future; atk-00003; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 170 | def-00011 | video_throttle | held | 0.000962778 | 0.55 | 0 | -0.00540778 | active; atk-00002; queue_pressure; target=LTE \|\| active; atk-00003; queue_pressure; target=LTE \|\| near_future; atk-00004; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 170 | def-00012 | stale_badge | held | 0.000962778 | 0.55 | 0 | -0.00540778 | active; atk-00002; queue_pressure; target=LTE \|\| active; atk-00003; queue_pressure; target=LTE \|\| near_future; atk-00004; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 175 | def-00013 | priority_reroute | held | -0.00248391 | 0 | 0 | -0.00496781 | active; atk-00002; queue_pressure; target=LTE \|\| active; atk-00003; queue_pressure; target=LTE \|\| near_future; atk-00004; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 200 | def-00014 | priority_reroute | improved | -0.0361699 | 0 | -0.0625 | -0.00358979 | active; atk-00003; queue_pressure; target=LTE \|\| near_future; atk-00004; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 200 | def-00015 | stale_badge | improved | -0.0361699 | 0 | -0.0625 | -0.00358979 | active; atk-00003; queue_pressure; target=LTE \|\| near_future; atk-00004; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 205 | def-00016 | video_throttle | improved | -0.0363792 | -0.05 | -0.0625 | -0.00334169 | active; atk-00003; queue_pressure; target=LTE \|\| near_future; atk-00004; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 240 | def-00017 | video_throttle | degraded_or_delayed | 0.0311303 | -0.3 | 0.0625 | -0.0024894 | active; atk-00003; queue_pressure; target=LTE \|\| active; atk-00004; queue_pressure; target=LTE \|\| near_future; atk-00005; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 245 | def-00018 | priority_reroute | degraded_or_delayed | 0.0315514 | -0.25 | 0.0625 | -0.00231396 | active; atk-00004; queue_pressure; target=LTE \|\| near_future; atk-00005; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 265 | def-00019 | stale_badge | held | -0.00202615 | -0.15 | 0 | -0.0020523 | active; atk-00004; queue_pressure; target=LTE \|\| active; atk-00005; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 270 | def-00020 | priority_reroute | held | -0.00196568 | -0.15 | 0 | -0.00193136 | active; atk-00004; queue_pressure; target=LTE \|\| active; atk-00005; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 275 | def-00021 | video_throttle | held | -0.00144421 | -0.1 | 0 | -0.00155508 | active; atk-00004; queue_pressure; target=LTE \|\| active; atk-00005; queue_pressure; target=LTE |
| E5_rule_aura_tsra_r | 295 | def-00022 | stale_badge | held | -0.000116538 | 0 | 0 | -0.000233075 | active; atk-00005; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 70 | def-00001 | priority_reroute | improved | -0.0779006 | 1.5 | -0.0625 | -0.107051 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 70 | def-00002 | video_throttle | improved | -0.0779006 | 1.5 | -0.0625 | -0.107051 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 70 | def-00003 | stale_badge | improved | -0.0779006 | 1.5 | -0.0625 | -0.107051 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 70 | def-00004 | pace_switch | improved | -0.0779006 | 1.5 | -0.0625 | -0.107051 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 80 | def-00005 | ml_attack_alert | held | -0.0919379 | -3.3 | -0.0625 | -0.0711258 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 105 | def-00006 | ml_attack_alert | held | -0.0656828 | -1.5 | -0.0625 | -0.0426156 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 105 | def-00007 | priority_reroute | improved | -0.0656828 | -1.5 | -0.0625 | -0.0426156 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 105 | def-00008 | video_throttle | improved | -0.0656828 | -1.5 | -0.0625 | -0.0426156 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 105 | def-00009 | stale_badge | improved | -0.0656828 | -1.5 | -0.0625 | -0.0426156 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 130 | def-00010 | ml_attack_alert | held | 0.00546442 | 0 | 0 | -0.0224045 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 130 | def-00011 | priority_reroute | held | 0.00546442 | 0 | 0 | -0.0224045 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 140 | def-00012 | video_throttle | degraded_or_delayed | 0.0423545 | 0 | 0.0625 | -0.0173744 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 150 | def-00013 | pace_switch | held | 0.0272148 | 0 | 0.0625 | -0.0143204 | active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 155 | def-00014 | ml_attack_alert | degraded_or_delayed | 0.0313713 | 0.5 | 0.0625 | -0.0126741 | active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 160 | def-00015 | stale_badge | held | 0.00118788 | 1 | 0 | -0.0109576 | active; ml-atk-00002; failover_chasing; target=LTE \|\| active; ml-atk-00003; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 175 | def-00016 | priority_reroute | held | 0.00249154 | 1 | 0 | -0.00835025 | active; ml-atk-00002; failover_chasing; target=LTE \|\| active; ml-atk-00003; failover_chasing; target=MESH \|\| near_future; ml-atk-00004; queue_pressure; target=MESH |
| E7_ml_aura_ml_tsra_r | 190 | def-00017 | stale_badge | improved | -0.037906 | 0 | -0.0625 | -0.00706201 | active; ml-atk-00003; failover_chasing; target=MESH \|\| near_future; ml-atk-00004; queue_pressure; target=MESH |
| E7_ml_aura_ml_tsra_r | 205 | def-00018 | video_throttle | held | -0.00297604 | 0 | 0 | -0.00595209 | active; ml-atk-00003; failover_chasing; target=MESH \|\| near_future; ml-atk-00004; queue_pressure; target=MESH |
| E7_ml_aura_ml_tsra_r | 220 | def-00019 | ml_attack_alert | held | -0.00248212 | 0 | 0 | -0.00496424 | active; ml-atk-00003; failover_chasing; target=MESH \|\| active; ml-atk-00004; queue_pressure; target=MESH \|\| near_future; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 220 | def-00020 | priority_reroute | held | -0.00248212 | 0 | 0 | -0.00496424 | active; ml-atk-00003; failover_chasing; target=MESH \|\| active; ml-atk-00004; queue_pressure; target=MESH \|\| near_future; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 235 | def-00021 | stale_badge | improved | -0.019793 | 0 | -0.0625 | -0.00416928 | active; ml-atk-00004; queue_pressure; target=MESH \|\| near_future; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 240 | def-00022 | video_throttle | degraded_or_delayed | 0.0490044 | 0 | 0.0625 | -0.00407462 | active; ml-atk-00004; queue_pressure; target=MESH \|\| near_future; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 245 | def-00023 | ml_attack_alert | degraded_or_delayed | 0.0490156 | 0 | 0.0625 | -0.00405208 | active; ml-atk-00004; queue_pressure; target=MESH \|\| near_future; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 260 | def-00024 | priority_reroute | degraded_or_delayed | 0.0324964 | 0 | 0.0625 | -0.00375716 | active; ml-atk-00004; queue_pressure; target=MESH \|\| active; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 260 | def-00025 | pace_switch | degraded_or_delayed | 0.0324964 | 0 | 0.0625 | -0.00375716 | active; ml-atk-00004; queue_pressure; target=MESH \|\| active; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 270 | def-00026 | ml_attack_alert | held | -0.00176331 | 0 | 0 | -0.00352661 | active; ml-atk-00004; queue_pressure; target=MESH \|\| active; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 270 | def-00027 | stale_badge | held | -0.00176331 | 0 | 0 | -0.00352661 | active; ml-atk-00004; queue_pressure; target=MESH \|\| active; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 275 | def-00028 | video_throttle | held | -0.00146257 | 0 | 0 | -0.00292514 | active; ml-atk-00004; queue_pressure; target=MESH \|\| active; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 295 | def-00029 | ml_attack_alert | held | -0.000270678 | 0 | 0 | -0.000541356 | active; ml-atk-00005; stale_cop_induction; target=MESH |
| E7_ml_aura_ml_tsra_r | 300 | def-00030 | stale_badge | held | 0 | 0 | 0 | 0 | active; ml-atk-00005; stale_cop_induction; target=MESH |

## Interpretation Rule

- Negative mission impact, critical latency, trusted stale exposure, or priority inversion deltas are local improvement signals.
- `held` means TSRA-R kept the local window bounded rather than visibly reducing the scalar metric in that 30-second slice.
- `degraded_or_delayed` means the response occurred while mission impact was still rising or the response effect lagged the window.
