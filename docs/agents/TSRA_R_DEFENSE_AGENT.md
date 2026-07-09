# TSRA-R 방어 에이전트

정식 명칭:

```text
TSRA-R: Tactical SATCOM Resilience Agent - Responder
```

## 1. 역할

TSRA-R은 AURA가 만든 통신 저하 효과를 관측하고, mission impact를 줄이는 Blue Team 방어 에이전트다.

쉽게 말하면:

> TSRA-R은 현재 통신 상태를 관측하고, 등록된 방어 도구로 조건을 평가한 뒤, 필요한 방어 액션과 선택 이유를 trace로 남기는 방어 에이전트다.

## 2. 방어 목표

TSRA-R의 목표는 SATCOM을 절대 끊기지 않게 만드는 것이 아니다.

현실적 목표:

- critical traffic 지연 최소화
- 영상 트래픽이 경보/명령을 밀어내는 상황 완화
- stale data를 최신 정보로 오인하지 않게 표시
- SATCOM 저하 시 PACE fallback link 사용
- Mission Impact 감소

## 3. 입력

TSRA-R은 AURA와 같은 `MissionState`를 본다.

주요 관측값:

- active link 상태
- SATCOM latency/loss/queue
- critical pending count
- video queue size
- stale data ratio
- priority inversion rate
- recent critical latency

코드:

- `src/tsra_r/rule_defender.py`
- `src/tsra_r/ml_defender.py`

## 4. 출력

TSRA-R은 `DefenseEvent`를 출력한다.

방어 이벤트 예:

```json
{
  "event_id": "def-00001",
  "agent": "TSRA-R",
  "time_sec": 65,
  "action": "priority_reroute",
  "details": {
    "until_sec": 135,
    "reason": "critical traffic waiting behind video load"
  }
}
```

## 5. 방어 액션

| 방어 액션 | 의미 |
|---|---|
| `priority_reroute` | critical traffic을 영상보다 먼저 처리 |
| `video_throttle` | 영상 트래픽 크기 축소 |
| `stale_badge` | 오래된 COP 객체를 신뢰 낮은 정보로 표시 |
| `pace_switch` | SATCOM 또는 현재 fallback link 저하 시 다른 PACE link 선택 |

## 6. 핵심 지표

TSRA-R 평가에는 `stale_data_ratio`만 쓰면 부족하다.

이유:

- TSRA-R은 오래된 정보를 즉시 제거하지 못한다.
- 대신 오래됐다고 표시해서 지휘소가 최신 정보로 오인하지 않게 한다.

그래서 별도 지표를 둔다.

```text
trusted_stale_exposure
= 지휘소가 stale 정보를 최신으로 신뢰할 위험
```

방어 전:

```text
stale_data_ratio = 0.50
trusted_stale_exposure = 0.50
```

stale badge 방어 후:

```text
stale_data_ratio = 0.50
trusted_stale_exposure = 0.12
```

## 7. ML TSRA-R

ML TSRA-R은 현재 상태가 단순 혼잡인지 공격성 저하인지 분류한다.

입력:

- 링크 변화
- 큐 변화
- stale ratio
- priority inversion
- critical pending count

출력:

```text
attack_present probability
```

성능:

```text
Synthetic holdout best F1 baseline: LogisticRegression, F1 0.980
Deployed closed-loop model: RandomForestClassifier
RandomForest Precision: 0.996
RandomForest Recall: 0.934
RandomForest F1: 0.964
```

RandomForest를 배포 모델로 둔 이유:

- LogisticRegression은 synthetic holdout 점수는 높았지만 실제 폐루프의 큰 queue-pressure 상태에서 detector probability가 낮게 나오는 calibration 문제가 있었다.
- RandomForest는 nonlinear feature interaction을 반영해 실제 시뮬레이터 상태에서 방어 window를 안정적으로 연다.

### 7.1 TSRA-R-ML Mission Risk Guard

TSRA-R-ML은 detector probability만 보는 구조로 두지 않는다.

문제:

- detector가 첫 공격 구간에서는 방어 window를 잘 열 수 있다.
- 하지만 공격 효과가 끝나가는 시점에는 probability가 낮아질 수 있다.
- 이때 COP stale exposure 같은 잔여 임무 위험이 남아 있으면 window가 닫히면서 `stale_badge` 갱신을 놓칠 수 있다.

보강:

