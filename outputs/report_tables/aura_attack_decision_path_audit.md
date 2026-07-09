# AURA Attack Decision Path Audit

This audit verifies that AURA and AURA-ML candidate scoring, selected actions, AttackEvent payloads, cadence gates, and defense-context score terms stay connected.
Safety boundary: closed simulation AURA attack decision-path audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| AAP01 | Candidate score contract | pass | candidate_total=123; rule_candidates=72; ml_candidates=51; base_formula_matches=123; selection_formula_matches=123 | AURA candidate ranking is formula-backed instead of relying on implicit branch order. |
| AAP02 | Candidate scoring toolchain | pass | candidate_traces=25; candidate_total=123; generated_candidate_total=123; generated_candidate_payload_matches=25; generated_candidate_payload_mismatches=0; generate_attack_candidates=25; estimate_candidate_effect=123; estimate_detectability=123; predict_candidate_impact=51; tool_errors=0; all_trace_tool_errors=0 | AURA uses AgentRuntime tools for generation and scoring rather than hidden inline state, and generated candidate payloads match the candidate_actions that are actually scored. |
| AAP03 | Top-score selection and event link | pass | attack_trace_count=25; attack_event_count=25; selected_matches_top_candidate=25; linked_attack_events=25; score_event_matches=25; type_link_event_matches=25; event_time_matches=25; event_agent_matches_trace=25; threshold_passes=25 | AURA selected actions are directly traceable to event logs and threshold support. |
| AAP04 | No-op and cadence gate discipline | pass | noop_traces=130; pre_start_noops=30; cooldown_noops=80; max_event_noops=20; below_threshold_noops=0; no_candidate_noops=0; pre_start_attack_events=0; min_attack_gap_sec=50; cooldown_gap_violations=0; event_budget_violations=0; no_op_threshold_violations=0 | AURA is an agent with start, cadence, threshold, and event-budget gates, not an always-fire loop. |
| AAP05 | AttackEvent payload consistency | pass | event_payloads=25; impact_field_matches=25; event_score_formula_matches=25; selected_at_matches_candidate=25; allowed_agent_events=25; allowed_attack_type_events=25; rule_agent_events=15; ml_agent_events=10 | AttackEvent logs preserve the same decision evidence and agent identity used by traces. |
| AAP06 | Tactical and defense-context coverage | pass | attack_types=bandwidth_limit,failover_chasing,queue_pressure,stale_cop_induction; target_links=LTE,MESH,SATCOM; defense_context_candidates=123; defense_context_used_candidates=95; selected_with_defense_context=19; objective_bonus_candidates=2; counter_defense_bonus_candidates=15; summarize_defense_context=155 | AURA/AURA-ML expose mission-tactic coverage and use TSRA-R context as bounded score evidence. |

## Detail

### AAP01 Candidate score contract

- Requirement: Every AURA candidate should expose a reproducible attack score formula; AURA-ML should additionally expose the bounded selection-score formula.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl
- Observed: candidate_total=123; rule_candidates=72; ml_candidates=51; base_formula_matches=123; selection_formula_matches=123
- Status: pass
- Interpretation: AURA candidate ranking is formula-backed instead of relying on implicit branch order.
- Safety boundary: closed simulation AURA attack decision-path audit only; no RF, exploit, or live network action

### AAP02 Candidate scoring toolchain

- Requirement: Candidate-generating traces should call candidate generation once, estimate effect and detectability for each candidate, and call ML prediction for each ML candidate.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl
- Observed: candidate_traces=25; candidate_total=123; generated_candidate_total=123; generated_candidate_payload_matches=25; generated_candidate_payload_mismatches=0; generate_attack_candidates=25; estimate_candidate_effect=123; estimate_detectability=123; predict_candidate_impact=51; tool_errors=0; all_trace_tool_errors=0
- Status: pass
- Interpretation: AURA uses AgentRuntime tools for generation and scoring rather than hidden inline state, and generated candidate payloads match the candidate_actions that are actually scored.
- Safety boundary: closed simulation AURA attack decision-path audit only; no RF, exploit, or live network action

### AAP03 Top-score selection and event link

- Requirement: Selected attack events should match the highest-scored candidate and the persisted AttackEvent log by id, score, type, link, time, and agent.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl | outputs/experiments/*/attack_events.jsonl
- Observed: attack_trace_count=25; attack_event_count=25; selected_matches_top_candidate=25; linked_attack_events=25; score_event_matches=25; type_link_event_matches=25; event_time_matches=25; event_agent_matches_trace=25; threshold_passes=25
- Status: pass
- Interpretation: AURA selected actions are directly traceable to event logs and threshold support.
- Safety boundary: closed simulation AURA attack decision-path audit only; no RF, exploit, or live network action

### AAP04 No-op and cadence gate discipline

- Requirement: AURA should avoid pre-start attacks, respect cooldown gaps and max-event budget, and never choose no-op while a candidate is above threshold.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl | outputs/experiments/*/attack_events.jsonl
- Observed: noop_traces=130; pre_start_noops=30; cooldown_noops=80; max_event_noops=20; below_threshold_noops=0; no_candidate_noops=0; pre_start_attack_events=0; min_attack_gap_sec=50; cooldown_gap_violations=0; event_budget_violations=0; no_op_threshold_violations=0
- Status: pass
- Interpretation: AURA is an agent with start, cadence, threshold, and event-budget gates, not an always-fire loop.
- Safety boundary: closed simulation AURA attack decision-path audit only; no RF, exploit, or live network action

### AAP05 AttackEvent payload consistency

- Requirement: Persisted AttackEvent payloads should carry mission-impact fields, score formula evidence, valid agent labels, valid attack types, and candidate start-time consistency.
- Evidence: outputs/experiments/*/attack_events.jsonl
- Observed: event_payloads=25; impact_field_matches=25; event_score_formula_matches=25; selected_at_matches_candidate=25; allowed_agent_events=25; allowed_attack_type_events=25; rule_agent_events=15; ml_agent_events=10
- Status: pass
- Interpretation: AttackEvent logs preserve the same decision evidence and agent identity used by traces.
- Safety boundary: closed simulation AURA attack decision-path audit only; no RF, exploit, or live network action

### AAP06 Tactical and defense-context coverage

- Requirement: AURA should cover multiple simulated tactics and links, carry defense context into candidate rows, and expose bounded objective/counter-defense score evidence.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl | outputs/experiments/*/attack_events.jsonl
- Observed: attack_types=bandwidth_limit,failover_chasing,queue_pressure,stale_cop_induction; target_links=LTE,MESH,SATCOM; defense_context_candidates=123; defense_context_used_candidates=95; selected_with_defense_context=19; objective_bonus_candidates=2; counter_defense_bonus_candidates=15; summarize_defense_context=155
- Status: pass
- Interpretation: AURA/AURA-ML expose mission-tactic coverage and use TSRA-R context as bounded score evidence.
- Safety boundary: closed simulation AURA attack decision-path audit only; no RF, exploit, or live network action
