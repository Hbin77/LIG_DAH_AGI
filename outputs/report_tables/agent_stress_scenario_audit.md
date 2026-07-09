# Agent Stress Scenario Audit

This audit runs closed-simulation stress fixtures and compares defended outcomes against attack-only outcomes.
Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 6
- Status counts: pass=6

| check_id | scenario_id | defender_variant | resilience_gain | defended_mission_impact | status |
|---|---|---|---:|---:|---|
| AS01 | stress_air_defense_queue_saturation | tsra_r_full | 0.854467 | 0.132677 | pass |
| AS02 | stress_air_defense_queue_saturation | tsra_r_ml | 0.854467 | 0.132677 | pass |
| AS03 | stress_stale_cop_latency_chain | tsra_r_full | 0.757678 | 0.196281 | pass |
| AS04 | stress_stale_cop_latency_chain | tsra_r_ml | 0.738553 | 0.211772 | pass |
| AS05 | stress_pace_failover_pressure | tsra_r_full | 0.82273 | 0.156737 | pass |
| AS06 | stress_pace_failover_pressure | tsra_r_ml | 0.784765 | 0.190303 | pass |

## Detail

### AS01 stress_air_defense_queue_saturation tsra_r_full

- Goal: Stress air-defense watch with SATCOM queue pressure and video saturation.
- Attack profile: stress-atk-001:queue_pressure@SATCOM/t=85-205/bw=1.1/lat+=900/loss+=0.04/queue_pressure
- Attack-only mission impact: 0.911667
- Defended mission impact: 0.132677
- Mission impact reduction: 0.778989
- Resilience gain: 0.854467
- P95 reduction sec: 103
- Trusted stale reduction: 0.375
- Priority inversion reduction: 0.756974
- Defense count: 21
- Status: pass
- Interpretation: tsra_r_full preserved stress resilience in stress_air_defense_queue_saturation: gain=0.854467, defended_impact=0.132677, p95_reduction_sec=103, trusted_stale_reduction=0.375, priority_inversion_reduction=0.756974.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS02 stress_air_defense_queue_saturation tsra_r_ml

- Goal: Stress air-defense watch with SATCOM queue pressure and video saturation.
- Attack profile: stress-atk-001:queue_pressure@SATCOM/t=85-205/bw=1.1/lat+=900/loss+=0.04/queue_pressure
- Attack-only mission impact: 0.911667
- Defended mission impact: 0.132677
- Mission impact reduction: 0.778989
- Resilience gain: 0.854467
- P95 reduction sec: 103
- Trusted stale reduction: 0.375
- Priority inversion reduction: 0.756974
- Defense count: 26
- Status: pass
- Interpretation: tsra_r_ml preserved stress resilience in stress_air_defense_queue_saturation: gain=0.854467, defended_impact=0.132677, p95_reduction_sec=103, trusted_stale_reduction=0.375, priority_inversion_reduction=0.756974.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS03 stress_stale_cop_latency_chain tsra_r_full

- Goal: Stress COP freshness and critical-window latency across two mission phases.
- Attack profile: stress-atk-101:stale_cop_induction@SATCOM/t=70-165/bw=1.2/lat+=1000/loss+=0.06/no_queue_pressure; stress-atk-102:critical_window_degradation@SATCOM/t=185-260/bw=1.4/lat+=700/loss+=0.03/no_queue_pressure
- Attack-only mission impact: 0.81
- Defended mission impact: 0.196281
- Mission impact reduction: 0.613719
- Resilience gain: 0.757678
- P95 reduction sec: 48.25
- Trusted stale reduction: 0.375
- Priority inversion reduction: 0.481463
- Defense count: 14
- Status: pass
- Interpretation: tsra_r_full preserved stress resilience in stress_stale_cop_latency_chain: gain=0.757678, defended_impact=0.196281, p95_reduction_sec=48.25, trusted_stale_reduction=0.375, priority_inversion_reduction=0.481463.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS04 stress_stale_cop_latency_chain tsra_r_ml

- Goal: Stress COP freshness and critical-window latency across two mission phases.
- Attack profile: stress-atk-101:stale_cop_induction@SATCOM/t=70-165/bw=1.2/lat+=1000/loss+=0.06/no_queue_pressure; stress-atk-102:critical_window_degradation@SATCOM/t=185-260/bw=1.4/lat+=700/loss+=0.03/no_queue_pressure
- Attack-only mission impact: 0.81
- Defended mission impact: 0.211772
- Mission impact reduction: 0.598228
- Resilience gain: 0.738553
- P95 reduction sec: 48.25
- Trusted stale reduction: 0.375
- Priority inversion reduction: 0.450481
- Defense count: 13
- Status: pass
- Interpretation: tsra_r_ml preserved stress resilience in stress_stale_cop_latency_chain: gain=0.738553, defended_impact=0.211772, p95_reduction_sec=48.25, trusted_stale_reduction=0.375, priority_inversion_reduction=0.450481.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS05 stress_pace_failover_pressure tsra_r_full

- Goal: Stress PACE switching under SATCOM pressure followed by LTE pressure.
- Attack profile: stress-atk-201:failover_chasing@SATCOM/t=90-170/bw=1.1/lat+=800/loss+=0.04/queue_pressure; stress-atk-202:failover_chasing@LTE/t=165-250/bw=0.9/lat+=500/loss+=0.05/queue_pressure
- Attack-only mission impact: 0.884167
- Defended mission impact: 0.156737
- Mission impact reduction: 0.72743
- Resilience gain: 0.82273
- P95 reduction sec: 69
- Trusted stale reduction: 0.375
- Priority inversion reduction: 0.541726
- Defense count: 24
- Status: pass
- Interpretation: tsra_r_full preserved stress resilience in stress_pace_failover_pressure: gain=0.82273, defended_impact=0.156737, p95_reduction_sec=69, trusted_stale_reduction=0.375, priority_inversion_reduction=0.541726.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS06 stress_pace_failover_pressure tsra_r_ml

- Goal: Stress PACE switching under SATCOM pressure followed by LTE pressure.
- Attack profile: stress-atk-201:failover_chasing@SATCOM/t=90-170/bw=1.1/lat+=800/loss+=0.04/queue_pressure; stress-atk-202:failover_chasing@LTE/t=165-250/bw=0.9/lat+=500/loss+=0.05/queue_pressure
- Attack-only mission impact: 0.884167
- Defended mission impact: 0.190303
- Mission impact reduction: 0.693863
- Resilience gain: 0.784765
- P95 reduction sec: 69
- Trusted stale reduction: 0.3125
- Priority inversion reduction: 0.543343
- Defense count: 29
- Status: pass
- Interpretation: tsra_r_ml preserved stress resilience in stress_pace_failover_pressure: gain=0.784765, defended_impact=0.190303, p95_reduction_sec=69, trusted_stale_reduction=0.3125, priority_inversion_reduction=0.543343.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action
