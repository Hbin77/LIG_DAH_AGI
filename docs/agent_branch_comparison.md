# Agent Branch Comparison

## Compared Branches

| Branch | Role | Main Strength |
|---|---|---|
| `origin/GubikoDev` | Current executable submission base | Stable `src.tsra_agent` API, trained TSRA-ML model artifacts, CLI, and `unittest` regression coverage. |
| `origin/hbin` | Other contributor branch | Stronger agent framing through separated AURA/TSRA-R packages, AgentRuntime, DecisionTrace logs, and report-generation assets. |
| `codex/agent-comparison-integration-20260709` | Integrated result | Keeps the stable GubikoDev execution path and adds hbin-style decision traces for attack and defense agents. |

## Decision

The best single result is not a wholesale replacement with `hbin`.

`GubikoDev` is the better execution base because it runs immediately, carries the trained scikit-learn TSRA-ML policy, has a compact CLI, and already passes regression tests. `hbin` is stronger as an agent-evidence design because it makes the observe-memory-tool-candidate-decision loop explicit.

The integration therefore keeps `GubikoDev` as the runnable package and ports the highest-value `hbin` idea: structured decision traces.

## Integration Scope

Implemented in this branch:

- `src/tsra_agent/runtime.py`: lightweight AgentMemory and AgentTraceRecorder.
- `src/tsra_agent/simulator.py`: AURA and TSRA-R decision traces for every simulation run.
- `src/tsra_agent/cli.py`: run manifest now lists decision-trace artifacts.
- `tests/test_simulation.py`: CLI regression now verifies TSRA decision trace structure.

Kept from `GubikoDev`:

- `src.tsra_agent` import path and CLI behavior.
- trained `models/tsra_sklearn_policy.joblib` and existing model reports.
- `scripts/build_submission_zip.py` source package workflow.
- existing metric and ML competitiveness tests.

Left as reference from `hbin` rather than copied wholesale:

- large `outputs/` report-table tree.
- regenerated `.pkl` model binaries and dataset-heavy workflow.
- separate `src/aura`, `src/tsra_r`, `src/experiments` package split.

## Repro Commands

```bash
conda run -n base python -m unittest discover -s tests -v
conda run -n base python -m src.tsra_agent.cli \
  --scenario hybrid \
  --ticks 180 \
  --seeds 7,11,19,23,31 \
  --output-dir outputs/integration_check
conda run -n base python scripts/build_submission_zip.py
```

Safety boundary: all attack effects remain closed synthetic mission simulation events only. No exploit code, operational RF parameter, live network action, or equipment-specific intrusion step is included.
