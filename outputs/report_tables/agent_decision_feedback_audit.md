# Agent Decision Feedback Audit

This audit links selected DecisionTrace events in the defended E5/E7 closed-loop runs to event logs, metric feedback, closed-loop outcomes, and defense action attribution.
Safety boundary: closed simulation decision-feedback audit only; no RF, exploit, or live network action

## Summary

- Feedback rows: 62
- Status counts: pass=62
- Event type counts: attack_event=10, defense_event=52
- Feedback classes: attack_contained_by_defense=5, attack_pressure_observed=5, defense_bounded_or_lagged=7, defense_held=26, defense_improved=17, ml_window_triggered=2

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
| E5_rule_aura_tsra_r | tsra-r-trace-00028 | def-00009 | defense_event | video_throttle | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00029 | def-00010 | defense_event | stale_badge | defense_bounded_or_lagged | pass |
| E5_rule_aura_tsra_r | aura-trace-00017 | atk-00003 | attack_event | queue_pressure | attack_contained_by_defense | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00035 | def-00011 | defense_event | video_throttle | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00035 | def-00012 | defense_event | stale_badge | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00036 | def-00013 | defense_event | priority_reroute | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00041 | def-00014 | defense_event | priority_reroute | defense_improved | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00041 | def-00015 | defense_event | stale_badge | defense_improved | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00042 | def-00016 | defense_event | video_throttle | defense_improved | pass |
| E5_rule_aura_tsra_r | aura-trace-00022 | atk-00004 | attack_event | queue_pressure | attack_contained_by_defense | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00049 | def-00017 | defense_event | video_throttle | defense_bounded_or_lagged | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00050 | def-00018 | defense_event | priority_reroute | defense_bounded_or_lagged | pass |
| E5_rule_aura_tsra_r | aura-trace-00027 | atk-00005 | attack_event | queue_pressure | attack_pressure_observed | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00054 | def-00019 | defense_event | stale_badge | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00055 | def-00020 | defense_event | priority_reroute | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00056 | def-00021 | defense_event | video_throttle | defense_held | pass |
| E5_rule_aura_tsra_r | tsra-r-trace-00060 | def-00022 | defense_event | stale_badge | defense_held | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00007 | ml-atk-00001 | attack_event | queue_pressure | attack_contained_by_defense | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00015 | def-00001 | defense_event | priority_reroute | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00015 | def-00002 | defense_event | video_throttle | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00015 | def-00003 | defense_event | stale_badge | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00015 | def-00004 | defense_event | pace_switch | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00017 | def-00005 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00022 | def-00006 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00022 | def-00007 | defense_event | priority_reroute | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00022 | def-00008 | defense_event | video_throttle | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00022 | def-00009 | defense_event | stale_badge | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00012 | ml-atk-00002 | attack_event | failover_chasing | attack_pressure_observed | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00027 | def-00010 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00027 | def-00011 | defense_event | priority_reroute | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00029 | def-00012 | defense_event | video_throttle | defense_bounded_or_lagged | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00031 | def-00013 | defense_event | pace_switch | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00032 | def-00014 | defense_event | ml_attack_alert | ml_window_triggered | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00017 | ml-atk-00003 | attack_event | failover_chasing | attack_contained_by_defense | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00033 | def-00015 | defense_event | stale_badge | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00036 | def-00016 | defense_event | priority_reroute | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00039 | def-00017 | defense_event | stale_badge | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00042 | def-00018 | defense_event | video_throttle | defense_held | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00022 | ml-atk-00004 | attack_event | queue_pressure | attack_pressure_observed | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00045 | def-00019 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00045 | def-00020 | defense_event | priority_reroute | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00048 | def-00021 | defense_event | stale_badge | defense_improved | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00049 | def-00022 | defense_event | video_throttle | defense_bounded_or_lagged | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00050 | def-00023 | defense_event | ml_attack_alert | ml_window_triggered | pass |
| E7_ml_aura_ml_tsra_r | aura-ml-trace-00027 | ml-atk-00005 | attack_event | stale_cop_induction | attack_pressure_observed | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00053 | def-00024 | defense_event | priority_reroute | defense_bounded_or_lagged | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00053 | def-00025 | defense_event | pace_switch | defense_bounded_or_lagged | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00055 | def-00026 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00055 | def-00027 | defense_event | stale_badge | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00056 | def-00028 | defense_event | video_throttle | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00060 | def-00029 | defense_event | ml_attack_alert | defense_held | pass |
| E7_ml_aura_ml_tsra_r | tsra-r-ml-trace-00061 | def-00030 | defense_event | stale_badge | defense_held | pass |

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
- Metrics: before=0.0975179@t=110; peak=0.115123; after=0.113727@t=190; delta=0.0162091; peak_latency=2; peak_trusted_stale=0.125; peak_priority_inversion=0.0742857
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.0194333
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00026 def-00008

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.0859692; after=0.0770536; delta=-0.00891563; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.0178313
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00028 def-00009

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.0822366; after=0.109699; delta=0.0274619; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.0138263
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00029 def-00010

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.08084; after=0.11201; delta=0.0311704; latency_delta=0.45; trusted_stale_delta=0.0625; priority_delta=-0.0124092
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r aura-trace-00017 atk-00003

