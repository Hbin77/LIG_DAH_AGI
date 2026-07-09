# Agent Interface Manifest

This manifest describes the observed runtime interface for each active attack/defense agent.

Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action

## AURA (attack)

- Goal: maximize simulated mission impact while staying inside safety constraints
- Policies: rule_attack_score
- Input contract: time_sec, mission_phase, active_link, signals.critical_pending, signals.defense_mode, signals.links, signals.priority_inversion_rate, signals.recent_p95_critical_latency_sec, signals.stale_data_ratio, signals.total_queue_kb, signals.video_queue_kb
- Memory contract: belief_state, decision_count, last_observed_at, last_selected_action, observation_count, belief_state.event_count, belief_state.last_attack_time, belief_state.last_attack_type
- Tool contract: estimate_candidate_effect, estimate_detectability, generate_attack_candidates
- Candidate contract: bandwidth_limit, critical_window_degradation, failover_chasing, link_degradation, queue_pressure, stale_cop_induction
- Selected action contract: attack_event, no_op
- Event outputs: attack_events.jsonl: bandwidth_limit, queue_pressure, stale_cop_induction
- Evidence experiments: E3_rule_aura, E5_rule_aura_tsra_r
- Trace count: 62
- Non-no-op decisions: 10
- Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action

## AURA-ML (attack)

- Goal: select simulated attack effect using learned mission-impact prediction
- Policies: ml_impact_predictor
- Input contract: time_sec, mission_phase, active_link, signals.critical_pending, signals.defense_mode, signals.links, signals.priority_inversion_rate, signals.recent_p95_critical_latency_sec, signals.stale_data_ratio, signals.total_queue_kb, signals.video_queue_kb
- Memory contract: belief_state, decision_count, last_observed_at, last_selected_action, observation_count, belief_state.event_count, belief_state.last_attack_time, belief_state.last_attack_type
- Tool contract: estimate_candidate_effect, estimate_detectability, generate_attack_candidates, predict_candidate_impact
- Candidate contract: bandwidth_limit, critical_window_degradation, failover_chasing, link_degradation, queue_pressure, stale_cop_induction
- Selected action contract: attack_event, no_op
- Event outputs: attack_events.jsonl: failover_chasing, queue_pressure
- Evidence experiments: E7_ml_aura_ml_tsra_r
- Trace count: 31
- Non-no-op decisions: 5
- Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action

## TSRA-R (defense)

- Goal: minimize mission impact with bounded defensive response actions
- Policies: rule_defense_full
- Input contract: time_sec, mission_phase, active_link, signals.critical_pending, signals.defense_mode, signals.links, signals.priority_inversion_rate, signals.recent_p95_critical_latency_sec, signals.stale_data_ratio, signals.total_queue_kb, signals.video_queue_kb
- Memory contract: belief_state, decision_count, last_observed_at, last_selected_action, observation_count, belief_state.action_cooldowns, belief_state.enabled_actions, belief_state.event_count, belief_state.mode
- Tool contract: evaluate_defense_conditions, select_fallback_link
- Candidate contract: pace_switch, priority_reroute, stale_badge, video_throttle
- Selected action contract: defense_events, no_op
- Event outputs: defense_events.jsonl: pace_switch, priority_reroute, stale_badge, video_throttle
- Evidence experiments: E5_rule_aura_tsra_r
- Trace count: 61
- Non-no-op decisions: 19
- Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action

## TSRA-R-ML (defense)

- Goal: open reactive defense windows when anomaly probability exceeds threshold
- Policies: ml_anomaly_detector
- Input contract: time_sec, mission_phase, active_link, signals.critical_pending, signals.defense_mode, signals.links, signals.priority_inversion_rate, signals.recent_p95_critical_latency_sec, signals.stale_data_ratio, signals.total_queue_kb, signals.video_queue_kb
- Memory contract: belief_state, decision_count, last_observed_at, last_selected_action, observation_count, belief_state.active_defense_until, belief_state.last_alert_time, belief_state.last_probability
- Tool contract: predict_attack_probability
- Candidate contract: open_defense_window
- Selected action contract: defense_events, no_op
- Event outputs: defense_events.jsonl: ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- Evidence experiments: E7_ml_aura_ml_tsra_r
- Trace count: 61
- Non-no-op decisions: 19
- Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action
