# 대회 방향 고정 문서

## 왜 이 문서를 두는가

이 프로젝트의 개발 방향은 단순히 기능을 많이 붙이는 것이 아니다. DAH 2026 예선의 핵심은 방산 임무 환경에서 공격, 방어, AI 에이전트가 실제로 맞물려 돌아가는 구조를 증명하는 것이다.

따라서 이후 모든 개발은 아래 원칙에 맞아야 한다.

```text
방산 임무 이해
+ 현실적인 공격 표면
+ 공격 단계와 맞물린 방어
+ 명시적인 AI 에이전트 런타임
+ 실행 로그와 반복 실험 증거
```

## 대회의 긍지

이 대회가 요구하는 수준은 일반 IT 보안 시나리오에 방산 이름만 붙이는 것이 아니다.

안내서 기준으로 보면 DAH 예선의 핵심은 아래 한 문장이다.

```text
방산 환경을 이해한 팀이 AI를 공격과 방어에 어떻게 실제로 쓸 수 있는지 증명하는 것
```

여기서 긍지는 exploit을 많이 아는 것이 아니라, 실제 작전 환경의 제약을 알고 그 안에서 책임 있게 공방 구조를 설계하는 데 있다.

지켜야 할 방향:

- 실제 방산 운용 제약을 반영한다.
- 공격은 시스템 파괴가 아니라 임무 영향으로 평가한다.
- 방어는 탐지, 차단, 복구가 공격 단계와 직접 연결되어야 한다.
- AI 에이전트는 장식이 아니라 판단 루프 안에 있어야 한다.
- 구현 증거는 코드, 로그, 실험 결과로 확인 가능해야 한다.

이 프로젝트에서의 해석:

```text
SATCOM이 완전히 끊기는 상황보다,
통신은 되는 것처럼 보이지만
critical message latency, stale COP, priority inversion이 악화되어
C4ISR 판단 신뢰성이 무너지는 상황을 다룬다.
```

## 대회 목표 해석

대회가 보는 것은 세 가지다.

1. 공격을 얼마나 현실적인 방산 임무 위협으로 설계했는가.
2. 그 공격을 탐지, 차단, 복구하는 방어 구조가 실제로 맞물리는가.
3. AI 에이전트가 장식이 아니라 판단 루프, 도구 호출, 메모리, 로그 안에서 동작하는가.

이 프로젝트의 개발 기준으로 바꾸면 다음과 같다.

| 대회 목표 | 개발 기준 |
|---|---|
| 공격 시나리오 설계 | AURA가 SATCOM/C4ISR 임무 영향이 큰 공격 효과를 고른다 |
| 방어 전략 수립 | TSRA-R이 AURA 공격 단계에 대응하는 탐지, 완화, 복구 액션을 낸다 |
| AI 에이전트 아키텍처 | Runtime, Memory, Tool, DecisionTrace가 실제 실행 로그로 남는다 |
| 구현 증거 | JSONL, CSV, figure, metric gate, package verifier로 재현된다 |

## 프로젝트 목표

최종 목표는 AURA와 TSRA-R이 같은 폐쇄형 C4ISR/SATCOM 시뮬레이터 안에서 공방하는 구조를 만드는 것이다.

목표 구조:

```text
AURA
  observe MissionState
  generate attack candidates
  predict mission impact
  select attack effect
  emit AttackEvent
  write DecisionTrace

MissionSimulator
  apply simulated attack effects
  process message queues
  update COP freshness
  compute mission metrics

TSRA-R
  observe MissionState
  detect attack-induced degradation
  select defensive actions
  emit DefenseEvent
  write DecisionTrace

Metrics
  critical latency
  trusted stale exposure
  priority inversion
  mission impact
  resilience gain
```

## 진행 방식

모든 기능 개발은 아래 순서를 지킨다.

1. 공격-방어 연결성을 먼저 확인한다.
2. 공격 capability가 어떤 방어 capability로 커버되는지 명시한다.
3. 에이전트 입력/출력/도구/상태를 명시한다.
4. 실제 공격 기능이 아니라 폐쇄형 시뮬레이션 효과로 구현한다.
5. 행동 선택 이유를 `DecisionTrace`에 남긴다.
6. 단일 실행과 반복 실행 결과를 확인한다.
7. 개발 판단 근거를 Markdown에 남긴다.
8. `hbin` 브랜치에만 커밋하고 푸시한다.