- Agent: AURA policy=rule_attack_score
- Decision: score=0.9775; expected_mission_impact=1; target=LTE; reason=increase non-critical queue occupancy
- Event link: linked
- Metrics: before=0.110655@t=160; peak=0.115123; after=0.0745913@t=240; delta=-0.0360634; peak_latency=2; peak_trusted_stale=0.125; peak_priority_inversion=0.0371429
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.0021496
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00035 def-00011

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.11201; after=0.112973; delta=0.000962778; latency_delta=0.55; trusted_stale_delta=0; priority_delta=-0.00540778
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00035 def-00012

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.11201; after=0.112973; delta=0.000962778; latency_delta=0.55; trusted_stale_delta=0; priority_delta=-0.00540778
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00036 def-00013

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.115123; after=0.112639; delta=-0.00248391; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00496781
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00041 def-00014

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.112973; after=0.0768033; delta=-0.0361699; latency_delta=0; trusted_stale_delta=-0.0625; priority_delta=-0.00358979
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00041 def-00015

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.112973; after=0.0768033; delta=-0.0361699; latency_delta=0; trusted_stale_delta=-0.0625; priority_delta=-0.00358979
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00042 def-00016

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.112639; after=0.0762597; delta=-0.0363792; latency_delta=-0.05; trusted_stale_delta=-0.0625; priority_delta=-0.00334169
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r aura-trace-00022 atk-00004

- Agent: AURA policy=rule_attack_score
- Decision: score=0.9475; expected_mission_impact=1; target=LTE; reason=increase non-critical queue occupancy
- Event link: linked
- Metrics: before=0.112348@t=210; peak=0.112348; after=0.104037@t=290; delta=-0.00831093; peak_latency=2; peak_trusted_stale=0.125; peak_priority_inversion=0.0271967
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.0395898
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00049 def-00017

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.0745913; after=0.105722; delta=0.0311303; latency_delta=-0.3; trusted_stale_delta=0.0625; priority_delta=-0.0024894
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00050 def-00018

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.0736488; after=0.1052; delta=0.0315514; latency_delta=-0.25; trusted_stale_delta=0.0625; priority_delta=-0.00231396
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r aura-trace-00027 atk-00005

- Agent: AURA policy=rule_attack_score
- Decision: score=0.9035; expected_mission_impact=0.956; target=LTE; reason=increase non-critical queue occupancy
- Event link: linked
- Metrics: before=0.0717066@t=260; peak=0.105899; after=0.103756@t=300; delta=0.0320493; peak_latency=1.45; peak_trusted_stale=0.125; peak_priority_inversion=0.0219966
- Attribution/outcome: response=complete; outcome=covered with residual mission impact; reduction_from_peak=0.00214269
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00054 def-00019

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.105899; after=0.103872; delta=-0.00202615; latency_delta=-0.15; trusted_stale_delta=0; priority_delta=-0.0020523
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00055 def-00020

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=critical traffic waiting behind video load
- Event link: linked
- Metrics: before=0.105722; after=0.103756; delta=-0.00196568; latency_delta=-0.15; trusted_stale_delta=0; priority_delta=-0.00193136
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00056 def-00021

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=protect critical traffic capacity
- Event link: linked
- Metrics: before=0.1052; after=0.103756; delta=-0.00144421; latency_delta=-0.1; trusted_stale_delta=0; priority_delta=-0.00155508
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E5_rule_aura_tsra_r tsra-r-trace-00060 def-00022

