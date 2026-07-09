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
outputs/package/release_handoff.md
```

## 포함하는 것

- `README.md`, `requirements.txt`, `requirements-gpu.txt`
- `scripts/`: 패키지 생성, release handoff 생성, release freeze 자동화, 최종 상태 검증, 외부 링크 검증 도구
- `src/`: AURA, TSRA-R, Agent Runtime, 시뮬레이터, ML, 실험 코드
- `docs/`: 시나리오, 에이전트 구조, 개발 판단 근거
- `outputs/experiments/experiment_summary.csv`
- `outputs/batch/*.csv`
- `outputs/figures/*.png`
- `outputs/report_tables/*`: trace, contract validation, trace quality audit, agent loop replay, agent decision causality audit, agent decision margin audit, agent memory belief audit, agent tool usage audit, agent interface manifest, agent capability matrix, agent collaboration graph, closed-loop episode replay, attack-defense coverage, response audit, PACE transition audit, operator alerts, defense effectiveness ledger, mission impact decomposition, metric gate, submission readiness audit, COA, battle timeline, incident summary, competition alignment matrix
- `outputs/models/*_metrics.json`

## 제외하는 것

- `.git/`, `.venv*`, `__pycache__/`, `*.pyc`
- `outputs/tmp*`
- `outputs/batch/seed_*`
- `outputs/datasets/`
- `outputs/models/*.pkl`
- `outputs/models/*.pt`
- `outputs/package/*.zip`은 Git에 커밋하지 않는다.
- `outputs/package/release_handoff.md`는 ZIP 안에 넣지 않는 repo-side handoff 문서로 둔다.

## 현재 검증 결과

패키지 생성 검증:

```text
payload_file_count: 164
zip_file_count: 165
zip_bytes: 재생성 시 outputs/package/submission_manifest.md 기준 확인
zip_sha256: 재생성 시 outputs/package/submission_manifest.md 기준 확인
manifest_integrity: zip_sha256, zip_bytes, zip_file_count, 포함 파일 목록, worktree payload parity 검증
zip_metadata: path-sorted entries, fixed timestamp, deflated compression
release_handoff: repo-only/current
external_link_verifier: included
metric_gate_summary: included
agent_interface_manifest: included
agent_capability_matrix: included
attack_defense_coverage: included
attack_defense_response_audit: included
pace_transition_audit: included
operator_alerts: included
defense_effectiveness_ledger: included
closed_loop_episode_replay: included
agent_collaboration_graph: included
mission_impact_decomposition: included
agent_contract_validation: included
decision_trace_quality_audit: included
agent_loop_replay: included
agent_decision_causality_audit: included
agent_decision_margin_audit: included
agent_memory_belief_audit: included
agent_tool_usage_audit: included
submission_readiness_audit: included
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
- 같은 payload에서 같은 SHA-256이 나오도록 ZIP entry 순서와 metadata를 고정한다.
- ZIP을 외부 클라우드에 올릴 때는 `outputs/package/submission_manifest.md`의 SHA-256 값을 함께 확인한다.
