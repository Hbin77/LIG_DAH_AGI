# DAH TSRA/AURA ML 개발 계획

## 1. 결론

ML은 처음부터 크게 넣으면 위험하다. 가장 좋은 전략은 아래 순서다.

```text
1. 공통 시뮬레이터와 로그 스키마를 만든다.
2. AURA v1은 rule/score 기반으로 만든다.
3. TSRA-R v1도 최소 rule 기반으로 만든다.
4. 시뮬레이터를 많이 돌려 학습 데이터를 만든다.
5. ML v1은 AURA의 공격 후보 피해 예측에 넣는다.
6. ML v2는 TSRA-R의 이상 탐지/공격 유형 분류에 넣는다.
7. 마지막에 AURA와 TSRA-R의 ML 적용 전후 성능을 실험표로 보여준다.
```

즉, ML은 시스템의 시작점이 아니라 성능 개선 레이어로 넣는다. 이렇게 해야 구현 가능하고, 보고서에서도 설득력이 있다.

## 2. 먼저 고쳐야 하는 구조

기존 AURA 계획의 가장 큰 구멍은 방어자 TSRA-R이 약하다는 점이다. ML을 넣기 전에 아래 구조를 먼저 고정해야 한다.

```text
Mission Simulator
  |
  |-- AURA: 공격 효과 선택
  |
  |-- TSRA-R: 탐지, 우선순위 재조정, PACE 전환
  |
  |-- Shared Logs: mission_events, attack_events, defense_events
  |
  |-- Metrics: latency, stale ratio, priority inversion, mission impact
```

이 구조가 있어야 E4, E5 실험이 실제로 돌아간다.

## 3. ML을 넣을 위치

ML을 넣을 위치는 3곳이다.

| 위치 | 모델 역할 | 우선순위 |
|---|---|---:|
| AURA Impact Predictor | 공격 후보를 넣으면 예상 mission impact를 예측 | 1순위 |
| TSRA-R Anomaly Detector | 현재 링크/큐/COP 상태가 공격성 저하인지 판단 | 2순위 |
| TSRA-R Defense Policy Ranker | 방어 액션 후보 중 어떤 것이 피해를 가장 줄일지 선택 | 3순위 |

처음에는 AURA Impact Predictor 하나만 ML로 만들어도 충분하다. 그다음 TSRA-R 탐지 모델을 넣으면 보고서에서 "공격 AI와 방어 AI가 모두 존재한다"는 그림이 강해진다.

## 4. 왜 강화학습부터 하면 안 되는가

강화학습은 멋있어 보이지만 지금 단계에서는 비추천이다.

이유:

- 환경 설계가 먼저 완성되어야 한다.
- reward 설계가 어렵다.
- 학습 안정성이 낮다.
- 결과 설명이 어렵다.
- 마감이 가까운 대회 보고서에는 재현성이 더 중요하다.

대신 아래 순서가 현실적이다.

```text
v1: rule/score 기반 AURA, rule 기반 TSRA-R
v2: supervised learning 기반 Impact Predictor
v3: supervised/unsupervised 기반 TSRA-R 탐지 모델
v4: optional contextual bandit
```

강화학습은 보고서의 "향후 계획"에 넣는 것이 좋다.

## 5. 전체 개발 단계

### Phase 0. 공통 스키마 고정

목표:

- AURA와 TSRA-R이 같은 데이터를 읽고 쓰게 만든다.

만들 것:

- `MissionState`
- `Message`
- `LinkState`
- `AttackEvent`
- `DefenseEvent`
- `MetricSnapshot`

로그:

```text
outputs/logs/mission_events.jsonl
outputs/logs/attack_events.jsonl
outputs/logs/defense_events.jsonl
outputs/logs/metric_snapshots.jsonl
```

완료 기준:

