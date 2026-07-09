# Defense Effectiveness Ledger

This ledger joins each TSRA-R DefenseEvent to local mission-metric movement before and after the response window.
Safety boundary: closed simulation defense-effect ledger only; no RF, exploit, or live network action

## Summary

### E5_rule_aura_tsra_r

- Ledger rows: 22
- Actions: pace_switch=1, priority_reroute=6, stale_badge=8, video_throttle=7
- Observed effects: degraded_or_delayed=3, held=11, improved=8

### E7_ml_aura_ml_tsra_r

- Ledger rows: 34
- Actions: ml_attack_alert=9, pace_switch=3, priority_reroute=7, stale_badge=8, video_throttle=7
- Observed effects: degraded_or_delayed=5, held=14, improved=15

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
| E7_ml_aura_ml_tsra_r | 80 | def-00001 | ml_attack_alert | held | -0.111367 | 0.5 | -0.0625 | -0.16065 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 80 | def-00002 | priority_reroute | improved | -0.111367 | 0.5 | -0.0625 | -0.16065 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 80 | def-00003 | video_throttle | improved | -0.111367 | 0.5 | -0.0625 | -0.16065 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 80 | def-00004 | stale_badge | improved | -0.111367 | 0.5 | -0.0625 | -0.16065 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 80 | def-00005 | pace_switch | improved | -0.111367 | 0.5 | -0.0625 | -0.16065 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 105 | def-00006 | ml_attack_alert | held | -0.0497869 | -2.6 | 0 | -0.0649071 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| near_future; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 115 | def-00007 | video_throttle | improved | -0.0118609 | -2.65 | 0.0625 | -0.0571386 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| active; ml-atk-00002; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 120 | def-00008 | priority_reroute | improved | -0.00801011 | -2.45 | 0.0625 | -0.0521035 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 120 | def-00009 | stale_badge | held | -0.00801011 | -2.45 | 0.0625 | -0.0521035 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 130 | def-00010 | ml_attack_alert | held | 0.0250046 | -0.9 | 0.0625 | -0.0400741 | active; ml-atk-00001; queue_pressure; target=SATCOM \|\| active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 150 | def-00011 | video_throttle | improved | -0.0302738 | -4.95 | 0 | -0.0278809 | active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 150 | def-00012 | stale_badge | improved | -0.0302738 | -4.95 | 0 | -0.0278809 | active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 155 | def-00013 | ml_attack_alert | held | -0.0322123 | -5.4 | 0 | -0.0257579 | active; ml-atk-00002; failover_chasing; target=LTE \|\| near_future; ml-atk-00003; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 160 | def-00014 | priority_reroute | improved | -0.053849 | -6.3 | 0 | -0.0236979 | active; ml-atk-00002; failover_chasing; target=LTE \|\| active; ml-atk-00003; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 160 | def-00015 | pace_switch | improved | -0.053849 | -6.3 | 0 | -0.0236979 | active; ml-atk-00002; failover_chasing; target=LTE \|\| active; ml-atk-00003; queue_pressure; target=LTE |
| E7_ml_aura_ml_tsra_r | 180 | def-00016 | ml_attack_alert | held | -0.0186291 | -1.8 | 0 | -0.0132583 | active; ml-atk-00002; failover_chasing; target=LTE \|\| active; ml-atk-00003; queue_pressure; target=LTE \|\| near_future; ml-atk-00004; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 180 | def-00017 | stale_badge | held | -0.0186291 | -1.8 | 0 | -0.0132583 | active; ml-atk-00002; failover_chasing; target=LTE \|\| active; ml-atk-00003; queue_pressure; target=LTE \|\| near_future; ml-atk-00004; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 185 | def-00018 | video_throttle | improved | -0.0151687 | -1.35 | 0 | -0.0123373 | active; ml-atk-00003; queue_pressure; target=LTE \|\| near_future; ml-atk-00004; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 190 | def-00019 | priority_reroute | improved | -0.0389228 | 0.15 | -0.0625 | -0.0110955 | active; ml-atk-00003; queue_pressure; target=LTE \|\| near_future; ml-atk-00004; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 205 | def-00020 | ml_attack_alert | held | 0.00152214 | 1 | 0 | -0.0102891 | active; ml-atk-00003; queue_pressure; target=LTE \|\| near_future; ml-atk-00004; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 210 | def-00021 | stale_badge | improved | -0.0329911 | 1 | -0.0625 | -0.0105656 | active; ml-atk-00003; queue_pressure; target=LTE \|\| active; ml-atk-00004; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 215 | def-00022 | priority_reroute | held | -0.0162537 | 1 | -0.0625 | -0.0104241 | active; ml-atk-00003; queue_pressure; target=LTE \|\| active; ml-atk-00004; failover_chasing; target=MESH |
| E7_ml_aura_ml_tsra_r | 220 | def-00023 | video_throttle | held | 0.0146139 | 0.4 | 0 | -0.00943882 | active; ml-atk-00003; queue_pressure; target=LTE \|\| active; ml-atk-00004; failover_chasing; target=MESH \|\| near_future; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 230 | def-00024 | ml_attack_alert | held | -0.0214715 | 0 | -0.0625 | -0.00752625 | active; ml-atk-00003; queue_pressure; target=LTE \|\| active; ml-atk-00004; failover_chasing; target=MESH \|\| near_future; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 240 | def-00025 | stale_badge | degraded_or_delayed | 0.0826905 | 0 | 0.125 | -0.00545236 | active; ml-atk-00003; queue_pressure; target=LTE \|\| active; ml-atk-00004; failover_chasing; target=MESH \|\| near_future; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 245 | def-00026 | priority_reroute | degraded_or_delayed | 0.0663487 | 0 | 0.125 | -0.00480253 | active; ml-atk-00004; failover_chasing; target=MESH \|\| near_future; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 245 | def-00027 | pace_switch | degraded_or_delayed | 0.0663487 | 0 | 0.125 | -0.00480253 | active; ml-atk-00004; failover_chasing; target=MESH \|\| near_future; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 255 | def-00028 | ml_attack_alert | degraded_or_delayed | 0.0322485 | 0 | 0.0625 | -0.00425306 | active; ml-atk-00004; failover_chasing; target=MESH \|\| near_future; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 255 | def-00029 | video_throttle | degraded_or_delayed | 0.0322485 | 0 | 0.0625 | -0.00425306 | active; ml-atk-00004; failover_chasing; target=MESH \|\| near_future; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 270 | def-00030 | stale_badge | improved | -0.0364491 | 0 | -0.0625 | -0.00414811 | active; ml-atk-00004; failover_chasing; target=MESH \|\| active; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 275 | def-00031 | priority_reroute | improved | -0.0360042 | 0 | -0.0625 | -0.00325843 | active; ml-atk-00004; failover_chasing; target=MESH \|\| active; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 280 | def-00032 | ml_attack_alert | held | -0.00127063 | 0 | 0 | -0.00254126 | active; ml-atk-00004; failover_chasing; target=MESH \|\| active; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 290 | def-00033 | video_throttle | held | -0.000551239 | 0 | 0 | -0.00110248 | active; ml-atk-00005; failover_chasing; target=LTE |
| E7_ml_aura_ml_tsra_r | 300 | def-00034 | stale_badge | held | 0 | 0 | 0 | 0 | active; ml-atk-00005; failover_chasing; target=LTE |

## Interpretation Rule

- Negative mission impact, critical latency, trusted stale exposure, or priority inversion deltas are local improvement signals.
- `held` means TSRA-R kept the local window bounded rather than visibly reducing the scalar metric in that 30-second slice.
- `degraded_or_delayed` means the response occurred while mission impact was still rising or the response effect lagged the window.
