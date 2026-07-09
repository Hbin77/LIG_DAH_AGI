# 구현 결과 요약

## 구현 범위

현재 구현은 실제 공격 도구가 아니라 폐쇄형 C4ISR/SATCOM 시뮬레이터다.

구현된 구성:

- AURA rule 공격 에이전트
- AURA ML Impact Predictor
- AURA GPU-scale MPS MLP Impact Predictor
- TSRA-R rule 방어 에이전트
- TSRA-R ML Anomaly Detector
- 공통 mission/attack/defense/metric JSONL 로그
- E1~E7 공방 실험
- 30-seed 반복 실험
- Resilience Gain 산출
- 시간축 공방 그래프
- Attack/Defense 이벤트 타임라인 표
- 실험 결과 CSV 및 그래프

## 실험 구성

| 실험 | AURA | TSRA-R | 목적 |
|---|---|---|---|
| E1 | 없음 | 없음 | 정상 baseline |
| E2 | 고정 공격 | 없음 | 단순 공격 피해 확인 |
| E3 | rule AURA | 없음 | 상황 인식 공격 효과 |
| E4 | rule AURA | basic rule defense | 기본 방어 효과 |
| E5 | rule AURA | full rule TSRA-R | PACE 포함 방어 효과 |
| E6 | ML AURA | full rule TSRA-R | ML 공격 후보 예측 효과 |
| E7 | ML AURA | ML TSRA-R | ML 공격/방어 공방 |

## 최신 실행 결과

`python3 -m src.experiments.run_all` 실행 결과:

```text
E1_baseline: impact=0.455, p95=3.00s, stale=0.50, trusted_stale=0.50, inv=0.32
E2_fixed_attack: impact=0.665, p95=28.50s, stale=0.50, trusted_stale=0.50, inv=0.57
E3_rule_aura: impact=0.950, p95=168.00s, stale=0.50, trusted_stale=0.50, inv=0.83
E4_rule_aura_basic_defense: impact=0.093, p95=2.00s, stale=0.50, trusted_stale=0.12, inv=0.02
E5_rule_aura_tsra_r: impact=0.133, p95=1.00s, stale=0.50, trusted_stale=0.12, inv=0.02
E6_ml_aura_tsra_r: impact=0.147, p95=2.00s, stale=0.50, trusted_stale=0.12, inv=0.03
E7_ml_aura_ml_tsra_r: impact=0.155, p95=2.00s, stale=0.50, trusted_stale=0.12, inv=0.05
```

해석:

- E3에서 AURA가 critical latency와 priority inversion을 크게 악화시킨다.
- E4~E7에서 TSRA-R이 critical latency와 priority inversion을 낮춘다.
- TSRA-R은 raw stale data 자체를 모두 제거하지는 못하지만, stale badge를 통해 `trusted_stale_exposure`를 0.50에서 0.12로 낮춘다.
- ML TSRA-R은 full rule 방어를 항상 실행하는 방식이 아니라, anomaly detector가 공격성 저하를 탐지했을 때 방어 window를 여는 reactive 방식으로 동작한다. 이 때문에 E7은 E6와 동일하지 않으며, 탐지 모델의 판단이 실제 폐루프 결과에 반영된다.

## 30-seed 반복 실험 결과

`python3 -m src.experiments.run_batch` 실행 결과:

| 실험 | Mission Impact 평균 | 표준편차 |
|---|---:|---:|
| E1 Baseline | 0.458 | 0.014 |
| E2 Fixed Attack | 0.695 | 0.077 |
| E3 Rule AURA | 0.914 | 0.056 |
| E4 Rule AURA + Basic Defense | 0.107 | 0.016 |
| E5 Rule AURA + TSRA-R | 0.157 | 0.029 |
| E6 ML AURA + TSRA-R | 0.149 | 0.013 |
| E7 ML AURA + ML TSRA-R | 0.166 | 0.012 |

Resilience Gain:

```text
E4 Basic Defense: 88.3% +- 1.8%
E5 TSRA-R:        82.7% +- 3.6%
E6 ML AURA/TSRA:  83.6% +- 1.5%
E7 ML/ML:         81.8% +- 1.8%
```

계산식:

```text
Resilience Gain = (E3 AURA Attack Impact - Defended Impact) / E3 AURA Attack Impact
```

보고서 문장:

> 30개 seed 반복 실험에서 AURA는 Mission Impact를 평균 0.914까지 증가시켰고, TSRA-R 적용 시 Mission Impact는 평균 0.157로 감소했다. 이는 AURA 공격 대비 약 82.7%의 Resilience Gain에 해당한다.

## ML 성능

AURA Impact Predictor:

- best model: HistGradientBoostingRegressor
- MAE: 약 0.011
- R2: 약 0.988
- Top-1 action match rate: 약 0.904

TSRA-R Anomaly Detector:

- deployed model: RandomForestClassifier
- precision: 약 0.996
- recall: 약 0.934
- F1: 약 0.964
- note: LogisticRegression baseline은 synthetic holdout F1이 약 0.980으로 높지만, 실제 폐루프 시뮬레이션의 큰 queue-pressure 상태에서 calibration이 불안정했다. 따라서 폐루프 방어용 배포 모델은 nonlinear RandomForest로 고정했다.

AURA GPU-scale MPS MLP:

- device: Apple Silicon MPS
- torch: 2.13.0
- 학습 규모: 1,000,000 synthetic attack candidates/epoch x 20 epochs = 20,000,000 sample-passes
- batch size: 32,768
- throughput: 약 1,566,851 samples/sec
- MAE: 약 0.0052
- RMSE: 약 0.0094
- R2: 약 0.995
- Top-1 action match rate: 약 0.749

주의:

- 위 ML 성능은 본 시뮬레이터가 생성한 합성 데이터 기준이다.
- 실제 군 통신망 성능을 주장하는 수치가 아니라, 프로토타입 환경 내 검증 결과로 보고서에 명시해야 한다.
- GPU MLP는 대규모 synthetic 후보 학습 가능성을 보이기 위한 선택 실험이다. 회귀 정밀도는 높지만 action selection 정확도는 HistGradientBoosting/RandomForest 계열이 더 안정적이므로, 최종 공방 실험에는 설명 가능성과 안정성이 높은 scikit-learn 모델을 기본값으로 사용한다.

## E4와 E5 해석

E4 basic defense가 Mission Impact 하나만 보면 E5 TSRA-R보다 약간 낮게 나온다. 이는 E4가 PACE 전환을 하지 않고 단순 priority/video/stale 정책만 강하게 적용하기 때문이다.

TSRA-R의 가치는 단일 impact 최소화만이 아니라 다음에 있다.

- `pace_switch`를 통해 SATCOM 저하 시 fallback link를 사용하는 적응성
- `trusted_stale_exposure` 감소를 통한 지휘소 오인 위험 축소
- `defense_events.jsonl`에 남는 operator-action trace
- ML detector와 결합 가능한 reactive defense window

따라서 보고서에서는 E5를 "항상 최소 impact를 내는 규칙 집합"이 아니라, PACE와 stale trust annotation까지 포함한 운용형 방어 아키텍처로 설명한다.

## 보고서에 넣을 증거 파일

- `outputs/experiments/experiment_summary.csv`
- `outputs/batch/repeated_experiment_summary.csv`
- `outputs/batch/resilience_gain_summary.csv`
- `outputs/models/aura_impact_model_metrics.json`
- `outputs/models/tsra_detector_metrics.json`
- `outputs/models/aura_mps_mlp_metrics.json`
- `outputs/figures/mission_impact.png`
- `outputs/figures/critical_latency.png`
- `outputs/figures/priority_inversion.png`
- `outputs/figures/stale_data_ratio.png`
- `outputs/figures/trusted_stale_exposure.png`
- `outputs/figures/E3_rule_aura_timeline.png`
- `outputs/figures/E5_rule_aura_tsra_r_timeline.png`
- `outputs/figures/E7_ml_aura_ml_tsra_r_timeline.png`
- `outputs/figures/aura_tsra_architecture.png`
- `outputs/figures/batch_mission_impact_errorbar.png`
- `outputs/figures/batch_resilience_gain.png`
- `outputs/figures/aura_mps_mlp_training_loss.png`
- `outputs/report_tables/E5_rule_aura_tsra_r_event_timeline.md`
- `outputs/report_tables/ml_model_comparison.md`
- 각 실험별 `attack_events.jsonl`
- 각 실험별 `defense_events.jsonl`
- 각 실험별 `metric_snapshots.jsonl`

## 보고서에서 강조할 포인트

1. AURA는 실제 공격 도구가 아니라 폐쇄형 시뮬레이터에서 공격 효과를 생성하는 Red Team 에이전트다.
2. TSRA-R은 단순 탐지가 아니라 priority reroute, video throttle, stale badge, PACE switch를 수행한다.
3. `stale_data_ratio`와 `trusted_stale_exposure`를 분리해 방어 의미를 정확히 보여준다.
4. 단일 seed가 아니라 30-seed 반복 실험으로 평균과 표준편차를 제시한다.
5. ML은 AURA 후보 영향 예측과 TSRA-R 이상 탐지에 사용했고, GPU MPS 실험은 대규모 synthetic 학습 확장성 근거로 제시한다.
