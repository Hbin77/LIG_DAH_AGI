# Agent Decision Feedback Audit

This audit links selected DecisionTrace events in the defended E5/E7 closed-loop runs to event logs, metric feedback, closed-loop outcomes, and defense action attribution.
Safety boundary: closed simulation decision-feedback audit only; no RF, exploit, or live network action

## Summary

- Feedback rows: 66
- Status counts: pass=66
- Event type counts: attack_event=10, defense_event=56
- Feedback classes: attack_contained_by_defense=5, attack_pressure_observed=5, defense_bounded_or_lagged=9, defense_held=27, defense_improved=19, ml_window_triggered=1

## Review Table

| experiment | trace_id | selected_event_id | selected_event_type | action | feedback_class | feedback_status |
| --- | --- | --- | --- | --- | --- | --- |
| E5_rule_aura_tsra_r | tsra-r-trace-00005 | def-00001 | defense_event | stale_badge | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00011 | def-00002 | defense_event | stale_badge | defense_held | pass |
| E5_rule_aura_tsra_r | aura-trace-00007 | atk-00001 | attack_event | queue_pressure | attack_contained_by_defense | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00014 | def-00003 | defense_event | priority_reroute | defense_improved | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00014 | def-00004 | defense_event | video_throttle | defense_improved | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00016 | def-00005 | defense_event | pace_switch | defense_improved | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00017 | def-00006 | defense_event | stale_badge | defense_improved | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00021 | def-00007 | defense_event | video_throttle | defense_improved | pass |
| E5_rule_aura_tsra_r | aura-trace-00012 | atk-00002 | attack_event | queue_pressure | attack_pressure_observed | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00026 | def-00008 | defense_event | priority_reroute | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00028 | def-00009 | defense_event | video_throttle | defense_bounded_or_lagged | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00029 | def-00010 | defense_event | stale_badge | defense_bounded_or_lagged | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00032 | def-00011 | defense_event | pace_switch | defense_held | pass |
| E5_rule_aura_tsra_r | aura-trace-00017 | atk-00003 | attack_event | queue_pressure | attack_contained_by_defense | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00035 | def-00012 | defense_event | priority_reroute | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00035 | def-00013 | defense_event | video_throttle | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00035 | def-00014 | defense_event | stale_badge | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00041 | def-00015 | defense_event | stale_badge | defense_improved | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00042 | def-00016 | defense_event | priority_reroute | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00042 | def-00017 | defense_event | video_throttle | defense_held | pass |
| E5_rule_aura_tsra_r | aura-trace-00022 | atk-00004 | attack_event | queue_pressure | attack_pressure_observed | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00048 | def-00018 | defense_event | priority_reroute | defense_bounded_or_lagged | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00048 | def-00019 | defense_event | pace_switch | defense_bounded_or_lagged | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00049 | def-00020 | defense_event | video_throttle | defense_bounded_or_lagged | pass |
| E5_rule_aura_tsra_r | aura-trace-00027 | atk-00005 | attack_event | queue_pressure | attack_pressure_observed | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00054 | def-00021 | defense_event | stale_badge | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00056 | def-00022 | defense_event | video_throttle | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00060 | def-00023 | defense_event | stale_badge | defense_held | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00007 | ml-atk-00001 | attack_event | queue_pressure | attack_pressure_observed | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00017 | def-00001 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00017 | def-00002 | defense_event | priority_reroute | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00017 | def-00003 | defense_event | video_throttle | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00017 | def-00004 | defense_event | stale_badge | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00017 | def-00005 | defense_event | pace_switch | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00022 | def-00006 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00012 | ml-atk-00002 | attack_event | failover_chasing | attack_contained_by_defense | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00024 | def-00007 | defense_event | video_throttle | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00025 | def-00008 | defense_event | priority_reroute | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00025 | def-00009 | defense_event | stale_badge | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00027 | def-00010 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00031 | def-00011 | defense_event | video_throttle | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00031 | def-00012 | defense_event | stale_badge | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00032 | def-00013 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00017 | ml-atk-00003 | attack_event | queue_pressure | attack_contained_by_defense | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00033 | def-00014 | defense_event | priority_reroute | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00033 | def-00015 | defense_event | pace_switch | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00037 | def-00016 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00037 | def-00017 | defense_event | stale_badge | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00038 | def-00018 | defense_event | video_throttle | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00039 | def-00019 | defense_event | priority_reroute | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00042 | def-00020 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00022 | ml-atk-00004 | attack_event | failover_chasing | attack_pressure_observed | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00043 | def-00021 | defense_event | stale_badge | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00044 | def-00022 | defense_event | priority_reroute | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00045 | def-00023 | defense_event | video_throttle | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00047 | def-00024 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00049 | def-00025 | defense_event | stale_badge | defense_bounded_or_lagged | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00049 | def-00026 | defense_event | pace_switch | defense_bounded_or_lagged | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00050 | def-00027 | defense_event | priority_reroute | defense_bounded_or_lagged | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00052 | def-00028 | defense_event | ml_attack_alert | ml_window_triggered | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00052 | def-00029 | defense_event | video_throttle | defense_bounded_or_lagged | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00027 | ml-atk-00005 | attack_event | failover_chasing | attack_contained_by_defense | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00055 | def-00030 | defense_event | stale_badge | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00057 | def-00031 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00059 | def-00032 | defense_event | video_throttle | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00061 | def-00033 | defense_event | stale_badge | defense_held | pass |