- AURA가 만든 `AttackEvent`를 시뮬레이터가 읽을 수 있다.
- TSRA-R이 만든 `DefenseEvent`를 시뮬레이터가 읽을 수 있다.
- 같은 실험에서 공격/방어/임무 로그가 모두 시간순으로 남는다.

### Phase 1. Rule 기반 MVP

목표:

- ML 없이도 전체 공방 실험 E1~E5를 돌릴 수 있게 만든다.

AURA v1:

- 공격 후보 생성
- MVP MissionImpactScore 계산
- DetectabilityScore 차감
- 최고 AttackScore 후보 선택
- `NoOp` 가능

TSRA-R v1:

- stale 객체 표시
- critical message 우선 전송
- SATCOM 저하 탐지
- 대체 링크 전환
- defense event 로그 저장

완료 기준:

- E1: 공격 없음
- E2: 단순 공격
- E3: AURA 공격
- E4: AURA vs Rule Defense
- E5: AURA vs TSRA-R v1

이 5개가 실행되어야 한다.

### Phase 2. 학습 데이터 생성

목표:

- 시뮬레이터를 여러 조건으로 반복 실행해서 ML 학습 데이터를 만든다.

방법:

```text
1. 링크 상태를 랜덤 샘플링한다.
2. 메시지 생성률을 랜덤 샘플링한다.
3. 작전 단계를 랜덤 샘플링한다.
4. 공격 후보를 여러 개 생성한다.
5. 각 후보의 결과를 실행 또는 근사 계산한다.
6. features, candidate, result, label을 저장한다.
```

생성할 데이터:

```text
outputs/datasets/aura_candidate_dataset.csv
outputs/datasets/tsra_detection_dataset.csv
outputs/datasets/defense_policy_dataset.csv
```

권장 규모:

- 초기: 1,000~3,000 rows
- 보고서용: 10,000 rows 이상

데이터 분할:

- train: 70%
- validation: 15%
- test: 15%

주의:

- 같은 scenario seed가 train과 test에 동시에 들어가면 안 된다.
- 랜덤 row split보다 scenario-level split이 안전하다.

### Phase 3. AURA Impact Predictor

목표:

- AURA가 후보 공격의 피해를 근사식이 아니라 ML로 예측하게 만든다.

입력 feature:

| feature 그룹 | 예시 |
|---|---|
| 링크 상태 | SATCOM latency, jitter, loss, bandwidth, queue depth |
| 트래픽 상태 | message count by type, bytes by type, critical ratio, video load |
| 메시지 deadline | min slack, avg slack, critical deadline pressure |
| COP 상태 | average age, max age, stale ratio |
| 작전 단계 | mission phase one-hot |
| 방어 상태 | active route, PACE state, defense mode |
| 공격 후보 | attack type, target link, duration, added latency, bandwidth limit |

예측 label:

```text
y_impact = MVP_MissionImpactScore
```

추천 모델:

| 모델 | 이유 |
|---|---|
| `HistGradientBoostingRegressor` | scikit-learn만으로 가능, 비선형 관계에 강함 |
| `RandomForestRegressor` | 구현 쉬움, feature importance 설명 가능 |
| `Ridge` | 단순 baseline |

평가 지표:

- MAE
- RMSE
- R2
- Top-1 action match rate

보고서에서 보여줄 것:

- rule predictor vs ML predictor MAE 비교
- AURA가 선택한 공격 후보와 실제 mission impact
- feature importance

### Phase 4. TSRA-R Anomaly Detector

목표:

- TSRA-R이 "그냥 혼잡"과 "공격성 저하"를 구분하게 만든다.

입력 feature:

| feature 그룹 | 예시 |
|---|---|
| 링크 변화량 | latency delta, jitter delta, loss delta |
| 큐 변화량 | total queue depth, critical queue depth, video queue depth |
| freshness | stale ratio, max object age |
| priority | priority inversion rate |
| 시간 패턴 | moving average, EWMA residual |

label:

```text
y_attack_present = 0 or 1
y_attack_type = link_degradation / bandwidth_limit / queue_pressure / critical_window_degradation
```

