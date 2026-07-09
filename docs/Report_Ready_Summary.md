# 보고서 삽입용 최종 요약

## 핵심 메시지

본 구현은 SATCOM을 실제로 공격하지 않는다. 폐쇄형 C4ISR/SATCOM 시뮬레이터에서 AURA가 통신 지연, 대역폭 제한, 큐 혼잡, critical window degradation 같은 공격 효과를 선택하고, TSRA-R이 priority reroute, video throttle, stale badge, PACE switch로 대응하는 공방 구조를 검증한다.

## 결과 한 줄

30개 seed 반복 실험에서 AURA는 Mission Impact를 평균 `0.914`까지 증가시켰고, TSRA-R 적용 후 평균 `0.124`로 감소했다. 이는 AURA 공격 대비 약 `86.4%`의 Resilience Gain이다.

## 보고서에 넣을 표

1. `outputs/batch/repeated_experiment_summary.csv`
2. `outputs/batch/resilience_gain_summary.csv`
3. `outputs/report_tables/E5_rule_aura_tsra_r_event_timeline.md`
4. `outputs/report_tables/ml_model_comparison.md`

## 보고서에 넣을 그림

1. `outputs/figures/aura_tsra_architecture.png`
2. `outputs/figures/batch_mission_impact_errorbar.png`
3. `outputs/figures/batch_resilience_gain.png`
4. `outputs/figures/E3_rule_aura_timeline.png`
5. `outputs/figures/E5_rule_aura_tsra_r_timeline.png`
6. `outputs/figures/E7_ml_aura_ml_tsra_r_timeline.png`
7. `outputs/figures/trusted_stale_exposure.png`
8. `outputs/figures/aura_mps_mlp_training_loss.png`

## 본문 문장 초안

> AURA는 작전 단계, 링크 상태, 메시지 큐, COP freshness를 관측해 공격 후보를 생성하고, MissionImpactScore가 가장 높은 공격 효과를 선택한다. TSRA-R은 같은 시뮬레이터 상태를 관측해 critical traffic 우선 전송, 영상 트래픽 제한, stale badge, PACE 전환을 수행한다. 두 에이전트는 attack_events.jsonl, defense_events.jsonl, metric_snapshots.jsonl을 통해 동일한 시간축에서 검증된다.

> TSRA-R은 stale data 자체를 즉시 제거하지는 못하지만, stale badge와 confidence annotation을 통해 지휘소가 오래된 정보를 최신 정보로 오인하는 비율을 낮춘다. 이를 표현하기 위해 본 실험은 raw stale_data_ratio와 trusted_stale_exposure를 분리했다.

> 30개 seed 반복 실험에서 AURA 공격은 Mission Impact를 평균 0.914까지 증가시켰다. TSRA-R 적용 후 Mission Impact는 평균 0.124로 감소했으며, 이는 AURA 공격 대비 약 86.4%의 Resilience Gain이다.

> ML은 두 지점에 적용했다. AURA Impact Predictor는 공격 후보의 MissionImpactScore를 예측하고, TSRA-R Anomaly Detector는 링크·큐·freshness 변화량을 기반으로 공격성 저하를 탐지한다. 추가로 Apple M3 Pro의 MPS backend를 활용해 2천만 개 synthetic attack candidate를 학습하는 GPU-scale MLP 실험을 수행했다.

## 주의 문장

> 본 구현은 실제 SATCOM 침해, RF 재밍, 장비 취약점 악용을 수행하지 않는다. 모든 공격은 폐쇄형 시뮬레이터 내부의 지연, 손실, 대역폭 제한, 큐 혼잡 효과로만 표현된다. ML 성능은 합성 데이터 기준이며 실제 운용망 적용 전에는 실측 telemetry 기반 재학습과 검증이 필요하다.

