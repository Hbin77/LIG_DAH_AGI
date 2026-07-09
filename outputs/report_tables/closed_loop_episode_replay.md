# Closed-Loop Episode Replay

This table connects each defended AURA attack event to TSRA-R responses, operator alerts, and mission metric movement.
Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

## Summary

### E5_rule_aura_tsra_r

- Episodes: 5
- Outcomes: contained after peak degradation=1, covered with residual mission impact=1, held near attack-time impact=3

### E7_ml_aura_ml_tsra_r

- Episodes: 5
- Outcomes: contained after peak degradation=1, covered with residual mission impact=1, held near attack-time impact=3

## Episode Table

| experiment | episode_id | attack_event_id | attack_type | target_link | response_status | first_required_response_latency_sec | peak_mission_impact | end_mission_impact | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-01 | atk-00001 | queue_pressure | SATCOM | complete | 0 | 0.170655 | 0.107999 | contained after peak degradation |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-02 | atk-00002 | queue_pressure | LTE | complete | 0 | 0.0975179 | 0.0780845 | held near attack-time impact |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-03 | atk-00003 | queue_pressure | LTE | complete | 0 | 0.115123 | 0.112973 | held near attack-time impact |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-04 | atk-00004 | queue_pressure | LTE | complete | 0 | 0.112348 | 0.0727585 | held near attack-time impact |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-05 | atk-00005 | queue_pressure | LTE | complete | 0 | 0.105899 | 0.103756 | covered with residual mission impact |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-01 | ml-atk-00001 | queue_pressure | SATCOM | complete | 10 | 0.383116 | 0.131467 | contained after peak degradation |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-02 | ml-atk-00002 | failover_chasing | LTE | complete | 0 | 0.132338 | 0.10647 | held near attack-time impact |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-03 | ml-atk-00003 | failover_chasing | MESH | complete | 0 | 0.13899 | 0.137665 | held near attack-time impact |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-04 | ml-atk-00004 | queue_pressure | MESH | complete | 0 | 0.136148 | 0.0986017 | held near attack-time impact |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-05 | ml-atk-00005 | stale_cop_induction | MESH | complete | 0 | 0.14835 | 0.146587 | covered with residual mission impact |

## Episode Detail

### E5_rule_aura_tsra_r-episode-01

- Attack: atk-00001 queue_pressure target=SATCOM
- Attack reason: increase non-critical queue occupancy
- Expected mission impact: 0.566191
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=stale_badge@20-until-110; stale_badge@50-until-140 | response=priority_reroute@65-until-135; video_throttle@65-until-125; pace_switch@75-until-175; stale_badge@80-until-170; video_throttle@100-until-160
- Operator alerts: t=65; def-00003; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=65; def-00004; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=75; def-00005; pace_switch; severity=high; PACE switch selected target=LTE; reason=SATCOM degraded beyond mission threshold. || t=80; def-00006; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=100; def-00007; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity.
- Mission impact: start=0.170655, peak=0.170655, end=0.107999
- Peak latency/stale/inversion: 2.4 / 0.125 / 0.190476
- Outcome: contained after peak degradation
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r-episode-02

- Attack: atk-00002 queue_pressure target=LTE
- Attack reason: increase non-critical queue occupancy
- Expected mission impact: 0.939263
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=stale_badge@20-until-110; stale_badge@50-until-140; priority_reroute@65-until-135; video_throttle@65-until-125; pace_switch@75-until-175; stale_badge@80-until-170; video_throttle@100-until-160 | response=priority_reroute@125-until-195; video_throttle@135-until-195; stale_badge@140-until-230
- Operator alerts: t=125; def-00008; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=135; def-00009; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=140; def-00010; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.0975179, peak=0.0975179, end=0.0780845
- Peak latency/stale/inversion: 1.4 / 0.0625 / 0.0742857
- Outcome: held near attack-time impact
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r-episode-03

