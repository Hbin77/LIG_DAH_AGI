# 최종 재현 QA

## 목적

최종 제출 직전 상태가 실제로 재현 가능한지 확인한다. 검증 범위는 코드 컴파일, README Full Reproduction 실행, 핵심 산출물 row count, 제출 ZIP 구성, ZIP 제외 규칙, Git 브랜치 상태다.

## 실행 명령

```bash
python3 -m src.ml.build_dataset --rows 3000
python3 -m src.ml.train_aura_impact_model
python3 -m src.ml.train_tsra_detector --rows 5000
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
python3 -m src.experiments.battle_timeline
python3 -m src.experiments.aura_coa_cards
python3 -m src.experiments.run_tsra_ablation
python3 -m src.experiments.run_adaptive_memory
python3 -m src.experiments.run_batch
python3 scripts/build_submission_package.py
python3 scripts/verify_submission_state.py
```

## 검증 결과

Full Reproduction은 끝까지 통과했다.

핵심 산출물:

```text
experiment_summary rows: 7
repeated_experiment_summary rows: 7
resilience_gain_summary rows: 4
tsra_action_ablation_summary rows: 5
adaptive_memory_summary conditions: full_tsra_r, adaptive_tsra_r
agent_decision_trace_summary rows: 215
aura_coa_cards rows: 15
battle_timeline rows: 46
```

패키지 검증:

```text
package_zip entries: 98
package exclusions: passed
excluded __pycache__: 0
excluded *.pyc: 0
excluded outputs/tmp*: 0
excluded outputs/datasets/: 0
excluded *.pkl/*.pt: 0
excluded outputs/batch/seed_*: 0
```

Git 검증:

```text
branch: hbin
origin/main: present
origin/hbin: present
```

## 판단

현재 `hbin` 브랜치 산출물은 README 기준으로 재현 가능하고, 제출 ZIP은 코드, 문서, 요약 CSV, figure, report table, model metric JSON 중심으로 구성된다. 실제 RF, exploit, live network action은 포함하지 않는다.
