# AURA / TSRA Agent Engineering Notes

## Purpose

This document records the engineering definition, implementation choices, and
verification basis of the attack and defense agents. It is a team handoff and
design record, not a claim that every future capability is already implemented.

The system is limited to a closed synthetic C4ISR/SATCOM mission simulator. It
contains no exploit code, no operational RF parameters, no equipment-specific
intrusion procedure, and no live network action.

## What Makes These Components Agents

Python alone does not make a component an AI agent. The implemented definition is
an executable loop with persistent state and an auditable action boundary:

```text
observe mission state
-> read bounded working memory
-> invoke registered tools
-> compare candidate actions
-> commit one action or no-op
-> receive environment feedback
-> carry the result into the next cycle
```

The runtime rejects a decision if no registered tool was actually invoked. Tool
input and output summaries are generated from the handler invocation itself, so a
simulator cannot fabricate a tool call after a policy has already executed.

The concrete contract is implemented in `src/tsra_agent/runtime.py`:

- `AgentRuntime`: owns the cycle phase, tool registry, memory, traces, and feedback.
- `AgentMemory`: retains the latest 24 observations and decisions plus compact beliefs.
- `AgentTool`: wraps a callable handler and records success or failure from the real call.
- `DecisionTrace`: records observation, prior memory, candidates, calls, decision, and feedback.

Every completed trace must end in `runtime.phase=feedback_attached`. A trace that
only records a decision but never observes the resulting environment state is
considered incomplete by the DEV verifier.

## Attack Agent: AURA-lite

Implementation: `src/tsra_agent/attack_agent.py`

Policy primitive: `AURALite` in `src/tsra_agent/agents.py`

Goal: select one bounded synthetic mission effect, including a valid no-op, from
the current link, queue, freshness, and PACE state.

Registered tools:

1. `rank_attack_candidates`
   - Produces no-op, link degradation, mission-aware delay, and failover-chasing candidates.
   - Scores only candidates allowed by the configured scenario and attack window.
   - Reads the previous attack mode from `AgentMemory` and applies a small, bounded repeat penalty.
2. `select_attack_effect`
   - Materializes the highest-scored candidate as an `AttackAction`.
   - Returns the selected score and candidate count as part of the real tool result.

The selected effect is applied only to simulator state. The following tick feedback
contains queue depth, delivered/lost/stale counts, active path, SATCOM health, and
critical latency observed after processing.

AURA-lite is currently a deterministic candidate-ranking agent. It is not described
as a trained attack model. This distinction is intentional and must remain explicit
until a trained attack-impact policy is integrated into this DEV execution path.

## Defense Agent: TSRA-R

Implementation: `src/tsra_agent/defense_agent.py`

Policy primitives: `TSRARLite` and `MLTSRARLite` in `src/tsra_agent/agents.py`

Goal: preserve critical traffic delivery and C4ISR data trust under synthetic
hybrid SATCOM disruption.

The defense agent has three execution modes behind the same runtime contract:

- `rule`: threshold-only comparison policy.
- `tsra`: adaptive heuristic risk-fusion policy.
- `ml`: trained scikit-learn risk model fused with mission safety guardrails.

TSRA-R tools:

1. `fuse_mission_risk`
2. `select_defense_action`

TSRA-ML adds two real model-path tools before risk fusion:

1. `extract_mission_features`
2. `predict_mission_risk`

The final action can combine priority boost, minimum mode, stale badge, PACE
transition, and quarantine recommendation. Each action records its trigger reasons.

## Training Data Quality

The first synthetic generator separated nominal and attacked ranges too cleanly.
That produced holdout F1 0.9956 but only 0.8102 F1 when the same oracle was checked
on an unmitigated simulator trajectory. The high score was therefore not accepted as
sufficient model evidence.

The current `overlap-balanced-v2` generator makes four changes:

- nominal, broad, stale-boundary, and latency-boundary feature regimes overlap;
- label classes are exactly balanced before the train/validation split;
- `defense_alerted` is removed because it is the agent's prior output, not an
  independent environment observation;
- the target is a proactive intervention oracle at weighted risk 0.18, before the
  severe-risk boundary that deterministic safety guardrails already prevent.

The primary 12-feature `HistGradientBoostingClassifier` result is:

| Validation surface | F1 | False-positive rate |
|---|---:|---:|
| Random synthetic holdout | 0.9884 | 0.0004 |
| Independent attacked trajectory | 0.9972 | 0.0155 |
| Independent TSRA-defended trajectory | 0.9771 | 0.0076 |
| Independent no-attack trajectory | 0.0000 (no positive labels) | 0.0000 |

