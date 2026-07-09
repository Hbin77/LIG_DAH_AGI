# Agent Tool Usage Audit

This audit verifies that agent tools are actually invoked inside DecisionTrace records with input and output summaries.
Safety boundary: closed simulation agent-tool audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 24
- Status counts: pass=24
- Tools: assess_mission_risk_guard, estimate_candidate_effect, estimate_detectability, evaluate_defense_conditions, generate_attack_candidates, predict_attack_probability, predict_candidate_impact, select_fallback_link

## Tool Table

| experiment | agent | policy | tool_name | invocation_count | trace_coverage | status |
| --- | --- | --- | --- | --- | --- | --- |
| E3_rule_aura | AURA | rule_attack_score | estimate_candidate_effect | 24 | 0.16129 | pass |
| E3_rule_aura | AURA | rule_attack_score | estimate_detectability | 24 | 0.16129 | pass |
| E3_rule_aura | AURA | rule_attack_score | generate_attack_candidates | 5 | 0.16129 | pass |
| E4_rule_aura_basic_defense | AURA | rule_attack_score | estimate_candidate_effect | 23 | 0.16129 | pass |
| E4_rule_aura_basic_defense | AURA | rule_attack_score | estimate_detectability | 23 | 0.16129 | pass |
| E4_rule_aura_basic_defense | AURA | rule_attack_score | generate_attack_candidates | 5 | 0.16129 | pass |
| E4_rule_aura_basic_defense | TSRA-R | rule_defense_basic | evaluate_defense_conditions | 61 | 1 | pass |
| E5_rule_aura_tsra_r | AURA | rule_attack_score | estimate_candidate_effect | 25 | 0.16129 | pass |
| E5_rule_aura_tsra_r | AURA | rule_attack_score | estimate_detectability | 25 | 0.16129 | pass |
| E5_rule_aura_tsra_r | AURA | rule_attack_score | generate_attack_candidates | 5 | 0.16129 | pass |
| E5_rule_aura_tsra_r | TSRA-R | rule_defense_full | evaluate_defense_conditions | 61 | 1 | pass |
| E5_rule_aura_tsra_r | TSRA-R | rule_defense_full | select_fallback_link | 1 | 0.0163934 | pass |
| E6_ml_aura_tsra_r | AURA-ML | ml_impact_predictor | estimate_candidate_effect | 25 | 0.16129 | pass |
| E6_ml_aura_tsra_r | AURA-ML | ml_impact_predictor | estimate_detectability | 25 | 0.16129 | pass |
| E6_ml_aura_tsra_r | AURA-ML | ml_impact_predictor | generate_attack_candidates | 5 | 0.16129 | pass |
| E6_ml_aura_tsra_r | AURA-ML | ml_impact_predictor | predict_candidate_impact | 25 | 0.16129 | pass |
| E6_ml_aura_tsra_r | TSRA-R | rule_defense_full | evaluate_defense_conditions | 61 | 1 | pass |
| E6_ml_aura_tsra_r | TSRA-R | rule_defense_full | select_fallback_link | 2 | 0.0327869 | pass |
| E7_ml_aura_ml_tsra_r | AURA-ML | ml_impact_predictor | estimate_candidate_effect | 26 | 0.16129 | pass |
| E7_ml_aura_ml_tsra_r | AURA-ML | ml_impact_predictor | estimate_detectability | 26 | 0.16129 | pass |
| E7_ml_aura_ml_tsra_r | AURA-ML | ml_impact_predictor | generate_attack_candidates | 5 | 0.16129 | pass |
| E7_ml_aura_ml_tsra_r | AURA-ML | ml_impact_predictor | predict_candidate_impact | 26 | 0.16129 | pass |
| E7_ml_aura_ml_tsra_r | TSRA-R-ML | ml_anomaly_detector | assess_mission_risk_guard | 61 | 1 | pass |
| E7_ml_aura_ml_tsra_r | TSRA-R-ML | ml_anomaly_detector | predict_attack_probability | 61 | 1 | pass |

## By Tool

### assess_mission_risk_guard

- Role: TSRA-R ML residual mission-risk guard assessment
- Rows: 1
- Total invocations: 61
- Status: pass=1
- Decision link: Residual mission risk can extend a previously opened TSRA-R-ML defense window

### estimate_candidate_effect

- Role: AURA analytic mission-impact what-if estimate
- Rows: 5
- Total invocations: 123
- Status: pass=5
- Decision link: mission impact estimates feed AURA score calculation

### estimate_detectability

- Role: AURA detectability penalty estimate
- Rows: 5
- Total invocations: 123
- Status: pass=5
- Decision link: detectability penalty is subtracted from AURA attack score

### evaluate_defense_conditions

- Role: TSRA-R defense condition evaluation
- Rows: 3
- Total invocations: 183
- Status: pass=3
- Decision link: condition outputs drive TSRA-R defense action candidates

### generate_attack_candidates

- Role: AURA attack candidate generation
- Rows: 5
- Total invocations: 25
- Status: pass=5
- Decision link: candidate_actions are generated before AURA ranks attack effects

### predict_attack_probability

- Role: TSRA-R ML anomaly probability prediction
- Rows: 1
- Total invocations: 61
- Status: pass=1
- Decision link: ML anomaly probability opens TSRA-R reactive defense window

### predict_candidate_impact

- Role: AURA ML impact prediction
- Rows: 2
- Total invocations: 51
- Status: pass=2
- Decision link: ML impact prediction feeds AURA-ML candidate ranking

### select_fallback_link

- Role: TSRA-R PACE fallback selection
- Rows: 2
- Total invocations: 3
- Status: pass=2
- Decision link: PACE fallback selection drives TSRA-R pace_switch details
