# AURA COA Cards

Each card describes a simulated attack-effect Course of Action selected by AURA.

Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-001: E3_rule_aura / atk-00001

- Agent: AURA
- Time: 60 sec
- Mission phase: normal_patrol
- Active link at decision: SATCOM
- Attack type: `queue_pressure`
- Target link: `SATCOM`
- Target traffic classes: video, telemetry
- Duration: 80 sec
- Simulated effects: latency +200ms; jitter +100ms; bandwidth cap 1.5Mbps; queue pressure enabled
- Expected mission impact: 0.566191
- Expected p95 critical latency: 7.94287 sec
- Expected stale data ratio: 0.676667
- Expected priority inversion rate: 0.650389
- Detectability score: 0.15
- Attack score: 0.543691
- Candidate rank: 1
- Runner-up: bandwidth_limit on SATCOM (score=0.434227, impact=0.456727)
- Selection reason: increase non-critical queue occupancy
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-002: E3_rule_aura / atk-00002

- Agent: AURA
- Time: 110 sec
- Mission phase: air_defense_watch
- Active link at decision: SATCOM
- Attack type: `bandwidth_limit`
- Target link: `SATCOM`
- Target traffic classes: all
- Duration: 80 sec
- Simulated effects: jitter +80ms; loss +0.02; bandwidth cap 1Mbps
- Expected mission impact: 1
- Expected p95 critical latency: 139.088 sec
- Expected stale data ratio: 0.91
- Expected priority inversion rate: 0.828951
- Detectability score: 0.35
- Attack score: 0.9475
- Candidate rank: 1
- Runner-up: queue_pressure on SATCOM (score=0.9475 tied, impact=1)
- Selection reason: reduce available capacity during queue growth
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-003: E3_rule_aura / atk-00003

- Agent: AURA
- Time: 160 sec
- Mission phase: resupply_move
- Active link at decision: SATCOM
- Attack type: `bandwidth_limit`
- Target link: `SATCOM`
- Target traffic classes: all
- Duration: 80 sec
- Simulated effects: jitter +80ms; loss +0.02; bandwidth cap 1Mbps
- Expected mission impact: 1
- Expected p95 critical latency: 227.816 sec
- Expected stale data ratio: 0.66
- Expected priority inversion rate: 0.969875
- Detectability score: 0.35
- Attack score: 0.9475
- Candidate rank: 1
- Runner-up: queue_pressure on SATCOM (score=0.9475 tied, impact=1)
- Selection reason: reduce available capacity during queue growth
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-004: E3_rule_aura / atk-00004

- Agent: AURA
- Time: 210 sec
- Mission phase: normal_patrol
- Active link at decision: SATCOM
- Attack type: `bandwidth_limit`
- Target link: `SATCOM`
- Target traffic classes: all
- Duration: 80 sec
- Simulated effects: jitter +80ms; loss +0.02; bandwidth cap 1Mbps
- Expected mission impact: 1
- Expected p95 critical latency: 276.17 sec
- Expected stale data ratio: 0.66
- Expected priority inversion rate: 1
- Detectability score: 0.35
- Attack score: 0.9475
- Candidate rank: 1
- Runner-up: queue_pressure on SATCOM (score=0.9475 tied, impact=1)
- Selection reason: reduce available capacity during queue growth
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-005: E3_rule_aura / atk-00005

- Agent: AURA
- Time: 260 sec
- Mission phase: normal_patrol
- Active link at decision: SATCOM
- Attack type: `stale_cop_induction`
- Target link: `SATCOM`
- Target traffic classes: telemetry, coordinate
- Duration: 70 sec
- Simulated effects: latency +800ms; jitter +160ms; loss +0.04; bandwidth cap 1Mbps
- Expected mission impact: 1
- Expected p95 critical latency: 391.747 sec
- Expected stale data ratio: 0.656667
- Expected priority inversion rate: 1
- Detectability score: 0.55
- Attack score: 0.9175
- Candidate rank: 1
- Runner-up: queue_pressure on SATCOM (score=0.9035, impact=0.956)
- Selection reason: COP freshness is already degraded
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-006: E5_rule_aura_tsra_r / atk-00001

