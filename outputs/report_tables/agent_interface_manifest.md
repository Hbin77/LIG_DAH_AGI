# Agent Interface Manifest

This manifest describes the observed runtime interface for each active attack/defense agent.

Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action

## AURA (attack)

- Goal: maximize simulated mission impact while staying inside safety constraints
- Policies: rule_attack_score
- Input contract: time_sec, mission_phase, active_link, signals.active_attack_count, signals.active_attack_targets, signals.active_attack_types, signals.active_defense_actions, signals.critical_pending, signals.defense_mode, signals.last_attack_target, signals.last_attack_time_sec, signals.last_attack_type, signals.last_defense_action, signals.last_defense_time_sec, signals.links, signals.priority_inversion_rate, signals.recent_attack_event_ids, signals.recent_attack_targets, signals.recent_attack_types, signals.recent_defense_actions, signals.recent_p95_critical_latency_sec, signals.stale_data_ratio, signals.total_queue_kb, signals.video_queue_kb
- Memory contract: belief_state, decision_count, last_observed_at, last_selected_action, observation_count, belief_state.counter_defense_context_seen, belief_state.defense_context, belief_state.event_count, belief_state.last_attack_time, belief_state.last_attack_type
- Tool contract: estimate_candidate_effect, estimate_detectability, generate_attack_candidates, summarize_defense_context
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
- Input contract: time_sec, mission_phase, active_link, signals.active_attack_count, signals.active_attack_targets, signals.active_attack_types, signals.active_defense_actions, signals.critical_pending, signals.defense_mode, signals.last_attack_target, signals.last_attack_time_sec, signals.last_attack_type, signals.last_defense_action, signals.last_defense_time_sec, signals.links, signals.priority_inversion_rate, signals.recent_attack_event_ids, signals.recent_attack_targets, signals.recent_attack_types, signals.recent_defense_actions, signals.recent_p95_critical_latency_sec, signals.stale_data_ratio, signals.total_queue_kb, signals.video_queue_kb
- Memory contract: belief_state, decision_count, last_observed_at, last_selected_action, observation_count, belief_state.attack_type_counts, belief_state.counter_defense_context_seen, belief_state.defense_context, belief_state.event_count, belief_state.last_attack_time, belief_state.last_attack_type, belief_state.last_objective_bonus
- Tool contract: estimate_candidate_effect, estimate_detectability, generate_attack_candidates, predict_candidate_impact, summarize_defense_context
- Candidate contract: bandwidth_limit, critical_window_degradation, failover_chasing, link_degradation, queue_pressure, stale_cop_induction
- Selected action contract: attack_event, no_op
- Event outputs: attack_events.jsonl: failover_chasing, queue_pressure, stale_cop_induction
- Evidence experiments: E7_ml_aura_ml_tsra_r
- Trace count: 31
- Non-no-op decisions: 5
- Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action

## TSRA-R (defense)

- Goal: minimize mission impact with bounded defensive response actions
- Policies: rule_defense_full
- Input contract: time_sec, mission_phase, active_link, signals.active_attack_count, signals.active_attack_targets, signals.active_attack_types, signals.active_defense_actions, signals.critical_pending, signals.defense_mode, signals.last_attack_target, signals.last_attack_time_sec, signals.last_attack_type, signals.last_defense_action, signals.last_defense_time_sec, signals.links, signals.priority_inversion_rate, signals.recent_attack_event_ids, signals.recent_attack_targets, signals.recent_attack_types, signals.recent_defense_actions, signals.recent_p95_critical_latency_sec, signals.stale_data_ratio, signals.total_queue_kb, signals.video_queue_kb
- Memory contract: belief_state, decision_count, last_observed_at, last_selected_action, observation_count, belief_state.action_cooldowns, belief_state.attack_context, belief_state.attack_context_seen, belief_state.enabled_actions, belief_state.event_count, belief_state.mode
- Tool contract: evaluate_defense_conditions, select_fallback_link, summarize_attack_context
- Candidate contract: pace_switch, priority_reroute, stale_badge, video_throttle
- Selected action contract: defense_events, no_op
- Event outputs: defense_events.jsonl: pace_switch, priority_reroute, stale_badge, video_throttle
- Evidence experiments: E5_rule_aura_tsra_r
- Trace count: 61
- Non-no-op decisions: 19
- Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action

## TSRA-R-ML (defense)

- Goal: open reactive defense windows when anomaly probability exceeds threshold or residual mission risk remains near window expiry
- Policies: ml_anomaly_detector
- Input contract: time_sec, mission_phase, active_link, signals.active_attack_count, signals.active_attack_targets, signals.active_attack_types, signals.active_defense_actions, signals.critical_pending, signals.defense_mode, signals.last_attack_target, signals.last_attack_time_sec, signals.last_attack_type, signals.last_defense_action, signals.last_defense_time_sec, signals.links, signals.priority_inversion_rate, signals.recent_attack_event_ids, signals.recent_attack_targets, signals.recent_attack_types, signals.recent_defense_actions, signals.recent_p95_critical_latency_sec, signals.stale_data_ratio, signals.total_queue_kb, signals.video_queue_kb
- Memory contract: belief_state, decision_count, last_observed_at, last_selected_action, observation_count, belief_state.active_defense_until, belief_state.attack_context, belief_state.attack_context_seen, belief_state.last_alert_time, belief_state.last_early_guard_triggered, belief_state.last_mission_guard_reason, belief_state.last_mission_guard_score, belief_state.last_probability
- Tool contract: assess_mission_risk_guard, predict_attack_probability, summarize_attack_context
- Candidate contract: open_defense_window
- Selected action contract: defense_events, no_op
- Event outputs: defense_events.jsonl: ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- Evidence experiments: E7_ml_aura_ml_tsra_r
- Trace count: 61
- Non-no-op decisions: 20
- Safety boundary: closed simulation agent-interface manifest only; no RF, exploit, or live network action
