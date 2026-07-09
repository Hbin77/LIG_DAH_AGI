# 개발 로그와 판단 근거

## 현재 목표

DAH 2026 예선 제출 산출물에 사용할 팀 단위 공방형 AI 에이전트 프로토타입을 만든다.

핵심 요구:

- 공격 에이전트와 방어 에이전트를 분리한다.
- 두 에이전트가 같은 시뮬레이터와 같은 로그 체계에서 공방한다.
- 실제 SATCOM 공격이 아니라 폐쇄형 synthetic simulation으로만 구현한다.
- 실험 결과는 단일 실행이 아니라 반복 실험 평균/표준편차로 제시한다.
- 개발 과정과 판단 근거를 팀 공유용 Markdown으로 남긴다.

## 2026-07-09 개발 판단

### 1. 실제 공격 구현을 하지 않기로 한 이유

실제 RF 재밍, 장비 침투, exploit code, 운용 가능한 SATCOM 파라미터는 공개 repo와 제출 산출물에 넣으면 위험하다.

따라서 공격은 다음으로 제한했다.

- latency 증가
- jitter 증가
- packet loss 증가
- bandwidth 제한
- queue pressure
- critical-window degradation

이들은 모두 시뮬레이터 내부 효과이며 실제 장비에 영향을 주지 않는다.

### 2. AURA와 TSRA-R을 분리한 이유

예선 배점에서 공격 시나리오, 방어 전략, AI 에이전트 아키텍처가 핵심이다. 공격만 있으면 방어 25점과 협력 구조 25점이 약해진다.

따라서 구조를 다음처럼 분리했다.

```text
AURA: 공격 후보 생성 및 공격 효과 선택
Mission Simulator: 링크, 큐, 메시지, COP freshness 계산
TSRA-R: 탐지, 우선순위 재조정, PACE 전환, stale badge
Metrics: Mission Impact, trusted stale exposure, priority inversion
```

### 3. `trusted_stale_exposure`를 추가한 이유

`stale_data_ratio`는 오래된 정보의 비율이다. TSRA-R이 오래된 정보를 즉시 없애지는 못한다.

하지만 TSRA-R은 stale badge를 붙여 지휘소가 오래된 정보를 최신 정보로 오인하지 않게 한다. 이 방어 효과를 표현하려면 별도 지표가 필요했다.

그래서 다음 지표를 추가했다.

```text
trusted_stale_exposure = 지휘소가 stale 정보를 최신으로 신뢰할 위험
```

방어 전에는 raw stale ratio와 같고, stale badge가 활성화되면 exposure를 낮춘다.

### 4. 30-seed 반복 실험을 추가한 이유

단일 seed 결과는 우연일 수 있다. 반복 실험 평균과 표준편차가 있어야 결과를 안정적으로 해석할 수 있다.

따라서 `run_batch.py`로 30개 seed 반복 실험을 추가했다.

산출물:

- `outputs/batch/repeated_experiment_summary.csv`
- `outputs/batch/resilience_gain_summary.csv`
- `outputs/figures/batch_mission_impact_errorbar.png`
- `outputs/figures/batch_resilience_gain.png`

### 5. ML 사용 위치를 제한한 이유

ML을 모든 곳에 넣으면 설명 가능성이 떨어진다. 그래서 기능을 두 곳으로 제한했다.

1. AURA Impact Predictor: 공격 후보의 Mission Impact 예측
2. TSRA-R Anomaly Detector: 공격성 저하 탐지

GPU MPS MLP는 최종 정책의 기본값이 아니라 대규모 synthetic 후보 학습 확장성 실험으로 둔다.

### 6. GitHub에 raw log/model binary를 제외한 이유

반복 실험 raw log와 dataset/model binary는 재생성 가능하고 repo를 무겁게 만든다.

따라서 GitHub에는 코드, 문서, 요약 CSV, 메트릭 JSON, 그래프만 올린다.

### 7. `main` 브랜치를 보호용 기본 브랜치로 복구한 이유

