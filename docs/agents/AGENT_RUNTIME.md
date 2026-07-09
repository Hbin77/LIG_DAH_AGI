# Agent Runtime 구조

## 목적

기존 AURA와 TSRA-R은 `decide(state)`가 바로 이벤트를 반환하는 정책 객체에 가까웠다. 이번 변경으로 두 에이전트는 공통 런타임을 통해 아래 루프를 명시적으로 수행한다.

```text
observe
-> memory summary
-> tool call
-> candidate action scoring
-> selected action
-> decision trace
-> feedback/belief update
```

이 구조의 목표는 Python 함수 호출을 넘어서, 각 에이전트가 어떤 목표로 어떤 도구를 호출했고 왜 그 행동을 골랐는지 실행 기록으로 남기는 것이다.

## 코드 구성

```text
src/agents/
  schema.py    AgentObservation, ToolCallRecord, DecisionTrace
  memory.py    AgentMemory
  tools.py     AgentTool, ToolRegistry
  runtime.py   AgentRuntime
```

## 핵심 컴포넌트

### AgentRuntime

역할:

- 에이전트 목표 보관
- `MissionState`를 `AgentObservation`으로 요약
- 도구 호출을 `ToolCallRecord`로 기록
- 최종 판단을 `DecisionTrace`로 저장
- `AgentMemory`에 관측/판단/믿음 상태를 반영

### AgentMemory

역할:

- 최근 관측값 유지
- 최근 판단 trace 유지
- 에이전트별 belief state 유지

현재 belief 예:

```text
AURA:
  last_attack_time
  event_count
  last_attack_type

TSRA-R:
  mode
  action_cooldowns
  event_count

TSRA-R-ML:
  active_defense_until
  last_probability
  last_alert_time

TSRA-R-ADAPTIVE:
  adaptive_policy
  enabled_actions
  action_cooldowns
```

### ToolRegistry

역할:

- 에이전트가 사용할 수 있는 도구를 이름으로 등록
- 실행 시 입력 요약과 출력 요약을 trace에 남김

AURA 도구:

```text
generate_attack_candidates
estimate_candidate_effect
estimate_detectability
predict_candidate_impact
```

TSRA-R 도구:

```text
evaluate_defense_conditions
select_fallback_link
predict_attack_probability
update_adaptive_action_policy
```

### DecisionTrace

각 판단 주기마다 아래 정보가 남는다.

```text
trace_id
agent
time_sec
goal
policy
observation
memory
candidate_actions
tool_calls
selected_action
reason
feedback
```

## 생성 로그

각 실험 폴더에 다음 JSONL 파일이 생성된다.

```text
outputs/experiments/<experiment>/aura_decision_traces.jsonl
outputs/experiments/<experiment>/tsra_r_decision_traces.jsonl
```

## 계약 검증

AURA, TSRA-R, MissionSimulator가 공유하는 JSONL 인터페이스는 다음 명령으로 검증한다.

```bash
python3 -m src.experiments.validate_event_contracts --fail-on-error
```

산출물:

```text
outputs/report_tables/agent_contract_validation.csv
outputs/report_tables/agent_contract_validation.md
```

검증 범위:

- attack event schema
- defense event schema
- mission event schema
- metric snapshot schema
- AURA DecisionTrace schema
- TSRA-R DecisionTrace schema
- attack/defense event와 trace의 cross-contract

## 품질 감사

DecisionTrace가 에이전트 판단 루프 증거로 충분한지는 다음 명령으로 감사한다.

```bash
python3 -m src.experiments.trace_quality_audit --fail-on-error
```

산출물:

```text
outputs/report_tables/decision_trace_quality_audit.csv
outputs/report_tables/decision_trace_quality_audit.md
```

감사 항목:

- reason, observation, memory, feedback, selected action coverage
- tool call coverage
- candidate action coverage
- non-no-op selected action count
- selected attack/defense event count

## 루프 리플레이

대표 판단 루프는 다음 명령으로 사람이 읽을 수 있는 replay로 재구성한다.

```bash
python3 -m src.experiments.agent_loop_replay
```

산출물:

```text
outputs/report_tables/agent_loop_replay.csv
outputs/report_tables/agent_loop_replay.md
```

Replay는 각 active agent/policy에서 `no_op` 판단과 실제 action 판단을 뽑아 아래 흐름으로 보여준다.

```text
observe -> memory -> tools -> candidates -> selected_action -> feedback -> reason
```

## Decision Causality Audit

DecisionTrace의 `selected_action`이 후보, 도구 호출, 점수 또는 threshold 근거와 맞는지 확인한다.

```bash
python3 -m src.experiments.agent_decision_causality_audit
```

산출물:

```text
outputs/report_tables/agent_decision_causality_audit.csv
outputs/report_tables/agent_decision_causality_audit.md
```

감사 항목:

- selected action과 candidate action 매칭
- required tool presence
- AURA score top-candidate support
- TSRA-R eligible/ready support
- TSRA-R-ML probability threshold support
- no-op 선택 근거

