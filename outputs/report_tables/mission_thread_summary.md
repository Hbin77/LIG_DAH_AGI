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
| thread-03 | E5_rule_aura_tsra_r | atk-00003 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=priority_reroute, stale_badge, video_throttle | start=0.110655; peak=0.115123; end=0.112973; reduction_from_peak=0.0021496; outcome=held near attack-time impact | pass |
| thread-04 | E5_rule_aura_tsra_r | atk-00004 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=2; actions=priority_reroute, video_throttle | start=0.112348; peak=0.112348; end=0.0727585; reduction_from_peak=0.0395898; outcome=held near attack-time impact | pass |
| thread-05 | E5_rule_aura_tsra_r | atk-00005 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=4; actions=priority_reroute, stale_badge, video_throttle | start=0.0717066; peak=0.105899; end=0.103756; reduction_from_peak=0.00214269; outcome=covered with residual mission impact | pass |
| thread-06 | E7_ml_aura_ml_tsra_r | ml-atk-00001 | queue_pressure | status=complete; first_required_latency_sec=10; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle | start=0.376905; peak=0.383116; end=0.131467; reduction_from_peak=0.251649; outcome=contained after peak degradation | pass |
| thread-07 | E7_ml_aura_ml_tsra_r | ml-atk-00002 | failover_chasing | status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=4; actions=ml_attack_alert, pace_switch, priority_reroute, video_throttle | start=0.114622; peak=0.132338; end=0.10647; reduction_from_peak=0.025868; outcome=held near attack-time impact | pass |
| thread-08 | E7_ml_aura_ml_tsra_r | ml-atk-00003 | failover_chasing | status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=3; actions=priority_reroute, stale_badge | start=0.137802; peak=0.13899; end=0.137665; reduction_from_peak=0.00132496; outcome=held near attack-time impact | pass |
| thread-09 | E7_ml_aura_ml_tsra_r | ml-atk-00004 | queue_pressure | status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=ml_attack_alert, priority_reroute, stale_badge, video_throttle | start=0.136148; peak=0.136148; end=0.0986017; reduction_from_peak=0.0375459; outcome=held near attack-time impact | pass |
| thread-10 | E7_ml_aura_ml_tsra_r | ml-atk-00005 | stale_cop_induction | status=complete; first_required_latency_sec=0; covered_required=stale_badge; defense_event_count=7; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle | start=0.114642; peak=0.14835; end=0.146587; reduction_from_peak=0.00176331; outcome=covered with residual mission impact | pass |

## Detail

### thread-01 E5_rule_aura_tsra_r atk-00001

- Attack: queue_pressure target=SATCOM at t=60
- Attack decision: agent=AURA; score=0.543691; expected_impact=0.566191; selection_margin=0.109464; threshold_margin=0.423691
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=pace_switch, priority_reroute, stale_badge, video_throttle
- Attribution: pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0217057 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.0208333 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.170655; peak=0.170655; end=0.107999; reduction_from_peak=0.0626556; outcome=contained after peak degradation
- Operator alert count: 5
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=5, operator_alerts=5, outcome=contained after peak degradation.

### thread-02 E5_rule_aura_tsra_r atk-00002

- Attack: queue_pressure target=LTE at t=110
- Attack decision: agent=AURA; score=0.916763; expected_impact=0.939263; selection_margin=0.001674; threshold_margin=0.796763
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=3; actions=priority_reroute, stale_badge, video_throttle
- Attribution: priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.0208333 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.0975179; peak=0.0975179; end=0.0780845; reduction_from_peak=0.0194333; outcome=held near attack-time impact
- Operator alert count: 3
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=3, operator_alerts=3, outcome=held near attack-time impact.

### thread-03 E5_rule_aura_tsra_r atk-00003

- Attack: queue_pressure target=LTE at t=160
- Attack decision: agent=AURA; score=0.9775; expected_impact=1; selection_margin=0.081359; threshold_margin=0.8575
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=priority_reroute, stale_badge, video_throttle
- Attribution: priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.0208333 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.110655; peak=0.115123; end=0.112973; reduction_from_peak=0.0021496; outcome=held near attack-time impact
- Operator alert count: 5
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=5, operator_alerts=5, outcome=held near attack-time impact.

### thread-04 E5_rule_aura_tsra_r atk-00004

- Attack: queue_pressure target=LTE at t=210
- Attack decision: agent=AURA; score=0.9475; expected_impact=1; selection_margin=0.056345; threshold_margin=0.8275
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=2; actions=priority_reroute, video_throttle
- Attribution: priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.112348; peak=0.112348; end=0.0727585; reduction_from_peak=0.0395898; outcome=held near attack-time impact
- Operator alert count: 2
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=2, operator_alerts=2, outcome=held near attack-time impact.

