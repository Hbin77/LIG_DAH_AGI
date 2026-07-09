# Attack-Defense Coverage

This table maps each AURA attack capability to the TSRA-R defense capabilities that cover it.
It is derived from the agent capability matrix and metric gate summary.

Safety boundary: closed simulation coverage mapping only; no RF, exploit, or live network action

| attack_capability | covered_by_defense_capabilities | coverage_status | validation_gates | residual_risk |
|---|---|---|---|---|
| bandwidth_limit | priority_reroute, video_throttle, pace_switch | covered | G01:pass; G02:pass; G03:pass; G04:pass; G06:pass; G09:pass | Scalar mission impact can undervalue PACE switching and video throttling, so action ablation and gate metrics must be read with mission context. |
| failover_chasing | ml_attack_alert, pace_switch, adaptive_optional_action_gating | covered | G02:pass; G03:pass; G04:pass; G08:pass; G09:pass; G10:pass | The prototype models fallback behavior inside a simulator, not real PACE network control. |
| queue_pressure | priority_reroute, video_throttle, stale_badge | covered | G01:pass; G02:pass; G03:pass; G04:pass; G05:pass; G06:pass; G07:pass | Queue pressure can still create residual latency during the response window before defenses take effect. |
| stale_cop_induction | stale_badge | covered | G01:pass; G02:pass; G03:pass; G05:pass; G07:pass | Stale badge protects trust decisions but cannot recover missing sensor freshness by itself. |

## Detail

### bandwidth_limit

- Attack agents: AURA
- Attack evidence count: 3
- Attack observed effect: targets=SATCOM; max_expected_impact=1; avg_attack_score=0.9475
- Covered by defense capabilities: priority_reroute, video_throttle, pace_switch
- Defense agents: TSRA-R, TSRA-R-ML
- Defense evidence count: priority_reroute=11; video_throttle=14; pace_switch=6
- Coverage logic: AURA reduces link capacity; TSRA-R protects critical traffic first, throttles optional video load, and can shift traffic to a bounded PACE fallback.
- Coverage status: covered
- Validation gates: G01:pass; G02:pass; G03:pass; G04:pass; G06:pass; G09:pass
- Battle evidence: E5/E7 timeline shows attack events followed by defense events and metric snapshots.
- Residual risk: Scalar mission impact can undervalue PACE switching and video throttling, so action ablation and gate metrics must be read with mission context.
- Safety boundary: closed simulation coverage mapping only; no RF, exploit, or live network action

### failover_chasing

- Attack agents: AURA-ML
- Attack evidence count: 3
- Attack observed effect: targets=LTE,MESH; max_expected_impact=0.916793; avg_attack_score=0.777388
- Covered by defense capabilities: ml_attack_alert, pace_switch, adaptive_optional_action_gating
- Defense agents: TSRA-R-ML, TSRA-R, TSRA-R-ADAPTIVE
- Defense evidence count: ml_attack_alert=9; pace_switch=6; adaptive_optional_action_gating=30 seeds
- Coverage logic: AURA-ML follows the active fallback path; ML TSRA-R opens a reactive defense window, PACE switching bounds link degradation, and AdaptiveTSRA-R limits optional action overuse.
- Coverage status: covered
- Validation gates: G02:pass; G03:pass; G04:pass; G08:pass; G09:pass; G10:pass
- Battle evidence: E7 timeline and metric gate G10 keep ML defense behavior distinct from E6.
- Residual risk: The prototype models fallback behavior inside a simulator, not real PACE network control.
- Safety boundary: closed simulation coverage mapping only; no RF, exploit, or live network action

### queue_pressure

- Attack agents: AURA, AURA-ML
- Attack evidence count: 8
- Attack observed effect: targets=LTE,MESH,SATCOM; max_expected_impact=1; avg_attack_score=0.787551
- Covered by defense capabilities: priority_reroute, video_throttle, stale_badge
- Defense agents: TSRA-R, TSRA-R-ML
- Defense evidence count: priority_reroute=11; video_throttle=14; stale_badge=16
- Coverage logic: AURA increases non-critical queue occupancy; TSRA-R reroutes critical messages, reduces optional video pressure, and marks stale COP data so it is not trusted as fresh.
- Coverage status: covered
- Validation gates: G01:pass; G02:pass; G03:pass; G04:pass; G05:pass; G06:pass; G07:pass
- Battle evidence: E5/E7 battle timelines and incident summaries show queue pressure with defense response.
- Residual risk: Queue pressure can still create residual latency during the response window before defenses take effect.
- Safety boundary: closed simulation coverage mapping only; no RF, exploit, or live network action

### stale_cop_induction

- Attack agents: AURA
- Attack evidence count: 1
- Attack observed effect: targets=SATCOM; max_expected_impact=1; avg_attack_score=0.9175
- Covered by defense capabilities: stale_badge
- Defense agents: TSRA-R, TSRA-R-ML
- Defense evidence count: stale_badge=16
- Coverage logic: AURA degrades COP freshness; TSRA-R does not pretend stale data disappeared, but lowers trusted stale exposure by tagging stale COP observations.
- Coverage status: covered
- Validation gates: G01:pass; G02:pass; G03:pass; G05:pass; G07:pass
- Battle evidence: Incident summary tracks attack-anchored windows with stale exposure and defense response.
- Residual risk: Stale badge protects trust decisions but cannot recover missing sensor freshness by itself.
- Safety boundary: closed simulation coverage mapping only; no RF, exploit, or live network action