원격 저장소 확인 결과 `main` 브랜치가 없고 GitHub 기본 브랜치가 `hbin`으로 잡혀 있었다. 대회 개발은 `hbin`에서 진행하되, 저장소의 기본 브랜치인 `main`은 삭제하지 않고 남겨두는 편이 안전하다.

조치:

- `main` 브랜치를 새로 만들었다.
- `main`에는 개발 산출물을 올리지 않고 보호용 README만 두었다.
- GitHub 기본 브랜치를 `main`으로 되돌렸다.
- 이후 코드, 실험 결과, 공유 문서는 계속 `hbin`에만 커밋한다.

의도:

```text
main = 저장소 기본/보호 브랜치
hbin = 실제 대회 개발 브랜치
```

이 방식이면 `main`은 보존하면서도, "개발은 hbin 브랜치에만 공유"라는 팀 운영 원칙을 지킬 수 있다.

### 8. 팀 협업 전제로 문서 표현을 정리한 이유

팀원이 추가될 예정이므로, 개발 문서와 공유 산출물에서 개인 중심 작업처럼 읽히는 표현을 피해야 한다. 지금부터 문서의 주체를 `팀`, `개발팀`, `공격 담당`, `방어 담당`, `실험 담당`처럼 확장 가능한 표현으로 유지한다.

운영 기준:

- 개인 중심 작업처럼 보이는 표현은 쓰지 않는다.
- 역할 분배가 확정되면 팀 구성 문서에 이름과 담당 영역을 연결한다.
- 개발 이력은 계속 `hbin` 브랜치와 Markdown 로그에 남긴다.

### 9. Agent Runtime을 추가한 이유

기존 AURA와 TSRA-R은 `decide(state)`가 바로 이벤트를 반환하는 정책 객체에 가까웠다. Python으로 구현했다는 사실만으로 AI 에이전트라고 보기에는 구조적 근거가 약했다.

그래서 공통 에이전트 런타임을 추가했다.

```text
src/agents/schema.py
src/agents/memory.py
src/agents/tools.py
src/agents/runtime.py
```

추가된 구조:

- `AgentRuntime`: observe, tool call, decision trace 기록 담당
- `AgentMemory`: 최근 관측/판단과 belief state 유지
- `ToolRegistry`: 에이전트별 도구 등록 및 호출
- `DecisionTrace`: 후보, 도구 호출, 선택 행동, 이유, 피드백 기록

AURA에 연결한 도구:

- `generate_attack_candidates`
- `estimate_candidate_effect`
- `estimate_detectability`
- `predict_candidate_impact`

TSRA-R에 연결한 도구:

- `evaluate_defense_conditions`
- `select_fallback_link`
- `predict_attack_probability`

생성 로그:

```text
outputs/experiments/<experiment>/aura_decision_traces.jsonl
outputs/experiments/<experiment>/tsra_r_decision_traces.jsonl
```

검증:

```text
python3 -m compileall src
python3 -m src.experiments.run_all
```

단일 실행 결과는 기존과 동일하게 유지됐다. 30-seed 배치에서는 ML TSRA-R의 `active_defense_until=0` 경계 조건을 바로잡으면서 E7 평균만 `0.13487`에서 `0.13515`로 미세하게 바뀌었다. 핵심 변경은 정책 고도화가 아니라 에이전트 구조와 판단 근거 기록 강화다.

### 10. 대회 방향을 개발 기준으로 고정한 이유

이 프로젝트의 방향은 단순 기능 추가가 아니라 방산 임무 환경에서 공격, 방어, AI 에이전트가 실제로 맞물려 돌아가는 구조를 만드는 것이다. 따라서 앞으로의 개발 기준을 별도 문서로 고정했다.

기준 문서:

```text
docs/process/COMPETITION_DIRECTION.md
```

이 문서에서 고정한 최상위 판단 기준:

```text
이 변경이 공격-방어-AI 에이전트 공방 루프를 더 명확하고 검증 가능하게 만드는가?
```

