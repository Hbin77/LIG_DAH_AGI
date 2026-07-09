# AURA 공격 에이전트 완성 계획

대상 시나리오: `Hybrid SATCOM Disruption 기반 C4ISR 데이터 신뢰성 붕괴`

정식 명칭: `AURA: Adversarial SATCOM Reconnaissance & Effects Agent`

## 1. 한 줄 정의

AURA는 실제 위성이나 통신 장비를 공격하는 도구가 아니다.

AURA는 우리가 만든 전술 C4ISR/SATCOM 시뮬레이터 안에서, 어떤 통신 지연·손실·큐 혼잡·대역폭 제한 효과를 언제 발생시키면 지휘소의 판단이 가장 늦어지는지 고르는 Red Team AI 에이전트다.

쉽게 말하면:

> AURA는 전장 통신 시뮬레이터 안에서 "어느 순간에 어떤 통신 병목을 만들면 방공 경보, 지휘 명령, 좌표 메시지가 가장 늦게 도착하는가"를 계산하고 실행하는 공격 효과 생성기다.

## 2. AURA가 절대 하지 않는 것

보고서와 코드에서 아래 내용은 명확히 제외한다.

- 실제 SATCOM 장비 침투
- 실제 RF 송신, 재밍, 스푸핑 수행
- exploit code 작성
- 특정 장비의 취약점 악용 절차
- 운용 가능한 주파수, 출력, 빔, 변조 파라미터 제시
- 실제 네트워크 공격 패킷 생성

AURA가 하는 것은 폐쇄형 시뮬레이션 안에서만 유효한 공격 효과 생성이다.

예시:

```json
{
  "attack_type": "mission_aware_degradation",
  "target_link": "SATCOM",
  "duration_sec": 90,
  "effects": {
    "latency_ms_add": 1200,
    "packet_loss_add": 0.08,
    "bandwidth_limit_mbps": 1.5,
    "jitter_ms_add": 300
  }
}
```

이 JSON은 실제 공격 명령이 아니라, 시뮬레이터에게 "이 시간 동안 SATCOM 링크가 나빠진 것으로 계산하라"고 알려주는 설정값이다.

## 3. 왜 이 에이전트가 필요한가

예선에서 높은 점수를 받으려면 공격 시나리오가 단순 설명으로 끝나면 안 된다. 공격자가 어떤 판단을 하고, 어떤 공격 효과를 선택하고, 그 결과 임무에 어떤 피해가 생기는지 보여줘야 한다.

AURA는 이 역할을 맡는다.

- 공격 시나리오를 자동 실행한다.
- 공격 후보 여러 개를 비교한다.
- 임무 피해가 큰 공격 효과를 선택한다.
- 결과를 로그와 표로 남긴다.
- 이후 방어 에이전트 TSRA-R이 막아야 할 입력을 만든다.
- TSRA-R과 같은 시뮬레이터, 같은 메시지 스키마, 같은 로그 포맷을 공유한다.

## 4. 전체 구조

```text
Scenario Config
      |
      v
Mission SATCOM Simulator
      |
      v
State Observer
      |
      v
Candidate Attack Generator
      |
      v
Impact Estimator
      |
      v
Decision Engine
      |
      v
Attack Event Emitter
      |
      v
Event Log / Attack Report
```

각 구성요소의 역할:

| 구성요소 | 쉬운 설명 | 산출물 |
|---|---|---|
| Scenario Config | 작전 상황 설정 파일 | 링크, 메시지, 작전 단계 |
| Mission SATCOM Simulator | 전장 통신을 흉내내는 환경 | 메시지 도착 시간, 큐 상태 |
| State Observer | 현재 상황을 읽는 눈 | 현재 링크 상태, 메시지 대기열 |
| Candidate Attack Generator | 가능한 공격 후보 생성 | 공격 후보 리스트 |
| Impact Estimator | 후보별 피해 예측 | 예상 지연, stale 비율 |
| Decision Engine | 제일 효과 큰 후보 선택 | 선택된 공격 |
| Attack Event Emitter | 시뮬레이터에 공격 효과 적용 | attack event JSON |
| Event Log / Attack Report | 증거 저장 | JSONL 로그, 표, 그래프 |