- Agent: AURA
- Time: 60 sec
- Mission phase: normal_patrol
- Active link at decision: SATCOM
- Attack type: `queue_pressure`
- Target link: `SATCOM`
- Target traffic classes: video, telemetry
- Duration: 80 sec
- Simulated effects: latency +200ms; jitter +100ms; bandwidth cap 1.5Mbps; queue pressure enabled
- Expected mission impact: 0.566191
- Expected p95 critical latency: 7.94287 sec
- Expected stale data ratio: 0.676667
- Expected priority inversion rate: 0.650389
- Detectability score: 0.15
- Attack score: 0.543691
- Candidate rank: 1
- Runner-up: bandwidth_limit on SATCOM (score=0.434227, impact=0.456727)
- Selection reason: increase non-critical queue occupancy
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-007: E5_rule_aura_tsra_r / atk-00002

- Agent: AURA
- Time: 110 sec
- Mission phase: air_defense_watch
- Active link at decision: LTE
- Attack type: `queue_pressure`
- Target link: `LTE`
- Target traffic classes: video, telemetry
- Duration: 80 sec
- Simulated effects: latency +200ms; jitter +100ms; bandwidth cap 1.5Mbps; queue pressure enabled
- Expected mission impact: 0.939263
- Expected p95 critical latency: 57.9916 sec
- Expected stale data ratio: 0.426667
- Expected priority inversion rate: 0.535229
- Detectability score: 0.15
- Attack score: 0.916763
- Candidate rank: 1
- Runner-up: stale_cop_induction on LTE (score=0.915089, impact=0.967589)
- Selection reason: increase non-critical queue occupancy
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-008: E5_rule_aura_tsra_r / atk-00003

- Agent: AURA
- Time: 160 sec
- Mission phase: resupply_move
- Active link at decision: LTE
- Attack type: `queue_pressure`
- Target link: `LTE`
- Target traffic classes: video, telemetry
- Duration: 80 sec
- Simulated effects: latency +200ms; jitter +100ms; bandwidth cap 1.5Mbps; queue pressure enabled
- Expected mission impact: 1
- Expected p95 critical latency: 68.2658 sec
- Expected stale data ratio: 0.676667
- Expected priority inversion rate: 0.497307
- Detectability score: 0.15
- Attack score: 0.9775
- Candidate rank: 1
- Runner-up: bandwidth_limit on LTE (score=0.896141, impact=0.948641)
- Selection reason: increase non-critical queue occupancy
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-009: E5_rule_aura_tsra_r / atk-00004

- Agent: AURA
- Time: 210 sec
- Mission phase: normal_patrol
- Active link at decision: LTE
- Attack type: `queue_pressure`
- Target link: `LTE`
- Target traffic classes: video, telemetry
- Duration: 80 sec
- Simulated effects: latency +200ms; jitter +100ms; bandwidth cap 1.5Mbps; queue pressure enabled
- Expected mission impact: 1
- Expected p95 critical latency: 126.09 sec
- Expected stale data ratio: 0.676667
- Expected priority inversion rate: 0.487311
- Detectability score: 0.35
- Attack score: 0.9475
- Candidate rank: 1
- Runner-up: bandwidth_limit on LTE (score=0.891155, impact=0.943655)
- Selection reason: increase non-critical queue occupancy
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-010: E5_rule_aura_tsra_r / atk-00005

- Agent: AURA
- Time: 260 sec
- Mission phase: normal_patrol
- Active link at decision: LTE
- Attack type: `queue_pressure`
- Target link: `LTE`
- Target traffic classes: video, telemetry
- Duration: 80 sec
- Simulated effects: latency +200ms; jitter +100ms; bandwidth cap 1.5Mbps; queue pressure enabled
- Expected mission impact: 0.956
- Expected p95 critical latency: 203.573 sec
- Expected stale data ratio: 0.426667
- Expected priority inversion rate: 0.481991
- Detectability score: 0.35
- Attack score: 0.9035
- Candidate rank: 1
- Runner-up: stale_cop_induction on LTE (score=0.858494, impact=0.940994)
- Selection reason: increase non-critical queue occupancy
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-011: E7_ml_aura_ml_tsra_r / ml-atk-00001