다음 개발 우선순위:

1. DecisionTrace 요약기
2. AURA COA Card
3. TSRA-R action ablation
4. Adaptive Memory

이 순서가 현재 프로젝트의 진행 방향이다.

### 11. DecisionTrace 요약기를 추가한 이유

Agent Runtime을 추가하면서 AURA와 TSRA-R은 각 판단 주기마다 `DecisionTrace`를 남긴다. 하지만 JSONL 원본은 상세해서 사람이 바로 흐름을 읽기 어렵다. 따라서 P0 작업으로 trace 요약기를 추가했다.

구현:

```text
src/experiments/trace_summary.py
```

입력:

```text
outputs/experiments/*/aura_decision_traces.jsonl
outputs/experiments/*/tsra_r_decision_traces.jsonl
```

출력:

```text
outputs/report_tables/agent_decision_trace_summary.csv
outputs/report_tables/agent_decision_trace_summary.md
```

요약 필드:

- experiment
- time_sec
- agent
- policy
- selected_action
- score
- probability
- top_candidate
- top_candidate_signal
- reason
- tool_calls

검증:

```text
python3 -m compileall src
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
```

결과:

```text
agent_decision_trace_summary.csv: 215 rows
experiments: E3_rule_aura, E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
```

이 변경으로 AURA가 왜 특정 공격 효과를 골랐는지, TSRA-R이 왜 특정 방어 액션 또는 no-op을 선택했는지 같은 시간축에서 확인할 수 있다.

### 12. AURA COA Card를 추가한 이유

DecisionTrace 요약기는 시간축 판단을 보여준다. 하지만 AURA가 실제로 선택한 각 공격 효과를 한 장 단위로 설명하기에는 부족했다. 그래서 P1 작업으로 AURA COA Card 생성기를 추가했다.

구현:

```text
src/experiments/aura_coa_cards.py
```

입력:

```text
outputs/experiments/*/attack_events.jsonl
outputs/experiments/*/aura_decision_traces.jsonl
```

출력:

```text
outputs/report_tables/aura_coa_cards.csv
outputs/report_tables/aura_coa_cards.md
```

각 COA card에 포함한 항목:

- experiment
- event_id
- selected_at
- mission_phase
- attack_type
- target_link
- target_traffic_classes
- simulated_effects
- expected mission impact
- detectability score
- attack score
- candidate rank
- runner-up candidate
- selection reason
- safety boundary

검증:

```text
python3 -m compileall src
python3 -m src.experiments.run_all
python3 -m src.experiments.aura_coa_cards
```

결과:

```text
aura_coa_cards.csv: 15 cards
experiments: E3_rule_aura, E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
agents: AURA, AURA-ML
missing_safety: 0
unknown_rank: 0
```

모든 카드에는 실제 공격 명령이 아니라 폐쇄형 시뮬레이션 효과임을 명시했다.

### 13. TSRA-R Action Ablation을 추가한 이유

TSRA-R은 `priority_reroute`, `video_throttle`, `stale_badge`, `pace_switch`를 함께 실행한다. 전체 결과만 보면 어떤 액션이 어떤 지표에 기여했는지 분리하기 어렵다.

그래서 full TSRA-R에서 방어 액션을 하나씩 제거하는 ablation을 추가했다.

구현:

```text
src/experiments/run_tsra_ablation.py
```

Rule TSRA-R 변경:

```text
RuleTSRAR(mode="full", enabled_actions={...})
```

기본값은 모든 액션 enabled이므로 기존 E1~E7 기본 동작은 유지된다. ablation runner에서만 특정 액션을 제거한다.

실험 조건:

```text
full
no_priority_reroute
no_video_throttle
no_stale_badge
no_pace_switch
```

산출물:

```text
outputs/batch/tsra_action_ablation_raw.csv
outputs/batch/tsra_action_ablation_summary.csv
outputs/figures/tsra_action_ablation.png
```

검증:

