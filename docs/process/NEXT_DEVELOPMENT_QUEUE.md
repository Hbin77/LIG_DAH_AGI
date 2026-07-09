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
full_tsra_r mission impact: 0.157423
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
- 완료. 11개 metric gate가 모두 pass다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.metric_gate --fail-on-error
```

검증 결과:

```text
metric_gate_summary.csv: 11 gates
status: all pass
checked: AURA impact, TSRA-R resilience, action ablation,
         adaptive memory, ML defender separation, repeated-run stability
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
- 완료. E5/E7 PACE 전환 6개가 감사된다.
- 완료. SATCOM 최초 fallback 2개, fallback 재선택 4개가 구분된다.
- 완료. self transition은 없다.

검증:

```bash
python3 -m src.experiments.pace_transition_audit
```

검증 결과:

```text
pace_transition_audit.csv: 6 rows
satcom_to_fallback: 2
fallback_reselect: 4
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
- 완료. E5/E7 방어 이벤트 56개가 operator alert로 변환된다.
- 완료. 핵심 action `ml_attack_alert`, `pace_switch`, `priority_reroute`, `stale_badge`, `video_throttle`이 모두 포함된다.
- 완료. README, package builder, final verifier, competition alignment matrix에 연결됐다.

검증:

```bash
python3 -m src.experiments.operator_alerts
```

검증 결과:

```text
operator_alerts.csv: 56 alerts
E5 alerts: 23
E7 alerts: 33
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
defense_effectiveness_ledger.csv: 56 rows
E5 rows: 23
E7 rows: 33
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
- 완료. 23개 agent/policy/tool row가 모두 `pass`다.
- 완료. 7개 tool이 모두 포함된다: `generate_attack_candidates`, `estimate_candidate_effect`, `estimate_detectability`, `predict_candidate_impact`, `evaluate_defense_conditions`, `select_fallback_link`, `predict_attack_probability`.
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
agent_tool_usage_audit.csv: 23 rows
status: pass=23
tools: estimate_candidate_effect, estimate_detectability, evaluate_defense_conditions, generate_attack_candidates, predict_attack_probability, predict_candidate_impact, select_fallback_link
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
package_zip entries: 161
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
package_zip entries: 161
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
  "file://$(pwd)/outputs/package/DAH2026_source_LIG_DAH_AGI.zip" \
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
- `outputs/package/release_handoff.md`를 생성한다.
- handoff 문서는 제출 ZIP 밖에 둔다.
- `scripts/verify_submission_state.py`가 handoff 문서에 현재 ZIP SHA/bytes/entry count가 들어 있는지 확인한다.
- verifier는 `release_handoff.md`가 제출 ZIP 안에 들어가면 실패한다.

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
tracked_worktree: clean
```

해석:

- 이 문서는 팀 인계용 release candidate sheet다.
- 실제 제출 ZIP에는 들어가지 않고, repo에서 ZIP SHA와 외부 링크 검증 명령을 확인하는 기준으로 사용한다.

## P30. 외부 제출 ZIP 업로드와 비로그인 다운로드 확인

상태: 다음 작업

문제:

- 로컬 ZIP과 링크 검증기는 준비됐지만, 외부 제출 링크는 업로드 위치와 권한 설정이 필요하다.

구현 방향:

- `python3 scripts/build_submission_package.py`
- `python3 scripts/verify_submission_state.py --require-clean`
- `outputs/package/submission_manifest.md`의 ZIP SHA-256 확인
- 외부 클라우드 업로드 후 비로그인 다운로드 검증
- `python3 scripts/verify_external_package_link.py "https://..."` 실행

완료 기준:

- `outputs/package/DAH2026_source_LIG_DAH_AGI.zip`가 최신 manifest와 일치한다.
- 외부 제출 링크가 비로그인 환경에서 다운로드된다.
- 외부 링크 verifier가 `status: pass`를 출력한다.
- `origin/main`은 유지되고 `origin/hbin`만 최신 개발 커밋을 가리킨다.

## 진행 원칙

각 작업은 완료 시 다음을 만족해야 한다.

- 코드가 실행된다.
- 출력 파일이 생성된다.
- 개발 판단 근거가 Markdown에 남는다.
- `hbin` 브랜치에만 커밋/푸시된다.
- `main`은 보호 브랜치로 유지된다.
