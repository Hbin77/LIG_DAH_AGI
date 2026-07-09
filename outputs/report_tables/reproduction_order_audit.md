# Reproduction Order Audit

This audit checks that README Full Reproduction commands are ordered so generated evidence does not depend on stale downstream files.
Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 13
- Status counts: pass=13

| check_id | command_index | command | order_status | output_status | status |
|---|---:|---|---|---|---|
| RO01 | 29 | python3 -m src.experiments.defense_action_attribution_audit --fail-on-error | pass | pass | pass |
| RO02 | 34 | python3 -m src.experiments.closed_loop_episode_replay | pass | pass | pass |
| RO03 | 35 | python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error | pass | pass | pass |
| RO04 | 36 | python3 -m src.experiments.agent_engagement_scorecard | pass | pass | pass |
| RO05 | 37 | python3 -m src.experiments.mission_thread_summary --fail-on-error | pass | pass | pass |
| RO06 | 41 | python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error | pass | pass | pass |
| RO07 | 42 | python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error | pass | pass | pass |
| RO08 | 43 | python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error | pass | pass | pass |
| RO09 | 44 | python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error | pass | pass | pass |
| RO10 | 49 | python3 -m src.experiments.competition_alignment --fail-on-incomplete | pass | pass | pass |
| RO11 | 50 | python3 scripts/build_submission_package.py | pass | pass | pass |
| RO12 | 51 | python3 scripts/generate_release_handoff.py | pass | pass | pass |
| RO13 | 53 | python3 scripts/verify_submission_state.py | pass | pass | pass |

## Detail

### RO01

- Command: `python3 -m src.experiments.defense_action_attribution_audit --fail-on-error`
- Required before: python3 -m src.experiments.defense_effectiveness_ledger | python3 -m src.experiments.run_tsra_ablation | python3 -m src.experiments.reactive_defense_tradeoff_audit --fail-on-error
- Output files: outputs/report_tables/defense_action_attribution_audit.csv | outputs/report_tables/defense_action_attribution_audit.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: Defense attribution needs event-level ledger evidence, ablation evidence, and reactive-window evidence before it can classify all TSRA-R actions.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO02

- Command: `python3 -m src.experiments.closed_loop_episode_replay`
- Required before: python3 -m src.experiments.attack_defense_response_audit | python3 -m src.experiments.operator_alerts | python3 -m src.experiments.defense_effectiveness_ledger
- Output files: outputs/report_tables/closed_loop_episode_replay.csv | outputs/report_tables/closed_loop_episode_replay.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: Closed-loop replay must run after response coverage, operator alert, and defense effectiveness evidence exist.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO03

- Command: `python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error`
- Required before: python3 -m src.experiments.attack_defense_response_audit | python3 -m src.experiments.closed_loop_episode_replay | python3 -m src.experiments.operator_alerts
- Output files: outputs/report_tables/agent_coordination_latency_audit.csv | outputs/report_tables/agent_coordination_latency_audit.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: Coordination latency is only meaningful after episode replay and response evidence have been regenerated.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO04

- Command: `python3 -m src.experiments.agent_engagement_scorecard`
- Required before: python3 -m src.experiments.closed_loop_episode_replay | python3 -m src.experiments.agent_decision_margin_audit | python3 -m src.experiments.defense_effectiveness_ledger
- Output files: outputs/report_tables/agent_engagement_scorecard.csv | outputs/report_tables/agent_engagement_scorecard.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: The engagement scorecard joins closed-loop episodes, attack decision margins, and defense-event metric movement.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO05

- Command: `python3 -m src.experiments.mission_thread_summary --fail-on-error`
- Required before: python3 -m src.experiments.closed_loop_episode_replay | python3 -m src.experiments.agent_engagement_scorecard | python3 -m src.experiments.defense_action_attribution_audit --fail-on-error
- Output files: outputs/report_tables/mission_thread_summary.csv | outputs/report_tables/mission_thread_summary.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: Mission threads should be generated only after replay, scorecard, and action attribution are fresh.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO06

- Command: `python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error`
- Required before: python3 -m src.experiments.agent_engagement_scorecard
- Output files: outputs/report_tables/ml_attack_decision_path_audit.csv | outputs/report_tables/ml_attack_decision_path_audit.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: The ML attack path audit uses engagement scorecard feedback to close the AURA-ML selection loop.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO07

- Command: `python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error`
- Required before: python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error
- Output files: outputs/report_tables/ml_defense_decision_path_audit.csv | outputs/report_tables/ml_defense_decision_path_audit.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: The ML defense path audit uses coordination latency evidence to prove closed-loop response effect.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO08

- Command: `python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error`
- Required before: python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error | python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error | python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error
- Output files: outputs/report_tables/ml_red_blue_interaction_audit.csv | outputs/report_tables/ml_red_blue_interaction_audit.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: The red-blue interaction audit should run after both ML path audits and the shared coordination evidence exist.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO09

- Command: `python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error`
- Required before: python3 -m src.ml.train_tsra_detector --rows 5000 | python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error | python3 -m src.experiments.attack_defense_response_audit
- Output files: outputs/report_tables/agent_stress_scenario_audit.csv | outputs/report_tables/agent_stress_scenario_audit.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: Stress scenario audit should run after detector training, response evidence, and the ML red-blue interaction audit so robustness evidence is generated before final gates.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO10

- Command: `python3 -m src.experiments.competition_alignment --fail-on-incomplete`
- Required before: python3 -m src.experiments.agent_collaboration_graph | python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error | python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error | python3 -m src.experiments.reproduction_order_audit --fail-on-error
- Output files: outputs/report_tables/competition_alignment_matrix.csv | outputs/report_tables/competition_alignment_matrix.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: Competition alignment should be the final evidence matrix after the graph, ML interaction, and reproduction-order checks are generated.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO11

- Command: `python3 scripts/build_submission_package.py`
- Required before: python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete | python3 -m src.experiments.competition_alignment --fail-on-incomplete
- Output files: outputs/package/submission_manifest.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: The package should be built only after readiness and alignment evidence have been regenerated.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO12

- Command: `python3 scripts/generate_release_handoff.py`
- Required before: python3 scripts/build_submission_package.py
- Output files: outputs/package/release_handoff.md
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: The handoff records package metadata, so it must run after package generation.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action

### RO13

- Command: `python3 scripts/verify_submission_state.py`
- Required before: python3 scripts/freeze_release_candidate.py
- Output files: not_applicable
- Order status: pass
- Output status: pass
- Status: pass
- Interpretation: Final verification should follow the freeze command so manifest, handoff, package, and link self-test evidence are current.
- Safety boundary: closed simulation reproduction-order audit only; no RF, exploit, or live network action
