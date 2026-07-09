# 다음 개발 큐

이 큐는 `COMPETITION_DIRECTION.md`를 실행 항목으로 바꾼 것이다. 작업 순서는 공격-방어-AI 에이전트 공방 루프를 더 명확하게 만드는 순서로 잡는다.

## P0. DecisionTrace 요약기

상태: 완료

문제:

- 현재 `aura_decision_traces.jsonl`, `tsra_r_decision_traces.jsonl`은 구조적으로 좋지만 사람이 바로 읽기에는 길다.
- AURA가 공격을 고른 이유와 TSRA-R이 방어를 고른 이유를 같은 시간축에서 비교하기 어렵다.

구현:

```text
src/experiments/trace_summary.py
```

입력:

```text
outputs/experiments/E3_rule_aura/aura_decision_traces.jsonl
outputs/experiments/E5_rule_aura_tsra_r/aura_decision_traces.jsonl
outputs/experiments/E5_rule_aura_tsra_r/tsra_r_decision_traces.jsonl
outputs/experiments/E7_ml_aura_ml_tsra_r/aura_decision_traces.jsonl
outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl
```

출력:

```text
outputs/report_tables/agent_decision_trace_summary.csv
outputs/report_tables/agent_decision_trace_summary.md
```

완료 기준:

- 완료. 시간, agent, policy, selected_action, reason, top candidate, probability/score가 표로 나온다.
- 완료. E3, E5, E7의 AURA/TSRA-R 판단이 한 파일에서 비교된다.
- 완료. `python3 -m src.experiments.trace_summary` 명령으로 재생성 가능하다.

검증:

```bash
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
python3 -m compileall src
```

검증 결과:

```text
agent_decision_trace_summary.csv: 215 rows
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
experiments: E3_rule_aura, E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
```

## P1. AURA COA Card

상태: 완료

문제:

- AURA가 고른 공격 효과가 event JSON에는 남지만, 공격 후보-예상 영향-선택 이유를 한 장 단위로 보기 어렵다.

구현:

```text
src/experiments/aura_coa_cards.py
```

출력:

```text
outputs/report_tables/aura_coa_cards.md
outputs/report_tables/aura_coa_cards.csv
```

완료 기준:

- 완료. 각 `AttackEvent`마다 COA card가 생성된다.
- 완료. card에는 attack_type, target_link, duration, expected_impact, score, reason이 들어간다.
- 완료. 실제 공격 명령처럼 보이지 않도록 safety boundary를 각 카드에 명시한다.

검증:

```bash
python3 -m src.experiments.run_all
python3 -m src.experiments.aura_coa_cards
```

검증 결과:

```text
aura_coa_cards.csv: 15 cards
experiments: E3_rule_aura, E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
agents: AURA, AURA-ML
missing_safety: 0
unknown_rank: 0
```

## P2. TSRA-R Action Ablation

상태: 완료

문제:

- TSRA-R이 여러 방어 액션을 동시에 수행하므로 어떤 액션이 어떤 지표에 기여했는지 분리하기 어렵다.

구현:

```text
src/experiments/run_tsra_ablation.py
```

실험 조건:

```text
full
no_priority_reroute
no_video_throttle
no_stale_badge
no_pace_switch
```

출력:

```text
outputs/batch/tsra_action_ablation_summary.csv
outputs/figures/tsra_action_ablation.png
```

완료 기준:

- 완료. 각 방어 액션 제거 시 mission impact, trusted stale exposure, priority inversion 변화가 나온다.
- 완료. TSRA-R의 가치가 단일 mission impact가 아니라 방어 기능별 지표로 설명 가능해진다.

검증:

```bash
python3 -m src.experiments.run_tsra_ablation
python3 -m compileall src
```

검증 결과:

```text
tsra_action_ablation_summary.csv: 5 conditions
tsra_action_ablation_raw.csv: 150 rows
conditions: full, no_priority_reroute, no_video_throttle, no_stale_badge, no_pace_switch
figure: outputs/figures/tsra_action_ablation.png
```

핵심 결과:

```text
no_priority_reroute: mission impact +0.208, priority inversion +0.473
no_stale_badge: mission impact +0.205, trusted stale exposure +0.388
no_video_throttle: mission impact -0.013
no_pace_switch: mission impact -0.017
```

해석:

- `priority_reroute`는 priority inversion과 critical latency 억제에 핵심이다.
- `stale_badge`는 trusted stale exposure 억제에 핵심이다.
- 현재 scalar mission impact에서는 `video_throttle`, `pace_switch`가 항상 이득으로 나타나지는 않으므로 운용 목적과 지표를 분리해 해석해야 한다.

## P3. Adaptive Memory

상태: 다음 작업

문제:

- 현재 AgentMemory는 최근 관측/판단과 belief state를 보관하지만, 다음 판단 기준을 바꾸는 데는 제한적으로만 사용된다.

구현 방향:

- 기본 E1~E7 baseline은 유지한다.
- 별도 옵션으로 adaptive mode를 둔다.
- 최근 false alarm, late defense, ineffective attack 등을 memory에 반영해 threshold/action ranking을 조정한다.

완료 기준:

- adaptive mode on/off가 가능하다.
- 기존 기본 실험 결과가 의도치 않게 바뀌지 않는다.
- adaptive mode 전용 실험 결과가 따로 생성된다.

검증:

```bash
python3 -m src.experiments.run_all
python3 -m src.experiments.run_adaptive_memory
```

## 진행 원칙

각 작업은 완료 시 다음을 만족해야 한다.

- 코드가 실행된다.
- 출력 파일이 생성된다.
- 개발 판단 근거가 Markdown에 남는다.
- `hbin` 브랜치에만 커밋/푸시된다.
- `main`은 보호 브랜치로 유지된다.
