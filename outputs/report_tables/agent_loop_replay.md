# Agent Loop Replay

This replay reconstructs representative observe-memory-tool-candidate-decision-feedback loops.

Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action

## Replay-01: E5_rule_aura_tsra_r / AURA / no_op

- Policy: `rule_attack_score`
- Trace: `aura-trace-00001` at t=0 sec
- Observe: phase=normal_patrol; active_link=SATCOM; critical_pending=0; queue_kb=32.024; video_kb=0; stale=0; priority_inversion=0
- Memory: observations=1; decisions=0; last_selected=
- Tools: none
- Candidates: none
- Selected action: no_op
- Feedback: attack_threshold=0.12; cooldown_sec=45; event_count=0
- Reason: waiting for min_start_sec=60.0
- Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action

## Replay-02: E5_rule_aura_tsra_r / AURA / action

- Policy: `rule_attack_score`
- Trace: `aura-trace-00007` at t=60 sec
- Observe: phase=normal_patrol; active_link=SATCOM; critical_pending=0; queue_kb=32.155; video_kb=0; stale=0.5; priority_inversion=0.1935
- Memory: observations=7; decisions=6; last_selected=no_op; event_count=1; last_attack_type=queue_pressure
- Tools: generate_attack_candidates -> items=4; estimate_candidate_effectx4 -> mission_impact=0.424215; estimate_detectabilityx4 -> 0.2
- Candidates: queue_pressure; score=0.543691; impact=0.566191; detectability=0.15; target=SATCOM || bandwidth_limit; score=0.434227; impact=0.456727; detectability=0.15; target=SATCOM || stale_cop_induction; score=0.41456; impact=0.46706; detectability=0.35; target=SATCOM; total=4
- Selected action: attack_event; atk-00001; queue_pressure; target=SATCOM; score=0.543691
- Feedback: attack_threshold=0.12; cooldown_sec=45
- Reason: increase non-critical queue occupancy
- Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action

## Replay-03: E5_rule_aura_tsra_r / TSRA-R / no_op

- Policy: `rule_defense_full`
- Trace: `tsra-r-trace-00001` at t=0 sec
- Observe: phase=normal_patrol; active_link=SATCOM; critical_pending=0; queue_kb=32.024; video_kb=0; stale=0; priority_inversion=0
- Memory: observations=1; decisions=0; last_selected=; mode=full; event_count=0; enabled_actions=pace_switch,priority_reroute,stale_badge,video_throttle
- Tools: evaluate_defense_conditions -> priority_reroute_needed=False; stale_badge_needed=False; pace_switch_needed=False; video_throttle_needed=False
- Candidates: priority_reroute; eligible=False; ready=True; enabled=True || video_throttle; eligible=False; ready=True; enabled=True || stale_badge; eligible=False; ready=True; enabled=True; total=4
- Selected action: no_op
- Feedback: event_count=0; mode=full; enabled_actions=pace_switch,priority_reroute,stale_badge,video_throttle
- Reason: no defense action emitted
- Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action

## Replay-04: E5_rule_aura_tsra_r / TSRA-R / action

- Policy: `rule_defense_full`
- Trace: `tsra-r-trace-00005` at t=20 sec
- Observe: phase=normal_patrol; active_link=SATCOM; critical_pending=0; queue_kb=0; video_kb=0; stale=0.5; priority_inversion=0.15
- Memory: observations=5; decisions=4; last_selected=no_op; mode=full; event_count=1; enabled_actions=pace_switch,priority_reroute,stale_badge,video_throttle
- Tools: evaluate_defense_conditions -> priority_reroute_needed=False; stale_badge_needed=True; pace_switch_needed=False; video_throttle_needed=False
- Candidates: stale_badge; eligible=True; ready=True; enabled=True || priority_reroute; eligible=False; ready=True; enabled=True || video_throttle; eligible=False; ready=True; enabled=True; total=4
- Selected action: defense_events: def-00001; stale_badge; until=110
- Feedback: event_count=1; mode=full; enabled_actions=pace_switch,priority_reroute,stale_badge,video_throttle
- Reason: emitted 1 defense event(s)
- Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action

