# Agent Stress Scenario Audit

This audit runs closed-simulation stress fixtures and compares defended outcomes against attack-only outcomes.
Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 6
- Status counts: pass=6

| check_id | scenario_id | defender_variant | seed_count | resilience_gain_mean | resilience_gain_min | defended_mission_impact_mean | status |
|---|---|---|---:|---:|---:|---:|---|
| AS01 | stress_air_defense_queue_saturation | tsra_r_full | 5 | 0.860771 | 0.854467 | 0.110857 | pass |
| AS02 | stress_air_defense_queue_saturation | tsra_r_ml | 5 | 0.843127 | 0.823947 | 0.124346 | pass |
| AS03 | stress_stale_cop_latency_chain | tsra_r_full | 5 | 0.772049 | 0.710987 | 0.162079 | pass |
| AS04 | stress_stale_cop_latency_chain | tsra_r_ml | 5 | 0.754937 | 0.699806 | 0.174011 | pass |
| AS05 | stress_pace_failover_pressure | tsra_r_full | 5 | 0.841155 | 0.80432 | 0.13917 | pass |
| AS06 | stress_pace_failover_pressure | tsra_r_ml | 5 | 0.843971 | 0.835152 | 0.136755 | pass |

## Detail

### AS01 stress_air_defense_queue_saturation tsra_r_full

- Goal: Stress air-defense watch with SATCOM queue pressure and video saturation.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-001:queue_pressure@SATCOM/t=85-205/bw=1.1/lat+=900/loss+=0.04/queue_pressure
- Attack-only mission impact mean: 0.794883
- Defended mission impact mean: 0.110857
- Defended mission impact std: 0.0115946
- Defended mission impact max: 0.132677
- Mission impact reduction mean: 0.684026
- Resilience gain mean: 0.860771
- Resilience gain min: 0.854467
- Resilience gain std: 0.00593979
- P95 reduction sec mean: 94.86
- Trusted stale reduction mean: 0.175
- Priority inversion reduction mean: 0.787065
- Defense count mean: 20.4
- Mission guard trigger count mean: 0
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_full preserved aggregate stress resilience in stress_air_defense_queue_saturation across 5 seeds: gain_mean=0.860771, gain_min=0.854467, defended_impact_mean=0.110857, p95_reduction_sec_mean=94.86, trusted_stale_reduction_mean=0.175, priority_inversion_reduction_mean=0.787065.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS02 stress_air_defense_queue_saturation tsra_r_ml

- Goal: Stress air-defense watch with SATCOM queue pressure and video saturation.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-001:queue_pressure@SATCOM/t=85-205/bw=1.1/lat+=900/loss+=0.04/queue_pressure
- Attack-only mission impact mean: 0.794883
- Defended mission impact mean: 0.124346
- Defended mission impact std: 0.0097641
- Defended mission impact max: 0.13416
- Mission impact reduction mean: 0.670537
- Resilience gain mean: 0.843127
- Resilience gain min: 0.823947
- Resilience gain std: 0.0131523
- P95 reduction sec mean: 94.86
- Trusted stale reduction mean: 0.175
- Priority inversion reduction mean: 0.773421
- Defense count mean: 24.8
- Mission guard trigger count mean: 1
- Mission guard event trace count mean: 0.2
- Status: pass
- Interpretation: tsra_r_ml preserved aggregate stress resilience in stress_air_defense_queue_saturation across 5 seeds: gain_mean=0.843127, gain_min=0.823947, defended_impact_mean=0.124346, p95_reduction_sec_mean=94.86, trusted_stale_reduction_mean=0.175, priority_inversion_reduction_mean=0.773421, mission_guard_trigger_count_mean=1, mission_guard_event_trace_count_mean=0.2.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS03 stress_stale_cop_latency_chain tsra_r_full

- Goal: Stress COP freshness and critical-window latency across two mission phases.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-101:stale_cop_induction@SATCOM/t=70-165/bw=1.2/lat+=1000/loss+=0.06/no_queue_pressure; stress-atk-102:critical_window_degradation@SATCOM/t=185-260/bw=1.4/lat+=700/loss+=0.03/no_queue_pressure
- Attack-only mission impact mean: 0.711933
- Defended mission impact mean: 0.162079
- Defended mission impact std: 0.0259974
- Defended mission impact max: 0.196281
- Mission impact reduction mean: 0.549854
- Resilience gain mean: 0.772049
- Resilience gain min: 0.710987
- Resilience gain std: 0.0351617
- P95 reduction sec mean: 33.74
- Trusted stale reduction mean: 0.375
- Priority inversion reduction mean: 0.550678
- Defense count mean: 15
- Mission guard trigger count mean: 0
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_full preserved aggregate stress resilience in stress_stale_cop_latency_chain across 5 seeds: gain_mean=0.772049, gain_min=0.710987, defended_impact_mean=0.162079, p95_reduction_sec_mean=33.74, trusted_stale_reduction_mean=0.375, priority_inversion_reduction_mean=0.550678.
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
- Defended mission impact mean: 0.13917
- Defended mission impact std: 0.0224409
- Defended mission impact max: 0.173014
- Mission impact reduction mean: 0.737263
- Resilience gain mean: 0.841155
- Resilience gain min: 0.80432
- Resilience gain std: 0.0258325
- P95 reduction sec mean: 63.32
- Trusted stale reduction mean: 0.35
- Priority inversion reduction mean: 0.548719
- Defense count mean: 22.4
- Mission guard trigger count mean: 0
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_full preserved aggregate stress resilience in stress_pace_failover_pressure across 5 seeds: gain_mean=0.841155, gain_min=0.80432, defended_impact_mean=0.13917, p95_reduction_sec_mean=63.32, trusted_stale_reduction_mean=0.35, priority_inversion_reduction_mean=0.548719.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action

### AS06 stress_pace_failover_pressure tsra_r_ml

- Goal: Stress PACE switching under SATCOM pressure followed by LTE pressure.
- Seed count: 5 (2607-2611)
- Attack profile: stress-atk-201:failover_chasing@SATCOM/t=90-170/bw=1.1/lat+=800/loss+=0.04/queue_pressure; stress-atk-202:failover_chasing@LTE/t=165-250/bw=0.9/lat+=500/loss+=0.05/queue_pressure
- Attack-only mission impact mean: 0.876433
- Defended mission impact mean: 0.136755
- Defended mission impact std: 0.00495601
- Defended mission impact max: 0.145204
- Mission impact reduction mean: 0.739679
- Resilience gain mean: 0.843971
- Resilience gain min: 0.835152
- Resilience gain std: 0.00526448
- P95 reduction sec mean: 63.09
- Trusted stale reduction mean: 0.375
- Priority inversion reduction mean: 0.529117
- Defense count mean: 27.8
- Mission guard trigger count mean: 0
- Mission guard event trace count mean: 0
- Status: pass
- Interpretation: tsra_r_ml preserved aggregate stress resilience in stress_pace_failover_pressure across 5 seeds: gain_mean=0.843971, gain_min=0.835152, defended_impact_mean=0.136755, p95_reduction_sec_mean=63.09, trusted_stale_reduction_mean=0.375, priority_inversion_reduction_mean=0.529117, mission_guard_trigger_count_mean=0, mission_guard_event_trace_count_mean=0.
- Safety boundary: closed simulation stress-scenario audit only; no RF, exploit, or live network action