## 5. AURA의 입력

AURA는 매 시점마다 아래 정보를 받는다.

### 5.1 작전 상태

```json
{
  "time_sec": 180,
  "mission_phase": "air_defense_watch",
  "expected_critical_event": "low_altitude_air_threat",
  "blue_defense_state": "normal"
}
```

의미:

- 지금 몇 초인가
- 현재 작전 단계가 무엇인가
- 곧 중요한 경보가 발생할 가능성이 있는가
- 방어 에이전트가 아직 정상 모드인가, PACE 전환을 했는가

### 5.2 링크 상태

```json
{
  "links": {
    "SATCOM": {
      "available": true,
      "bandwidth_mbps": 5.0,
      "latency_ms": 650,
      "jitter_ms": 80,
      "loss_rate": 0.01,
      "queue_depth": 42
    },
    "TACTICAL_RADIO": {
      "available": true,
      "bandwidth_mbps": 0.8,
      "latency_ms": 250,
      "jitter_ms": 40,
      "loss_rate": 0.02,
      "queue_depth": 8
    }
  }
}
```

의미:

- SATCOM이 현재 얼마나 느린가
- 대체 통신망이 있는가
- 어디에 큐가 쌓였는가
- 어떤 링크를 건드리면 임무 피해가 커지는가

### 5.3 메시지 큐 상태

```json
{
  "message_queue": [
    {
      "message_type": "video",
      "size_kb": 1200,
      "priority": 2,
      "deadline_sec": 30,
      "created_at": 178
    },
    {
      "message_type": "air_defense_alert",
      "size_kb": 8,
      "priority": 10,
      "deadline_sec": 3,
      "created_at": 180
    }
  ]
}
```

의미:

- 어떤 메시지가 기다리고 있는가
- 영상처럼 큰 데이터가 큐를 막고 있는가
- 방공 경보처럼 작지만 중요한 메시지가 밀릴 위험이 있는가

### 5.4 COP freshness 상태

```json
{
  "cop_objects": [
    {
      "object_id": "UAV-01",
      "object_type": "uav",
      "last_update_age_sec": 95,
      "freshness_limit_sec": 30
    },
    {
      "object_id": "UGV-02",
      "object_type": "ugv",
      "last_update_age_sec": 15,
      "freshness_limit_sec": 20
    }
  ]
}
```

의미:

- 지휘소 상황판에 올라온 정보가 얼마나 오래됐는가
- 오래된 위치가 최신처럼 보일 위험이 있는가

## 6. AURA의 출력

AURA의 출력은 공격 이벤트다.

```json
{
  "event_id": "atk-00042",
  "time_sec": 180,
  "agent": "AURA",
  "attack_type": "critical_window_degradation",
  "target": {
    "link": "SATCOM",
    "traffic_class": ["air_defense_alert", "command", "coordinate"]
  },
  "duration_sec": 90,
  "effects": {
    "latency_ms_add": 1200,
    "jitter_ms_add": 250,
    "packet_loss_add": 0.05,
    "bandwidth_limit_mbps": 1.2,
    "queue_pressure": true
  },
  "expected_impact": {
    "critical_latency_p95_add_sec": 18,
    "stale_data_ratio_add": 0.22,
    "kill_chain_delay_add_sec": 75
  },
  "reason": "air_defense_alert is entering a high-consequence window while video traffic occupies the SATCOM queue"
}
```

이 출력은 나중에 보고서에 그대로 증거로 넣을 수 있다.

## 7. 공격 액션 종류

MVP에서는 공격 액션을 6개로 제한한다.

