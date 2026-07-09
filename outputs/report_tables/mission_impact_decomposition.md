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
| E5_rule_aura_tsra_r | critical_latency | 1.84333 | 0.0307222 | 0.35 | 0.0107528 | 0.076663 |
| E5_rule_aura_tsra_r | trusted_stale_exposure | 0.125 | 0.25 | 0.25 | 0.0625 | 0.4456 |
| E5_rule_aura_tsra_r | priority_inversion | 0.049554 | 0.123885 | 0.2 | 0.024777 | 0.17665 |
| E5_rule_aura_tsra_r | kill_chain_delay | 9.34333 | 0.0519074 | 0.15 | 0.00778611 | 0.0555118 |
| E5_rule_aura_tsra_r | recovery_instability | 2.06667 | 0.688889 | 0.05 | 0.0344444 | 0.245575 |
| E6_ml_aura_tsra_r | critical_latency | 1.94 | 0.0323333 | 0.35 | 0.0113167 | 0.077342 |
| E6_ml_aura_tsra_r | trusted_stale_exposure | 0.125 | 0.25 | 0.25 | 0.0625 | 0.427146 |
| E6_ml_aura_tsra_r | priority_inversion | 0.0370509 | 0.0926273 | 0.2 | 0.0185255 | 0.126609 |
| E6_ml_aura_tsra_r | kill_chain_delay | 9.44 | 0.0524444 | 0.15 | 0.00786667 | 0.0537635 |
| E6_ml_aura_tsra_r | recovery_instability | 2.76667 | 0.922222 | 0.05 | 0.0461111 | 0.315139 |
| E7_ml_aura_ml_tsra_r | critical_latency | 2.39 | 0.0398333 | 0.35 | 0.0139417 | 0.0871832 |
| E7_ml_aura_ml_tsra_r | trusted_stale_exposure | 0.127083 | 0.254167 | 0.25 | 0.0635417 | 0.397353 |
| E7_ml_aura_ml_tsra_r | priority_inversion | 0.0503886 | 0.125971 | 0.2 | 0.0251943 | 0.157551 |
| E7_ml_aura_ml_tsra_r | kill_chain_delay | 10.015 | 0.0556389 | 0.15 | 0.00834583 | 0.0521901 |
| E7_ml_aura_ml_tsra_r | recovery_instability | 2.93333 | 0.977778 | 0.05 | 0.0488889 | 0.305723 |

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

- Reported mission impact mean: 0.14026
- Reconstructed from mean components: 0.14026
- Reconstruction delta: 0
- Largest component: trusted_stale_exposure (0.0625)

### E6_ml_aura_tsra_r

- Reported mission impact mean: 0.14632
- Reconstructed from mean components: 0.14632
- Reconstruction delta: 0
- Largest component: trusted_stale_exposure (0.0625)

### E7_ml_aura_ml_tsra_r

- Reported mission impact mean: 0.159912
- Reconstructed from mean components: 0.159912
- Reconstruction delta: 0
- Largest component: trusted_stale_exposure (0.0635417)
