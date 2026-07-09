# DecisionTrace Quality Audit

This table audits whether AURA and TSRA-R traces show a complete agent decision loop.

Safety boundary: closed simulation trace-quality audit only; no RF, exploit, or live network action

| experiment | agent | policy | trace_count | tool_call_coverage | candidate_action_coverage | non_noop_count | selected_event_count | status | issues |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E3_rule_aura | AURA | rule_attack_score | 31 | 1 | 0.16129 | 5 | 5 | pass |  |
| E4_rule_aura_basic_defense | AURA | rule_attack_score | 31 | 1 | 0.16129 | 5 | 5 | pass |  |
| E4_rule_aura_basic_defense | TSRA-R | rule_defense_basic | 61 | 1 | 1 | 21 | 24 | pass |  |
| E5_rule_aura_tsra_r | AURA | rule_attack_score | 31 | 1 | 0.16129 | 5 | 5 | pass |  |
| E5_rule_aura_tsra_r | TSRA-R | rule_defense_full | 61 | 1 | 1 | 19 | 22 | pass |  |
| E6_ml_aura_tsra_r | AURA-ML | ml_impact_predictor | 31 | 1 | 0.16129 | 5 | 5 | pass |  |
| E6_ml_aura_tsra_r | TSRA-R | rule_defense_full | 61 | 1 | 1 | 21 | 24 | pass |  |
| E7_ml_aura_ml_tsra_r | AURA-ML | ml_impact_predictor | 31 | 1 | 0.16129 | 5 | 5 | pass |  |
| E7_ml_aura_ml_tsra_r | TSRA-R-ML | ml_anomaly_detector | 61 | 1 | 1 | 20 | 30 | pass |  |
| E7_ml_aura_ml_tsra_r | TSRA-R | rule_defense_full | 47 | 1 | 1 | 16 | 22 | pass |  |
