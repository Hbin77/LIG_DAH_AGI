# AURA Mac MPS Scale Experiment

## 질문

Mac GPU를 실제 학습에 사용할 수 있는지, 규모를 키운 신경망이 현재
ExtraTrees 공격 정책보다 나은지 검증했습니다. GPU 사용 자체를 성능 근거로
간주하지 않고 candidate validation과 폐루프 승격 게이트를 분리했습니다.

## 환경

- Machine: MacBook Pro, Apple M3 Pro
- GPU: 14-core Apple GPU, Metal 4
- Memory: 18 GB
- Python: 3.14.4
- PyTorch: 2.13.0
- Backend: MPS (`is_built=true`, `is_available=true`)

## 데이터

기존 analytic estimator 데이터는 사용하지 않습니다.
`scripts/train_aura_rollout_policy.py`가 실제 paired simulator rollout으로 만든
동일 dataset을 사용합니다.

- unique train: 1,440 candidate rows, 360 state groups
- unique validation: 576 candidate rows, 144 state groups
- feature count: 28
- train/validation split: seed 단위 완전 분리
- dataset SHA-256: CPU ExtraTrees 학습근거와 일치

`20,000,000`은 서로 다른 후보 개수가 아닙니다. 1,440개 고유 train row를
GPU batch에서 반복한 총 sample-pass입니다.

## 학습 규모

```text
sample-pass per epoch: 1,000,000
epochs: 20
total sample-pass: 20,000,000
batch groups: 8,192
rows per group: 4
elapsed: 11.0838 sec
throughput: 1,804,443.12 sample-pass/sec
```

모델은 28-192-192-96-1 MLP이며 regression SmoothL1과 listwise ranking loss를
함께 사용합니다. 가장 낮은 selection regret를 보인 epoch 6 checkpoint를
선택했습니다.

## Candidate validation

| Metric | MPS MLP | ExtraTrees |
|---|---:|---:|
| Top-1 optimal rate | 0.7986 | 0.7361 |
| Exact top-1 match | 0.6111 | 0.5694 |
| Mean selection regret | 0.2341 | 0.3465 |
| P95 selection regret | 1.3500 | 2.6400 |
| MAE | 0.7650 | 0.8538 |

이 단계에서는 MPS 모델이 우위였습니다. PyTorch checkpoint와 함께 동일한
출력을 만드는 portable NumPy weight export를 생성했고, validation 지표가
소수점 6자리까지 일치하는 것을 확인했습니다.

## Closed-loop promotion gate

candidate validation에 사용하지 않은 10개 정책 개발 seed에서 MPS와
ExtraTrees를 같은 180-tick 환경으로 비교했습니다. 양수는 MPS가 더 높은
mission impact를 만들었다는 뜻입니다.

| Defense context | MPS - ExtraTrees | Win/Tie/Loss |
|---|---:|---:|
| none | +1.0020 | 6/1/3 |
| threshold rule | -37.1930 | 0/0/10 |
| TSRA-R | +6.6280 | 9/0/1 |
| TSRA-ML | +1.7720 | 8/0/2 |

threshold-rule 맥락에서 10/10 seed 모두 크게 열세였습니다. candidate validation
개선이 폐루프 정책의 전체 상태 분포 일반화를 보장하지 않는다는 증거입니다.
사전에 정한 "모든 방어 맥락에서 평균 비열세" 조건을 실패했으므로 새로운
30-seed promotion holdout을 소비하지 않았습니다.

## 결정

- MPS 학습과 scale 실험: 성공
- MPS candidate validation gate: 성공
- MPS closed-loop promotion gate: 실패
- 기본 AURA-ML runtime: `sklearn_extra_trees_regressor` 유지
- MPS model: 연구·후속 DAgger 후보로만 보존

GPU 모델을 기본으로 채택하지 않은 것은 계산 자원 부족 때문이 아니라 실제
폐루프 근거가 나빴기 때문입니다.

## 재현

```bash
.venv/bin/python scripts/train_aura_rollout_policy.py
.venv-gpu/bin/python scripts/train_aura_mps_student.py \
  --device mps \
  --samples-per-epoch 1000000 \
  --epochs 20 \
  --batch-groups 8192
.venv/bin/python scripts/evaluate_aura_mps_candidate.py
```

Artifacts:

- `models/aura_mps_student.pt`
- `models/aura_mps_student_weights.npz`
- `models/aura_mps_student_metrics.json`
- `models/aura_mps_selection_report.json`
