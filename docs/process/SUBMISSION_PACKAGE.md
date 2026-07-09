# 제출 패키지 기준

## 목적

제출용 부가자료 ZIP은 전체 작업 디렉터리를 그대로 압축하지 않는다. 재생성 가능한 임시 로그, synthetic dataset, model binary를 제외하고, 심사자가 실행과 검증에 필요한 코드, 문서, 요약 산출물만 담는다.

생성 명령:

```bash
python3 scripts/build_submission_package.py
```

산출물:

```text
outputs/package/DAH2026_source_LIG_DAH_AGI.zip
outputs/package/submission_manifest.md
```

## 포함하는 것

- `README.md`, `requirements.txt`, `requirements-gpu.txt`
- `src/`: AURA, TSRA-R, Agent Runtime, 시뮬레이터, ML, 실험 코드
- `docs/`: 시나리오, 에이전트 구조, 개발 판단 근거
- `outputs/experiments/experiment_summary.csv`
- `outputs/batch/*.csv`
- `outputs/figures/*.png`
- `outputs/report_tables/*`: trace, contract validation, trace quality audit, agent loop replay, agent interface manifest, agent capability matrix, attack-defense coverage, metric gate, COA, battle timeline, incident summary, competition alignment matrix
- `outputs/models/*_metrics.json`

## 제외하는 것

- `.git/`, `.venv*`, `__pycache__/`, `*.pyc`
- `outputs/tmp*`
- `outputs/batch/seed_*`
- `outputs/datasets/`
- `outputs/models/*.pkl`
- `outputs/models/*.pt`
- `outputs/package/*.zip`은 Git에 커밋하지 않는다.

## 현재 검증 결과

패키지 생성 검증:

```text
payload_file_count: 124
zip_file_count: 125
zip_bytes: 재생성 시 outputs/package/submission_manifest.md 기준 확인
zip_sha256: 재생성 시 outputs/package/submission_manifest.md 기준 확인
metric_gate_summary: included
agent_interface_manifest: included
agent_capability_matrix: included
attack_defense_coverage: included
agent_contract_validation: included
decision_trace_quality_audit: included
agent_loop_replay: included
competition_alignment_matrix: included
```

ZIP 내부 제외 항목 검증:

```text
__pycache__: 0
*.pyc: 0
outputs/tmp*: 0
outputs/datasets/: 0
*.pkl: 0
*.pt: 0
outputs/batch/seed_*: 0
```

## 운영 기준

- 개발 산출물은 계속 `hbin` 브랜치에 커밋한다.
- `main` 브랜치는 보호용 기본 브랜치로 유지한다.
- ZIP 파일은 로컬 생성 산출물로 두고 Git에는 올리지 않는다.
- ZIP을 외부 클라우드에 올릴 때는 `outputs/package/submission_manifest.md`의 SHA-256 값을 함께 확인한다.