- Attack: atk-00003 queue_pressure target=LTE
- Attack reason: increase non-critical queue occupancy
- Expected mission impact: 1
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=pace_switch@75-until-175; stale_badge@80-until-170; video_throttle@100-until-160; priority_reroute@125-until-195; video_throttle@135-until-195; stale_badge@140-until-230 | response=video_throttle@170-until-230; stale_badge@170-until-260; priority_reroute@175-until-245; priority_reroute@200-until-270; stale_badge@200-until-290
- Operator alerts: t=170; def-00011; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=170; def-00012; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=175; def-00013; priority_reroute; severity=medium; Critical traffic is waiting behind lower-priority load. || t=200; def-00014; priority_reroute; severity=medium; Critical traffic is waiting behind lower-priority load. || t=200; def-00015; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.110655, peak=0.115123, end=0.112973
- Peak latency/stale/inversion: 2 / 0.125 / 0.0371429
- Outcome: held near attack-time impact
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r-episode-04

- Attack: atk-00004 queue_pressure target=LTE
- Attack reason: increase non-critical queue occupancy
- Expected mission impact: 1
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=stale_badge@140-until-230; video_throttle@170-until-230; stale_badge@170-until-260; priority_reroute@175-until-245; priority_reroute@200-until-270; stale_badge@200-until-290; video_throttle@205-until-265 | response=video_throttle@240-until-300; priority_reroute@245-until-315
- Operator alerts: t=240; def-00017; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=245; def-00018; priority_reroute; severity=medium; Critical traffic is waiting behind lower-priority load.
- Mission impact: start=0.112348, peak=0.112348, end=0.0727585
- Peak latency/stale/inversion: 2 / 0.125 / 0.0271967
- Outcome: held near attack-time impact
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r-episode-05

- Attack: atk-00005 queue_pressure target=LTE
- Attack reason: increase non-critical queue occupancy
- Expected mission impact: 0.956
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=stale_badge@170-until-260; priority_reroute@200-until-270; stale_badge@200-until-290; video_throttle@205-until-265; video_throttle@240-until-300; priority_reroute@245-until-315 | response=stale_badge@265-until-355; priority_reroute@270-until-340; video_throttle@275-until-335; stale_badge@295-until-385
- Operator alerts: t=265; def-00019; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=270; def-00020; priority_reroute; severity=medium; Critical traffic is waiting behind lower-priority load. || t=275; def-00021; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=295; def-00022; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.0717066, peak=0.105899, end=0.103756
- Peak latency/stale/inversion: 1.45 / 0.125 / 0.0219966
- Outcome: covered with residual mission impact
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-01

- Attack: ml-atk-00001 queue_pressure target=SATCOM
- Attack reason: ML impact predictor selected queue_pressure
- Expected mission impact: 0.602005
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 10
- Defense chain: response=priority_reroute@70-until-140; video_throttle@70-until-130; stale_badge@70-until-160; pace_switch@70-until-170; ml_attack_alert@80-until-150
- Operator alerts: t=70; def-00001; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=70; def-00002; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=70; def-00003; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=70; def-00004; pace_switch; severity=high; PACE switch selected target=LTE; reason=SATCOM degraded beyond mission threshold. || t=80; def-00005; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.955265 above threshold=0.75.
- Mission impact: start=0.376905, peak=0.383116, end=0.131467
- Peak latency/stale/inversion: 4.9 / 0.5 / 0.234568
- Outcome: contained after peak degradation
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-02

- Attack: ml-atk-00002 failover_chasing target=LTE
- Attack reason: ML impact predictor selected failover_chasing
- Expected mission impact: 0.836848
- Response status: complete
- Required defenses: ml_attack_alert
- Covered required defenses: ml_attack_alert
- First required response latency: 0
- Defense chain: active=priority_reroute@70-until-140; video_throttle@70-until-130; stale_badge@70-until-160; pace_switch@70-until-170; ml_attack_alert@80-until-150; ml_attack_alert@105-until-175; priority_reroute@105-until-175; video_throttle@105-until-165; stale_badge@105-until-195 | response=ml_attack_alert@130-until-200; priority_reroute@130-until-200; video_throttle@140-until-200; pace_switch@150-until-250
- Operator alerts: t=130; def-00010; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.972249 above threshold=0.75. || t=130; def-00011; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=140; def-00012; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=150; def-00013; pace_switch; severity=high; PACE switch selected target=MESH; reason=fallback link degraded beyond mission threshold.
- Mission impact: start=0.114622, peak=0.132338, end=0.10647
- Peak latency/stale/inversion: 1.3 / 0.125 / 0.109827
- Outcome: held near attack-time impact
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-03

