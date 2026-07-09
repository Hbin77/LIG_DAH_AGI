# Agent Capability Matrix

This matrix maps AURA/TSRA-R capabilities to runtime actions and validation evidence.

Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

| capability_id | side | agent_family | capability | evidence_count | observed_effect | validation_gate |
|---|---|---|---|---:|---|---|
| ATK-01 | attack | AURA | bandwidth_limit | 3 | targets=SATCOM; max_expected_impact=1; avg_attack_score=0.9475 | G01/G02 |
| ATK-02 | attack | AURA-ML | failover_chasing | 3 | targets=LTE,MESH; max_expected_impact=0.916793; avg_attack_score=0.777388 | G02/G10 |
| ATK-03 | attack | AURA, AURA-ML | queue_pressure | 8 | targets=LTE,MESH,SATCOM; max_expected_impact=1; avg_attack_score=0.787551 | G01/G02 |
| ATK-04 | attack | AURA | stale_cop_induction | 1 | targets=SATCOM; max_expected_impact=1; avg_attack_score=0.9175 | G01/G02 |
| DEF-01 | defense | TSRA-R-ML | ml_attack_alert | 9 | ML detector opens or maintains reactive defense window; validated by E6/E7 separation gate | G10 |
| DEF-02 | defense | TSRA-R, TSRA-R-ML | pace_switch | 4 | removal_delta_recovery_instability=-2.06667; used as bounded fallback path control | G03/G04 |
| DEF-03 | defense | TSRA-R, TSRA-R-ML | priority_reroute | 13 | removal_delta_priority_inversion=0.424361; removal_delta_impact=0.19956 | G03/G04/G06 |
| DEF-04 | defense | TSRA-R, TSRA-R-ML | stale_badge | 16 | removal_delta_trusted_stale=0.375; removal_delta_impact=0.20625 | G03/G05/G07 |
| DEF-05 | defense | TSRA-R, TSRA-R-ML | video_throttle | 14 | removal_delta_impact=-0.0231413; used as optional capacity control | G03/G09 |
| DEF-ADAPT-01 | defense | TSRA-R-ADAPTIVE | adaptive_optional_action_gating | 30 seeds | mission_impact_improvement=0.0307717; video_throttle_reduction=3.26667 | G08/G09 |

## Detail

### ATK-01 bandwidth_limit

- Side: attack
- Agent family: AURA
- Runtime actions: attack_event
- Decision source: generate_attack_candidates, estimate_candidate_effect, estimate_detectability
- Trigger or selection logic: reduce available capacity during queue growth
- Evidence count: 3
- Evidence experiments: E3_rule_aura
- Observed effect: targets=SATCOM; max_expected_impact=1; avg_attack_score=0.9475
- Validation gate: G01/G02
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### ATK-02 failover_chasing

- Side: attack
- Agent family: AURA-ML
- Runtime actions: attack_event
- Decision source: generate_attack_candidates, estimate_candidate_effect, estimate_detectability, predict_candidate_impact
- Trigger or selection logic: ML impact predictor selected failover_chasing
- Evidence count: 3
- Evidence experiments: E7_ml_aura_ml_tsra_r
- Observed effect: targets=LTE,MESH; max_expected_impact=0.916793; avg_attack_score=0.777388
- Validation gate: G02/G10
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### ATK-03 queue_pressure

- Side: attack
- Agent family: AURA, AURA-ML
- Runtime actions: attack_event
- Decision source: generate_attack_candidates, estimate_candidate_effect, estimate_detectability, predict_candidate_impact
- Trigger or selection logic: increase non-critical queue occupancy
- Evidence count: 8
- Evidence experiments: E3_rule_aura, E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
- Observed effect: targets=LTE,MESH,SATCOM; max_expected_impact=1; avg_attack_score=0.787551
- Validation gate: G01/G02
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### ATK-04 stale_cop_induction

- Side: attack
- Agent family: AURA
- Runtime actions: attack_event
- Decision source: generate_attack_candidates, estimate_candidate_effect, estimate_detectability
- Trigger or selection logic: COP freshness is already degraded
- Evidence count: 1
- Evidence experiments: E3_rule_aura
- Observed effect: targets=SATCOM; max_expected_impact=1; avg_attack_score=0.9175
- Validation gate: G01/G02
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### DEF-01 ml_attack_alert

- Side: defense
- Agent family: TSRA-R-ML
- Runtime actions: defense_events
- Decision source: predict_attack_probability
- Trigger or selection logic: detector probability exceeds threshold
- Evidence count: 9
- Evidence experiments: E7_ml_aura_ml_tsra_r
- Observed effect: ML detector opens or maintains reactive defense window; validated by E6/E7 separation gate
- Validation gate: G10
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### DEF-02 pace_switch

- Side: defense
- Agent family: TSRA-R, TSRA-R-ML
- Runtime actions: defense_events
- Decision source: TSRA-R: evaluate_defense_conditions, select_fallback_link; TSRA-R-ML: predict_attack_probability, assess_mission_risk_guard, reactive defense window
- Trigger or selection logic: active link degradation crosses mission threshold
- Evidence count: 4
- Evidence experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
- Observed effect: removal_delta_recovery_instability=-2.06667; used as bounded fallback path control
- Validation gate: G03/G04
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### DEF-03 priority_reroute

- Side: defense
- Agent family: TSRA-R, TSRA-R-ML
- Runtime actions: defense_events
- Decision source: TSRA-R: evaluate_defense_conditions; TSRA-R-ML: predict_attack_probability, assess_mission_risk_guard, reactive defense window
- Trigger or selection logic: critical traffic waits behind video or queue pressure
- Evidence count: 13
- Evidence experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
- Observed effect: removal_delta_priority_inversion=0.424361; removal_delta_impact=0.19956
- Validation gate: G03/G04/G06
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### DEF-04 stale_badge

- Side: defense
- Agent family: TSRA-R, TSRA-R-ML
- Runtime actions: defense_events
- Decision source: TSRA-R: evaluate_defense_conditions; TSRA-R-ML: predict_attack_probability, assess_mission_risk_guard, reactive defense window
- Trigger or selection logic: COP stale ratio exceeds trust threshold
- Evidence count: 16
- Evidence experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
- Observed effect: removal_delta_trusted_stale=0.375; removal_delta_impact=0.20625
- Validation gate: G03/G05/G07
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### DEF-05 video_throttle

- Side: defense
- Agent family: TSRA-R, TSRA-R-ML
- Runtime actions: defense_events
- Decision source: TSRA-R: evaluate_defense_conditions; TSRA-R-ML: predict_attack_probability, assess_mission_risk_guard, reactive defense window
- Trigger or selection logic: video load threatens critical traffic capacity
- Evidence count: 14
- Evidence experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
- Observed effect: removal_delta_impact=-0.0231413; used as optional capacity control
- Validation gate: G03/G09
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action

### DEF-ADAPT-01 adaptive_optional_action_gating

- Side: defense
- Agent family: TSRA-R-ADAPTIVE
- Runtime actions: memory-backed policy gate
- Decision source: AgentMemory, update_adaptive_action_policy
- Trigger or selection logic: optional actions require repeated memory evidence before activation
- Evidence count: 30 seeds
- Evidence experiments: adaptive_memory_summary
- Observed effect: mission_impact_improvement=0.0307717; video_throttle_reduction=3.26667
- Validation gate: G08/G09
- Safety boundary: closed simulation capability matrix only; no RF, exploit, or live network action
