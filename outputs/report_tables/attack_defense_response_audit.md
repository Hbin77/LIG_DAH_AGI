# Attack-Defense Response Audit

This audit checks whether defended AURA attack events have active or timely TSRA-R responses.

Response window: 40 seconds
Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

| experiment | attack_event_id | attack_capability | response_status | first_required_response_latency_sec | missing_required_defenses | missing_support_defenses |
|---|---|---|---|---:|---|---|
| E5_rule_aura_tsra_r | atk-00001 | queue_pressure | complete | 0 | none | none |
| E5_rule_aura_tsra_r | atk-00002 | queue_pressure | complete | 0 | none | none |
| E5_rule_aura_tsra_r | atk-00003 | queue_pressure | complete | 0 | none | none |
| E5_rule_aura_tsra_r | atk-00004 | queue_pressure | complete | 0 | none | none |
| E5_rule_aura_tsra_r | atk-00005 | queue_pressure | complete | 0 | none | none |
| E7_ml_aura_ml_tsra_r | ml-atk-00001 | queue_pressure | complete | 10 | none | none |
| E7_ml_aura_ml_tsra_r | ml-atk-00002 | failover_chasing | complete | 0 | none | none |
| E7_ml_aura_ml_tsra_r | ml-atk-00003 | failover_chasing | complete | 0 | none | none |
| E7_ml_aura_ml_tsra_r | ml-atk-00004 | queue_pressure | complete | 0 | none | none |
| E7_ml_aura_ml_tsra_r | ml-atk-00005 | stale_cop_induction | complete | 0 | none | none |

## Detail

### E5_rule_aura_tsra_r atk-00001

- Attack time: 60
- Attack capability: queue_pressure
- Attack agent: AURA
- Target link: SATCOM
- Required runtime defenses: priority_reroute, stale_badge
- Support defenses: video_throttle
- Active defenses at attack: stale_badge@20-until-110; stale_badge@50-until-140
- Response defenses after attack: priority_reroute@65-until-135; video_throttle@65-until-125; pace_switch@75-until-175; stale_badge@80-until-170; video_throttle@100-until-160
- Covered required defenses: priority_reroute, stale_badge
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r atk-00002

- Attack time: 110
- Attack capability: queue_pressure
- Attack agent: AURA
- Target link: LTE
- Required runtime defenses: priority_reroute, stale_badge
- Support defenses: video_throttle
- Active defenses at attack: stale_badge@20-until-110; stale_badge@50-until-140; priority_reroute@65-until-135; video_throttle@65-until-125; pace_switch@75-until-175; stale_badge@80-until-170; video_throttle@100-until-160
- Response defenses after attack: priority_reroute@125-until-195; video_throttle@135-until-195; stale_badge@140-until-230
- Covered required defenses: priority_reroute, stale_badge
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r atk-00003

- Attack time: 160
- Attack capability: queue_pressure
- Attack agent: AURA
- Target link: LTE
- Required runtime defenses: priority_reroute, stale_badge
- Support defenses: video_throttle
- Active defenses at attack: pace_switch@75-until-175; stale_badge@80-until-170; video_throttle@100-until-160; priority_reroute@125-until-195; video_throttle@135-until-195; stale_badge@140-until-230
- Response defenses after attack: video_throttle@170-until-230; stale_badge@170-until-260; priority_reroute@175-until-245; priority_reroute@200-until-270; stale_badge@200-until-290
- Covered required defenses: priority_reroute, stale_badge
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r atk-00004

- Attack time: 210
- Attack capability: queue_pressure
- Attack agent: AURA
- Target link: LTE
- Required runtime defenses: priority_reroute, stale_badge
- Support defenses: video_throttle
- Active defenses at attack: stale_badge@140-until-230; video_throttle@170-until-230; stale_badge@170-until-260; priority_reroute@175-until-245; priority_reroute@200-until-270; stale_badge@200-until-290; video_throttle@205-until-265
- Response defenses after attack: video_throttle@240-until-300; priority_reroute@245-until-315
- Covered required defenses: priority_reroute, stale_badge
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r atk-00005

