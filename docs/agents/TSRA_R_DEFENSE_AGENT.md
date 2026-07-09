# TSRA-R 방어 에이전트

정식 명칭:

```text
TSRA-R: Tactical SATCOM Resilience Agent - Responder
```

## 1. 역할

TSRA-R은 AURA가 만든 통신 저하 효과를 관측하고, mission impact를 줄이는 Blue Team 방어 에이전트다.

쉽게 말하면:

> TSRA-R은 중요한 메시지를 먼저 살리고, 오래된 정보가 최신처럼 보이지 않게 만들고, SATCOM이 나빠지면 대체 링크로 바꾸는 방어 에이전트다.

## 2. 방어 목표

TSRA-R의 목표는 SATCOM을 절대 끊기지 않게 만드는 것이 아니다.

현실적 목표:

- critical traffic 지연 최소화
- 영상 트래픽이 경보/명령을 밀어내는 상황 완화
- stale data를 최신 정보로 오인하지 않게 표시
- SATCOM 저하 시 PACE fallback link 사용
- Mission Impact 감소

## 3. 입력

TSRA-R은 AURA와 같은 `MissionState`를 본다.

주요 관측값:

- active link 상태
- SATCOM latency/loss/queue
- critical pending count
- video queue size
- stale data ratio
- priority inversion rate
- recent critical latency

코드:

- `src/tsra_r/rule_defender.py`
- `src/tsra_r/ml_defender.py`

## 4. 출력

TSRA-R은 `DefenseEvent`를 출력한다.

방어 이벤트 예:

```json
{
  "event_id": "def-00001",
  "agent": "TSRA-R",
  "time_sec": 65,
  "action": "priority_reroute",
  "details": {
    "until_sec": 135,
    "reason": "critical traffic waiting behind video load"
  }
}
```

## 5. 방어 액션

| 방어 액션 | 의미 |
|---|---|
| `priority_reroute` | critical traffic을 영상보다 먼저 처리 |
| `video_throttle` | 영상 트래픽 크기 축소 |
| `stale_badge` | 오래된 COP 객체를 신뢰 낮은 정보로 표시 |
| `pace_switch` | SATCOM 저하 시 LTE/Tactical Radio/Mesh 중 fallback 선택 |

## 6. 핵심 지표

TSRA-R 평가에는 `stale_data_ratio`만 쓰면 부족하다.

이유:

- TSRA-R은 오래된 정보를 즉시 제거하지 못한다.
- 대신 오래됐다고 표시해서 지휘소가 최신 정보로 오인하지 않게 한다.

그래서 별도 지표를 둔다.

```text
trusted_stale_exposure
= 지휘소가 stale 정보를 최신으로 신뢰할 위험
```

방어 전:

```text
stale_data_ratio = 0.50
trusted_stale_exposure = 0.50
```

stale badge 방어 후:

```text
stale_data_ratio = 0.50
trusted_stale_exposure = 0.12
```

## 7. ML TSRA-R

ML TSRA-R은 현재 상태가 단순 혼잡인지 공격성 저하인지 분류한다.

입력:

- 링크 변화
- 큐 변화
- stale ratio
- priority inversion
- critical pending count

출력:

```text
attack_present probability
```

성능:

```text
Synthetic holdout best F1 baseline: LogisticRegression, F1 0.980
Deployed closed-loop model: RandomForestClassifier
RandomForest Precision: 0.996
RandomForest Recall: 0.934
RandomForest F1: 0.964
```

RandomForest를 배포 모델로 둔 이유:

- LogisticRegression은 synthetic holdout 점수는 높았지만 실제 폐루프의 큰 queue-pressure 상태에서 detector probability가 낮게 나오는 calibration 문제가 있었다.
- RandomForest는 nonlinear feature interaction을 반영해 실제 시뮬레이터 상태에서 방어 window를 안정적으로 연다.

## 8. 반복 실험 결과

30개 seed 평균:

```text
E3 AURA Attack:           impact 0.914 +- 0.056
E5 AURA + TSRA-R Defense: impact 0.124 +- 0.019
E7 ML AURA + ML TSRA-R Defense: impact 0.135 +- 0.013
```

Resilience Gain:

```text
약 86.4% +- 2.0%
ML/ML reactive defense: 약 85.2% +- 1.8%
```

## 9. 현재 구현 상태

완료:

- rule 기반 priority reroute
- rule 기반 video throttle
- stale badge
- PACE switch
- ML anomaly detector
- ML detector 기반 reactive defense window
- defense event JSONL 로그
- 30-seed 반복 실험

보완할 것:

- PACE switch의 link selection 근거를 더 정교화
- 방어 action별 ablation study
- operator alert 문구 자동 생성
- incident report 자동 생성

## 10. 보고서에서의 주장

보고서에서는 이렇게 주장한다.

> TSRA-R은 AURA와 동일한 시뮬레이터 상태를 관측해 priority reroute, video throttle, stale badge, PACE switch를 수행한다. TSRA-R은 raw stale data를 즉시 제거하지는 못하지만, trusted stale exposure를 낮춰 지휘소가 오래된 정보를 최신 정보로 오인하는 위험을 줄인다.