## Detail

### E5_rule_aura_tsra_r tsra-r-trace-00005 def-00001

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.150417; after=0.169756; delta=0.0193396; latency_delta=0; trusted_stale_delta=0; priority_delta=0.0386792
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00011 def-00002

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.169756; after=0.162583; delta=-0.00717296; latency_delta=1.2; trusted_stale_delta=0; priority_delta=-0.0636792
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r aura-trace-00007 atk-00001

- Agent: AURA policy=rule_attack_score
- Decision: score=0.543691; expected_mission_impact=0.566191; target=SATCOM; reason=increase non-critical queue occupancy
- Event link: linked
- Metrics: before=0.170655@t=60; peak=0.170655; after=0.08084@t=140; delta=-0.0898148; peak_latency=2.4; peak_trusted_stale=0.125; peak_priority_inversion=0.190476
- Attribution/outcome: response=complete; outcome=contained after peak degradation; reduction_from_peak=0.0626556
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00014 def-00003

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.166966; after=0.112487; delta=-0.054479; latency_delta=1.1; trusted_stale_delta=-0.0625; priority_delta=-0.0882081
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00014 def-00004

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.166966; after=0.112487; delta=-0.054479; latency_delta=1.1; trusted_stale_delta=-0.0625; priority_delta=-0.0882081
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00016 def-00005

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=SATCOM degraded beyond mission threshold
- Event link: linked
- Metrics: before=0.170642; after=0.102009; delta=-0.0686333; latency_delta=-0.6; trusted_stale_delta=-0.0625; priority_delta=-0.0605167
- Attribution/outcome: observed_effect=improved; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00017 def-00006

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.162583; after=0.0975179; delta=-0.0650655; latency_delta=-0.8; trusted_stale_delta=-0.0625; priority_delta=-0.0507143
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00021 def-00007

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.107999; after=0.0840241; delta=-0.023975; latency_delta=-1; trusted_stale_delta=0; priority_delta=-0.0346167
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r aura-trace-00012 atk-00002

- Agent: AURA policy=rule_attack_score
- Decision: score=0.916763; expected_mission_impact=0.939263; target=LTE; reason=increase non-critical queue occupancy
- Event link: linked
- Metrics: before=0.0975179@t=110; peak=0.127164; after=0.122669@t=190; delta=0.0251508; peak_latency=1.4; peak_trusted_stale=0.125; peak_priority_inversion=0.0742857
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.0194333
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00026 def-00008

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.0859692; after=0.0937202; delta=0.00775104; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.0178313
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00028 def-00009

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.0822366; after=0.126037; delta=0.0438006; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.0144821
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00029 def-00010

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.08084; after=0.125164; delta=0.0443241; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.0134351
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00032 def-00011

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=fallback link degraded beyond mission threshold
- Event link: linked
- Metrics: before=0.0937202; after=0.123194; delta=0.0294742; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00980159
- Attribution/outcome: observed_effect=held; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r aura-trace-00017 atk-00003

- Agent: AURA policy=rule_attack_score
- Decision: score=0.9475; expected_mission_impact=1; target=MESH; reason=increase non-critical queue occupancy
- Event link: linked
- Metrics: before=0.127164@t=160; peak=0.127164; after=0.101182@t=240; delta=-0.0259815; peak_latency=1; peak_trusted_stale=0.125; peak_priority_inversion=0.0368272
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.00546539
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00035 def-00012

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.125164; after=0.121698; delta=-0.00346593; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00693187
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00035 def-00013

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.125164; after=0.121698; delta=-0.00346593; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00693187
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00035 def-00014

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.125164; after=0.121698; delta=-0.00346593; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00693187
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00041 def-00015

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.121698; after=0.0850658; delta=-0.0366324; latency_delta=0; trusted_stale_delta=-0.0625; priority_delta=-0.00451484
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00042 def-00016

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.121226; after=0.101458; delta=-0.0197677; latency_delta=0; trusted_stale_delta=-0.0625; priority_delta=-0.00411868
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00042 def-00017

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.121226; after=0.101458; delta=-0.0197677; latency_delta=0; trusted_stale_delta=-0.0625; priority_delta=-0.00411868
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r aura-trace-00022 atk-00004

