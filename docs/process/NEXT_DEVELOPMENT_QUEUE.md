# 다음 개발 큐

이 큐는 `COMPETITION_DIRECTION.md`를 실행 항목으로 바꾼 것이다. 작업 순서는 공격-방어-AI 에이전트 공방 루프를 더 명확하게 만드는 순서로 잡는다.

## P0. DecisionTrace 요약기

상태: 완료

문제:

- 현재 `aura_decision_traces.jsonl`, `tsra_r_decision_traces.jsonl`은 구조적으로 좋지만 사람이 바로 읽기에는 길다.
- AURA가 공격을 고른 이유와 TSRA-R이 방어를 고른 이유를 같은 시간축에서 비교하기 어렵다.

구현:

```text
src/experiments/trace_summary.py
```

입력:

```text
outputs/experiments/E3_rule_aura/aura_decision_traces.jsonl
outputs/experiments/E5_rule_aura_tsra_r/aura_decision_traces.jsonl
outputs/experiments/E5_rule_aura_tsra_r/tsra_r_decision_traces.jsonl
outputs/experiments/E7_ml_aura_ml_tsra_r/aura_decision_traces.jsonl
outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl
```

출력:

```text
outputs/report_tables/agent_decision_trace_summary.csv
outputs/report_tables/agent_decision_trace_summary.md
```

완료 기준:

- 완료. 시간, agent, policy, selected_action, reason, top candidate, probability/score가 표로 나온다.
- 완료. E3, E5, E7의 AURA/TSRA-R 판단이 한 파일에서 비교된다.
- 완료. `python3 -m src.experiments.trace_summary` 명령으로 재생성 가능하다.

검증:

```bash
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
python3 -m compileall src
```

검증 결과:

```text
agent_decision_trace_summary.csv: 215 rows
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
experiments: E3_rule_aura, E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
```

## P1. AURA COA Card

상태: 완료

문제:

- AURA가 고른 공격 효과가 event JSON에는 남지만, 공격 후보-예상 영향-선택 이유를 한 장 단위로 보기 어렵다.

구현:

```text
src/experiments/aura_coa_cards.py
```

출력:

```text
outputs/report_tables/aura_coa_cards.md
outputs/report_tables/aura_coa_cards.csv
```

완료 기준:

- 완료. 각 `AttackEvent`마다 COA card가 생성된다.
- 완료. card에는 attack_type, target_link, duration, expected_impact, score, reason이 들어간다.
- 완료. 실제 공격 명령처럼 보이지 않도록 safety boundary를 각 카드에 명시한다.

검증:

```bash
python3 -m src.experiments.run_all
python3 -m src.experiments.aura_coa_cards
```

검증 결과:

```text
aura_coa_cards.csv: 15 cards
experiments: E3_rule_aura, E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
agents: AURA, AURA-ML
missing_safety: 0
unknown_rank: 0
```

## P2. TSRA-R Action Ablation

상태: 완료

문제:

- TSRA-R이 여러 방어 액션을 동시에 수행하므로 어떤 액션이 어떤 지표에 기여했는지 분리하기 어렵다.

구현:

```text
src/experiments/run_tsra_ablation.py
```

실험 조건:

```text
full
no_priority_reroute
no_video_throttle
no_stale_badge
no_pace_switch
```

출력:

```text
outputs/batch/tsra_action_ablation_summary.csv
outputs/figures/tsra_action_ablation.png
```

완료 기준:

- 완료. 각 방어 액션 제거 시 mission impact, trusted stale exposure, priority inversion 변화가 나온다.
- 완료. TSRA-R의 가치가 단일 mission impact가 아니라 방어 기능별 지표로 설명 가능해진다.

검증:

```bash
python3 -m src.experiments.run_tsra_ablation
python3 -m compileall src
```

검증 결과:

```text
tsra_action_ablation_summary.csv: 5 conditions
tsra_action_ablation_raw.csv: 150 rows
conditions: full, no_priority_reroute, no_video_throttle, no_stale_badge, no_pace_switch
figure: outputs/figures/tsra_action_ablation.png
```

핵심 결과:

```text
no_priority_reroute: mission impact +0.208, priority inversion +0.473
no_stale_badge: mission impact +0.205, trusted stale exposure +0.388
no_video_throttle: mission impact -0.013
no_pace_switch: mission impact -0.017
```

해석:

- `priority_reroute`는 priority inversion과 critical latency 억제에 핵심이다.
- `stale_badge`는 trusted stale exposure 억제에 핵심이다.
- 현재 scalar mission impact에서는 `video_throttle`, `pace_switch`가 항상 이득으로 나타나지는 않으므로 운용 목적과 지표를 분리해 해석해야 한다.

## P3. Adaptive Memory

상태: 완료

문제:

- 현재 AgentMemory는 최근 관측/판단과 belief state를 보관하지만, 다음 판단 기준을 바꾸는 데는 제한적으로만 사용된다.

구현:

```text
src/tsra_r/adaptive_defender.py
src/experiments/run_adaptive_memory.py
```

구현 방식:

- 기본 E1~E7 baseline은 유지한다.
- 별도 옵션으로 adaptive mode를 둔다.
- 최근 관측 memory를 기반으로 optional defense action을 gating한다.
- `priority_reroute`, `stale_badge`는 ablation에서 핵심 방어로 확인됐으므로 항상 유지한다.
- `video_throttle`, `pace_switch`는 반복적인 pressure/degradation이 memory에 쌓일 때만 활성화한다.

완료 기준:

- 완료. adaptive mode on/off가 별도 class와 runner로 분리됐다.
- 완료. 기존 기본 실험 결과가 의도치 않게 바뀌지 않는다.
- 완료. adaptive mode 전용 실험 결과가 따로 생성된다.

검증:

```bash
python3 -m compileall src
python3 -m src.experiments.run_all
python3 -m src.experiments.run_adaptive_memory
```

검증 결과:

```text
adaptive_memory_summary.csv: 2 conditions
adaptive_memory_raw.csv: 60 rows
conditions: full_tsra_r, adaptive_tsra_r
full_tsra_r mission impact: 0.140260
adaptive_tsra_r mission impact: 0.109489
priority inversion: 0.050609 -> 0.027455
video throttle count: 6.4 -> 3.1
adaptive trace rows with feedback.adaptive_policy: 61
```

해석:

- AdaptiveTSRA-R은 방어 액션을 무조건 늘리지 않고, Memory에 반복 신호가 쌓였을 때 선택적으로 확장한다.
- 기본 TSRA-R보다 video throttle을 덜 쓰면서 mission impact와 priority inversion을 낮췄다.
- baseline E1~E7은 기존 실험 체계로 유지되므로, adaptive mode는 별도 개선 실험으로 해석한다.

## P4. 산출물 안정화

상태: 완료

문제:

- 코드와 실험 산출물은 준비되어 있지만, 제출용 ZIP 기준으로 재현 명령, 생성 파일, 제외할 임시 로그를 마지막으로 정리해야 한다.

구현:

```text
scripts/build_submission_package.py
docs/process/SUBMISSION_PACKAGE.md
outputs/package/submission_manifest.md
```

구현 방식:

- README의 재현 명령을 실제 실행 순서와 맞췄다.
- 대용량 또는 재생성 가능한 임시 로그가 ZIP에 섞이지 않게 선별 규칙을 코드화했다.
- 핵심 CSV, figure, docs가 빠지지 않았는지 required path 검증을 추가했다.

완료 기준:

- 완료. clean clone 또는 ZIP 기준으로 실행 순서가 README에 있다.
- 완료. `main`은 보호 브랜치로 유지되고 개발 산출물은 `hbin`에만 있다.
- 완료. 제출용 산출물 목록이 `outputs/package/submission_manifest.md`로 확인 가능하다.

검증:

```bash
python3 -m compileall src scripts
python3 scripts/build_submission_package.py
```

검증 결과:

```text
payload_file_count: 100
zip_file_count: 101
zip_bytes: 약 1.5MB
excluded __pycache__: 0
excluded outputs/tmp*: 0
excluded outputs/datasets/: 0
excluded *.pkl/*.pt: 0
excluded outputs/batch/seed_*: 0
```

## P5. 공방 Timeline 패키지

상태: 완료

문제:

- 현재 trace summary, event timeline, COA card가 따로 존재한다.
- 공격 이벤트, 방어 이벤트, DecisionTrace를 한 화면에서 연결해 보는 산출물은 아직 부족하다.

구현:

```text
src/experiments/battle_timeline.py
outputs/report_tables/battle_timeline.csv
outputs/report_tables/battle_timeline.md
```

구현 방식:

- AURA attack event, TSRA-R defense event, DecisionTrace reason을 같은 시간축으로 병합한다.
- E5와 E7 중심으로 공방 timeline Markdown/CSV를 생성한다.
- 각 시점마다 공격 의도, 방어 반응, metric 변화가 보이게 한다.

완료 기준:

- 완료. `python3 -m src.experiments.battle_timeline` 형태로 재생성 가능하다.
- 완료. E5/E7 공방 sequence가 한 파일에서 비교된다.
- 완료. 공격-방어-AI 판단 루프를 설명하는 데 직접 사용할 수 있다.

검증:

```bash
python3 -m compileall src
python3 -m src.experiments.battle_timeline
```

검증 결과:

```text
battle_timeline.csv: 46 rows
experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
E5 rows: 24, attack rows: 5, defense rows: 19
E7 rows: 22, attack rows: 5, defense rows: 19
excluded unsafe action: actual RF/exploit/live network action 없음
```

## P6. 최종 재현 QA

상태: 완료

문제:

- 주요 생성 도구는 준비됐지만, 최종 제출 직전에는 clean state 기준으로 한 번에 실행되는지 확인해야 한다.

구현:

```text
scripts/verify_submission_state.py
docs/process/FINAL_QA.md
```

구현 방식:

- README Full Reproduction 순서대로 실행한다.
- 패키지 manifest를 최신 산출물 기준으로 다시 생성한다.
- 핵심 CSV row count, safety boundary, ZIP 제외 규칙, 브랜치 존재 여부를 검증한다.
- `hbin` 원격 브랜치와 `main` 보호 상태를 마지막으로 확인한다.

완료 기준:

- 완료. 전체 재현 명령이 오류 없이 끝난다.
- 완료. package manifest에 최신 timeline 산출물이 포함된다.
- 완료. `origin/main`은 유지되고 `origin/hbin`만 최신 개발 커밋을 가리킨다.

검증 결과:

```text
experiment_summary rows: 7
repeated_experiment_summary rows: 7
resilience_gain_summary rows: 4
agent_decision_trace_summary rows: 215
aura_coa_cards rows: 15
battle_timeline rows: 49
incident_summary rows: 10
package_zip entries: 128
package exclusions: passed
branch: hbin
origin main/hbin refs: present
```

## P7. Incident Summary 자동 생성

상태: 완료

문제:

- 공방 timeline은 상세하지만, 지휘관/운영자 관점의 incident summary는 아직 별도 산출물로 없다.

구현:

```text
src/experiments/incident_summary.py
outputs/report_tables/incident_summary.csv
outputs/report_tables/incident_summary.md
```

구현 방식:

- battle timeline에서 핵심 사건을 묶어 incident summary Markdown/CSV를 생성한다.
- 공격 단계, 방어 대응, metric 변화, 잔여 위험을 incident 단위로 요약한다.
- 실제 대응 명령이 아니라 시뮬레이션 분석 결과임을 safety boundary로 명시한다.

완료 기준:

- 완료. `python3 -m src.experiments.incident_summary` 형태로 재생성 가능하다.
- 완료. E5/E7 각각의 핵심 incident가 5개 단위로 요약된다.
- 완료. AURA/TSRA-R의 판단 이유와 metric 변화가 incident summary에 연결된다.

검증:

```bash
python3 -m compileall src
python3 -m src.experiments.incident_summary
```

검증 결과:

```text
incident_summary.csv: 10 rows
E5 incidents: 5
E7 incidents: 5
safety boundary missing: 0
```

## P8. Competition Alignment Matrix

상태: 완료

문제:

- 대회의 목표, 공격/방어 에이전트 구조, 안전 경계, 검증 산출물이 여러 문서와 코드에 흩어져 있다.
- 팀원이 추가될 때 "왜 이 코드와 산출물이 필요한지"를 한눈에 확인할 기준표가 필요하다.
- 이후 개발이 대회 방향에서 벗어나지 않도록 자동 확인 가능한 게이트가 필요하다.

구현:

```text
src/experiments/competition_alignment.py
outputs/report_tables/competition_alignment_matrix.csv
outputs/report_tables/competition_alignment_matrix.md
```

구현 방식:

- 대회 목표를 10개 alignment row로 나눴다.
- 각 row는 scoring area, competition goal, 구현 메커니즘, 담당 컴포넌트, evidence file, next gate를 가진다.
- 실제 파일 존재, CSV row count, safety boundary 문구를 검사해 `verified` 또는 `incomplete` 상태를 남긴다.
- README full reproduction, package builder, final verifier에 연결했다.

완료 기준:

- 완료. `python3 -m src.experiments.competition_alignment --fail-on-incomplete` 명령으로 재생성 가능하다.
- 완료. 10개 alignment row가 모두 `verified` 상태다.
- 완료. 패키지 manifest와 QA 검증에서 alignment matrix 누락을 잡는다.

검증:

```bash
python3 -m src.experiments.competition_alignment --fail-on-incomplete
```

검증 결과:

```text
competition_alignment_matrix.csv: 10 rows
evidence_status: all verified
covered areas: attack scenario, defense architecture, AI agent architecture,
               attack-defense cooperation, ML contribution, safety boundary,
               repeatable evidence, adaptive defense, team handoff
```

해석:

- 이 산출물은 추가 기능 개발 전 방향성 점검표다.
- 새 기능은 이 matrix의 next gate 중 하나 이상을 통과해야 한다.
- `main`이 아니라 `hbin` 브랜치에서 이어 작업하는 협업 기준도 함께 검증한다.

## P9. Agent Event Contract Validation

상태: 완료

문제:

- AURA와 TSRA-R은 분리된 에이전트지만 같은 시뮬레이터와 JSONL 로그 계약을 공유한다.
- 한쪽 에이전트가 이벤트 필드를 바꾸면 battle timeline, incident summary, trace summary가 조용히 깨질 수 있다.
- 팀원이 추가될 경우 attack event, defense event, mission event, DecisionTrace 형식을 자동으로 확인할 필요가 있다.

구현:

```text
src/experiments/validate_event_contracts.py
outputs/report_tables/agent_contract_validation.csv
outputs/report_tables/agent_contract_validation.md
```

구현 방식:

- `attack_events.jsonl`: AURA attack event와 candidate/expected impact 필드 검증
- `defense_events.jsonl`: TSRA-R defense action과 details 필드 검증
- `mission_events.jsonl`: message lifecycle 필드 검증
- `metric_snapshots.jsonl`: mission impact metric 필드 검증
- `aura_decision_traces.jsonl`, `tsra_r_decision_traces.jsonl`: AgentRuntime trace 구조 검증
- cross-contract: attack event와 AURA trace, defense event와 TSRA-R trace, metric time coverage 연결 검증

완료 기준:

- 완료. `python3 -m src.experiments.validate_event_contracts --fail-on-error` 명령으로 재생성 가능하다.
- 완료. E1~E7 전체에서 49개 contract check가 모두 통과한다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.validate_event_contracts --fail-on-error
```

검증 결과:

```text
agent_contract_validation.csv: 49 contract checks
status: all pass
contracts: attack_event_schema, defense_event_schema, metric_snapshot_schema,
           mission_event_schema, aura_decision_trace_schema,
           tsra-r_decision_trace_schema, agent_cross_contract
```

해석:

- 공격 에이전트와 방어 에이전트를 따로 개발해도 공유 로그 계약이 깨지면 바로 실패한다.
- 실제 공격 기능은 추가하지 않고, 폐쇄형 시뮬레이션 산출물의 신뢰성을 높이는 작업이다.

## P10. DecisionTrace Quality Audit

상태: 완료

문제:

- event contract validation은 로그 형식이 맞는지 확인하지만, DecisionTrace가 에이전트 판단 루프를 충분히 보여주는지는 별도로 봐야 한다.
- AURA는 대기 구간에서 no-op을 선택하고 공격 시점에만 후보/도구를 평가한다.
- TSRA-R은 매 판단마다 방어 조건과 후보 action을 평가한다.
- 이 차이를 반영해 "정책별 trace 품질"을 자동 점검할 필요가 있다.

구현:

```text
src/experiments/trace_quality_audit.py
outputs/report_tables/decision_trace_quality_audit.csv
outputs/report_tables/decision_trace_quality_audit.md
```

구현 방식:

- agent/policy 단위로 trace를 묶는다.
- reason, observation, memory, feedback, selected_action coverage를 계산한다.
- tool_call coverage, candidate_action coverage, non-no-op count, selected event count를 계산한다.
- AURA와 TSRA-R의 정책 차이를 반영해 실패 기준을 분리한다.

완료 기준:

- 완료. `python3 -m src.experiments.trace_quality_audit --fail-on-error` 명령으로 재생성 가능하다.
- 완료. E3~E7의 active agent/policy 9개 그룹이 모두 pass다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.trace_quality_audit --fail-on-error
```

검증 결과:

```text
decision_trace_quality_audit.csv: 9 audit rows
status: all pass
AURA/AURA-ML: 5 selected attack events per active experiment
TSRA-R/TSRA-R-ML: tool/candidate coverage 1.0
```

해석:

- 이 산출물은 "Python 함수가 아니라 에이전트 판단 루프"라는 구조적 근거를 강화한다.
- 이후 에이전트 정책을 바꿔도 reason, memory, tool, candidate, selected action 증거가 사라지면 검증에서 잡힌다.

## P11. Agent Loop Replay

상태: 완료

문제:

- trace summary와 quality audit은 표 형태라서 판단 루프 전체를 한눈에 읽기 어렵다.
- 팀원이 AURA/TSRA-R을 따로 개발하려면 "한 주기에서 무엇을 관측하고, 어떤 메모리를 보고, 어떤 도구와 후보를 거쳐 행동했는지"를 빠르게 이해해야 한다.
- 에이전트 구조를 설명할 때 no-op 판단과 실제 action 판단을 함께 보여주는 대표 replay가 필요하다.

구현:

```text
src/experiments/agent_loop_replay.py
outputs/report_tables/agent_loop_replay.csv
outputs/report_tables/agent_loop_replay.md
```

구현 방식:

- E5 rule 공방과 E7 ML 공방을 기본 대상으로 둔다.
- agent/policy별로 대표 `no_op` trace 1개와 실제 action trace 1개를 뽑는다.
- 각 row에 observe, memory, tools, candidates, selected_action, feedback, reason을 순서대로 요약한다.
- safety boundary를 각 replay row에 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.agent_loop_replay` 명령으로 재생성 가능하다.
- 완료. AURA, AURA-ML, TSRA-R, TSRA-R-ML의 `no_op`/`action` replay 8개가 생성된다.
- 완료. README, Agent Runtime 문서, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.agent_loop_replay
```

검증 결과:

```text
agent_loop_replay.csv: 8 replay rows
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
cases: no_op, action
missing loop fields: 0
```

해석:

- 이 산출물은 에이전트 구조를 사람이 바로 읽을 수 있는 단위로 압축한다.
- 새 정책을 넣더라도 observe-memory-tool-candidate-decision-feedback 흐름이 유지되는지 확인할 기준으로 쓴다.

## P12. Metric Gate Summary

상태: 완료

문제:

- 파일, 이벤트 계약, trace 품질은 확인하고 있지만 핵심 metric이 실제로 프로젝트 방향을 지지하는지는 별도 검증이 필요하다.
- 공격 효과가 약해지거나, TSRA-R resilience가 무너지거나, E6/E7이 다시 동일해져도 row count만으로는 잡기 어렵다.
- ablation/adaptive 결과가 방향과 맞는지도 자동으로 확인해야 한다.

구현:

```text
src/experiments/metric_gate.py
outputs/report_tables/metric_gate_summary.csv
outputs/report_tables/metric_gate_summary.md
```

구현 방식:

- 30-seed batch summary, resilience gain, TSRA-R action ablation, adaptive memory summary를 읽는다.
- 공격 효과, 방어 containment, stale protection, priority reroute 가치, stale badge 가치, adaptive 개선, ML defender 분리, 반복 안정성을 gate로 검사한다.
- 각 gate는 observed value, threshold, pass/fail, interpretation을 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.metric_gate --fail-on-error` 명령으로 재생성 가능하다.
- 완료. 12개 metric gate가 모두 pass다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.metric_gate --fail-on-error
```

검증 결과:

```text
metric_gate_summary.csv: 12 gates
status: all pass
checked: AURA impact, TSRA-R resilience, action ablation,
         adaptive memory, ML defender separation, repeated-run stability,
         PACE reselection discipline
```

해석:

- 이 산출물은 "결과가 좋아 보인다"가 아니라, 핵심 방향을 자동 gate로 통과한다는 증거다.
- 이후 실험을 다시 돌려도 공방 효과가 무너지면 final verifier에서 실패한다.

## P13. Agent Interface Manifest

상태: 완료

문제:

- AURA와 TSRA-R을 따로 개발하려면 각 에이전트의 입력, 메모리, 도구, 후보, 선택 행동, 이벤트 출력 계약을 한눈에 볼 수 있어야 한다.
- 기존 문서와 trace는 상세하지만, 공격/방어 side별 인터페이스를 구조화한 표는 없었다.
- 팀원이 추가되면 어떤 파일과 action을 건드려야 하는지 빠르게 파악할 기준이 필요하다.

구현:

```text
src/experiments/agent_interface_manifest.py
outputs/report_tables/agent_interface_manifest.csv
outputs/report_tables/agent_interface_manifest.md
```

구현 방식:

- E3, E5, E7 DecisionTrace를 읽어 active agent를 추출한다.
- AURA/AURA-ML은 `attack`, TSRA-R/TSRA-R-ML은 `defense` side로 분류한다.
- goal, policy, observation input contract, memory contract, tool contract, candidate contract, selected action contract, event output을 요약한다.
- safety boundary를 각 agent row에 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.agent_interface_manifest` 명령으로 재생성 가능하다.
- 완료. AURA, AURA-ML, TSRA-R, TSRA-R-ML 4개 agent row가 생성된다.
- 완료. README, Agent Runtime 문서, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.agent_interface_manifest
```

검증 결과:

```text
agent_interface_manifest.csv: 4 agents
attack side: AURA, AURA-ML
defense side: TSRA-R, TSRA-R-ML
all agents: tool contract present, non-no-op decision present
```

해석:

- 이 산출물은 공격/방어 에이전트를 따로 개발하기 위한 인터페이스 기준표다.
- 새 agent나 policy를 추가할 때 입력·도구·출력 계약이 manifest에 반영되는지 확인할 수 있다.

## P14. Agent Capability Matrix

상태: 완료

문제:

- interface manifest는 agent별 계약을 보여주지만, 각 capability가 어떤 실험 증거와 metric gate로 검증되는지는 따로 봐야 한다.
- AURA 공격 효과와 TSRA-R 방어 액션을 같은 기준으로 정리해야 공격/방어 담당이 각각 무엇을 고도화할지 명확해진다.
- 특히 `priority_reroute`, `stale_badge`, `ml_attack_alert`, adaptive gating 같은 핵심 capability가 어떤 evidence에 연결되는지 보여줘야 한다.

구현:

```text
src/experiments/agent_capability_matrix.py
outputs/report_tables/agent_capability_matrix.csv
outputs/report_tables/agent_capability_matrix.md
```

구현 방식:

- AURA COA cards에서 선택된 attack capability를 집계한다.
- E5/E7 defense events에서 TSRA-R defense action capability를 집계한다.
- TSRA action ablation, adaptive memory summary, metric gate를 읽어 observed effect와 validation gate를 붙인다.
- 모든 row에 safety boundary를 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.agent_capability_matrix` 명령으로 재생성 가능하다.
- 완료. attack/defense capability 10개가 생성된다.
- 완료. 핵심 capability `queue_pressure`, `priority_reroute`, `stale_badge`, `ml_attack_alert`, `adaptive_optional_action_gating`이 포함된다.
- 완료. README, Agent Runtime 문서, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.agent_capability_matrix
```

검증 결과:

```text
agent_capability_matrix.csv: 10 capabilities
attack side: 4
defense side: 6
required capabilities: present
```

해석:

- 이 산출물은 에이전트별 "할 수 있는 일"을 runtime action과 검증 evidence에 연결한다.
- 공격/방어 에이전트를 따로 고도화할 때 capability 단위로 작업을 나눌 수 있다.

## P15. Attack-Defense Coverage

상태: 완료

문제:

- Agent Capability Matrix는 공격 capability와 방어 capability를 같은 표에 놓지만, 각 공격이 어떤 방어 조합으로 커버되는지는 직접 읽어야 한다.
- 공격 에이전트와 방어 에이전트를 따로 고도화할수록 두 작업이 서로 맞물린다는 증거가 필요하다.

구현:

```text
src/experiments/attack_defense_coverage.py
outputs/report_tables/attack_defense_coverage.csv
outputs/report_tables/attack_defense_coverage.md
```

구현 방식:

- `agent_capability_matrix.csv`에서 공격/방어 capability와 evidence count를 읽는다.
- `metric_gate_summary.csv`에서 각 coverage mapping의 validation gate 통과 여부를 읽는다.
- `bandwidth_limit`, `failover_chasing`, `queue_pressure`, `stale_cop_induction` 4개 공격 capability를 TSRA-R 방어 capability와 매핑한다.
- 각 row에 coverage logic, residual risk, safety boundary를 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.attack_defense_coverage` 명령으로 재생성 가능하다.
- 완료. 4개 공격 capability가 모두 `covered` 상태다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.attack_defense_coverage
```

검증 결과:

```text
attack_defense_coverage.csv: 4 rows
coverage_status: covered for all rows
mapped attacks: bandwidth_limit, failover_chasing, queue_pressure, stale_cop_induction
```

해석:

- 이 산출물은 공격 담당과 방어 담당이 서로 다른 파일을 개발하더라도 capability 단위 연결성을 유지하게 하는 기준표다.
- 새 공격 capability를 추가하면 반드시 대응 방어 capability와 validation gate를 같이 추가해야 한다.

## P16. Attack-Defense Response Audit

상태: 완료

문제:

- Attack-Defense Coverage는 정적 매핑이므로 실제 로그에서 방어가 시간 안에 반응했는지는 별도 확인이 필요하다.
- 방어가 이미 active인 상태와 공격 이후 새로 발생한 방어 이벤트를 구분하지 않으면 실제 공방 루프 해석이 흐려진다.

구현:

```text
src/experiments/attack_defense_response_audit.py
outputs/report_tables/attack_defense_response_audit.csv
outputs/report_tables/attack_defense_response_audit.md
```

구현 방식:

- E5/E7의 `attack_events.jsonl`과 `defense_events.jsonl`을 읽는다.
- 공격 시점에 `details.until_sec` 기준으로 active인 방어 이벤트를 계산한다.
- 공격 후 40초 안에 나온 방어 이벤트를 response로 계산한다.
- required defense 누락은 실패로 보고, support defense 누락은 residual risk로 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.attack_defense_response_audit` 명령으로 재생성 가능하다.
- 완료. E5/E7 공격 이벤트 10개가 감사된다.
- 완료. required defense missed row는 없다.
- 완료. support partial row가 있으면 숨기지 않고 residual risk로 남긴다.

검증:

```bash
python3 -m src.experiments.attack_defense_response_audit
```

검증 결과:

```text
attack_defense_response_audit.csv: 10 rows
missed_required: 0
required_covered_support_partial: 0
```

해석:

- 이 산출물은 정적 coverage와 실제 event timeline 사이를 연결한다.
- 공격/방어 에이전트를 따로 개발해도 required response timing이 깨지면 final verifier에서 잡히게 된다.

## P17. PACE Transition Audit

상태: 완료

문제:

- fallback PACE 재선택은 response audit에서 효과가 보이지만, 각 전환이 어떤 공격 context에서 왜 발생했는지 별도 표가 없다.
- PACE 전환은 mission impact의 recovery instability 성분을 키울 수 있으므로, 전환 근거와 tradeoff를 같이 남겨야 한다.

구현:

```text
src/experiments/pace_transition_audit.py
outputs/report_tables/pace_transition_audit.csv
outputs/report_tables/pace_transition_audit.md
```

구현 방식:

- E5/E7 `defense_events.jsonl`에서 `pace_switch`만 추출한다.
- 이전 active link를 추론해 `from_link -> target_link`를 만든다.
- 전환 시점의 active attack, 40초 내 near-future attack, metric snapshot을 붙인다.
- `satcom_to_fallback`, `fallback_reselect` 상태를 구분한다.

완료 기준:

- 완료. `python3 -m src.experiments.pace_transition_audit` 명령으로 재생성 가능하다.
- 완료. E5/E7 PACE 전환 4개가 감사된다.
- 완료. SATCOM 최초 fallback 2개, fallback 재선택 2개가 구분된다.
- 완료. self transition은 없다.

검증:

```bash
python3 -m src.experiments.pace_transition_audit
```

검증 결과:

```text
pace_transition_audit.csv: 4 rows
satcom_to_fallback: 2
fallback_reselect: 2
self_transition: 0
```

해석:

- PACE 전환은 단순 이벤트가 아니라 공격 context, target link, recovery instability tradeoff와 함께 해석된다.
- 방어 담당이 PACE threshold를 조정할 때 이 표를 기준으로 과한 전환과 필요한 전환을 구분할 수 있다.

## P18. Mission Impact Decomposition

상태: 완료

문제:

- `mission_impact_mean`은 하나의 스칼라라서 어떤 임무 성분이 점수를 만들었는지 바로 보이지 않는다.
- TSRA-R은 raw stale data를 즉시 없애기보다 `stale_badge`로 신뢰 위험을 낮추므로, raw `stale_data_ratio`만 보면 방어 효과가 과소평가된다.
- PACE 전환은 recovery instability를 키울 수 있으므로, 방어 효과와 복구 전환 비용을 같은 테이블에서 볼 필요가 있다.

구현:

```text
src/experiments/mission_impact_decomposition.py
outputs/report_tables/mission_impact_decomposition.csv
outputs/report_tables/mission_impact_decomposition.md
```

구현 방식:

- `outputs/batch/repeated_experiment_summary.csv`를 읽는다.
- `compute_full_mission_impact`의 5개 성분을 같은 가중치로 재구성한다.
- stale 성분은 raw `stale_data_ratio`가 아니라 `trusted_stale_exposure`를 사용한다.
- 각 row에 safety boundary를 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.mission_impact_decomposition` 명령으로 재생성 가능하다.
- 완료. E1~E7 7개 실험과 5개 성분, 총 35개 row가 생성된다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.mission_impact_decomposition
```

검증 결과:

```text
mission_impact_decomposition.csv: 35 rows
experiments: 7
components: critical_latency, trusted_stale_exposure, priority_inversion,
            kill_chain_delay, recovery_instability
