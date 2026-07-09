# Agent Runtime Invariant Audit

This audit checks runtime-level invariants across DecisionTrace logs.
Safety boundary: closed simulation agent-runtime invariant audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 10
- Status counts: pass=10

## Runtime Invariants

| experiment | agent | policy | trace_count | trace_id_sequence_ok | decision_count_expected | tool_error_count | status | issues |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E3_rule_aura | AURA | rule_attack_score | 31 | true | true | 0 | pass |  |
| E4_rule_aura_basic_defense | AURA | rule_attack_score | 31 | true | true | 0 | pass |  |
| E4_rule_aura_basic_defense | TSRA-R | rule_defense_basic | 61 | true | true | 0 | pass |  |
| E5_rule_aura_tsra_r | AURA | rule_attack_score | 31 | true | true | 0 | pass |  |
| E5_rule_aura_tsra_r | TSRA-R | rule_defense_full | 61 | true | true | 0 | pass |  |
| E6_ml_aura_tsra_r | AURA-ML | ml_impact_predictor | 31 | true | true | 0 | pass |  |
| E6_ml_aura_tsra_r | TSRA-R | rule_defense_full | 61 | true | true | 0 | pass |  |
| E7_ml_aura_ml_tsra_r | AURA-ML | ml_impact_predictor | 31 | true | true | 0 | pass |  |
| E7_ml_aura_ml_tsra_r | TSRA-R-ML | ml_anomaly_detector | 61 | true | true | 0 | pass |  |
| E7_ml_aura_ml_tsra_r | TSRA-R | rule_defense_full | 47 | true | true | 0 | pass |  |