### thread-05 E5_rule_aura_tsra_r atk-00005

- Attack: queue_pressure target=LTE at t=260
- Attack decision: agent=AURA; score=0.9035; expected_impact=0.956; selection_margin=0.045006; threshold_margin=0.7835
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=4; actions=priority_reroute, stale_badge, video_throttle
- Attribution: priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.0208333 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.0717066; peak=0.105899; end=0.103756; reduction_from_peak=0.00214269; outcome=covered with residual mission impact
- Operator alert count: 4
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=4, operator_alerts=4, outcome=covered with residual mission impact.

### thread-06 E7_ml_aura_ml_tsra_r ml-atk-00001

- Attack: queue_pressure target=SATCOM at t=60
- Attack decision: agent=AURA; score=0.579505; expected_impact=0.602005; selection_margin=0.072803; threshold_margin=0.459505
- Response: status=complete; first_required_latency_sec=10; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.00953569 || pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0217057 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.0208333 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.376905; peak=0.383116; end=0.131467; reduction_from_peak=0.251649; outcome=contained after peak degradation
- Operator alert count: 5
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=5, operator_alerts=5, outcome=contained after peak degradation.

### thread-07 E7_ml_aura_ml_tsra_r ml-atk-00002

- Attack: failover_chasing target=LTE at t=110
- Attack decision: agent=AURA; score=0.841848; expected_impact=0.836848; selection_margin=0.101344; threshold_margin=0.721848
- Response: status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=4; actions=ml_attack_alert, pace_switch, priority_reroute, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.00953569 || pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0217057 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.114622; peak=0.132338; end=0.10647; reduction_from_peak=0.025868; outcome=held near attack-time impact
- Operator alert count: 4
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=4, operator_alerts=4, outcome=held near attack-time impact.

### thread-08 E7_ml_aura_ml_tsra_r ml-atk-00003

- Attack: failover_chasing target=MESH at t=160
- Attack decision: agent=AURA; score=0.817403; expected_impact=0.822403; selection_margin=0.1252; threshold_margin=0.697403
- Response: status=complete; first_required_latency_sec=0; covered_required=ml_attack_alert; defense_event_count=3; actions=priority_reroute, stale_badge
- Attribution: priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.0208333
- Metrics: start=0.137802; peak=0.13899; end=0.137665; reduction_from_peak=0.00132496; outcome=held near attack-time impact
- Operator alert count: 3
- Residual risk: Failover chasing is detected by the ML defense window; PACE support may already be active or may expire before a later attack window.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=3, operator_alerts=3, outcome=held near attack-time impact.

### thread-09 E7_ml_aura_ml_tsra_r ml-atk-00004

- Attack: queue_pressure target=MESH at t=210
- Attack decision: agent=AURA; score=0.779372; expected_impact=0.801872; selection_margin=0.165075; threshold_margin=0.659372
- Response: status=complete; first_required_latency_sec=0; covered_required=priority_reroute, stale_badge; defense_event_count=5; actions=ml_attack_alert, priority_reroute, stale_badge, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.00953569 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.0208333 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.136148; peak=0.136148; end=0.0986017; reduction_from_peak=0.0375459; outcome=held near attack-time impact
- Operator alert count: 5
- Residual risk: Queue pressure can still create residual latency until reroute and throttling take effect.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=5, operator_alerts=5, outcome=held near attack-time impact.

### thread-10 E7_ml_aura_ml_tsra_r ml-atk-00005

- Attack: stale_cop_induction target=MESH at t=260
- Attack decision: agent=AURA; score=0.779393; expected_impact=0.661893; selection_margin=0.150585; threshold_margin=0.659393
- Response: status=complete; first_required_latency_sec=0; covered_required=stale_badge; defense_event_count=7; actions=ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
- Attribution: ml_attack_alert:class=reactive_window_supported,status=pass,primary=mission_impact,delta=-0.00953569 || pace_switch:class=bounded_tradeoff_supported,status=pass,primary=mission_impact,delta=-0.0217057 || priority_reroute:class=ablation_supported,status=pass,primary=priority_inversion_rate,delta=-0.0256654 || stale_badge:class=ablation_supported,status=pass,primary=trusted_stale_exposure,delta=-0.0208333 || video_throttle:class=local_metric_supported,status=pass,primary=p95_critical_latency_sec,delta=0.0153846
- Metrics: start=0.114642; peak=0.14835; end=0.146587; reduction_from_peak=0.00176331; outcome=covered with residual mission impact
- Operator alert count: 7
- Residual risk: Stale badge reduces trusted stale exposure but cannot recreate missing freshness.
- Status: pass
- Interpretation: Attack, defense response, operator alerts, action attribution, and metric movement form one complete mission thread; defense_events=7, operator_alerts=7, outcome=covered with residual mission impact.