즉 진행 방식은 기능을 많이 붙이는 순서가 아니다.

```text
대회 목표 확인
-> 공격/방어/AI 중 어느 축을 강화하는지 명시
-> 폐쇄형 시뮬레이션으로 구현
-> DecisionTrace causality, Memory audit, Tool audit, metric으로 증명
-> 검증 스크립트와 패키지에 포함
-> hbin 브랜치에 공유
```

## 개발 게이트

새 기능을 넣기 전에 아래 질문에 답할 수 있어야 한다.

| 질문 | 통과 기준 |
|---|---|
| 방산 임무와 연결되는가 | C4ISR, SATCOM, PACE, COP, critical traffic 중 하나 이상과 직접 연결 |
| 공격/방어 중 어디에 기여하는가 | AURA 또는 TSRA-R의 행동 선택에 직접 영향 |
| AI 에이전트 구조를 강화하는가 | Runtime, Memory, Tool, DecisionTrace 중 하나 이상 개선 |
| 실행 증거가 남는가 | JSONL 로그, CSV, figure, metric 중 하나 이상 생성 |
| 안전 경계를 지키는가 | 실제 RF, exploit, 장비 침투, 운용 가능한 공격 파라미터 없음 |
| 실험으로 확인 가능한가 | `run_all`, `run_batch`, 또는 전용 검증 명령 존재 |

하나도 통과하지 못하는 기능은 넣지 않는다.

## 피해야 할 방향

금지 또는 후순위:

- 실제 공격 도구처럼 보이는 기능
- 대회 시나리오와 무관한 ML 모델 추가
- 예쁜 UI만 있고 공방 판단에 영향 없는 작업
- LLM/API 사용을 이유 없이 붙이는 작업
- 실험 로그 없이 주장만 늘리는 작업
- 공격 에이전트만 강화하고 방어 연결을 방치하는 작업
- Mission Impact와 연결되지 않는 수치 장식

## 현재 구현의 기준점

현재 기준점:

```text
도메인: Hybrid SATCOM Disruption 기반 C4ISR 데이터 신뢰성 붕괴
공격 에이전트: AURA
방어 에이전트: TSRA-R
시뮬레이터: MissionSimulator
에이전트 런타임: AgentRuntime, AgentMemory, ToolRegistry, DecisionTrace
실험: E1~E7, 30-seed batch
핵심 지표: Mission Impact, Resilience Gain, trusted stale exposure
```

현재 가장 중요한 개발 방향:

1. 새 기능이 DAH 대회 목표와 직접 연결되는지 alignment matrix로 먼저 확인한다.
2. 공격, 방어, AI 에이전트 판단 루프 중 어디를 강화하는지 명시한다.
3. AURA/TSRA-R/MissionSimulator 사이의 event contract가 깨지지 않는지 검증한다.
4. DecisionTrace가 reason, memory, tool, candidate, selected action을 충분히 남기는지 검증한다.
5. 대표 agent loop replay로 observe-memory-tool-candidate-decision-feedback 흐름을 확인한다.
6. 에이전트별 입력, 메모리, 도구, 후보, 선택 행동, 이벤트 출력 인터페이스를 manifest로 명시한다.
7. 에이전트 capability를 runtime action, observed effect, validation gate에 연결한다.
8. 공격 capability가 어떤 TSRA-R 방어 capability로 커버되는지 coverage matrix로 검증한다.
9. 실제 E5/E7 로그에서 required defense가 active 또는 response window 안에 나오는지 감사한다.
10. PACE 전환의 reason, target link, 공격 context, recovery instability tradeoff를 감사한다.
11. 핵심 metric gate가 공격 효과, 방어 효과, adaptive 개선, ML 분리를 통과하는지 확인한다.
12. 실행 증거와 safety boundary가 함께 남는 산출물만 유지한다.
13. TSRA-R 방어 이벤트는 operator alert로도 해석 가능해야 한다.
14. 공격-시뮬레이터-방어-알림-지표-verifier 협력 구조는 graph edge로 검증한다.
15. 공격 1건 단위의 closed-loop episode replay로 순차 흐름을 검증한다.
16. TSRA-R 방어 이벤트는 local before/after metric movement ledger로 효과를 확인한다.
17. AgentMemory는 belief 변화와 previous-action carryover audit로 검증한다.
18. AgentTool은 invocation, input summary, output summary audit로 검증한다.
19. DecisionTrace의 selected action은 candidate/tool/score causality audit로 검증한다.
20. 제출 전 실행 재현성과 산출물 구성을 안정화한다.

