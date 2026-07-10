# TSRA-X / AURA DAH 2026 Agent Package

DAH 2026 Hybrid SATCOM Disruption 시나리오용 실행 가능한 AI 공방 에이전트 프로토타입입니다. 공격·방어 판단, 폐쇄형 mission-event simulator, 훈련된 공격·방어 모델, 판단 trace, 반복 검증을 한 패키지에서 재현합니다.

이 패키지는 실제 SATCOM 침투, 장비별 절차, 운용 가능한 RF 파라미터, exploit code를 포함하지 않습니다. `AURA-lite`와 `AURA-ML`은 폐쇄형 synthetic mission-event simulator에서 추상 공격 효과만 생성하고, `TSRA-R-lite`와 `TSRA-ML`은 C4ISR 데이터 신뢰성 붕괴를 탐지·완화합니다.

## 구성

- `src/tsra_agent/attack_agent.py`: rule `AURA-lite`와 trained `AURA-ML`을 실행하는 독립 공격 `AgentRuntime`
- `src/tsra_agent/attack_ml_policy.py`: 28-feature rollout-impact 모델 계약, loader, zero-model ablation
- `src/tsra_agent/defense_agent.py`: rule, `TSRA-R-lite`, `TSRA-ML` 모드를 같은 런타임 계약으로 실행하는 방어 에이전트
- `src/tsra_agent/agents.py`: 공격 후보 점수화, TSRA-R risk fusion, TSRA-ML trained-policy primitive
- `src/tsra_agent/ml_policy.py`: synthetic training-data generator, scikit-learn model loader, standard-library logistic fallback
- `src/tsra_agent/simulator.py`: UAV/UGV/SATCOM/PACE mission event simulator
- `src/tsra_agent/evaluator.py`: latency, stale ratio, priority inversion, backlog, false alarm, resilience gain 평가
- `src/tsra_agent/cli.py`: 단일/다중 seed 실험 실행 및 산출물 생성
- `src/tsra_agent/runtime.py`: 실제 callable tool 실행, bounded memory, decision commit, environment feedback을 소유하는 `AgentRuntime`
- `models/`: trained AURA-ML ExtraTrees rollout ranker, TSRA-ML histogram gradient-boosting model, policy config와 provenance
- `scripts/train_aura_rollout_policy.py`: paired simulator rollout 라벨 생성, seed-grouped model selection, AURA-ML 학습
- `scripts/evaluate_aura_policy.py`: rule/ML/zero-model AURA를 4개 방어 맥락의 독립 30-seed에서 비교
- `scripts/train_aura_mps_student.py`: Apple MPS에서 rollout-labeled listwise ranking MLP 대규모 학습
- `scripts/evaluate_aura_mps_candidate.py`: MPS 모델의 폐루프 runtime 승격 게이트
- `scripts/train_sklearn_policy.py`: primary TSRA-ML model training and independent simulator-trajectory validation script
- `scripts/train_ml_policy.py`: dependency-free logistic fallback training script
- `scripts/tune_ml_policy.py`: mission simulator 기반 TSRA-ML action gate 튜닝 스크립트
- `docs/agent_engineering_notes.md`: 에이전트 정의, 기술 선택, ML 행동 귀속, 브랜치 운영 판단 기록
- `docs/aura_ml_engineering_record.md`: 공격 ML의 라벨, 데이터 품질, ablation, holdout 판단 근거
- `docs/aura_mps_scale_experiment.md`: Mac GPU 처리량, validation, 폐루프 탈락 근거
- `docs/`: 아키텍처, 평가 계획, 안전 경계
- `docs/report_writer_guide.md`: 보고서 담당자가 결과물, 수치, 안전 경계, 복붙 가능한 문장을 이해하기 위한 작성 가이드
- `examples/`: 5-seed development 결과와 독립 30-seed post-tuning holdout 요약
- `tests/`: 표준 라이브러리 `unittest` 회귀 테스트

## 실행

ML 모델은 `models/aura_rollout_policy.joblib`과 `models/tsra_sklearn_policy.joblib`에 훈련된 상태로 포함되어 있습니다. 재훈련이 필요하면 아래를 실행합니다.

번들된 scikit-learn 모델은 `scikit-learn 1.9.x` 계열에서 로드하는 것을 기준으로 합니다. 실행 전 `pip install -r requirements.txt` 또는 같은 버전대가 설치된 Conda 환경을 사용하세요.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/train_sklearn_policy.py --samples 100000
.venv/bin/python scripts/train_aura_rollout_policy.py
```

scikit-learn 없는 환경을 위한 fallback 모델 재훈련:

```bash
.venv/bin/python scripts/train_ml_policy.py --samples 10000 --epochs 260
```

TSRA-ML action gate 재튜닝:

```bash
.venv/bin/python scripts/tune_ml_policy.py \
  --candidates 16 \
  --ticks 180 \
  --tune-seeds 7,11,19 \
  --validation-seeds 23,31
