# Defense Action Attribution Audit

This audit aggregates the defense effectiveness ledger by TSRA-R action and links local metric movement to ablation or reactive-window evidence.
Safety boundary: closed simulation defense-action attribution audit only; no RF, exploit, or live network action

## Summary

- Audit rows: 5
- Status counts: pass=5
- Attribution classes: ablation_supported=2, bounded_tradeoff_supported=1, local_metric_supported=1, reactive_window_supported=1

## Audit Table

| action | event_count | improved_or_held_rate | primary_metric | primary_metric_delta_mean | ablation_delta_value | attribution_class | attribution_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| priority_reroute | 11 | 0.818182 | priority_inversion_rate | -0.0347756 | 0.410888 | ablation_supported | pass |
| video_throttle | 14 | 0.785714 | p95_critical_latency_sec | -0.567857 | -0.371667 | local_metric_supported | pass |
| stale_badge | 16 | 0.875 | trusted_stale_exposure | -0.00390625 | 0.38125 | ablation_supported | pass |
| pace_switch | 6 | 0.666667 | mission_impact | -0.0232876 | -0.0506426 | bounded_tradeoff_supported | pass |
| ml_attack_alert | 9 | 0.888889 | mission_impact | -0.0157261 |  | reactive_window_supported | pass |

## Interpretation

### priority_reroute

- Target: reduce priority inversion and critical-traffic queuing
- Mean deltas: impact=-0.0212136, latency=-0.545455, trusted_stale=-0.0113636, priority=-0.0347756
- Attribution class: ablation_supported
- Status: pass
- Interpretation: Priority reroute has local priority-inversion relief and ablation support: removing it raises priority inversion by 0.411.

### video_throttle

- Target: reduce optional video pressure on critical traffic
- Mean deltas: impact=-0.010561, latency=-0.567857, trusted_stale=0.00446429, priority=-0.0303661
- Attribution class: local_metric_supported
- Status: pass
- Interpretation: Video throttle is credited through local latency/priority relief rather than scalar mission-impact ablation; this records it as a bounded capacity-control tradeoff.

### stale_badge

- Target: bound trusted stale COP exposure
- Mean deltas: impact=-0.0128044, latency=-0.45625, trusted_stale=-0.00390625, priority=-0.0235618
- Attribution class: ablation_supported
- Status: pass
- Interpretation: Stale badge is the clearest trust-protection action: ablation raises trusted stale exposure by 0.381, while local windows mostly improve or hold.

### pace_switch

- Target: move critical traffic away from degraded active links
- Mean deltas: impact=-0.0232876, latency=-1.06667, trusted_stale=0.0104167, priority=-0.0438112
- Attribution class: bounded_tradeoff_supported
- Status: pass
- Interpretation: PACE switching shows local mission-impact or latency relief, but scalar ablation can undervalue recovery stability and fallback-chasing context.

### ml_attack_alert

- Target: open reactive defense windows during active AURA-ML attack effects
- Mean deltas: impact=-0.0157261, latency=-1.02222, trusted_stale=0.00694444, priority=-0.0365725
- Attribution class: reactive_window_supported
- Status: pass
- Interpretation: ML alerts are attributed as reactive-window triggers: every alert overlaps an active AURA-ML attack window and most local windows improve or hold mission impact.
