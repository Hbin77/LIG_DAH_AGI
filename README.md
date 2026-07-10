# TSRA-X / AURA-lite DAH 2026 Agent Package

DAH 2026 예선용 AI 공방 에이전트 부가자료입니다. 범위는 예선 보고서 6번 항목인 **AI 에이전트 설계 및 구현**을 입증하는 소스코드, 실행 방법, 산출 로그, 안전 경계 문서입니다.

이 패키지는 실제 SATCOM 침투, 장비별 절차, 운용 가능한 RF 파라미터, exploit code를 포함하지 않습니다. `AURA-lite`는 폐쇄형 synthetic mission-event simulator에서 공격 효과만 생성하고, `TSRA-R-lite`는 C4ISR 데이터 신뢰성 붕괴를 탐지·완화하는 방어 에이전트입니다.

## 구성

- `src/tsra_agent/agents.py`: `AURA-lite` red scenario generator, `TSRA-R-lite` risk-fusion defense agent, `TSRA-ML` trained-policy agent
- `src/tsra_agent/ml_policy.py`: synthetic training-data generator, scikit-learn model loader, standard-library logistic fallback
- `src/tsra_agent/simulator.py`: UAV/UGV/SATCOM/PACE mission event simulator
- `src/tsra_agent/evaluator.py`: latency, stale ratio, priority inversion, backlog, false alarm, resilience gain 평가
- `src/tsra_agent/cli.py`: 단일/다중 seed 실험 실행 및 산출물 생성
- `src/tsra_agent/runtime.py`: AURA/TSRA-R 판단 과정을 observation, memory, structured AgentTool result, candidate action, selected action, model-risk basis, feedback 형태로 기록하고 검증하는 경량 AgentRuntime
- `models/`: trained TSRA-ML scikit-learn ensemble, tuned/final policy config, logistic fallback model, training/tuning/selection reports
- `scripts/train_sklearn_policy.py`: primary TSRA-ML scikit-learn ensemble training script
- `scripts/train_ml_policy.py`: dependency-free logistic fallback training script
- `scripts/tune_ml_policy.py`: mission simulator 기반 TSRA-ML action gate 튜닝 스크립트
- `docs/`: 아키텍처, 평가 계획, 안전 경계
- `docs/report_writer_guide.md`: 보고서 담당자가 결과물, 수치, 안전 경계, 복붙 가능한 문장을 이해하기 위한 작성 가이드
- `examples/`: 5개 seed 검증 결과 샘플
- `tests/`: 표준 라이브러리 `unittest` 회귀 테스트

## 실행

ML 모델은 이미 `models/tsra_sklearn_policy.joblib`에 훈련된 상태로 포함되어 있습니다. 재훈련이 필요하면 먼저 아래를 실행합니다.

번들된 scikit-learn 모델은 `scikit-learn 1.9.x` 계열에서 로드하는 것을 기준으로 합니다. 실행 전 `pip install -r requirements.txt` 또는 같은 버전대가 설치된 Conda 환경을 사용하세요.

```bash
conda run -n base python scripts/train_sklearn_policy.py --samples 100000
```

scikit-learn 없는 환경을 위한 fallback 모델 재훈련:

```bash
conda run -n base python scripts/train_ml_policy.py --samples 10000 --epochs 260
```

TSRA-ML action gate 재튜닝:

```bash
conda run -n base python scripts/tune_ml_policy.py --candidates 8 --ticks 180
```

```bash
conda run -n base python -m src.tsra_agent.cli \
  --scenario hybrid \
  --ticks 180 \
  --seeds 7,11,19,23,31 \
  --output-dir outputs/final_run
```

생성 파일:

- `summary.json`: seed별/평균 지표
- `incident_report.md`: 보고서에 붙일 수 있는 실행 요약
- `run_manifest.json`: 산출물 구조와 안전 경계
- `seed_<seed>/*_events.jsonl`: 실험별 이벤트 로그
- `seed_<seed>/*_decision_traces.jsonl`: AURA/TSRA-R 판단 trace 로그

## 검증

```bash
conda run -n base python -m unittest discover -s tests -v
```

최종 제출 전 DEV 브랜치 품질 게이트:

```bash
conda run -n base python scripts/verify_submission_state.py --require-dev --require-clean
```

이 검증은 unit test뿐 아니라 CLI smoke run, 모든 DecisionTrace의 structured tool-call schema, TSRA-ML의 model/heuristic/fused risk basis, 모델/예시 수치, 안전 경계, 제출 ZIP 포함 파일까지 함께 확인합니다. GitHub Actions의 `DEV Submission Quality Gate`도 같은 검증기를 실행합니다.

현재 검증 기준 결과는 `examples/summary_multi_seed.json`에 고정했습니다.

핵심 평균값:

- attacked mission impact: `82.162`
- rule defense mission impact: `61.228`
- TSRA-R/TSRA-ML adaptive defense mission impact: `15.306`
- attacked priority inversion rate: `0.0629`
- TSRA-R priority inversion rate: `0.0`
- TSRA-ML priority inversion rate: `0.0`
- TSRA-ML compressed snapshot messages: `41.4`
- TSRA-ML deferred messages: `13.0`
- TSRA-ML backlog messages: `0.0`
- TSRA-ML expired messages: `0.0`
- TSRA-R detection time: `1` tick
- TSRA-R adaptive recovery time: `3` ticks after first alert stabilization
- TSRA-ML recovery time: `2` ticks after first alert stabilization
- guarded baseline false alarm rate: `0.0`
- TSRA-R adaptive baseline-adjusted resilience gain: `90.374%`
- TSRA-ML adaptive baseline-adjusted resilience gain: `90.374%`
- TSRA-ML scikit-learn validation F1: `0.9956`
- TSRA-ML scikit-learn ROC-AUC: `1.0`

## 브랜치 비교 통합 결과

`origin/GubikoDev`는 실행 안정성, CLI, 훈련된 모델, 테스트가 강하고 `origin/hbin`은 AgentRuntime/DecisionTrace 기반 설명 가능성과 제출 검증 게이트가 강합니다. 최종 DEV 통합본은 `GubikoDev` 계열의 실행 베이스를 유지하고, `hbin`의 핵심 장점인 판단 trace 구조와 최종 검증 관점을 `src/tsra_agent/runtime.py`, simulator 산출물, `scripts/verify_submission_state.py`, GitHub Actions 품질 게이트로 이식했습니다.

상세 비교는 `docs/agent_branch_comparison.md`에 기록했습니다.

보고서 작성자는 먼저 `docs/report_writer_guide.md`를 읽으면 됩니다. 보고서에 넣을 수 있는 주장, 핵심 수치, 표 예시, 안전 경계, 재현 명령을 한 문서에 정리했습니다.

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
conda run -n base python scripts/build_submission_zip.py
```

주의: `dist/*.zip`는 생성 산출물이므로 Git에 추적하지 않습니다. 최종 제출 직전에 위 명령으로 새 ZIP을 만들고, `scripts/verify_submission_state.py --require-dev --require-clean` 검증을 통과한 상태의 ZIP만 제출하세요.
