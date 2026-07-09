# Metric Gate Summary

This table checks whether the generated experiment metrics still support the intended AURA/TSRA-R development direction.

| gate_id | area | metric | observed | threshold | status | interpretation |
|---|---|---|---:|---|---|---|
| G01 | AURA attack effectiveness | E3 mission_impact_mean - E1 mission_impact_mean | 0.456259 | >= 0.35 | pass | AURA should create substantially higher simulated mission impact than baseline. |
| G02 | AURA adaptive selection | E3 mission_impact_mean - E2 mission_impact_mean | 0.219717 | >= 0.10 | pass | AURA should outperform the fixed attack baseline in mission impact. |
| G03 | TSRA-R resilience | E5 resilience_gain_mean | 0.846145 | >= 0.80 | pass | TSRA-R should recover at least 80% of AURA-induced impact in repeated runs. |
| G04 | TSRA-R impact containment | E5 mission_impact_mean / E3 mission_impact_mean | 0.153384 | <= 0.20 | pass | Defended mission impact should stay below one fifth of undefended AURA impact. |
| G05 | Trusted stale protection | E5 trusted_stale_exposure_mean | 0.125 | <= 0.15 | pass | TSRA-R stale_badge should keep trusted stale exposure bounded. |
| G06 | Priority reroute ablation | no_priority_reroute delta_priority_inversion_rate_mean | 0.424361 | >= 0.25 | pass | Removing priority_reroute should materially increase priority inversion. |
| G07 | Stale badge ablation | no_stale_badge delta_trusted_stale_exposure_mean | 0.375 | >= 0.25 | pass | Removing stale_badge should materially increase trusted stale exposure. |
| G08 | Adaptive memory improvement | adaptive mission impact improvement over full TSRA-R | 0.0307717 | >= 0.005 | pass | AdaptiveTSRA-R should improve mission impact versus full TSRA-R baseline. |
| G09 | Adaptive memory action economy | full video_throttle_count_mean - adaptive video_throttle_count_mean | 3.26667 | >= 1.0 | pass | AdaptiveTSRA-R should reduce optional video throttle actions while preserving core defenses. |
| G10 | ML defender separation | abs(E7 mission_impact_mean - E6 mission_impact_mean) | 0.0107652 | >= 0.005 | pass | E7 should remain behaviorally distinct from E6 so ML TSRA-R is not a no-op copy. |
| G11 | Repeated-run stability | max(E5/E7 mission_impact_std) | 0.0256799 | <= 0.03 | pass | Defended repeated-run mission impact should remain stable across seeds. |
| G12 | PACE reselection discipline | full TSRA-R recovery_instability_mean | 2.06667 | <= 2.20 | pass | Full TSRA-R should avoid repeated fallback reselection unless residual mission pressure justifies the extra recovery instability. |
