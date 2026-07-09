# GitHub 작업 원칙

## 브랜치 원칙

- 작업 브랜치: `hbin`
- 보호/기본 브랜치: `main`
- 원격 저장소: `https://github.com/Hbin77/LIG_DAH_AGI.git`
- `main` 브랜치는 삭제하지 않고 보존한다.
- `main` 브랜치에는 개발 산출물을 직접 push하지 않는다.
- 모든 개발 기록, 실험 근거, 문서 수정은 `hbin` 브랜치에 커밋한다.

현재 운영 방식:

```text
main: GitHub 기본 브랜치. 보호용 README만 둔다.
hbin: 실제 개발 브랜치. 코드, 실험 결과, 보고서 문서를 계속 갱신한다.
```

이렇게 분리하는 이유는 두 가지다.

1. `main`을 안정적인 기본 브랜치로 남겨 저장소 구조가 깨지지 않게 한다.
2. 대회 개발 과정의 모든 변경 이력은 `hbin`에서만 추적해 main 오염을 막는다.

## 커밋 원칙

커밋은 다음 기준으로 나눈다.

1. 실행 가능한 코드 단위
2. 에이전트 설계 문서 단위
3. 실험 결과/보고서 자산 단위
4. README/제출 문서 정리 단위

각 커밋 메시지는 무엇을 왜 바꿨는지 드러나야 한다.

예:

```text
Implement AURA attack-effect agent baseline
Document TSRA-R defense policy and evidence flow
Add repeated experiment summaries and report figures
```

## GitHub에 올리는 것

올린다:

- `src/`: 실행 코드
- `docs/`: 설계, 근거, 보고서 요약
- `README.md`
- `requirements.txt`, `requirements-gpu.txt`
- `outputs/batch/repeated_experiment_summary.csv`
- `outputs/batch/resilience_gain_summary.csv`
- `outputs/report_tables/*.md`, `*.csv`
- `outputs/figures/*.png`
- `outputs/models/*_metrics.json`

올리지 않는다:

- `.venv-gpu/`
- `__pycache__/`
- 대량 seed별 raw log
- 대량 synthetic dataset CSV
- model binary `.pkl`, `.pt`

이유:

- raw log와 dataset은 코드로 재생성 가능하다.
- model binary는 GitHub repo를 불필요하게 무겁게 만든다.
- 보고서 검증에 필요한 것은 요약 CSV, 메트릭 JSON, 그래프, 재현 명령이다.

## 재현 명령

```bash
python3 -m src.ml.build_dataset --rows 3000
python3 -m src.ml.train_aura_impact_model
python3 -m src.ml.train_tsra_detector --rows 5000
python3 -m src.experiments.run_all
python3 -m src.experiments.run_batch
```

GPU-scale 실험:

```bash
python3 -m venv .venv-gpu
.venv-gpu/bin/python -m pip install --upgrade pip
.venv-gpu/bin/python -m pip install -r requirements-gpu.txt
.venv-gpu/bin/python -m src.ml.train_aura_mps_mlp --device mps --samples 1000000 --epochs 20 --batch-size 32768 --eval-samples 120000 --top1-groups 1500
```
