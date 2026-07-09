# Safety Boundary

This package is intentionally a safe DAH 2026 preliminary prototype.

## Included

- Synthetic mission events for UAV video, UGV status, sensor alert, command, and position messages.
- Abstract link degradation and mission-traffic effects.
- PACE routing logic over SATCOM, radio, LTE, and mesh abstractions.
- Adaptive UAV snapshot compression and traffic shaping inside the synthetic simulator.
- C4ISR data freshness and urgency scoring.
- Event logs and metrics for report evidence.
- Synthetic ML training data, a trained scikit-learn mission-risk classifier, and tuned defensive action gates.

## Excluded

- Exploit code.
- Operational RF parameters.
- Specific SATCOM device intrusion steps.
- Real network scanning or exploitation.
- Live weapon, UAV, UGV, or radio control.
- Guidance for unauthorized access.
- Training on real operational telemetry or classified data.

## Report wording

Use:

> AURA-lite generates bounded mission effects inside a synthetic simulator.

Avoid:

> AURA attacks SATCOM systems.

Use:

> TSRA-R protects mission-effective bandwidth through priority routing, traffic shaping, and PACE selection.

Avoid:

> TSRA-R increases physical bandwidth.