- Agent: AURA policy=rule_attack_score
- Decision: score=0.9475; expected_mission_impact=1; target=MESH; reason=increase non-critical queue occupancy
- Event link: linked
- Metrics: before=0.120809@t=210; peak=0.134572; after=0.133686@t=290; delta=0.012877; peak_latency=1; peak_trusted_stale=0.125; peak_priority_inversion=0.0241187
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.0201095
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00048 def-00018

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.101458; after=0.134572; delta=0.0331133; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00252347
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00048 def-00019

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=fallback link degraded beyond mission threshold
- Event link: linked
- Metrics: before=0.101458; after=0.134572; delta=0.0331133; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00252347
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00049 def-00020

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.101182; after=0.134395; delta=0.0332125; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00232501
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r aura-trace-00027 atk-00005

- Agent: AURA policy=rule_attack_score
- Decision: score=0.9035; expected_mission_impact=0.956; target=LTE; reason=increase non-critical queue occupancy
- Event link: linked
- Metrics: before=0.100367@t=260; peak=0.134572; after=0.133373@t=300; delta=0.0330053; peak_latency=1; peak_trusted_stale=0.125; peak_priority_inversion=0.0186514
- Attribution/outcome: response=complete; outcome=covered with residual mission impact; reduction_from_peak=0.00119899
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00054 def-00021

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.134572; after=0.133521; delta=-0.00105019; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00210038
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00056 def-00022

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.134189; after=0.133373; delta=-0.000815993; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00163199
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00060 def-00023

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.133521; after=0.133373; delta=-0.000148802; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.000297604
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00007 ml-atk-00001

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.579505; expected_mission_impact=0.602005; target=SATCOM; reason=ML impact predictor selected queue_pressure
- Event link: linked
- Metrics: before=0.376905@t=60; peak=0.437917; after=0.166086@t=140; delta=-0.210819; peak_latency=12.4; peak_trusted_stale=0.5; peak_priority_inversion=0.340426
- Attribution/outcome: response=complete; outcome=contained after peak degradation; reduction_from_peak=0.205612
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00017 def-00001

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.946005; threshold=0.75; active_defense_until=150
- Event link: linked
- Metrics: before=0.322963; after=0.211596; delta=-0.111367; latency_delta=0.5; trusted_stale_delta=-0.0625; priority_delta=-0.16065
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00017 def-00002

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.322963; after=0.211596; delta=-0.111367; latency_delta=0.5; trusted_stale_delta=-0.0625; priority_delta=-0.16065
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00017 def-00003

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.322963; after=0.211596; delta=-0.111367; latency_delta=0.5; trusted_stale_delta=-0.0625; priority_delta=-0.16065
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00017 def-00004

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.322963; after=0.211596; delta=-0.111367; latency_delta=0.5; trusted_stale_delta=-0.0625; priority_delta=-0.16065
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00017 def-00005

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.322963; after=0.211596; delta=-0.111367; latency_delta=0.5; trusted_stale_delta=-0.0625; priority_delta=-0.16065
- Attribution/outcome: observed_effect=improved; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00022 def-00006

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.951098; threshold=0.75; active_defense_until=175
- Event link: linked
- Metrics: before=0.220011; after=0.170224; delta=-0.0497869; latency_delta=-2.6; trusted_stale_delta=0; priority_delta=-0.0649071
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00012 ml-atk-00002

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.841793; expected_mission_impact=0.916793; target=LTE; reason=ML impact predictor selected failover_chasing
- Event link: linked
- Metrics: before=0.211596@t=110; peak=0.211596; after=0.159966@t=180; delta=-0.0516303; peak_latency=10.6; peak_trusted_stale=0.125; peak_priority_inversion=0.179775
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.0213565
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00024 def-00007

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.205481; after=0.19362; delta=-0.0118609; latency_delta=-2.65; trusted_stale_delta=0.0625; priority_delta=-0.0571386
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00025 def-00008

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.19825; after=0.190239; delta=-0.00801011; latency_delta=-2.45; trusted_stale_delta=0.0625; priority_delta=-0.0521035
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00025 def-00009

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.19825; after=0.190239; delta=-0.00801011; latency_delta=-2.45; trusted_stale_delta=0.0625; priority_delta=-0.0521035
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00027 def-00010

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.971653; threshold=0.75; active_defense_until=200
- Event link: linked
- Metrics: before=0.176793; after=0.201798; delta=0.0250046; latency_delta=-0.9; trusted_stale_delta=0.0625; priority_delta=-0.0400741
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00031 def-00011

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.190239; after=0.159966; delta=-0.0302738; latency_delta=-4.95; trusted_stale_delta=0; priority_delta=-0.0278809
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00031 def-00012

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.190239; after=0.159966; delta=-0.0302738; latency_delta=-4.95; trusted_stale_delta=0; priority_delta=-0.0278809
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00032 def-00013

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.96213; threshold=0.75; active_defense_until=225
- Event link: linked
- Metrics: before=0.187877; after=0.155665; delta=-0.0322123; latency_delta=-5.4; trusted_stale_delta=0; priority_delta=-0.0257579
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00017 ml-atk-00003

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.918255; expected_mission_impact=0.970755; target=LTE; reason=ML impact predictor selected queue_pressure
- Event link: linked
- Metrics: before=0.201798@t=160; peak=0.201798; after=0.125012@t=240; delta=-0.076786; peak_latency=7.75; peak_trusted_stale=0.125; peak_priority_inversion=0.0960961
- Attribution/outcome: response=complete; outcome=contained after peak degradation; reduction_from_peak=0.05886
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00033 def-00014

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.201798; after=0.147949; delta=-0.053849; latency_delta=-6.3; trusted_stale_delta=0; priority_delta=-0.0236979
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00033 def-00015

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.201798; after=0.147949; delta=-0.053849; latency_delta=-6.3; trusted_stale_delta=0; priority_delta=-0.0236979
- Attribution/outcome: observed_effect=improved; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00037 def-00016

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.959167; threshold=0.75; active_defense_until=250
- Event link: linked
- Metrics: before=0.159966; after=0.141337; delta=-0.0186291; latency_delta=-1.8; trusted_stale_delta=0; priority_delta=-0.0132583
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00037 def-00017

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.159966; after=0.141337; delta=-0.0186291; latency_delta=-1.8; trusted_stale_delta=0; priority_delta=-0.0132583
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00038 def-00018

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.155665; after=0.140496; delta=-0.0151687; latency_delta=-1.35; trusted_stale_delta=0; priority_delta=-0.0123373
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00039 def-00019

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.147949; after=0.109026; delta=-0.0389228; latency_delta=0.15; trusted_stale_delta=-0.0625; priority_delta=-0.0110955
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00042 def-00020

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.957447; threshold=0.75; active_defense_until=275
- Event link: linked
- Metrics: before=0.142014; after=0.143536; delta=0.00152214; latency_delta=1; trusted_stale_delta=0; priority_delta=-0.0102891
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00022 ml-atk-00004

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.745517; expected_mission_impact=0.820517; target=MESH; reason=ML impact predictor selected failover_chasing
- Event link: linked
- Metrics: before=0.141337@t=210; peak=0.157241; after=0.155822@t=280; delta=0.0144856; peak_latency=2; peak_trusted_stale=0.125; peak_priority_inversion=0.0651731
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.0205729
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00043 def-00021

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.141337; after=0.125012; delta=-0.0163245; latency_delta=1; trusted_stale_delta=-0.0625; priority_delta=-0.0105656
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00044 def-00022

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.140496; after=0.124242; delta=-0.0162537; latency_delta=1; trusted_stale_delta=-0.0625; priority_delta=-0.0104241
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00045 def-00023

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.109026; after=0.123725; delta=0.0146983; latency_delta=0.4; trusted_stale_delta=0; priority_delta=-0.00927016
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00047 def-00024

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.934522; threshold=0.75; active_defense_until=300
- Event link: linked
- Metrics: before=0.144298; after=0.157241; delta=0.012943; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00744727
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00049 def-00025

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.125012; after=0.156548; delta=0.0315361; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00567784
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00049 def-00026

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.125012; after=0.156548; delta=0.0315361; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00567784
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00050 def-00027

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.124242; after=0.156143; delta=0.0319012; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00494769
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00052 def-00028

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.915386; threshold=0.75; active_defense_until=325
- Event link: linked
- Metrics: before=0.123349; after=0.155544; delta=0.0321944; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00436123
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: ml_window_triggered
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00052 def-00029

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.123349; after=0.155544; delta=0.0321944; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00436123
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00027 ml-atk-00005

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.744854; expected_mission_impact=0.819854; target=LTE; reason=ML impact predictor selected failover_chasing
- Event link: linked
- Metrics: before=0.157241@t=260; peak=0.157241; after=0.154619@t=300; delta=-0.00262202; peak_latency=2; peak_trusted_stale=0.125; peak_priority_inversion=0.0503145
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.00262202
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00055 def-00030

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.156548; after=0.154619; delta=-0.00192962; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00385924
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00057 def-00031

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.963056; threshold=0.75; active_defense_until=350
- Event link: linked
- Metrics: before=0.155822; after=0.154619; delta=-0.00120366; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00240732
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00059 def-00032

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.155205; after=0.154619; delta=-0.000586176; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00117235
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00061 def-00033

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.154619; after=0.154619; delta=0; latency_delta=0; trusted_stale_delta=0; priority_delta=0
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none
