# Adaptive Defense Decision Path Audit

This audit verifies that Adaptive TSRA-R uses AgentMemory to gate optional defense actions while preserving core protections.
Safety boundary: closed simulation adaptive-defense decision-path audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| ADP01 | Batch-level adaptive effect | pass | mission_improvement=0.0307717; defense_count_reduction=3.93333; video_throttle_reduction=3.26667; pace_switch_reduction=1.06667; trusted_stale_delta=0 | The adaptive policy improves mission impact by reducing optional defensive load while keeping stale-COP protection intact. |
| ADP02 | Adaptive policy tool path | pass | trace_files=30; trace_count=1830; update_adaptive_action_policy=1830; candidate_total=7320; policy_feedback_count=1830; tool_errors=0 | Adaptive TSRA-R is not a post-hoc metric filter: each decision calls the policy tool and records four defense candidates. |
| ADP03 | Core defense preservation | pass | priority_enabled=1830/1830; stale_enabled=1830/1830; priority_emitted=204; stale_emitted=242 | The adaptive layer preserves the defenses that ablation proved essential: priority ordering and stale-COP trust marking. |
| ADP04 | Video throttle memory gate | pass | video_candidates=1830; video_enabled=287; video_held=1543; video_eligible_held=1146; video_gate_reasons=1830; video_emitted=93 | Video throttle remains available, but the agent withholds it on many eligible single-window spikes until memory confirms repeated pressure. |
| ADP05 | PACE switch memory gate | pass | pace_candidates=1830; pace_enabled=60; pace_held=1770; pace_eligible_held=154; pace_gate_reasons=1830; pace_emitted=30 | PACE remains a real option, but memory prevents fallback switching from becoming a repeated recovery-instability source. |
| ADP06 | Gate-to-event consistency | pass | emission_gate_violations=0; memory_evidence_candidates=7320; selected_optional_events=123 | Selected adaptive events are consistent with the candidate-level memory gate, so the trace can explain both action and restraint. |

## Detail

### ADP01 Batch-level adaptive effect

- Requirement: Adaptive TSRA-R should reduce mission impact and optional action load without increasing trusted stale exposure.
- Evidence: outputs/batch/adaptive_memory_summary.csv
- Observed: mission_improvement=0.0307717; defense_count_reduction=3.93333; video_throttle_reduction=3.26667; pace_switch_reduction=1.06667; trusted_stale_delta=0
- Status: pass
- Interpretation: The adaptive policy improves mission impact by reducing optional defensive load while keeping stale-COP protection intact.
- Safety boundary: closed simulation adaptive-defense decision-path audit only; no RF, exploit, or live network action

### ADP02 Adaptive policy tool path

- Requirement: Every adaptive TSRA-R decision should call the memory policy tool and keep candidate evidence.
- Evidence: outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/tsra_r_decision_traces.jsonl
- Observed: trace_files=30; trace_count=1830; update_adaptive_action_policy=1830; candidate_total=7320; policy_feedback_count=1830; tool_errors=0
- Status: pass
- Interpretation: Adaptive TSRA-R is not a post-hoc metric filter: each decision calls the policy tool and records four defense candidates.
- Safety boundary: closed simulation adaptive-defense decision-path audit only; no RF, exploit, or live network action

### ADP03 Core defense preservation

- Requirement: Memory gating should keep priority reroute and stale badge available as core protections.
- Evidence: outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/tsra_r_decision_traces.jsonl | outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/defense_events.jsonl
- Observed: priority_enabled=1830/1830; stale_enabled=1830/1830; priority_emitted=204; stale_emitted=242
- Status: pass
- Interpretation: The adaptive layer preserves the defenses that ablation proved essential: priority ordering and stale-COP trust marking.
- Safety boundary: closed simulation adaptive-defense decision-path audit only; no RF, exploit, or live network action

### ADP04 Video throttle memory gate

- Requirement: Video throttling should be held until repeated critical/video pressure appears in memory.
- Evidence: outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/tsra_r_decision_traces.jsonl | outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/defense_events.jsonl
- Observed: video_candidates=1830; video_enabled=287; video_held=1543; video_eligible_held=1146; video_gate_reasons=1830; video_emitted=93
- Status: pass
- Interpretation: Video throttle remains available, but the agent withholds it on many eligible single-window spikes until memory confirms repeated pressure.
- Safety boundary: closed simulation adaptive-defense decision-path audit only; no RF, exploit, or live network action

### ADP05 PACE switch memory gate

- Requirement: PACE switching should require persistent SATCOM degradation and severe queue evidence.
- Evidence: outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/tsra_r_decision_traces.jsonl | outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/defense_events.jsonl
- Observed: pace_candidates=1830; pace_enabled=60; pace_held=1770; pace_eligible_held=154; pace_gate_reasons=1830; pace_emitted=30
- Status: pass
- Interpretation: PACE remains a real option, but memory prevents fallback switching from becoming a repeated recovery-instability source.
- Safety boundary: closed simulation adaptive-defense decision-path audit only; no RF, exploit, or live network action

### ADP06 Gate-to-event consistency

- Requirement: Emitted adaptive defense events must be backed by enabled candidate gates and memory evidence.
- Evidence: outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/tsra_r_decision_traces.jsonl
- Observed: emission_gate_violations=0; memory_evidence_candidates=7320; selected_optional_events=123
- Status: pass
- Interpretation: Selected adaptive events are consistent with the candidate-level memory gate, so the trace can explain both action and restraint.
- Safety boundary: closed simulation adaptive-defense decision-path audit only; no RF, exploit, or live network action
