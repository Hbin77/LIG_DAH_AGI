# AURA-ML Engineering Record

## 목적

이 문서는 공격 에이전트를 규칙형 `AURA-lite`에서 trained `AURA-ML`로 올린
기술적 이유와 검증 근거를 기록합니다. 구현 범위는 폐쇄형 synthetic
mission-event simulator 내부의 추상 효과 선택으로 제한됩니다.

## 기존 모델을 그대로 쓰지 않은 이유

기존 `hbin` 실험의 공격 모델은 analytic impact estimator가 만든 값을 다시
학습했습니다. 높은 R2는 시뮬레이터의 실제 미래 결과가 아니라 정해진 수식을
근사했다는 뜻입니다. 후보 행을 random split하면 같은 mission state의 다른
후보가 train과 validation에 나뉘는 누수 위험도 있었습니다.

따라서 기존 모델 파일과 수치는 DEV 실행 경로에 병합하지 않았습니다.

## 최종 에이전트 구조

`AURA-ML`은 `src/tsra_agent/attack_agent.py`의 독립 `AgentRuntime`을 사용합니다.

```text
MissionState 관측
-> AgentMemory 조회
-> generate_attack_candidates 도구 실행
-> predict_attack_impacts 도구로 네 후보 일괄 추론
-> rank_attack_candidates 도구로 impact, detectability, 반복 비용 결합
-> AttackAction 또는 NoOp 결정
-> 4-tick bounded commitment를 Memory에 저장
-> 환경 feedback을 같은 DecisionTrace에 연결
```

후보는 `none`, `link_degradation`, `mission_aware_delay`,
`failover_chasing` 네 개입니다. 각 tick의 효과 duration은 1이며, 학습 모델이
선택한 행동은 4 tick 동안 Memory commitment로 집행됩니다. 공격 가능 창 30
tick과 개별 행동 duration을 혼동하지 않습니다.

## 학습 라벨

학습 grain은 "같은 상태에서 평가한 후보 행동 하나"입니다. 각 상태에서 네
후보를 동일 seed, 동일 방어 맥락, 동일 이전 행동 경로로 실행합니다. 후보를
4 tick 적용한 뒤 30-tick horizon의 mission impact를 계산하고, 같은 조건의
NoOp impact를 뺀 값을 라벨로 사용합니다.

```text
label = impact(candidate commitment) - impact(no-op commitment)
```

이 방식은 분석식 출력이 아니라 실제 simulator queue, loss, stale, priority,
PACE, defense reaction을 거친 counterfactual 결과를 사용합니다.

## 데이터 분리와 품질

- train: 10개 seed, 360개 상태, 1,440개 후보 rollout
- validation: 별도 4개 seed, 144개 상태, 576개 후보 rollout
- 총 504개 상태, 2,016개 후보 rollout
- 방어 맥락: none, threshold rule, TSRA-R, TSRA-ML
- feature: 의사결정 시점에 관측 가능한 28개 state/action 값
- train/validation seed overlap: 0
- row random split: 사용하지 않음
- 모델 선택: train seed 내부 `GroupKFold`

validation 행의 16.3194%는 같은 observable feature인데 라벨이 다릅니다. 미래
packet loss의 확률성과 AURA에 노출되지 않은 방어 정책 차이 때문에 발생하는
부분관측 불확실성입니다. 숨은 defense mode를 feature로 넣어 수치를 인위적으로
높이지 않았습니다.

## 모델 선택 결과

`HistGradientBoostingRegressor`와 `ExtraTreesRegressor`를 train seed grouped CV로
비교했고 selection regret가 낮은 ExtraTrees를 채택했습니다. 실시간 4-candidate
추론에서 병렬화 오버헤드를 피하기 위해 번들 모델의 `n_jobs`는 1입니다.

| Validation metric | AURA-ML | Rule ranker | Zero model |
|---|---:|---:|---:|
| Top-1 optimal rate | 0.7361 | 0.3264 | 0.2083 |
| Exact top-1 action match | 0.5694 | 0.1736 | 0.2083 |
| Mean selection regret | 0.3465 | 1.5947 | 2.0089 |
| P95 selection regret | 2.6400 | 4.9800 | 6.4400 |

회귀 MAE는 0.8538, R2는 0.1762입니다. 따라서 이 모델은 정밀한 impact 값
예측기로 주장하지 않습니다. 근거가 있는 주장은 noisy rollout에서 후보 선택
순위를 개선한다는 것입니다.

## 폐루프 30-seed holdout

holdout seed는 train, validation, 10개 정책 확인 seed와 모두 다릅니다. 높은
mission impact가 공격 에이전트 관점에서 더 좋은 결과입니다.

| Defense context | Rule impact | AURA-ML impact | ML-rule | 95% CI | Win |
|---|---:|---:|---:|---:|---:|
| none | 82.2947 | 82.9720 | 0.6773 | [-0.1240, 1.3657] | 23/30 |
| threshold rule | 60.4740 | 80.9177 | 20.4437 | [19.2633, 21.6117] | 30/30 |
| TSRA-R | 17.2787 | 20.3677 | 3.0890 | [2.1193, 4.0370] | 25/30 |
| TSRA-ML | 15.0240 | 19.4317 | 4.4077 | [3.5283, 5.2823] | 29/30 |

무방어 비교의 CI는 0을 포함하므로 우월성을 확정하지 않습니다. 방어가 있는
세 맥락은 lower bound가 모두 0보다 큽니다. zero-model과 비교하면 네 맥락
모두 30/30 seed에서 AURA-ML이 더 높은 impact를 만들었습니다.

## 행동 귀속

DecisionTrace에는 다음을 함께 남깁니다.

- `predicted_incremental_impact`
- `detectability_score`
- `rule_selected_action`
- `zero_model_selected_action`
- `model_influenced`
- `model_changed_rule_choice`
- `selection_source`
- `commitment_ticks`

모델 class를 사용했다는 이유만으로 모든 행동을 ML 기여로 세지 않습니다.
실제 선택이 zero-model 선택과 달라질 때만 `model_influenced=true`입니다.

## 재현 명령

```bash
.venv/bin/python scripts/train_aura_rollout_policy.py
.venv/bin/python scripts/evaluate_aura_policy.py
.venv/bin/python -m src.tsra_agent.cli \
  --scenario hybrid \
  --attack-policy ml \
  --ticks 180 \
  --seed 2003 \
  --output-dir outputs/aura_ml_example
```

주요 artifact:

- `models/aura_rollout_policy.joblib`
- `models/aura_rollout_training_report.json`
- `models/aura_ml_policy_config.json`
- `examples/aura_ml_holdout_30_seed_summary.json`

## 한계

- 모든 라벨과 holdout은 같은 synthetic simulator 계열에서 생성됩니다.
- 실제 SATCOM 환경 정확도나 운용 효과를 의미하지 않습니다.
- 무방어 상황에서 rule 대비 통계적 우월성은 입증되지 않았습니다.
- MPS MLP는 candidate validation에서 ExtraTrees보다 높았지만 threshold-rule 폐루프에서 크게 실패해 기본 실행은 CPU ExtraTrees입니다.
- 실제 RF 제어, exploit, 장비별 침투, live network action은 구현하지 않습니다.

GPU scale 및 승격 탈락 근거는 `docs/aura_mps_scale_experiment.md`에 분리했습니다.
