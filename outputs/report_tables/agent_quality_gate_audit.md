# Agent Quality Gate Audit

This audit verifies that fast agent-core regression tests and the hbin quality workflow are wired into reproduction, packaging, and final verification.
Safety boundary: closed simulation agent quality-gate audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 6
- Status counts: pass=6

| check_id | area | observed | status |
|---|---|---|---|
| AQG01 | unit_regression_execution | test_count=4; result=pass; output=.... \| ---------------------------------------------------------------------- \| Ran 4 tests in 0.002s \|  \| OK | pass |
| AQG02 | unit_regression_scope | missing_scope_tokens=none | pass |
| AQG03 | final_verifier_integration | missing_verifier_tokens=none | pass |
| AQG04 | hbin_workflow_gate | missing_workflow_tokens=none; main_branch_trigger=false | pass |
| AQG05 | readme_reproduction_gate | unittest_command_present=true; quality_audit_command_present=true; quality_before_run_all=true | pass |
| AQG06 | package_inclusion_gate | missing_builder_tokens=none; missing_manifest_tokens=none | pass |

## Detail

### AQG01 unit_regression_execution

- Requirement: Agent core regression tests must execute locally and pass.
- Observed: test_count=4; result=pass; output=.... | ---------------------------------------------------------------------- | Ran 4 tests in 0.002s |  | OK
- Evidence: tests/test_agent_regression.py
- Status: pass
- Interpretation: Fast regression tests run before full experiments, so core agent invariants fail early.
- Safety boundary: closed simulation agent quality-gate audit only; no RF, exploit, or live network action

### AQG02 unit_regression_scope

- Requirement: Tests must cover AgentRuntime, AURA-ML identity/scoring, and TSRA-R priority/cooldown invariants.
- Observed: missing_scope_tokens=none
- Evidence: tests/test_agent_regression.py
- Status: pass
- Interpretation: The test file names the three agent-core regression areas instead of only checking file existence.
- Safety boundary: closed simulation agent quality-gate audit only; no RF, exploit, or live network action

### AQG03 final_verifier_integration

- Requirement: Final verifier must execute agent regression tests and require test/workflow files.
- Observed: missing_verifier_tokens=none
- Evidence: scripts/verify_submission_state.py
- Status: pass
- Interpretation: Regression tests are part of the final gate, not an optional developer command.
- Safety boundary: closed simulation agent quality-gate audit only; no RF, exploit, or live network action

### AQG04 hbin_workflow_gate

- Requirement: GitHub Actions quality gate must run on hbin and avoid main-branch push automation.
- Observed: missing_workflow_tokens=none; main_branch_trigger=false
- Evidence: .github/workflows/quality.yml
- Status: pass
- Interpretation: CI protects the shared hbin branch while preserving main as a separate protected branch.
- Safety boundary: closed simulation agent quality-gate audit only; no RF, exploit, or live network action

### AQG05 readme_reproduction_gate

- Requirement: README Full Reproduction must run unit regression and this audit before heavy experiments.
- Observed: unittest_command_present=true; quality_audit_command_present=true; quality_before_run_all=true
- Evidence: README.md
- Status: pass
- Interpretation: The fast code gate appears early in reproduction order, before long-running experiments.
- Safety boundary: closed simulation agent quality-gate audit only; no RF, exploit, or live network action

### AQG06 package_inclusion_gate

- Requirement: Submission package must include regression tests and hbin quality workflow.
- Observed: missing_builder_tokens=none; missing_manifest_tokens=none
- Evidence: scripts/build_submission_package.py | outputs/package/submission_manifest.md
- Status: pass
- Interpretation: The regression gate is shipped with the source package and is not only a local workspace artifact.
- Safety boundary: closed simulation agent quality-gate audit only; no RF, exploit, or live network action