- Attack time: 260
- Attack capability: queue_pressure
- Attack agent: AURA
- Target link: LTE
- Required runtime defenses: priority_reroute, stale_badge
- Support defenses: video_throttle
- Active defenses at attack: stale_badge@170-until-260; priority_reroute@200-until-270; stale_badge@200-until-290; video_throttle@205-until-265; video_throttle@240-until-300; priority_reroute@245-until-315
- Response defenses after attack: stale_badge@265-until-355; priority_reroute@270-until-340; video_throttle@275-until-335; stale_badge@295-until-385
- Covered required defenses: priority_reroute, stale_badge
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r ml-atk-00001

- Attack time: 60
- Attack capability: queue_pressure
- Attack agent: AURA
- Target link: SATCOM
- Required runtime defenses: priority_reroute, stale_badge
- Support defenses: video_throttle
- Active defenses at attack: none
- Response defenses after attack: priority_reroute@70-until-140; video_throttle@70-until-130; stale_badge@70-until-160; pace_switch@70-until-170; ml_attack_alert@80-until-150
- Covered required defenses: priority_reroute, stale_badge
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 10
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r ml-atk-00002

- Attack time: 110
- Attack capability: failover_chasing
- Attack agent: AURA
- Target link: LTE
- Required runtime defenses: ml_attack_alert
- Support defenses: pace_switch, priority_reroute
- Active defenses at attack: priority_reroute@70-until-140; video_throttle@70-until-130; stale_badge@70-until-160; pace_switch@70-until-170; ml_attack_alert@80-until-150; ml_attack_alert@105-until-175; priority_reroute@105-until-175; video_throttle@105-until-165; stale_badge@105-until-195
- Response defenses after attack: ml_attack_alert@130-until-200; priority_reroute@130-until-200; video_throttle@140-until-200; pace_switch@150-until-250
- Covered required defenses: ml_attack_alert
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r ml-atk-00003

- Attack time: 160
- Attack capability: failover_chasing
- Attack agent: AURA
- Target link: MESH
- Required runtime defenses: ml_attack_alert
- Support defenses: pace_switch, priority_reroute
- Active defenses at attack: stale_badge@70-until-160; pace_switch@70-until-170; ml_attack_alert@105-until-175; priority_reroute@105-until-175; video_throttle@105-until-165; stale_badge@105-until-195; ml_attack_alert@130-until-200; priority_reroute@130-until-200; video_throttle@140-until-200; pace_switch@150-until-250; ml_attack_alert@155-until-225; stale_badge@160-until-250
- Response defenses after attack: priority_reroute@175-until-245; stale_badge@190-until-280
- Covered required defenses: ml_attack_alert
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r ml-atk-00004

- Attack time: 210
- Attack capability: queue_pressure
- Attack agent: AURA
- Target link: MESH
- Required runtime defenses: priority_reroute, stale_badge
- Support defenses: video_throttle
- Active defenses at attack: pace_switch@150-until-250; ml_attack_alert@155-until-225; stale_badge@160-until-250; priority_reroute@175-until-245; stale_badge@190-until-280; video_throttle@205-until-265
- Response defenses after attack: ml_attack_alert@220-until-290; priority_reroute@220-until-290; stale_badge@235-until-325; video_throttle@240-until-300; ml_attack_alert@245-until-315
- Covered required defenses: priority_reroute, stale_badge
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r ml-atk-00005

- Attack time: 260
- Attack capability: stale_cop_induction
- Attack agent: AURA
- Target link: MESH
- Required runtime defenses: stale_badge
- Support defenses: none
- Active defenses at attack: stale_badge@190-until-280; video_throttle@205-until-265; ml_attack_alert@220-until-290; priority_reroute@220-until-290; stale_badge@235-until-325; video_throttle@240-until-300; ml_attack_alert@245-until-315; priority_reroute@260-until-330; pace_switch@260-until-360
- Response defenses after attack: ml_attack_alert@270-until-340; stale_badge@270-until-360; video_throttle@275-until-335; ml_attack_alert@295-until-365; stale_badge@300-until-390
- Covered required defenses: stale_badge
- Missing required defenses: none
- Missing support defenses: none
- First required response latency sec: 0
- Response status: complete
- Audit basis: defense is counted if active at attack time through details.until_sec or emitted within the response window
- Residual risk: Stale badge reduces trusted stale exposure but cannot recreate missing freshness.
- Safety boundary: closed simulation response audit only; no RF, exploit, or live network action