## Decision Margin Audit

DecisionTrace의 선택이 단순히 유효한지뿐 아니라 얼마나 강한 근거를 가졌는지 확인한다.

```bash
python3 -m src.experiments.agent_decision_margin_audit
```

산출물:

```text
outputs/report_tables/agent_decision_margin_audit.csv
outputs/report_tables/agent_decision_margin_audit.md
```

감사 항목:

- AURA selected score와 runner-up score 차이
- AURA attack threshold 대비 margin
- TSRA-R eligible/ready defense action count
- TSRA-R-ML anomaly probability와 threshold margin
- no-op 판단의 근거

## Goal Alignment Audit

DecisionTrace의 선택이 각 에이전트의 목표와 관측 위험에 맞는지 확인한다.

```bash
python3 -m src.experiments.agent_goal_alignment_audit --fail-on-error
```

산출물:

```text
outputs/report_tables/agent_goal_alignment_audit.csv
outputs/report_tables/agent_goal_alignment_audit.md
```

감사 항목:

- AURA attack_event가 threshold 이상 top mission-impact score인지
- AURA no-op이 min_start, cooldown, max_events, no candidate, below-threshold 근거를 갖는지
- TSRA-R defense action이 priority, video, stale, PACE, ML threshold 조건과 맞는지
- TSRA-R no-op이 ready action 부재 또는 active defense window 유지로 설명되는지

## Decision Feedback Audit

DecisionTrace의 선택이 실제 event log와 metric feedback으로 이어졌는지 확인한다.

```bash
python3 -m src.experiments.agent_decision_feedback_audit --fail-on-error
```

산출물:

```text
outputs/report_tables/agent_decision_feedback_audit.csv
outputs/report_tables/agent_decision_feedback_audit.md
```

감사 항목:

- E5/E7 selected attack/defense event가 event log에 존재하는지
- selected event 주변 metric feedback window가 있는지
- attack_event가 pressure observed 또는 defense containment로 설명되는지
- defense_event가 improved, held, bounded attribution, 또는 ML defense window trigger로 설명되는지

## Memory/Belief Audit

AgentMemory가 단순 필드가 아니라 다음 판단에 이어지는 loop state인지 확인한다.

```bash
python3 -m src.experiments.agent_memory_belief_audit
```

산출물:

```text
outputs/report_tables/agent_memory_belief_audit.csv
outputs/report_tables/agent_memory_belief_audit.md
```

감사 항목:

- memory coverage
- observation/decision count nondecreasing 여부
- belief key와 changing belief key
- feedback key
- 이전 selected action이 다음 memory의 `last_selected_action`으로 들어가는지

## Memory Influence Audit

AgentMemory가 단순 저장소가 아니라 실제 decision gate로 작동하는지 확인한다.

```bash
python3 -m src.experiments.agent_memory_influence_audit --fail-on-error
```

산출물:

```text
outputs/report_tables/agent_memory_influence_audit.csv
outputs/report_tables/agent_memory_influence_audit.md
```

감사 항목:

- AURA/AURA-ML cadence memory가 cooldown과 max-event gate를 만드는지
- TSRA-R action cooldown memory가 eligible-but-not-ready defense action을 막는지
- TSRA-R-ML active defense window memory가 reactive window를 유지하는지
- Adaptive TSRA-R memory policy가 mission impact와 optional defense load를 줄이는지

## Tool Usage Audit

AgentTool이 단순 등록 목록이 아니라 실제 판단 루프에서 호출되는지 확인한다.

```bash
python3 -m src.experiments.agent_tool_usage_audit
```

산출물:

```text
outputs/report_tables/agent_tool_usage_audit.csv
outputs/report_tables/agent_tool_usage_audit.md
```

감사 항목:

- tool invocation count
- trace coverage
- input_summary coverage
- output_summary coverage
- tool status/error count
- tool role과 decision link

## Operator Alerts

TSRA-R의 `DefenseEvent`와 `DecisionTrace`는 operator-facing alert로도 재구성한다.

```bash
python3 -m src.experiments.operator_alerts
```

산출물:

```text
outputs/report_tables/operator_alerts.csv
outputs/report_tables/operator_alerts.md
```

각 alert는 방어 action, severity, mission rationale, expected operator response, related attack context, metric snapshot, trace reason을 연결한다. 이 산출물도 폐쇄형 시뮬레이션 설명이며 실제 RF, exploit, live network action은 포함하지 않는다.

## Defense Effectiveness Ledger

TSRA-R의 `DefenseEvent`는 local metric before/after movement와도 연결한다.

```bash
python3 -m src.experiments.defense_effectiveness_ledger
```

산출물:

```text
outputs/report_tables/defense_effectiveness_ledger.csv
outputs/report_tables/defense_effectiveness_ledger.md
```

각 ledger row는 방어 action, operator alert, related attack context, 30초 전후 mission impact, critical latency, trusted stale exposure, priority inversion 변화량, observed effect, interpretation을 묶는다.

## Collaboration Graph