```

```bash
.venv/bin/python -m src.tsra_agent.cli \
  --scenario hybrid \
  --ticks 180 \
  --seeds 7,11,19,23,31 \
  --output-dir outputs/final_run
```

같은 전체 실험군을 trained `AURA-ML` 공격 정책으로 실행:

```bash
.venv/bin/python -m src.tsra_agent.cli \
  --scenario hybrid \
  --attack-policy ml \
  --ticks 180 \
  --seeds 2003,2011,2017 \
  --output-dir outputs/aura_ml_run
```

Mac MPS 보조 모델 재현은 먼저 CPU rollout dataset을 만든 다음 별도 PyTorch
환경에서 실행합니다. 이 모델은 validation ranking은 높지만 폐루프 승격 게이트를
통과하지 못해 기본 runtime에는 사용하지 않습니다.

```bash
python3 -m venv .venv-gpu
.venv-gpu/bin/python -m pip install -r requirements-gpu.txt
.venv/bin/python scripts/train_aura_rollout_policy.py
.venv-gpu/bin/python scripts/train_aura_mps_student.py --device mps
.venv/bin/python scripts/evaluate_aura_mps_candidate.py
```

생성 파일:

- `summary.json`: seed별/평균 지표
- `incident_report.md`: 보고서에 붙일 수 있는 실행 요약
- `run_manifest.json`: 산출물 구조와 안전 경계
- `seed_<seed>/*_events.jsonl`: 실험별 이벤트 로그
- `seed_<seed>/*_decision_traces.jsonl`: AURA/TSRA-R 판단 trace 로그

보고서용으로 trace를 평탄화한 표가 필요하면 다음 명령을 사용합니다.

```bash
.venv/bin/python scripts/summarize_decision_traces.py \
  --input-dir outputs/final_run \
  --output-csv outputs/final_run/report_tables/decision_trace_summary.csv \
  --output-md outputs/final_run/report_tables/decision_trace_summary.md
```

생성된 CSV/Markdown은 seed, 실험군, tick, 에이전트, 선택 행동, 후보 수, 도구 호출, 판단 이유를 한 표로 정리합니다. 이 요약기는 DEV 품질 게이트의 CLI smoke 검증에도 포함됩니다.

## 검증

```bash
.venv/bin/python -m unittest discover -s tests -v
```

최종 제출 전 DEV 브랜치 품질 게이트:

```bash
.venv/bin/python scripts/verify_submission_state.py --require-dev --require-clean
```

이 로컬 검증은 unit test뿐 아니라 CLI smoke run, DecisionTrace 요약표, structured tool-call schema, AURA-ML rollout 모델과 30-seed ablation, TSRA-ML risk basis, 모델 해시, 안전 경계, 제출 ZIP 포함 파일까지 함께 확인합니다.

현재 검증 기준 결과는 `examples/summary_multi_seed.json`에 고정했습니다.

5-seed development 기준 평균값:

- attacked mission impact: `82.162`
- rule defense mission impact: `61.228`
- TSRA-R adaptive defense mission impact: `15.306`
- TSRA-ML adaptive defense mission impact: `12.926`
- TSRA-ML zero-model ablation mission impact: `15.180`
- learned-model impact contribution in this simulator: `2.254`
- attacked priority inversion rate: `0.0629`
- TSRA-R priority inversion rate: `0.0`
- TSRA-ML priority inversion rate: `0.0`
- TSRA-ML compressed snapshot messages: `43.8`
- TSRA-ML deferred messages: `9.2`
- TSRA-ML backlog messages: `0.0`
- TSRA-ML expired messages: `0.0`
- TSRA-R detection time: `1` tick
- TSRA-R adaptive recovery time: `3` ticks after first alert stabilization
- TSRA-ML recovery time: `1` tick after first alert stabilization
- guarded baseline false alarm rate: `0.0`
- TSRA-R adaptive baseline-adjusted resilience gain: `90.374%`
- TSRA-ML adaptive baseline-adjusted resilience gain: `93.600%`
- TSRA-R defense intervention ticks: `134.4`
- TSRA-ML defense intervention ticks: `116.0`
- TSRA-R priority-boost ticks: `118.0`
- TSRA-ML priority-boost ticks: `97.2`
- TSRA-ML model-influenced ticks: `83.8`
- TSRA-ML synthetic holdout F1: `0.9884`
- TSRA-ML synthetic holdout ROC-AUC: `0.9995`
- TSRA-ML attacked-trajectory oracle F1: `0.9972`
- TSRA-ML TSRA-defended-trajectory oracle F1: `0.9771`

독립 30-seed post-tuning holdout:

- TSRA-R mission impact: `16.2180`
- TSRA-ML mission impact: `15.3187`
- zero-model ablation mission impact: `16.9810`
- TSRA-ML resilience gain: `91.0330%`
- TSRA-R 대비 paired mean improvement: `0.8993` (`22/30` seed win)
- zero-model ablation 대비 paired mean improvement: `1.6623` (`22/30` seed win)
- bootstrap 95% interval: `[0.1500, 1.6387]`, `[0.7063, 2.7050]`

AURA-ML 독립 30-seed holdout은 모델 학습·validation·정책 확인에 사용하지 않은 seed를 사용합니다. 높은 mission impact가 공격 에이전트 관점의 우수한 결과입니다.

- candidate validation top-1 optimal rate: `0.7361` (rule ranker `0.3264`)
- candidate validation mean selection regret: `0.3465` (rule ranker `1.5947`)
- versus rule defense: `+20.4437`, bootstrap 95% CI `[19.2633, 21.6117]`
- versus TSRA-R: `+3.0890`, bootstrap 95% CI `[2.1193, 4.0370]`
- versus TSRA-ML: `+4.4077`, bootstrap 95% CI `[3.5283, 5.2823]`
- versus zero-model: 모든 방어 맥락에서 `30/30` seed 우세
- no-defense comparison: 평균 `+0.6773`, CI `[-0.1240, 1.3657]`; 통계적 우월성은 주장하지 않음

Mac MPS scale 결과:

- Apple M3 Pro 14-core GPU, PyTorch MPS
- 고유 rollout train row: `1,440`; 2천만 개의 서로 다른 후보가 아님
- 1,000,000 sample-pass/epoch x 20 epoch = `20,000,000` sample-pass
- elapsed: `11.0838s`, throughput: `1,804,443.12 sample-pass/s`
- validation top-1: MPS `0.7986` > ExtraTrees `0.7361`
- validation mean regret: MPS `0.2341` < ExtraTrees `0.3465`
- 폐루프 promotion gate: threshold-rule 맥락 `-37.1930` impact로 실패
- runtime 선택: `sklearn_extra_trees_regressor` 유지

재현:

```bash
.venv/bin/python scripts/evaluate_aura_policy.py
```

Holdout 재현은 모델 학습·정책 튜닝에 쓰지 않은 seed로 전체 CLI를 실행한 뒤 compact 요약을 생성합니다.

```bash
.venv/bin/python -m src.tsra_agent.cli \
  --scenario hybrid \
  --ticks 180 \
  --seeds 101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251,257 \
  --output-dir outputs/holdout_30

.venv/bin/python scripts/summarize_holdout.py \
  --input outputs/holdout_30/summary.json \
  --output examples/holdout_30_seed_summary.json
```

## 브랜치 비교 통합 결과

`origin/GubikoDev`는 실행 안정성, CLI, 훈련된 모델, 테스트가 강하고 `origin/hbin`은 AgentRuntime/DecisionTrace 기반 설명 가능성과 제출 검증 게이트가 강합니다. 최종 DEV 통합본은 `GubikoDev` 계열의 실행 베이스를 유지하고, `hbin`의 핵심 장점인 판단 trace 구조와 최종 검증 관점을 `src/tsra_agent/runtime.py`, simulator 산출물, 로컬 `scripts/verify_submission_state.py` 검증기로 이식했습니다.

상세 비교는 `docs/agent_branch_comparison.md`에 기록했습니다.

구현 구조와 개발 판단은 먼저 `docs/agent_engineering_notes.md`에서 확인할 수 있습니다.

## 제출 패키지 권장

예선 안내서의 부가자료 ZIP 권장 구성에 맞춰 다음 파일을 포함하면 됩니다.

- `README.md`
- `requirements.txt`
- `src/`
- `docs/`
- `models/`
- `scripts/`
- `examples/`
- `tests/`

패키징 스크립트:

```bash
.venv/bin/python scripts/build_submission_zip.py
```

주의: `dist/*.zip`는 생성 산출물이므로 Git에 추적하지 않습니다. 최종 제출 직전에 위 명령으로 새 ZIP을 만들고, `scripts/verify_submission_state.py --require-dev --require-clean` 검증을 통과한 상태의 ZIP만 제출하세요.
