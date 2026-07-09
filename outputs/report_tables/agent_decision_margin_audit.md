# Agent Decision Margin Audit

This audit explains how much decision support existed for each AURA/TSRA-R selected action.
Safety boundary: closed simulation decision-margin audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 399
- Action rows: 110
- Threshold rows: 86
- Status counts: pass=399
- Agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML

## Sample Action Margins

- E3_rule_aura 60s AURA queue_pressure: basis=top_attack_score_minus_runner_up_and_threshold, selected=0.543691, runner_up=0.434227, margin=0.109464, threshold_margin=0.423691
- E3_rule_aura 110s AURA bandwidth_limit: basis=top_attack_score_minus_runner_up_and_threshold, selected=0.9475, runner_up=0.9475, margin=0, threshold_margin=0.8275
- E3_rule_aura 160s AURA bandwidth_limit: basis=top_attack_score_minus_runner_up_and_threshold, selected=0.9475, runner_up=0.9475, margin=0, threshold_margin=0.8275
- E3_rule_aura 210s AURA bandwidth_limit: basis=top_attack_score_minus_runner_up_and_threshold, selected=0.9475, runner_up=0.9475, margin=0, threshold_margin=0.8275
- E3_rule_aura 260s AURA stale_cop_induction: basis=top_attack_score_minus_runner_up_and_threshold, selected=0.9175, runner_up=0.9035, margin=0.014, threshold_margin=0.7975
- E4_rule_aura_basic_defense 20s TSRA-R stale_badge: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 50s TSRA-R stale_badge: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 60s AURA queue_pressure: basis=top_attack_score_minus_runner_up_and_threshold, selected=0.543691, runner_up=0.434227, margin=0.109464, threshold_margin=0.423691
- E4_rule_aura_basic_defense 65s TSRA-R priority_reroute, video_throttle: basis=selected_all_eligible_ready_defense_actions, selected=2, runner_up=n/a, margin=2, threshold_margin=n/a
- E4_rule_aura_basic_defense 80s TSRA-R stale_badge: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 90s TSRA-R priority_reroute: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 100s TSRA-R video_throttle: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 110s AURA queue_pressure: basis=top_attack_score_minus_runner_up_and_threshold, selected=0.9335, runner_up=0.88506, margin=0.04844, threshold_margin=0.8135
- E4_rule_aura_basic_defense 115s TSRA-R priority_reroute: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 135s TSRA-R video_throttle: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 140s TSRA-R priority_reroute: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 145s TSRA-R stale_badge: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a
- E4_rule_aura_basic_defense 160s AURA queue_pressure: basis=top_attack_score_minus_runner_up_and_threshold, selected=0.9475, runner_up=0.900372, margin=0.047128, threshold_margin=0.8275
- E4_rule_aura_basic_defense 170s TSRA-R priority_reroute, video_throttle: basis=selected_all_eligible_ready_defense_actions, selected=2, runner_up=n/a, margin=2, threshold_margin=n/a
- E4_rule_aura_basic_defense 175s TSRA-R stale_badge: basis=selected_all_eligible_ready_defense_actions, selected=1, runner_up=n/a, margin=1, threshold_margin=n/a

## Failures

None.

## Audit Table