| 공격 액션 | 쉬운 설명 | 시뮬레이터 효과 |
|---|---|---|
| `link_degradation` | 링크가 전반적으로 느려짐 | latency, jitter, loss 증가 |
| `bandwidth_limit` | 도로 차선이 줄어듦 | bandwidth 감소 |
| `queue_pressure` | 큰 영상 트래픽이 큐를 차지함 | video/telemetry 큐 점유 증가 |
| `critical_window_degradation` | 중요한 경보 타이밍에만 저하 | critical message 지연 증가 |
| `stale_cop_induction` | 위치/상태 갱신을 늦춤 | COP object age 증가 |
| `failover_chasing` | 대체 통신망 전환 후 다시 병목 유도 | PACE recovery time 증가 |

1차 구현에서는 `link_degradation`, `bandwidth_limit`, `queue_pressure`, `critical_window_degradation`만 만든다.

2차 구현에서 `stale_cop_induction`, `failover_chasing`을 추가한다.

## 8. AURA의 판단 방식

처음부터 복잡한 강화학습을 쓰지 않는다. 1차 버전은 점수 기반 선택기로 만든다.

### 8.1 판단 순서

```text
1. 현재 상태를 읽는다.
2. 가능한 공격 후보를 만든다.
3. 각 후보의 짧은 미래 피해를 근사 계산한다.
4. 후보별 Mission Impact Score를 계산한다.
5. 너무 쉽게 탐지될 후보는 감점한다.
6. 점수가 가장 높은 후보를 선택한다.
7. 공격 이벤트를 시뮬레이터에 적용한다.
8. 결과를 로그로 저장한다.
```

### 8.2 의사코드

```python
def decide_attack(state):
    candidates = generate_candidates(state)
    scored = []

    for candidate in candidates:
        predicted = estimate_candidate_effect(state, candidate, horizon_sec=120)
        impact = compute_mvp_mission_impact(predicted)
        detectability = estimate_detectability(candidate, predicted)
        score = impact - 0.15 * detectability
        scored.append((score, candidate, predicted))

    best_score, best_candidate, best_prediction = max(scored, key=lambda x: x[0])

    if best_score < ATTACK_THRESHOLD:
        return NoOp(reason="no useful attack window")

    return AttackEvent.from_candidate(best_candidate, best_prediction)
```

핵심은 "무조건 공격"이 아니다. 피해가 충분히 크지 않으면 `NoOp`를 선택한다. 그래야 에이전트가 더 지능적으로 보인다.

MVP에서는 후보마다 전체 discrete-event simulation을 다시 돌리지 않는다. 구현 난이도와 실행 시간을 줄이기 위해 큐 길이, 링크 대역폭, 메시지 크기, deadline slack을 이용한 근사식으로 `estimate_candidate_effect()`를 만든다. 전체 시뮬레이션 기반 `simulate_what_if()`는 2차 확장에서 추가한다.

## 9. Mission Impact Score

공격 성공은 시스템 파괴가 아니라 임무 피해로 계산한다.

### 9.1 최종 AttackScore

```text
AttackScore =
  MissionImpactScore
- 0.15 * DetectabilityScore
```

이 식 하나를 보고서와 코드에서 공통으로 사용한다.

### 9.2 MVP MissionImpactScore

1차 MVP에서는 방어자 PACE 복구와 kill chain 세부 모델이 아직 없으므로 계산 가능한 세 지표만 사용한다.

```text
MVP_MissionImpactScore =
  0.50 * CriticalLatencyScore
+ 0.30 * StaleDataScore
+ 0.20 * PriorityInversionScore
```

### 9.3 Full MissionImpactScore

2차 확장에서 TSRA-R의 PACE 전환, 복구 안정성, kill chain 단계 모델이 들어간 뒤에는 풀 공식을 사용한다.

```text
MissionImpactScore =
  0.35 * CriticalLatencyScore
+ 0.25 * StaleDataScore
+ 0.20 * PriorityInversionScore
+ 0.15 * KillChainDelayScore
+ 0.05 * RecoveryInstabilityScore
```

### 9.4 각 점수의 의미