```text
python3 -m compileall src
python3 -m src.experiments.run_all
python3 -m src.experiments.run_tsra_ablation
```

결과:

```text
full impact:             0.124
no_priority_reroute:     0.332  delta +0.208
no_stale_badge:          0.329  delta +0.205
no_video_throttle:       0.111  delta -0.013
no_pace_switch:          0.107  delta -0.017
```

해석:

- `priority_reroute`는 priority inversion과 critical latency 억제의 핵심이다.
- `stale_badge`는 trusted stale exposure 억제의 핵심이다.
- `video_throttle`, `pace_switch`는 현재 scalar mission impact에서는 항상 이득으로 나타나지 않는다. 이 둘은 운용형 방어 기능으로 분리해 다루고, 이후 정책 조건을 더 정교화해야 한다.

### 14. Adaptive Memory를 추가한 이유

Agent Runtime을 추가한 뒤에도 Memory가 단순 기록에 머무르면, 에이전트 구조의 설득력이 약하다. 그래서 TSRA-R에 별도 adaptive mode를 추가해 최근 관측 memory가 다음 방어 액션 선택에 직접 영향을 주게 했다.

구현:

```text
src/tsra_r/adaptive_defender.py
src/experiments/run_adaptive_memory.py
```

설계 판단:

- 기본 E1~E7은 그대로 유지한다.
- `AdaptiveTSRAR`는 별도 class로 두어 실험에서만 켠다.
- `priority_reroute`와 `stale_badge`는 ablation에서 핵심 액션으로 확인됐으므로 항상 유지한다.
- `video_throttle`은 최근 memory에 critical/video pressure가 반복될 때만 켠다.
- `pace_switch`는 SATCOM 저하와 심한 queue pressure가 같이 반복될 때만 켠다.
- 각 판단의 `feedback.adaptive_policy`에 memory count, enabled actions, reasons를 남긴다.

검증:

```text
python3 -m compileall src
python3 -m src.experiments.run_all
python3 -m src.experiments.run_adaptive_memory
```

결과:

```text
full TSRA-R mission impact:      0.123928
adaptive TSRA-R mission impact:  0.109489
delta mission impact:           -0.014439
trusted stale exposure:         0.129167 -> 0.125000
priority inversion:             0.047238 -> 0.027455
video throttle count:           6.4 -> 3.1
pace switch count:              1.0 -> 1.0
adaptive trace feedback rows:   61
```

해석:

- AdaptiveTSRA-R은 방어 액션을 많이 내보내는 방식이 아니라, memory에 반복 증거가 쌓인 경우에만 optional action을 켠다.
- 결과적으로 video throttle은 줄었고, mission impact와 priority inversion도 함께 내려갔다.
- 이 변경은 기본 baseline을 바꾸지 않으므로, 별도 adaptive defense 개선 실험으로 해석한다.

### 15. 제출 패키지 생성기를 추가한 이유

전체 작업 디렉터리를 그대로 압축하면 재생성 가능한 임시 로그, synthetic dataset, model binary가 섞인다. 이는 제출 ZIP을 불필요하게 무겁게 만들고, 심사자가 봐야 할 핵심 산출물을 흐린다.

그래서 제출용 패키지를 명시적으로 생성하는 스크립트를 추가했다.

구현:

```text
scripts/build_submission_package.py
docs/process/SUBMISSION_PACKAGE.md
outputs/package/submission_manifest.md
```

포함 기준:

- `README.md`, `requirements*.txt`
- `src/`: 에이전트, 시뮬레이터, ML, 실험 코드
- `docs/`: 시나리오, 에이전트 구조, 개발 판단 근거
- `outputs/batch/*.csv`
- `outputs/figures/*.png`
- `outputs/report_tables/*`
- `outputs/models/*_metrics.json`

제외 기준:

- `.git/`, `.venv*`, `__pycache__/`, `*.pyc`
- `outputs/tmp*`
- `outputs/batch/seed_*`
- `outputs/datasets/`
- `outputs/models/*.pkl`, `outputs/models/*.pt`