추천 모델:

| 모델 | 용도 |
|---|---|
| `LogisticRegression` | baseline classifier |
| `RandomForestClassifier` | 비선형 탐지 |
| `IsolationForest` | label 부족 시 이상 탐지 |
| EWMA + threshold | rule baseline |

평가 지표:

- precision
- recall
- F1
- false alarm rate
- detection delay

보고서에서 중요한 점:

- 군 환경에서는 오탐이 많으면 안 되므로 false alarm rate를 꼭 보여준다.
- 탐지가 빠른지 보기 위해 detection delay를 보여준다.

### Phase 5. TSRA-R Defense Policy Ranker

목표:

- 방어 액션 후보 중 mission impact를 가장 많이 줄이는 액션을 고른다.

방어 액션 후보:

| 방어 액션 | 설명 |
|---|---|
| `priority_reroute` | critical message 우선 전송 |
| `video_throttle` | 영상 품질/전송량 축소 |
| `pace_switch` | 대체 링크 전환 |
| `stale_badge` | COP 객체 stale 표시 |
| `store_forward_reorder` | 저장 후 재정렬 |
| `no_op` | 방어하지 않음 |

label:

```text
y_resilience_gain = impact_without_defense - impact_with_defense
```

추천 모델:

- `RandomForestRegressor`
- `HistGradientBoostingRegressor`

평가:

- ML 방어 선택 vs rule 방어 선택
- resilience gain
- P95 critical latency 감소율
- stale data ratio 감소율

이 단계는 시간이 부족하면 생략 가능하다. 보고서에는 향후 계획으로 넣어도 된다.

## 6. MVP 점수식과 Full 점수식

### 6.1 MVP 점수식

MVP에서는 PACE 복구 안정성과 kill chain 세부 단계가 아직 약하므로 아래만 사용한다.

```text
MVP_MissionImpactScore =
  0.50 * CriticalLatencyScore
+ 0.30 * StaleDataScore
+ 0.20 * PriorityInversionScore
```

```text
AttackScore =
  MVP_MissionImpactScore
- 0.15 * DetectabilityScore
```

### 6.2 Full 점수식

TSRA-R의 PACE와 kill chain 모델이 들어간 뒤 사용한다.

```text
Full_MissionImpactScore =
  0.35 * CriticalLatencyScore
+ 0.25 * StaleDataScore
+ 0.20 * PriorityInversionScore
+ 0.15 * KillChainDelayScore
+ 0.05 * RecoveryInstabilityScore
```

```text
AttackScore =
  Full_MissionImpactScore
- 0.15 * DetectabilityScore
```

## 7. ML 적용 전후 실험표

보고서에는 아래 표를 채우는 것을 목표로 한다.

| 실험 | AURA | TSRA-R | 목적 |
|---|---|---|---|
| E1 | 없음 | 없음 | 정상 기준 |
| E2 | 고정 공격 | 없음 | 단순 공격 피해 |
| E3 | rule AURA | 없음 | 상황 인식 공격 피해 |
| E4 | rule AURA | rule TSRA-R | 기본 방어 효과 |
| E5 | ML AURA | rule TSRA-R | ML 공격 예측 효과 |
| E6 | ML AURA | ML TSRA-R detector | ML 방어 탐지 효과 |
| E7 | ML AURA | ML TSRA-R policy ranker | 최종 공방 |

시간이 부족하면 E1~E6까지만 해도 된다.

## 8. 개발 우선순위

### 1순위: 무조건 해야 함

- 공통 스키마
- 시뮬레이터
- rule AURA
- rule TSRA-R
- E1~E5 실험
- CSV/JSONL 로그

### 2순위: ML을 넣는다면 여기까지

- 학습 데이터 생성기
- AURA Impact Predictor
- ML AURA vs rule AURA 비교
- feature importance

### 3순위: 시간이 있으면

