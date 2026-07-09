# 최종 재현 QA

## 목적

최종 제출 직전 상태가 실제로 재현 가능한지 확인한다. 검증 범위는 코드 컴파일, README Full Reproduction 실행, 핵심 산출물 row count, 제출 ZIP 구성, ZIP 제외 규칙, Git 브랜치 상태다.

## 실행 명령

```bash
python3 -m src.ml.build_dataset --rows 3000
python3 -m src.ml.train_aura_impact_model
python3 -m src.ml.train_tsra_detector --rows 5000
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
python3 -m src.experiments.validate_event_contracts --fail-on-error
python3 -m src.experiments.trace_quality_audit --fail-on-error
python3 -m src.experiments.agent_loop_replay
python3 -m src.experiments.agent_decision_causality_audit
python3 -m src.experiments.agent_decision_margin_audit
python3 -m src.experiments.agent_memory_belief_audit
python3 -m src.experiments.agent_tool_usage_audit
python3 -m src.experiments.agent_interface_manifest
python3 -m src.experiments.agent_capability_matrix
python3 -m src.experiments.battle_timeline
python3 -m src.experiments.incident_summary
python3 -m src.experiments.operator_alerts
python3 -m src.experiments.defense_effectiveness_ledger
python3 -m src.experiments.aura_coa_cards
python3 -m src.experiments.run_tsra_ablation
python3 -m src.experiments.run_adaptive_memory
python3 -m src.experiments.run_batch
python3 -m src.experiments.metric_gate --fail-on-error
python3 -m src.experiments.attack_defense_coverage
python3 -m src.experiments.attack_defense_response_audit
python3 -m src.experiments.closed_loop_episode_replay
python3 -m src.experiments.agent_engagement_scorecard
python3 -m src.experiments.pace_transition_audit
python3 -m src.experiments.mission_impact_decomposition
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 -m src.experiments.agent_collaboration_graph
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/build_submission_package.py
python3 scripts/generate_release_handoff.py
python3 scripts/freeze_release_candidate.py
python3 scripts/verify_submission_state.py
python3 scripts/verify_external_package_link.py "file://$(pwd)/outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip" --allow-file-url
```

## 검증 결과

Full Reproduction은 끝까지 통과했다.

핵심 산출물:

```text
experiment_summary rows: 7
repeated_experiment_summary rows: 7
resilience_gain_summary rows: 4
tsra_action_ablation_summary rows: 5
adaptive_memory_summary conditions: full_tsra_r, adaptive_tsra_r
metric_gate_summary rows: 11 pass
agent_decision_trace_summary rows: 215
agent_contract_validation rows: 49 pass
decision_trace_quality_audit rows: 9 pass
agent_loop_replay rows: 8
agent_decision_causality_audit rows: 399 pass
agent_decision_margin_audit rows: 399 pass
agent_memory_belief_audit rows: 9 pass
agent_tool_usage_audit rows: 23 pass
agent_interface_manifest rows: 4
agent_capability_matrix rows: 10
attack_defense_coverage rows: 4 covered
attack_defense_response_audit rows: 10 no missed required
pace_transition_audit rows: 6 status=2 initial/4 fallback
mission_impact_decomposition rows: 35 components=5
submission_readiness_audit rows: 10 pass
aura_coa_cards rows: 15
battle_timeline rows: 49
incident_summary rows: 10
operator_alerts rows: 56 actions=5
defense_effectiveness_ledger rows: 56 actions=5
closed_loop_episode_replay rows: 10 complete
agent_engagement_scorecard rows: 10 pass
agent_collaboration_graph edges: 17 verified
competition_alignment_matrix rows: 10 verified
```

패키지 검증:

```text
package_zip entries: 168
package_manifest_integrity: passed
package_zip_metadata: deterministic
release_handoff: repo-only/current
generated_branch: hbin
freeze_status: pass
package exclusions: passed
external_package_link_self_test: pass
excluded __pycache__: 0
excluded *.pyc: 0
excluded outputs/tmp*: 0
excluded outputs/datasets/: 0
excluded *.pkl/*.pt: 0
excluded outputs/batch/seed_*: 0
```

Git 검증:

```text
branch: hbin
origin/main: present
origin/hbin: present
```

## 판단

현재 `hbin` 브랜치 산출물은 README 기준으로 재현 가능하고, 제출 ZIP은 코드, 문서, 요약 CSV, figure, report table, model metric JSON 중심으로 구성된다. 실제 RF, exploit, live network action은 포함하지 않는다.
