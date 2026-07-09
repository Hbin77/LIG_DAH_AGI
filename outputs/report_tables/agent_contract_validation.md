# Agent Contract Validation

This table validates the interface contract between AURA, TSRA-R, and MissionSimulator logs.

Safety boundary: closed simulation event-contract validation only; no RF, exploit, or live network action

| experiment | contract | status | checked_rows | issues |
|---|---|---|---:|---|
| E1_baseline | attack_event_schema | pass | 0 | none |
| E1_baseline | defense_event_schema | pass | 0 | none |
| E1_baseline | metric_snapshot_schema | pass | 61 | none |
| E1_baseline | mission_event_schema | pass | 701 | none |
| E1_baseline | aura_decision_trace_schema | pass | 0 | none |
| E1_baseline | tsra-r_decision_trace_schema | pass | 0 | none |
| E1_baseline | agent_cross_contract | pass | 61 | none |
| E2_fixed_attack | attack_event_schema | pass | 1 | none |
| E2_fixed_attack | defense_event_schema | pass | 0 | none |
| E2_fixed_attack | metric_snapshot_schema | pass | 61 | none |
| E2_fixed_attack | mission_event_schema | pass | 703 | none |
| E2_fixed_attack | aura_decision_trace_schema | pass | 0 | none |
| E2_fixed_attack | tsra-r_decision_trace_schema | pass | 0 | none |
| E2_fixed_attack | agent_cross_contract | pass | 62 | none |
| E3_rule_aura | attack_event_schema | pass | 5 | none |
| E3_rule_aura | defense_event_schema | pass | 0 | none |
| E3_rule_aura | metric_snapshot_schema | pass | 61 | none |
| E3_rule_aura | mission_event_schema | pass | 492 | none |
| E3_rule_aura | aura_decision_trace_schema | pass | 31 | none |
| E3_rule_aura | tsra-r_decision_trace_schema | pass | 0 | none |
| E3_rule_aura | agent_cross_contract | pass | 66 | none |
| E4_rule_aura_basic_defense | attack_event_schema | pass | 5 | none |
| E4_rule_aura_basic_defense | defense_event_schema | pass | 24 | none |
| E4_rule_aura_basic_defense | metric_snapshot_schema | pass | 61 | none |
| E4_rule_aura_basic_defense | mission_event_schema | pass | 802 | none |
| E4_rule_aura_basic_defense | aura_decision_trace_schema | pass | 31 | none |
| E4_rule_aura_basic_defense | tsra-r_decision_trace_schema | pass | 61 | none |
| E4_rule_aura_basic_defense | agent_cross_contract | pass | 90 | none |
| E5_rule_aura_tsra_r | attack_event_schema | pass | 5 | none |
| E5_rule_aura_tsra_r | defense_event_schema | pass | 22 | none |
| E5_rule_aura_tsra_r | metric_snapshot_schema | pass | 61 | none |
| E5_rule_aura_tsra_r | mission_event_schema | pass | 810 | none |
| E5_rule_aura_tsra_r | aura_decision_trace_schema | pass | 31 | none |
| E5_rule_aura_tsra_r | tsra-r_decision_trace_schema | pass | 61 | none |
| E5_rule_aura_tsra_r | agent_cross_contract | pass | 88 | none |
| E6_ml_aura_tsra_r | attack_event_schema | pass | 5 | none |
| E6_ml_aura_tsra_r | defense_event_schema | pass | 24 | none |
| E6_ml_aura_tsra_r | metric_snapshot_schema | pass | 61 | none |
| E6_ml_aura_tsra_r | mission_event_schema | pass | 745 | none |
| E6_ml_aura_tsra_r | aura_decision_trace_schema | pass | 31 | none |
| E6_ml_aura_tsra_r | tsra-r_decision_trace_schema | pass | 61 | none |
| E6_ml_aura_tsra_r | agent_cross_contract | pass | 90 | none |
| E7_ml_aura_ml_tsra_r | attack_event_schema | pass | 5 | none |
| E7_ml_aura_ml_tsra_r | defense_event_schema | pass | 30 | none |
| E7_ml_aura_ml_tsra_r | metric_snapshot_schema | pass | 61 | none |
| E7_ml_aura_ml_tsra_r | mission_event_schema | pass | 757 | none |
| E7_ml_aura_ml_tsra_r | aura_decision_trace_schema | pass | 31 | none |
| E7_ml_aura_ml_tsra_r | tsra-r_decision_trace_schema | pass | 61 | none |
| E7_ml_aura_ml_tsra_r | tsra-r_rule_delegate_trace_schema | pass | 47 | none |
| E7_ml_aura_ml_tsra_r | agent_cross_contract | pass | 96 | none |
