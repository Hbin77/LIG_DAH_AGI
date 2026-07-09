# Agent Goal Alignment Audit

This audit checks whether AURA and TSRA-R decisions align with their stated attack or defense goals, not only whether the trace schema is valid.
Safety boundary: closed simulation agent goal-alignment audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 399
- Status counts: pass=399
- Agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML

## Goal Checks

- AURA attack events must clear the attack threshold, match the top score, and carry positive predicted mission impact.
- AURA no-op decisions must cite cadence, budget, candidate, or score-gate reasons.
- TSRA-R defense events must match priority, video, stale-data, PACE, or ML-threshold conditions in the observation.
- TSRA-R no-op decisions must have no ready rule action or must maintain a detector-controlled window.

## Sample Failures

None.

## Audit Table

| experiment | time_sec | agent | selected_actions | goal_signal | goal_alignment_status |
| --- | --- | --- | --- | --- | --- |
| E3_rule_aura | 0 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E3_rule_aura | 10 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E3_rule_aura | 20 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E3_rule_aura | 30 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E3_rule_aura | 40 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E3_rule_aura | 50 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E3_rule_aura | 60 | AURA | queue_pressure | selected_score=0.543691; top_score=0.543691; attack_threshold=0.12; predicted_mission_impact=0.566191; detectability_score=0.15 | pass |
| E3_rule_aura | 70 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 80 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 90 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 100 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 110 | AURA | bandwidth_limit | selected_score=0.9475; top_score=0.9475; attack_threshold=0.12; predicted_mission_impact=1; detectability_score=0.35 | pass |
| E3_rule_aura | 120 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 130 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 140 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 150 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 160 | AURA | bandwidth_limit | selected_score=0.9475; top_score=0.9475; attack_threshold=0.12; predicted_mission_impact=1; detectability_score=0.35 | pass |
| E3_rule_aura | 170 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 180 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 190 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 200 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 210 | AURA | bandwidth_limit | selected_score=0.9475; top_score=0.9475; attack_threshold=0.12; predicted_mission_impact=1; detectability_score=0.35 | pass |
| E3_rule_aura | 220 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 230 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 240 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 250 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E3_rule_aura | 260 | AURA | stale_cop_induction | selected_score=0.9175; top_score=0.9175; attack_threshold=0.12; predicted_mission_impact=1; detectability_score=0.55 | pass |
| E3_rule_aura | 270 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E3_rule_aura | 280 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E3_rule_aura | 290 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E3_rule_aura | 300 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 0 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 0 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 5 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 10 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 10 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 15 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 20 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 20 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=0; stale_data_ratio=0.5; total_queue_kb=0; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 25 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 30 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 30 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 35 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 40 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 40 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 45 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 50 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 50 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=0; stale_data_ratio=0.5; total_queue_kb=0; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 55 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 60 | AURA | queue_pressure | selected_score=0.543691; top_score=0.543691; attack_threshold=0.12; predicted_mission_impact=0.566191; detectability_score=0.15 | pass |
| E4_rule_aura_basic_defense | 60 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 65 | TSRA-R | priority_reroute, video_throttle | critical_pending=1; video_queue_kb=3560.49; stale_data_ratio=0.5; total_queue_kb=3604.15; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 70 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 70 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 75 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 80 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 80 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=8053.78; stale_data_ratio=0.5; total_queue_kb=8081.5; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 85 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 90 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 90 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=10081; stale_data_ratio=0.5; total_queue_kb=10088.4; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 95 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 100 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 100 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=13878.5; stale_data_ratio=0.25; total_queue_kb=13914.3; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 105 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 110 | AURA | queue_pressure | selected_score=0.9335; top_score=0.9335; attack_threshold=0.12; predicted_mission_impact=0.956; detectability_score=0.15 | pass |
| E4_rule_aura_basic_defense | 110 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 115 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=18752.1; stale_data_ratio=0.25; total_queue_kb=18759.2; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 120 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 120 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 125 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 130 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 130 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 135 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=31913.7; stale_data_ratio=0.25; total_queue_kb=31944.4; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 140 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 140 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=35603.8; stale_data_ratio=0.25; total_queue_kb=35613.3; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 145 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=37269.4; stale_data_ratio=0.5; total_queue_kb=37302.2; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 150 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 150 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 155 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 160 | AURA | queue_pressure | selected_score=0.9475; top_score=0.9475; attack_threshold=0.12; predicted_mission_impact=1; detectability_score=0.35 | pass |
| E4_rule_aura_basic_defense | 160 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 165 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 170 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 170 | TSRA-R | priority_reroute, video_throttle | critical_pending=1; video_queue_kb=46495.2; stale_data_ratio=0.5; total_queue_kb=46540.9; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 175 | TSRA-R | stale_badge | critical_pending=2; video_queue_kb=48743.3; stale_data_ratio=0.5; total_queue_kb=48789.3; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 180 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 180 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 185 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 190 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 190 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 195 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=59565.2; stale_data_ratio=0.5; total_queue_kb=59607.4; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 200 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 200 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 205 | TSRA-R | video_throttle, stale_badge | critical_pending=0; video_queue_kb=62770.5; stale_data_ratio=0.5; total_queue_kb=62770.5; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 210 | AURA | queue_pressure | selected_score=0.9475; top_score=0.9475; attack_threshold=0.12; predicted_mission_impact=1; detectability_score=0.35 | pass |
| E4_rule_aura_basic_defense | 210 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 215 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 220 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 220 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=71395.6; stale_data_ratio=0.25; total_queue_kb=71434.9; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 225 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 230 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 230 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 235 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=79093.7; stale_data_ratio=0.5; total_queue_kb=79125.9; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 240 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 240 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=83158.5; stale_data_ratio=0.5; total_queue_kb=83191.3; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 245 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 250 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 250 | TSRA-R | priority_reroute | critical_pending=2; video_queue_kb=85417.3; stale_data_ratio=0.25; total_queue_kb=85464.9; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 255 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 260 | AURA | queue_pressure | selected_score=0.9035; top_score=0.9035; attack_threshold=0.12; predicted_mission_impact=0.956; detectability_score=0.35 | pass |
| E4_rule_aura_basic_defense | 260 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 265 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=91147.2; stale_data_ratio=0.5; total_queue_kb=91182.5; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 270 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 270 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 275 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=96065.9; stale_data_ratio=0.5; total_queue_kb=96099.3; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 280 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 280 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 285 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 290 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 290 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E4_rule_aura_basic_defense | 295 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=108136; stale_data_ratio=0.5; total_queue_kb=108165; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E4_rule_aura_basic_defense | 300 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E4_rule_aura_basic_defense | 300 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 0 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 0 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 5 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 10 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 10 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 15 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 20 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 20 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=0; stale_data_ratio=0.5; total_queue_kb=0; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 25 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 30 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 30 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 35 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 40 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 40 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 45 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 50 | AURA | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 50 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=0; stale_data_ratio=0.5; total_queue_kb=0; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 55 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 60 | AURA | queue_pressure | selected_score=0.543691; top_score=0.543691; attack_threshold=0.12; predicted_mission_impact=0.566191; detectability_score=0.15 | pass |
| E5_rule_aura_tsra_r | 60 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 65 | TSRA-R | priority_reroute, video_throttle | critical_pending=1; video_queue_kb=3560.49; stale_data_ratio=0.5; total_queue_kb=3604.15; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 70 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 70 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 75 | TSRA-R | pace_switch | critical_pending=1; video_queue_kb=5260.95; stale_data_ratio=0.5; total_queue_kb=5297.75; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 80 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 80 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=7350.76; stale_data_ratio=0.5; total_queue_kb=7384.89; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 85 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 90 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 90 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 95 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 100 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 100 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=11100.8; stale_data_ratio=0.25; total_queue_kb=11129.1; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 105 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 110 | AURA | queue_pressure | selected_score=0.916763; top_score=0.916763; attack_threshold=0.12; predicted_mission_impact=0.939263; detectability_score=0.15 | pass |
| E5_rule_aura_tsra_r | 110 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 115 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 120 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 120 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 125 | TSRA-R | priority_reroute | critical_pending=2; video_queue_kb=20250.9; stale_data_ratio=0.25; total_queue_kb=20301.1; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 130 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 130 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 135 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=23450.4; stale_data_ratio=0.25; total_queue_kb=23485.9; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 140 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 140 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=26552.7; stale_data_ratio=0.5; total_queue_kb=26552.7; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 145 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 150 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 150 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 155 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 160 | AURA | queue_pressure | selected_score=0.9775; top_score=0.9775; attack_threshold=0.12; predicted_mission_impact=1; detectability_score=0.15 | pass |
| E5_rule_aura_tsra_r | 160 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 165 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 170 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 170 | TSRA-R | video_throttle, stale_badge | critical_pending=0; video_queue_kb=19591.3; stale_data_ratio=0.5; total_queue_kb=19620.5; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 175 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=22187.4; stale_data_ratio=0.5; total_queue_kb=22198.6; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 180 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 180 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 185 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 190 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 190 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 195 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 200 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 200 | TSRA-R | priority_reroute, stale_badge | critical_pending=1; video_queue_kb=35317.7; stale_data_ratio=0.5; total_queue_kb=35359.3; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 205 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=35980.4; stale_data_ratio=0.5; total_queue_kb=36009.2; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 210 | AURA | queue_pressure | selected_score=0.9475; top_score=0.9475; attack_threshold=0.12; predicted_mission_impact=1; detectability_score=0.35 | pass |
| E5_rule_aura_tsra_r | 210 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 215 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 220 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 220 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 225 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 230 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 230 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 235 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 240 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 240 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=54904.6; stale_data_ratio=0.25; total_queue_kb=54939.2; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 245 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=56591.4; stale_data_ratio=0.25; total_queue_kb=56628.4; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 250 | AURA | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 250 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 255 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 260 | AURA | queue_pressure | selected_score=0.9035; top_score=0.9035; attack_threshold=0.12; predicted_mission_impact=0.956; detectability_score=0.35 | pass |
| E5_rule_aura_tsra_r | 260 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 265 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=63571.2; stale_data_ratio=0.5; total_queue_kb=63571.2; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 270 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 270 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=65733.9; stale_data_ratio=0.5; total_queue_kb=65776.5; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 275 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=68473.3; stale_data_ratio=0.5; total_queue_kb=68507.9; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 280 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 280 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 285 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 290 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 290 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E5_rule_aura_tsra_r | 295 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=80599.5; stale_data_ratio=0.5; total_queue_kb=80629.4; active_link=LTE; probability=0; threshold=0.75 | pass |
| E5_rule_aura_tsra_r | 300 | AURA | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E5_rule_aura_tsra_r | 300 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 0 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 0 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 5 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 10 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 10 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 15 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 20 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 20 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=0; stale_data_ratio=0.5; total_queue_kb=0; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 25 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 30 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 30 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 35 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 40 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 40 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 45 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 50 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 50 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=0; stale_data_ratio=0.5; total_queue_kb=0; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 55 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 60 | AURA-ML | queue_pressure | selected_score=0.579505; top_score=0.579505; attack_threshold=0.12; predicted_mission_impact=0.602005; detectability_score=0.15 | pass |
| E6_ml_aura_tsra_r | 60 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 65 | TSRA-R | priority_reroute, video_throttle | critical_pending=1; video_queue_kb=3560.49; stale_data_ratio=0.5; total_queue_kb=3604.15; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 70 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 70 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 75 | TSRA-R | pace_switch | critical_pending=1; video_queue_kb=5260.95; stale_data_ratio=0.5; total_queue_kb=5297.75; active_link=SATCOM; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 80 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 80 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=7350.76; stale_data_ratio=0.5; total_queue_kb=7384.89; active_link=LTE; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 85 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 90 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 90 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 95 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 100 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 100 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=11100.8; stale_data_ratio=0.25; total_queue_kb=11129.1; active_link=LTE; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 105 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 110 | AURA-ML | failover_chasing | selected_score=0.754678; top_score=0.754678; attack_threshold=0.12; predicted_mission_impact=0.829678; detectability_score=0.5 | pass |
| E6_ml_aura_tsra_r | 110 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 115 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 120 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 120 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 125 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=16200.8; stale_data_ratio=0.5; total_queue_kb=16236.3; active_link=LTE; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 130 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 130 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 135 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=17237.4; stale_data_ratio=0.25; total_queue_kb=17264.9; active_link=LTE; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 140 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 140 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=17574.9; stale_data_ratio=0.25; total_queue_kb=17622.2; active_link=LTE; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 145 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 150 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 150 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 155 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 160 | AURA-ML | queue_pressure | selected_score=0.873385; top_score=0.873385; attack_threshold=0.12; predicted_mission_impact=0.925885; detectability_score=0.35 | pass |
| E6_ml_aura_tsra_r | 160 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=5385.28; stale_data_ratio=0.5; total_queue_kb=5385.28; active_link=LTE; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 165 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 170 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 170 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=3469.95; stale_data_ratio=0.5; total_queue_kb=3503.05; active_link=LTE; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 175 | TSRA-R | priority_reroute, pace_switch | critical_pending=1; video_queue_kb=5220.52; stale_data_ratio=0.5; total_queue_kb=5229.03; active_link=LTE; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 180 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 180 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 185 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 190 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 190 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=9425.41; stale_data_ratio=0.5; total_queue_kb=9457.68; active_link=MESH; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 195 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 200 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 200 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 205 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=12424.9; stale_data_ratio=0.5; total_queue_kb=12453.7; active_link=MESH; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 210 | AURA-ML | failover_chasing | selected_score=0.731039; top_score=0.731039; attack_threshold=0.12; predicted_mission_impact=0.806039; detectability_score=0.5 | pass |
| E6_ml_aura_tsra_r | 210 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 215 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 220 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 220 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=16771.2; stale_data_ratio=0.25; total_queue_kb=16810.8; active_link=MESH; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 225 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 230 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 230 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 235 | TSRA-R | stale_badge | critical_pending=1; video_queue_kb=18613; stale_data_ratio=0.5; total_queue_kb=18652.6; active_link=MESH; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 240 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 240 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=19333; stale_data_ratio=0.5; total_queue_kb=19365; active_link=MESH; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 245 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 250 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 250 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 255 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 260 | AURA-ML | queue_pressure | selected_score=0.816681; top_score=0.816681; attack_threshold=0.12; predicted_mission_impact=0.869181; detectability_score=0.35 | pass |
| E6_ml_aura_tsra_r | 260 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 265 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=12827.8; stale_data_ratio=0.5; total_queue_kb=12857.2; active_link=MESH; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 270 | AURA-ML | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 270 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 275 | TSRA-R | video_throttle | critical_pending=0; video_queue_kb=12086; stale_data_ratio=0.5; total_queue_kb=12117.7; active_link=MESH; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 280 | AURA-ML | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 280 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 285 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 290 | AURA-ML | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 290 | TSRA-R | no_op | ready_goal_actions=none; reason=no defense action emitted | pass |
| E6_ml_aura_tsra_r | 295 | TSRA-R | stale_badge | critical_pending=0; video_queue_kb=13854.5; stale_data_ratio=0.5; total_queue_kb=14045.1; active_link=MESH; probability=0; threshold=0.75 | pass |
| E6_ml_aura_tsra_r | 300 | AURA-ML | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E6_ml_aura_tsra_r | 300 | TSRA-R | priority_reroute | critical_pending=1; video_queue_kb=17027.1; stale_data_ratio=0.5; total_queue_kb=17057.6; active_link=MESH; probability=0; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 0 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 0 | TSRA-R-ML | no_op | probability=0.282859; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 5 | TSRA-R-ML | no_op | probability=0.282859; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 10 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 10 | TSRA-R-ML | no_op | probability=0.247714; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 15 | TSRA-R-ML | no_op | probability=0.258732; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 20 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 20 | TSRA-R-ML | no_op | probability=0.276425; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 25 | TSRA-R-ML | no_op | probability=0.265128; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 30 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 30 | TSRA-R-ML | no_op | probability=0.271906; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 35 | TSRA-R-ML | no_op | probability=0.280129; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 40 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 40 | TSRA-R-ML | no_op | probability=0.26774; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 45 | TSRA-R-ML | no_op | probability=0.229467; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 50 | AURA-ML | no_op | reason=waiting for min_start_sec=60.0; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 50 | TSRA-R-ML | no_op | probability=0.274111; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 55 | TSRA-R-ML | no_op | probability=0.289896; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 60 | AURA-ML | queue_pressure | selected_score=0.579505; top_score=0.579505; attack_threshold=0.12; predicted_mission_impact=0.602005; detectability_score=0.15 | pass |
| E7_ml_aura_ml_tsra_r | 60 | TSRA-R-ML | no_op | probability=0.266695; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 65 | TSRA-R-ML | no_op | probability=0.409505; threshold=0.75; active_defense_until=0; active_window=False; reason=probability below threshold and no active defense window | pass |
| E7_ml_aura_ml_tsra_r | 70 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 70 | TSRA-R-ML | priority_reroute, video_throttle, stale_badge, pace_switch | critical_pending=1; video_queue_kb=5239.34; stale_data_ratio=0.5; total_queue_kb=5421.4; active_link=SATCOM; probability=0.503568; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 75 | TSRA-R-ML | no_op | probability=0.534851; threshold=0.75; active_defense_until=115; active_window=True; reason=active defense window maintained while downstream rule actions were evaluated | pass |
| E7_ml_aura_ml_tsra_r | 80 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 80 | TSRA-R-ML | ml_attack_alert | critical_pending=1; video_queue_kb=8355.54; stale_data_ratio=0.5; total_queue_kb=8394.57; active_link=LTE; probability=0.955265; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 85 | TSRA-R-ML | no_op | probability=0.960033; threshold=0.75; active_defense_until=155; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 90 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 90 | TSRA-R-ML | no_op | probability=0.952487; threshold=0.75; active_defense_until=160; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 95 | TSRA-R-ML | no_op | probability=0.952487; threshold=0.75; active_defense_until=165; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 100 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 100 | TSRA-R-ML | no_op | probability=0.952487; threshold=0.75; active_defense_until=170; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 105 | TSRA-R-ML | ml_attack_alert, priority_reroute, video_throttle, stale_badge | critical_pending=2; video_queue_kb=12348.1; stale_data_ratio=0.5; total_queue_kb=12395.2; active_link=LTE; probability=0.961885; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 110 | AURA-ML | failover_chasing | selected_score=0.761848; top_score=0.761848; attack_threshold=0.12; predicted_mission_impact=0.836848; detectability_score=0.5 | pass |
| E7_ml_aura_ml_tsra_r | 110 | TSRA-R-ML | no_op | probability=0.972533; threshold=0.75; active_defense_until=180; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 115 | TSRA-R-ML | no_op | probability=0.965304; threshold=0.75; active_defense_until=185; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 120 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 120 | TSRA-R-ML | no_op | probability=0.969471; threshold=0.75; active_defense_until=190; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 125 | TSRA-R-ML | no_op | probability=0.969471; threshold=0.75; active_defense_until=195; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 130 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 130 | TSRA-R-ML | ml_attack_alert, priority_reroute | critical_pending=1; video_queue_kb=17026.6; stale_data_ratio=0.5; total_queue_kb=17071.1; active_link=LTE; probability=0.972249; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 135 | TSRA-R-ML | no_op | probability=0.969471; threshold=0.75; active_defense_until=205; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 140 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 140 | TSRA-R-ML | video_throttle | critical_pending=0; video_queue_kb=17850.1; stale_data_ratio=0.25; total_queue_kb=17880.8; active_link=LTE; probability=0.965503; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 145 | TSRA-R-ML | no_op | probability=0.966197; threshold=0.75; active_defense_until=215; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 150 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 150 | TSRA-R-ML | pace_switch | critical_pending=1; video_queue_kb=11880.1; stale_data_ratio=0.25; total_queue_kb=11921.4; active_link=LTE; probability=0.96828; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 155 | TSRA-R-ML | ml_attack_alert | critical_pending=0; video_queue_kb=8505.48; stale_data_ratio=0.25; total_queue_kb=8537.23; active_link=MESH; probability=0.966892; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 160 | AURA-ML | failover_chasing | selected_score=0.777403; top_score=0.777403; attack_threshold=0.12; predicted_mission_impact=0.822403; detectability_score=0.3 | pass |
| E7_ml_aura_ml_tsra_r | 160 | TSRA-R-ML | stale_badge | critical_pending=0; video_queue_kb=5482.94; stale_data_ratio=0.5; total_queue_kb=5515.18; active_link=MESH; probability=0.916883; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 165 | TSRA-R-ML | no_op | probability=0.921799; threshold=0.75; active_defense_until=235; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 170 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 170 | TSRA-R-ML | no_op | probability=0.898968; threshold=0.75; active_defense_until=240; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 175 | TSRA-R-ML | priority_reroute | critical_pending=1; video_queue_kb=557.283; stale_data_ratio=0.5; total_queue_kb=601.192; active_link=MESH; probability=0.895079; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 180 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 180 | TSRA-R-ML | no_op | probability=0.279461; threshold=0.75; active_defense_until=245; active_window=True; reason=active defense window maintained while downstream rule actions were evaluated | pass |
| E7_ml_aura_ml_tsra_r | 185 | TSRA-R-ML | no_op | probability=0.279184; threshold=0.75; active_defense_until=245; active_window=True; reason=active defense window maintained while downstream rule actions were evaluated | pass |
| E7_ml_aura_ml_tsra_r | 190 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 190 | TSRA-R-ML | stale_badge | critical_pending=1; video_queue_kb=728.975; stale_data_ratio=0.5; total_queue_kb=739.009; active_link=MESH; probability=0.280771; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 195 | TSRA-R-ML | no_op | probability=0.279871; threshold=0.75; active_defense_until=245; active_window=True; reason=active defense window maintained while downstream rule actions were evaluated | pass |
| E7_ml_aura_ml_tsra_r | 200 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 200 | TSRA-R-ML | no_op | probability=0.28753; threshold=0.75; active_defense_until=245; active_window=True; reason=active defense window maintained while downstream rule actions were evaluated | pass |
| E7_ml_aura_ml_tsra_r | 205 | TSRA-R-ML | video_throttle | critical_pending=0; video_queue_kb=1807.34; stale_data_ratio=0.5; total_queue_kb=1839.01; active_link=MESH; probability=0.407404; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 210 | AURA-ML | queue_pressure | selected_score=0.779372; top_score=0.779372; attack_threshold=0.12; predicted_mission_impact=0.801872; detectability_score=0.15 | pass |
| E7_ml_aura_ml_tsra_r | 210 | TSRA-R-ML | no_op | probability=0.394108; threshold=0.75; active_defense_until=245; active_window=True; reason=active defense window maintained while downstream rule actions were evaluated | pass |
| E7_ml_aura_ml_tsra_r | 215 | TSRA-R-ML | no_op | probability=0.477419; threshold=0.75; active_defense_until=245; active_window=True; reason=active defense window maintained while downstream rule actions were evaluated | pass |
| E7_ml_aura_ml_tsra_r | 220 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 220 | TSRA-R-ML | ml_attack_alert, priority_reroute | critical_pending=1; video_queue_kb=6507; stale_data_ratio=0.25; total_queue_kb=6541.7; active_link=MESH; probability=0.88058; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 225 | TSRA-R-ML | no_op | probability=0.920677; threshold=0.75; active_defense_until=295; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 230 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 230 | TSRA-R-ML | no_op | probability=0.936032; threshold=0.75; active_defense_until=300; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 235 | TSRA-R-ML | stale_badge | critical_pending=1; video_queue_kb=10132.8; stale_data_ratio=0.5; total_queue_kb=10173.1; active_link=MESH; probability=0.943578; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 240 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 240 | TSRA-R-ML | video_throttle | critical_pending=0; video_queue_kb=12813.3; stale_data_ratio=0.25; total_queue_kb=12846.1; active_link=MESH; probability=0.936032; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 245 | TSRA-R-ML | ml_attack_alert | critical_pending=0; video_queue_kb=13962.1; stale_data_ratio=0.25; total_queue_kb=13962.1; active_link=MESH; probability=0.936032; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 250 | AURA-ML | no_op | reason=attack cooldown active; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 250 | TSRA-R-ML | no_op | probability=0.936032; threshold=0.75; active_defense_until=320; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 255 | TSRA-R-ML | no_op | probability=0.936032; threshold=0.75; active_defense_until=325; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 260 | AURA-ML | failover_chasing | selected_score=0.69979; top_score=0.69979; attack_threshold=0.12; predicted_mission_impact=0.77479; detectability_score=0.5 | pass |
| E7_ml_aura_ml_tsra_r | 260 | TSRA-R-ML | priority_reroute, pace_switch | critical_pending=1; video_queue_kb=18901.8; stale_data_ratio=0.25; total_queue_kb=18912.7; active_link=MESH; probability=0.920677; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 265 | TSRA-R-ML | no_op | probability=0.920677; threshold=0.75; active_defense_until=335; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 270 | AURA-ML | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 270 | TSRA-R-ML | ml_attack_alert, stale_badge | critical_pending=0; video_queue_kb=21339.3; stale_data_ratio=0.5; total_queue_kb=21339.3; active_link=LTE; probability=0.923455; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 275 | TSRA-R-ML | video_throttle | critical_pending=0; video_queue_kb=22558.1; stale_data_ratio=0.5; total_queue_kb=22587.6; active_link=LTE; probability=0.921603; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 280 | AURA-ML | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 280 | TSRA-R-ML | no_op | probability=0.921603; threshold=0.75; active_defense_until=350; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 285 | TSRA-R-ML | priority_reroute | critical_pending=1; video_queue_kb=26495.6; stale_data_ratio=0.5; total_queue_kb=26537.5; active_link=LTE; probability=0.921603; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 290 | AURA-ML | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 290 | TSRA-R-ML | no_op | probability=0.921603; threshold=0.75; active_defense_until=360; active_window=True; reason=detector opened or maintained defense window | pass |
| E7_ml_aura_ml_tsra_r | 295 | TSRA-R-ML | ml_attack_alert | critical_pending=0; video_queue_kb=27708.8; stale_data_ratio=0.5; total_queue_kb=27708.8; active_link=LTE; probability=0.925769; threshold=0.75 | pass |
| E7_ml_aura_ml_tsra_r | 300 | AURA-ML | no_op | reason=max_events=5 reached; candidate_count=0 | pass |
| E7_ml_aura_ml_tsra_r | 300 | TSRA-R-ML | stale_badge | critical_pending=0; video_queue_kb=27431.3; stale_data_ratio=0.5; total_queue_kb=27464.8; active_link=LTE; probability=0.925769; threshold=0.75 | pass |