## 다음 작업 우선순위

### P0. DecisionTrace 요약기

상태: 완료

목적:

- JSONL trace를 사람이 읽을 수 있는 Markdown/CSV로 요약한다.
- AURA와 TSRA-R의 판단 이유를 같은 시간축에서 비교한다.

산출물:

```text
src/experiments/trace_summary.py
outputs/report_tables/agent_decision_trace_summary.md
outputs/report_tables/agent_decision_trace_summary.csv
```

### P1. AURA COA Card

상태: 완료

목적:

- AURA가 선택한 공격 효과를 COA 카드로 정리한다.
- 공격 후보, 예상 impact, detectability, 선택 이유를 한 장 단위로 남긴다.

산출물:

```text
outputs/report_tables/aura_coa_cards.md
```

### P2. TSRA-R Action Ablation

상태: 완료

목적:

- `priority_reroute`, `video_throttle`, `stale_badge`, `pace_switch`가 각각 어떤 효과를 내는지 분리 검증한다.

산출물:

```text
outputs/batch/tsra_action_ablation_summary.csv
outputs/figures/tsra_action_ablation.png
```

### P3. Adaptive Memory

상태: 완료

목적:

- AgentMemory가 단순 기록을 넘어서 최근 실패/성공을 다음 threshold나 action ranking에 반영하게 한다.

주의:

- 기존 E1~E7 baseline은 유지한다.
- adaptive mode는 별도 실험으로 켜고 끌 수 있게 둔다.

산출물:

```text
src/tsra_r/adaptive_defender.py
src/experiments/run_adaptive_memory.py
outputs/batch/adaptive_memory_summary.csv
outputs/figures/adaptive_memory_comparison.png
```

검증 결과:

```text
full TSRA-R impact:      0.157423
adaptive TSRA-R impact:  0.109489
priority inversion:      0.050609 -> 0.027455
video throttle count:    6.4 -> 3.1
E1-E7 baseline:          unchanged in run_all
```

### P4. 산출물 안정화

상태: 완료

목적:

- 제출용 ZIP과 GitHub 공유 기준으로 재현 명령, 핵심 산출물, 제외할 임시 파일을 정리한다.
- 팀원이 같은 브랜치에서 이어 받아도 실행 순서와 파일 의미를 바로 이해하게 한다.

완료 기준:

- 완료. README의 full reproduction 명령이 최신 코드와 일치한다.
- 완료. 핵심 CSV/figure/docs가 누락되지 않도록 패키지 required path를 검증한다.
- 완료. 재생성 가능한 대용량 임시 로그는 제출물에서 제외할 수 있게 구분된다.

산출물:

```text
scripts/build_submission_package.py
docs/process/SUBMISSION_PACKAGE.md
outputs/package/submission_manifest.md
```

검증 결과:

```text
package zip: outputs/package/DAH2026_source_LIG_DAH_AGI.zip
zip size:    about 1.5MB
excluded:    __pycache__, tmp logs, datasets, model binaries, seed-level logs
```

### P5. 공방 Timeline 패키지

상태: 완료

목적:

- 공격 이벤트, 방어 이벤트, DecisionTrace 이유, metric 변화를 같은 시간축에서 확인한다.
- E5 rule 공방과 E7 ML 공방을 같은 파일에서 비교한다.

산출물:

```text
src/experiments/battle_timeline.py
outputs/report_tables/battle_timeline.csv
outputs/report_tables/battle_timeline.md
```

검증 결과:

```text
battle timeline rows: 46
experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
attack rows: 10
defense rows: 38
safe boundary: closed simulation only
```

### P6. 최종 재현 QA

상태: 완료

목적:

- README Full Reproduction 순서가 실제로 끝까지 실행되는지 확인한다.
- 핵심 산출물 row count, 패키지 포함/제외 규칙, 브랜치 상태를 자동 검증한다.

산출물:

```text
scripts/verify_submission_state.py
docs/process/FINAL_QA.md
```

검증 결과:

```text
Full Reproduction: passed
package exclusions: passed
branch: hbin
origin/main: present
origin/hbin: present
```

### P7. Incident Summary 자동 생성

상태: 완료

목적:

- 상세 battle timeline을 incident 단위로 압축한다.
- 공격, 방어 대응, metric 변화, 잔여 위험, 결과를 한 행으로 요약한다.

산출물:

```text
src/experiments/incident_summary.py
outputs/report_tables/incident_summary.csv
outputs/report_tables/incident_summary.md
```

검증 결과:

```text
incident summary rows: 10
E5 incidents: 5
E7 incidents: 5
safe boundary: closed simulation only
```

### P8. Competition Alignment Matrix

상태: 완료

목적:

- 대회 목표와 현재 구현 산출물을 한 표로 연결한다.
- 공격 시나리오, 방어 아키텍처, AI 에이전트 구조, 안전 경계, 반복 검증이 모두 실제 파일로 증명되는지 확인한다.
- 이후 개발의 next gate를 명시해 방향이 흐려지지 않게 한다.

산출물:

```text
src/experiments/competition_alignment.py
outputs/report_tables/competition_alignment_matrix.csv
outputs/report_tables/competition_alignment_matrix.md
```

검증 결과:

```text
competition_alignment_matrix rows: 10
evidence_status: all verified
checked: file existence, row counts, safety boundary text
```

### P9. Agent Event Contract Validation

상태: 완료

목적:

- AURA와 TSRA-R이 분리 개발돼도 공유 JSONL 계약이 유지되는지 확인한다.
- attack event, defense event, mission event, metric snapshot, DecisionTrace 구조를 자동 검증한다.
- 공방 timeline과 incident summary가 참조하는 원천 로그의 신뢰성을 높인다.

산출물:

```text
src/experiments/validate_event_contracts.py
outputs/report_tables/agent_contract_validation.csv
outputs/report_tables/agent_contract_validation.md
```

검증 결과:

```text
agent_contract_validation checks: 49
status: all pass
safety boundary: closed simulation only
```

### P10. DecisionTrace Quality Audit

상태: 완료

목적:

- DecisionTrace가 단순 로그가 아니라 에이전트 판단 루프 증거로 충분한지 확인한다.
- active AURA/TSRA-R policy별로 reason, observation, memory, feedback, selected action, tool/candidate evidence를 점검한다.
- AURA의 공격 시점 후보 평가와 TSRA-R의 지속적 방어 후보 평가를 구분해 품질 기준을 적용한다.

산출물:

```text
src/experiments/trace_quality_audit.py
outputs/report_tables/decision_trace_quality_audit.csv
outputs/report_tables/decision_trace_quality_audit.md
```

검증 결과:

```text
decision_trace_quality_audit rows: 9
status: all pass
checked: AURA, AURA-ML, TSRA-R, TSRA-R-ML active policies
```

### P11. Agent Loop Replay

상태: 완료

목적:

- AURA와 TSRA-R의 판단 주기를 사람이 바로 읽을 수 있는 replay로 만든다.
- no-op 판단과 실제 action 판단을 모두 보여줘 에이전트가 무조건 행동하는 것이 아니라 조건부로 판단함을 남긴다.
- observe, memory, tools, candidates, selected action, feedback, reason을 한 행에 연결한다.

산출물:

```text
src/experiments/agent_loop_replay.py
outputs/report_tables/agent_loop_replay.csv
outputs/report_tables/agent_loop_replay.md
```

검증 결과:

```text
agent_loop_replay rows: 8
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
cases: no_op, action
```

### P12. Metric Gate Summary

상태: 완료

목적:

- 핵심 실험 숫자가 프로젝트 방향을 실제로 지지하는지 자동 검사한다.
- AURA 공격 효과, TSRA-R resilience, action ablation, adaptive memory, ML defender separation, repeated-run stability를 gate로 확인한다.
- 파일이 존재해도 metric 방향이 무너지면 최종 검증에서 실패하게 한다.

산출물:

```text
src/experiments/metric_gate.py
outputs/report_tables/metric_gate_summary.csv
outputs/report_tables/metric_gate_summary.md
```

검증 결과:

```text
metric gates: 11
status: all pass
key gates: E5 resilience >= 0.80, E5/E3 impact ratio <= 0.20,
           E6/E7 separation >= 0.005
```

### P13. Agent Interface Manifest

상태: 완료

목적:

- 공격/방어 에이전트를 분리 개발하기 위한 인터페이스 기준을 명시한다.
- AURA/AURA-ML과 TSRA-R/TSRA-R-ML의 side, goal, policy, input, memory, tool, candidate, selected action, event output을 정리한다.
- 팀원이 추가되어도 각 agent가 어떤 계약을 지키는지 바로 확인할 수 있게 한다.

산출물:

```text
src/experiments/agent_interface_manifest.py
outputs/report_tables/agent_interface_manifest.csv
outputs/report_tables/agent_interface_manifest.md
```

검증 결과:

```text
agent_interface_manifest rows: 4
attack side: AURA, AURA-ML
defense side: TSRA-R, TSRA-R-ML
```

### P14. Agent Capability Matrix

상태: 완료

목적:

- AURA 공격 capability와 TSRA-R 방어 capability를 같은 표에서 관리한다.
- 각 capability를 runtime action, decision source, observed effect, validation gate에 연결한다.
- 공격/방어 에이전트 고도화 작업을 capability 단위로 분리할 수 있게 한다.

산출물:

```text
src/experiments/agent_capability_matrix.py
outputs/report_tables/agent_capability_matrix.csv
outputs/report_tables/agent_capability_matrix.md
```

검증 결과:

```text
agent_capability_matrix rows: 10
attack capabilities: 4
defense capabilities: 6
```

### P15. Attack-Defense Coverage

상태: 완료

목적:

- AURA 공격 capability가 어떤 TSRA-R 방어 capability로 커버되는지 명시한다.
- 공격/방어 에이전트를 따로 개발하더라도 공방 연결성이 끊기지 않게 한다.
- coverage 상태를 metric gate와 safety boundary까지 연결해 검증한다.

산출물:

```text
src/experiments/attack_defense_coverage.py
outputs/report_tables/attack_defense_coverage.csv
outputs/report_tables/attack_defense_coverage.md
```

검증 결과:

```text
attack_defense_coverage rows: 4
coverage_status: all covered
covered attacks: bandwidth_limit, failover_chasing, queue_pressure, stale_cop_induction
```

### P16. Attack-Defense Response Audit

상태: 완료

목적:

- coverage matrix가 정적 매핑에 그치지 않게 실제 E5/E7 event log에서 방어 반응을 확인한다.
- 공격 시점에 이미 active인 방어와 공격 후 response window 안에 새로 나온 방어를 함께 계산한다.
- required defense 누락과 support defense partial을 구분해 잔여 위험을 숨기지 않는다.

산출물:

```text
src/experiments/attack_defense_response_audit.py
outputs/report_tables/attack_defense_response_audit.csv
outputs/report_tables/attack_defense_response_audit.md
```

검증 결과:

```text
attack_defense_response_audit rows: 10
missed required defenses: 0
support partial residual risk: 0 rows
```

### P17. PACE Transition Audit

상태: 완료

목적:

- `pace_switch`가 언제, 왜, 어느 link로 전환했는지 명시한다.
- PACE 전환이 공격 context와 어떤 관계인지 보여준다.
- fallback 재선택의 복원력 이득과 recovery instability tradeoff를 함께 남긴다.

산출물:

```text
src/experiments/pace_transition_audit.py
outputs/report_tables/pace_transition_audit.csv
outputs/report_tables/pace_transition_audit.md
```

검증 결과:

```text
pace_transition_audit rows: 6
satcom_to_fallback: 2
fallback_reselect: 4
self_transition: 0
```

## 최종 판단 기준

이 프로젝트의 개발이 올바른 방향인지 판단하는 기준은 하나다.

```text
이 변경이 공격-방어-AI 에이전트 공방 루프를 더 명확하고 검증 가능하게 만드는가?
```

그렇다면 진행한다.

아니라면 후순위로 둔다.