| 점수 | 의미 | 높으면 무슨 뜻인가 |
|---|---|---|
| `CriticalLatencyScore` | 경보·명령·좌표 메시지 지연 | 중요한 메시지가 늦게 도착함 |
| `StaleDataScore` | COP에 오래된 객체가 많음 | 지휘소가 낡은 정보를 봄 |
| `PriorityInversionScore` | 덜 중요한 트래픽이 먼저 처리됨 | 영상이 경보를 밀어냄 |
| `KillChainDelayScore` | 탐지→보고→승인→대응 누적 지연 | 대응이 늦어짐 |
| `RecoveryInstabilityScore` | 복구가 반복 실패함 | PACE 전환 후에도 안정화 안 됨 |

### 9.5 정규화 방식

모든 점수는 0~1 사이로 맞춘다.

예시:

```text
CriticalLatencyScore = min(P95CriticalLatencySec / 60, 1.0)
StaleDataScore = min(StaleDataRatio / 0.5, 1.0)
PriorityInversionScore = min(PriorityInversionRate / 0.4, 1.0)
KillChainDelayScore = min(KillChainDelaySec / 180, 1.0)
RecoveryInstabilityScore = min(FailoverOscillationCount / 3, 1.0)
```

해석:

- critical 메시지 P95 지연이 60초 이상이면 최악에 가까움
- COP 객체 중 50% 이상이 오래됐으면 최악에 가까움
- 우선순위 역전이 40% 이상이면 최악에 가까움
- kill chain이 180초 이상 늦어지면 최악에 가까움
- PACE 전환이 3번 이상 흔들리면 최악에 가까움

이 숫자는 실제 군 기준이 아니라 본 시뮬레이션의 평가 기준이라고 명시한다.

## 10. 탐지 가능성 패널티

AURA가 너무 노골적인 공격만 고르면 지능적으로 보이지 않는다. 그래서 탐지 가능성 패널티를 둔다.

```text
AttackScore =
  MissionImpactScore
- 0.15 * DetectabilityScore
```

MVP의 DetectabilityScore는 실제 방어자 탐지 모델이 아니라 본 시뮬레이션 내부 휴리스틱 기준이다. 보고서에도 이 점을 명시한다.

DetectabilityScore 예시:

| 조건 | 탐지 가능성 |
|---|---:|
| loss가 갑자기 20% 이상 증가 | 높음 |
| latency가 5배 이상 급증 | 높음 |
| 짧은 시간에 여러 링크 동시 저하 | 높음 |
| 작전 피크 시간에 작은 지연만 유도 | 중간 |
| 자연 혼잡과 비슷한 완만한 저하 | 낮음 |

이렇게 하면 AURA는 "가장 큰 피해"와 "너무 쉽게 들키지 않는 정도" 사이를 계산하는 에이전트가 된다.

## 11. 후보 공격 생성 규칙

AURA는 현재 상태를 보고 후보를 만든다.

### 11.1 기본 후보

```text
Candidate A: SATCOM latency + jitter 증가
Candidate B: SATCOM bandwidth 제한
Candidate C: video queue pressure 증가
Candidate D: critical event window에만 지연 증가
Candidate E: COP update traffic 지연
Candidate F: PACE 전환 직후 대체 링크 병목
```

### 11.2 상황별 후보 생성

| 상황 | AURA가 우선 생성할 후보 |
|---|---|
| 방공 경보가 곧 발생 | `critical_window_degradation` |
| 영상 트래픽이 큼 | `queue_pressure` |
| COP 객체 age가 이미 높음 | `stale_cop_induction` |
| SATCOM 큐가 길어짐 | `bandwidth_limit` |
| 방어자가 PACE 전환 준비 | `failover_chasing` |
| 정상 혼잡처럼 보이는 상태 | 약한 `link_degradation` |

## 12. 구현 범위

### 12.1 1차 MVP

목표: AURA가 실제로 공격 이벤트를 선택하고 로그를 남기게 만든다.

포함:

- 메시지 타입 5개
  - `video`
  - `telemetry`
  - `air_defense_alert`
  - `command`
  - `coordinate`
- 링크 타입 4개
  - `SATCOM`
  - `TACTICAL_RADIO`
  - `LTE`
  - `MESH`
