# ML Threshold Sweep

This table sweeps the TSRA-R-ML anomaly threshold across closed simulation runs.
The sweep does not change the deployed E7 baseline by itself; it records the tuning tradeoff around the baseline threshold.
Safety boundary: closed simulation ML threshold sweep only; no RF, exploit, or live network action

| threshold | runs | mission impact mean | ML alerts mean | first alert latency mean | no-op mean | status | interpretation |
|---:|---:|---:|---:|---:|---:|---|---|
| 0.55 | 10 | 0.15671 | 9.2 | 19 | 39.7 | usable | lower threshold opens reactive windows more readily; status=usable; impact_mean=0.157; alert_mean=9.20; first_alert_latency_mean=19.0s; no_op_mean=39.7 |
| 0.65 | 10 | 0.15671 | 9.2 | 19 | 39.7 | usable | lower threshold opens reactive windows more readily; status=usable; impact_mean=0.157; alert_mean=9.20; first_alert_latency_mean=19.0s; no_op_mean=39.7 |
| 0.75 | 10 | 0.15671 | 9.2 | 19 | 39.7 | usable | baseline threshold balances alert timing and no-op evidence; status=usable; impact_mean=0.157; alert_mean=9.20; first_alert_latency_mean=19.0s; no_op_mean=39.7 |
| 0.85 | 10 | 0.15671 | 9.1 | 19 | 39.5 | usable | higher threshold requires stronger anomaly probability before action; status=usable; impact_mean=0.157; alert_mean=9.10; first_alert_latency_mean=19.0s; no_op_mean=39.5 |
| 0.95 | 10 | 0.17848 | 5.7 | 24.5 | 42 | watch | higher threshold requires stronger anomaly probability before action; status=watch; impact_mean=0.178; alert_mean=5.70; first_alert_latency_mean=24.5s; no_op_mean=42.0 |
