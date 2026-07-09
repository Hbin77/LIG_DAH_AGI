# ML Threshold Sweep

This table sweeps the TSRA-R-ML anomaly threshold across closed simulation runs.
The sweep does not change the deployed E7 baseline by itself; it records the tuning tradeoff around the baseline threshold.
Safety boundary: closed simulation ML threshold sweep only; no RF, exploit, or live network action

| threshold | runs | mission impact mean | ML alerts mean | first alert latency mean | no-op mean | status | interpretation |
|---:|---:|---:|---:|---:|---:|---|---|
| 0.55 | 10 | 0.15208 | 9.1 | 19 | 38.7 | usable | lower threshold opens reactive windows more readily; status=usable; impact_mean=0.152; alert_mean=9.10; first_alert_latency_mean=19.0s; no_op_mean=38.7 |
| 0.65 | 10 | 0.15208 | 9.1 | 19 | 38.7 | usable | lower threshold opens reactive windows more readily; status=usable; impact_mean=0.152; alert_mean=9.10; first_alert_latency_mean=19.0s; no_op_mean=38.7 |
| 0.75 | 10 | 0.15208 | 9.1 | 19 | 38.7 | usable | baseline threshold balances alert timing and no-op evidence; status=usable; impact_mean=0.152; alert_mean=9.10; first_alert_latency_mean=19.0s; no_op_mean=38.7 |
| 0.85 | 10 | 0.15208 | 8.8 | 20.5 | 39.1 | usable | higher threshold requires stronger anomaly probability before action; status=usable; impact_mean=0.152; alert_mean=8.80; first_alert_latency_mean=20.5s; no_op_mean=39.1 |
| 0.95 | 10 | 0.15208 | 5.8 | 20.5 | 41.2 | watch | higher threshold requires stronger anomaly probability before action; status=watch; impact_mean=0.152; alert_mean=5.80; first_alert_latency_mean=20.5s; no_op_mean=41.2 |