- 공격 액션 4개
  - `link_degradation`
  - `bandwidth_limit`
  - `queue_pressure`
  - `critical_window_degradation`
- 점수 기반 AURA
- 최소 rule 기반 TSRA-R
  - stale COP 표시
  - critical traffic 우선 라우팅
  - 단순 link degradation 탐지
  - SATCOM 상태 악화 시 TACTICAL_RADIO/LTE/MESH 중 하나로 전환
- JSONL 로그 저장
- 실험 결과 CSV 저장

제외:

- 실제 LLM/RAG
- 실제 RF 모델
- 실제 장비 취약점
- 강화학습
- 복잡한 terminal/ground compromise

MVP에서 TSRA-R은 고급 AI가 아니라 E4/E5 실험을 가능하게 하는 최소 방어자다. 이 방어자가 있어야 AURA의 공격 효과와 방어 후 개선 효과를 같은 지표로 비교할 수 있다.

### 12.2 2차 확장

목표: 보고서에서 "적응형 공격 에이전트"로 보이게 만든다.

추가:

- `stale_cop_induction`
- `failover_chasing`
- 방어자 반응 관측
- 다음 라운드 공격 후보 조정
- 공격 그래프 시각화
- COA card 자동 생성

### 12.3 3차 확장

목표: 고득점용 차별화 요소를 넣는다.

추가:

- SPARTA/NIST TTP 매핑 테이블
- 간단한 RAG 기반 위협 설명 생성
- Streamlit 대시보드
- 공격 전/후 COP freshness 화면
- 자동 실험 리포트 생성

## 13. 권장 파일 구조

```text
DAH2026_TSRA/
  README.md
  requirements.txt
  scenarios/
    baseline.yaml
    link_degradation.yaml
    mission_aware_attack.yaml
    failover_chasing.yaml
  src/
    shared/
      __init__.py
      schemas.py
      metrics.py
      event_log.py
    aura/
      __init__.py
      models.py
      state_observer.py
      candidate_generator.py
      impact_estimator.py
      decision_engine.py
      attack_event.py
      reporter.py
    tsra_r/
      __init__.py
      rule_defender.py
      freshness_guard.py
      critical_router.py
      pace_orchestrator.py
      defense_event.py
    simulator/
      __init__.py
      links.py
      messages.py
      queues.py
      mission.py
      metrics.py
    experiments/
      run_experiment.py
      compare_results.py
  outputs/
    logs/
      attack_events.jsonl
      mission_events.jsonl
    results/
      experiment_summary.csv
      metrics_by_round.csv
    figures/
      critical_latency.png
      stale_data_ratio.png
      mission_impact.png
  docs/
    architecture.md
    demo_screenshots/
```

## 14. 데이터 모델

### 14.1 Message

```python
class Message:
    id: str
    type: str
    source: str
    destination: str
    created_at: float
    size_kb: float
    priority: int
    deadline_sec: float
    route: str
```

중요도 예시:

| 메시지 | priority | deadline |
|---|---:|---:|
| `air_defense_alert` | 10 | 3초 |
| `command` | 9 | 5초 |
| `coordinate` | 8 | 5초 |
| `telemetry` | 5 | 15초 |
| `video` | 2 | 30초 |

### 14.2 LinkState

```python
class LinkState:
    name: str
    available: bool
    bandwidth_mbps: float
    base_latency_ms: float
    jitter_ms: float
    loss_rate: float
    queue_depth: int
```

### 14.3 AttackCandidate

```python
class AttackCandidate:
    attack_type: str
    target_link: str
    target_traffic_classes: list[str]
    start_time: float
    duration_sec: float
    latency_ms_add: float
    jitter_ms_add: float
    packet_loss_add: float
    bandwidth_limit_mbps: float | None
```

### 14.4 AttackEvent

```python
class AttackEvent:
    event_id: str
    selected_at: float
    candidate: AttackCandidate
    expected_impact: dict
    reason: str
    score: float
```

