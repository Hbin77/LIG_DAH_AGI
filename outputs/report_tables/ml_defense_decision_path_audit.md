# ML Defense Decision Path Audit

This audit traces the E7 TSRA-R-ML path from detector probability to defense-window behavior and closed-loop effect.
Safety boundary: closed simulation ML defense decision-path audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| MDP01 | Pre-threshold guard discipline | pass | trace_count=61; first_threshold_time=80; pre_threshold_traces=16; pre_threshold_noop_count=15; pre_threshold_defense_events=4; pre_threshold_guard_traces=1; pre_threshold_guard_event_count=4; pre_threshold_ml_alerts=0; pre_threshold_max_probability=0.534851; threshold=0.75 | The ML defender remains reactive: below-threshold actions are limited to an explicit mission-pressure guard, while attack alerts still wait for detector confidence. |
| MDP02 | Threshold-to-window transition | pass | first_attack_time=60; first_threshold_time=80; first_response_latency_sec=20; first_probability=0.955265; threshold=0.75; opened_window=true; event_count=1; same_time_actions=ml_attack_alert | The detector threshold is wired to an actual defense-window transition, not only to an offline probability score. |
| MDP03 | Alert cooldown and window refresh | pass | threshold_traces=37; above_threshold_event_traces=17; above_threshold_no_event_refresh_traces=20; ml_attack_alerts=8; min_alert_gap_sec=25; all_alert_probabilities_above_threshold=true | No-op traces above threshold are not dead code; they represent cooldown-bounded window refresh decisions. |
| MDP04 | Core defense fanout | pass | defense_events=30; ml_attack_alert=8; priority_reroute=6; stale_badge=7; video_throttle=6; pace_switch=3 | The ML detector opens the gate; the defense agent still executes mission-aware TSRA-R actions inside that window. |
| MDP05 | Memory continuity | pass | memory_mismatches=0; threshold_window_nondecreasing=true; first_active_until=150; last_active_until=370 | The window is agent memory, not a stateless if-branch; trace feedback and memory stay aligned across the E7 run. |
| MDP06 | Closed-loop coordination effect | pass | e7_coordination_rows=5; ml_reactive_rows=1; max_ml_reactive_defense_latency_sec=10; min_ml_reactive_impact_reduction_from_peak=0.251649 | The ML decision path reaches closed-loop evidence: response latency is bounded and post-peak mission impact decreases. |

## Detail

### MDP01 Pre-threshold guard discipline

- Requirement: TSRA-R-ML should stay quiet below threshold except for trace-backed early mission-pressure guard actions, and it should not emit ML attack alerts before the detector threshold.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl
- Observed: trace_count=61; first_threshold_time=80; pre_threshold_traces=16; pre_threshold_noop_count=15; pre_threshold_defense_events=4; pre_threshold_guard_traces=1; pre_threshold_guard_event_count=4; pre_threshold_ml_alerts=0; pre_threshold_max_probability=0.534851; threshold=0.75
- Status: pass
- Interpretation: The ML defender remains reactive: below-threshold actions are limited to an explicit mission-pressure guard, while attack alerts still wait for detector confidence.
- Safety boundary: closed simulation ML defense decision-path audit only; no RF, exploit, or live network action

### MDP02 Threshold-to-window transition

- Requirement: The first above-threshold detector decision must open a defense window and emit a same-time ML alert.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl
- Observed: first_attack_time=60; first_threshold_time=80; first_response_latency_sec=20; first_probability=0.955265; threshold=0.75; opened_window=true; event_count=1; same_time_actions=ml_attack_alert
- Status: pass
- Interpretation: The detector threshold is wired to an actual defense-window transition, not only to an offline probability score.
- Safety boundary: closed simulation ML defense decision-path audit only; no RF, exploit, or live network action

### MDP03 Alert cooldown and window refresh

- Requirement: Repeated high-confidence decisions should refresh the window while limiting alert spam.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl
- Observed: threshold_traces=37; above_threshold_event_traces=17; above_threshold_no_event_refresh_traces=20; ml_attack_alerts=8; min_alert_gap_sec=25; all_alert_probabilities_above_threshold=true
- Status: pass
- Interpretation: No-op traces above threshold are not dead code; they represent cooldown-bounded window refresh decisions.
- Safety boundary: closed simulation ML defense decision-path audit only; no RF, exploit, or live network action

### MDP04 Core defense fanout

- Requirement: The ML-opened window must enable core TSRA-R actions beyond the alert itself.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl
- Observed: defense_events=30; ml_attack_alert=8; priority_reroute=6; stale_badge=7; video_throttle=6; pace_switch=3
- Status: pass
- Interpretation: The ML detector opens the gate; the defense agent still executes mission-aware TSRA-R actions inside that window.
- Safety boundary: closed simulation ML defense decision-path audit only; no RF, exploit, or live network action

### MDP05 Memory continuity

- Requirement: Active defense window memory should match trace feedback and extend monotonically on above-threshold decisions.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl
- Observed: memory_mismatches=0; threshold_window_nondecreasing=true; first_active_until=150; last_active_until=370
- Status: pass
- Interpretation: The window is agent memory, not a stateless if-branch; trace feedback and memory stay aligned across the E7 run.
- Safety boundary: closed simulation ML defense decision-path audit only; no RF, exploit, or live network action

### MDP06 Closed-loop coordination effect

- Requirement: At least one ML-reactive episode should connect the ML defense window to bounded response latency and positive post-peak reduction.
- Evidence: outputs/report_tables/agent_coordination_latency_audit.csv
- Observed: e7_coordination_rows=5; ml_reactive_rows=1; max_ml_reactive_defense_latency_sec=10; min_ml_reactive_impact_reduction_from_peak=0.251649
- Status: pass
- Interpretation: The ML decision path reaches closed-loop evidence: response latency is bounded and post-peak mission impact decreases.
- Safety boundary: closed simulation ML defense decision-path audit only; no RF, exploit, or live network action
