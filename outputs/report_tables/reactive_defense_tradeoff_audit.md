# Reactive Defense Tradeoff Audit

This audit explains what E7 gains and pays for by using ML-triggered reactive defense instead of E6 always-on rule defense.
Safety boundary: closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| RDT01 | Policy separation | pass | e6_policies=rule_defense_full; e7_policies=ml_anomaly_detector; e6_trace_count=61; e7_trace_count=61 | E6 is the always-on full rule defender; E7 is the ML anomaly detector that opens or refreshes reactive defense windows. |
| RDT02 | Pre-attack defense suppression | pass | first_attack_sec=60; e6_pre_first_defense_events=2; e7_pre_first_defense_events=0 | E7 removes the pre-attack stale-badge behavior seen in E6. This is a reactive-defense benefit, separate from mission-impact minimization. |
| RDT03 | First-response latency cost | pass | e6_first_core_response_latency_sec=5; e7_first_ml_alert_latency_sec=20 | E7 waits for detector confidence before opening the defense window; the measured cost in the representative run is a 20 second first-alert delay. |
| RDT04 | ML alert attack overlap | pass | ml_attack_alerts=9; active_attack_overlap=9; avg_alert_probability=0.951163; threshold=0.75 | Every E7 ML alert overlaps an active simulated attack window, so the alert stream is tied to attack context rather than arbitrary noise. |
| RDT05 | Core defense preservation | pass | e6_core_defense_events=24; e7_core_defense_events=24; e7_actions=ml_attack_alert:9,pace_switch:3,priority_reroute:6,stale_badge:8,video_throttle:7 | E7 adds ML alerting without dropping the core response vocabulary: PACE, priority reroute, stale badge, and video throttle remain present. |
| RDT06 | Bounded impact tradeoff | pass | e6_mission_impact_mean=0.14924; e7_mission_impact_mean=0.165471; e7_minus_e6=0.0162307; e6_std=0.012923; e7_std=0.0119458 | E7 is not sold as lower-impact than E6. Its observed cost is bounded while remaining stable across repeated seeds. |
| RDT07 | Detector threshold evidence | pass | trace_count=61; probability_count=61; threshold=0.75; below_threshold=16; above_threshold=45; opened_window=45; no_op=38; min_probability=0.229467; max_probability=0.97963 | The ML defender is not always-on: traces include no-op decisions below threshold and defense-window openings above threshold. |

## Detail

### RDT01 Policy separation

- Requirement: E6 and E7 must represent different defense policies, not the same rule path.
- Evidence: outputs/experiments/E6_ml_aura_tsra_r/tsra_r_decision_traces.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl
- Observed: e6_policies=rule_defense_full; e7_policies=ml_anomaly_detector; e6_trace_count=61; e7_trace_count=61
- Status: pass
- Interpretation: E6 is the always-on full rule defender; E7 is the ML anomaly detector that opens or refreshes reactive defense windows.
- Safety boundary: closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action

### RDT02 Pre-attack defense suppression

- Requirement: Reactive ML defense should avoid emitting defense events before the first observed AURA-ML attack.
- Evidence: outputs/experiments/E6_ml_aura_tsra_r/defense_events.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl
- Observed: first_attack_sec=60; e6_pre_first_defense_events=2; e7_pre_first_defense_events=0
- Status: pass
- Interpretation: E7 removes the pre-attack stale-badge behavior seen in E6. This is a reactive-defense benefit, separate from mission-impact minimization.
- Safety boundary: closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action

### RDT03 First-response latency cost

- Requirement: Reactive gating must expose its first-response delay instead of hiding it.
- Evidence: outputs/experiments/E6_ml_aura_tsra_r/defense_events.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl
- Observed: e6_first_core_response_latency_sec=5; e7_first_ml_alert_latency_sec=20
- Status: pass
- Interpretation: E7 waits for detector confidence before opening the defense window; the measured cost in the representative run is a 20 second first-alert delay.
- Safety boundary: closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action

### RDT04 ML alert attack overlap

- Requirement: ML alerts should occur during active simulated AURA-ML attack windows.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl
- Observed: ml_attack_alerts=9; active_attack_overlap=9; avg_alert_probability=0.951163; threshold=0.75
- Status: pass
- Interpretation: Every E7 ML alert overlaps an active simulated attack window, so the alert stream is tied to attack context rather than arbitrary noise.
- Safety boundary: closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action

### RDT05 Core defense preservation

- Requirement: Reactive ML TSRA-R must still emit the core TSRA-R actions after detection.
- Evidence: outputs/experiments/E6_ml_aura_tsra_r/defense_events.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl
- Observed: e6_core_defense_events=24; e7_core_defense_events=24; e7_actions=ml_attack_alert:9,pace_switch:3,priority_reroute:6,stale_badge:8,video_throttle:7
- Status: pass
- Interpretation: E7 adds ML alerting without dropping the core response vocabulary: PACE, priority reroute, stale badge, and video throttle remain present.
- Safety boundary: closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action

### RDT06 Bounded impact tradeoff

- Requirement: Reactive defense may cost mission-impact containment versus always-on rule defense, but the cost must stay bounded.
- Evidence: outputs/batch/repeated_experiment_summary.csv
- Observed: e6_mission_impact_mean=0.14924; e7_mission_impact_mean=0.165471; e7_minus_e6=0.0162307; e6_std=0.012923; e7_std=0.0119458
- Status: pass
- Interpretation: E7 is not sold as lower-impact than E6. Its observed cost is bounded while remaining stable across repeated seeds.
- Safety boundary: closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action

### RDT07 Detector threshold evidence

- Requirement: E7 traces must show both below-threshold no-op behavior and above-threshold reactive windows.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl
- Observed: trace_count=61; probability_count=61; threshold=0.75; below_threshold=16; above_threshold=45; opened_window=45; no_op=38; min_probability=0.229467; max_probability=0.97963
- Status: pass
- Interpretation: The ML defender is not always-on: traces include no-op decisions below threshold and defense-window openings above threshold.
- Safety boundary: closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action
