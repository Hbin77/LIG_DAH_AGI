# Defense Priority Decision Path Audit

This audit verifies that TSRA-R defense priority scores are formula-backed, bounded, and connected to selected DefenseEvent ordering.
Safety boundary: closed simulation defense-priority decision-path audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| DPR01 | Candidate priority score contract | pass | scored_candidates=671; base_score_present=671; formula_matches=671; reason_count=671 | TSRA-R candidate priority is explicit rather than implicit branch order. |
| DPR02 | Bounded priority score inputs | pass | max_score=0.94; max_attack_context_bonus=0.12; negative_scores=0; over_bound_scores=0; non_eligible_bonus=0 | The score term is bounded and cannot silently turn an ineligible defense into an emitted event. |
| DPR03 | Attack-context priority bonus | pass | attack_context_bonus_candidates=177; attack_context_bonus_events=51; bonus_reasons=counter_link_or_failover_attack,counter_queue_pressure_priority_reroute,counter_stale_cop_induction,counter_video_queue_pressure | The defense agent uses attack context in its scoring path, not only in logs. |
| DPR04 | Selected event score consistency | pass | checked_event_matches=70; event_match_failures=0; no_candidate_for_event=0 | DefenseEvent details preserve the same priority evidence used in the decision trace. |
| DPR05 | Core defense event ordering | pass | ordered_core_defense_traces=12/12 | The simulator receives same-tick core defenses in the order selected by the agent score. |
| DPR06 | No-op and ready-action consistency | pass | no_op_traces=122; no_op_ready_violations=0; defense_event_traces=61; unselected_ready_actions=0; selected_without_ready=0; condition_trace_count=183; missing_condition_tool_traces=0; condition_candidate_checks=671; condition_candidate_matches=671; condition_candidate_mismatches=0; pace_reason_matches=122; pace_reason_mismatches=0 | Priority scoring refines defense ordering without weakening the existing eligibility and cooldown gates, and candidate ready/eligible fields match the condition tool output. |

## Detail

### DPR01 Candidate priority score contract

- Requirement: Every TSRA-R core defense candidate should expose a reproducible priority score formula.
- Evidence: outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: scored_candidates=671; base_score_present=671; formula_matches=671; reason_count=671
- Status: pass
- Interpretation: TSRA-R candidate priority is explicit rather than implicit branch order.
- Safety boundary: closed simulation defense-priority decision-path audit only; no RF, exploit, or live network action

### DPR02 Bounded priority score inputs

- Requirement: Defense priority scores and attack-context bonuses should remain bounded and only apply to eligible actions.
- Evidence: outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: max_score=0.94; max_attack_context_bonus=0.12; negative_scores=0; over_bound_scores=0; non_eligible_bonus=0
- Status: pass
- Interpretation: The score term is bounded and cannot silently turn an ineligible defense into an emitted event.
- Safety boundary: closed simulation defense-priority decision-path audit only; no RF, exploit, or live network action

### DPR03 Attack-context priority bonus

- Requirement: AURA attack context should create bounded TSRA-R priority bonuses when the attack type matches the defense action.
- Evidence: outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: attack_context_bonus_candidates=177; attack_context_bonus_events=51; bonus_reasons=counter_link_or_failover_attack,counter_queue_pressure_priority_reroute,counter_stale_cop_induction,counter_video_queue_pressure
- Status: pass
- Interpretation: The defense agent uses attack context in its scoring path, not only in logs.
- Safety boundary: closed simulation defense-priority decision-path audit only; no RF, exploit, or live network action

### DPR04 Selected event score consistency

- Requirement: Selected Rule TSRA-R defense events should carry priority details matching their candidate row.
- Evidence: outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: checked_event_matches=70; event_match_failures=0; no_candidate_for_event=0
- Status: pass
- Interpretation: DefenseEvent details preserve the same priority evidence used in the decision trace.
- Safety boundary: closed simulation defense-priority decision-path audit only; no RF, exploit, or live network action

### DPR05 Core defense event ordering

- Requirement: When multiple core defenses are emitted in the same decision, their event order should follow priority score.
- Evidence: outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: ordered_core_defense_traces=12/12
- Status: pass
- Interpretation: The simulator receives same-tick core defenses in the order selected by the agent score.
- Safety boundary: closed simulation defense-priority decision-path audit only; no RF, exploit, or live network action

### DPR06 No-op and ready-action consistency

- Requirement: No-op traces should have no ready scored defense action, and selected events should not omit ready actions.
- Evidence: outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: no_op_traces=122; no_op_ready_violations=0; defense_event_traces=61; unselected_ready_actions=0; selected_without_ready=0; condition_trace_count=183; missing_condition_tool_traces=0; condition_candidate_checks=671; condition_candidate_matches=671; condition_candidate_mismatches=0; pace_reason_matches=122; pace_reason_mismatches=0
- Status: pass
- Interpretation: Priority scoring refines defense ordering without weakening the existing eligibility and cooldown gates, and candidate ready/eligible fields match the condition tool output.
- Safety boundary: closed simulation defense-priority decision-path audit only; no RF, exploit, or live network action