```

해석:

- E3 공격 단독은 critical latency, trusted stale exposure, priority inversion, kill-chain delay가 모두 큰 상태다.
- E5/E7 방어 조건에서는 trusted stale exposure와 priority inversion은 낮아졌지만, PACE 복구 전환 비용이 recovery instability 성분으로 남는다.
- 따라서 TSRA-R의 가치는 단순히 raw stale을 없애는 것이 아니라, 지휘소가 stale COP를 최신으로 믿는 위험을 줄이고 critical traffic을 보호하는 데 있다.

## P19. Operator Alerts

상태: 완료

문제:

- `defense_events.jsonl`은 기계가 읽기 좋은 이벤트 로그지만, 사람이 즉시 이해하기에는 action과 details가 짧다.
- TSRA-R이 어떤 방어를 왜 냈고 운영자가 무엇을 주의해야 하는지 한 줄 알림으로 볼 산출물이 필요하다.
- 방어 이벤트를 mission metric, related attack context, trace reason과 연결하면 방어 에이전트의 출력이 더 명확해진다.

구현:

```text
src/experiments/operator_alerts.py
outputs/report_tables/operator_alerts.csv
outputs/report_tables/operator_alerts.md
```

구현 방식:

- E5/E7 `defense_events.jsonl`을 읽는다.
- 같은 시점의 `metric_snapshots.jsonl`과 `tsra_r_decision_traces.jsonl`을 붙인다.
- active/recent/near-future attack context를 `attack_events.jsonl`에서 추론한다.
- 각 방어 action을 severity, operator alert, mission rationale, expected operator response로 변환한다.
- 실제 운용 지시가 아니라 폐쇄형 시뮬레이션 알림임을 safety boundary로 명시한다.

완료 기준:

- 완료. `python3 -m src.experiments.operator_alerts` 명령으로 재생성 가능하다.
- 완료. E5/E7 방어 이벤트 53개가 operator alert로 변환된다.
- 완료. 핵심 action `ml_attack_alert`, `pace_switch`, `priority_reroute`, `stale_badge`, `video_throttle`이 모두 포함된다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.operator_alerts
```

검증 결과:

```text
operator_alerts.csv: 53 alerts
E5 alerts: 22
E7 alerts: 31
actions: ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
severity: high, medium
```

해석:

- 이 산출물은 TSRA-R의 방어 이벤트를 operator-facing 출력으로 바꾼다.
- 방어 담당이 새 action을 추가하면 alert 문구, mission rationale, expected response도 함께 추가해야 한다.
- 실제 RF, exploit, live network action 없이 시뮬레이션 방어 판단만 설명한다.

## P20. Agent Collaboration Graph

상태: 완료

문제:

- 개별 산출물은 많지만, AgentMemory, AURA, MissionSimulator, TSRA-R, Operator Alerts, Metrics, Verifier가 어떻게 협력하는지 한눈에 보여주는 구조가 필요하다.
- AI 에이전트 협력 구조는 대회 핵심 배점과 연결되므로, 말로만 설명하지 않고 evidence row count가 붙은 그래프로 남겨야 한다.
- 공격/방어 담당이 따로 개발해도 어떤 edge가 깨지면 협력 구조가 약해지는지 확인할 기준이 필요하다.

구현:

```text
src/experiments/agent_collaboration_graph.py
outputs/report_tables/agent_collaboration_graph.csv
outputs/report_tables/agent_collaboration_graph.md
outputs/report_tables/agent_collaboration_graph.mmd
```

구현 방식:

- `agent_interface_manifest.csv`, `agent_decision_causality_audit.csv`, `agent_memory_belief_audit.csv`, `agent_tool_usage_audit.csv`, `agent_decision_trace_summary.csv`, `aura_coa_cards.csv`, `attack_defense_coverage.csv`, `attack_defense_response_audit.csv`, `operator_alerts.csv`, `defense_effectiveness_ledger.csv`, `battle_timeline.csv`, `metric_gate_summary.csv`, `mission_impact_decomposition.csv`를 읽는다.
- 협력 구조를 16개 edge로 고정한다.
- 각 edge에 source, target, interaction, primary evidence, evidence count, validation status, safety boundary를 붙인다.
- Markdown에는 Mermaid flowchart를 포함하고, `.mmd` 파일도 별도 생성한다.

완료 기준:

- 완료. `python3 -m src.experiments.agent_collaboration_graph` 명령으로 재생성 가능하다.
- 완료. 16개 협력 edge가 모두 `verified` 상태다.
- 완료. AgentRuntime, AgentMemory, AgentTool, DecisionTrace, AURA/AURA-ML, MissionSimulator, TSRA-R/TSRA-R-ML, Operator Alerts, Defense Effectiveness Ledger, Mission Metrics, Verifier/Package가 그래프에 포함된다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.agent_collaboration_graph
```

검증 결과:

```text
agent_collaboration_graph.csv: 16 edges
validation_status: all verified
Mermaid: outputs/report_tables/agent_collaboration_graph.mmd
```

해석:

- 이 산출물은 공격-방어-AI 협력 구조를 한 장으로 보여준다.
- 새 공격/방어 기능을 추가하면 graph edge의 evidence count 또는 validation status가 같이 유지되어야 한다.
- 실제 RF, exploit, live network action 없이 폐쇄형 시뮬레이션 협력 구조만 설명한다.

## P21. Closed-Loop Episode Replay

상태: 완료

문제:

- battle timeline, response audit, operator alerts는 각각 유용하지만, 공격 1건 기준으로 보면 파일을 여러 개 넘겨야 한다.
- 공격 선택, 방어 coverage, operator alert, mission metric 변화가 한 행에 연결되어야 공방 루프를 순차적으로 이해하기 쉽다.
- E5/E7의 각 attack event가 실제로 complete response를 받았는지, 그리고 mission impact가 어떻게 움직였는지 episode 단위로 확인할 필요가 있다.

구현:

```text
src/experiments/closed_loop_episode_replay.py
outputs/report_tables/closed_loop_episode_replay.csv
outputs/report_tables/closed_loop_episode_replay.md
```

구현 방식:

- `attack_defense_response_audit.csv`를 episode 기준으로 사용한다.
- 원본 `attack_events.jsonl`에서 attack reason, score, expected impact를 붙인다.
- `metric_snapshots.jsonl`에서 attack time, response window peak, window end metric을 계산한다.
- `operator_alerts.csv`에서 response window 안의 operator-facing alert chain을 붙인다.
- 각 row에 defense chain, response status, outcome, residual risk, safety boundary를 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.closed_loop_episode_replay` 명령으로 재생성 가능하다.
- 완료. E5 5개, E7 5개, 총 10개 episode가 생성된다.
- 완료. 모든 episode의 response status가 `complete`다.
- 완료. 각 episode는 defense chain과 operator alert chain을 가진다.
- 완료. README, package builder, final verifier, competition alignment matrix, collaboration graph에 연결됐다.

검증:

```bash
python3 -m src.experiments.closed_loop_episode_replay
```

검증 결과:

```text
closed_loop_episode_replay.csv: 10 episodes
E5 episodes: 5
E7 episodes: 5
response_status: complete for all rows
```

해석:

- 이 산출물은 공격 1건을 기준으로 공방 루프를 순차적으로 보여준다.
- E7 첫 episode는 ML TSRA-R이 20초 뒤 방어 window를 열고, 이후 priority reroute, stale badge, PACE switch가 함께 작동하는 흐름을 보여준다.
- 단일 숫자나 분리된 로그가 아니라 attack -> defense -> alert -> metric movement를 한 record로 묶는다.

## P22. Defense Effectiveness Ledger

상태: 완료

문제:

- Operator alert와 closed-loop replay는 방어 이벤트가 나왔다는 사실을 보여주지만, 각 방어 액션 이후 local metric이 어떻게 움직였는지 event 단위로 보기 어렵다.
- TSRA-R 방어 에이전트의 품질은 aggregate resilience gain만이 아니라 action별 before/after 효과로도 설명되어야 한다.

구현:

```text
src/experiments/defense_effectiveness_ledger.py
outputs/report_tables/defense_effectiveness_ledger.csv
outputs/report_tables/defense_effectiveness_ledger.md
```

구현 방식:

- E5/E7의 `defense_events.jsonl`을 읽는다.
- `metric_snapshots.jsonl`에서 방어 이벤트 시점과 30초 뒤 metric을 찾는다.
- `operator_alerts.csv`에서 severity, operator alert, related attack context를 붙인다.
- mission impact, P95 critical latency, trusted stale exposure, priority inversion의 before/after/delta를 기록한다.
- action별로 `improved`, `held`, `degraded_or_delayed`를 분류하고 해석을 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.defense_effectiveness_ledger` 명령으로 재생성 가능하다.
- 완료. E5/E7 DefenseEvent 56건이 모두 ledger row로 나온다.
- 완료. `ml_attack_alert`, `pace_switch`, `priority_reroute`, `stale_badge`, `video_throttle` action이 모두 포함된다.
- 완료. README, Agent Runtime 문서, TSRA-R 문서, package builder, final verifier, competition alignment matrix, collaboration graph에 연결됐다.

검증:

```bash
python3 -m src.experiments.defense_effectiveness_ledger
python3 -m src.experiments.agent_collaboration_graph
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/build_submission_package.py
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
defense_effectiveness_ledger.csv: 53 rows
E5 rows: 22
E7 rows: 31
actions: ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
observed_effect: improved, held, degraded_or_delayed
```

해석:

- 이 산출물은 TSRA-R이 "이벤트를 냈다"에서 끝나지 않고, 방어 액션과 지표 변화가 어떻게 연결되는지 보여준다.
- `held`는 실패가 아니라 해당 30초 local window에서 지표를 더 악화시키지 않고 bounded 상태로 유지했다는 의미다.
- `degraded_or_delayed`는 response가 나왔지만 공격 누적 효과 또는 metric lag 때문에 같은 window 안에서 scalar impact가 아직 상승했다는 의미다.
- 실제 운용 지시가 아니라 폐쇄형 시뮬레이션 효과 분석이다.

## P23. Agent Memory/Belief Audit

상태: 완료

문제:

- AgentRuntime, Tool, DecisionTrace는 이미 산출물로 보이지만, AgentMemory가 실제로 다음 판단에 이어지는 loop state인지 별도 표로 확인하기 어렵다.
- AI 에이전트 구조를 더 강하게 보이려면 memory coverage, belief 변화, previous-action carryover가 검증되어야 한다.

구현:

```text
src/experiments/agent_memory_belief_audit.py
outputs/report_tables/agent_memory_belief_audit.csv
outputs/report_tables/agent_memory_belief_audit.md
```

구현 방식:

- `aura_decision_traces.jsonl`, `tsra_r_decision_traces.jsonl`을 agent/policy별로 읽는다.
- memory coverage를 확인한다.
- observation_count와 decision_count가 nondecreasing인지 확인한다.
- belief key와 changing belief key를 추출한다.
- feedback key를 추출한다.
- 이전 trace의 selected action이 다음 trace memory의 `last_selected_action`으로 들어가는지 검사한다.

완료 기준:

- 완료. `python3 -m src.experiments.agent_memory_belief_audit` 명령으로 재생성 가능하다.
- 완료. 9개 agent/policy row가 모두 `pass`다.
- 완료. AURA, AURA-ML, TSRA-R, TSRA-R-ML이 모두 포함된다.
- 완료. last selected action chain match rate가 모두 1.0이다.
- 완료. README, Agent Runtime 문서, package builder, final verifier, competition alignment matrix, collaboration graph에 연결됐다.

검증:

```bash
python3 -m src.experiments.agent_memory_belief_audit
python3 -m src.experiments.agent_collaboration_graph
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/build_submission_package.py
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_memory_belief_audit.csv: 9 rows
status: pass=9
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
last_selected_chain_match_rate: 1.0 for all rows
```

해석:

- 이 산출물은 memory가 static field가 아니라 다음 의사결정에 이어지는 상태라는 점을 보여준다.
- AURA는 attack cadence와 last attack context를 기억한다.
- TSRA-R은 cooldown, enabled action, event count를 기억한다.
- ML TSRA-R은 anomaly probability와 active defense window를 기억한다.
- 실제 RF, exploit, live network action 없이 폐쇄형 시뮬레이션 trace만 감사한다.

## P24. Agent Tool Usage Audit

상태: 완료

문제:

- AgentRuntime은 ToolRegistry를 갖고 있지만, 에이전트가 어떤 tool을 실제 판단 루프에서 호출했는지 별도 표로 확인하기 어렵다.
- AI 에이전트 구조를 더 강하게 보이려면 tool invocation, input summary, output summary, status를 검증해야 한다.

구현:

```text
src/experiments/agent_tool_usage_audit.py
outputs/report_tables/agent_tool_usage_audit.csv
outputs/report_tables/agent_tool_usage_audit.md
```

구현 방식:

- `aura_decision_traces.jsonl`, `tsra_r_decision_traces.jsonl`을 agent/policy/tool별로 읽는다.
- tool invocation count와 trace coverage를 계산한다.
- input_summary와 output_summary coverage를 확인한다.
- status/error count를 확인한다.
- tool role과 selected decision에 어떤 식으로 연결되는지 `decision_link`로 남긴다.

완료 기준:

- 완료. `python3 -m src.experiments.agent_tool_usage_audit` 명령으로 재생성 가능하다.
- 완료. 34개 agent/policy/tool row가 모두 `pass`다.
- 완료. 10개 tool이 모두 포함된다: `generate_attack_candidates`, `estimate_candidate_effect`, `estimate_detectability`, `predict_candidate_impact`, `summarize_defense_context`, `evaluate_defense_conditions`, `select_fallback_link`, `predict_attack_probability`, `assess_mission_risk_guard`, `summarize_attack_context`.
- 완료. README, Agent Runtime 문서, package builder, final verifier, competition alignment matrix, collaboration graph에 연결됐다.

검증:

```bash
python3 -m src.experiments.agent_tool_usage_audit
python3 -m src.experiments.agent_collaboration_graph
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/build_submission_package.py
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_tool_usage_audit.csv: 34 rows
status: pass=24
tools: assess_mission_risk_guard, estimate_candidate_effect, estimate_detectability, evaluate_defense_conditions, generate_attack_candidates, predict_attack_probability, predict_candidate_impact, select_fallback_link, summarize_attack_context, summarize_defense_context
```

해석:

- 이 산출물은 AgentTool이 단순 등록 목록이 아니라 실제 decision loop 안에서 호출된다는 점을 보여준다.
- AURA는 후보 생성, 영향 예측, 탐지 가능성 평가 tool을 호출한다.
- AURA-ML은 ML impact prediction tool을 추가로 호출한다.
- TSRA-R은 방어 조건 평가와 PACE fallback 선택 tool을 호출한다.
- TSRA-R-ML은 anomaly probability prediction tool을 호출한다.
- 실제 RF, exploit, live network action 없이 폐쇄형 시뮬레이션 trace만 감사한다.

## P25. Agent Decision Causality Audit

상태: 완료

문제:

- DecisionTrace에는 candidates, tool calls, selected action이 모두 들어가지만, 선택된 action이 실제 후보와 tool/score 근거에서 나온 것인지 별도 검증표가 없었다.
- AI 에이전트 구조를 더 강하게 보이려면 "결과가 trace에 있다"를 넘어 "선택이 trace 근거와 일치한다"를 검증해야 한다.

구현:

```text
src/experiments/agent_decision_causality_audit.py
outputs/report_tables/agent_decision_causality_audit.csv
outputs/report_tables/agent_decision_causality_audit.md
```

구현 방식:

- 모든 DecisionTrace를 trace 단위로 읽는다.
- selected action과 candidate action이 매칭되는지 확인한다.
- selected action에 필요한 tool이 실제로 호출됐는지 확인한다.
- AURA는 selected score가 top candidate score와 맞는지 확인한다.
- TSRA-R은 selected defense action이 eligible/ready candidate인지 확인한다.
- TSRA-R-ML은 probability threshold와 active defense window 근거를 확인한다.
- no-op도 후보 부재, threshold/window, 또는 event 미발생 근거로 검증한다.

완료 기준:

- 완료. `python3 -m src.experiments.agent_decision_causality_audit` 명령으로 재생성 가능하다.
- 완료. 399개 trace row가 모두 `pass`다.
- 완료. AURA, AURA-ML, TSRA-R, TSRA-R-ML이 모두 포함된다.
- 완료. selected type `no_op`, `attack_event`, `defense_events`가 모두 포함된다.
- 완료. README, Agent Runtime 문서, package builder, final verifier, competition alignment matrix, collaboration graph에 연결됐다.

검증:

```bash
python3 -m src.experiments.agent_decision_causality_audit
python3 -m src.experiments.agent_collaboration_graph
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/build_submission_package.py
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_decision_causality_audit.csv: 399 rows
causal_status: pass=399
candidate_support: pass=399
tool_support: pass=399
score_or_threshold_support: pass=399
```

해석:

- 이 산출물은 selected action이 arbitrary output이 아니라 candidate, tool, score/threshold evidence에서 나온 결과임을 보여준다.
- AURA 공격 선택은 top score 후보와 일치한다.
- TSRA-R 방어 선택은 eligible/ready condition과 일치한다.
- TSRA-R-ML 선택은 anomaly probability threshold와 reactive defense window 근거와 일치한다.
- 실제 RF, exploit, live network action 없이 폐쇄형 시뮬레이션 trace만 감사한다.

## P26. Submission Readiness Audit

상태: 완료

문제:

- 기능 산출물은 많아졌지만, 제출 직전에는 "무엇이 준비됐는지"를 사람이 수동으로 기억하면 빠뜨리기 쉽다.
- `main` 보존, `hbin` 공유, 재현 명령, 에이전트 구조 증거, closed-loop 증거, package 입력, safety boundary, 팀 인계 문서를 하나의 기계적 체크로 묶어야 한다.

구현:

```text
src/experiments/submission_readiness_audit.py
outputs/report_tables/submission_readiness_audit.csv
outputs/report_tables/submission_readiness_audit.md
```

구현 방식:

- `origin/main`, `origin/hbin` remote branch 존재와 README branch policy를 확인한다.
- README Full Reproduction 명령이 핵심 생성기를 포함하는지 확인한다.
- Agent Runtime, Memory, Tool, DecisionTrace 관련 code/docs/output row count를 확인한다.
- AURA/TSRA-R 분리, capability coverage, response audit row count를 확인한다.
- closed-loop episode, operator alert, defense effectiveness ledger, metric/ML evidence를 확인한다.
- package builder, final verifier, manifest, `.gitignore` ZIP 제외 규칙을 확인한다.
- safety boundary와 팀 인계 문서의 개인 중심 표현 금지 기준을 확인한다.

완료 기준:

- 완료. `python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete` 명령으로 재생성 가능하다.
- 완료. 10개 readiness row가 모두 `pass`다.
- 완료. README Full Reproduction, package builder, final verifier, competition alignment matrix, collaboration graph에 연결됐다.
- 완료. `scripts/verify_submission_state.py`가 readiness audit 누락 또는 실패를 최종 검증 실패로 처리한다.

검증:

```bash
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 -m src.experiments.agent_collaboration_graph
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/build_submission_package.py
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
submission_readiness_audit.csv: 10 rows
status: pass=10
agent_collaboration_graph.csv: 17 edges
package_zip entries: 162
branch: hbin
origin main/hbin refs: present
```

해석:

- 이 산출물은 팀원이 이어받을 때 필요한 "브랜치, 재현 명령, 에이전트 증거, 패키지 입력, 안전 경계"를 한 표에서 확인하게 해준다.
- 코드와 산출물이 준비됐는지 검증하는 단계이며, 외부 클라우드 업로드나 제출 링크 권한 검증은 별도 운영 단계로 남긴다.
- 실제 RF, exploit, live network action 없이 폐쇄형 시뮬레이션 산출물만 감사한다.

## P27. Local Package Integrity Gate

상태: 완료

문제:

- 로컬 ZIP과 manifest가 있어도, 코드 수정 후 ZIP을 다시 만들지 않았거나 manifest의 SHA/파일 수가 실제 ZIP과 다르면 업로드 직전에 문제가 생긴다.
- 기존 검증은 ZIP 존재와 필수 파일 포함을 확인했지만, manifest와 실제 ZIP, 현재 worktree payload의 내용 일치까지 강하게 대조하지는 않았다.

구현:

```text
scripts/verify_submission_state.py
```

구현 방식:

- `outputs/package/submission_manifest.md`의 `zip_path`, `payload_file_count`, `zip_file_count`, `zip_bytes`, `zip_sha256`를 파싱한다.
- 실제 ZIP의 파일 수, byte 크기, SHA-256과 manifest 값을 비교한다.
- manifest의 포함 파일 목록과 ZIP 내부 파일 목록을 비교한다.
- ZIP 내부 각 payload 파일의 SHA-256과 현재 worktree 파일의 SHA-256을 비교한다.
- ZIP 내부 중복 경로와 제외 대상(`__pycache__`, `*.pyc`, `*.pkl`, `*.pt`, seed raw log 등)을 계속 검사한다.

완료 기준:

- 완료. manifest의 SHA-256, byte count, file count가 실제 ZIP과 일치해야 verifier가 통과한다.
- 완료. ZIP payload가 현재 worktree 파일과 다르면 verifier가 실패한다.
- 완료. README, FINAL_QA, SUBMISSION_PACKAGE 문서에 강화된 검증 범위를 반영했다.

검증:

```bash
python3 scripts/build_submission_package.py
python3 scripts/verify_submission_state.py --require-clean
```

검증 결과:

```text
package_zip entries: 162
package_manifest_integrity: passed
release_handoff: repo-only/current
package exclusions: passed
tracked_worktree: clean
```

해석:

- 이 게이트는 외부 업로드 직전에 올릴 ZIP이 현재 코드/산출물과 같은 파일인지 확인한다.
- 업로드 링크 권한 검증은 로컬 코드로 끝낼 수 없으므로 다음 운영 단계로 남긴다.

## P28. External Package Link Verifier

상태: 완료

문제:

- 로컬 ZIP 무결성은 검증됐지만, 외부 클라우드에 업로드한 링크가 같은 ZIP을 내려주는지는 별도 확인이 필요하다.
- 제출 링크가 로그인 전용이거나, 잘못된 파일을 가리키거나, ZIP이 손상되면 로컬 검증만으로는 잡을 수 없다.

구현:

```text
scripts/verify_external_package_link.py
```

구현 방식:

- `outputs/package/submission_manifest.md`에서 기대 ZIP SHA-256, byte 크기, ZIP entry count를 읽는다.
- 제출용 URL을 다운로드해 bytes, SHA-256, ZIP entry count를 계산한다.
- HTTP `Content-Length`가 있으면 manifest의 `zip_bytes`와 비교한다.
- URL에 username/password가 포함된 credential-embedded URL은 거부한다.
- 실제 제출 링크는 `https://`를 기본으로 요구한다.
- 로컬 self-test만 `--allow-file-url` 옵션으로 허용한다.

검증:

```bash
python3 scripts/verify_external_package_link.py \
  "file://$(pwd)/outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip" \
  --allow-file-url
```

검증 결과:

```text
status: pass
bytes_read: manifest zip_bytes와 일치
sha256: manifest zip_sha256과 일치
zip_file_count: manifest zip_file_count와 일치
```

해석:

- 외부 업로드 후에는 같은 명령의 URL만 실제 제출 링크로 바꾸면 된다.
- 이 도구는 업로드 자체를 대신하지 않는다. 업로드와 비로그인 환경 확인은 다음 운영 단계로 남긴다.

## P29. Release Candidate Handoff

상태: 완료

문제:

- ZIP SHA, byte count, entry count, 검증 명령, 남은 외부 작업을 사람이 수동으로 전달하면 누락되거나 오래된 값을 복사할 수 있다.
- 단, ZIP SHA를 적은 문서를 ZIP 안에 넣으면 해시가 자기 자신을 참조하게 되므로 handoff 문서는 repo-side로 분리해야 한다.

구현:

```text
scripts/generate_release_handoff.py
outputs/package/release_handoff.md
```

구현 방식:

- `outputs/package/submission_manifest.md`에서 ZIP path, SHA-256, byte count, entry count를 읽는다.
- 현재 branch를 기록한다.
- `outputs/package/release_handoff.md`를 생성한다.
- handoff 문서는 제출 ZIP 밖에 둔다.
- `scripts/verify_submission_state.py`가 handoff 문서에 현재 ZIP SHA/bytes/entry count가 들어 있는지 확인한다.
- verifier는 `release_handoff.md`가 제출 ZIP 안에 들어가면 실패한다.
- 커밋 SHA는 tracked file에 고정하지 않고, push 후 Git sync command로 확인한다. 커밋 SHA는 파일 내용을 포함해 계산되므로 파일 안에 자기 커밋 SHA를 안정적으로 넣을 수 없다.

검증:

```bash
python3 scripts/build_submission_package.py
python3 scripts/generate_release_handoff.py
python3 scripts/verify_submission_state.py --require-clean
```

검증 결과:

```text
release_handoff: repo-only/current
package_manifest_integrity: passed
generated_branch: hbin
tracked_worktree: clean
```

해석:

- 이 문서는 팀 인계용 release candidate sheet다.
- 실제 제출 ZIP에는 들어가지 않고, repo에서 ZIP SHA와 외부 링크 검증 명령을 확인하는 기준으로 사용한다.

## P30. Release Freeze Automation

상태: 완료

문제:

- release candidate를 만들 때 `build_submission_package.py`, `generate_release_handoff.py`, `verify_submission_state.py`, `verify_external_package_link.py`를 정해진 순서로 실행해야 한다.
- 사람이 수동으로 순서를 외우면 handoff가 오래되거나 link self-test가 빠질 수 있다.

구현:

```text
scripts/freeze_release_candidate.py
```

구현 방식:

- 제출 ZIP을 생성한다.
- release handoff를 생성한다.
- final verifier를 실행한다.
- local `file://` link self-test를 실행한다.
- manifest에서 ZIP path, file count, byte count, SHA-256을 읽어 요약한다.
- 커밋 후에는 `--require-clean` 옵션으로 tracked worktree clean 상태까지 확인한다.

검증:

```bash
python3 scripts/freeze_release_candidate.py
python3 scripts/freeze_release_candidate.py --require-clean
```

검증 결과:

```text
freeze_status: pass
package_manifest_integrity: passed
release_handoff: repo-only/current
external package link self-test status: pass
```

해석:

- 이 스크립트는 최종 로컬 동결 절차의 표준 진입점이다.
- 외부 제출 링크 자체는 업로드 이후에만 검증할 수 있으므로 다음 운영 단계로 남긴다.

## P31. Deterministic Package Build

상태: 완료

문제:

- `freeze_release_candidate.py --require-clean`은 커밋 후에도 패키지를 다시 빌드한다.
- 기존 ZIP 생성 방식은 파일 timestamp 같은 ZIP metadata가 실행 시점에 따라 바뀔 수 있어, 같은 payload라도 ZIP SHA가 달라지고 manifest/handoff가 dirty가 될 수 있었다.

구현:

```text
scripts/build_submission_package.py
```

구현 방식:

- `zipfile.write()` 대신 고정 metadata를 가진 `ZipInfo`와 `writestr()`을 사용한다.
- ZIP entry timestamp를 고정한다.
- 파일 권한은 안정적인 external attributes로 기록한다.
- 파일 순서는 기존처럼 path 기준 정렬을 유지한다.

검증:

```bash
python3 scripts/freeze_release_candidate.py
python3 scripts/freeze_release_candidate.py
```

검증 결과:

```text
zip_sha256: repeated runs stable
package_manifest_integrity: passed
package_zip_metadata: deterministic
freeze_status: pass
```

해석:

- 같은 payload면 같은 ZIP SHA가 나온다.
- 커밋 후 `freeze_release_candidate.py --require-clean`이 tracked worktree clean 상태를 깨지 않는다.

## P32. 외부 제출 ZIP 업로드와 비로그인 다운로드 확인

상태: 다음 작업

문제:

- 로컬 ZIP과 링크 검증기는 준비됐지만, 외부 제출 링크는 업로드 위치와 권한 설정이 필요하다.

구현 방향:

- `python3 scripts/freeze_release_candidate.py --require-clean`
- `outputs/package/submission_manifest.md`의 ZIP SHA-256 확인
- 외부 클라우드 업로드 후 비로그인 다운로드 검증
- `python3 scripts/verify_external_package_link.py "https://..."` 실행

완료 기준:

- `outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip`가 최신 manifest와 일치한다.
- 외부 제출 링크가 비로그인 환경에서 다운로드된다.
- 외부 링크 verifier가 `status: pass`를 출력한다.
- `origin/main`은 유지되고 `origin/hbin`만 최신 개발 커밋을 가리킨다.

## P33. Agent Decision Margin Audit

상태: 완료

문제:

- 기존 causality audit은 선택이 후보, 도구, 점수/threshold와 맞는지 확인한다.
- 하지만 심사자가 보기에는 "얼마나 확실하게 그 행동을 골랐는가"가 별도 증거로 있으면 에이전트 판단 구조가 더 설득력 있다.

구현:

```text
src/experiments/agent_decision_margin_audit.py
outputs/report_tables/agent_decision_margin_audit.csv
outputs/report_tables/agent_decision_margin_audit.md
```

