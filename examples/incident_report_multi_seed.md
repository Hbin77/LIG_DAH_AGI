# TSRA-R / AURA-lite Incident Summary

## Scenario

- Mode: `hybrid`
- Ticks: `180`
- Seeds: `7, 11, 19, 23, 31`

## Key Findings

- AURA-lite increased mean mission impact score to `82.162` under the attack condition.
- Rule defense reduced mean mission impact score to `61.228` with `28.266%` baseline-adjusted gain.
- TSRA-R-lite reduced mean mission impact score to `15.306`.
- Mean baseline-adjusted resilience gain was `90.374%`.
- TSRA-ML reduced mean mission impact score to `15.306`.
- TSRA-ML mean baseline-adjusted resilience gain was `90.374%`.
- Defended mean P95 critical latency: `5.14` ticks.
- Defended mean stale data ratio: `0.0107`.
- Defended mean priority inversion rate: `0.0`.
- TSRA-ML mean P95 critical latency: `5.14` ticks.
- TSRA-ML mean stale data ratio: `0.0107`.
- TSRA-ML mean priority inversion rate: `0.0`.
- TSRA-ML mean compressed snapshot messages: `41.4`.
- TSRA-ML mean deferred messages: `13`.
- TSRA-ML mean backlog messages: `0`.
- TSRA-ML mean expired messages: `0`.
- TSRA-R mean detection time: `1` ticks after first attack.
- TSRA-R mean recovery time: `3` ticks after first TSRA-R alert stabilization.
- Guarded no-attack false alarm rate: `0.0`.
- TSRA-ML guarded no-attack false alarm rate: `0.0`.

## Agent Actions

- AURA-lite selected bounded, abstract COAs across link degradation, mission-aware delay, and failover chasing inside a synthetic mission-event simulator.
- TSRA-R-lite applied risk fusion, critical traffic priority boosting, PACE routing, COP stale badge, terminal/source quarantine flags, and minimum mode.
- TSRA-ML used a trained scikit-learn ensemble plus tuned guardrail policy for earlier priority boosting, adaptive UAV snapshot compression, EDF scheduling, SATCOM return hysteresis, and stale noncritical backlog control.

## Safety Boundary

The run models mission effects only. It does not include exploit code, equipment-specific procedures, or operational RF parameters.
