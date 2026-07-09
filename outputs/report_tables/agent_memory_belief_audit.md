# Agent Memory Belief Audit

This audit verifies that AgentMemory is populated, evolves across decisions, and carries the previous selected action into the next decision loop.
Safety boundary: closed simulation agent-memory audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 9
- Status counts: pass=9
- Agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML

## Audit Table

| experiment | agent | policy | trace_count | memory_signature_count | changing_belief_keys | last_selected_chain_match_rate | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E3_rule_aura | AURA | rule_attack_score | 31 | 31 | event_count, last_attack_time, last_attack_type | 1 | pass |
| E4_rule_aura_basic_defense | AURA | rule_attack_score | 31 | 31 | counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type | 1 | pass |
| E4_rule_aura_basic_defense | TSRA-R | rule_defense_basic | 61 | 61 | action_cooldowns, attack_context, attack_context_seen, event_count | 1 | pass |
| E5_rule_aura_tsra_r | AURA | rule_attack_score | 31 | 31 | counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type | 1 | pass |
| E5_rule_aura_tsra_r | TSRA-R | rule_defense_full | 61 | 61 | action_cooldowns, attack_context, attack_context_seen, event_count | 1 | pass |
| E6_ml_aura_tsra_r | AURA-ML | ml_impact_predictor | 31 | 31 | attack_type_counts, counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type, last_objective_bonus | 1 | pass |
| E6_ml_aura_tsra_r | TSRA-R | rule_defense_full | 61 | 61 | action_cooldowns, attack_context, attack_context_seen, event_count | 1 | pass |
| E7_ml_aura_ml_tsra_r | AURA-ML | ml_impact_predictor | 31 | 31 | attack_type_counts, counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type, last_objective_bonus | 1 | pass |
| E7_ml_aura_ml_tsra_r | TSRA-R-ML | ml_anomaly_detector | 61 | 61 | active_defense_until, attack_context, attack_context_seen, last_alert_time, last_early_guard_triggered, last_mission_guard_reason, last_mission_guard_score, last_probability | 1 | pass |

## Detail

### E3_rule_aura AURA rule_attack_score

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type
- Changing belief keys: event_count, last_attack_time, last_attack_type
- Feedback keys: attack_threshold, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget
- Last-selected chain: 30/30
- Effect summary: AURA memory carries attack cadence and last attack context into later candidate decisions; changing=event_count, last_attack_time, last_attack_type; feedback=attack_threshold, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget.
- Status: pass
- Issues: none

### E4_rule_aura_basic_defense AURA rule_attack_score

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type
- Changing belief keys: counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type
- Feedback keys: attack_threshold, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget
- Last-selected chain: 30/30
- Effect summary: AURA memory carries attack cadence and last attack context into later candidate decisions; changing=counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type; feedback=attack_threshold, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget.
- Status: pass
- Issues: none

### E4_rule_aura_basic_defense TSRA-R rule_defense_basic

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: action_cooldowns, attack_context, attack_context_seen, enabled_actions, event_count, mode
- Changing belief keys: action_cooldowns, attack_context, attack_context_seen, event_count
- Feedback keys: action_cooldowns, attack_context, enabled_actions, event_count, mode
- Last-selected chain: 60/60
- Effect summary: TSRA-R memory carries cooldown, enabled action, and event count state into bounded response decisions; changing=action_cooldowns, attack_context, attack_context_seen, event_count; feedback=action_cooldowns, attack_context, enabled_actions, event_count, mode.
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r AURA rule_attack_score

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type
- Changing belief keys: counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type
- Feedback keys: attack_threshold, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget
- Last-selected chain: 30/30
- Effect summary: AURA memory carries attack cadence and last attack context into later candidate decisions; changing=counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type; feedback=attack_threshold, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget.
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r TSRA-R rule_defense_full

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: action_cooldowns, attack_context, attack_context_seen, enabled_actions, event_count, mode
- Changing belief keys: action_cooldowns, attack_context, attack_context_seen, event_count
- Feedback keys: action_cooldowns, attack_context, enabled_actions, event_count, mode
- Last-selected chain: 60/60
- Effect summary: TSRA-R memory carries cooldown, enabled action, and event count state into bounded response decisions; changing=action_cooldowns, attack_context, attack_context_seen, event_count; feedback=action_cooldowns, attack_context, enabled_actions, event_count, mode.
- Status: pass
- Issues: none

