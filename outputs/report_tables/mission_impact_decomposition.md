# Mission Impact Decomposition

This table decomposes repeated-run Mission Impact into the five weighted components used by `compute_full_mission_impact`.
The stale component uses `trusted_stale_exposure`, not raw `stale_data_ratio`, because TSRA-R may mark stale COP objects as untrusted rather than removing them.
The reconstruction uses mean component values, so it may differ slightly from the reported mean of per-run mission impact.

Safety boundary: closed simulation metric decomposition only; no RF, exploit, or live network action

| experiment | component | raw_metric_mean | normalized_score | weight | weighted_contribution | share |
|---|---|---:|---:|---:|---:|---:|
| E1_baseline | critical_latency | 2.82 | 0.047 | 0.35 | 0.01645 | 0.0359029 |
| E1_baseline | trusted_stale_exposure | 0.5 | 1 | 0.25 | 0.25 | 0.545637 |
| E1_baseline | priority_inversion | 0.32876 | 0.8219 | 0.2 | 0.16438 | 0.358767 |
| E1_baseline | kill_chain_delay | 32.82 | 0.182333 | 0.15 | 0.02735 | 0.0596927 |
| E1_baseline | recovery_instability | 0 | 0 | 0.05 | 0 | 0 |
| E2_fixed_attack | critical_latency | 32.8333 | 0.547222 | 0.35 | 0.191528 | 0.27569 |
| E2_fixed_attack | trusted_stale_exposure | 0.516667 | 1 | 0.25 | 0.25 | 0.359856 |
| E2_fixed_attack | priority_inversion | 0.566798 | 1 | 0.2 | 0.2 | 0.287885 |
| E2_fixed_attack | kill_chain_delay | 63.8333 | 0.35463 | 0.15 | 0.0531944 | 0.0765694 |
| E2_fixed_attack | recovery_instability | 0 | 0 | 0.05 | 0 | 0 |
| E3_rule_aura | critical_latency | 160.692 | 1 | 0.35 | 0.35 | 0.368421 |
| E3_rule_aura | trusted_stale_exposure | 0.525 | 1 | 0.25 | 0.25 | 0.263158 |
| E3_rule_aura | priority_inversion | 0.825202 | 1 | 0.2 | 0.2 | 0.210526 |
| E3_rule_aura | kill_chain_delay | 192.192 | 1 | 0.15 | 0.15 | 0.157895 |
| E3_rule_aura | recovery_instability | 0 | 0 | 0.05 | 0 | 0 |
| E4_rule_aura_basic_defense | critical_latency | 2.13333 | 0.0355556 | 0.35 | 0.0124444 | 0.116543 |
| E4_rule_aura_basic_defense | trusted_stale_exposure | 0.125 | 0.25 | 0.25 | 0.0625 | 0.585315 |
| E4_rule_aura_basic_defense | priority_inversion | 0.0476158 | 0.11904 | 0.2 | 0.0238079 | 0.222962 |
| E4_rule_aura_basic_defense | kill_chain_delay | 9.63333 | 0.0535185 | 0.15 | 0.00802778 | 0.0751804 |
| E4_rule_aura_basic_defense | recovery_instability | 0 | 0 | 0.05 | 0 | 0 |
| E5_rule_aura_tsra_r | critical_latency | 1.83333 | 0.0305556 | 0.35 | 0.0106944 | 0.0679345 |
| E5_rule_aura_tsra_r | trusted_stale_exposure | 0.127083 | 0.254167 | 0.25 | 0.0635417 | 0.403637 |
| E5_rule_aura_tsra_r | priority_inversion | 0.0506094 | 0.126524 | 0.2 | 0.0253047 | 0.160744 |
| E5_rule_aura_tsra_r | kill_chain_delay | 9.45833 | 0.0525463 | 0.15 | 0.00788194 | 0.0500686 |
| E5_rule_aura_tsra_r | recovery_instability | 3.03333 | 1 | 0.05 | 0.05 | 0.317616 |
| E6_ml_aura_tsra_r | critical_latency | 1.84667 | 0.0307778 | 0.35 | 0.0107722 | 0.0721803 |
| E6_ml_aura_tsra_r | trusted_stale_exposure | 0.125 | 0.25 | 0.25 | 0.0625 | 0.418787 |
| E6_ml_aura_tsra_r | priority_inversion | 0.0363588 | 0.0908969 | 0.2 | 0.0181794 | 0.121813 |
| E6_ml_aura_tsra_r | kill_chain_delay | 9.34667 | 0.0519259 | 0.15 | 0.00778889 | 0.0521902 |
| E6_ml_aura_tsra_r | recovery_instability | 3 | 1 | 0.05 | 0.05 | 0.33503 |
| E7_ml_aura_ml_tsra_r | critical_latency | 2.69 | 0.0448333 | 0.35 | 0.0156917 | 0.0945187 |
| E7_ml_aura_ml_tsra_r | trusted_stale_exposure | 0.127083 | 0.254167 | 0.25 | 0.0635417 | 0.382743 |
| E7_ml_aura_ml_tsra_r | priority_inversion | 0.0563749 | 0.140937 | 0.2 | 0.0281874 | 0.169787 |
| E7_ml_aura_ml_tsra_r | kill_chain_delay | 10.315 | 0.0573056 | 0.15 | 0.00859583 | 0.0517769 |
| E7_ml_aura_ml_tsra_r | recovery_instability | 3 | 1 | 0.05 | 0.05 | 0.301175 |

## Experiment Summary

### E1_baseline

- Reported mission impact mean: 0.45818
- Reconstructed from mean components: 0.45818
- Reconstruction delta: 0
- Largest component: trusted_stale_exposure (0.25)

### E2_fixed_attack

- Reported mission impact mean: 0.694722
- Reconstructed from mean components: 0.694722
- Reconstruction delta: -1.11022e-16
- Largest component: trusted_stale_exposure (0.25)

### E3_rule_aura

- Reported mission impact mean: 0.914439
- Reconstructed from mean components: 0.95
- Reconstruction delta: -0.0355611
- Largest component: critical_latency (0.35)

### E4_rule_aura_basic_defense

- Reported mission impact mean: 0.10678
- Reconstructed from mean components: 0.10678
- Reconstruction delta: 0
- Largest component: trusted_stale_exposure (0.0625)

### E5_rule_aura_tsra_r

- Reported mission impact mean: 0.157423
- Reconstructed from mean components: 0.157423
- Reconstruction delta: 2.77556e-17
- Largest component: trusted_stale_exposure (0.0635417)

### E6_ml_aura_tsra_r

- Reported mission impact mean: 0.14924
- Reconstructed from mean components: 0.14924
- Reconstruction delta: 0
- Largest component: trusted_stale_exposure (0.0625)

### E7_ml_aura_ml_tsra_r

- Reported mission impact mean: 0.166017
- Reconstructed from mean components: 0.166017
- Reconstruction delta: 0
- Largest component: trusted_stale_exposure (0.0635417)