```text
Tool: assess_mission_risk_guard
조건:
- 이전에 ML detector가 방어 window를 연 적이 있어야 한다.
- window 종료가 가까워졌거나 이미 지나야 한다.
- residual_stale_cop, critical_queue_pressure, residual_link_degradation 중 하나가 있어야 한다.
- probability가 threshold 아래일 때만 guard extension으로 해석한다.

초기 공격 구간에서는 예외적으로 early mission-pressure guard를 허용한다. 이전 window가 없어도 probability가 0.50 이상, risk score가 0.85 이상이고 `critical_queue_pressure` 또는 `residual_link_degradation`이 있으면 짧은 방어 window를 연다. 이 경우에도 `ml_attack_alert`는 만들지 않고, DecisionTrace에 `early_guard_triggered=true`와 guard reason만 남긴다.
```

출력:

```text
mission_guard_triggered
mission_guard_reason
mission_guard_score
active_defense_until
```

이 guard는 새 방어 action을 만들지 않는다. 기존 `stale_badge`, `priority_reroute`, `video_throttle`, `pace_switch`를 실행할 수 있는 짧은 방어 window만 연장한다. 그래서 시뮬레이터 action contract는 유지되고, 근거는 `DecisionTrace`와 `agent_stress_scenario_audit`에 남는다.

stress 검증 결과:

```text
stale-COP chain TSRA-R-ML gain_mean: 0.675561 -> 0.754937
stale-COP chain TSRA-R-ML gain_min:  0.486689 -> 0.699806
mission_guard_trigger_count_mean:    3.2
mission_guard_event_trace_count_mean: 1.0
```

## 8. 반복 실험 결과

30개 seed 평균:

```text
E3 AURA Attack:           impact 0.914 +- 0.056
E5 AURA + TSRA-R Defense: impact 0.140 +- 0.026
E7 ML AURA + ML TSRA-R Defense: impact 0.156 +- 0.013
```

Resilience Gain:

```text
TSRA-R full: 약 84.6% +- 2.9%
ML/ML reactive defense: 약 82.8% +- 1.9%
```

## 9. Action Ablation

TSRA-R action별 기여도를 보기 위해 full TSRA-R에서 방어 액션을 하나씩 제거하는 ablation을 추가했다.

실행:

```bash
python3 -m src.experiments.run_tsra_ablation
```

산출물:

```text
outputs/batch/tsra_action_ablation_summary.csv
outputs/figures/tsra_action_ablation.png
```

핵심 결과:

```text
full impact:              0.140
no_priority_reroute:      0.340  delta +0.200
no_stale_badge:           0.347  delta +0.206
no_video_throttle:        0.117  delta -0.023
no_pace_switch:           0.107  delta -0.033
```

## 10. Mission Impact Decomposition

`Mission Impact`는 아래 5개 성분으로 해석한다.

```text
critical latency
trusted stale exposure
priority inversion
kill-chain delay
recovery instability
```

중요한 점:

- TSRA-R은 raw stale data를 항상 제거하지 않는다.
- 대신 `stale_badge`로 오래된 COP 객체가 최신 정보처럼 신뢰되는 위험을 줄인다.
- 따라서 stale 성분은 raw `stale_data_ratio`가 아니라 `trusted_stale_exposure`로 본다.

실행:

```bash
python3 -m src.experiments.mission_impact_decomposition
```

산출물:

```text
outputs/report_tables/mission_impact_decomposition.csv
outputs/report_tables/mission_impact_decomposition.md
```

## 11. Operator Alerts

TSRA-R은 `DefenseEvent`만 남기는 데서 끝나지 않는다.

방어 이벤트를 사람이 읽는 운영 알림으로 변환하는 산출물을 둔다.

실행:

```bash
python3 -m src.experiments.operator_alerts
```

산출물:

```text
outputs/report_tables/operator_alerts.csv
outputs/report_tables/operator_alerts.md
```

각 alert에는 다음이 들어간다.

```text
severity
operator_alert
mission_rationale
expected_operator_response
related_attack_context
metric snapshot
decision_trace_reason
```

현재 포함 action:

```text
ml_attack_alert
pace_switch
priority_reroute
stale_badge
video_throttle
```

주의:

- 실제 운용 지시가 아니라 폐쇄형 시뮬레이션 알림이다.
- RF, exploit, live network action은 포함하지 않는다.

## 12. Defense Effectiveness Ledger

Operator alert는 사람이 읽는 알림이고, defense effectiveness ledger는 같은 `DefenseEvent`가 지표에 어떤 local effect를 남겼는지 확인하는 표다.