- Agent: TSRA-R policy=rule_defense_full
- Decision: eligible=True; ready=True; enabled=True; reason=mark stale COP objects as lower trust
- Event link: linked
- Metrics: before=0.103872; after=0.103756; delta=-0.000116538; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.000233075
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00007 ml-atk-00001

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.579505; expected_mission_impact=0.602005; target=SATCOM; reason=ML impact predictor selected queue_pressure
- Event link: linked
- Metrics: before=0.376905@t=60; peak=0.383116; after=0.0931561@t=140; delta=-0.283749; peak_latency=4.9; peak_trusted_stale=0.5; peak_priority_inversion=0.234568
- Attribution/outcome: response=complete; outcome=contained after peak degradation; reduction_from_peak=0.251649
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00015 def-00001

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=mission risk guard opened or maintained defense window
- Event link: linked
- Metrics: before=0.209367; after=0.131467; delta=-0.0779006; latency_delta=1.5; trusted_stale_delta=-0.0625; priority_delta=-0.107051
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00015 def-00002

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=mission risk guard opened or maintained defense window
- Event link: linked
- Metrics: before=0.209367; after=0.131467; delta=-0.0779006; latency_delta=1.5; trusted_stale_delta=-0.0625; priority_delta=-0.107051
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00015 def-00003

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=mission risk guard opened or maintained defense window
- Event link: linked
- Metrics: before=0.209367; after=0.131467; delta=-0.0779006; latency_delta=1.5; trusted_stale_delta=-0.0625; priority_delta=-0.107051
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00015 def-00004

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=mission risk guard opened or maintained defense window
- Event link: linked
- Metrics: before=0.209367; after=0.131467; delta=-0.0779006; latency_delta=1.5; trusted_stale_delta=-0.0625; priority_delta=-0.107051
- Attribution/outcome: observed_effect=improved; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00017 def-00005

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.955265; threshold=0.75; active_defense_until=150
- Event link: linked
- Metrics: before=0.20656; after=0.114622; delta=-0.0919379; latency_delta=-3.3; trusted_stale_delta=-0.0625; priority_delta=-0.0711258
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00022 def-00006

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.961885; threshold=0.75; active_defense_until=175
- Event link: linked
- Metrics: before=0.16109; after=0.0954067; delta=-0.0656828; latency_delta=-1.5; trusted_stale_delta=-0.0625; priority_delta=-0.0426156
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00022 def-00007

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.16109; after=0.0954067; delta=-0.0656828; latency_delta=-1.5; trusted_stale_delta=-0.0625; priority_delta=-0.0426156
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00022 def-00008

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.16109; after=0.0954067; delta=-0.0656828; latency_delta=-1.5; trusted_stale_delta=-0.0625; priority_delta=-0.0426156
- Attribution/outcome: observed_effect=improved; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00022 def-00009

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.16109; after=0.0954067; delta=-0.0656828; latency_delta=-1.5; trusted_stale_delta=-0.0625; priority_delta=-0.0426156
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00012 ml-atk-00002

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.841848; expected_mission_impact=0.836848; target=LTE; reason=ML impact predictor selected failover_chasing
- Event link: linked
- Metrics: before=0.114622@t=110; peak=0.137802; after=0.133684@t=180; delta=0.0190628; peak_latency=1.3; peak_trusted_stale=0.125; peak_priority_inversion=0.109827
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.025868
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00027 def-00010

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.972249; threshold=0.75; active_defense_until=200
- Event link: linked
- Metrics: before=0.132338; after=0.137802; delta=0.00546442; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.0224045
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00027 def-00011

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.132338; after=0.137802; delta=0.00546442; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.0224045
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00029 def-00012

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.0931561; after=0.135511; delta=0.0423545; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.0173744
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00031 def-00013

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.10647; after=0.133684; delta=0.0272148; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.0143204
- Attribution/outcome: observed_effect=held; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00032 def-00014

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.966892; threshold=0.75; active_defense_until=225
- Event link: linked
- Metrics: before=0.104824; after=0.136195; delta=0.0313713; latency_delta=0.5; trusted_stale_delta=0.0625; priority_delta=-0.0126741
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: ml_window_triggered
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00017 ml-atk-00003

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.817403; expected_mission_impact=0.822403; target=MESH; reason=ML impact predictor selected failover_chasing
- Event link: linked
- Metrics: before=0.137802@t=160; peak=0.13899; after=0.100118@t=230; delta=-0.037684; peak_latency=2; peak_trusted_stale=0.125; peak_priority_inversion=0.058104
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.00132496
- Class: attack_contained_by_defense
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00033 def-00015

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.137802; after=0.13899; delta=0.00118788; latency_delta=1; trusted_stale_delta=0; priority_delta=-0.0109576
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00036 def-00016

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.134565; after=0.137057; delta=0.00249154; latency_delta=1; trusted_stale_delta=0; priority_delta=-0.00835025
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00039 def-00017

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=active defense window maintained while downstream rule actions were evaluated
- Event link: linked
- Metrics: before=0.13899; after=0.101084; delta=-0.037906; latency_delta=0; trusted_stale_delta=-0.0625; priority_delta=-0.00706201
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00042 def-00018

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=active defense window maintained while downstream rule actions were evaluated
- Event link: linked
- Metrics: before=0.137057; after=0.134081; delta=-0.00297604; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00595209
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00022 ml-atk-00004

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.779372; expected_mission_impact=0.801872; target=MESH; reason=ML impact predictor selected queue_pressure
- Event link: linked
- Metrics: before=0.136148@t=210; peak=0.14835; after=0.147139@t=290; delta=0.0109912; peak_latency=2; peak_trusted_stale=0.125; peak_priority_inversion=0.0421286
- Attribution/outcome: response=complete; outcome=held near attack-time impact; reduction_from_peak=0.0375459
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00045 def-00019

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.88058; threshold=0.75; active_defense_until=290
- Event link: linked
- Metrics: before=0.101084; after=0.0986017; delta=-0.00248212; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00496424
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00045 def-00020

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.101084; after=0.0986017; delta=-0.00248212; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00496424
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00048 def-00021

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.134081; after=0.114288; delta=-0.019793; latency_delta=0; trusted_stale_delta=-0.0625; priority_delta=-0.00416928
- Attribution/outcome: observed_effect=improved; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_improved
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00049 def-00022

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.0993461; after=0.14835; delta=0.0490044; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00407462
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00050 def-00023

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.936032; threshold=0.75; active_defense_until=315
- Event link: linked
- Metrics: before=0.0990341; after=0.14805; delta=0.0490156; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00405208
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: ml_window_triggered
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r aura-ml-trace-00027 ml-atk-00005

