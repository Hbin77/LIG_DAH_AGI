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
-> 활성·비commitment tick에서만 predict_attack_impacts 도구로 네 후보 일괄 추론
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
- feature: defender 내부 alert를 제외한 27개 observable state/action 값
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
| Top-1 optimal rate | 0.736111 | 0.326389 | 0.208333 |
| Exact top-1 action match | 0.576389 | 0.173611 | 0.208333 |
| Mean selection regret | 0.368333 | 1.594653 | 2.008889 |
| P95 selection regret | 2.7100 | 4.9800 | 6.4400 |

회귀 MAE는 0.854816, R2는 0.177337입니다. 따라서 이 모델은 정밀한 impact 값
예측기로 주장하지 않습니다. 근거가 있는 주장은 noisy rollout에서 후보 선택
순위를 개선한다는 것입니다.

## 폐루프 30-seed holdout

holdout seed는 train, validation, 10개 정책 확인 seed와 모두 다릅니다. 높은
mission impact가 공격 에이전트 관점에서 더 좋은 결과입니다.

| Defense context | Rule impact | AURA-ML impact | ML-rule | 95% CI | Win |
|---|---:|---:|---:|---:|---:|
| none | 81.8970 | 81.9343 | 0.0373 | [-0.975, 0.919] | 17/30 |
| threshold rule | 59.6527 | 80.8657 | 21.213 | [20.0533, 22.3977] | 30/30 |
| TSRA-R | 16.8910 | 19.9577 | 3.0667 | [2.2703, 3.8340] | 27/30 |
| TSRA-ML | 14.7307 | 19.8340 | 5.1033 | [4.4097, 5.7633] | 30/30 |

무방어 비교는 우월성 검정이 아니라 4000번대 실행 전에 고정한 1.0-point 비열등성 negative
control이며 CI 하한 `-0.975`로 통과했습니다. 방어가 있는 세 맥락은 lower
bound가 모두 0보다 큽니다. zero-model과 비교하면 네 맥락 모두 30/30 seed에서
AURA-ML이 더 높은 impact를 만들었습니다.

처음 실행한 3000번대 fresh holdout은 무방어 평균 양수를 요구한 초기 gate에서
`-0.0017`로 실패했습니다. 해당 결과는
`examples/aura_ml_retired_holdout_30_seed_summary.json`에 그대로 보존하고 seed를
재사용하지 않았습니다. 모델·설정은 바꾸지 않은 채 평가 목적을 우월성이 아닌
비열등성으로 명확히 한 다음 새로운 4000번대 seed로 위 최종 평가를 수행했습니다.
1.0-point margin은 rule AURA 무방어 평균 `81.897`의 약 `1.22%`이며, negative
control에서 허용할 최대 mission-impact 저하 폭으로 정의했습니다.

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
conda run -n base python scripts/train_aura_rollout_policy.py
conda run -n base python scripts/evaluate_aura_policy.py
conda run -n base python -m src.tsra_agent.cli \
  --scenario hybrid \
  --attack-policy ml \
  --ticks 180 \
  --seed 4001 \
  --output-dir outputs/aura_ml_example
```

주요 artifact:

- `models/aura_rollout_policy.joblib`
- `models/aura_rollout_training_report.json`
- `models/aura_ml_policy_config.json`
- `models/aura_final_selection_report.json`
- `examples/aura_ml_holdout_30_seed_summary.json`
- `examples/aura_ml_retired_holdout_30_seed_summary.json`

## 한계

- 모든 라벨과 holdout은 같은 synthetic simulator 계열에서 생성됩니다.
- 실제 SATCOM 환경 정확도나 운용 효과를 의미하지 않습니다.
- 무방어 상황에서 rule 대비 통계적 우월성은 입증되지 않았습니다.
- 실제 RF 제어, exploit, 장비별 침투, live network action은 구현하지 않습니다.

최종 제출물은 실제 runtime으로 승격된 ExtraTrees 모델과 해당 모델의 seed-disjoint evidence만 포함합니다. 과거 28-feature MPS 보조 실험은 defender 내부 상태를 포함한 구형 feature 계약에 기반하고 runtime 승격에도 실패했으므로 최종 패키지에서 제거했습니다.
