# Mission Thread Summary

This summary joins each attack episode to decision evidence, response coverage, defense-action attribution, operator alerts, metric movement, and residual risk.
Safety boundary: closed simulation mission-thread summary only; no RF, exploit, or live network action

## Summary

- Mission threads: 10
- Status counts: pass=10
- Experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r

## Thread Table

| thread_id | experiment | attack_event_id | attack_type | response_signal | metric_signal | thread_status |
| --- | --- | --- | --- | --- | --- | --- |
| thread-01 | E5_rule_aura_tsra_r | atk-00001 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=pace_switch, priority_reroute, stale_badge, video_throttle | start=0.170655; peak=0.170655; end=0.107999; reduction_from_peak=0.0626556; outcome=contained after peak degradation | pass |
| thread-02 | E5_rule_aura_tsra_r | atk-00002 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=3; actions=priority_reroute, stale_badge, video_throttle | start=0.0975179; peak=0.0975179; end=0.0780845; reduction_from_peak=0.0194333; outcome=held near attack-time impact | pass |
| thread-03 | E5_rule_aura_tsra_r | atk-00003 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=4; actions=priority_reroute, stale_badge, video_throttle | start=0.127164; peak=0.127164; end=0.121698; reduction_from_peak=0.00546539; outcome=held near attack-time impact | pass |
| thread-04 | E5_rule_aura_tsra_r | atk-00004 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=3; actions=pace_switch, priority_reroute, video_throttle | start=0.120809; peak=0.120809; end=0.1007; reduction_from_peak=0.0201095; outcome=held near attack-time impact | pass |
| thread-05 | E5_rule_aura_tsra_r | atk-00005 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=3; actions=stale_badge, video_throttle | start=0.100367; peak=0.134572; end=0.133373; reduction_from_peak=0.00119899; outcome=covered with residual mission impact | pass |
| thread-06 | E7_ml_aura_ml_tsra_r | ml-atk-00001 | queue_pressure | status=complete; first_required_latency_sec=20; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle | start=0.376905; peak=0.437917; end=0.232305; reduction_from_peak=0.205612; outcome=contained after peak degradation | pass |
| thread-07 | E7_ml_aura_ml_tsra_r | ml-atk-00002 | failover_chasing | status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=6; actions=ml_attack_alert, priority_reroute, stale_badge, video_throttle | start=0.211596; peak=0.211596; end=0.190239; reduction_from_peak=0.0213565; outcome=held near attack-time impact | pass |
| thread-08 | E7_ml_aura_ml_tsra_r | ml-atk-00003 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=6; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle | start=0.201798; peak=0.201798; end=0.142938; reduction_from_peak=0.05886; outcome=contained after peak degradation | pass |
| thread-09 | E7_ml_aura_ml_tsra_r | ml-atk-00004 | failover_chasing | status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=7; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle | start=0.141337; peak=0.144298; end=0.123725; reduction_from_peak=0.0205729; outcome=held near attack-time impact | pass |
| thread-10 | E7_ml_aura_ml_tsra_r | ml-atk-00005 | failover_chasing | status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=4; actions=ml_attack_alert, stale_badge, video_throttle | start=0.157241; peak=0.157241; end=0.154619; reduction_from_peak=0.00262202; outcome=held near attack-time impact | pass |

## Detail

### thread-01 E5_rule_aura_tsra_r atk-00001

- Attack: queue_pressure target=SATCOM at t=60
- Attack decision: agent=AURA; score=0.543691; expected_impact=0.566191; selection_margin=0.109464; threshold_margin=0.423691
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=pace_switch, priority_reroute, stale_badge, video_throttle
- Attribution: pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0232876 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0347756 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.170655; peak=0.170655; end=0.107999; reduction_from_peak=0.0626556; outcome=contained after peak degradation
- Operator alert count: 5
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=5, operator_alerts=5, outcome=contained after peak degradation.

### thread-02 E5_rule_aura_tsra_r atk-00002

- Attack: queue_pressure target=LTE at t=110
- Attack decision: agent=AURA; score=0.916763; expected_impact=0.939263; selection_margin=0.001674; threshold_margin=0.796763
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=3; actions=priority_reroute, stale_badge, video_throttle
- Attribution: priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0347756 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.0975179; peak=0.0975179; end=0.0780845; reduction_from_peak=0.0194333; outcome=held near attack-time impact
- Operator alert count: 3
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=3, operator_alerts=3, outcome=held near attack-time impact.

### thread-03 E5_rule_aura_tsra_r atk-00003