## Replay-05: E7_ml_aura_ml_tsra_r / AURA-ML / no_op

- Policy: `ml_impact_predictor`
- Trace: `aura-ml-trace-00001` at t=0 sec
- Observe: phase=normal_patrol; active_link=SATCOM; critical_pending=0; queue_kb=32.024; video_kb=0; stale=0; priority_inversion=0
- Memory: observations=1; decisions=0; last_selected=
- Tools: none
- Candidates: none
- Selected action: no_op
- Feedback: attack_threshold=0.12; cooldown_sec=45; event_count=0
- Reason: waiting for min_start_sec=60.0
- Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action

## Replay-06: E7_ml_aura_ml_tsra_r / AURA-ML / action

- Policy: `ml_impact_predictor`
- Trace: `aura-ml-trace-00007` at t=60 sec
- Observe: phase=normal_patrol; active_link=SATCOM; critical_pending=0; queue_kb=32.155; video_kb=0; stale=0.5; priority_inversion=0.1935
- Memory: observations=7; decisions=6; last_selected=no_op; event_count=1; last_attack_type=queue_pressure
- Tools: generate_attack_candidates -> items=4; predict_candidate_impactx4 -> 0.4914; estimate_candidate_effectx4 -> mission_impact=0.424215; estimate_detectabilityx4 -> 0.2
- Candidates: queue_pressure; score=0.579505; impact=0.602005; detectability=0.15; target=SATCOM || bandwidth_limit; score=0.506702; impact=0.529202; detectability=0.15; target=SATCOM || stale_cop_induction; score=0.48621; impact=0.53871; detectability=0.35; target=SATCOM; total=4
- Selected action: attack_event; ml-atk-00001; queue_pressure; target=SATCOM; score=0.579505
- Feedback: attack_threshold=0.12; cooldown_sec=45
- Reason: ML impact predictor selected queue_pressure
- Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action

## Replay-07: E7_ml_aura_ml_tsra_r / TSRA-R-ML / no_op

- Policy: `ml_anomaly_detector`
- Trace: `tsra-r-ml-trace-00001` at t=0 sec
- Observe: phase=normal_patrol; active_link=SATCOM; critical_pending=0; queue_kb=32.024; video_kb=0; stale=0; priority_inversion=0
- Memory: observations=1; decisions=0; last_selected=; last_probability=0.282859; active_defense_until=0
- Tools: predict_attack_probability -> 0.282859; assess_mission_risk_guard -> had_prior_window=False; near_or_after_window_end=True; open_window=False
- Candidates: open_defense_window; probability=0.282859; threshold=0.75; eligible=False; total=1
- Selected action: no_op
- Feedback: event_count=0; active_defense_until=0
- Reason: probability below threshold and no active defense window
- Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action

## Replay-08: E7_ml_aura_ml_tsra_r / TSRA-R-ML / action

- Policy: `ml_anomaly_detector`
- Trace: `tsra-r-ml-trace-00017` at t=80 sec
- Observe: phase=normal_patrol; active_link=SATCOM; critical_pending=1; queue_kb=9400.7; video_kb=8962.41; stale=0.5; priority_inversion=0.3678
- Memory: observations=17; decisions=16; last_selected=no_op; last_probability=0.946005; active_defense_until=150
- Tools: predict_attack_probability -> 0.946005; assess_mission_risk_guard -> had_prior_window=False; near_or_after_window_end=True; open_window=False
- Candidates: open_defense_window; probability=0.946005; threshold=0.75; eligible=True; total=1
- Selected action: defense_events: def-00001; ml_attack_alert; probability=0.946005; until=150 + def-00002; priority_reroute; until=150 + def-00003; video_throttle; until=140 + def-00004; stale_badge; until=170 + def-00005; pace_switch; until=180
- Feedback: event_count=5; active_defense_until=150
- Reason: detector opened or maintained defense window
- Safety boundary: closed simulation agent-loop replay only; no RF, exploit, or live network action