These are synthetic-oracle agreement metrics. They are not operational incident
accuracy. `models/tsra_sklearn_training_report.json` records class balance, feature
ranges, missing/duplicate checks, independent trajectory seeds, runtime versions,
limitations, and the SHA-256 of the bundled model.

## Model Attribution

A high validation F1 does not prove that a model affects a closed-loop agent. The
runtime therefore separates two sources of action:

- `model_influenced_actions`: the fused threshold crosses only because the trained
  model contributes risk probability, or a model-only threshold directly fires.
- `guardrail_triggered_actions`: a deterministic mission safety condition is enough
  to require the action even without the model.

This is a counterfactual attribution check. For fused thresholds, the implementation
compares the selected fused risk with the heuristic-only weighted component. It does
not label every action produced by the ML class as an ML contribution.

Current five-seed closed-loop result:

| Measure | TSRA-R | TSRA-ML |
|---|---:|---:|
| Mission impact | 15.306 | 12.926 |
| Defense intervention ticks | 134.4 | 116.0 |
| Priority-boost ticks | 118.0 | 97.2 |
| Model-influenced ticks | 0.0 | 83.8 |
| Baseline-adjusted resilience gain | 90.374% | 93.600% |

With the same tuned action gate and learned risk fixed to zero, mission impact rises
to 15.180. The 2.254-point difference from TSRA-ML 12.926 is the bounded causal
contribution supported by this simulator ablation. No model-influenced action occurs
in the no-attack guarded baseline. Mission guardrails remain active because critical
traffic protection cannot depend only on classifier confidence.

The five-seed values include policy development seeds. A disjoint 30-seed holdout
therefore provides the stronger robustness check:

| Holdout measure | TSRA-R | TSRA-ML | Zero-model ablation |
|---|---:|---:|---:|
| Mission impact | 16.2180 | 15.3187 | 16.9810 |
| Resilience gain | 89.8057% | 91.0330% | 88.7730% |

TSRA-ML beats TSRA-R and the zero-model ablation on 22 of 30 paired seeds. The
bootstrap 95% mean-difference intervals are `[0.1500, 1.6387]` and
`[0.7063, 2.7050]`, respectively. Eight losing seeds are retained in the artifact;
the engineering claim is positive average effect under simulator uncertainty, not
universal dominance.

## Why Python Is Appropriate Here

Python is an implementation choice, not the agent definition. It is suitable for
this prototype because the simulator, scikit-learn model, deterministic policy
logic, JSONL audit records, and test suite share one reproducible process. Adding an
LLM framework would not improve the bounded real-time decision contract and would
introduce network, nondeterminism, latency, and secret-management dependencies.

For a live system, the same event and trace contracts could be hosted in a service,
message bus, or embedded runtime. This prototype does not claim live integration.

## Verification Contract

`scripts/verify_submission_state.py` rejects the package when any of these conditions
fails:

- attack and defense modules or runtime artifacts are missing;
- a decision was not produced through registered callable tools;
- tool input/output, status, or synthetic safety check is missing;
- environment feedback was not attached to every smoke-run trace;
- AURA selection differs from the highest ranked candidate;
- TSRA-ML prediction, risk fusion, action selection, or attribution is missing;
- TSRA-ML has no model-influenced actions in the closed-loop smoke run;
- TSRA-ML intervention count is not lower than TSRA-R in the fixed evaluation;
- unit, CLI, package, branch, or safety checks fail.

## Branch Discipline

Active integration work is committed to `DEV`. The `hbin` contributor branch is
preserved as a separate history, and `main` remains present and untouched. Team
members can review each engineering decision as an isolated DEV commit before any
future merge policy is chosen.

## Development Decisions

### 2026-07-10: Runtime execution ownership

Replaced simulator-owned, post-hoc tool records with agent-owned `AgentRuntime`
cycles. Attack and defense agents now execute registered handlers and own their
memory and traces.

### 2026-07-10: Attack and defense module separation

Created `attack_agent.py` and `defense_agent.py`. The simulator now exchanges
`AttackAction`, `DefenseAction`, and `MissionState` contracts with those agents
instead of directly orchestrating their policy internals.

### 2026-07-10: ML contribution evidence

Added model-versus-guardrail attribution and action-economy metrics. This resolves
the ambiguity created when TSRA-R and TSRA-ML had identical mission-impact columns
despite taking different control paths.

### 2026-07-10: Reproducible package contents

Excluded local `.DS_Store` and `__MACOSX` metadata from generated ZIP files and the
package verifier. Local workspaces and fresh GitHub clones now produce the same
source-file entry set.
