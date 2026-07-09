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
2. 에이전트 입력/출력/도구/상태를 명시한다.
3. 실제 공격 기능이 아니라 폐쇄형 시뮬레이션 효과로 구현한다.
4. 행동 선택 이유를 `DecisionTrace`에 남긴다.
5. 단일 실행과 반복 실행 결과를 확인한다.
6. 개발 판단 근거를 Markdown에 남긴다.
7. `hbin` 브랜치에만 커밋하고 푸시한다.

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

1. AgentMemory 기반 adaptive defense를 기본 baseline과 분리해 검증한다.
2. 공방 timeline에서 `왜 이 행동이 나왔는지`를 더 직접적으로 확인 가능하게 한다.
3. 제출 전 실행 재현성과 산출물 구성을 안정화한다.

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
full TSRA-R impact:      0.123928
adaptive TSRA-R impact:  0.109489
priority inversion:      0.047238 -> 0.027455
video throttle count:    6.4 -> 3.1
E1-E7 baseline:          unchanged in run_all
```

### P4. 산출물 안정화

상태: 다음 작업

목적:

- 제출용 ZIP과 GitHub 공유 기준으로 재현 명령, 핵심 산출물, 제외할 임시 파일을 정리한다.
- 팀원이 같은 브랜치에서 이어 받아도 실행 순서와 파일 의미를 바로 이해하게 한다.

완료 기준:

- README의 full reproduction 명령이 최신 코드와 일치한다.
- 핵심 CSV/figure/docs가 누락되지 않는다.
- 재생성 가능한 대용량 임시 로그는 제출물에서 제외할 수 있게 구분된다.

## 최종 판단 기준

이 프로젝트의 개발이 올바른 방향인지 판단하는 기준은 하나다.

```text
이 변경이 공격-방어-AI 에이전트 공방 루프를 더 명확하고 검증 가능하게 만드는가?
```

그렇다면 진행한다.

아니라면 후순위로 둔다.