검증:

```text
python3 -m compileall src scripts
python3 scripts/build_submission_package.py
```

결과:

```text
payload_file_count: 100
zip_file_count: 101
zip_bytes: about 1.5MB
excluded __pycache__: 0
excluded outputs/tmp*: 0
excluded outputs/datasets/: 0
excluded *.pkl/*.pt: 0
excluded outputs/batch/seed_*: 0
```

해석:

- ZIP은 코드와 핵심 산출물을 포함하지만 재생성 가능한 대용량 파일은 제외한다.
- `outputs/package/submission_manifest.md`가 ZIP 구성과 SHA-256 확인 기준이 된다.
- ZIP 파일 자체는 로컬 생성 산출물이며 Git에는 올리지 않는다.

### 16. 공방 Timeline 패키지를 추가한 이유

기존 산출물은 각각 역할이 달랐다.

- `agent_decision_trace_summary`: 에이전트 판단 로그 요약
- `aura_coa_cards`: AURA가 선택한 공격 효과 카드
- `E5_rule_aura_tsra_r_event_timeline`: 단순 공격/방어 이벤트 순서

하지만 공격 이벤트, 방어 이벤트, 판단 이유, mission metric이 한 시간축에 붙어 있지 않아 공방 흐름을 한 번에 설명하기 어려웠다. 그래서 E5와 E7 중심의 battle timeline을 추가했다.

구현:

```text
src/experiments/battle_timeline.py
outputs/report_tables/battle_timeline.csv
outputs/report_tables/battle_timeline.md
```

포함 필드:

- experiment
- time_sec
- AURA attack event
- TSRA-R defense event
- AURA DecisionTrace reason
- TSRA-R DecisionTrace reason
- mission impact
- trusted stale exposure
- priority inversion rate
- critical/video/total queue signal
- safety boundary

검증:

```text
python3 -m compileall src
python3 -m src.experiments.battle_timeline
```

결과:

```text
battle_timeline.csv: 46 rows
experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
E5 rows: 24, attack rows: 5, defense rows: 19
E7 rows: 22, attack rows: 5, defense rows: 19
```

해석:

- E5는 rule AURA와 rule TSRA-R의 공방을 보여준다.
- E7은 ML AURA와 ML TSRA-R의 탐지 기반 reactive defense 공방을 보여준다.
- 각 row는 실제 공격 명령이 아니라 폐쇄형 시뮬레이션 event라는 safety boundary를 가진다.

### 17. 최종 재현 QA를 추가한 이유

최종 제출 직전에는 "파일이 있다"가 아니라 "README 재현 명령이 실제로 끝까지 실행되고, 제출 패키지가 요구 기준을 만족한다"는 증거가 필요하다. 그래서 제출 상태 검증 스크립트를 추가했다.

구현:

```text
scripts/verify_submission_state.py
docs/process/FINAL_QA.md
```

검증 범위:

- 필수 파일 존재 여부
- 핵심 CSV row count
- AURA COA와 battle timeline의 safety boundary
- 제출 ZIP 포함 파일
- 제출 ZIP 제외 규칙
- `hbin` 브랜치와 `origin/main`, `origin/hbin` 존재 여부

실행:

```text
python3 -m src.ml.build_dataset --rows 3000
python3 -m src.ml.train_aura_impact_model
python3 -m src.ml.train_tsra_detector --rows 5000
python3 -m src.experiments.run_all
python3 -m src.experiments.trace_summary
python3 -m src.experiments.battle_timeline
python3 -m src.experiments.aura_coa_cards
python3 -m src.experiments.run_tsra_ablation
python3 -m src.experiments.run_adaptive_memory
python3 -m src.experiments.run_batch
python3 scripts/build_submission_package.py
python3 scripts/verify_submission_state.py
```

결과:

