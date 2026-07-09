# Closed-Loop Episode Replay

This table connects each defended AURA attack event to TSRA-R responses, operator alerts, and mission metric movement.
Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

## Summary

### E5_rule_aura_tsra_r

- Episodes: 5
- Outcomes: contained after peak degradation=1, covered with residual mission impact=1, held near attack-time impact=3

### E7_ml_aura_ml_tsra_r

- Episodes: 5
- Outcomes: contained after peak degradation=2, held near attack-time impact=3

## Episode Table

| experiment | episode_id | attack_event_id | attack_type | target_link | response_status | first_required_response_latency_sec | peak_mission_impact | end_mission_impact | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-01 | atk-00001 | queue_pressure | SATCOM | complete | 0 | 0.170655 | 0.107999 | contained after peak degradation |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-02 | atk-00002 | queue_pressure | LTE | complete | 0 | 0.0975179 | 0.0780845 | held near attack-time impact |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-03 | atk-00003 | queue_pressure | MESH | complete | 0 | 0.127164 | 0.121698 | held near attack-time impact |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-04 | atk-00004 | queue_pressure | MESH | complete | 0 | 0.120809 | 0.1007 | held near attack-time impact |
| E5_rule_aura_tsra_r | E5_rule_aura_tsra_r-episode-05 | atk-00005 | queue_pressure | LTE | complete | 0 | 0.134572 | 0.133373 | covered with residual mission impact |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-01 | ml-atk-00001 | queue_pressure | SATCOM | complete | 20 | 0.437917 | 0.232305 | contained after peak degradation |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-02 | ml-atk-00002 | failover_chasing | LTE | complete | 0 | 0.211596 | 0.190239 | held near attack-time impact |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-03 | ml-atk-00003 | queue_pressure | LTE | complete | 0 | 0.201798 | 0.142938 | contained after peak degradation |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-04 | ml-atk-00004 | failover_chasing | MESH | complete | 0 | 0.144298 | 0.123725 | held near attack-time impact |
| E7_ml_aura_ml_tsra_r | E7_ml_aura_ml_tsra_r-episode-05 | ml-atk-00005 | failover_chasing | LTE | complete | 0 | 0.157241 | 0.154619 | held near attack-time impact |

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

- Attack: atk-00003 queue_pressure target=MESH
- Attack reason: increase non-critical queue occupancy
- Expected mission impact: 1
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=pace_switch@75-until-175; stale_badge@80-until-170; video_throttle@100-until-160; priority_reroute@125-until-195; video_throttle@135-until-195; stale_badge@140-until-230; pace_switch@155-until-255 | response=priority_reroute@170-until-240; video_throttle@170-until-230; stale_badge@170-until-260; stale_badge@200-until-290
- Operator alerts: t=170; def-00012; priority_reroute; severity=medium; Critical traffic is waiting behind lower-priority load. || t=170; def-00013; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=170; def-00014; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=200; def-00015; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.127164, peak=0.127164, end=0.121698
- Peak latency/stale/inversion: 1 / 0.125 / 0.0368272
- Outcome: held near attack-time impact
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E5_rule_aura_tsra_r-episode-04

- Attack: atk-00004 queue_pressure target=MESH
- Attack reason: increase non-critical queue occupancy
- Expected mission impact: 1
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=stale_badge@140-until-230; pace_switch@155-until-255; priority_reroute@170-until-240; video_throttle@170-until-230; stale_badge@170-until-260; stale_badge@200-until-290; priority_reroute@205-until-275; video_throttle@205-until-265 | response=priority_reroute@235-until-305; pace_switch@235-until-335; video_throttle@240-until-300
- Operator alerts: t=235; def-00018; priority_reroute; severity=medium; Critical traffic is waiting behind lower-priority load. || t=235; def-00019; pace_switch; severity=high; PACE switch selected target=LTE; reason=fallback link degraded beyond mission threshold. || t=240; def-00020; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity.
- Mission impact: start=0.120809, peak=0.120809, end=0.1007
- Peak latency/stale/inversion: 1 / 0.125 / 0.0241187
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
- Defense chain: active=stale_badge@170-until-260; stale_badge@200-until-290; priority_reroute@205-until-275; video_throttle@205-until-265; priority_reroute@235-until-305; pace_switch@235-until-335; video_throttle@240-until-300 | response=stale_badge@265-until-355; video_throttle@275-until-335; stale_badge@295-until-385
- Operator alerts: t=265; def-00021; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=275; def-00022; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=295; def-00023; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.100367, peak=0.134572, end=0.133373
- Peak latency/stale/inversion: 1 / 0.125 / 0.0186514
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
- First required response latency: 20
- Defense chain: response=ml_attack_alert@80-until-150; priority_reroute@80-until-150; video_throttle@80-until-140; stale_badge@80-until-170; pace_switch@80-until-180
- Operator alerts: t=80; def-00001; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.946005 above threshold=0.75. || t=80; def-00002; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=80; def-00003; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=80; def-00004; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=80; def-00005; pace_switch; severity=high; PACE switch selected target=LTE; reason=SATCOM degraded beyond mission threshold.
- Mission impact: start=0.376905, peak=0.437917, end=0.232305
- Peak latency/stale/inversion: 12.4 / 0.5 / 0.340426
- Outcome: contained after peak degradation
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-02