### E6_ml_aura_tsra_r AURA-ML ml_impact_predictor

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: attack_type_counts, counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type, last_objective_bonus
- Changing belief keys: attack_type_counts, counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type, last_objective_bonus
- Feedback keys: attack_threshold, attack_type_counts, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget, selected_base_attack_score, selected_objective_bonus, selected_repeated_tactic_penalty
- Last-selected chain: 30/30
- Effect summary: AURA memory carries attack cadence and last attack context into later candidate decisions; changing=attack_type_counts, counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type, last_objective_bonus; feedback=attack_threshold, attack_type_counts, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget, selected_base_attack_score, selected_objective_bonus, selected_repeated_tactic_penalty.
- Status: pass
- Issues: none

### E6_ml_aura_tsra_r TSRA-R rule_defense_full

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: action_cooldowns, attack_context, attack_context_seen, enabled_actions, event_count, mode
- Changing belief keys: action_cooldowns, attack_context, attack_context_seen, event_count
- Feedback keys: action_cooldowns, attack_context, enabled_actions, event_count, mode
- Last-selected chain: 60/60
- Effect summary: TSRA-R memory carries cooldown, enabled action, and event count state into bounded response decisions; changing=action_cooldowns, attack_context, attack_context_seen, event_count; feedback=action_cooldowns, attack_context, enabled_actions, event_count, mode.
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r AURA-ML ml_impact_predictor

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: attack_type_counts, counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type, last_objective_bonus
- Changing belief keys: attack_type_counts, counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type, last_objective_bonus
- Feedback keys: attack_threshold, attack_type_counts, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget, selected_base_attack_score, selected_objective_bonus, selected_repeated_tactic_penalty
- Last-selected chain: 30/30
- Effect summary: AURA memory carries attack cadence and last attack context into later candidate decisions; changing=attack_type_counts, counter_defense_context_seen, defense_context, event_count, last_attack_time, last_attack_type, last_objective_bonus; feedback=attack_threshold, attack_type_counts, cooldown_remaining_sec, cooldown_sec, defense_context, event_count, remaining_event_budget, selected_base_attack_score, selected_objective_bonus, selected_repeated_tactic_penalty.
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r TSRA-R-ML ml_anomaly_detector

- Memory coverage: 1
- Observation count: 1 -> 24 (true)
- Decision count: 0 -> 24 (true)
- Belief keys: active_defense_until, attack_context, attack_context_seen, last_alert_time, last_early_guard_triggered, last_mission_guard_reason, last_mission_guard_score, last_probability
- Changing belief keys: active_defense_until, attack_context, attack_context_seen, last_alert_time, last_early_guard_triggered, last_mission_guard_reason, last_mission_guard_score, last_probability
- Feedback keys: active_defense_until, attack_context, detector_triggered, early_guard_triggered, event_count, expiry_guard_triggered, mission_guard_reason, mission_guard_score, mission_guard_triggered, opened_window, probability, threshold
- Last-selected chain: 60/60
- Effect summary: ML TSRA-R memory carries anomaly probability and active defense window state into reactive defense decisions; changing=active_defense_until, attack_context, attack_context_seen, last_alert_time, last_early_guard_triggered, last_mission_guard_reason, last_mission_guard_score, last_probability; feedback=active_defense_until, attack_context, detector_triggered, early_guard_triggered, event_count, expiry_guard_triggered, mission_guard_reason, mission_guard_score, mission_guard_triggered, opened_window, probability, threshold.
- Status: pass
- Issues: none