- Attack: queue_pressure target=MESH at t=160
- Attack decision: agent=AURA; score=0.9475; expected_impact=1; selection_margin=0.051469; threshold_margin=0.8275
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=4; actions=priority_reroute, stale_badge, video_throttle
- Attribution: priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0347756 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.127164; peak=0.127164; end=0.121698; reduction_from_peak=0.00546539; outcome=held near attack-time impact
- Operator alert count: 4
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=4, operator_alerts=4, outcome=held near attack-time impact.

### thread-04 E5_rule_aura_tsra_r atk-00004

- Attack: queue_pressure target=MESH at t=210
- Attack decision: agent=AURA; score=0.9475; expected_impact=1; selection_margin=0.057984; threshold_margin=0.8275
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=3; actions=pace_switch, priority_reroute, video_throttle
- Attribution: pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0232876 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0347756 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.120809; peak=0.120809; end=0.1007; reduction_from_peak=0.0201095; outcome=held near attack-time impact
- Operator alert count: 3
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=3, operator_alerts=3, outcome=held near attack-time impact.

### thread-05 E5_rule_aura_tsra_r atk-00005

- Attack: queue_pressure target=LTE at t=260
- Attack decision: agent=AURA; score=0.9035; expected_impact=0.956; selection_margin=0.046724; threshold_margin=0.7835
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=3; actions=stale_badge, video_throttle
- Attribution: stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.100367; peak=0.134572; end=0.133373; reduction_from_peak=0.00119899; outcome=covered with residual mission impact
- Operator alert count: 3
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=3, operator_alerts=3, outcome=covered with residual mission impact.

### thread-06 E7_ml_aura_ml_tsra_r ml-atk-00001

- Attack: queue_pressure target=SATCOM at t=60
- Attack decision: agent=AURA; score=0.579505; expected_impact=0.602005; selection_margin=0.072803; threshold_margin=0.459505
- Response: status=complete; first_required_latency_sec=20; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.0157261 || pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0232876 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0347756 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.376905; peak=0.437917; end=0.232305; reduction_from_peak=0.205612; outcome=contained after peak degradation
- Operator alert count: 5
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=5, operator_alerts=5, outcome=contained after peak degradation.

### thread-07 E7_ml_aura_ml_tsra_r ml-atk-00002

- Attack: failover_chasing target=LTE at t=110
- Attack decision: agent=AURA; score=0.841793; expected_impact=0.916793; selection_margin=0.018343; threshold_margin=0.721793
- Response: status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=6; actions=ml_attack_alert, priority_reroute, stale_badge, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.0157261 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0347756 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.211596; peak=0.211596; end=0.190239; reduction_from_peak=0.0213565; outcome=held near attack-time impact
- Operator alert count: 6
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=6, operator_alerts=6, outcome=held near attack-time impact.

### thread-08 E7_ml_aura_ml_tsra_r ml-atk-00003

- Attack: queue_pressure target=LTE at t=160
- Attack decision: agent=AURA; score=0.918255; expected_impact=0.970755; selection_margin=0.09985; threshold_margin=0.798255
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=6; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.0157261 || pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0232876 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0347756 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.201798; peak=0.201798; end=0.142938; reduction_from_peak=0.05886; outcome=contained after peak degradation
- Operator alert count: 6
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=6, operator_alerts=6, outcome=contained after peak degradation.

### thread-09 E7_ml_aura_ml_tsra_r ml-atk-00004

- Attack: failover_chasing target=MESH at t=210
- Attack decision: agent=AURA; score=0.745517; expected_impact=0.820517; selection_margin=0.046648; threshold_margin=0.625517
- Response: status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=7; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.0157261 || pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0232876 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0347756 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.141337; peak=0.144298; end=0.123725; reduction_from_peak=0.0205729; outcome=held near attack-time impact
- Operator alert count: 7
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=7, operator_alerts=7, outcome=held near attack-time impact.

### thread-10 E7_ml_aura_ml_tsra_r ml-atk-00005

- Attack: failover_chasing target=LTE at t=260
- Attack decision: agent=AURA; score=0.744854; expected_impact=0.819854; selection_margin=0.048348; threshold_margin=0.624854
- Response: status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=4; actions=ml_attack_alert, stale_badge, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.0157261 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.00390625 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=-0.567857
- Metrics: start=0.157241; peak=0.157241; end=0.154619; reduction_from_peak=0.00262202; outcome=held near attack-time impact
- Operator alert count: 4
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=4, operator_alerts=4, outcome=held near attack-time impact.