## 15. 실험 계획

최소 5개 실험을 돌린다.

| 실험 | 설명 | 목적 |
|---|---|---|
| E1 Baseline | 공격 없음 | 정상 기준 확보 |
| E2 Naive Degradation | 단순 링크 저하 | 공격 효과 확인 |
| E3 Mission-Aware AURA | AURA가 중요 시점 공격 선택 | AURA가 단순 공격보다 위험함을 증명 |
| E4 AURA vs Rule Defense | 기본 방어와 대결 | 단순 임계값 방어의 한계 확인 |
| E5 AURA vs TSRA-R | 방어 에이전트와 대결 | 최종 공방 구조 증명 |

E4와 E5는 방어자가 있어야만 의미가 있다. 따라서 MVP부터 최소 rule 기반 TSRA-R을 함께 만든다. ML 기반 TSRA-R은 2차 확장에서 추가한다.

## 16. 실험 결과로 보여줄 숫자

보고서에는 아래 표를 넣는다.

| 실험 | P95 critical latency | stale data ratio | priority inversion | kill chain delay | mission impact |
|---|---:|---:|---:|---:|---:|
| E1 | 낮음 | 낮음 | 낮음 | 낮음 | 낮음 |
| E2 | 중간 | 중간 | 낮음 | 중간 | 중간 |
| E3 | 높음 | 높음 | 높음 | 높음 | 높음 |
| E4 | 중간~높음 | 중간 | 중간 | 중간 | 중간 |
| E5 | 낮음~중간 | 낮음 | 낮음 | 낮음 | 낮음 |

최종 보고서에서는 실제 실행 결과 숫자로 채운다.

예시 목표:

```text
E3에서 E1 대비 mission impact 3배 이상 증가
E5에서 E3 대비 mission impact 50% 이상 감소
TSRA-R 적용 후 P95 critical latency 40% 이상 감소
TSRA-R 적용 후 stale data ratio 50% 이상 감소
```

## 17. 보고서에 넣을 그림과 표

필수:

- AURA 전체 구조도
- AURA 입력/출력 표
- 공격 후보 생성 규칙 표
- Mission Impact Score 계산식
- 공격 이벤트 JSON 예시
- E1~E5 실험 결과 표
- critical latency 비교 그래프
- stale data ratio 비교 그래프
- mission impact 비교 그래프

가능하면 추가:

- 시간대별 공격 선택 로그
- 메시지 큐 변화 그래프
- COP freshness 변화 화면
- 공격-방어 라운드별 공방 흐름도

## 18. 개발 순서

### Step 1. 시뮬레이터 뼈대

먼저 실제 AI 없이 전술 메시지가 링크를 타고 이동하는 시뮬레이터를 만든다.

완료 기준:

- 메시지가 생성된다.
- 링크 큐에 들어간다.
- 대역폭, latency, jitter, loss에 따라 도착 시간이 달라진다.
- 결과 로그가 저장된다.

### Step 2. 공격 효과 적용

시뮬레이터에 공격 이벤트를 적용한다.

완료 기준:

- 특정 시간 동안 SATCOM latency가 증가한다.
- 특정 시간 동안 bandwidth가 낮아진다.
- queue pressure가 발생한다.
- critical message가 늦어지는 것을 로그에서 확인할 수 있다.

### Step 3. AURA v1

점수 기반 AURA를 만든다.

완료 기준:

- 현재 상태를 읽는다.
- 공격 후보를 만든다.
- 후보별 예상 mission impact를 계산한다.
- 가장 높은 점수의 공격을 선택한다.
- 선택 이유를 로그로 남긴다.

### Step 4. 실험 자동화

E1~E5 실험을 명령어 하나로 돌린다.

완료 기준:

```bash
python -m experiments.run_experiment --scenario scenarios/mission_aware_attack.yaml
```

실행 후 생성물:

```text
outputs/logs/attack_events.jsonl
outputs/logs/mission_events.jsonl
outputs/results/experiment_summary.csv
outputs/figures/mission_impact.png
```