- Attack: ml-atk-00002 failover_chasing target=LTE
- Attack reason: ML impact predictor selected failover_chasing
- Expected mission impact: 0.916793
- Response status: complete
- Required defenses: ml_attack_alert
- Covered required defenses: ml_attack_alert
- First required response latency: 0
- Defense chain: active=ml_attack_alert@80-until-150; priority_reroute@80-until-150; video_throttle@80-until-140; stale_badge@80-until-170; pace_switch@80-until-180; ml_attack_alert@105-until-175 | response=video_throttle@115-until-175; priority_reroute@120-until-190; stale_badge@120-until-210; ml_attack_alert@130-until-200; video_throttle@150-until-210; stale_badge@150-until-240
- Operator alerts: t=115; def-00007; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=120; def-00008; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=120; def-00009; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=130; def-00010; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.971653 above threshold=0.75. || t=150; def-00011; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=150; def-00012; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.211596, peak=0.211596, end=0.190239
- Peak latency/stale/inversion: 10.6 / 0.125 / 0.179775
- Outcome: held near attack-time impact
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-03

- Attack: ml-atk-00003 queue_pressure target=LTE
- Attack reason: ML impact predictor selected queue_pressure
- Expected mission impact: 0.970755
- Response status: complete
- Required defenses: priority_reroute, stale_badge
- Covered required defenses: priority_reroute, stale_badge
- First required response latency: 0
- Defense chain: active=stale_badge@80-until-170; pace_switch@80-until-180; ml_attack_alert@105-until-175; video_throttle@115-until-175; priority_reroute@120-until-190; stale_badge@120-until-210; ml_attack_alert@130-until-200; video_throttle@150-until-210; stale_badge@150-until-240; ml_attack_alert@155-until-225; priority_reroute@160-until-230; pace_switch@160-until-260 | response=ml_attack_alert@180-until-250; stale_badge@180-until-270; video_throttle@185-until-245; priority_reroute@190-until-260
- Operator alerts: t=160; def-00014; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=160; def-00015; pace_switch; severity=high; PACE switch selected target=MESH; reason=fallback link degraded beyond mission threshold. || t=180; def-00016; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.959167 above threshold=0.75. || t=180; def-00017; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=185; def-00018; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=190; def-00019; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load.
- Mission impact: start=0.201798, peak=0.201798, end=0.142938
- Peak latency/stale/inversion: 7.75 / 0.125 / 0.0960961
- Outcome: contained after peak degradation
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-04

- Attack: ml-atk-00004 failover_chasing target=MESH
- Attack reason: ML impact predictor selected failover_chasing
- Expected mission impact: 0.820517
- Response status: complete
- Required defenses: ml_attack_alert
- Covered required defenses: ml_attack_alert
- First required response latency: 0
- Defense chain: active=stale_badge@120-until-210; video_throttle@150-until-210; stale_badge@150-until-240; ml_attack_alert@155-until-225; priority_reroute@160-until-230; pace_switch@160-until-260; ml_attack_alert@180-until-250; stale_badge@180-until-270; video_throttle@185-until-245; priority_reroute@190-until-260; ml_attack_alert@205-until-275; stale_badge@210-until-300 | response=priority_reroute@215-until-285; video_throttle@220-until-280; ml_attack_alert@230-until-300; stale_badge@240-until-330; pace_switch@240-until-340; priority_reroute@245-until-315
- Operator alerts: t=210; def-00021; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=215; def-00022; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load. || t=220; def-00023; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=230; def-00024; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.934522 above threshold=0.75. || t=240; def-00025; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=240; def-00026; pace_switch; severity=high; PACE switch selected target=LTE; reason=fallback link degraded beyond mission threshold. || t=245; def-00027; priority_reroute; severity=high; Critical traffic is waiting behind lower-priority load.
- Mission impact: start=0.141337, peak=0.144298, end=0.123725
- Peak latency/stale/inversion: 2 / 0.125 / 0.0651731
- Outcome: held near attack-time impact
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action

### E7_ml_aura_ml_tsra_r-episode-05

- Attack: ml-atk-00005 failover_chasing target=LTE
- Attack reason: ML impact predictor selected failover_chasing
- Expected mission impact: 0.819854
- Response status: complete
- Required defenses: ml_attack_alert
- Covered required defenses: ml_attack_alert
- First required response latency: 0
- Defense chain: active=pace_switch@160-until-260; stale_badge@180-until-270; priority_reroute@190-until-260; ml_attack_alert@205-until-275; stale_badge@210-until-300; priority_reroute@215-until-285; video_throttle@220-until-280; ml_attack_alert@230-until-300; stale_badge@240-until-330; pace_switch@240-until-340; priority_reroute@245-until-315; ml_attack_alert@255-until-325; video_throttle@255-until-315 | response=stale_badge@270-until-360; ml_attack_alert@280-until-350; video_throttle@290-until-350; stale_badge@300-until-390
- Operator alerts: t=270; def-00030; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5. || t=280; def-00031; ml_attack_alert; severity=high; ML detector flags attack-like degradation probability=0.963056 above threshold=0.75. || t=290; def-00032; video_throttle; severity=medium; Video traffic is being reduced to protect critical capacity. || t=300; def-00033; stale_badge; severity=medium; COP stale confidence badge active; stale_ratio=0.5.
- Mission impact: start=0.157241, peak=0.157241, end=0.154619
- Peak latency/stale/inversion: 2 / 0.125 / 0.0503145
- Outcome: held near attack-time impact
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Safety boundary: closed simulation closed-loop replay only; no RF, exploit, or live network action