| experiment | time_sec | agent | selected_actions | decision_basis | selection_margin | threshold_margin | margin_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E3_rule_aura | 0 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 10 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 20 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 30 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 40 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 50 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 60 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.109464 | 0.423691 | pass |
| E3_rule_aura | 70 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 80 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 90 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 100 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 110 | AURA | bandwidth_limit | top_attack_score_minus_runner_up_and_threshold | 0 | 0.8275 | pass |
| E3_rule_aura | 120 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 130 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 140 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 150 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 160 | AURA | bandwidth_limit | top_attack_score_minus_runner_up_and_threshold | 0 | 0.8275 | pass |
| E3_rule_aura | 170 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 180 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 190 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 200 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 210 | AURA | bandwidth_limit | top_attack_score_minus_runner_up_and_threshold | 0 | 0.8275 | pass |
| E3_rule_aura | 220 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 230 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 240 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 250 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 260 | AURA | stale_cop_induction | top_attack_score_minus_runner_up_and_threshold | 0.014 | 0.7975 | pass |
| E3_rule_aura | 270 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 280 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 290 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E3_rule_aura | 300 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 0 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 0 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 5 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 10 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 10 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 15 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 20 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 20 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 25 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 30 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 30 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 35 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 40 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 40 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 45 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 50 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 50 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 55 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 60 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.109464 | 0.423691 | pass |
| E4_rule_aura_basic_defense | 60 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 65 | TSRA-R | priority_reroute, video_throttle | selected_all_eligible_ready_defense_actions | 2 |  | pass |
| E4_rule_aura_basic_defense | 70 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 70 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 75 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 80 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 80 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 85 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 90 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 90 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 95 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 100 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 100 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 105 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 110 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.04844 | 0.8135 | pass |
| E4_rule_aura_basic_defense | 110 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 115 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 120 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 120 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 125 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 130 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 130 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 135 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 140 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 140 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 145 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 150 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 150 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 155 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 160 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.047128 | 0.8275 | pass |
| E4_rule_aura_basic_defense | 160 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 165 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 170 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 170 | TSRA-R | priority_reroute, video_throttle | selected_all_eligible_ready_defense_actions | 2 |  | pass |
| E4_rule_aura_basic_defense | 175 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 180 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 180 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 185 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 190 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 190 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 195 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 200 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 200 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 205 | TSRA-R | video_throttle, stale_badge | selected_all_eligible_ready_defense_actions | 2 |  | pass |
| E4_rule_aura_basic_defense | 210 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.053835 | 0.8275 | pass |
| E4_rule_aura_basic_defense | 210 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 215 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 220 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 220 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 225 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 230 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 230 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 235 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 240 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 240 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 245 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 250 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 250 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 255 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 260 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.043426 | 0.7835 | pass |
| E4_rule_aura_basic_defense | 260 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 265 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 270 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 270 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 275 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 280 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 280 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 285 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 290 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 290 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E4_rule_aura_basic_defense | 295 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E4_rule_aura_basic_defense | 300 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E4_rule_aura_basic_defense | 300 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 0 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 0 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 5 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 10 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 10 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 15 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 20 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 20 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 25 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 30 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 30 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 35 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 40 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 40 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 45 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 50 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 50 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 55 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 60 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.109464 | 0.423691 | pass |
| E5_rule_aura_tsra_r | 60 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 65 | TSRA-R | priority_reroute, video_throttle | selected_all_eligible_ready_defense_actions | 2 |  | pass |
| E5_rule_aura_tsra_r | 70 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 70 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 75 | TSRA-R | pace_switch | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 80 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 80 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 85 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 90 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 90 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 95 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 100 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 100 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 105 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 110 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.001674 | 0.796763 | pass |
| E5_rule_aura_tsra_r | 110 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 115 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 120 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 120 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 125 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 130 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 130 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 135 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 140 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 140 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 145 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 150 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 150 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 155 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 160 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.081359 | 0.8575 | pass |
| E5_rule_aura_tsra_r | 160 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 165 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 170 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 170 | TSRA-R | video_throttle, stale_badge | selected_all_eligible_ready_defense_actions | 2 |  | pass |
| E5_rule_aura_tsra_r | 175 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 180 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 180 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 185 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 190 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 190 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 195 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 200 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 200 | TSRA-R | priority_reroute, stale_badge | selected_all_eligible_ready_defense_actions | 2 |  | pass |
| E5_rule_aura_tsra_r | 205 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 210 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.056345 | 0.8275 | pass |
| E5_rule_aura_tsra_r | 210 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 215 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 220 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 220 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 225 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 230 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 230 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 235 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 240 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 240 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 245 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 250 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 250 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 255 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 260 | AURA | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.045006 | 0.7835 | pass |
| E5_rule_aura_tsra_r | 260 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 265 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 270 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 270 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 275 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 280 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 280 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 285 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 290 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 290 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E5_rule_aura_tsra_r | 295 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E5_rule_aura_tsra_r | 300 | AURA | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E5_rule_aura_tsra_r | 300 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 0 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 0 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 5 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 10 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 10 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 15 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 20 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 20 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 25 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 30 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 30 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 35 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 40 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 40 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 45 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 50 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 50 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 55 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 60 | AURA-ML | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.072803 | 0.459505 | pass |
| E6_ml_aura_tsra_r | 60 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 65 | TSRA-R | priority_reroute, video_throttle | selected_all_eligible_ready_defense_actions | 2 |  | pass |
| E6_ml_aura_tsra_r | 70 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 70 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 75 | TSRA-R | pace_switch | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 80 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 80 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 85 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 90 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 90 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 95 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 100 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 100 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 105 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 110 | AURA-ML | failover_chasing | top_attack_score_minus_runner_up_and_threshold | 0.012864 | 0.634678 | pass |
| E6_ml_aura_tsra_r | 110 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 115 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 120 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 120 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 125 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 130 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 130 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 135 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 140 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 140 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 145 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 150 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 150 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 155 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 160 | AURA-ML | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.075032 | 0.753385 | pass |
| E6_ml_aura_tsra_r | 160 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 165 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 170 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 170 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 175 | TSRA-R | priority_reroute, pace_switch | selected_all_eligible_ready_defense_actions | 2 |  | pass |
| E6_ml_aura_tsra_r | 180 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 180 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 185 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 190 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 190 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 195 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 200 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 200 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 205 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 210 | AURA-ML | failover_chasing | top_attack_score_minus_runner_up_and_threshold | 0.02877 | 0.611039 | pass |
| E6_ml_aura_tsra_r | 210 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 215 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 220 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 220 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 225 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 230 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 230 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 235 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 240 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 240 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 245 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 250 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 250 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 255 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 260 | AURA-ML | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.090416 | 0.696681 | pass |
| E6_ml_aura_tsra_r | 260 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 265 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 270 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 270 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 275 | TSRA-R | video_throttle | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 280 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 280 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 285 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 290 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 290 | TSRA-R | no_op | eligible_ready_defense_conditions |  |  | pass |
| E6_ml_aura_tsra_r | 295 | TSRA-R | stale_badge | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E6_ml_aura_tsra_r | 300 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E6_ml_aura_tsra_r | 300 | TSRA-R | priority_reroute | selected_all_eligible_ready_defense_actions | 1 |  | pass |
| E7_ml_aura_ml_tsra_r | 0 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 0 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.467141 | pass |
| E7_ml_aura_ml_tsra_r | 5 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.467141 | pass |
| E7_ml_aura_ml_tsra_r | 10 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 10 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.502286 | pass |
| E7_ml_aura_ml_tsra_r | 15 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.491268 | pass |
| E7_ml_aura_ml_tsra_r | 20 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 20 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.473575 | pass |
| E7_ml_aura_ml_tsra_r | 25 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.484872 | pass |
| E7_ml_aura_ml_tsra_r | 30 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 30 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.478094 | pass |
| E7_ml_aura_ml_tsra_r | 35 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.469871 | pass |
| E7_ml_aura_ml_tsra_r | 40 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 40 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.48226 | pass |
| E7_ml_aura_ml_tsra_r | 45 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.520533 | pass |
| E7_ml_aura_ml_tsra_r | 50 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 50 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.475889 | pass |
| E7_ml_aura_ml_tsra_r | 55 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.460104 | pass |
| E7_ml_aura_ml_tsra_r | 60 | AURA-ML | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.072803 | 0.459505 | pass |
| E7_ml_aura_ml_tsra_r | 60 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.483305 | pass |
| E7_ml_aura_ml_tsra_r | 65 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.340495 | pass |
| E7_ml_aura_ml_tsra_r | 70 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 70 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.246432 | pass |
| E7_ml_aura_ml_tsra_r | 75 | TSRA-R-ML | no_op | probability_below_threshold_no_window |  | -0.227696 | pass |
| E7_ml_aura_ml_tsra_r | 80 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 80 | TSRA-R-ML | ml_attack_alert, priority_reroute, video_throttle, stale_badge, pace_switch | probability_above_threshold |  | 0.196005 | pass |
| E7_ml_aura_ml_tsra_r | 85 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.206653 | pass |
| E7_ml_aura_ml_tsra_r | 90 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 90 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.208644 | pass |
| E7_ml_aura_ml_tsra_r | 95 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.201098 | pass |
| E7_ml_aura_ml_tsra_r | 100 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 100 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.201098 | pass |
| E7_ml_aura_ml_tsra_r | 105 | TSRA-R-ML | ml_attack_alert | probability_above_threshold |  | 0.201098 | pass |
| E7_ml_aura_ml_tsra_r | 110 | AURA-ML | failover_chasing | top_attack_score_minus_runner_up_and_threshold | 0.018343 | 0.721793 | pass |
| E7_ml_aura_ml_tsra_r | 110 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.221653 | pass |
| E7_ml_aura_ml_tsra_r | 115 | TSRA-R-ML | video_throttle | probability_above_threshold |  | 0.221653 | pass |
| E7_ml_aura_ml_tsra_r | 120 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 120 | TSRA-R-ML | priority_reroute, stale_badge | probability_above_threshold |  | 0.224431 | pass |
| E7_ml_aura_ml_tsra_r | 125 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.221653 | pass |
| E7_ml_aura_ml_tsra_r | 130 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 130 | TSRA-R-ML | ml_attack_alert | probability_above_threshold |  | 0.221653 | pass |
| E7_ml_aura_ml_tsra_r | 135 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.221653 | pass |
| E7_ml_aura_ml_tsra_r | 140 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 140 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.217685 | pass |
| E7_ml_aura_ml_tsra_r | 145 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.216296 | pass |
| E7_ml_aura_ml_tsra_r | 150 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 150 | TSRA-R-ML | video_throttle, stale_badge | probability_above_threshold |  | 0.21213 | pass |
| E7_ml_aura_ml_tsra_r | 155 | TSRA-R-ML | ml_attack_alert | probability_above_threshold |  | 0.21213 | pass |
| E7_ml_aura_ml_tsra_r | 160 | AURA-ML | queue_pressure | top_attack_score_minus_runner_up_and_threshold | 0.09985 | 0.798255 | pass |
| E7_ml_aura_ml_tsra_r | 160 | TSRA-R-ML | priority_reroute, pace_switch | probability_above_threshold |  | 0.219074 | pass |
| E7_ml_aura_ml_tsra_r | 165 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.220463 | pass |
| E7_ml_aura_ml_tsra_r | 170 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 170 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.204861 | pass |
| E7_ml_aura_ml_tsra_r | 175 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.22963 | pass |
| E7_ml_aura_ml_tsra_r | 180 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 180 | TSRA-R-ML | ml_attack_alert, stale_badge | probability_above_threshold |  | 0.209167 | pass |
| E7_ml_aura_ml_tsra_r | 185 | TSRA-R-ML | video_throttle | probability_above_threshold |  | 0.209167 | pass |
| E7_ml_aura_ml_tsra_r | 190 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 190 | TSRA-R-ML | priority_reroute | probability_above_threshold |  | 0.213532 | pass |
| E7_ml_aura_ml_tsra_r | 195 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.210225 | pass |
| E7_ml_aura_ml_tsra_r | 200 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 200 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.207447 | pass |
| E7_ml_aura_ml_tsra_r | 205 | TSRA-R-ML | ml_attack_alert | probability_above_threshold |  | 0.207447 | pass |
| E7_ml_aura_ml_tsra_r | 210 | AURA-ML | failover_chasing | top_attack_score_minus_runner_up_and_threshold | 0.046648 | 0.625517 | pass |
| E7_ml_aura_ml_tsra_r | 210 | TSRA-R-ML | stale_badge | probability_above_threshold |  | 0.18095 | pass |
| E7_ml_aura_ml_tsra_r | 215 | TSRA-R-ML | priority_reroute | probability_above_threshold |  | 0.189345 | pass |
| E7_ml_aura_ml_tsra_r | 220 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 220 | TSRA-R-ML | video_throttle | probability_above_threshold |  | 0.179892 | pass |
| E7_ml_aura_ml_tsra_r | 225 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.183331 | pass |
| E7_ml_aura_ml_tsra_r | 230 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 230 | TSRA-R-ML | ml_attack_alert | probability_above_threshold |  | 0.184522 | pass |
| E7_ml_aura_ml_tsra_r | 235 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.184522 | pass |
| E7_ml_aura_ml_tsra_r | 240 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 240 | TSRA-R-ML | stale_badge | probability_above_threshold |  | 0.173719 | pass |
| E7_ml_aura_ml_tsra_r | 245 | TSRA-R-ML | priority_reroute, pace_switch | probability_above_threshold |  | 0.177485 | pass |
| E7_ml_aura_ml_tsra_r | 250 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 250 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.173781 | pass |
| E7_ml_aura_ml_tsra_r | 255 | TSRA-R-ML | ml_attack_alert, video_throttle | probability_above_threshold |  | 0.163534 | pass |
| E7_ml_aura_ml_tsra_r | 260 | AURA-ML | failover_chasing | top_attack_score_minus_runner_up_and_threshold | 0.059656 | 0.588246 | pass |
| E7_ml_aura_ml_tsra_r | 260 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.191744 | pass |
| E7_ml_aura_ml_tsra_r | 265 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.192207 | pass |
| E7_ml_aura_ml_tsra_r | 270 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 270 | TSRA-R-ML | stale_badge | probability_above_threshold |  | 0.192207 | pass |
| E7_ml_aura_ml_tsra_r | 275 | TSRA-R-ML | priority_reroute | probability_above_threshold |  | 0.190355 | pass |
| E7_ml_aura_ml_tsra_r | 280 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 280 | TSRA-R-ML | ml_attack_alert | probability_above_threshold |  | 0.213056 | pass |
| E7_ml_aura_ml_tsra_r | 285 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.213056 | pass |
| E7_ml_aura_ml_tsra_r | 290 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 290 | TSRA-R-ML | video_throttle | probability_above_threshold |  | 0.213056 | pass |
| E7_ml_aura_ml_tsra_r | 295 | TSRA-R-ML | no_op | active_window_without_downstream_event |  | 0.213056 | pass |
| E7_ml_aura_ml_tsra_r | 300 | AURA-ML | no_op | pre_start_or_cooldown_no_candidates |  |  | pass |
| E7_ml_aura_ml_tsra_r | 300 | TSRA-R-ML | stale_badge | probability_above_threshold |  | 0.213056 | pass |