### Step 5. 보고서 증거화

결과를 보고서에 넣을 수 있게 정리한다.

완료 기준:

- 공격 이벤트 로그 캡처
- 실험 결과 표
- 그래프 3개
- AURA 구조도
- 코드 스니펫
- 실행 방법 README

## 19. AURA가 똑똑해 보이는 포인트

단순히 랜덤으로 공격하면 안 된다. 아래 행동이 보여야 한다.

- 방공 경보가 곧 올 때 공격 강도를 높인다.
- 영상 트래픽이 많을 때 큐 압박을 선택한다.
- 이미 SATCOM이 나쁘면 무리하게 공격하지 않고 NoOp를 선택한다.
- 방어자가 대체 통신망으로 바꾸면 다음 라운드에서 failover 병목을 노린다.
- 너무 탐지 쉬운 강한 공격보다 자연 혼잡처럼 보이는 공격을 선택한다.
- 공격 결과를 보고 다음 후보의 우선순위를 바꾼다.

## 20. 보고서 문장 초안

아래 문장을 그대로 보고서에 넣을 수 있다.

> AURA는 실제 SATCOM 침해를 수행하는 도구가 아니라, 폐쇄형 C4ISR 통신 시뮬레이터에서 공격 효과를 생성하는 Red Team AI 에이전트이다. AURA는 작전 단계, 링크 상태, 메시지 큐, COP freshness, 방어 에이전트 상태를 관측하고, link degradation, bandwidth limit, queue pressure, critical-window degradation 등 후보 공격 효과를 생성한다. MVP에서는 각 후보의 임무 피해를 큐 지연 근사식으로 예측하고, Critical Message Delay, Stale Data Ratio, Priority Inversion Rate로 구성된 MVP MissionImpactScore에서 DetectabilityScore를 차감해 AttackScore를 계산한다. 2차 확장에서는 TSRA-R의 PACE 전환과 kill chain 모델을 포함해 KillChainDelay와 RecoveryInstability까지 반영한다. AURA와 TSRA-R은 같은 시뮬레이터, 같은 event schema, 같은 JSONL 로그를 공유하며, 공방 결과는 실험별 latency, stale ratio, priority inversion, mission impact로 비교된다.

## 21. 최종 완성 기준

AURA 계획이 실제로 완성됐다고 말하려면 아래가 있어야 한다.

- [ ] AURA의 목적이 한 문장으로 설명된다.
- [ ] 실제 공격이 아니라 시뮬레이션 공격 효과임이 명확하다.
- [ ] 입력 데이터 구조가 정의되어 있다.
- [ ] 출력 attack event 구조가 정의되어 있다.
- [ ] TSRA-R과 공유할 mission event, attack event, defense event 스키마가 정의되어 있다.
- [ ] 공격 액션 종류가 정의되어 있다.
- [ ] 후보 생성 규칙이 있다.
- [ ] MVP MissionImpactScore와 Full MissionImpactScore가 분리되어 있다.
- [ ] AttackScore가 `MissionImpactScore - 0.15 * DetectabilityScore`로 통일되어 있다.
- [ ] 탐지 가능성 패널티가 있다.
- [ ] MVP 구현 범위가 정해져 있다.
- [ ] E4/E5를 위한 최소 rule 기반 TSRA-R 범위가 정해져 있다.
- [ ] 실험 E1~E5가 정해져 있다.
- [ ] 보고서에 넣을 표와 그림이 정해져 있다.
- [ ] README/로그/결과표/그래프 산출물이 정해져 있다.

## 22. 가장 먼저 만들 코드

첫 코드는 AI 모델이 아니라 데이터 모델과 시뮬레이터다.

우선순위:

1. `Message`
2. `LinkState`
3. `AttackCandidate`
4. `AttackEvent`
5. `MissionState`
6. `compute_mission_impact()`
7. `generate_candidates()`
8. `decide_attack()`

이 순서로 만들면 AURA가 추상적인 아이디어가 아니라 실제 실행 가능한 에이전트로 변한다.
