# PACE Transition Audit

This audit explains why each TSRA-R PACE transition happened and what attack context surrounded it.

Context window: 40 seconds
Safety boundary: closed simulation PACE audit only; no RF, exploit, or live network action

| experiment | pace_event_id | time_sec | from_link_inferred | target_link | reason | audit_status | recovery_instability_at_switch |
|---|---|---:|---|---|---|---|---:|
| E5_rule_aura_tsra_r | def-00005 | 75 | SATCOM | LTE | SATCOM degraded beyond mission threshold | satcom_to_fallback | 1 |
| E7_ml_aura_ml_tsra_r | def-00003 | 70 | SATCOM | LTE | SATCOM degraded beyond mission threshold | satcom_to_fallback | 1 |
| E7_ml_aura_ml_tsra_r | def-00013 | 150 | LTE | MESH | fallback link degraded beyond mission threshold | fallback_reselect | 2 |
| E7_ml_aura_ml_tsra_r | def-00025 | 260 | MESH | LTE | fallback link degraded beyond mission threshold | fallback_reselect | 3 |

## Detail

### E5_rule_aura_tsra_r def-00005

- Time: 75
- Inferred transition: SATCOM -> LTE
- Reason: SATCOM degraded beyond mission threshold
- Move critical traffic: true
- Active attacks at switch: atk-00001:queue_pressure@60->SATCOM
- Near future attacks: atk-00002:queue_pressure@110->LTE
- Mission impact at switch: 0.170642
- P95 critical latency at switch: 2.3
- Trusted stale exposure at switch: 0.125
- Priority inversion at switch: 0.139785
- Recovery instability at switch: 1
- Audit status: satcom_to_fallback
- Residual risk: initial PACE switch protects SATCOM degradation but may expose fallback links to later chasing
- Safety boundary: closed simulation PACE audit only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r def-00003

- Time: 70
- Inferred transition: SATCOM -> LTE
- Reason: SATCOM degraded beyond mission threshold
- Move critical traffic: true
- Active attacks at switch: ml-atk-00001:queue_pressure@60->SATCOM
- Near future attacks: ml-atk-00002:failover_chasing@110->LTE
- Mission impact at switch: 0.209367
- P95 critical latency at switch: 1
- Trusted stale exposure at switch: 0.125
- Priority inversion at switch: 0.234568
- Recovery instability at switch: 1
- Audit status: satcom_to_fallback
- Residual risk: initial PACE switch protects SATCOM degradation but may expose fallback links to later chasing
- Safety boundary: closed simulation PACE audit only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r def-00013

- Time: 150
- Inferred transition: LTE -> MESH
- Reason: fallback link degraded beyond mission threshold
- Move critical traffic: true
- Active attacks at switch: ml-atk-00002:failover_chasing@110->LTE
- Near future attacks: ml-atk-00003:failover_chasing@160->MESH
- Mission impact at switch: 0.10647
- P95 critical latency at switch: 1
- Trusted stale exposure at switch: 0.0625
- Priority inversion at switch: 0.0641892
- Recovery instability at switch: 2
- Audit status: fallback_reselect
- Residual risk: fallback reselection closes the immediate failover-chasing gap but can increase recovery_instability through extra PACE transitions
- Safety boundary: closed simulation PACE audit only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r def-00025

- Time: 260
- Inferred transition: MESH -> LTE
- Reason: fallback link degraded beyond mission threshold
- Move critical traffic: true
- Active attacks at switch: ml-atk-00004:queue_pressure@210->MESH; ml-atk-00005:stale_cop_induction@260->MESH
- Near future attacks: none
- Mission impact at switch: 0.114642
- P95 critical latency at switch: 2
- Trusted stale exposure at switch: 0.0625
- Priority inversion at switch: 0.0338681
- Recovery instability at switch: 3
- Audit status: fallback_reselect
- Residual risk: fallback reselection closes the immediate failover-chasing gap but can increase recovery_instability through extra PACE transitions
- Safety boundary: closed simulation PACE audit only; no RF, exploit, or live network action
