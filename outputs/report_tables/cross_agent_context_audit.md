# Cross-Agent Context Audit

This audit verifies that AURA and TSRA-R exchange opponent-context evidence through AgentRuntime observations, tool calls, memory, feedback, candidate rows, and emitted events.
Safety boundary: closed simulation cross-agent context audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| XAG01 | Shared observation context | pass | aura_observation_context=62/62; tsra_observation_context=122/122 | Both agents observe the same simulation clock plus opponent-context summaries. |
| XAG02 | TSRA-R attack-context tool path | pass | tsra_traces=122; summarize_attack_context=122; feedback_attack_context=122; memory_attack_context=122; candidate_attack_context=305/305; candidate_attack_context_used=147; tool_errors=0 | TSRA-R is using AURA event context inside its agent loop, not only in downstream reports. |
| XAG03 | Attack-to-defense handoff | pass | attack_handoffs=10/10; response_window_sec=5 | The defense agent receives attack context before it emits the response-window decisions. |
| XAG04 | AURA defense-context tool path | pass | aura_traces=62; summarize_defense_context=62; feedback_defense_context=62; memory_defense_context=62; candidate_defense_context=51/51; candidate_defense_context_used=47; selected_attack_with_defense_context=9 | AURA records the defender state that explains counter-defense choices such as failover chasing. |
| XAG05 | Defense-to-attack handoff | pass | experiments_with_post_defense_context=2/2; defense_context_seen_traces=51; selected_attack_with_defense_context=9 | The attack agent can see that TSRA-R has changed the battlefield before later attack selections. |
| XAG06 | Event-level context consistency | pass | defense_events=52; related_context_events=52; active_related_events=50; missing_related_context=0 | Selected defense events retain the attack context that was visible during the decision. |

## Detail

### XAG01 Shared observation context

- Requirement: AURA and TSRA-R observations should expose closed-loop opponent context fields.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl | outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: aura_observation_context=62/62; tsra_observation_context=122/122
- Status: pass
- Interpretation: Both agents observe the same simulation clock plus opponent-context summaries.
- Safety boundary: closed simulation cross-agent context audit only; no RF, exploit, or live network action

### XAG02 TSRA-R attack-context tool path

- Requirement: Every TSRA-R decision should call the attack-context tool and keep attack context in memory, feedback, and candidates.
- Evidence: outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: tsra_traces=122; summarize_attack_context=122; feedback_attack_context=122; memory_attack_context=122; candidate_attack_context=305/305; candidate_attack_context_used=147; tool_errors=0
- Status: pass
- Interpretation: TSRA-R is using AURA event context inside its agent loop, not only in downstream reports.
- Safety boundary: closed simulation cross-agent context audit only; no RF, exploit, or live network action

### XAG03 Attack-to-defense handoff

- Requirement: Each AURA attack should be visible to the first TSRA-R decision in the immediate response window.
- Evidence: outputs/experiments/*/attack_events.jsonl | outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: attack_handoffs=10/10; response_window_sec=5
- Status: pass
- Interpretation: The defense agent receives attack context before it emits the response-window decisions.
- Safety boundary: closed simulation cross-agent context audit only; no RF, exploit, or live network action

### XAG04 AURA defense-context tool path

- Requirement: Every AURA decision should call the defense-context tool and keep defense context in memory, feedback, and candidates.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl
- Observed: aura_traces=62; summarize_defense_context=62; feedback_defense_context=62; memory_defense_context=62; candidate_defense_context=51/51; candidate_defense_context_used=47; selected_attack_with_defense_context=9
- Status: pass
- Interpretation: AURA records the defender state that explains counter-defense choices such as failover chasing.
- Safety boundary: closed simulation cross-agent context audit only; no RF, exploit, or live network action

### XAG05 Defense-to-attack handoff

- Requirement: After TSRA-R emits defenses, later AURA traces should carry active or recent defense context.
- Evidence: outputs/experiments/*/defense_events.jsonl | outputs/experiments/*/aura_decision_traces.jsonl
- Observed: experiments_with_post_defense_context=2/2; defense_context_seen_traces=51; selected_attack_with_defense_context=9
- Status: pass
- Interpretation: The attack agent can see that TSRA-R has changed the battlefield before later attack selections.
- Safety boundary: closed simulation cross-agent context audit only; no RF, exploit, or live network action

### XAG06 Event-level context consistency

- Requirement: Defense events emitted in closed-loop runs should carry related AURA attack context for auditability.
- Evidence: outputs/experiments/*/defense_events.jsonl
- Observed: defense_events=52; related_context_events=52; active_related_events=50; missing_related_context=0
- Status: pass
- Interpretation: Selected defense events retain the attack context that was visible during the decision.
- Safety boundary: closed simulation cross-agent context audit only; no RF, exploit, or live network action
