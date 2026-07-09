# Mac GPU-Scale AURA MLP 실험

## 목적

기존 AURA Impact Predictor는 scikit-learn 기반 CPU 모델이다. 데이터가 작을 때는 이 방식이 더 단순하고 설명 가능하다.

하지만 GPU 사용 근거를 만들기 위해, Apple Silicon MPS에서 대규모 synthetic attack candidate를 온라인 생성하고 MLP로 `MissionImpactScore`를 학습하는 선택 실험을 추가했다.

## 환경

```text
Machine: Apple M3 Pro
GPU: 14-core Apple GPU
Backend: PyTorch MPS
Python: 3.14
torch: 2.13.0
```

## 실행 명령

```bash
.venv-gpu/bin/python -m src.ml.train_aura_mps_mlp \
  --device mps \
  --samples 1000000 \
  --epochs 20 \
  --batch-size 32768 \
  --eval-samples 120000 \
  --top1-groups 1500
```

## 최신 결과

```json
{
  "mae": 0.005236480850726366,
  "rmse": 0.009371194988489151,
  "r2": 0.9951224327087402,
  "top1_action_match_rate": 0.7486666666666667,
  "device": "mps",
  "torch_version": "2.13.0",
  "train_samples_per_epoch": 1000000,
  "epochs": 20,
  "batch_size": 32768,
  "elapsed_sec": 12.764454416930676,
  "samples_per_sec": 1566851.143553159
}
```

## 해석

- GPU MLP는 100만 개 synthetic 후보를 20 epoch 반복해 총 2천만 sample-pass를 약 13초에 학습했다.
- R2는 약 0.995로 impact regression 성능은 높다.
- Top-1 action match는 약 0.749로, action selection에서는 scikit-learn tree 계열 모델이 더 안정적이다.
- 보고서에서는 `scikit-learn gradient boosting`을 기본 impact predictor로 두고, GPU MLP는 대규모 synthetic 학습 처리량과 회귀 확장성 실험으로 제시하는 것이 가장 안전하다.

## 산출물

- `outputs/models/aura_mps_mlp.pt`
- `outputs/models/aura_mps_mlp_metrics.json`
- `outputs/figures/aura_mps_mlp_training_loss.png`