실행:

```bash
python3 -m src.experiments.defense_effectiveness_ledger
```

산출물:

```text
outputs/report_tables/defense_effectiveness_ledger.csv
outputs/report_tables/defense_effectiveness_ledger.md
```

각 row에는 다음이 들어간다.

```text
DefenseEvent
operator_alert
related_attack_context
before/after mission_impact
before/after p95_critical_latency_sec
before/after trusted_stale_exposure
before/after priority_inversion_rate
observed_effect
interpretation
```

현재 검증 기준:

```text
E5 + E7 defense ledger rows: 52
actions: ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
observed_effect labels: improved, held, degraded_or_delayed
```

해석:

- `priority_reroute`를 제거하면 priority inversion이 크게 증가한다. 이 액션은 critical traffic 보호의 핵심이다.
- `stale_badge`를 제거하면 trusted stale exposure가 크게 증가한다. 이 액션은 지휘소가 오래된 COP 정보를 최신 정보로 믿는 위험을 낮추는 핵심이다.
- `pace_switch`는 fallback chasing 대응성을 높이지만 전환 횟수가 recovery instability 성분을 키울 수 있다. 따라서 단일 점수 최소화가 아니라 PACE 운용 복원력으로 분리해서 해석한다.
- `video_throttle`은 현재 scalar mission impact만 보면 항상 이득으로 나타나지 않지만, critical traffic capacity 보호용 운용 기능으로 유지한다.

PACE 전환별 근거는 다음 산출물에서 확인한다.

```bash
python3 -m src.experiments.pace_transition_audit
```

```text
outputs/report_tables/pace_transition_audit.csv
outputs/report_tables/pace_transition_audit.md
```

현재 감사 결과는 4개 PACE 전환을 `satcom_to_fallback` 2개, `fallback_reselect` 2개로 구분한다.

## 10. Adaptive Memory TSRA-R

AdaptiveTSRA-R은 기본 TSRA-R을 대체하지 않는다. 기본 E1~E7 baseline은 그대로 두고, AgentMemory가 다음 방어 판단에 영향을 주는 별도 실험 모드로 구현했다.

코드:

```text
src/tsra_r/adaptive_defender.py
src/experiments/run_adaptive_memory.py
src/experiments/adaptive_defense_decision_path_audit.py
```

동작 방식:

- `priority_reroute`와 `stale_badge`는 항상 유지한다.
- `video_throttle`은 최근 memory에서 critical traffic과 video queue pressure가 반복될 때만 켠다.
- `pace_switch`는 SATCOM 저하와 심한 queue pressure가 같이 반복될 때만 켠다.
- 판단마다 `feedback.adaptive_policy`에 enabled actions, memory counts, action별 gate decision, reasons를 남긴다.
- 각 `candidate_actions` row에는 `adaptive_enabled`, `adaptive_gate_class`, `adaptive_gate_reason`, `adaptive_memory_evidence`가 남는다.

30-seed 비교 결과:

```text
full TSRA-R impact:      0.140260
adaptive TSRA-R impact:  0.109489
priority inversion:      0.050609 -> 0.027455
video throttle count:    6.4 -> 3.1
```

Decision path 감사:

```bash
python3 -m src.experiments.adaptive_defense_decision_path_audit --fail-on-error
```

```text
adaptive_defense_decision_path_audit rows: 6 pass
trace_count: 1830
update_adaptive_action_policy: 1830
video_eligible_held: 1146
pace_eligible_held: 154
emission_gate_violations: 0
```

해석:

- AdaptiveTSRA-R은 방어 액션을 무조건 많이 쓰는 정책이 아니다.
- Memory에 반복 증거가 있을 때만 optional action을 켜서 과한 video throttle을 줄인다.
- 후보별 memory gate와 실제 emitted defense event가 일치하므로, action과 restraint를 모두 trace로 설명할 수 있다.
- mission impact와 priority inversion이 같이 감소했으므로, Memory가 실제 방어 판단에 영향을 준 증거로 볼 수 있다.

## 11. 현재 구현 상태

완료:

