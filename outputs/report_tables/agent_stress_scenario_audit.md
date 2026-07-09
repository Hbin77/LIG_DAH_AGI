# Agent Stress Scenario Audit

This audit runs closed-simulation stress fixtures and compares defended outcomes against attack-only outcomes.
Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 6
- Status counts: pass=6

| check_id | scenario_id | defender_variant | seed_count | resilience_gain_mean | resilience_gain_min | defended_mission_impact_mean | status |
|---|---|---|---:|---:|---:|---:|---|
| AS01 | stress_air_defense_queue_saturation | tsra_r_full | 5 | 0.842876 | 0.830982 | 0.124559 | pass |
| AS02 | stress_air_defense_queue_saturation | tsra_r_ml | 5 | 0.83369 | 0.823518 | 0.131583 | pass |
| AS03 | stress_stale_cop_latency_chain | tsra_r_full | 5 | 0.775357 | 0.710987 | 0.159802 | pass |
| AS04 | stress_stale_cop_latency_chain | tsra_r_ml | 5 | 0.754937 | 0.699806 | 0.174011 | pass |
| AS05 | stress_pace_failover_pressure | tsra_r_full | 5 | 0.837013 | 0.82273 | 0.142861 | pass |
| AS06 | stress_pace_failover_pressure | tsra_r_ml | 5 | 0.816883 | 0.784765 | 0.160554 | pass |

## Detail

### AS01 stress_air_defense_queue_saturation tsra_r_full

- Goal: Stress air-defense watch with SATCOM queue pressure and video saturation.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-001:queue_pressure@SATCOM/t=85-205/bw=1.1/lat+=900/loss+=0.04/queue_pressure
- Attack-only mission impact mean: 0.794883
- Defended mission impact mean: 0.124559
- Defended mission impact std: 0.00621489
- Defended mission impact max: 0.132677
- Mission impact reduction mean: 0.670324
- Resilience gain mean: 0.842876
- Resilience gain min: 0.830982
- Resilience gain std: 0.00838024
- P95 reduction sec mean: 94.86
- Trusted stale reduction mean: 0.175
- Priority inversion reduction mean: 0.786327
- Defense count mean: 21.2
- Mission guard trigger count mean: 0
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_full preserved aggregate stress resilience in stress_air_defense_queue_saturation across 5 seeds: gain_mean=0.842876, gain_min=0.830982, defended_impact_mean=0.124559, p95_reduction_sec_mean=94.86, trusted_stale_reduction_mean=0.175, priority_inversion_reduction_mean=0.786327.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS02 stress_air_defense_queue_saturation tsra_r_ml

- Goal: Stress air-defense watch with SATCOM queue pressure and video saturation.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-001:queue_pressure@SATCOM/t=85-205/bw=1.1/lat+=900/loss+=0.04/queue_pressure
- Attack-only mission impact mean: 0.794883
- Defended mission impact mean: 0.131583
- Defended mission impact std: 0.0032283
- Defended mission impact max: 0.135155
- Mission impact reduction mean: 0.663301
- Resilience gain mean: 0.83369
- Resilience gain min: 0.823518
- Resilience gain std: 0.0113236
- P95 reduction sec mean: 94.86
- Trusted stale reduction mean: 0.175
- Priority inversion reduction mean: 0.772281
- Defense count mean: 25.2
- Mission guard trigger count mean: 1
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_ml preserved aggregate stress resilience in stress_air_defense_queue_saturation across 5 seeds: gain_mean=0.83369, gain_min=0.823518, defended_impact_mean=0.131583, p95_reduction_sec_mean=94.86, trusted_stale_reduction_mean=0.175, priority_inversion_reduction_mean=0.772281, mission_guard_trigger_count_mean=1, mission_guard_event_trace_count_mean=0.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS03 stress_stale_cop_latency_chain tsra_r_full

- Goal: Stress COP freshness and critical-window latency across two mission phases.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-101:stale_cop_induction@SATCOM/t=70-165/bw=1.2/lat+=1000/loss+=0.06/no_queue_pressure; stress-atk-102:critical_window_degradation@SATCOM/t=185-260/bw=1.4/lat+=700/loss+=0.03/no_queue_pressure
- Attack-only mission impact mean: 0.711933
- Defended mission impact mean: 0.159802
- Defended mission impact std: 0.0283668
- Defended mission impact max: 0.196281
- Mission impact reduction mean: 0.552131
- Resilience gain mean: 0.775357
- Resilience gain min: 0.710987
- Resilience gain std: 0.0381901
- P95 reduction sec mean: 33.94
- Trusted stale reduction mean: 0.375
- Priority inversion reduction mean: 0.552567
- Defense count mean: 14.8
- Mission guard trigger count mean: 0
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_full preserved aggregate stress resilience in stress_stale_cop_latency_chain across 5 seeds: gain_mean=0.775357, gain_min=0.710987, defended_impact_mean=0.159802, p95_reduction_sec_mean=33.94, trusted_stale_reduction_mean=0.375, priority_inversion_reduction_mean=0.552567.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS04 stress_stale_cop_latency_chain tsra_r_ml