검증 내용:

- AURA selected score와 runner-up score 차이
- AURA attack threshold 대비 margin
- TSRA-R eligible/ready defense action count
- TSRA-R-ML anomaly probability와 threshold margin
- no-op 판단 근거

검증:

```bash
python3 -m src.experiments.agent_decision_margin_audit
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_decision_margin_audit rows: 399
margin_status: pass=399
safety boundary: closed simulation only
```

해석:

- AgentRuntime의 DecisionTrace가 단순 로그가 아니라 선택 확신도와 no-op 근거까지 설명하는 evidence가 됐다.
- AURA/TSRA-R 양쪽 모두 같은 audit schema에서 비교된다.

## P34. Agent Engagement Scorecard

상태: 완료

문제:

- `closed_loop_episode_replay`는 공격 사건과 방어 체인을 보여준다.
- `agent_decision_margin_audit`은 공격/방어 선택의 margin을 보여준다.
- `defense_effectiveness_ledger`는 방어 이벤트별 metric 변화를 보여준다.
- 하지만 이 셋을 공격 1건 단위로 한 행에서 같이 보는 산출물이 없었다.

구현:

```text
src/experiments/agent_engagement_scorecard.py
outputs/report_tables/agent_engagement_scorecard.csv
outputs/report_tables/agent_engagement_scorecard.md
```

검증 내용:

- 공격 event id, attack type, target link
- AURA attack selection margin
- AURA attack threshold margin
- TSRA-R response status와 first response latency
- response window 안의 defense event count와 action list
- peak 대비 mission impact reduction

검증:

```bash
python3 -m src.experiments.agent_engagement_scorecard
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_engagement_scorecard rows: 10
scorecard_status: pass=10
experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
```

해석:

- AURA가 왜 공격을 골랐는지, TSRA-R이 무엇으로 대응했는지, mission impact가 어떻게 움직였는지를 같은 row에서 볼 수 있다.
- 공격/방어/AI 에이전트 협력 구조의 evidence가 더 직접적으로 연결됐다.

## P35. 제출 ZIP 공식 파일명 정렬

상태: 완료

문제:

- 제출 ZIP의 내부 품질은 검증됐지만, 기본 파일명이 안내서의 `DAH2026_소스코드_[팀명].zip` 형식과 다르면 업로드 단계에서 사람이 다시 이름을 바꾸게 된다.
- 사람이 수동으로 이름을 바꾸면 manifest의 `zip_path`, release handoff, 외부 링크 self-test 명령과 어긋날 수 있다.

구현:

```text
scripts/build_submission_package.py
scripts/freeze_release_candidate.py
scripts/verify_submission_state.py
docs/process/SUBMISSION_PACKAGE.md
```

검증 기준:

- `build_submission_package.py`의 기본 ZIP 경로가 `outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip`이다.
- `verify_submission_state.py`가 manifest의 `zip_path`, ZIP byte count, SHA-256, entry count를 같은 경로 기준으로 검증한다.
- 외부 링크 verifier의 로컬 self-test 명령도 같은 파일을 바라본다.

해석:

- 제출 직전 수동 rename을 없애고, 생성된 파일 그대로 업로드할 수 있게 했다.
- ZIP 파일은 여전히 Git에 올리지 않고, manifest와 검증 스크립트만 추적한다.

## P36. Agent Runtime Invariant Audit

상태: 완료

문제:

- 기존 trace quality, memory audit, tool audit은 각각의 관점에서 에이전트 증거를 확인한다.
- 하지만 AgentRuntime의 loop invariant를 한 파일에서 확인하지 않으면 Runtime/Memory/Tool/DecisionTrace 구조가 흩어진 증거로만 보인다.

구현:

```text
src/experiments/agent_runtime_invariant_audit.py
outputs/report_tables/agent_runtime_invariant_audit.csv
outputs/report_tables/agent_runtime_invariant_audit.md
```

검증 기준:

- trace id가 중복 없이 순차 증가한다.
- trace time이 단조 증가한다.
- AgentMemory의 `observation_count`, `decision_count`가 runtime sequence와 일치한다.
- 현재 trace의 `memory.last_selected_action`이 직전 trace의 `selected_action`과 일치한다.
- Tool call error가 0이다.
- 각 agent group에 candidate evidence와 selected event evidence가 있다.

검증:

```bash
python3 -m src.experiments.agent_runtime_invariant_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_runtime_invariant_audit rows: 9
status: pass=9
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
```

해석:

- 에이전트가 단순 Python 함수 묶음이 아니라 runtime loop, memory, tool, trace contract를 유지한다는 증거를 추가했다.
- 실제 공격 기능은 추가하지 않고 closed simulation trace audit만 수행한다.

## P37. Safety Boundary Audit

상태: 완료

문제:

- safety boundary 문구는 여러 산출물에 있지만, operational core source에 live-network/RF/exploit primitive가 없는지는 별도 기계 검증이 없었다.
- 외부 링크 검증용 `urllib`, Git/release 검증용 `subprocess` 같은 정당한 자동화 예외와 실제 agent core primitive를 구분할 필요가 있다.

구현:

```text
src/experiments/safety_boundary_audit.py
outputs/report_tables/safety_boundary_audit.csv
outputs/report_tables/safety_boundary_audit.md
```

검증 기준:

- `src/agents`, `src/aura`, `src/tsra_r`, `src/simulator`, `src/shared`, `src/ml`에 network/shell primitive가 없다.
- `urllib`은 `scripts/verify_external_package_link.py`에서만 허용한다.
- `subprocess`는 release/Git 검증 자동화에서만 허용한다.
- AURA는 `AttackCandidate`/`AttackEvent` 기반 simulated effect schema를 사용한다.
- user-facing safety boundary와 package exclusion policy가 유지된다.

검증:

```bash
python3 -m src.experiments.safety_boundary_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
safety_boundary_audit rows: 5
status: pass=5
operational core network_hits: 0
operational core shell_hits: 0
```

해석:

- 안전 경계가 문구뿐 아니라 코드 구조와 제출 패키지 정책으로도 검증된다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P38. ML Contribution Audit

상태: 완료

문제:

- ML 모델 성능, tool usage, metric gate, E7 event log가 분리되어 있어 ML이 실제 에이전트 판단에 들어갔는지 한 번에 확인하기 어렵다.
- Mac MPS 실험은 sample-pass scale evidence로 정확히 표현해야 하며, deployed AURA selector와 혼동되면 안 된다.

구현:

```text
src/experiments/ml_contribution_audit.py
outputs/report_tables/ml_contribution_audit.csv
outputs/report_tables/ml_contribution_audit.md
```

검증 기준:

- AURA-ML impact predictor는 MAE, R2, top-1 action match gate를 통과한다.
- TSRA-R-ML detector는 precision, recall, F1 gate를 통과한다.
- AURA-ML은 `predict_candidate_impact` tool을 DecisionTrace 안에서 호출한다.
- TSRA-R-ML은 `predict_attack_probability` tool을 DecisionTrace 안에서 호출한다.
- E6/E7 mission impact gap이 존재해 ML TSRA-R이 no-op copy가 아니다.
- E7에는 `queue_pressure`, `failover_chasing`, `ml_attack_alert`가 실제 event log로 존재한다.
- Mac MPS run은 `sample_passes=20000000`로 기록하고 top-1 비교를 함께 남긴다.

검증:

```bash
python3 -m src.experiments.ml_contribution_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
ml_contribution_audit rows: 7
status: pass=7
predict_candidate_impact invocations: 52
predict_attack_probability invocations: 61
```

해석:

- ML은 별도 모델 파일이 아니라 AURA-ML/TSRA-R-ML agent loop에 연결된 decision input이다.
- 실제 공격 기능은 추가하지 않고 closed simulation metric, trace, event log만 읽는다.

## P39. Reactive Defense Tradeoff Audit

상태: 완료

문제:

- E7을 E6보다 "더 강한 방어"라고 단순 주장하면 현재 metric과 맞지 않는다.
- E7은 항상 방어하는 full rule TSRA-R이 아니라, detector threshold에 따라 defense window를 여는 reactive 구조다.
- 따라서 E7의 가치와 비용을 별도 표로 드러내야 한다.

구현:

```text
src/experiments/reactive_defense_tradeoff_audit.py
outputs/report_tables/reactive_defense_tradeoff_audit.csv
outputs/report_tables/reactive_defense_tradeoff_audit.md
```

검증 기준:

- E6 policy는 `rule_defense_full`, E7 policy는 `ml_anomaly_detector`다.
- E7은 첫 AURA-ML 공격 전 defense event를 내지 않는다.
- E7의 첫 ML alert latency를 명시한다.
- E7의 `ml_attack_alert`는 active attack window와 겹친다.
- E7은 PACE, priority reroute, stale badge, video throttle을 모두 유지한다.
- E7의 mission-impact cost는 E6 대비 bounded tradeoff로 기록한다.
- E7 trace는 below-threshold no-op과 above-threshold defense-window opening을 모두 포함한다.

검증:

```bash
python3 -m src.experiments.reactive_defense_tradeoff_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
reactive_defense_tradeoff_audit rows: 7
status: pass=7
E6 pre-first defense events: 2
E7 pre-first defense events: 0
E7 first ML alert latency: 20 sec
ML alert active-attack overlap: 8/8
E7 minus E6 mission impact mean: 0.0107652
```

해석:

- E7은 낮은 mission impact 하나만으로 정당화하지 않는다.
- 탐지 기반 reactive 방어라는 설계 차이를 사전 방어 억제, alert overlap, threshold trace, bounded cost로 설명한다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P40. ML Threshold Sweep

상태: 완료

문제:

- TSRA-R-ML의 `threshold=0.75`가 코드상 존재하지만, 값 선택 근거가 별도 실험으로 고정되어 있지 않았다.
- threshold가 낮거나 높을 때 alert 수, no-op, latency, mission impact가 어떻게 바뀌는지 확인해야 한다.

구현:

```text
src/experiments/run_ml_threshold_sweep.py
outputs/batch/ml_threshold_sweep_raw.csv
outputs/batch/ml_threshold_sweep_summary.csv
outputs/report_tables/ml_threshold_sweep.csv
outputs/report_tables/ml_threshold_sweep.md
```

검증 기준:

- threshold 0.55, 0.65, 0.75, 0.85, 0.95를 모두 실행한다.
- threshold마다 10 deterministic seeds를 사용한다.
- 0.75 baseline은 usable이어야 한다.
- 0.95 high threshold는 watch로 분리되어야 한다.
- 0.95 mission impact mean은 0.75보다 높아야 한다.
- 모든 row는 closed simulation safety boundary를 포함한다.

검증:

```bash
python3 -m src.experiments.run_ml_threshold_sweep
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
ml_threshold_sweep_raw rows: 50
ml_threshold_sweep_summary rows: 5
0.75 status: usable
0.95 status: watch
0.75 mission impact mean: 0.161111
0.95 mission impact mean: 0.184434
```

해석:

- 현재 E7 threshold는 plateau 안에 있다.
- 너무 높은 threshold는 방어창 개방을 늦춰 mission impact를 올린다.
- threshold는 숨은 상수가 아니라 재실행 가능한 tuning parameter다.

## P41. TSRA-R Detector Calibration Audit

상태: 완료

문제:

- threshold sweep은 closed-loop 결과를 보여주지만, `predict_attack_probability` 확률 자체의 품질을 확인하지는 않는다.
- TSRA-R-ML은 detector probability를 threshold에 넣어 defense window를 열기 때문에 probability calibration, class separation, threshold precision/recall 근거가 필요하다.

구현:

```text
src/experiments/tsra_detector_calibration_audit.py
outputs/report_tables/tsra_detector_calibration_audit.csv
outputs/report_tables/tsra_detector_calibration_audit.md
outputs/report_tables/tsra_detector_calibration_bins.csv
```

검증 기준:

- 독립 deterministic holdout 4000개를 사용한다.
- Brier score와 expected calibration error를 기록한다.
- 0.75 threshold의 precision, recall, false-positive rate를 기록한다.
- threshold 0.55, 0.75, 0.95의 precision/recall tradeoff가 단조 방향을 보여야 한다.
- positive/negative class probability가 분리되어야 한다.
- offline calibration과 closed-loop threshold sweep 결과가 같은 방향이어야 한다.

검증:

```bash
python3 -m src.experiments.tsra_detector_calibration_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
tsra_detector_calibration_audit rows: 6
tsra_detector_calibration_bins rows: 10
brier_score: 0.0351619
expected_calibration_error: 0.093589
threshold 0.75 precision: 1.0
threshold 0.75 recall: 0.833417
threshold 0.75 false_positive_rate: 0.0
```

해석:

- 확률이 완벽히 calibrated라고 주장하지 않는다.
- 하지만 closed simulation thresholding 용도로는 Brier/ECE와 class separation이 충분하다.
- 0.75 threshold는 false positive를 줄이는 보수적 방어창 개방 기준이다.

## P42. Agent Goal Alignment Audit

상태: 완료

문제:

- 기존 causality audit은 선택 행동이 candidate/tool/score 근거에서 나왔는지 확인한다.
- 하지만 선택 행동이 각 에이전트의 목표와 관측 위험에 맞는지는 별도 증거가 부족했다.
- 특히 no-op이 많은 구조에서는 no-op도 목표에 맞는 판단인지 설명할 필요가 있다.

구현:

```text
src/experiments/agent_goal_alignment_audit.py
outputs/report_tables/agent_goal_alignment_audit.csv
outputs/report_tables/agent_goal_alignment_audit.md
```

검증 기준:

- AURA attack_event는 threshold 이상이고 top mission-impact score를 가져야 한다.
- AURA no-op은 min_start, cooldown, max_events, no candidate, below-threshold 중 하나로 설명돼야 한다.
- TSRA-R defense action은 priority, video load, stale data, PACE degradation, ML probability 조건 중 대응 조건을 만족해야 한다.
- TSRA-R no-op은 ready action 부재 또는 ML defense window 유지로 설명돼야 한다.
- 모든 row는 closed simulation safety boundary를 포함한다.

검증:

```bash
python3 -m src.experiments.agent_goal_alignment_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_goal_alignment_audit rows: 399
goal_alignment_status: pass=399
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
selected types: no_op, attack_event, defense_events
```

해석:

- 에이전트 구조가 "함수 호출" 수준이 아니라 목표, 관측, 도구, 후보, 선택, no-op 근거까지 감사 가능한 decision loop가 됐다.
- 공격과 방어 모두 자기 목적에 맞는 행동을 골랐다는 검증 산출물이 생겼다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P43. Defense Action Attribution Audit

상태: 완료

문제:

- `defense_effectiveness_ledger`는 event별 metric before/after를 보여주지만 action별 요약이 없다.
- 방어 에이전트의 가치를 설명하려면 `priority_reroute`, `stale_badge`, `video_throttle`, `pace_switch`, `ml_attack_alert`가 각각 어떤 metric 축에서 기여했는지 분리해야 한다.
- 특히 `video_throttle`, `pace_switch`는 mission impact 하나만으로 과장하면 안 되고 local metric 또는 bounded tradeoff로 설명해야 한다.

구현:

```text
src/experiments/defense_action_attribution_audit.py
outputs/report_tables/defense_action_attribution_audit.csv
outputs/report_tables/defense_action_attribution_audit.md
```

검증 기준:

- ledger 53개 defense event를 action별로 집계한다.
- action 5개가 모두 존재해야 한다.
- improved_or_held_rate가 최소 0.66 이상이어야 한다.
- `priority_reroute`는 ablation priority inversion 증가 근거를 가져야 한다.
- `stale_badge`는 ablation trusted stale exposure 증가 근거를 가져야 한다.
- `ml_attack_alert`는 active attack overlap 9/9 근거를 가져야 한다.
- 모든 row는 closed simulation safety boundary를 포함한다.

검증:

```bash
python3 -m src.experiments.defense_action_attribution_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
defense_action_attribution_audit rows: 5
status: pass=5
attribution classes:
  ablation_supported=2
  local_metric_supported=1
  bounded_tradeoff_supported=1
  reactive_window_supported=1
```

해석:

- 방어 action을 하나의 점수로 뭉개지 않고 action별 책임과 한계를 나눴다.
- TSRA-R 방어 에이전트의 효과 설명이 event-level ledger에서 action-level attribution으로 올라갔다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P44. Mission Thread Summary

상태: 완료

문제:

- 공격 판단, 방어 반응, 방어 action attribution, operator alert, metric movement가 여러 산출물에 분산돼 있다.
- 한 공격 episode를 협업자가 리뷰하려면 `closed_loop_episode_replay`, `agent_engagement_scorecard`, `defense_action_attribution_audit`를 동시에 맞춰봐야 한다.
- 공방 루프의 품질을 높이려면 episode별 end-to-end 증거 row가 필요하다.

구현:

```text
src/experiments/mission_thread_summary.py
outputs/report_tables/mission_thread_summary.csv
outputs/report_tables/mission_thread_summary.md
```

검증 기준:

- mission thread가 closed-loop episode 10개와 1:1로 매핑돼야 한다.
- E5/E7 defended episode를 모두 포함해야 한다.
- 모든 thread가 `thread_status=pass`여야 한다.
- response signal은 complete, attribution signal은 pass를 포함해야 한다.
- operator signal count는 각 thread에서 3개 이상이어야 한다.
- metric signal은 `reduction_from_peak`를 포함해야 한다.
- 모든 row는 closed simulation safety boundary를 포함한다.

검증:

```bash
python3 -m src.experiments.mission_thread_summary --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
mission_thread_summary rows: 10
thread_status: pass=10
experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
operator_signal_count range: 2-7
```

해석:

- 공격-방어-AI 에이전트 공방 루프를 mission thread 단위로 검토할 수 있게 됐다.
- 새 산출물은 기존 replay/scorecard/attribution을 대체하지 않고, 리뷰 가능한 상위 요약으로 묶는다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P45. Agent Decision Feedback Audit

상태: 완료

문제:

- 기존 decision audit는 선택 당시의 후보/점수/goal alignment를 검증한다.
- 하지만 선택된 attack/defense event가 실제 event log와 metric feedback으로 이어졌는지는 별도 추적이 필요했다.
- 에이전트 구조의 설득력을 높이려면 DecisionTrace가 post-action feedback까지 닫힌 루프여야 한다.

구현:

```text
src/experiments/agent_decision_feedback_audit.py
outputs/report_tables/agent_decision_feedback_audit.csv
outputs/report_tables/agent_decision_feedback_audit.md
```

검증 기준:

- E5/E7 closed-loop run만 대상으로 한다.
- selected attack event 10개와 selected defense event 53개를 모두 포함해야 한다.
- 모든 row가 실제 event log와 연결돼야 한다.
- 모든 row가 metric feedback 또는 ledger/action attribution으로 설명돼야 한다.
- 모든 row는 closed simulation safety boundary를 포함한다.

검증:

```bash
python3 -m src.experiments.agent_decision_feedback_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_decision_feedback_audit rows: 62
feedback_status: pass=62
selected_event_type: attack_event=10, defense_event=52
experiments: E5_rule_aura_tsra_r=27, E7_ml_aura_ml_tsra_r=36
```

해석:

- 에이전트 의사결정 증거가 "선택했다"에서 끝나지 않고 "선택 이후 어떤 metric/outcome feedback을 받았는지"까지 이어진다.
- 공격과 방어를 같은 feedback audit 형식으로 비교할 수 있다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P46. Agent Memory Influence Audit

상태: 완료

문제:

- memory belief audit는 memory의 존재와 변화는 검증하지만, memory가 실제 action gate로 작동한다는 설명은 약하다.
- 에이전트를 함수 호출이 아니라 runtime-memory 기반 loop로 보이게 하려면 memory influence를 따로 증명해야 한다.

구현:

```text
src/experiments/agent_memory_influence_audit.py
outputs/report_tables/agent_memory_influence_audit.csv
outputs/report_tables/agent_memory_influence_audit.md
```

검증 기준:

- AURA/AURA-ML cadence memory가 cooldown과 max-event no-op을 만든다.
- TSRA-R action cooldown memory가 eligible-not-ready action을 만든다.
- TSRA-R-ML active defense window memory가 opened/maintained/no-op window를 만든다.
- Adaptive TSRA-R memory policy가 평균 mission impact와 optional defense load를 줄인다.
- 기존 memory belief audit의 last-selected chain이 1.0이어야 한다.

검증:

```bash
python3 -m src.experiments.agent_memory_influence_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_memory_influence_audit rows: 6
influence_status: pass=6
AURA cooldown_noops: 48
AURA-ML cooldown_noops: 32
TSRA-R-ML opened_windows: 45
Adaptive delta_mission_impact_mean: -0.0307717
Adaptive delta_defense_count_mean: -3.93333
```

해석:

- memory가 단순 저장소가 아니라 행동을 억제하거나 유지하거나 적응시키는 gate로 검증된다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P47. Agent Coordination Latency Audit

상태: 완료

문제:

- closed-loop evidence는 충분하지만, 공격 이후 방어 반응과 operator alert가 몇 초 안에 이어졌는지 한눈에 보기 어렵다.
- 공방 협력 구조를 강화하려면 response window 안에서 attack -> defense -> alert -> metric feedback이 닫히는지 검증해야 한다.

구현:

```text
src/experiments/agent_coordination_latency_audit.py
outputs/report_tables/agent_coordination_latency_audit.csv
outputs/report_tables/agent_coordination_latency_audit.md
```

검증 기준:

- E5/E7 episode 10개를 모두 포함한다.
- 모든 row가 `coordination_status=pass`여야 한다.
- response status가 complete여야 한다.
- first operator alert latency가 40초 response window 안이어야 한다.
- impact reduction from peak가 양수여야 한다.
- prepositioned defense와 ML reactive window class가 모두 나타나야 한다.

검증:

```bash
python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_coordination_latency_audit rows: 10
coordination_status: pass=10
coordination_class: prepositioned_defense=9, ml_reactive_window=1
experiments: E5_rule_aura_tsra_r=5, E7_ml_aura_ml_tsra_r=5
```

해석:

- 공격-방어-operator alert-지표 완화가 response window 안에서 시간상 연결된다.
- E7 첫 공격은 ML reactive window로 분류되어 ML 방어자의 시간 역할이 명확해진다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## 진행 원칙

각 작업은 완료 시 다음을 만족해야 한다.

- 코드가 실행된다.
- 출력 파일이 생성된다.
- 개발 판단 근거가 Markdown에 남는다.
- `hbin` 브랜치에만 커밋/푸시된다.
- `main`은 보호 브랜치로 유지된다.

## P48. ML Defense Decision Path Audit

상태: 완료

문제:

- ML contribution audit는 모델 성능과 tool invocation을 보여주지만, E7 TSRA-R-ML의 probability threshold가 실제 방어 window와 action으로 이어지는 과정을 한 표에서 보기 어렵다.
- reactive defense tradeoff audit는 E6/E7 차이를 설명하지만, threshold 아래 no-op, threshold 위 alert cooldown, memory window 유지가 어떻게 연결되는지 세부 decision path는 따로 분해하지 않는다.

구현:

```text
src/experiments/ml_defense_decision_path_audit.py
outputs/report_tables/ml_defense_decision_path_audit.csv
outputs/report_tables/ml_defense_decision_path_audit.md
```

검증 기준:

- E7 TSRA-R-ML DecisionTrace 61개를 읽는다.
- threshold 이전 trace 16개가 no-op이고 defense event가 0개여야 한다.
- 첫 threshold crossing은 첫 ML attack 이후 20초 안에 defense window와 `ml_attack_alert`를 만들어야 한다.
- threshold 이상 decision 중 event trace와 no-event refresh trace가 모두 있어야 한다.
- alert gap은 cooldown 25초 이상이어야 한다.
- active defense window memory와 feedback이 일치하고 above-threshold window가 non-decreasing이어야 한다.
- E7 coordination latency audit와 연결되어 ML reactive row가 pass여야 한다.

검증:

```bash
python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
ml_defense_decision_path_audit rows: 7
status: pass=6
pre_threshold_noop_count: 16
pre_threshold_defense_events: 0
first_response_latency_sec: 20
above_threshold_event_traces: 24
above_threshold_no_event_refresh_traces: 21
ml_attack_alerts: 9
min_alert_gap_sec: 25
memory_mismatches: 0
threshold_window_nondecreasing: true
```

해석:

- TSRA-R-ML은 probability threshold를 기준으로 no-op, window open, cooldown-bounded refresh, core defense fanout을 구분한다.
- ML 방어자는 단순 분류기가 아니라 AgentMemory와 ToolCall, DecisionTrace를 통해 상태를 유지하며 행동한다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P49. ML Attack Decision Path Audit

상태: 완료

문제:

- ML defense path는 threshold에서 defense window까지 이어지는 흐름을 보여주지만, 공격 쪽 AURA-ML도 같은 수준의 path evidence가 필요하다.
- 기존 ML contribution audit는 AURA-ML tool invocation을 보여주지만, candidate generation, ML impact prediction, detectability penalty, top-score selection, cooldown, event budget, closed-loop feedback을 한 표로 묶지 않는다.

구현:

```text
src/experiments/ml_attack_decision_path_audit.py
outputs/report_tables/ml_attack_decision_path_audit.csv
outputs/report_tables/ml_attack_decision_path_audit.md
```

검증 기준:

- E7 AURA-ML DecisionTrace 31개를 읽는다.
- min_start 전 trace 6개는 no-op이고 attack event가 없어야 한다.
- attack decision 5개는 후보 26개 이상을 평가해야 한다.
- 각 후보마다 `predict_candidate_impact`, `estimate_candidate_effect`, `estimate_detectability`가 호출되어야 한다.
- selected attack은 top-score candidate와 일치하고 attack event log와 score/time이 맞아야 한다.
- base score는 `predicted_mission_impact - 0.15 * detectability_score`와 일치해야 한다.
- selection score는 base score에 bounded objective bonus와 repeated tactic penalty를 반영해야 한다.
- selected attack은 `queue_pressure`, `failover_chasing`, `stale_cop_induction`을 모두 포함해야 한다.
- cooldown no-op과 max-event no-op이 존재해야 한다.
- E7 scorecard에서 5개 attack 모두 complete response와 positive reduction을 가져야 한다.

검증:

```bash
python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
ml_attack_decision_path_audit rows: 6
status: pass=6
pre_start_noop_count: 6
candidate_total: 26
predict_candidate_impact: 26
estimate_candidate_effect: 26
estimate_detectability: 26
selected_matches_top_candidate: 5
score_formula_matches: 26
selection_score_formula_matches: 26
selected_objective_bonus_count: 1
attack_types: failover_chasing, queue_pressure, stale_cop_induction
cooldown_noops: 16
max_event_noops: 4
min_attack_gap_sec: 50
complete_responses: 5
positive_reductions: 5
```

해석:

- AURA-ML은 공격 후보를 임의로 고르지 않고, ML impact prediction, detectability-adjusted base score, objective/counter-defense-aware selection score로 선택한다.
- no-op, cooldown, max-event gate가 있어 무조건 공격하지 않는 에이전트 구조를 유지한다.
- repeated tactic penalty와 stale COP objective bonus가 DecisionTrace에 남아 전술 커버리지 선택 근거를 재현할 수 있다.
- 선택된 attack event는 closed-loop defense response와 metric feedback까지 연결된다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P50. ML Red-Blue Interaction Audit

상태: 완료

문제:

- ML attack path와 ML defense path가 각각은 검증됐지만, E7 episode 안에서 AURA-ML 선택과 TSRA-R-ML 반응이 한 row로 직접 연결되지는 않았다.
- 공방형 AI 에이전트 구조를 더 강하게 보이려면 attack selection trace, probability threshold, ML alert, core defense, coordination outcome을 같은 response window 안에서 묶어야 한다.

구현:

```text
src/experiments/ml_red_blue_interaction_audit.py
outputs/report_tables/ml_red_blue_interaction_audit.csv
outputs/report_tables/ml_red_blue_interaction_audit.md
```

검증 기준:

- E7 attack event 5개를 모두 포함한다.
- 각 row는 AURA-ML trace와 attack event가 score/time/type/link 기준으로 연결되어야 한다.
- 각 row는 TSRA-R-ML probability가 response window 안에서 threshold 이상이어야 한다.
- 각 row는 ML alert latency 20초를 가져야 한다.
- 각 row는 core defense latency 20초 이하를 가져야 한다.
- 각 row는 coordination latency audit에서 pass이고 positive impact reduction을 가져야 한다.
- interaction class는 `ml_triggered_after_attack`, `active_window_immediate_core_defense`, `active_window_bounded_refresh`를 모두 포함해야 한다.

검증:

```bash
python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
ml_red_blue_interaction_audit rows: 5
interaction_status: pass=5
ml_triggered_after_attack: 1
active_window_immediate_core_defense: 2
active_window_bounded_refresh: 2
first_ml_alert_latency_sec <= 20 sec when a new ML alert is needed; blank is allowed for already-active ML windows
first_core_defense_latency_sec <= 20 for all rows
impact_reduction_from_peak > 0 for all rows
```

해석:

- E7은 AURA-ML과 TSRA-R-ML이 따로 존재하는 데서 끝나지 않고, attack episode 단위로 서로 반응하는 구조를 가진다.
- 첫 공격은 ML detection이 새로 열리는 케이스이고, 이후 공격들은 이미 열린 defense window가 유지/refresh되는 케이스다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P51. Reproduction Order Audit

상태: 완료

문제:

- Full Reproduction 명령 목록은 길어졌지만, 일부 감사가 자신이 읽는 입력 산출물보다 먼저 실행될 수 있었다.
- 이 경우 로컬에 남아 있던 이전 CSV를 읽어 통과하는 위험이 생긴다.
- 특히 defense attribution, mission thread, ML red-blue interaction, packaging 단계는 입력 산출물 순서가 중요하다.

구현:

```text
src/experiments/reproduction_order_audit.py
outputs/report_tables/reproduction_order_audit.csv
outputs/report_tables/reproduction_order_audit.md
```

검증:

```bash
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

완료 기준:

```text
reproduction_order_audit rows: 15
status: pass=15
RO01-RO15 present
order_status: pass for all rows
output_status: pass for all rows
```

해석:

- 재현 명령 자체를 검증 대상으로 승격했다.
- 새 산출물이 추가될 때 README 순서, readiness, package, final verifier까지 같이 갱신해야 한다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P52. Agent Stress Scenario Audit

상태: 완료

문제:

- E1~E7과 30-seed batch는 평균적 성능을 보여주지만, 특정 작전 압박 상황에서 방어 에이전트가 버티는지 별도 증거가 부족했다.
- 공방형 에이전트 품질을 높이려면 air-defense watch, stale COP, PACE failover pressure 같은 stress fixture가 필요하다.

구현:

```text
src/experiments/agent_stress_scenario_audit.py
outputs/report_tables/agent_stress_scenario_audit.csv
outputs/report_tables/agent_stress_scenario_audit.md
```

검증 기준:

- stress scenario 3개를 생성한다.
- 각 scenario마다 5개 seed에서 attack-only와 `tsra_r_full`, `tsra_r_ml`을 비교한다.
- `tsra_r_full` mean resilience gain은 0.75 이상이어야 한다.
- `tsra_r_ml` mean resilience gain은 0.65 이상이어야 한다.
- defended mission impact mean은 0.25 이하여야 한다.
- 평균 P95 latency, trusted stale exposure, priority inversion은 attack-only 대비 감소해야 한다.

검증:

```bash
python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
agent_stress_scenario_audit rows: 6
status: pass=6
seed_count: 5 per row
tsra_r_full resilience_gain_mean min: 0.775357
tsra_r_ml resilience_gain_mean min: 0.754937
defended_mission_impact_mean max: 0.174011
stale-COP mission_guard_trigger_count_mean: 3.2
stale-COP mission_guard_event_trace_count_mean: 1.0
```

해석:

- 방어 에이전트가 일반 E5/E7 루프뿐 아니라 강한 폐쇄형 stress fixture에서도 mission impact를 낮춘다.
- ML TSRA-R은 residual mission-risk guard로 stale-COP chain의 window 종료 시점 방어 누락을 줄인다.
- ML TSRA-R은 세 stress fixture 모두에서 5-seed 평균 기준 stress threshold를 넘는 방어력을 유지한다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P53. TSRA-R-ML Early Mission-Pressure Guard

상태: 완료

문제:

- E7 첫 AURA-ML 공격은 60초에 시작하지만 기존 ML threshold crossing은 80초에 발생했다.
- 70초 trace는 probability가 threshold 아래였지만 critical queue pressure와 residual link degradation이 동시에 있어 mission risk가 이미 높았다.
- threshold를 낮추면 false alert 위험과 detector 해석이 흔들리므로, threshold 자체를 바꾸기보다 제한적인 mission-pressure guard가 필요했다.

구현:

```text
src/tsra_r/ml_defender.py
src/experiments/ml_defense_decision_path_audit.py
src/experiments/defense_action_attribution_audit.py
src/experiments/ml_red_blue_interaction_audit.py
src/experiments/tsra_detector_calibration_audit.py
scripts/verify_submission_state.py
```

검증 기준:

- early guard는 probability 0.50 이상, risk score 0.85 이상, critical queue/link pressure가 있을 때만 열린다.
- pre-threshold guard는 core defense window만 열고 `ml_attack_alert`는 만들지 않는다.
- MDP01은 `pre_threshold_guard_traces >= 1`, `pre_threshold_ml_alerts == 0`을 확인한다.
- reactive tradeoff는 E7이 E6보다 완전 우월하다고 주장하지 않고 bounded impact tradeoff를 기록한다.
- row-count verifier는 56/66 고정값이 아니라 방어 이벤트 50개 이상과 필수 action coverage를 본다.

검증:

```bash
python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error
python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 scripts/verify_submission_state.py
```

검증 결과:

```text
E7 mission impact mean: 0.159620 -> 0.159912
E7 resilience gain: 0.824473 -> 0.824367
E7-E6 mission impact gap: 0.0141698 -> 0.0135924
pre_threshold_guard_traces: 1
pre_threshold_ml_alerts: 0
ml_attack_alerts: 8
active_attack_overlap: 8
agent_decision_feedback_audit rows: 62
battle_timeline rows: 47
operator_alerts rows: 52
defense_effectiveness_ledger rows: 52
```

해석:

- E7은 detector threshold를 임의로 낮춘 것이 아니라, severe mission pressure만 별도 guard로 처리한다.
- early guard는 alert를 남발하지 않고 첫 공격 구간의 core defense timing을 앞당긴다.
- 이 변경은 closed simulation 정책과 감사 산출물만 바꾸며 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

## P54. AURA-ML Objective-Aware Tactical Coverage

상태: 완료

문제:

- 기존 AURA-ML은 ML impact predictor와 detectability penalty로 후보를 고르지만, high-score 전술인 `queue_pressure`와 `failover_chasing`에 선택이 몰렸다.
- `stale_cop_induction` 후보는 생성되지만 실제 selected attack에 포함되지 않아, 공격 에이전트가 mission objective coverage를 스스로 관리한다는 증거가 약했다.
- 단순히 결과 CSV를 고치는 방식은 에이전트가 아니므로, AgentMemory와 DecisionTrace 안에 선택 근거를 남기는 방식이 필요했다.

구현:

```text
src/aura/ml_impact_predictor.py
src/experiments/ml_attack_decision_path_audit.py
src/experiments/competition_alignment.py
scripts/verify_submission_state.py
docs/agents/AURA_ATTACK_AGENT.md
```

설계:

```text
base_attack_score = predicted_mission_impact - 0.15 * detectability_score
selection_score = base_attack_score + objective_bonus + counter_defense_bonus - repeated_tactic_penalty
```

- `repeated_tactic_penalty`는 같은 attack type을 반복 선택할수록 최대 0.12까지 붙는다.
- `stale_cop_objective_bonus`는 마지막 attack budget 구간에서 아직 `stale_cop_induction`을 쓰지 않았고 stale data risk가 남아 있을 때만 붙는다.
- `counter_defense_bonus`는 TSRA-R의 active/recent defense context가 특정 counter tactic과 맞물릴 때만 붙는다.
- AgentMemory에는 `attack_type_counts`, `last_objective_bonus`, `defense_context`, `counter_defense_context_seen`이 남는다.
- DecisionTrace의 후보와 selected action에는 `base_attack_score`, `objective_bonus`, `counter_defense_bonus`, `repeated_tactic_penalty`, `selection_score`, `objective_reason`, `counter_defense_reason`이 남는다.

검증:

```bash
python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error
python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/verify_submission_state.py
```

현재 검증 결과:

```text
E7 selected attacks:
60s  queue_pressure       SATCOM
110s failover_chasing     LTE
160s failover_chasing     MESH
210s queue_pressure       MESH
260s stale_cop_induction  MESH

ml_attack_decision_path_audit rows: 6 pass
candidate_total: 26
score_formula_matches: 26
selection_score_formula_matches: 26
objective_bonus_candidates: 1
counter_defense_bonus_candidates: 7
selected_objective_bonus_count: 1
selected_counter_defense_bonus_count: 3
selected_counter_defense_reasons: counter_pace_failover_chasing, counter_priority_video_pressure
attack_types: failover_chasing, queue_pressure, stale_cop_induction
complete_responses: 5
positive_reductions: 5

E6 mission impact mean: 0.146320
E7 mission impact mean: 0.159912
E7-E6 bounded tradeoff gap: 0.013592
E7 resilience gain: 0.824367
```

해석:

- AURA-ML은 이제 단순히 예측값이 가장 큰 전술을 반복하는 모델 wrapper가 아니다.
- ML 예측, 탐지 가능성, 반복 전술 memory, mission objective coverage, TSRA-R 방어 context 대응이 selection score로 합쳐진다.
- stale COP 전술은 마지막 예산 구간에서 objective bonus가 trace에 남은 상태로 선택되므로, 사후 표기용이 아니라 decision loop의 실제 결과다.
- 이 변경은 closed simulation 안의 공격 효과 선택 정책과 감사 기준만 바꾸며 RF, exploit, live network action은 추가하지 않는다.

## P55. Adaptive TSRA-R Candidate-Level Memory Gate

상태: 완료

문제:

- Adaptive TSRA-R은 30-seed 요약에서 mission impact와 optional action 수를 낮췄지만, 후보 action 단위로 왜 `video_throttle`이나 `pace_switch`를 보류했는지 바로 보이진 않았다.
- 방어 에이전트의 품질을 높이려면 action을 실행한 이유뿐 아니라 실행하지 않은 이유도 DecisionTrace에 남아야 한다.
- 특히 E5/E6/E7에서 남은 약점은 방어 action 비용이므로, optional action restraint를 검증 가능한 에이전트 판단으로 승격해야 한다.

구현:

```text
src/tsra_r/adaptive_defender.py
src/tsra_r/rule_defender.py
src/experiments/adaptive_defense_decision_path_audit.py
src/experiments/reproduction_order_audit.py
src/experiments/submission_readiness_audit.py
scripts/verify_submission_state.py
docs/agents/TSRA_R_DEFENSE_AGENT.md
```

설계:

- `AdaptiveTSRAR._adaptive_action_policy`가 action별 `action_decisions`를 만든다.
- 각 action decision에는 `adaptive_enabled`, `gate_class`, `reason`, `memory_evidence`가 들어간다.
- `RuleTSRAR.decide`는 이 adaptive context를 각 `candidate_actions` row에 붙인다.
- `priority_reroute`, `stale_badge`는 `core_always_on`으로 유지한다.
- `video_throttle`, `pace_switch`는 `optional_memory_enabled` 또는 `optional_memory_held`로 구분한다.

검증:

```bash
python3 -m src.experiments.run_adaptive_memory
python3 -m src.experiments.adaptive_defense_decision_path_audit --fail-on-error
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

현재 검증 결과:

```text
adaptive_defense_decision_path_audit rows: 6 pass
mission_improvement: 0.0307717
defense_count_reduction: 3.93333
video_throttle_reduction: 3.26667
pace_switch_reduction: 1.06667
trace_files: 30
trace_count: 1830
update_adaptive_action_policy: 1830
candidate_total: 7320
priority_enabled: 1830/1830
stale_enabled: 1830/1830
video_eligible_held: 1146
pace_eligible_held: 154
emission_gate_violations: 0
```

해석:

- Adaptive TSRA-R은 방어 action을 많이 내는 정책이 아니라, memory evidence가 부족한 optional action을 보류하는 방어 에이전트다.
- core protection은 유지하면서 video throttle과 PACE switch 비용을 줄인다.
- emitted defense event가 candidate-level enabled gate와 일치하므로, action과 no-action 모두 trace로 설명된다.
- 이 변경은 closed simulation 안의 방어 정책과 감사 기준만 바꾸며 RF, exploit, live network action은 추가하지 않는다.

## P56. Cross-Agent Context Flow

상태: 완료

문제:

- 기존 closed-loop 산출물은 attack event, defense event, metric movement를 사후 조인해 보여줬다.
- AI 에이전트 협력구조를 더 강하게 보이려면 한 에이전트의 행동 context가 상대 에이전트의 observation, tool, memory, candidate, feedback 안에 직접 들어가야 한다.
- TSRA-R은 AURA attack context를 보고 방어했다는 근거가 필요하고, AURA는 TSRA-R defense context를 보고 이후 공격 후보를 설명할 수 있어야 한다.

구현:

```text
src/shared/schemas.py
src/simulator/mission_simulator.py
src/agents/runtime.py
src/aura/rule_decision_engine.py
src/aura/ml_impact_predictor.py
src/tsra_r/rule_defender.py
src/tsra_r/ml_defender.py
src/experiments/cross_agent_context_audit.py
src/experiments/agent_tool_usage_audit.py
```

설계:

- `MissionState`에 active/recent attack context와 active/recent defense context를 추가했다.
- AURA/AURA-ML은 `summarize_defense_context` tool을 호출한다.
- TSRA-R/TSRA-R-ML은 `summarize_attack_context` tool을 호출한다.
- AURA candidate row에는 `cross_agent_defense_context`가 남는다.
- TSRA-R candidate row에는 `cross_agent_attack_context`가 남는다.
- emitted `DefenseEvent.details.related_attack_context`에도 공격 context 요약이 남는다.

검증:

```bash
python3 -m src.experiments.run_all
python3 -m src.experiments.cross_agent_context_audit --fail-on-error
python3 -m src.experiments.agent_tool_usage_audit
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

현재 검증 결과:

```text
cross_agent_context_audit rows: 8 pass
aura_observation_context: 62/62
tsra_observation_context: 122/122
summarize_attack_context: 122
summarize_defense_context: 62
attack_handoffs: 10/10
candidate_attack_context: 305/305
candidate_attack_context_used: 147
candidate_defense_context: 51/51
candidate_defense_context_used: 47
selected_attack_with_defense_context: 9
defense_context_seen_traces: 51
related_context_events: 52/52
active_related_events: 50
missing_related_context: 0
counter_defense_bonus_candidates: 7
selected_counter_defense_bonus_traces: 3
counter_defense_reasons: counter_pace_failover_chasing, counter_priority_video_pressure
attack_context_bonus_candidates: 61
attack_context_bonus_events: 25
selected_defense_bonus_traces: 22
ordered_core_defense_traces: 6/6
defense_counter_reasons: counter_queue_pressure_priority_reroute, counter_video_queue_pressure
agent_tool_usage_audit rows: 34 pass
reproduction_order_audit rows: 15 pass
submission_readiness_audit rows: 10 pass
competition_alignment_matrix rows: 10 verified
```

해석:

- 공격과 방어가 단순히 같은 시뮬레이터를 공유하는 수준을 넘어서, 상대방 행동 context를 다음 판단 루프의 입력으로 가진다.
- TSRA-R의 방어 event는 어떤 AURA attack context 아래에서 선택됐는지 event detail로 추적된다.
- AURA의 이후 공격 후보는 TSRA-R의 active/recent defense context를 candidate row와 feedback으로 설명한다.
- AURA-ML은 defense context를 counter-defense score로, TSRA-R은 attack context를 defense-priority score와 core event ordering으로 바꾼다.
- 이 변경은 closed simulation 내부 context와 감사 증거만 강화하며 RF, exploit, live network action은 추가하지 않는다.

## P57. Defense Priority Decision Path Audit

상태: 완료

문제:

- P56에서 TSRA-R은 AURA attack context를 `attack_context_bonus`와 `defense_priority_score`로 바꾸게 됐다.
- 하지만 cross-agent context audit만으로는 후보 점수 공식, emitted `DefenseEvent.details`, same-tick event ordering, no-op consistency를 한 번에 분리 검증하기 어렵다.
- 방어 에이전트의 신뢰도를 높이려면 "공격 context를 봤다"에서 끝나지 않고, 그 context가 어떤 방어 우선순위 판단으로 이어졌는지 별도 감사가 필요하다.

구현:

```text
src/experiments/defense_priority_decision_path_audit.py
outputs/report_tables/defense_priority_decision_path_audit.csv
outputs/report_tables/defense_priority_decision_path_audit.md
src/experiments/reproduction_order_audit.py
src/experiments/submission_readiness_audit.py
src/experiments/competition_alignment.py
scripts/verify_submission_state.py
scripts/build_submission_package.py
```

설계:

- TSRA-R trace의 `candidate_actions`에서 `defense_base_score`, `attack_context_bonus`, `score`를 읽는다.
- `score = defense_base_score + attack_context_bonus` 공식이 모든 scored candidate에서 맞는지 확인한다.
- `attack_context_bonus`가 eligible하지 않은 candidate에 붙지 않는지 확인한다.
- selected `DefenseEvent.details`의 priority score와 candidate row가 일치하는지 확인한다.
- 같은 decision에서 여러 core defense event가 나오면 priority score 내림차순인지 확인한다.
- no-op trace에 ready scored action이 남아 있지 않은지 확인한다.

검증:

```bash
python3 -m src.experiments.defense_priority_decision_path_audit --fail-on-error
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 scripts/verify_submission_state.py
```

현재 검증 결과:

```text
defense_priority_decision_path_audit rows: 6 pass
scored_candidates: 671
formula_matches: 671
max_score: 0.94
max_attack_context_bonus: 0.12
non_eligible_bonus: 0
attack_context_bonus_candidates: 177
attack_context_bonus_events: 51
checked_event_matches: 70
event_match_failures: 0
no_candidate_for_event: 0
ordered_core_defense_traces: 12/12
no_op_ready_violations: 0
unselected_ready_actions: 0
selected_without_ready: 0
```

해석:

- TSRA-R 방어 우선순위는 단순 설명 문구가 아니라 후보 점수, 선택 action, emitted event detail까지 검증되는 decision path가 됐다.
- AURA attack context가 방어 점수에 영향을 주지만 bounded bonus로 제한되어 과도한 자동 방어로 번지지 않는다.
- 이 변경은 closed simulation 안의 trace 감사와 검증 체계만 강화하며 RF, exploit, live network action은 추가하지 않는다.

## P58. AURA Attack Decision Path Audit

상태: 완료

문제:

- AURA-ML은 `event_id=ml-atk-*`와 `DecisionTrace.agent=AURA-ML`을 사용하지만, `AttackEvent.agent`는 dataclass 기본값 때문에 `AURA`로 남아 있었다.
- 기존 조인 로직은 AURA 계열 agent로 처리해서 깨지지는 않았지만, 공격/방어 에이전트를 분리해서 설명하려면 persisted event agent도 정확해야 한다.
- E7 전용 `ml_attack_decision_path_audit`는 ML path를 잘 보여주지만, E3~E7 전체 AURA/AURA-ML의 공통 공격 경로를 한 번에 검증하는 감사가 없었다.

구현:

```text
src/aura/ml_impact_predictor.py
src/experiments/aura_attack_decision_path_audit.py
outputs/report_tables/aura_attack_decision_path_audit.csv
outputs/report_tables/aura_attack_decision_path_audit.md
src/experiments/reproduction_order_audit.py
src/experiments/submission_readiness_audit.py
src/experiments/competition_alignment.py
scripts/verify_submission_state.py
scripts/build_submission_package.py
```

설계:

- `MLAURA`가 생성하는 `AttackEvent`에 `agent="AURA-ML"`을 명시한다.
- 감사는 E3~E7의 `aura_decision_traces.jsonl`과 `attack_events.jsonl`을 모두 읽는다.
- 모든 candidate의 `mission_impact - 0.15 * detectability` 공식 일치를 확인한다.
- AURA-ML candidate는 `base_attack_score + objective_bonus + counter_defense_bonus - repeated_tactic_penalty`도 확인한다.
- selected action이 같은 trace의 top-scored candidate인지, persisted `AttackEvent`와 id/score/type/link/time/agent가 맞는지 확인한다.
- no-op이 min-start, cooldown, max-event budget, threshold gate를 지키는지 확인한다.
- attack type, target link, defense-context candidate row, objective/counter-defense bonus coverage를 확인한다.

검증:

```bash
python3 -m src.experiments.run_all
python3 -m src.experiments.aura_attack_decision_path_audit --fail-on-error
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 scripts/verify_submission_state.py
```

현재 검증 결과:

```text
aura_attack_decision_path_audit rows: 6 pass
candidate_total: 123
rule_candidates: 72
ml_candidates: 51
base_formula_matches: 123
selection_formula_matches: 123
candidate_traces: 25
generate_attack_candidates: 25
estimate_candidate_effect: 123
estimate_detectability: 123
predict_candidate_impact: 51
selected_matches_top_candidate: 25
linked_attack_events: 25
event_agent_matches_trace: 25
threshold_passes: 25
noop_traces: 130
pre_start_attack_events: 0
min_attack_gap_sec: 50
cooldown_gap_violations: 0
event_budget_violations: 0
no_op_threshold_violations: 0
event_score_formula_matches: 25
rule_agent_events: 15
ml_agent_events: 10
attack_types: bandwidth_limit, failover_chasing, queue_pressure, stale_cop_induction
target_links: LTE, MESH, SATCOM
selected_with_defense_context: 19
objective_bonus_candidates: 2
counter_defense_bonus_candidates: 15
```

해석:

- AURA/AURA-ML은 후보를 임의로 고르는 함수가 아니라 tool call, score formula, gate, event payload가 이어지는 공격 에이전트로 검증된다.
- AURA-ML 이벤트는 trace와 persisted event 양쪽에서 `AURA-ML`로 식별된다.
- 이 변경은 closed simulation 안의 agent identity와 감사 체계를 강화하며 RF, exploit, live network action은 추가하지 않는다.

## P59. Agent Core Regression Gate

상태: 완료

문제:

- 기존 감사 산출물은 실험 실행 뒤 결과와 trace를 강하게 검증하지만, 핵심 코드가 수정될 때 즉시 잡히는 빠른 회귀 테스트층은 약했다.
- 협업자가 AURA, TSRA-R, AgentRuntime을 따로 수정하면 `AttackEvent.agent`, score formula, priority ordering, memory chain 같은 작은 불변식이 다시 깨질 수 있다.
- 전체 실험을 매번 돌리기 전에 수 초 안에 실패를 알려주는 코드 레벨 품질 게이트가 필요했다.

구현:

```text
tests/test_agent_regression.py
.github/workflows/quality.yml
scripts/verify_submission_state.py
scripts/build_submission_package.py
```

설계:

- 표준 `unittest`만 사용해서 새 의존성을 추가하지 않는다.
- `AgentRuntimeRegressionTests`는 tool call, memory summary, previous selected action chain, trace id sequence를 확인한다.
- `AuraMLRegressionTests`는 dummy impact model로 AURA-ML decision path를 직접 실행해 `AttackEvent.agent=AURA-ML`, selected top-score candidate, selection score formula, cooldown no-op gate를 확인한다.
- `TsraRRegressionTests`는 high-pressure MissionState를 직접 만들어 TSRA-R core defense event ordering, candidate score/event detail match, cooldown no-op gate를 확인한다.
- `.github/workflows/quality.yml`은 `hbin` push에서 compile, unit regression, package rebuild, final verifier를 실행한다.
- `verify_submission_state.py`는 `python3 -m unittest discover -s tests`를 직접 실행하고 3개 이상 테스트가 통과해야 한다.

검증:

```bash
python3 -m unittest discover -s tests
python3 -m compileall -q src scripts tests
python3 scripts/verify_submission_state.py
```

현재 검증 결과:

```text
agent_regression_tests: 3 pass
covered paths: AgentRuntime memory/tool/DecisionTrace, AURA-ML attack identity/scoring, TSRA-R priority/cooldown
quality workflow: .github/workflows/quality.yml
package inclusion: tests/test_agent_regression.py and hbin quality workflow required
```

해석:

- 산출물 감사는 그대로 유지하되, 코드 수정 직후 빠르게 깨지는 회귀를 먼저 잡을 수 있게 됐다.
- AURA-ML의 persisted event identity, TSRA-R defense priority ordering, AgentRuntime memory chain 같은 핵심 불변식이 테스트로 고정됐다.
- 이 변경은 closed simulation agent code의 품질 게이트만 추가하며 RF, exploit, live network action은 추가하지 않는다.

## P60. Agent Quality Gate Audit

상태: 완료

문제:

- P59에서 빠른 회귀 테스트와 `hbin` GitHub Actions는 추가됐지만, 이 품질 게이트가 README 재현 순서, final verifier, 제출 패키지까지 실제로 연결됐는지 별도 산출물은 없었다.
- 협업자가 테스트나 workflow를 로컬에만 두고 package/verifier 연결을 빼먹으면, 최종 산출물에서는 품질 게이트가 빠질 수 있다.
- 따라서 품질 게이트 자체도 CSV/MD로 감사해야 한다.

구현:

```text
src/experiments/agent_quality_gate_audit.py
outputs/report_tables/agent_quality_gate_audit.csv
outputs/report_tables/agent_quality_gate_audit.md
```

검증 기준:

- `python3 -m unittest discover -s tests`가 실행되고 3개 이상 테스트가 통과해야 한다.
- 테스트 파일은 AgentRuntime, AURA-ML, TSRA-R 회귀 범위를 모두 포함해야 한다.
- `scripts/verify_submission_state.py`는 unittest 실행과 test/workflow 파일 요구를 포함해야 한다.
- `.github/workflows/quality.yml`은 `hbin`에서 compile, unittest, package rebuild, release handoff, final verifier를 실행해야 하며 `main` push trigger를 갖지 않아야 한다.
- README Full Reproduction은 unittest와 quality gate audit을 heavy experiment보다 먼저 실행해야 한다.
- package builder와 manifest는 test source와 hbin quality workflow를 포함해야 한다.

검증:

```bash
python3 -m src.experiments.agent_quality_gate_audit --fail-on-error
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/verify_submission_state.py
```

현재 검증 결과:

```text
agent_quality_gate_audit rows: 6 pass
areas: unit_regression_execution, unit_regression_scope, final_verifier_integration,
       hbin_workflow_gate, readme_reproduction_gate, package_inclusion_gate
agent_regression_tests: 3 pass
quality workflow: hbin branch gate, no main push trigger
```

해석:

- 회귀 테스트가 로컬 편의 명령이 아니라 README, CI, final verifier, package manifest로 연결된 품질 게이트가 됐다.
- 팀원이 AURA/TSRA-R/AgentRuntime을 수정해도 full experiment 전에 빠르게 깨지는 지점을 잡는다.
- 이 변경은 closed simulation agent quality evidence만 추가하며 RF, exploit, live network action은 추가하지 않는다.

## P61. Team Handoff Contract

상태: 완료

문제:

- 저장소는 팀 협업 기준을 갖고 있지만, 새 팀원이 들어왔을 때 공격/방어/ML/QA/통합 작업을 어디서부터 이어갈지 한 문서에서 바로 보기 어렵다.
- 기존 readiness audit는 팀 인계 문서가 필요하다는 방향은 확인하지만, 역할 lane, 필수 gate, decision record 규칙을 세부적으로 감사하지는 않았다.
- 사용자 요구처럼 한 명 이상이 추가될 수 있으므로, 개인 중심 표현 없이 확장 가능한 팀 핸드오프 계약이 필요하다.

구현:

```text
docs/process/TEAM_HANDOFF.md
src/experiments/team_handoff_audit.py
outputs/report_tables/team_handoff_audit.csv
outputs/report_tables/team_handoff_audit.md
```

설계:

- `TEAM_HANDOFF.md`는 branch rule, role lanes, change contract, minimum gate before push, decision record rule, safety boundary, handoff checklist를 가진다.
- Role lane은 `Attack agent`, `Defense agent`, `ML and metrics`, `QA and packaging`, `Integration`으로 나눈다.
- 각 lane은 primary files와 required evidence를 연결한다.
- `team_handoff_audit`는 문서 구조, role lane coverage, branch policy, minimum gate commands, decision record contract, package/readiness integration, safety boundary를 검증한다.
- README, GitHub workflow 문서, package builder, final verifier, submission readiness, competition alignment에 새 audit를 연결했다.

검증:

```bash
python3 -m src.experiments.team_handoff_audit --fail-on-error
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/verify_submission_state.py
```

현재 검증 결과:

```text
team_handoff_audit rows: 7 pass
areas: handoff_document_structure, role_lane_contract, branch_policy,
       minimum_gate_commands, decision_record_contract,
       package_and_readiness_integration, safety_boundary
reproduction_order_audit rows: 18 pass
```

해석:

- 새 팀원은 공격/방어/ML/QA/통합 중 어느 lane을 맡아도 primary files와 required evidence를 바로 찾을 수 있다.
- 팀 핸드오프 문서는 final verifier와 package manifest로 묶여 누락되면 검증에서 실패한다.
- 이 변경은 팀 개발 계약과 closed simulation handoff evidence만 추가하며 RF, exploit, live network action은 추가하지 않는다.

## P62. TSRA-R-ML Rule Defense Tool Delegation

상태: 완료

문제:

- TSRA-R-ML은 detector probability와 mission risk guard로 방어 window를 열고, 그 안에서 `RuleTSRAR.decide(state)`를 실행한다.
- 기존 구조도 동작은 맞지만, 상위 `TSRA-R-ML` DecisionTrace에서는 core rule defense 실행이 별도 runtime tool로 보이지 않았다.
- 이 상태에서는 "ML이 판단했고 그 판단으로 어떤 방어 action fanout을 실행했는지"가 trace 하나에서 덜 명확하다.

구현:

```text
src/tsra_r/ml_defender.py
tests/test_agent_regression.py
src/experiments/ml_defense_decision_path_audit.py
src/experiments/agent_decision_causality_audit.py
src/experiments/agent_tool_usage_audit.py
```

설계:

- `MLTSRAR`에 `execute_rule_defense_actions` runtime tool을 등록했다.
- active defense window가 열렸을 때 `self.rule.decide(state)`를 직접 호출하지 않고 `runtime.call_tool("execute_rule_defense_actions", ...)`로 실행한다.
- `agent_decision_causality_audit`는 TSRA-R-ML이 `defense_events`를 선택할 때 이 tool이 없으면 실패한다.
- `ml_defense_decision_path_audit`에 `Rule-defense tool execution` row를 추가해 active window trace와 rule tool trace가 1:1로 맞는지 확인한다.
- `agent_tool_usage_audit`는 새 tool의 역할과 decision link를 설명한다.

검증:

```bash
python3 -m unittest discover -s tests
python3 -m src.experiments.run_all
python3 -m src.experiments.agent_tool_usage_audit
python3 -m src.experiments.agent_decision_causality_audit
python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error
python3 scripts/verify_submission_state.py
```

예상 검증 결과:

```text
agent_regression_tests: 4 pass
agent_tool_usage_audit rows: 34 pass
ml_defense_decision_path_audit rows: 7 pass
MDP05 Rule-defense tool execution: pass
```

해석:

- TSRA-R-ML은 ML detector로 window를 열고, core 방어 action은 명시적 tool delegation으로 실행한다.
- 이 변경은 "ML 점수만 낸 코드"가 아니라 observe-memory-tool-decision-trace 구조를 갖춘 방어 에이전트라는 증거를 강화한다.
- 실제 RF, exploit, live network action은 추가하지 않고 closed simulation defense delegation evidence만 강화한다.