```text
Full Reproduction: passed
experiment_summary rows: 7
repeated_experiment_summary rows: 7
resilience_gain_summary rows: 4
agent_decision_trace_summary rows: 215
aura_coa_cards rows: 15
battle_timeline rows: 46
package exclusions: passed
branch: hbin
origin main/hbin refs: present
```

해석:

- 현재 산출물은 README 기준으로 재현 가능하다.
- ZIP에는 코드, 문서, 요약 CSV, figure, report table, model metric JSON이 들어간다.
- ZIP에는 실제 공격 도구, RF 운용 파라미터, exploit, live network action이 들어가지 않는다.

### 18. Incident Summary를 추가한 이유

Battle Timeline은 상세하지만 한 행에 담긴 정보가 많다. 운영자 관점에서는 "공격 하나가 발생했고, 방어자가 어떻게 대응했고, metric이 어떻게 움직였는가"를 incident 단위로 보는 산출물이 필요하다.

그래서 attack event를 기준으로 timeline window를 묶는 incident summary 생성기를 추가했다.

구현:

```text
src/experiments/incident_summary.py
outputs/report_tables/incident_summary.csv
outputs/report_tables/incident_summary.md
```

요약 기준:

- AURA attack event를 incident 시작점으로 둔다.
- 다음 attack event 전까지의 TSRA-R defense event를 같은 incident window로 묶는다.
- mission impact, critical latency, trusted stale exposure, priority inversion의 peak/end 값을 계산한다.
- 잔여 위험과 결과를 incident 단위로 표시한다.
- 모든 행에 closed simulation safety boundary를 남긴다.

검증:

```text
python3 -m compileall src
python3 -m src.experiments.incident_summary
```

결과:

```text
incident_summary.csv: 10 rows
E5 incidents: 5
E7 incidents: 5
safety boundary missing: 0
```

해석:

- E5는 rule AURA/rule TSRA-R 공방 incident를 5개로 요약한다.
- E7은 ML AURA/ML TSRA-R 공방 incident를 5개로 요약한다.
- 이 산출물은 상세 timeline보다 상위 관점에서 공격-방어 결과를 설명하는 데 쓰인다.

### 19. Competition Alignment Matrix를 추가한 이유

대회의 핵심은 공격, 방어, AI 에이전트, 안전 경계, 실행 증거가 하나의 방향으로 맞물리는 것이다. 현재 프로젝트에는 코드와 산출물이 충분히 쌓였지만, 팀원이 추가되거나 제출 직전 수정이 들어오면 어떤 파일이 어떤 대회 목표를 증명하는지 흐려질 수 있다.

그래서 대회 목표와 구현 증거를 직접 연결하는 alignment matrix 생성기를 추가했다.

구현:

```text
src/experiments/competition_alignment.py
outputs/report_tables/competition_alignment_matrix.csv
outputs/report_tables/competition_alignment_matrix.md
```

정렬 항목:

```text
Defense mission grounding
Attack scenario
Defense architecture
AI agent architecture
Attack-defense cooperation
ML contribution
Repeatable evidence
Adaptive defense
Safety boundary
Team handoff and reproducibility
```

검증 방식:

- evidence file 존재 여부를 확인한다.
- 핵심 CSV row count를 확인한다.
- COA, battle timeline, incident summary의 safety boundary 문구를 확인한다.
- 모든 alignment row가 `verified`가 아니면 `--fail-on-incomplete` 실행에서 실패한다.

검증:

```text
python3 -m src.experiments.competition_alignment --fail-on-incomplete
```

결과:

```text
competition_alignment_matrix.csv: 10 rows
evidence_status: all verified
```

해석:

- 이후 새 기능은 alignment matrix의 next gate 중 하나 이상을 만족해야 한다.
- 이 변경은 기능 추가 자체보다 개발 방향 이탈을 막는 자동 점검 장치다.
- README, package builder, final verifier에도 연결해 제출 산출물에서 빠지지 않게 했다.

### 20. Agent Event Contract Validation을 추가한 이유

