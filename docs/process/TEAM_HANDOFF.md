# Team Handoff Guide

이 문서는 새 팀원이 들어왔을 때 공격 에이전트, 방어 에이전트, ML/실험, QA/패키징 작업을 어디서부터 이어가야 하는지 정리한다. 모든 작업은 폐쇄형 시뮬레이션 코드와 산출물만 다루며 실제 RF(actual RF), exploit, live network action은 추가하지 않는다.

## Branch Rule

- Active development branch: `hbin`
- Protected/default branch: `main`
- Development changes are committed and pushed to `hbin`.
- `main` is preserved as the protected/default branch and is not used for direct development pushes.
- Before handoff, run `git status --short --branch` and `git ls-remote --heads origin main hbin`.

## Role Lanes

| lane | owner label | primary files | required evidence |
|---|---|---|---|
| Attack agent | 공격 담당 | `src/aura/`, `src/experiments/aura_attack_decision_path_audit.py`, `src/experiments/ml_attack_decision_path_audit.py` | AURA attack path, ML attack path, COA cards, attack-defense response |
| Defense agent | 방어 담당 | `src/tsra_r/`, `src/experiments/defense_priority_decision_path_audit.py`, `src/experiments/adaptive_defense_decision_path_audit.py` | defense priority path, adaptive defense path, action attribution, stress scenarios |
| ML and metrics | ML/실험 담당 | `src/ml/`, `src/experiments/metric_gate.py`, `src/experiments/ml_contribution_audit.py`, `src/experiments/tsra_detector_calibration_audit.py` | model metrics, ML contribution, threshold sweep, detector calibration, metric gates |
| QA and packaging | QA/패키지 담당 | `tests/`, `.github/workflows/quality.yml`, `scripts/build_submission_package.py`, `scripts/verify_submission_state.py` | unit regression, agent quality gate, package manifest, release handoff, final verifier |
| Integration | 통합 담당 | `README.md`, `docs/process/`, `src/experiments/competition_alignment.py`, `src/experiments/submission_readiness_audit.py` | reproduction order, submission readiness, competition alignment, development log |

## Change Contract

Every substantial change must update the matching source, generated evidence, and process documentation.

- Attack changes update AURA traces, attack path audits, COA cards, response evidence, and `docs/agents/AURA_ATTACK_AGENT.md`.
- Defense changes update TSRA-R traces, defense priority/adaptive audits, action attribution, stress evidence, and `docs/agents/TSRA_R_DEFENSE_AGENT.md`.
- ML changes update model metrics, ML contribution/path/interaction audits, threshold or calibration evidence, and metric gates.
- Runtime changes update unit regression tests, runtime invariant, causality, memory, tool, quality gate, interface, and capability evidence.
- Packaging or workflow changes update the package manifest, release handoff, final verifier, GitHub workflow, and this handoff guide.

## Minimum Gate Before Push

Run the fast checks first:

```bash
python3 -m unittest discover -s tests
python3 -m src.experiments.agent_quality_gate_audit --fail-on-error
```

Run the affected evidence generators for the changed lane. Before handoff or release freeze, run:

```bash
python3 -m src.experiments.reproduction_order_audit --fail-on-error
python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete
python3 -m src.experiments.competition_alignment --fail-on-incomplete
python3 scripts/freeze_release_candidate.py
python3 scripts/verify_submission_state.py --require-clean
```

GitHub Actions also runs the hbin quality gate on every `hbin` push.

## Decision Record Rule

For each meaningful change:

- Add the rationale and validation result to `docs/process/DEVELOPMENT_LOG.md`.
- Add or update the matching item in `docs/process/NEXT_DEVELOPMENT_QUEUE.md`.
- Update agent docs when AURA, TSRA-R, AgentRuntime, ML policy, or evidence contracts change.
- Update README Full Reproduction when a new generator or audit becomes required.
- Regenerate package manifest and release handoff if packaged files change.

## Safety Boundary

The repository models simulated mission effects only. Do not add operational RF control, exploit steps, live packet manipulation, credential handling, or live network attack actions. Safety boundary changes must pass:

```bash
python3 -m src.experiments.safety_boundary_audit --fail-on-error
```

## Handoff Checklist

- `git status --short --branch` shows `hbin` and no tracked changes before final handoff.
- `origin/main` and `origin/hbin` are both present.
- `DAH Agent Quality Gate` is green on the latest `hbin` push.
- `outputs/package/submission_manifest.md` and `outputs/package/release_handoff.md` match the latest package ZIP.
- `docs/process/DEVELOPMENT_LOG.md` and `docs/process/NEXT_DEVELOPMENT_QUEUE.md` explain what changed and why.
