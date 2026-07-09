# AURA 공격 에이전트

정식 명칭:

```text
AURA: Adversarial SATCOM Reconnaissance & Effects Agent
```

## 1. 역할

AURA는 실제 SATCOM을 공격하는 도구가 아니다.

AURA는 폐쇄형 C4ISR/SATCOM 시뮬레이터 안에서 공격 효과를 선택하는 Red Team 에이전트다.

쉽게 말하면:

> AURA는 현재 작전 상황을 보고, 어떤 통신 병목을 만들면 지휘소 판단이 가장 늦어지는지 고르는 공격 효과 선택기다.

## 2. 공격 경계

AURA가 하지 않는 것:

- 실제 RF 송신
- 실제 재밍
- 실제 스푸핑
- exploit code
- 특정 장비 침투 절차
- 실제 네트워크 패킷 공격
- 운용 가능한 주파수/출력/빔 파라미터

AURA가 하는 것:

- 시뮬레이터 안에서 latency 증가
- 시뮬레이터 안에서 jitter 증가
- 시뮬레이터 안에서 packet loss 증가
- 시뮬레이터 안에서 bandwidth 제한
- 시뮬레이터 안에서 queue pressure 생성
- critical traffic이 밀릴 수 있는 타이밍 선택

## 3. 입력

AURA는 `MissionState`를 입력으로 받는다.

주요 필드:

- 현재 시간
- 작전 단계
- active link
- 링크별 bandwidth, latency, jitter, loss
- 메시지 큐 크기
- critical pending count
- video queue size
- stale data ratio
- 최근 critical latency
- priority inversion rate
- defense mode

코드:

- `src/shared/schemas.py`

## 4. 출력

AURA는 `AttackEvent`를 출력한다.

출력 예:

```json
{
  "event_id": "atk-00001",
  "agent": "AURA",
  "selected_at": 60,
  "candidate": {
    "attack_type": "queue_pressure",
    "target_link": "SATCOM",
    "duration_sec": 80
  },
  "expected_impact": {
    "mission_impact": 0.56
  },
  "reason": "increase non-critical queue occupancy"
}
```

코드:

- `src/aura/rule_decision_engine.py`
- `src/aura/ml_impact_predictor.py`

## 5. 공격 액션

현재 구현된 공격 액션:

| 공격 액션 | 의미 |
|---|---|
| `link_degradation` | 링크 전반의 latency/jitter/loss 증가 |
| `bandwidth_limit` | 사용 가능 대역폭 제한 |
| `queue_pressure` | 영상/텔레메트리 트래픽으로 큐 점유 |
| `critical_window_degradation` | 방공 경보 등 중요한 시점에 저하 집중 |
| `stale_cop_induction` | COP update traffic 지연 유도 |
| `failover_chasing` | 방어자의 PACE 전환 후 fallback link 병목 유도 |

## 6. 판단 방식

현재 AURA는 두 방식이 있다.

### 6.1 Rule AURA

순서:

```text
1. MissionState 관측
2. 공격 후보 생성
3. 후보별 예상 Mission Impact 계산
4. DetectabilityScore 차감
5. AttackScore가 가장 높은 후보 선택
6. AttackEvent 기록
```

공식:

```text
AttackScore = MissionImpactScore - 0.15 * DetectabilityScore
```

### 6.2 ML AURA

ML AURA는 후보별 impact를 `aura_impact_model.pkl`로 예측한다.

학습 대상:

```text
입력: 링크 상태, 큐 상태, 작전 단계, 공격 후보 파라미터
출력: 예상 MissionImpactScore
```

성능:

```text
Best model: HistGradientBoostingRegressor
MAE: 0.011
R2: 0.988
Top-1 action match: 0.904
```

## 7. GPU-scale 실험

추가 실험으로 Apple M3 Pro GPU / PyTorch MPS 기반 MLP도 구현했다.

목적:

- 대규모 synthetic attack candidate 학습 확장성 확인

결과:

```text
20,000,000 synthetic candidates
MAE: 0.0052
R2: 0.995
Throughput: 약 1,566,851 samples/sec
```

주의:

- GPU MLP는 기본 공방 정책 모델이 아니라 확장성 실험이다.
- Top-1 action match는 scikit-learn gradient boosting이 더 안정적이다.

## 8. 현재 구현 상태

완료:

- 공격 후보 생성
- rule 기반 공격 선택
- ML 기반 impact predictor
- GPU MPS MLP 확장 실험
- attack event JSONL 로그
- 30-seed 반복 실험

보완할 것:

- 공격 후보 설명을 COA card 형태로 자동 생성
- attack graph 시각화
- SPARTA/NIST TTP mapping을 후보 생성 근거에 연결
- ML AURA가 실제 공방 결과에서 rule 대비 어떤 장점이 있는지 더 뚜렷하게 비교

## 9. 보고서에서의 주장

보고서에서는 이렇게 주장한다.

> AURA는 실제 위성통신 침해를 수행하지 않고, 폐쇄형 C4ISR/SATCOM 시뮬레이터 내에서 공격 효과를 생성한다. AURA는 작전 단계, 링크 상태, 메시지 큐, COP freshness를 관측해 공격 후보를 만들고, MissionImpactScore가 가장 높은 공격 효과를 선택한다.