AURA와 TSRA-R은 별도 에이전트로 개발하지만, 실제 실행에서는 같은 MissionSimulator와 JSONL 로그를 공유한다. 따라서 공격 에이전트가 `attack_events.jsonl` 형식을 바꾸거나 방어 에이전트가 `defense_events.jsonl` 필드를 바꾸면, timeline, incident summary, trace summary가 연쇄적으로 깨질 수 있다.

이 문제를 막기 위해 event contract validation을 추가했다.

구현:

```text
src/experiments/validate_event_contracts.py
outputs/report_tables/agent_contract_validation.csv
outputs/report_tables/agent_contract_validation.md
```

검증 범위:

- `attack_events.jsonl`: event id, selected time, candidate, expected impact, agent
- `defense_events.jsonl`: event id, time, action, details, agent
- `mission_events.jsonl`: message lifecycle 필드
- `metric_snapshots.jsonl`: mission impact 관련 지표
- `aura_decision_traces.jsonl`: AURA AgentRuntime trace
- `tsra_r_decision_traces.jsonl`: TSRA-R AgentRuntime trace
- cross-contract: attack event와 AURA trace, defense event와 TSRA-R trace, metric time coverage 연결

검증:

```text
python3 -m src.experiments.validate_event_contracts --fail-on-error
```

결과:

```text
agent_contract_validation.csv: 49 contract checks
status: all pass
```

해석:

- 이 검증기는 새 공격/방어 로직을 추가하지 않는다.
- 대신 두 에이전트가 분리 개발돼도 공유 인터페이스가 깨지지 않게 한다.
- `verify_submission_state.py`와 `competition_alignment.py`에 연결해 최종 산출물의 필수 게이트로 만들었다.

## 최신 핵심 결과

30-seed 반복 실험:

```text
E1 Baseline:              impact 0.458 +- 0.014
E2 Fixed Attack:          impact 0.695 +- 0.077
E3 AURA Attack:           impact 0.914 +- 0.056
E5 AURA + TSRA-R Defense: impact 0.124 +- 0.019
E7 ML AURA + ML TSRA-R Defense: impact 0.135 +- 0.013
```

Resilience Gain:

```text
TSRA-R: 약 86.4% +- 2.0%
ML AURA + TSRA-R: 약 86.9% +- 1.6%
ML AURA + ML TSRA-R: 약 85.2% +- 1.8%
```

## 2026-07-09 검증 반영

### E6/E7 동일 문제

검증 중 E6와 E7이 완전히 동일한 문제가 발견됐다. 원인은 `MLTSRAR`가 내부에서 `RuleTSRAR(mode="full")`을 항상 먼저 실행하고, ML detector는 이미 방어 액션이 나간 뒤 보조 액션만 추가하는 구조였기 때문이다.

수정:

- `MLTSRAR`를 reactive defense로 변경했다.
- detector probability가 threshold 이상일 때만 defense window를 연다.
- defense window 안에서만 full TSRA-R rule actions를 실행한다.
- `ml_attack_alert` 이벤트를 남겨 ML 판단이 실제 폐루프에 개입했음을 로그로 확인 가능하게 했다.

결과:

```text
E6 ML AURA + TSRA-R:     impact 0.120 +- 0.016
E7 ML AURA + ML TSRA-R:  impact 0.135 +- 0.013
```

E7은 E6보다 약간 높은 impact를 보이지만, 이는 항상 방어하는 E6와 달리 ML detector가 공격성 저하를 탐지한 구간에서만 방어를 여는 설계 때문이다. 따라서 E7은 "최소 impact"가 아니라 "탐지 기반 reactive defense"의 근거로 사용한다.

## 다음 개발 기준

1. 공격 에이전트 AURA를 먼저 완성도 있게 다듬는다.
2. 그 다음 방어 에이전트 TSRA-R을 같은 수준으로 다듬는다.
3. 각 단계마다 설계 문서와 결과 요약을 커밋한다.
4. `hbin` 브랜치에만 push한다.
