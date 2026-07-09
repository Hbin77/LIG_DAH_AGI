# Safety Boundary Audit

This audit checks that the project remains a closed simulation prototype.
Safety boundary: closed simulation safety-boundary audit only; no RF, exploit, or live network action

| check_id | area | status | observed | allowed_exceptions |
|---|---|---|---|---|
| S01 | Operational core source | pass | files_scanned=26; network_hits=0; shell_hits=0 | none in operational core |
| S02 | Automation exceptions | pass | network_hits=scripts/verify_external_package_link.py; shell_hits=scripts/freeze_release_candidate.py,scripts/generate_release_handoff.py,scripts/verify_submission_state.py,src/experiments/agent_quality_gate_audit.py,src/experiments/submission_readiness_audit.py; unexpected_network_hits=0; unexpected_shell_hits=0 | urllib only in scripts/verify_external_package_link.py; subprocess only in release/Git verification scripts |
| S03 | Attack-effect schema | pass | uses_AttackCandidate=True; uses_AttackEvent=True; simulated_effect_fields=True | packet_loss_add is a simulator metric field, not packet generation |
| S04 | Safety-boundary text | pass | closed_simulation=True; no_rf=True; no_exploit=True; no_live_network=True | safety terms may appear in negative boundary statements |
| S05 | Submission package safety | pass | zip_path=outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip; zip_exists=True; manifest_has_exclusion_policy=True; excluded_artifact_hits=0 | model metric JSON is included; .pkl/.pt binaries are excluded |

## Detail

### S01 Operational core source

- Requirement: Core agent/simulator/model code must not import or call live network, RF, exploit, or shell primitives.
- Evidence: src/agents | src/aura | src/tsra_r | src/simulator | src/shared | src/ml
- Observed: files_scanned=26; network_hits=0; shell_hits=0
- Status: pass
- Allowed exceptions: none in operational core
- Next gate: Any future core primitive hit must be removed or moved into an explicitly documented verifier-only path.
- Safety boundary: closed simulation safety-boundary audit only; no RF, exploit, or live network action

### S02 Automation exceptions

- Requirement: External access primitives may appear only in package-link or Git/local verification automation.
- Evidence: scripts | src/experiments
- Observed: network_hits=scripts/verify_external_package_link.py; shell_hits=scripts/freeze_release_candidate.py,scripts/generate_release_handoff.py,scripts/verify_submission_state.py,src/experiments/agent_quality_gate_audit.py,src/experiments/submission_readiness_audit.py; unexpected_network_hits=0; unexpected_shell_hits=0
- Status: pass
- Allowed exceptions: urllib only in scripts/verify_external_package_link.py; subprocess only in release/Git verification scripts
- Next gate: New automation that touches network or subprocess must be listed in this allowlist and justified.
- Safety boundary: closed simulation safety-boundary audit only; no RF, exploit, or live network action

### S03 Attack-effect schema

- Requirement: AURA must emit simulated AttackCandidate/AttackEvent effects, not operational commands.
- Evidence: src/aura/candidate_generator.py | src/shared/schemas.py
- Observed: uses_AttackCandidate=True; uses_AttackEvent=True; simulated_effect_fields=True
- Status: pass
- Allowed exceptions: packet_loss_add is a simulator metric field, not packet generation
- Next gate: Attack changes must stay as simulator effect fields and regenerate COA/safety evidence.
- Safety boundary: closed simulation safety-boundary audit only; no RF, exploit, or live network action

### S04 Safety-boundary text

- Requirement: Core handoff artifacts must explicitly state closed simulation, no RF, no exploit, and no live network action.
- Evidence: README.md | docs/agents/AURA_ATTACK_AGENT.md | docs/agents/TSRA_R_DEFENSE_AGENT.md | docs/agents/AGENT_RUNTIME.md | outputs/report_tables/aura_coa_cards.csv | outputs/report_tables/incident_summary.csv | outputs/report_tables/agent_collaboration_graph.csv
- Observed: closed_simulation=True; no_rf=True; no_exploit=True; no_live_network=True
- Status: pass
- Allowed exceptions: safety terms may appear in negative boundary statements
- Next gate: New user-facing artifacts must carry the same closed-simulation boundary.
- Safety boundary: closed simulation safety-boundary audit only; no RF, exploit, or live network action

### S05 Submission package safety

- Requirement: Submission ZIP must exclude caches, generated model binaries, and other non-source execution artifacts.
- Evidence: outputs/package/submission_manifest.md | outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip
- Observed: zip_path=outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip; zip_exists=True; manifest_has_exclusion_policy=True; excluded_artifact_hits=0
- Status: pass
- Allowed exceptions: model metric JSON is included; .pkl/.pt binaries are excluded
- Next gate: Any package rule change must keep binary/cache exclusions passing.
- Safety boundary: closed simulation safety-boundary audit only; no RF, exploit, or live network action