- TSRA-R Anomaly Detector
- 공격 탐지 F1, false alarm rate, detection delay

### 4순위: 보고서 차별화

- TSRA-R Defense Policy Ranker
- Streamlit 대시보드
- COP freshness 시각화
- 자동 리포트 생성

## 9. 추천 코드 구조

```text
src/
  shared/
    schemas.py
    metrics.py
    event_log.py
    features.py
  simulator/
    mission_simulator.py
    link_model.py
    queue_model.py
    traffic_generator.py
  aura/
    candidate_generator.py
    rule_decision_engine.py
    ml_impact_predictor.py
    attack_event_emitter.py
  tsra_r/
    rule_defender.py
    anomaly_detector.py
    policy_ranker.py
    defense_event_emitter.py
  ml/
    build_dataset.py
    train_aura_impact_model.py
    train_tsra_detector.py
    evaluate_models.py
  experiments/
    run_e1_baseline.py
    run_e2_fixed_attack.py
    run_e3_rule_aura.py
    run_e4_rule_defense.py
    run_e5_ml_aura.py
    run_all.py
```

## 10. 가장 먼저 만들 파일 순서

```text
1. src/shared/schemas.py
2. src/shared/metrics.py
3. src/simulator/mission_simulator.py
4. src/aura/candidate_generator.py
5. src/aura/rule_decision_engine.py
6. src/tsra_r/rule_defender.py
7. src/experiments/run_all.py
8. src/ml/build_dataset.py
9. src/aura/ml_impact_predictor.py
10. src/ml/train_aura_impact_model.py
```

## 11. 보고서에서 ML을 설명하는 방식

보고서에서는 이렇게 설명하면 된다.

> 본 구현은 먼저 rule 기반 AURA와 rule 기반 TSRA-R으로 공통 시뮬레이션 환경을 구성한 뒤, 시뮬레이터에서 생성된 공격 후보와 임무 영향 결과를 학습 데이터로 사용한다. AURA의 ML Impact Predictor는 링크 상태, 메시지 큐, COP freshness, 작전 단계, 공격 후보 파라미터를 입력으로 받아 후보 공격의 MissionImpactScore를 예측한다. 이를 통해 AURA는 모든 후보를 전체 시뮬레이션으로 재실행하지 않고도 높은 피해가 예상되는 공격 효과를 선택할 수 있다. 방어 측 TSRA-R은 rule 기반 방어를 baseline으로 두고, 이후 링크·큐·freshness 변화량을 이용한 ML Anomaly Detector를 추가해 공격성 저하 탐지 성능을 개선한다.

## 12. 제출 전 증거물

보고서와 ZIP에 반드시 넣을 것:

- `attack_events.jsonl`
- `defense_events.jsonl`
- `metric_snapshots.jsonl`
- `aura_candidate_dataset.csv`
- `model_metrics.json`
- ML 학습/검증 결과 표
- feature importance 그래프
- E1~E6 비교 그래프
- README 실행 명령

README 실행 예:

```bash
python -m src.experiments.run_all
python -m src.ml.build_dataset --runs 3000
python -m src.ml.train_aura_impact_model
python -m src.ml.train_tsra_detector
python -m src.ml.evaluate_models
```

## 13. 최종 권장 범위

마감과 구현 가능성을 고려하면 최종 목표는 아래가 적절하다.

```text
필수:
- rule AURA
- rule TSRA-R
- 공통 시뮬레이터
- E1~E5 실험

ML 필수:
- AURA Impact Predictor
- rule AURA 대비 ML AURA 성능 비교

ML 선택:
- TSRA-R Anomaly Detector

향후 계획:
- Defense Policy Ranker
- contextual bandit
- RAG 기반 TTP 설명 생성
- 강화학습 기반 adaptive COA
```

이 정도면 ML을 억지로 넣은 것이 아니라, 공격 후보 평가와 방어 탐지라는 명확한 기능에 넣은 것이 된다.