공격 에이전트, 시뮬레이터, 방어 에이전트, operator alerts, defense effectiveness ledger, metrics, verifier의 협력 구조는 별도 graph로 재구성한다.

```bash
python3 -m src.experiments.agent_collaboration_graph
```

산출물:

```text
outputs/report_tables/agent_collaboration_graph.csv
outputs/report_tables/agent_collaboration_graph.md
outputs/report_tables/agent_collaboration_graph.mmd
```

이 그래프는 각 edge마다 evidence file, evidence count, validation status를 붙인다.

## Closed-Loop Episode Replay

공격 1건 기준의 순차 공방 흐름은 closed-loop episode replay로 재구성한다.

```bash
python3 -m src.experiments.closed_loop_episode_replay
```

산출물:

```text
outputs/report_tables/closed_loop_episode_replay.csv
outputs/report_tables/closed_loop_episode_replay.md
```

각 episode는 AttackEvent, response audit, defense chain, operator alert chain, mission impact start/peak/end, outcome, residual risk를 한 record로 묶는다.

## 인터페이스 Manifest

에이전트별 입력, 메모리, 도구, 후보, 선택 행동, 이벤트 출력 계약은 다음 명령으로 생성한다.

```bash
python3 -m src.experiments.agent_interface_manifest
```

산출물:

```text
outputs/report_tables/agent_interface_manifest.csv
outputs/report_tables/agent_interface_manifest.md
```

이 manifest는 AURA/AURA-ML을 `attack`, TSRA-R/TSRA-R-ML을 `defense` side로 분리해 보여준다.

## Capability Matrix

에이전트별 capability와 검증 증거는 다음 명령으로 생성한다.

```bash
python3 -m src.experiments.agent_capability_matrix
```

산출물:

```text
outputs/report_tables/agent_capability_matrix.csv
outputs/report_tables/agent_capability_matrix.md
```

이 matrix는 AURA 공격 효과와 TSRA-R 방어 액션을 runtime action, decision source, observed effect, validation gate에 연결한다.

## Attack-Defense Coverage

AURA 공격 capability가 어떤 TSRA-R 방어 capability로 커버되는지는 다음 명령으로 생성한다.

```bash
python3 -m src.experiments.attack_defense_coverage
```

산출물:

```text
outputs/report_tables/attack_defense_coverage.csv
outputs/report_tables/attack_defense_coverage.md
```

이 coverage table은 `bandwidth_limit`, `failover_chasing`, `queue_pressure`, `stale_cop_induction`을 각각 대응 방어 capability, validation gate, residual risk에 연결한다. 공격/방어 에이전트를 따로 개발해도 이 표가 공방 연결성 기준이 된다.

## Response Audit

정적 coverage가 실제 이벤트 로그에서 지켜지는지는 다음 명령으로 감사한다.

```bash
python3 -m src.experiments.attack_defense_response_audit
```

산출물:

```text
outputs/report_tables/attack_defense_response_audit.csv
outputs/report_tables/attack_defense_response_audit.md
```

이 audit는 E5/E7의 공격 이벤트마다 required defense가 공격 시점에 이미 active였는지, 또는 40초 response window 안에 나왔는지 확인한다. required defense가 누락되면 실패로 보고, support defense 누락은 residual risk로 남긴다.

## PACE Transition Audit

`pace_switch` 전환의 이유와 tradeoff는 다음 명령으로 감사한다.

```bash
python3 -m src.experiments.pace_transition_audit
```

산출물:

```text
outputs/report_tables/pace_transition_audit.csv
outputs/report_tables/pace_transition_audit.md
```

이 audit는 각 PACE 전환을 inferred source link, target link, active attack context, near-future attack, metric snapshot, recovery instability와 연결한다.

예시:

```json
{
  "agent": "TSRA-R-ML",
  "goal": "open reactive defense windows when anomaly probability exceeds threshold",
  "policy": "ml_anomaly_detector",
  "candidate_actions": [
    {
      "action": "open_defense_window",
      "eligible": true,
      "probability": 0.954537,
      "threshold": 0.75
    }
  ],
  "selected_action": {
    "type": "defense_events",
    "events": [
      {
        "action": "stale_badge"
      }
    ]
  },
  "reason": "detector opened or maintained defense window"
}
```

## 현재 한계

- Memory는 최근 관측/판단과 belief state를 저장하는 경량 메모리다.
- AdaptiveTSRA-R에서는 이 Memory가 optional defense action gating에 직접 사용된다.
- 장기 학습 또는 온라인 policy update는 아직 없다.
- Tool은 시뮬레이터 내부 함수만 호출한다.
- 외부 네트워크, 실제 RF, 실제 공격 도구는 호출하지 않는다.

## 다음 개선

1. Adaptive Memory 정책을 더 많은 mission phase별 rule로 분리
2. 공방 timeline에서 trace와 event를 같이 보여주는 요약 산출물 추가
3. PACE switch의 link selection 근거를 더 정교화
4. operator alert와 incident summary 자동 생성
