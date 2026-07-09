# Agent Memory Influence Audit

This audit checks whether AgentMemory influences bounded agent decisions instead of acting only as passive trace storage.
Safety boundary: closed simulation memory-influence audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 6
- Status counts: pass=6

## Audit Table

| check_id | area | observed | influence_status |
| --- | --- | --- | --- |
| MI01 | AURA cadence memory | traces=93; selected_attacks=15; cooldown_noops=48; max_event_noops=12; belief_rows=75 | pass |
| MI02 | AURA-ML cadence memory | traces=62; selected_attacks=10; cooldown_noops=32; max_event_noops=8; belief_rows=50 | pass |
| MI03 | TSRA-R action cooldown memory | eligible_not_ready=pace_switch=4, priority_reroute=21, stale_badge=86, video_throttle=123; eligible_ready=pace_switch=4, priority_reroute=19, stale_badge=26, video_throttle=21; emitted_events=pace_switch=4, priority_reroute=19, stale_badge=26, video_throttle=21 | pass |
| MI04 | TSRA-R-ML active defense window memory | opened_windows=38; active_window_traces=47; active_window_noops=27; below_threshold_no_window=14 | pass |
| MI05 | Adaptive TSRA-R memory policy | delta_mission_impact_mean=-0.0307717; delta_defense_count_mean=-3.93333; delta_video_throttle_count_mean=-3.26667; delta_pace_switch_count_mean=-1.06667 | pass |
| MI06 | Memory chain integrity | rows=9.0; pass_rows=9.0; min_last_selected_chain_match_rate=1 | pass |

## Detail

### MI01 AURA cadence memory

- Mechanism: AURA stores attack cadence and event budget state, then uses cooldown and max-event gates before selecting another simulated attack effect.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl
- Observed: traces=93; selected_attacks=15; cooldown_noops=48; max_event_noops=12; belief_rows=75
- Status: pass
- Interpretation: Rule AURA is not stateless; prior attack timing and event budget suppress later actions.

### MI02 AURA-ML cadence memory

- Mechanism: AURA-ML uses the same cadence memory gates while ranking candidates with the learned impact predictor.
- Evidence: outputs/experiments/*/aura_decision_traces.jsonl
- Observed: traces=62; selected_attacks=10; cooldown_noops=32; max_event_noops=8; belief_rows=50
- Status: pass
- Interpretation: ML ranking is bounded by memory-backed cadence and event-budget controls.

### MI03 TSRA-R action cooldown memory

- Mechanism: TSRA-R stores action cooldowns in memory and blocks eligible actions until their cooldowns are ready.
- Evidence: outputs/experiments/*/tsra_r_decision_traces.jsonl
- Observed: eligible_not_ready=pace_switch=4, priority_reroute=21, stale_badge=86, video_throttle=123; eligible_ready=pace_switch=4, priority_reroute=19, stale_badge=26, video_throttle=21; emitted_events=pace_switch=4, priority_reroute=19, stale_badge=26, video_throttle=21
- Status: pass
- Interpretation: Rule TSRA-R memory directly gates repeated defensive actions instead of emitting every eligible action every tick.

### MI04 TSRA-R-ML active defense window memory

- Mechanism: TSRA-R-ML stores active_defense_until and last probability so a detector hit opens or maintains a bounded defense window.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl
- Observed: opened_windows=38; active_window_traces=47; active_window_noops=27; below_threshold_no_window=14
- Status: pass
- Interpretation: The ML defender uses memory to maintain a reactive window and to avoid unnecessary action when probability is below threshold outside the window.

### MI05 Adaptive TSRA-R memory policy

- Mechanism: Adaptive TSRA-R uses recent memory windows to gate optional defenses and is compared against full TSRA-R over the repeated adaptive-memory experiment.
- Evidence: outputs/batch/adaptive_memory_summary.csv
- Observed: delta_mission_impact_mean=-0.0307717; delta_defense_count_mean=-3.93333; delta_video_throttle_count_mean=-3.26667; delta_pace_switch_count_mean=-1.06667
- Status: pass
- Interpretation: Memory gating reduces average mission impact while also reducing optional defense load.

### MI06 Memory chain integrity

- Mechanism: AgentMemory carries the previous selected action into the next DecisionTrace memory summary.
- Evidence: outputs/report_tables/agent_memory_belief_audit.csv
- Observed: rows=9.0; pass_rows=9.0; min_last_selected_chain_match_rate=1
- Status: pass
- Interpretation: The runtime memory chain is complete before higher-level memory influence claims are made.
