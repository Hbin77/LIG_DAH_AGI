# Agent Branch Comparison

## Compared Branches

| Branch | Role | Main Strength |
|---|---|---|
| `origin/GubikoDev` | Current executable submission base | Stable `src.tsra_agent` API, trained TSRA-ML model artifacts, CLI, and `unittest` regression coverage. |
| `origin/hbin` | Other contributor branch | Stronger agent framing through separated AURA/TSRA-R packages, AgentRuntime, DecisionTrace logs, and report-generation assets. |
| `origin/DEV` | Final integrated submission branch | Keeps the stable GubikoDev execution path and adds hbin-style decision traces plus a DEV submission verifier and CI quality gate. |

## Decision

The best single result is not a wholesale replacement with `hbin`.

`GubikoDev` is the better execution base because it runs immediately, carries the trained scikit-learn TSRA-ML policy, has a compact CLI, and already passes regression tests. `hbin` is stronger as an agent-evidence design because it makes the observe-memory-tool-candidate-decision loop explicit.

The integration therefore keeps `GubikoDev` as the runnable package and ports the highest-value `hbin` ideas: structured decision traces, explicit safety boundaries, and a final verifier that checks code, traces, model evidence, package contents, and branch hygiene together.

## Integration Scope

Implemented in this branch:

- `src/tsra_agent/runtime.py`: callable-tool `AgentRuntime`, bounded `AgentMemory`, lifecycle enforcement, and environment feedback.
- `src/tsra_agent/attack_agent.py`: AURA-owned runtime, tools, memory, candidate selection, and traces.
- `src/tsra_agent/defense_agent.py`: rule/TSRA-R/TSRA-ML runtime ownership and model-versus-guardrail action attribution.
- `src/tsra_agent/simulator.py`: typed mission-state/action exchange and post-action feedback for every agent cycle.
- `src/tsra_agent/cli.py`: run manifest now lists decision-trace artifacts.
- `tests/test_simulation.py`: runtime invocation, attack/defense separation, feedback, ML attribution, and CLI regression.
- `scripts/verify_submission_state.py`: DEV-specific final gate for tests, CLI smoke output, DecisionTrace schema, model metrics, safety boundary, package contents, and branch/worktree hygiene.
- `.github/workflows/dev-quality.yml`: CI gate for pushes and pull requests targeting `DEV`.

Kept from `GubikoDev`:

- `src.tsra_agent` import path and CLI behavior.
- trained `models/tsra_sklearn_policy.joblib` and existing model reports.
- `scripts/build_submission_zip.py` source package workflow.
- existing metric and ML competitiveness tests.

Left as reference from `hbin` rather than copied wholesale:

- large `outputs/` report-table tree.
- regenerated `.pkl` model binaries and dataset-heavy workflow.
- separate `src/aura`, `src/tsra_r`, `src/experiments` package split.

Why not copy `hbin` wholesale:

- `hbin` is stronger for broad evidence generation, but its large report-table tree and split packages would make the DEV branch heavier and harder for a report writer to run quickly.
- `DEV` already has trained TSRA-ML artifacts, a compact CLI, and a reproducible multi-seed scenario.
- The final compromise is to keep DEV compact and executable while adding the hbin-style proof points that matter for judging an AI agent: observation, memory, tool calls, candidate actions, selected action, feedback, safety boundary, and an automated quality gate.

## Latest Recomparison (2026-07-10)

The latest comparison used `origin/DEV@5d2609c` and `origin/hbin@e8cbbad`. These branches have no common Git ancestor, so direct merge, cherry-pick, and raw metric comparison are not valid integration methods.

The latest `hbin` commits improve evidence handling rather than attack, defense, simulator, or ML-policy performance. They add rule-delegate trace exposure, fixed-output audit tables, and regression tests for the relationship between candidate actions and final actions. The equivalent high-value ideas adopted for DEV are:

- `scripts/summarize_decision_traces.py`: converts freshly generated CLI JSONL traces into a report-ready CSV and Markdown table with trace source, ID, candidate count, tool calls, selected action, and reason.
- `tests/test_simulation.py`: checks that TSRA-R-lite and TSRA-ML selected candidate actions exactly match the emitted action list, including an explicit no-op case.
- `scripts/verify_submission_state.py`: regenerates the trace summary during its CLI smoke run and checks row coverage plus the TSRA candidate-to-action contract.

The following `hbin` material remains intentionally excluded: its separate `src/aura`/`src/tsra_r` implementation, generated `outputs/` snapshot tree, branch-specific workflow, and fixed trace-count assertions. Those artifacts would replace the executable DEV path or bind verification to historical outputs rather than freshly generated simulation evidence.

## Repro Commands

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m src.tsra_agent.cli \
  --scenario hybrid \
  --ticks 180 \
  --seeds 7,11,19,23,31 \
  --output-dir outputs/integration_check
.venv/bin/python scripts/build_submission_zip.py
.venv/bin/python scripts/verify_submission_state.py --require-dev --require-clean
```

Safety boundary: all attack effects remain closed synthetic mission simulation events only. No exploit code, operational RF parameter, live network action, or equipment-specific intrusion step is included.