- Goal: Stress COP freshness and critical-window latency across two mission phases.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-101:stale_cop_induction@SATCOM/t=70-165/bw=1.2/lat+=1000/loss+=0.06/no_queue_pressure; stress-atk-102:critical_window_degradation@SATCOM/t=185-260/bw=1.4/lat+=700/loss+=0.03/no_queue_pressure
- Attack-only mission impact mean: 0.711933
- Defended mission impact mean: 0.174011
- Defended mission impact std: 0.0212417
- Defended mission impact max: 0.196281
- Mission impact reduction mean: 0.537922
- Resilience gain mean: 0.754937
- Resilience gain min: 0.699806
- Resilience gain std: 0.0306495
- P95 reduction sec mean: 33.81
- Trusted stale reduction mean: 0.375
- Priority inversion reduction mean: 0.525881
- Defense count mean: 15.6
- Mission guard trigger count mean: 3.2
- Mission guard event trace count mean: 1
- Status: pass
- Interpretation: tsra_r_ml preserved aggregate stress resilience in stress_stale_cop_latency_chain across 5 seeds: gain_mean=0.754937, gain_min=0.699806, defended_impact_mean=0.174011, p95_reduction_sec_mean=33.81, trusted_stale_reduction_mean=0.375, priority_inversion_reduction_mean=0.525881, mission_guard_trigger_count_mean=3.2, mission_guard_event_trace_count_mean=1.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS05 stress_pace_failover_pressure tsra_r_full

- Goal: Stress PACE switching under SATCOM pressure followed by LTE pressure.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-201:failover_chasing@SATCOM/t=90-170/bw=1.1/lat+=800/loss+=0.04/queue_pressure; stress-atk-202:failover_chasing@LTE/t=165-250/bw=0.9/lat+=500/loss+=0.05/queue_pressure
- Attack-only mission impact mean: 0.876433
- Defended mission impact mean: 0.142861
- Defended mission impact std: 0.00859267
- Defended mission impact max: 0.156737
- Mission impact reduction mean: 0.733572
- Resilience gain mean: 0.837013
- Resilience gain min: 0.82273
- Resilience gain std: 0.00936838
- P95 reduction sec mean: 63.3
- Trusted stale reduction mean: 0.375
- Priority inversion reduction mean: 0.547437
- Defense count mean: 24.4
- Mission guard trigger count mean: 0
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_full preserved aggregate stress resilience in stress_pace_failover_pressure across 5 seeds: gain_mean=0.837013, gain_min=0.82273, defended_impact_mean=0.142861, p95_reduction_sec_mean=63.3, trusted_stale_reduction_mean=0.375, priority_inversion_reduction_mean=0.547437.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS06 stress_pace_failover_pressure tsra_r_ml

- Goal: Stress PACE switching under SATCOM pressure followed by LTE pressure.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-201:failover_chasing@SATCOM/t=90-170/bw=1.1/lat+=800/loss+=0.04/queue_pressure; stress-atk-202:failover_chasing@LTE/t=165-250/bw=0.9/lat+=500/loss+=0.05/queue_pressure
- Attack-only mission impact mean: 0.876433
- Defended mission impact mean: 0.160554
- Defended mission impact std: 0.0156672
- Defended mission impact max: 0.190303
- Mission impact reduction mean: 0.715879
- Resilience gain mean: 0.816883
- Resilience gain min: 0.784765
- Resilience gain std: 0.0169224
- P95 reduction sec mean: 63.09
- Trusted stale reduction mean: 0.3625
- Priority inversion reduction mean: 0.528601
- Defense count mean: 30.2
- Mission guard trigger count mean: 0
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_ml preserved aggregate stress resilience in stress_pace_failover_pressure across 5 seeds: gain_mean=0.816883, gain_min=0.784765, defended_impact_mean=0.160554, p95_reduction_sec_mean=63.09, trusted_stale_reduction_mean=0.3625, priority_inversion_reduction_mean=0.528601, mission_guard_trigger_count_mean=0, mission_guard_event_trace_count_mean=0.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action