- Agent: AURA-ML
- Time: 60 sec
- Mission phase: normal_patrol
- Active link at decision: SATCOM
- Attack type: `queue_pressure`
- Target link: `SATCOM`
- Target traffic classes: video, telemetry
- Duration: 80 sec
- Simulated effects: latency +200ms; jitter +100ms; bandwidth cap 1.5Mbps; queue pressure enabled
- Expected mission impact: 0.602005
- Expected p95 critical latency: 7.94287 sec
- Expected stale data ratio: 0.676667
- Expected priority inversion rate: 0.650389
- Detectability score: 0.15
- Attack score: 0.579505
- Candidate rank: 1
- Runner-up: bandwidth_limit on SATCOM (score=0.506702, impact=0.529202)
- Selection reason: ML impact predictor selected queue_pressure
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-012: E7_ml_aura_ml_tsra_r / ml-atk-00002

- Agent: AURA-ML
- Time: 110 sec
- Mission phase: air_defense_watch
- Active link at decision: LTE
- Attack type: `failover_chasing`
- Target link: `LTE`
- Target traffic classes: all
- Duration: 70 sec
- Simulated effects: latency +600ms; jitter +120ms; loss +0.03; bandwidth cap 0.45Mbps
- Expected mission impact: 0.836848
- Expected p95 critical latency: 151.618 sec
- Expected stale data ratio: 0.46
- Expected priority inversion rate: 0.371232
- Detectability score: 0.5
- Attack score: 0.761848
- Candidate rank: 1
- Runner-up: queue_pressure on LTE (score=0.740504, impact=0.763004)
- Selection reason: ML impact predictor selected failover_chasing
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-013: E7_ml_aura_ml_tsra_r / ml-atk-00003

- Agent: AURA-ML
- Time: 160 sec
- Mission phase: resupply_move
- Active link at decision: MESH
- Attack type: `failover_chasing`
- Target link: `MESH`
- Target traffic classes: all
- Duration: 70 sec
- Simulated effects: latency +600ms; jitter +120ms; loss +0.03; bandwidth cap 0.45Mbps
- Expected mission impact: 0.822403
- Expected p95 critical latency: 61.4505 sec
- Expected stale data ratio: 0.71
- Expected priority inversion rate: 0.31759
- Detectability score: 0.3
- Attack score: 0.777403
- Candidate rank: 1
- Runner-up: queue_pressure on MESH (score=0.692203, impact=0.714703)
- Selection reason: ML impact predictor selected failover_chasing
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-014: E7_ml_aura_ml_tsra_r / ml-atk-00004

- Agent: AURA-ML
- Time: 210 sec
- Mission phase: normal_patrol
- Active link at decision: MESH
- Attack type: `queue_pressure`
- Target link: `MESH`
- Target traffic classes: video, telemetry
- Duration: 80 sec
- Simulated effects: latency +200ms; jitter +100ms; bandwidth cap 1.5Mbps; queue pressure enabled
- Expected mission impact: 0.801872
- Expected p95 critical latency: 41.2243 sec
- Expected stale data ratio: 0.676667
- Expected priority inversion rate: 0.500637
- Detectability score: 0.15
- Attack score: 0.779372
- Candidate rank: 1
- Runner-up: failover_chasing on MESH (score=0.614297, impact=0.659297)
- Selection reason: ML impact predictor selected queue_pressure
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.

## COA-015: E7_ml_aura_ml_tsra_r / ml-atk-00005

- Agent: AURA-ML
- Time: 260 sec
- Mission phase: normal_patrol
- Active link at decision: MESH
- Attack type: `failover_chasing`
- Target link: `MESH`
- Target traffic classes: all
- Duration: 70 sec
- Simulated effects: latency +600ms; jitter +120ms; loss +0.03; bandwidth cap 0.45Mbps
- Expected mission impact: 0.77479
- Expected p95 critical latency: 205.933 sec
- Expected stale data ratio: 0.46
- Expected priority inversion rate: 0.293886
- Detectability score: 0.5
- Attack score: 0.69979
- Candidate rank: 1
- Runner-up: queue_pressure on MESH (score=0.640587, impact=0.693087)
- Selection reason: ML impact predictor selected failover_chasing
- Safety boundary: Simulated effect only: no RF transmission, no exploit, no real packet generation, no operational SATCOM parameters.