- AgentRuntime 연결
- AgentMemory belief state 유지
- ToolRegistry 기반 방어 조건 평가/탐지 도구 호출
- DecisionTrace JSONL 로그
- rule 기반 priority reroute
- rule 기반 video throttle
- stale badge
- PACE switch
- ML anomaly detector
- ML detector 기반 reactive defense window
- AURA attack context 기반 defense priority score
- defense priority score 기반 core event ordering
- Defense Priority Decision Path 감사
- Adaptive Memory 기반 optional action gating
- Adaptive Defense Decision Path 감사
- defense event JSONL 로그
- 30-seed 반복 실험

보완할 것:

- PACE switch의 link selection 근거를 더 정교화
- operator alert 문구 자동 생성
- incident report 자동 생성

## 12. 런타임 구조

TSRA-R은 `src/agents/AgentRuntime` 위에서 실행된다.

Rule TSRA-R:

```text
AgentRuntime
  goal: minimize mission impact with bounded defensive response actions
  memory: mode, action_cooldowns, event_count, attack_context, attack_context_seen
  tools:
    - summarize_attack_context
    - evaluate_defense_conditions
    - select_fallback_link
	  trace:
	    - observation
	    - cross_agent_attack_context
	    - candidate_actions
	    - defense_base_score
	    - attack_context_bonus
	    - attack_context_score_reason
	    - tool_calls
	    - selected_action
	    - reason
    - feedback
```

ML TSRA-R:

```text
AgentRuntime
  goal: open reactive defense windows when anomaly probability exceeds threshold
  memory: active_defense_until, last_probability, last_alert_time, attack_context
  tools:
    - summarize_attack_context
    - predict_attack_probability
    - assess_mission_risk_guard
  trace:
    - detector probability
    - threshold decision
    - opened defense window
    - emitted defense events
```

Adaptive TSRA-R:

```text
AgentRuntime
  goal: minimize mission impact using memory-gated defensive response actions
  memory: adaptive_policy, enabled_actions, action_cooldowns
  tools:
    - summarize_attack_context
    - update_adaptive_action_policy
    - evaluate_defense_conditions
    - select_fallback_link
  trace:
    - memory-based enabled action set
    - candidate-level adaptive gate reason
    - candidate-level attack context reason
    - repeated pressure/degradation counts
    - emitted defense events
    - selected no-op/action reason
```

생성 로그:

```text
outputs/experiments/<experiment>/tsra_r_decision_traces.jsonl
```

이제 TSRA-R의 한 번의 판단은 `DefenseEvent`만 남기지 않는다. 탐지 확률, 방어 조건, cooldown 상태, AURA attack context, 어떤 액션이 가능했는지, 왜 no-op 또는 특정 방어 액션을 실행했는지까지 남긴다. emitted `DefenseEvent.details.related_attack_context`에도 같은 공격 context 요약이 남는다.

추가로 Rule TSRA-R은 후보별 방어 우선순위 점수를 남긴다.

```text
score = defense_base_score + attack_context_bonus
```

- `defense_base_score`: action별 기본 임무 보호 우선순위다.
- `attack_context_bonus`: active/recent AURA attack type이 해당 방어 action과 직접 관련될 때만 붙는 제한된 가산점이다.
- `attack_context_score_reason`: `counter_queue_pressure_priority_reroute`, `counter_video_queue_pressure` 같은 점수 이유를 남긴다.

방어 우선순위 판단 경로는 별도 감사로 검증한다.

```bash
python3 -m src.experiments.defense_priority_decision_path_audit --fail-on-error
```

현재 감사 결과:

```text
defense_priority_decision_path_audit rows: 6 pass
scored_candidates: 671
formula_matches: 671
attack_context_bonus_candidates: 177
attack_context_bonus_events: 51
checked_event_matches: 70
event_match_failures: 0
ordered_core_defense_traces: 12/12
no_op_ready_violations: 0
```

해석:

- 후보 row의 `score`와 emitted `DefenseEvent.details.defense_priority_score`가 같은 공식으로 이어진다.
- attack context bonus는 관련 방어 action에만 붙고, 상한 안에서 유지된다.
- 같은 tick에 여러 core defense event가 나오면 priority score가 높은 순서로 정렬된다.
- no-op 판단은 ready candidate가 없을 때만 통과한다.
- 같은 tick에서 여러 core defense event가 나오면 `defense_priority_score` 내림차순으로 생성되어 시뮬레이터에 적용된다.

Cross-agent 감사 결과:

```text
cross_agent_context_audit rows: 8 pass
attack_context_bonus_candidates: 61
attack_context_bonus_events: 25
selected_defense_bonus_traces: 22
ordered_core_defense_traces: 6/6
```