- Attack: ml-atk-00003 failover_chasing target=MESH
- Attack reason: ML impact predictor selected failover_chasing
- Expected mission impact: 0.822403
- Response status: complete
- Required defenses: ml_attack_alert
- Covered required defenses: ml_attack_alert
- First required response latency: 0
- Defense chain: active=stale_badge@70-until-160; pace_switch@70-until-170; ml_attack_alert@105-until-175; priority_reroute@105-until-175; video_throttle@105-until-165; stale_badge@105-until-195; ml_attack_alert@130-until-200; priority_reroute@130-until-200; video_throttle@140-until-200; pace_switch@150-until-250; ml_attack_alert@155-until-225; stale_badge@160-until-250 | response=priority_reroute@175-until-245; stale_badge@190-until-280
- Operator alerts: t=160; def-00015; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=175; def-00016; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=190; def-00017; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.137802, peak=0.13899, end=0.137665
- Peak latency/stale/inversion: 2 / 0.125 / 0.058104
- Outcome: held near attack-time impact
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-04

- Attack: ml-atk-00004 queue_pressure target=MESH
- Attack reason: ML impact predictor selected queue_pressure
- Expected mission impact: 0.801872
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=pace_switch@150-until-250; ml_attack_alert@155-until-225; stale_badge@160-until-250; priority_reroute@175-until-245; stale_badge@190-until-280; video_throttle@205-until-265 | response=ml_attack_alert@220-until-290; priority_reroute@220-until-290; stale_badge@235-until-325; video_throttle@240-until-300; ml_attack_alert@245-until-315
- Operator alerts: t=220; def-00019; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.88058 above threshold=0.75. || t=220; def-00020; priority_reroute; severity=medium; Critical traffic is waiting behind lower-priority load. || t=235; def-00021; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=240; def-00022; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=245; def-00023; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.936032 above threshold=0.75.
- Mission impact: start=0.136148, peak=0.136148, end=0.0986017
- Peak latency/stale/inversion: 2 / 0.125 / 0.0421286
- Outcome: held near attack-time impact
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-05

- Attack: ml-atk-00005 stale_cop_induction target=MESH
- Attack reason: ML impact predictor selected stale_cop_induction
- Expected mission impact: 0.661893
- Response status: complete
- Required defenses: stale_badge
- Covered required defenses: stale_badge
- First required response latency: 0
- Defense chain: active=stale_badge@190-until-280; video_throttle@205-until-265; ml_attack_alert@220-until-290; priority_reroute@220-until-290; stale_badge@235-until-325; video_throttle@240-until-300; ml_attack_alert@245-until-315; priority_reroute@260-until-330; pace_switch@260-until-360 | response=ml_attack_alert@270-until-340; stale_badge@270-until-360; video_throttle@275-until-335; ml_attack_alert@295-until-365; stale_badge@300-until-390
- Operator alerts: t=260; def-00024; priority_reroute; severity=medium; Critical traffic is waiting behind lower-priority load. || t=260; def-00025; pace_switch; severity=high; PACE switch selected target=LTE; reason=fallback link degraded beyond mission threshold. || t=270; def-00026; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.930785 above threshold=0.75. || t=270; def-00027; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=275; def-00028; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=295; def-00029; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.9331 above threshold=0.75. || t=300; def-00030; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.114642, peak=0.14835, end=0.146587
- Peak latency/stale/inversion: 2 / 0.125 / 0.0338681
- Outcome: covered with residual mission impact
- Residual risk: Stale badge reduces trusted stale exposure but cannot recreate missing freshness.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action