- Agent: AURA-ML policy=ml_impact_predictor
- Decision: score=0.779393; expected_mission_impact=0.661893; target=MESH; reason=ML impact predictor selected stale_cop_induction
- Event link: linked
- Metrics: before=0.114642@t=260; peak=0.14835; after=0.146587@t=300; delta=0.0319448; peak_latency=2; peak_trusted_stale=0.125; peak_priority_inversion=0.0338681
- Attribution/outcome: response=complete; outcome=covered with residual mission impact; reduction_from_peak=0.00176331
- Class: attack_pressure_observed
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00053 def-00024

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.114642; after=0.147139; delta=0.0324964; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00375716
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=ablation_supported; attribution_status=pass; primary_metric=priority_inversion_rate
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00053 def-00025

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.114642; after=0.147139; delta=0.0324964; latency_delta=0; trusted_stale_delta=0.0625; priority_delta=-0.00375716
- Attribution/outcome: observed_effect=degraded_or_delayed; attribution_class=bounded_tradeoff_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_bounded_or_lagged
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00055 def-00026

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.930785; threshold=0.75; active_defense_until=340
- Event link: linked
- Metrics: before=0.14835; after=0.146587; delta=-0.00176331; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00352661
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00055 def-00027

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.14835; after=0.146587; delta=-0.00176331; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00352661
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00056 def-00028

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.14805; after=0.146587; delta=-0.00146257; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.00292514
- Attribution/outcome: observed_effect=held; attribution_class=local_metric_supported; attribution_status=pass; primary_metric=p95_critical_latency_sec
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00060 def-00029

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: probability=0.9331; threshold=0.75; active_defense_until=365
- Event link: linked
- Metrics: before=0.146858; after=0.146587; delta=-0.000270678; latency_delta=0; trusted_stale_delta=0; priority_delta=-0.000541356
- Attribution/outcome: observed_effect=held; attribution_class=reactive_window_supported; attribution_status=pass; primary_metric=mission_impact
- Class: defense_held
- Status: pass
- Issues: none

### E7_ml_aura_ml_tsra_r tsra-r-ml-trace-00061 def-00030

- Agent: TSRA-R-ML policy=ml_anomaly_detector
- Decision: reason=detector opened or maintained defense window
- Event link: linked
- Metrics: before=0.146587; after=0.146587; delta=0; latency_delta=0; trusted_stale_delta=0; priority_delta=0
- Attribution/outcome: observed_effect=held; attribution_class=ablation_supported; attribution_status=pass; primary_metric=trusted_stale_exposure
- Class: defense_held
- Status: pass
- Issues: none
