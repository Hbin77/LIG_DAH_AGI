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
- 장기 학습 또는 온라인 policy update는 아직 없다.
- Tool은 시뮬레이터 내부 함수만 호출한다.
- 외부 네트워크, 실제 RF, 실제 공격 도구는 호출하지 않는다.

## 다음 개선

1. decision trace를 요약하는 CLI 추가
2. AURA 후보별 COA card 자동 생성
3. TSRA-R 방어 action별 ablation 실행기 추가
4. Memory에 최근 공격/방어 효과 피드백을 누적해 adaptive threshold 조정
