# Agent Decision Trace Summary

This table is generated from AURA and TSRA-R DecisionTrace JSONL logs.

| experiment | time_sec | agent | policy | selected_action | score | probability | top_candidate | top_candidate_signal | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E3_rule_aura | 0 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E3_rule_aura | 10 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E3_rule_aura | 20 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E3_rule_aura | 30 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E3_rule_aura | 40 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E3_rule_aura | 50 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E3_rule_aura | 60 | AURA | rule_attack_score | queue_pressure | 0.543691 |  | queue_pressure | impact=0.566191; detectability=0.15 | increase non-critical queue occupancy |
| E3_rule_aura | 70 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 80 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 90 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 100 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 110 | AURA | rule_attack_score | bandwidth_limit | 0.9475 |  | bandwidth_limit | impact=1; detectability=0.35 | reduce available capacity during queue growth |
| E3_rule_aura | 120 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 130 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 140 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 150 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 160 | AURA | rule_attack_score | bandwidth_limit | 0.9475 |  | bandwidth_limit | impact=1; detectability=0.35 | reduce available capacity during queue growth |
| E3_rule_aura | 170 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 180 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 190 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 200 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 210 | AURA | rule_attack_score | bandwidth_limit | 0.9475 |  | bandwidth_limit | impact=1; detectability=0.35 | reduce available capacity during queue growth |
| E3_rule_aura | 220 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 230 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 240 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 250 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E3_rule_aura | 260 | AURA | rule_attack_score | stale_cop_induction | 0.9175 |  | stale_cop_induction | impact=1; detectability=0.55 | COP freshness is already degraded |
| E3_rule_aura | 270 | AURA | rule_attack_score | no_op |  |  |  |  | max_events=5 reached |
| E3_rule_aura | 280 | AURA | rule_attack_score | no_op |  |  |  |  | max_events=5 reached |
| E3_rule_aura | 290 | AURA | rule_attack_score | no_op |  |  |  |  | max_events=5 reached |
| E3_rule_aura | 300 | AURA | rule_attack_score | no_op |  |  |  |  | max_events=5 reached |
| E5_rule_aura_tsra_r | 0 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E5_rule_aura_tsra_r | 0 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=False; ready=True | no defense action emitted |
| E5_rule_aura_tsra_r | 5 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=False; ready=True | no defense action emitted |
| E5_rule_aura_tsra_r | 10 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E5_rule_aura_tsra_r | 10 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=False; ready=True | no defense action emitted |
| E5_rule_aura_tsra_r | 15 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=False; ready=True | no defense action emitted |
| E5_rule_aura_tsra_r | 20 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E5_rule_aura_tsra_r | 20 | TSRA-R | rule_defense_full | stale_badge |  |  | stale_badge | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 25 | TSRA-R | rule_defense_full | no_op |  |  | stale_badge | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 30 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E5_rule_aura_tsra_r | 30 | TSRA-R | rule_defense_full | no_op |  |  | stale_badge | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 35 | TSRA-R | rule_defense_full | no_op |  |  | stale_badge | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 40 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E5_rule_aura_tsra_r | 40 | TSRA-R | rule_defense_full | no_op |  |  | stale_badge | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 45 | TSRA-R | rule_defense_full | no_op |  |  | stale_badge | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 50 | AURA | rule_attack_score | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E5_rule_aura_tsra_r | 50 | TSRA-R | rule_defense_full | stale_badge |  |  | stale_badge | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 55 | TSRA-R | rule_defense_full | no_op |  |  | stale_badge | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 60 | AURA | rule_attack_score | queue_pressure | 0.543691 |  | queue_pressure | impact=0.566191; detectability=0.15 | increase non-critical queue occupancy |
| E5_rule_aura_tsra_r | 60 | TSRA-R | rule_defense_full | no_op |  |  | stale_badge | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 65 | TSRA-R | rule_defense_full | priority_reroute+video_throttle |  |  | priority_reroute | eligible=True; ready=True | emitted 2 defense event(s) |
| E5_rule_aura_tsra_r | 70 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 70 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 75 | TSRA-R | rule_defense_full | pace_switch |  |  | pace_switch | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 80 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 80 | TSRA-R | rule_defense_full | stale_badge |  |  | stale_badge | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 85 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 90 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 90 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 95 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 100 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 100 | TSRA-R | rule_defense_full | video_throttle |  |  | video_throttle | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 105 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 110 | AURA | rule_attack_score | queue_pressure | 0.916763 |  | queue_pressure | impact=0.939263; detectability=0.15 | increase non-critical queue occupancy |
| E5_rule_aura_tsra_r | 110 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 115 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 120 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 120 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 125 | TSRA-R | rule_defense_full | priority_reroute |  |  | priority_reroute | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 130 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 130 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 135 | TSRA-R | rule_defense_full | video_throttle |  |  | video_throttle | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 140 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 140 | TSRA-R | rule_defense_full | stale_badge |  |  | stale_badge | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 145 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 150 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 150 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 155 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 160 | AURA | rule_attack_score | queue_pressure | 0.9775 |  | queue_pressure | impact=1; detectability=0.15 | increase non-critical queue occupancy |
| E5_rule_aura_tsra_r | 160 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 165 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 170 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 170 | TSRA-R | rule_defense_full | video_throttle+stale_badge |  |  | video_throttle | eligible=True; ready=True | emitted 2 defense event(s) |
| E5_rule_aura_tsra_r | 175 | TSRA-R | rule_defense_full | priority_reroute |  |  | priority_reroute | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 180 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 180 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 185 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 190 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 190 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 195 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 200 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 200 | TSRA-R | rule_defense_full | priority_reroute+stale_badge |  |  | priority_reroute | eligible=True; ready=True | emitted 2 defense event(s) |
| E5_rule_aura_tsra_r | 205 | TSRA-R | rule_defense_full | video_throttle |  |  | video_throttle | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 210 | AURA | rule_attack_score | queue_pressure | 0.9475 |  | queue_pressure | impact=1; detectability=0.35 | increase non-critical queue occupancy |
| E5_rule_aura_tsra_r | 210 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 215 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 220 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 220 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 225 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 230 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 230 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 235 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 240 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 240 | TSRA-R | rule_defense_full | video_throttle |  |  | video_throttle | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 245 | TSRA-R | rule_defense_full | priority_reroute |  |  | priority_reroute | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 250 | AURA | rule_attack_score | no_op |  |  |  |  | attack cooldown active |
| E5_rule_aura_tsra_r | 250 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 255 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 260 | AURA | rule_attack_score | queue_pressure | 0.9035 |  | queue_pressure | impact=0.956; detectability=0.35 | increase non-critical queue occupancy |
| E5_rule_aura_tsra_r | 260 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 265 | TSRA-R | rule_defense_full | stale_badge |  |  | stale_badge | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 270 | AURA | rule_attack_score | no_op |  |  |  |  | max_events=5 reached |
| E5_rule_aura_tsra_r | 270 | TSRA-R | rule_defense_full | priority_reroute |  |  | priority_reroute | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 275 | TSRA-R | rule_defense_full | video_throttle |  |  | video_throttle | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 280 | AURA | rule_attack_score | no_op |  |  |  |  | max_events=5 reached |
| E5_rule_aura_tsra_r | 280 | TSRA-R | rule_defense_full | no_op |  |  | priority_reroute | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 285 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 290 | AURA | rule_attack_score | no_op |  |  |  |  | max_events=5 reached |
| E5_rule_aura_tsra_r | 290 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E5_rule_aura_tsra_r | 295 | TSRA-R | rule_defense_full | stale_badge |  |  | stale_badge | eligible=True; ready=True | emitted 1 defense event(s) |
| E5_rule_aura_tsra_r | 300 | AURA | rule_attack_score | no_op |  |  |  |  | max_events=5 reached |
| E5_rule_aura_tsra_r | 300 | TSRA-R | rule_defense_full | no_op |  |  | video_throttle | eligible=True; ready=False | no defense action emitted |
| E7_ml_aura_ml_tsra_r | 0 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E7_ml_aura_ml_tsra_r | 0 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.282859 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 5 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.282859 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 10 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E7_ml_aura_ml_tsra_r | 10 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.247714 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 15 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.258732 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 20 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E7_ml_aura_ml_tsra_r | 20 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.276425 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 25 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.265128 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 30 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E7_ml_aura_ml_tsra_r | 30 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.271906 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 35 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.280129 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 40 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E7_ml_aura_ml_tsra_r | 40 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.26774 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 45 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.229467 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 50 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | waiting for min_start_sec=60.0 |
| E7_ml_aura_ml_tsra_r | 50 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.274111 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 55 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.289896 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 60 | AURA-ML | ml_impact_predictor | queue_pressure | 0.579505 |  | queue_pressure | impact=0.602005; detectability=0.15 | ML impact predictor selected queue_pressure |
| E7_ml_aura_ml_tsra_r | 60 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.266695 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 65 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.409505 | open_defense_window | eligible=False; threshold=0.75; active_until=0 | probability below threshold and no active defense window |
| E7_ml_aura_ml_tsra_r | 70 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 70 | TSRA-R-ML | ml_anomaly_detector | priority_reroute+video_throttle+stale_badge+pace_switch |  | 0.503568 | open_defense_window | eligible=True; threshold=0.75; active_until=115 | mission risk guard opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 75 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.534851 | open_defense_window | eligible=False; threshold=0.75; active_until=115 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 80 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 80 | TSRA-R-ML | ml_anomaly_detector | ml_attack_alert |  | 0.955265 | open_defense_window | eligible=True; threshold=0.75; active_until=150 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 85 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.960033 | open_defense_window | eligible=True; threshold=0.75; active_until=155 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 90 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 90 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.952487 | open_defense_window | eligible=True; threshold=0.75; active_until=160 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 95 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.952487 | open_defense_window | eligible=True; threshold=0.75; active_until=165 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 100 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 100 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.952487 | open_defense_window | eligible=True; threshold=0.75; active_until=170 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 105 | TSRA-R-ML | ml_anomaly_detector | ml_attack_alert+priority_reroute+video_throttle+stale_badge |  | 0.961885 | open_defense_window | eligible=True; threshold=0.75; active_until=175 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 110 | AURA-ML | ml_impact_predictor | failover_chasing | 0.761848 |  | failover_chasing | impact=0.836848; detectability=0.5 | ML impact predictor selected failover_chasing |
| E7_ml_aura_ml_tsra_r | 110 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.972533 | open_defense_window | eligible=True; threshold=0.75; active_until=180 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 115 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.965304 | open_defense_window | eligible=True; threshold=0.75; active_until=185 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 120 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 120 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.969471 | open_defense_window | eligible=True; threshold=0.75; active_until=190 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 125 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.969471 | open_defense_window | eligible=True; threshold=0.75; active_until=195 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 130 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 130 | TSRA-R-ML | ml_anomaly_detector | ml_attack_alert+priority_reroute |  | 0.972249 | open_defense_window | eligible=True; threshold=0.75; active_until=200 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 135 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.969471 | open_defense_window | eligible=True; threshold=0.75; active_until=205 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 140 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 140 | TSRA-R-ML | ml_anomaly_detector | video_throttle |  | 0.965503 | open_defense_window | eligible=True; threshold=0.75; active_until=210 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 145 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.966197 | open_defense_window | eligible=True; threshold=0.75; active_until=215 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 150 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 150 | TSRA-R-ML | ml_anomaly_detector | pace_switch |  | 0.96828 | open_defense_window | eligible=True; threshold=0.75; active_until=220 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 155 | TSRA-R-ML | ml_anomaly_detector | ml_attack_alert |  | 0.966892 | open_defense_window | eligible=True; threshold=0.75; active_until=225 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 160 | AURA-ML | ml_impact_predictor | failover_chasing | 0.737403 |  | failover_chasing | impact=0.822403; detectability=0.3 | ML impact predictor selected failover_chasing |
| E7_ml_aura_ml_tsra_r | 160 | TSRA-R-ML | ml_anomaly_detector | stale_badge |  | 0.916883 | open_defense_window | eligible=True; threshold=0.75; active_until=230 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 165 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.921799 | open_defense_window | eligible=True; threshold=0.75; active_until=235 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 170 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 170 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.898968 | open_defense_window | eligible=True; threshold=0.75; active_until=240 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 175 | TSRA-R-ML | ml_anomaly_detector | priority_reroute |  | 0.895079 | open_defense_window | eligible=True; threshold=0.75; active_until=245 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 180 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 180 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.279461 | open_defense_window | eligible=False; threshold=0.75; active_until=245 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 185 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.279184 | open_defense_window | eligible=False; threshold=0.75; active_until=245 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 190 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 190 | TSRA-R-ML | ml_anomaly_detector | stale_badge |  | 0.280771 | open_defense_window | eligible=False; threshold=0.75; active_until=245 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 195 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.279871 | open_defense_window | eligible=False; threshold=0.75; active_until=245 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 200 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 200 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.28753 | open_defense_window | eligible=False; threshold=0.75; active_until=245 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 205 | TSRA-R-ML | ml_anomaly_detector | video_throttle |  | 0.407404 | open_defense_window | eligible=False; threshold=0.75; active_until=245 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 210 | AURA-ML | ml_impact_predictor | queue_pressure | 0.739372 |  | queue_pressure | impact=0.801872; detectability=0.15 | ML impact predictor selected queue_pressure |
| E7_ml_aura_ml_tsra_r | 210 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.394108 | open_defense_window | eligible=False; threshold=0.75; active_until=245 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 215 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.477419 | open_defense_window | eligible=False; threshold=0.75; active_until=245 | active defense window maintained while downstream rule actions were evaluated |
| E7_ml_aura_ml_tsra_r | 220 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 220 | TSRA-R-ML | ml_anomaly_detector | ml_attack_alert+priority_reroute |  | 0.88058 | open_defense_window | eligible=True; threshold=0.75; active_until=290 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 225 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.920677 | open_defense_window | eligible=True; threshold=0.75; active_until=295 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 230 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 230 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.936032 | open_defense_window | eligible=True; threshold=0.75; active_until=300 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 235 | TSRA-R-ML | ml_anomaly_detector | stale_badge |  | 0.943578 | open_defense_window | eligible=True; threshold=0.75; active_until=305 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 240 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 240 | TSRA-R-ML | ml_anomaly_detector | video_throttle |  | 0.936032 | open_defense_window | eligible=True; threshold=0.75; active_until=310 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 245 | TSRA-R-ML | ml_anomaly_detector | ml_attack_alert |  | 0.936032 | open_defense_window | eligible=True; threshold=0.75; active_until=315 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 250 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | attack cooldown active |
| E7_ml_aura_ml_tsra_r | 250 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.936032 | open_defense_window | eligible=True; threshold=0.75; active_until=320 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 255 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.936032 | open_defense_window | eligible=True; threshold=0.75; active_until=325 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 260 | AURA-ML | ml_impact_predictor | stale_cop_induction | 0.779393 |  | stale_cop_induction | impact=0.661893; detectability=0.55 | ML impact predictor selected stale_cop_induction |
| E7_ml_aura_ml_tsra_r | 260 | TSRA-R-ML | ml_anomaly_detector | priority_reroute+pace_switch |  | 0.928007 | open_defense_window | eligible=True; threshold=0.75; active_until=330 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 265 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.928007 | open_defense_window | eligible=True; threshold=0.75; active_until=335 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 270 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | max_events=5 reached |
| E7_ml_aura_ml_tsra_r | 270 | TSRA-R-ML | ml_anomaly_detector | ml_attack_alert+stale_badge |  | 0.930785 | open_defense_window | eligible=True; threshold=0.75; active_until=340 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 275 | TSRA-R-ML | ml_anomaly_detector | video_throttle |  | 0.928933 | open_defense_window | eligible=True; threshold=0.75; active_until=345 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 280 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | max_events=5 reached |
| E7_ml_aura_ml_tsra_r | 280 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.928933 | open_defense_window | eligible=True; threshold=0.75; active_until=350 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 285 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.928933 | open_defense_window | eligible=True; threshold=0.75; active_until=355 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 290 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | max_events=5 reached |
| E7_ml_aura_ml_tsra_r | 290 | TSRA-R-ML | ml_anomaly_detector | no_op |  | 0.928933 | open_defense_window | eligible=True; threshold=0.75; active_until=360 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 295 | TSRA-R-ML | ml_anomaly_detector | ml_attack_alert |  | 0.9331 | open_defense_window | eligible=True; threshold=0.75; active_until=365 | detector opened or maintained defense window |
| E7_ml_aura_ml_tsra_r | 300 | AURA-ML | ml_impact_predictor | no_op |  |  |  |  | max_events=5 reached |
| E7_ml_aura_ml_tsra_r | 300 | TSRA-R-ML | ml_anomaly_detector | stale_badge |  | 0.9331 | open_defense_window | eligible=True; threshold=0.75; active_until=370 | detector opened or maintained defense window |
