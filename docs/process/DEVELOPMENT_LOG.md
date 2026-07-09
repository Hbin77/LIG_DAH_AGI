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
full impact:             0.157
no_priority_reroute:     0.343  delta +0.185
no_stale_badge:          0.363  delta +0.206
no_video_throttle:       0.141  delta -0.017
no_pace_switch:          0.107  delta -0.051
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
full TSRA-R mission impact:      0.157423
adaptive TSRA-R mission impact:  0.109489
delta mission impact:           -0.047934
trusted stale exposure:         0.127083 -> 0.125000
priority inversion:             0.050609 -> 0.027455
video throttle count:           6.4 -> 3.1
pace switch count:              3.0 -> 1.0
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
battle_timeline rows: 49
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

### 21. DecisionTrace Quality Audit을 추가한 이유

Event contract validation은 로그 필드가 맞는지 확인한다. 하지만 AI 에이전트 아키텍처 관점에서는 "로그가 있다"만으로 충분하지 않다. 각 에이전트가 관측, 메모리, 도구 호출, 후보 평가, 선택 행동, 이유를 실제로 남기고 있는지 확인해야 한다.

그래서 DecisionTrace 품질 감사기를 추가했다.

구현:

```text
src/experiments/trace_quality_audit.py
outputs/report_tables/decision_trace_quality_audit.csv
outputs/report_tables/decision_trace_quality_audit.md
```

감사 기준:

- reason coverage
- observation coverage
- memory coverage
- feedback coverage
- selected_action coverage
- tool_call coverage
- candidate_action coverage
- non-no-op selected action count
- selected attack/defense event count

AURA와 TSRA-R은 운영 방식이 다르므로 기준을 분리했다.

- AURA: 대기 구간은 no-op이고, 공격 시점에 candidate/tool evidence가 있어야 한다.
- TSRA-R: 매 판단마다 defense condition tool과 candidate action evidence가 있어야 한다.

검증:

```text
python3 -m src.experiments.trace_quality_audit --fail-on-error
```

결과:

```text
decision_trace_quality_audit.csv: 9 audit rows
status: all pass
AURA/AURA-ML selected events: 5 per active experiment
TSRA-R/TSRA-R-ML tool_call_coverage: 1.0
```

해석:

- 이 산출물은 "에이전트"라는 주장을 말이 아니라 trace 품질로 검증한다.
- 이후 공격/방어 정책을 수정해도 DecisionTrace 품질이 낮아지면 final verifier에서 실패한다.

### 22. Agent Loop Replay를 추가한 이유

DecisionTrace summary와 quality audit은 유용하지만, 한 판단 주기의 흐름을 그대로 읽기에는 여전히 표가 넓다. 에이전트 구조를 이해하려면 한 row에서 관측, 메모리, 도구, 후보, 선택 행동, 피드백, 이유가 연결돼야 한다.

그래서 representative loop replay를 추가했다.

구현:

```text
src/experiments/agent_loop_replay.py
outputs/report_tables/agent_loop_replay.csv
outputs/report_tables/agent_loop_replay.md
```

Replay 구성:

```text
observe -> memory -> tools -> candidates -> selected_action -> feedback -> reason
```

선정 방식:

- E5 rule 공방과 E7 ML 공방을 기본 대상으로 둔다.
- AURA, AURA-ML, TSRA-R, TSRA-R-ML 각각에서 `no_op` trace 1개와 실제 action trace 1개를 뽑는다.
- 총 8개 replay row를 생성한다.

검증:

```text
python3 -m src.experiments.agent_loop_replay
```

결과:

```text
agent_loop_replay.csv: 8 rows
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
cases: no_op, action
missing fields: 0
```

해석:

- 이 산출물은 에이전트가 무조건 행동하는 것이 아니라, no-op과 action을 조건부로 선택한다는 점을 보여준다.
- AURA의 공격 후보 평가와 TSRA-R의 방어 후보 평가를 같은 형식으로 비교할 수 있다.
- `verify_submission_state.py`와 `competition_alignment.py`에 연결해 필수 산출물로 만들었다.

### 23. Metric Gate Summary를 추가한 이유

지금까지의 검증은 파일 존재, 로그 계약, trace 품질, replay를 확인했다. 하지만 실험 숫자가 프로젝트 방향을 실제로 지지하는지도 자동 확인해야 한다. 예를 들어 AURA impact가 약해지거나, TSRA-R resilience가 낮아지거나, E6/E7이 다시 동일해지는 문제가 생기면 row count 검증만으로는 잡기 어렵다.

그래서 metric gate summary를 추가했다.

구현:

```text
src/experiments/metric_gate.py
outputs/report_tables/metric_gate_summary.csv
outputs/report_tables/metric_gate_summary.md
```

Gate 범위:

- AURA attack effectiveness
- AURA adaptive selection
- TSRA-R resilience
- TSRA-R impact containment
- trusted stale protection
- priority reroute ablation
- stale badge ablation
- adaptive memory improvement
- adaptive memory action economy
- ML defender separation
- repeated-run stability

검증:

```text
python3 -m src.experiments.metric_gate --fail-on-error
```

결과:

```text
metric_gate_summary.csv: 11 gates
status: all pass
E3-E1 impact delta: 0.456259
E5 resilience gain: 0.826993
E5/E3 impact ratio: 0.172152
E6/E7 impact separation: 0.0162307
```

해석:

- 이 산출물은 공방 효과가 숫자로 유지되는지 확인하는 품질 게이트다.
- 이후 정책이나 실험을 바꿔 핵심 결과가 약해지면 최종 검증에서 실패한다.

### 24. Agent Interface Manifest를 추가한 이유

공격 에이전트와 방어 에이전트를 따로 개발하려면, 각 agent가 어떤 입력을 보고 어떤 메모리와 도구를 사용하며 어떤 이벤트를 출력하는지 명확해야 한다. trace와 replay는 실행 사례를 보여주지만, 팀 협업 관점에서는 agent별 인터페이스 기준표가 필요하다.

그래서 observed trace를 기반으로 Agent Interface Manifest를 추가했다.

구현:

```text
src/experiments/agent_interface_manifest.py
outputs/report_tables/agent_interface_manifest.csv
outputs/report_tables/agent_interface_manifest.md
```

Manifest 필드:

- agent
- side: attack 또는 defense
- goal
- policies
- input contract
- memory contract
- tool contract
- candidate contract
- selected action contract
- event outputs
- evidence experiments
- trace count
- non-no-op count
- safety boundary

검증:

```text
python3 -m src.experiments.agent_interface_manifest
```

결과:

```text
agent_interface_manifest.csv: 4 agents
AURA / AURA-ML: attack side
TSRA-R / TSRA-R-ML: defense side
tool contract present: yes
non-no-op decisions: present for all agents
```

해석:

- 이 산출물은 AURA와 TSRA-R을 따로 고도화할 때 깨지면 안 되는 인터페이스 기준이다.
- `verify_submission_state.py`와 `competition_alignment.py`에 연결해 필수 산출물로 만들었다.

### 25. Agent Capability Matrix를 추가한 이유

Agent Interface Manifest는 각 agent의 입력/도구/출력 계약을 보여준다. 하지만 실제 개발을 나누려면 "각 agent가 어떤 capability를 가지고 있고, 그 capability가 어떤 실험 증거와 연결되는지"가 필요하다.

그래서 AURA 공격 효과와 TSRA-R 방어 액션을 같은 형식으로 정리하는 capability matrix를 추가했다.

구현:

```text
src/experiments/agent_capability_matrix.py
outputs/report_tables/agent_capability_matrix.csv
outputs/report_tables/agent_capability_matrix.md
```

집계 기준:

- AURA COA cards: 선택된 attack capability와 예상 impact
- E5/E7 defense events: 실제 방어 action 사용 횟수
- TSRA-R action ablation: action 제거 시 metric 변화
- adaptive memory summary: adaptive gating 효과
- metric gate summary: capability별 validation gate

검증:

```text
python3 -m src.experiments.agent_capability_matrix
```

결과:

```text
agent_capability_matrix.csv: 10 capabilities
attack side: bandwidth_limit, failover_chasing, queue_pressure, stale_cop_induction
defense side: ml_attack_alert, pace_switch, priority_reroute, stale_badge,
              video_throttle, adaptive_optional_action_gating
```

해석:

- 이 산출물은 공격/방어 에이전트를 capability 단위로 분리 개발하기 위한 기준표다.
- `priority_reroute`, `stale_badge`, `ml_attack_alert`, adaptive gating 같은 핵심 capability가 어떤 evidence와 gate를 갖는지 바로 확인할 수 있다.
- final verifier와 competition alignment에 연결해 필수 산출물로 만들었다.

### 27. Attack-Defense Coverage를 추가한 이유

Agent Capability Matrix는 공격 capability와 방어 capability를 같은 표에 놓지만, 각 공격이 어떤 방어 capability 조합으로 커버되는지는 별도로 해석해야 했다.

사용자가 요구한 방향은 공격 에이전트와 방어 에이전트를 따로 만들되, 둘이 끊어지지 않게 실제 공방 구조로 올리는 것이다. 그래서 공격 capability별 방어 coverage를 별도 산출물로 추가했다.

구현:

```text
src/experiments/attack_defense_coverage.py
outputs/report_tables/attack_defense_coverage.csv
outputs/report_tables/attack_defense_coverage.md
```

매핑 기준:

```text
bandwidth_limit      -> priority_reroute, video_throttle, pace_switch
failover_chasing     -> ml_attack_alert, pace_switch, adaptive_optional_action_gating
queue_pressure       -> priority_reroute, video_throttle, stale_badge
stale_cop_induction  -> stale_badge
```

검증:

```text
python3 -m src.experiments.attack_defense_coverage
```

결과:

```text
attack_defense_coverage.csv: 4 rows
coverage_status: all covered
validation_gates: all pass
```

해석:

- 이 산출물은 공격 담당과 방어 담당이 각각 개발해도 capability 단위 연결성을 유지하게 한다.
- 새 공격 capability는 반드시 대응 방어 capability, validation gate, residual risk와 함께 추가해야 한다.
- `verify_submission_state.py`와 `competition_alignment.py`에 연결해 최종 산출물의 필수 게이트로 만들었다.

### 28. Attack-Defense Response Audit를 추가한 이유

Attack-Defense Coverage는 공격 capability와 방어 capability의 정적 연결을 보여준다. 하지만 실제 공방 루프에서는 방어가 공격 시점에 이미 active인지, 아니면 공격 뒤 response window 안에 나왔는지가 중요하다.

그래서 E5/E7 실제 event log를 읽는 response audit를 추가했다.

구현:

```text
src/experiments/attack_defense_response_audit.py
outputs/report_tables/attack_defense_response_audit.csv
outputs/report_tables/attack_defense_response_audit.md
```

감사 기준:

```text
active defense:
  defense_event.time_sec <= attack_time <= defense_event.details.until_sec

timely response:
  attack_time < defense_event.time_sec <= attack_time + 40 sec
```

결과:

```text
audited attack events: 10
missed required defenses: 0
support partial residual risk: 0
```

해석:

- E5/E7의 모든 공격 이벤트는 required defense를 active 또는 timely response로 받았다.
- E7 `failover_chasing`도 `ml_attack_alert`와 PACE support를 모두 받는다.
- support partial row가 생기면 실패로 숨기지 않고 residual risk로 기록한다.
- `verify_submission_state.py`와 `competition_alignment.py`에 연결해 required response가 누락되면 최종 검증에서 실패하게 만들었다.

### 29. Fallback PACE 재선택을 추가한 이유

Response Audit에서 late `failover_chasing` 구간의 PACE support가 partial로 남을 수 있음을 확인했다. 원인은 기존 `RuleTSRAR`가 SATCOM이 나빠질 때만 `pace_switch`를 고려하고, 이미 LTE/MESH 같은 fallback link로 넘어간 뒤에는 fallback 자체가 공격받아도 다시 PACE 링크를 고르지 않는 구조였기 때문이다.

수정:

```text
src/tsra_r/rule_defender.py
```

변경 내용:

- active link가 SATCOM이 아니어도 fallback link가 latency/loss/queue 기준을 넘으면 `pace_switch_needed`가 켜진다.
- fallback 후보 선택 시 현재 active link를 제외한다.
- 방어 이벤트 reason을 `fallback link degraded beyond mission threshold`로 남긴다.

검증 결과:

```text
attack_defense_response_audit.csv: 10 rows
missed required defenses: 0
required_covered_support_partial: 0
metric gates: 11 pass
```

tradeoff:

- fallback 재선택으로 late failover 대응성은 좋아졌다.
- 대신 PACE 전환 횟수가 늘어 scalar Mission Impact의 recovery instability 성분은 증가했다.
- 그래도 E5 resilience 0.827, E5/E3 impact ratio 0.172로 metric gate는 통과한다.

### 30. PACE 조건을 SATCOM/fallback으로 분리한 이유

Fallback PACE 재선택을 추가한 뒤, `pace_switch_needed` 조건을 다시 확인했다. 최초 구현은 active link 공통 조건과 fallback 조건을 함께 사용했기 때문에, fallback link에서도 `total_queue_kb > 4500` 같은 SATCOM용 기준이 먼저 걸릴 수 있었다.

수정:

```text
src/tsra_r/rule_defender.py
```

변경 내용:

- `satcom_link_bad`: active link가 SATCOM일 때만 SATCOM 저하 기준을 적용한다.
- `fallback_link_bad`: active link가 SATCOM이 아닐 때만 fallback 저하 기준을 적용한다.
- `pace_switch_needed = satcom_link_bad or fallback_link_bad`로 명시했다.

검증 결과:

```text
run_all: passed
attack_defense_response_audit.csv: 10 rows, all complete
metric gates: 11 pass
30-seed core metrics: unchanged from fallback PACE response run
```

해석:

- 이 변경은 수치 개선보다 방어 정책의 의미적 정확도를 높이는 수정이다.
- SATCOM과 fallback link의 임계값을 분리했기 때문에 이후 PACE tuning을 더 안전하게 할 수 있다.

### 31. PACE Transition Audit를 추가한 이유

Fallback PACE 재선택은 response audit에서 required/support coverage를 완성했지만, 전환 횟수가 늘면서 recovery instability 성분도 커졌다. 따라서 단순히 "PACE가 늘었다"가 아니라 각 전환이 어떤 공격 context에서 발생했는지 설명할 별도 산출물이 필요했다.

구현:

```text
src/experiments/pace_transition_audit.py
outputs/report_tables/pace_transition_audit.csv
outputs/report_tables/pace_transition_audit.md
```

감사 기준:

```text
E5/E7 pace_switch event
-> inferred from_link
-> target_link
-> active attack at switch
-> near future attack within 40 sec
-> metric snapshot at switch
-> audit_status
```

검증 결과:

```text
pace_transition_audit.csv: 6 rows
satcom_to_fallback: 2
fallback_reselect: 4
self_transition: 0
```

해석:

- 초기 `SATCOM -> LTE` 전환은 SATCOM 저하 대응이다.
- 이후 `LTE -> MESH`, `MESH -> LTE` 전환은 fallback link가 공격받는 상황의 재선택이다.
- recovery instability tradeoff를 숨기지 않고 각 row에 남긴다.
- `verify_submission_state.py`와 `competition_alignment.py`에 연결해 PACE 전환 근거가 빠지면 최종 검증에서 실패하게 만들었다.

### 32. Mission Impact Decomposition을 추가한 이유

`Mission Impact`는 최종 판단에는 유용하지만 하나의 숫자라서, 어느 성분이 공격/방어 결과를 만들었는지 바로 보이지 않는다.

특히 TSRA-R은 raw stale COP 객체를 즉시 없애는 것이 아니라, stale badge로 지휘소가 오래된 정보를 최신으로 믿는 위험을 줄인다. 따라서 분해 시 raw `stale_data_ratio`가 아니라 `trusted_stale_exposure`를 사용해야 실제 방어 효과와 맞는다.

구현:

```text
src/experiments/mission_impact_decomposition.py
outputs/report_tables/mission_impact_decomposition.csv
outputs/report_tables/mission_impact_decomposition.md
```

분해 성분:

```text
critical_latency
trusted_stale_exposure
priority_inversion
kill_chain_delay
recovery_instability
```

검증 결과:

```text
mission_impact_decomposition.csv: 35 rows
experiments: 7
components: 5
```

해석:

- E3 공격 단독은 critical latency, trusted stale exposure, priority inversion, kill-chain delay가 모두 큰 상태다.
- E5/E7은 priority inversion과 trusted stale exposure를 낮추지만, PACE 전환 비용이 recovery instability로 남는다.
- 이 표는 TSRA-R이 왜 raw stale 제거기가 아니라 COP 신뢰 위험 완화와 critical traffic 보호 에이전트인지 설명한다.

### 33. Operator Alerts를 추가한 이유

`defense_events.jsonl`은 TSRA-R이 어떤 action을 냈는지 기록하지만, 사람이 바로 이해하는 운영 알림 형태는 아니다. 방어 에이전트가 실제로 유용해 보이려면 action, metric, attack context, trace reason을 묶어 "왜 이 조치가 필요한지"를 설명해야 한다.

구현:

```text
src/experiments/operator_alerts.py
outputs/report_tables/operator_alerts.csv
outputs/report_tables/operator_alerts.md
```

변환 기준:

```text
DefenseEvent
-> severity
-> operator_alert
-> mission_rationale
-> expected_operator_response
-> related_attack_context
-> metric snapshot
```

검증 결과:

```text
operator_alerts.csv: 56 rows
E5 alerts: 23
E7 alerts: 33
actions: ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
severity: high, medium
```

해석:

- `ml_attack_alert`는 ML detector가 reactive defense window를 여는 근거를 보여준다.
- `priority_reroute`는 critical traffic 보호 이유를 보여준다.
- `stale_badge`는 COP 객체를 최신으로 신뢰하지 말아야 하는 이유를 보여준다.
- `pace_switch`는 PACE fallback/reselect와 recovery churn 주의점을 보여준다.
- 모든 row는 폐쇄형 시뮬레이션 알림이며 실제 RF, exploit, live network action을 포함하지 않는다.

### 34. Agent Collaboration Graph를 추가한 이유

대회에서 AI 에이전트 아키텍처는 에이전트가 따로 존재한다는 설명만으로는 부족하다. AURA, MissionSimulator, TSRA-R, Operator Alerts, Metrics, Verifier가 어떤 산출물로 연결되는지 한눈에 보여줘야 한다.

그래서 기존 evidence를 읽어 협력 구조를 Mermaid graph와 CSV edge table로 재구성했다.

구현:

```text
src/experiments/agent_collaboration_graph.py
outputs/report_tables/agent_collaboration_graph.csv
outputs/report_tables/agent_collaboration_graph.md
outputs/report_tables/agent_collaboration_graph.mmd
```

edge 기준:

```text
AgentRuntime -> AURA/AURA-ML
AURA/AURA-ML -> MissionSimulator
MissionSimulator -> TSRA-R/TSRA-R-ML
TSRA-R/TSRA-R-ML -> MissionSimulator
MissionSimulator -> Mission Metrics
Mission Metrics -> AURA/AURA-ML
Mission Metrics -> TSRA-R/TSRA-R-ML
AURA Capabilities -> TSRA-R Capabilities
AttackEvent -> DefenseEvent
DefenseEvent -> Operator Alerts
Mission Metrics -> Verifier/Package
```

검증 결과:

```text
agent_collaboration_graph.csv: 11 edges
validation_status: all verified
Mermaid graph: outputs/report_tables/agent_collaboration_graph.mmd
```

해석:

- 이 산출물은 공격-방어-AI 협력 구조를 제출 산출물 안에서 바로 확인하게 한다.
- 새 기능은 이 협력 edge 중 하나 이상을 강화해야 한다.
- 특정 edge가 evidence count 또는 verification status를 잃으면 협력 구조가 약해진 것으로 본다.

### 35. Closed-Loop Episode Replay를 추가한 이유

공격-방어 루프를 이해하려면 attack event, response audit, operator alert, metric snapshot을 따로 읽어야 했다. 이 방식은 검증에는 충분하지만, 공격 1건이 어떻게 방어되고 어떤 metric 변화를 만들었는지 순차적으로 이해하기 어렵다.

그래서 attack event 1개를 episode 기준으로 잡고, 방어 coverage, defense chain, operator alert chain, mission impact movement를 한 row로 묶었다.

구현:

```text
src/experiments/closed_loop_episode_replay.py
outputs/report_tables/closed_loop_episode_replay.csv
outputs/report_tables/closed_loop_episode_replay.md
```

episode 구성:

```text
AttackEvent
-> response audit status
-> active/timely defense chain
-> operator alert chain
-> mission impact start/peak/end
-> outcome and residual risk
```

검증 결과:

```text
closed_loop_episode_replay.csv: 10 rows
E5 episodes: 5
E7 episodes: 5
response_status: complete for all rows
```

해석:

- 이 산출물은 사용자가 "순차적으로 이해"할 수 있게 만든 공방 episode 표다.
- E5/E7의 모든 공격 event가 complete response를 가진다.
- 일부 episode는 peak 이후 impact가 크게 내려가고, 일부는 residual mission impact가 남는다. 이 차이를 숨기지 않고 outcome으로 남긴다.
- 실제 공격이나 실제 운용 지시가 아니라 폐쇄형 시뮬레이션 replay다.

## 최신 핵심 결과

30-seed 반복 실험:

```text
E1 Baseline:              impact 0.458 +- 0.014
E2 Fixed Attack:          impact 0.695 +- 0.077
E3 AURA Attack:           impact 0.914 +- 0.056
E5 AURA + TSRA-R Defense: impact 0.157 +- 0.029
E7 ML AURA + ML TSRA-R Defense: impact 0.166 +- 0.012
```

Resilience Gain:

```text
TSRA-R: 약 82.7% +- 3.6%
ML AURA + TSRA-R: 약 83.6% +- 1.5%
ML AURA + ML TSRA-R: 약 81.8% +- 1.8%
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
E6 ML AURA + TSRA-R:     impact 0.149 +- 0.013
E7 ML AURA + ML TSRA-R:  impact 0.166 +- 0.012
```

E7은 E6보다 약간 높은 impact를 보이지만, 이는 항상 방어하는 E6와 달리 ML detector가 공격성 저하를 탐지한 구간에서만 방어를 여는 설계 때문이다. 따라서 E7은 "최소 impact"가 아니라 "탐지 기반 reactive defense"의 근거로 사용한다.

## 다음 개발 기준

1. 공격 에이전트 AURA를 먼저 완성도 있게 다듬는다.
2. 그 다음 방어 에이전트 TSRA-R을 같은 수준으로 다듬는다.
3. 각 단계마다 설계 문서와 결과 요약을 커밋한다.
4. `hbin` 브랜치에만 push한다.

### 36. Defense Effectiveness Ledger를 추가한 이유

TSRA-R은 `DefenseEvent`와 operator alert를 남기지만, 그것만으로는 방어 이벤트가 local mission metric에 어떤 효과를 냈는지 event 단위로 확인하기 어렵다. aggregate resilience gain은 전체 평균이고, closed-loop episode replay는 공격 1건 기준 흐름이다. 방어 에이전트 자체의 판단 품질을 보려면 방어 액션 1건마다 before/after 지표 변화가 필요하다.

추가한 것:

```text
src/experiments/defense_effectiveness_ledger.py
outputs/report_tables/defense_effectiveness_ledger.csv
outputs/report_tables/defense_effectiveness_ledger.md
```

처리 방식:

```text
DefenseEvent
-> operator_alerts.csv에서 alert/context join
-> metric_snapshots.jsonl에서 event time metric 추출
-> metric_snapshots.jsonl에서 30초 뒤 metric 추출
-> mission impact / critical latency / trusted stale exposure / priority inversion delta 계산
-> action별 observed_effect와 interpretation 기록
```

검증 결과:

```text
defense_effectiveness_ledger.csv: 56 rows
E5 rows: 23
E7 rows: 33
actions: ml_attack_alert, pace_switch, priority_reroute, stale_badge, video_throttle
observed_effect labels: improved, held, degraded_or_delayed
```

연결한 것:

- README 실행 명령
- Agent Runtime 문서
- TSRA-R 방어 에이전트 문서
- package builder required paths
- final verifier row/action/effect checks
- competition alignment matrix
- agent collaboration graph E13 edge

판단:

- 이 산출물은 TSRA-R 방어 이벤트가 단순 로그가 아니라 metric movement와 연결된 판단 결과임을 보여준다.
- `held`는 실패가 아니라 30초 local window에서 지표를 bounded 상태로 유지했다는 의미로 둔다.
- `degraded_or_delayed`는 공격 누적 또는 metric lag가 response window 안에 남은 경우로 숨기지 않고 기록한다.
- 실제 RF, exploit, live network action 없이 폐쇄형 시뮬레이션 효과만 분석한다.

### 37. Agent Memory/Belief Audit를 추가한 이유

사용자가 요구한 에이전트 구조는 단순 Python 함수가 아니라 `Agent Runtime`, `Memory`, `Tool`, `DecisionTrace`를 가진 구조다. Runtime, Tool, DecisionTrace는 기존 trace quality audit과 loop replay로 어느 정도 보이지만, `Memory`가 실제로 다음 판단에 이어지는 상태인지 별도 산출물로 확인하기 어려웠다.

추가한 것:

```text
src/experiments/agent_memory_belief_audit.py
outputs/report_tables/agent_memory_belief_audit.csv
outputs/report_tables/agent_memory_belief_audit.md
```

감사 방식:

```text
DecisionTrace
-> memory coverage 확인
-> observation_count / decision_count nondecreasing 확인
-> belief key와 changing belief key 추출
-> feedback key 추출
-> 이전 selected_action이 다음 memory.last_selected_action으로 이어지는지 확인
```

검증 결과:

```text
agent_memory_belief_audit.csv: 9 rows
status: pass=9
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
last_selected_chain_match_rate: 1.0 for all rows
```

해석:

- AURA memory는 attack cadence와 last attack context를 다음 후보 선택에 들고 간다.
- TSRA-R memory는 cooldown, enabled action, event count를 다음 방어 판단에 들고 간다.
- ML TSRA-R memory는 last anomaly probability와 active defense window를 reactive defense 판단에 들고 간다.
- 이 산출물은 `Memory`가 정적 JSON 필드가 아니라 closed-loop decision state라는 점을 검증한다.

연결한 것:

- README 실행 명령
- Agent Runtime 문서
- package builder required paths
- final verifier row/status/chain checks
- competition alignment matrix
- agent collaboration graph E14 edge

### 38. Agent Tool Usage Audit를 추가한 이유

사용자가 요구한 에이전트 구조는 `Agent Runtime`, `Memory`, `Tool`, `DecisionTrace`를 모두 갖춘 구조다. Memory audit로 상태 유지 증거는 보강했지만, Tool이 실제 판단 루프에서 호출된다는 증거도 별도 산출물로 분리할 필요가 있었다.

추가한 것:

```text
src/experiments/agent_tool_usage_audit.py
outputs/report_tables/agent_tool_usage_audit.csv
outputs/report_tables/agent_tool_usage_audit.md
```

감사 방식:

```text
DecisionTrace.tool_calls
-> agent / policy / tool_name 단위로 그룹화
-> invocation count 계산
-> trace coverage 계산
-> input_summary coverage 확인
-> output_summary coverage 확인
-> status / error count 확인
-> tool_role과 decision_link 기록
```

검증 결과:

```text
agent_tool_usage_audit.csv: 24 rows
status: pass=24
tools:
  assess_mission_risk_guard
  estimate_candidate_effect
  estimate_detectability
  evaluate_defense_conditions
  generate_attack_candidates
  predict_attack_probability
  predict_candidate_impact
  select_fallback_link
```

해석:

- AURA는 후보 생성, mission impact what-if, detectability penalty tool을 실제 호출한다.
- AURA-ML은 ML impact prediction tool을 추가로 호출한다.
- TSRA-R은 방어 조건 평가와 PACE fallback 선택 tool을 실제 호출한다.
- TSRA-R-ML은 anomaly probability prediction tool과 residual mission-risk guard tool을 실제 호출한다.
- 이 산출물은 `Tool`이 정적 코드 구조가 아니라 DecisionTrace 안에서 검증 가능한 실행 증거라는 점을 보여준다.

연결한 것:

- README 실행 명령
- Agent Runtime 문서
- package builder required paths
- final verifier row/status/tool/input-output coverage checks
- competition alignment matrix
- agent collaboration graph E15 edge

### 39. Agent Decision Causality Audit를 추가한 이유

DecisionTrace에는 observation, memory, tool_calls, candidate_actions, selected_action, feedback이 들어간다. 하지만 이 필드들이 모두 있다는 것과, selected_action이 실제 candidate/tool/score 근거에서 나온 것인지는 별개의 문제다. AI 에이전트 구조를 더 강하게 보이려면 "선택의 인과성"을 검증해야 한다.

추가한 것:

```text
src/experiments/agent_decision_causality_audit.py
outputs/report_tables/agent_decision_causality_audit.csv
outputs/report_tables/agent_decision_causality_audit.md
```

감사 방식:

```text
DecisionTrace
-> selected action 추출
-> candidate_actions와 매칭
-> required tool presence 확인
-> AURA score top-candidate support 확인
-> TSRA-R eligible/ready support 확인
-> TSRA-R-ML probability threshold/window support 확인
-> no-op 근거 확인
```

검증 결과:

```text
agent_decision_causality_audit.csv: 399 rows
causal_status: pass=399
candidate_support: pass=399
tool_support: pass=399
score_or_threshold_support: pass=399
```

해석:

- AURA의 selected attack event는 candidate score와 일치한다.
- TSRA-R의 selected defense event는 eligible/ready candidate와 일치한다.
- TSRA-R-ML의 reactive defense는 probability threshold와 active defense window 근거와 일치한다.
- no-op도 candidate 부재, threshold/window, 또는 event 미발생 근거로 설명된다.
- 이 산출물은 DecisionTrace가 단순 로그가 아니라 선택 근거를 검증할 수 있는 감사 trail이라는 점을 보여준다.

연결한 것:

- README 실행 명령
- Agent Runtime 문서
- package builder required paths
- final verifier row/status/support checks
- competition alignment matrix
- agent collaboration graph E16 edge

### 40. Submission Readiness Audit를 추가한 이유

에이전트 구조와 공방 evidence는 충분히 쌓였지만, 팀 인계와 제출 직전 상태는 별도 관점이다. 파일이 많아질수록 `main` 보존, `hbin` 공유, README 재현 명령, package 입력, safety boundary, 팀 인계 문서 중 하나가 빠져도 사람이 눈으로 놓치기 쉽다.

그래서 제출/협업 준비 상태를 별도 generated audit으로 만들었다.

추가한 것:

```text
src/experiments/submission_readiness_audit.py
outputs/report_tables/submission_readiness_audit.csv
outputs/report_tables/submission_readiness_audit.md
```

감사 방식:

```text
branch policy
-> origin/main, origin/hbin 존재와 README main push 금지 문구 확인
reproduction
-> README Full Reproduction 핵심 명령 확인
agent evidence
-> Runtime, Memory, Tool, DecisionTrace 산출물 row count 확인
attack-defense evidence
-> capability, coverage, response, closed-loop 산출물 확인
package evidence
-> package builder, verifier, manifest, ZIP ignore rule 확인
safety / handoff
-> closed simulation boundary와 팀 인계 문서 확인
```

검증 결과:

```text
submission_readiness_audit.csv: 10 rows
status: pass=10
agent_collaboration_graph.csv: 17 edges
competition_alignment_matrix.csv: 10 rows verified
package_zip entries: 162
branch: hbin
origin main/hbin refs: present
```

해석:

- 이 산출물은 팀원이 이어받을 때 필요한 최소 상태를 한 표에서 확인하게 해준다.
- readiness audit은 `HEAD == origin/hbin`처럼 커밋 전후에 바뀌는 값을 파일에 고정하지 않는다. 해당 동적 상태는 `verify_submission_state.py --require-clean` 실행 시점에 검증한다.
- 외부 클라우드 업로드와 비로그인 다운로드 검증은 로컬 코드로 끝낼 수 없는 운영 단계라 P27로 분리했다.
- 실제 RF, exploit, live network action 없이 폐쇄형 시뮬레이션 산출물만 감사한다.

연결한 것:

- README 실행 명령
- package builder required paths
- final verifier row/status/package manifest checks
- competition alignment matrix A10 row
- agent collaboration graph E17 edge
- FINAL_QA와 SUBMISSION_PACKAGE count

### 41. Local Package Integrity Gate를 강화한 이유

제출 직전에는 "ZIP 파일이 있다"보다 "그 ZIP이 현재 코드와 산출물 그대로인가"가 더 중요하다. 코드나 문서를 고친 뒤 ZIP을 다시 만들지 않으면, GitHub의 `hbin` 상태와 실제 업로드 ZIP이 달라질 수 있다.

그래서 final verifier의 package 검증을 강화했다.

수정한 것:

```text
scripts/verify_submission_state.py
README.md
docs/process/FINAL_QA.md
docs/process/SUBMISSION_PACKAGE.md
docs/process/NEXT_DEVELOPMENT_QUEUE.md
```

검증 방식:

```text
submission_manifest.md
-> zip_path 확인
-> payload_file_count 확인
-> zip_file_count 확인
-> zip_bytes 확인
-> zip_sha256 확인
-> manifest 포함 파일 목록과 ZIP 내부 목록 비교
-> ZIP 내부 payload 파일 SHA-256과 현재 worktree 파일 SHA-256 비교
-> 제외 대상 파일이 ZIP에 없는지 확인
```

검증 결과:

```text
package_zip entries: 162
package_manifest_integrity: passed
release_handoff: repo-only/current
package exclusions: passed
tracked_worktree: clean
```

해석:

- 이제 `scripts/verify_submission_state.py --require-clean`은 오래된 ZIP이나 manifest mismatch를 잡는다.
- 외부 클라우드 업로드 전에 `build_submission_package.py`와 final verifier를 다시 실행해야 한다.
- 외부 링크 다운로드 권한 검증은 업로드 위치가 필요하므로 별도 P28 운영 단계로 남긴다.

### 42. External Package Link Verifier를 추가한 이유

로컬 ZIP 무결성을 검증해도, 외부 클라우드에 업로드한 링크가 같은 파일을 내려주는지는 별도 문제다. 제출 링크가 로그인 전용이거나, 다른 ZIP을 가리키거나, 파일이 업로드 중 손상되면 로컬 verifier만으로는 확인할 수 없다.

그래서 외부 링크를 다운로드해 local manifest와 비교하는 도구를 추가했다.

추가한 것:

```text
scripts/verify_external_package_link.py
```

검증 방식:

```text
submission_manifest.md
-> expected zip_bytes / zip_sha256 / zip_file_count 읽기
external URL
-> GET download
-> bytes_read 계산
-> SHA-256 계산
-> ZIP entry count 계산
-> optional Content-Length 비교
-> expected 값과 비교
```

사용 방식:

```bash
python3 scripts/verify_external_package_link.py "https://..."
```

로컬 self-test:

```bash
python3 scripts/verify_external_package_link.py \
  "file://$(pwd)/outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip" \
  --allow-file-url
```

판단:

- 실제 제출 링크는 `https://`를 기본으로 요구한다.
- URL 안에 username/password가 들어간 credential-embedded URL은 거부한다.
- 다운로드된 ZIP의 SHA-256, byte count, ZIP entry count가 manifest와 일치해야 통과한다.
- 이 도구는 업로드 자체를 대신하지 않는다. 업로드 후 비로그인 링크를 받아 검증하는 단계에서 사용한다.

### 43. Release Candidate Handoff를 추가한 이유

제출 직전 인계에는 ZIP SHA-256, byte count, file count, 검증 명령, 남은 외부 업로드 작업이 한 장에 있어야 한다. 하지만 이 정보를 수동으로 문서에 쓰면 오래된 값을 복사할 위험이 있다.

그래서 manifest에서 값을 읽어 release candidate handoff 문서를 생성하는 도구를 추가했다.

추가한 것:

```text
scripts/generate_release_handoff.py
outputs/package/release_handoff.md
```

중요한 설계 판단:

```text
release_handoff.md는 repo-side 문서다.
제출 ZIP 안에는 넣지 않는다.
commit SHA는 파일에 고정하지 않고 push 후 명령으로 확인한다.
```

이유:

- handoff 문서는 ZIP SHA-256을 기록한다.
- 이 문서가 다시 ZIP 안에 들어가면 ZIP SHA가 자기 자신을 참조하게 된다.
- commit SHA도 tracked file 내용 전체를 포함해 계산되므로, 파일 안에 자기 커밋 SHA를 안정적으로 넣을 수 없다.
- 따라서 `outputs/package/release_handoff.md`는 GitHub `hbin` 브랜치에서 확인하는 인계 문서로 두고, 제출 ZIP에는 포함하지 않는다.
- release commit이 원격에 올라갔는지는 `git status --short --branch`, `git ls-remote --heads origin main hbin`, `git log --oneline --decorate -3`로 확인한다.

검증 방식:

```text
scripts/verify_submission_state.py
-> release_handoff.md 존재 확인
-> 현재 manifest의 zip_sha256 / zip_bytes / zip_file_count가 handoff에 있는지 확인
-> generated_branch가 hbin인지 확인
-> Git sync 확인 명령이 handoff에 있는지 확인
-> release_handoff.md가 ZIP 내부에 있으면 실패
```

검증 결과:

```text
release_handoff: repo-only/current
package_manifest_integrity: passed
tracked_worktree: clean
```

해석:

- release handoff는 외부 업로드 담당자가 마지막으로 볼 기준 문서다.
- ZIP 자체의 무결성은 `submission_manifest.md`와 final verifier가 책임지고, 외부 링크 검증은 `verify_external_package_link.py`가 책임진다.

### 44. Release Freeze Automation을 추가한 이유

최종 동결 절차는 순서가 중요하다. ZIP을 만든 뒤 handoff를 갱신하고, final verifier와 local link self-test까지 실행해야 한다. 이 순서를 사람이 매번 직접 기억하면 누락이 생길 수 있다.

그래서 release freeze 자동화 스크립트를 추가했다.

추가한 것:

```text
scripts/freeze_release_candidate.py
```

실행 순서:

```text
build_submission_package.py
-> generate_release_handoff.py
-> verify_submission_state.py
-> verify_external_package_link.py file://... --allow-file-url
-> manifest summary 출력
```

사용 방식:

```bash
python3 scripts/freeze_release_candidate.py
python3 scripts/freeze_release_candidate.py --require-clean
```

판단:

- 첫 번째 명령은 생성/검증 흐름을 재실행한다.
- `--require-clean`은 커밋 후 최종 상태 확인에 사용한다.
- 외부 다운로드 링크 검증은 업로드 후 `verify_external_package_link.py "https://..."`로 수행한다.

### 45. Deterministic Package Build로 바꾼 이유

`freeze_release_candidate.py --require-clean`을 커밋 후 실행했을 때 manifest와 handoff가 dirty가 되는 문제가 있었다. 원인은 ZIP 생성 시 파일 timestamp 같은 metadata가 ZIP에 들어가면서, payload가 같아도 ZIP SHA가 달라질 수 있었기 때문이다.

수정한 것:

```text
scripts/build_submission_package.py
```

변경 방식:

```text
zipfile.write()
-> ZipInfo + writestr()
-> 고정 ZIP timestamp
-> 안정적인 external_attr
-> path 기준 정렬 유지
```

검증:

```text
python3 scripts/freeze_release_candidate.py
python3 scripts/freeze_release_candidate.py
```

결과:

```text
두 번 연속 실행해도 zip_sha256 유지
package_manifest_integrity: passed
package_zip_metadata: deterministic
freeze_status: pass
```

해석:

- 같은 파일 payload라면 같은 ZIP SHA가 나온다.
- 커밋 후 `--require-clean` 검증이 package rebuild 때문에 실패하지 않는다.

### 46. Agent Decision Margin Audit를 추가한 이유

기존 `agent_decision_causality_audit.py`는 selected action이 candidate, tool, score 또는 threshold 근거와 일치하는지 확인했다. 이번 변경은 거기서 한 단계 더 나아가, 선택이 얼마나 강한 근거를 가졌는지 별도 산출물로 남긴다.

추가한 것:

```text
src/experiments/agent_decision_margin_audit.py
outputs/report_tables/agent_decision_margin_audit.csv
outputs/report_tables/agent_decision_margin_audit.md
```

검증 항목:

```text
AURA selected score vs runner-up score
AURA attack threshold margin
TSRA-R eligible/ready defense action count
TSRA-R-ML anomaly probability threshold margin
no-op decision basis
```

검증 결과:

```text
agent_decision_margin_audit rows: 399
margin_status: pass=399
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
```

해석:

- 이제 DecisionTrace는 "무엇을 골랐다"뿐 아니라 "얼마나 확실하게 골랐다"를 보여준다.
- no-op도 무행동이 아니라 threshold, cooldown, active window, eligible/ready 조건에 의해 설명된다.
- 실제 공격 도구나 live network action은 추가하지 않고 closed simulation evidence만 강화했다.

### 47. Agent Engagement Scorecard를 추가한 이유

공격 선택 근거, 방어 대응, metric 효과가 각각 다른 산출물에 나뉘어 있으면 심사자가 공방 1건의 흐름을 따라가려면 여러 파일을 오가야 한다. 이번 변경은 공방 1건을 한 행으로 묶어 AURA 선택 margin, TSRA-R 대응, mission impact movement를 같이 보게 한다.

추가한 것:

```text
src/experiments/agent_engagement_scorecard.py
outputs/report_tables/agent_engagement_scorecard.csv
outputs/report_tables/agent_engagement_scorecard.md
```

입력으로 결합한 산출물:

```text
outputs/report_tables/closed_loop_episode_replay.csv
outputs/report_tables/agent_decision_margin_audit.csv
outputs/report_tables/defense_effectiveness_ledger.csv
```

검증 결과:

```text
agent_engagement_scorecard rows: 10
scorecard_status: pass=10
experiments: E5_rule_aura_tsra_r, E7_ml_aura_ml_tsra_r
```

해석:

- 공격 이벤트 10건 모두 공격 선택 margin, 방어 이벤트 수, response status, peak 대비 impact reduction으로 연결된다.
- E7의 AURA-ML trace와 attack event agent 표기 차이는 AURA 계열 agent로 조인되게 처리했다.
- closed simulation evidence만 결합하며 실제 공격 기능은 추가하지 않았다.

### 48. 제출 ZIP 공식 파일명 정렬

제출 직전 운영에서 같은 ZIP을 가리키는 이름이 여러 개 있으면 업로드, manifest 검증, 외부 링크 검증 단계에서 혼선이 생긴다. 이번 변경은 기본 생성 파일명과 문서의 검증 명령을 예선 안내서 형식에 맞춰 하나로 정렬했다.

변경한 기준:

```text
outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip
```

적용 범위:

```text
scripts/build_submission_package.py
scripts/freeze_release_candidate.py
scripts/verify_submission_state.py
README.md
docs/process/SUBMISSION_PACKAGE.md
docs/process/FINAL_QA.md
docs/process/NEXT_DEVELOPMENT_QUEUE.md
docs/process/COMPETITION_DIRECTION.md
```

판단:

- 기본 파일명은 `DAH2026_소스코드_[팀명].zip` 제출 형식과 맞춘다.
- ZIP 자체는 Git에 커밋하지 않고, manifest와 SHA-256 검증으로 동일성을 확인한다.
- `main`은 그대로 두고 `hbin`에서만 이 기준을 공유한다.

### 49. Agent Runtime Invariant Audit를 추가한 이유

기존 산출물은 DecisionTrace 품질, Memory 변화, Tool 사용 여부를 각각 검증했다. 하지만 AgentRuntime 자체가 매 decision loop에서 같은 불변조건을 지키는지 한 장으로 확인하는 표는 없었다.

이번 변경은 `DecisionTrace` 로그를 다시 읽어서 runtime-level invariant를 검증한다.

추가한 것:

```text
src/experiments/agent_runtime_invariant_audit.py
outputs/report_tables/agent_runtime_invariant_audit.csv
outputs/report_tables/agent_runtime_invariant_audit.md
```

검증 항목:

```text
trace_id uniqueness and contiguous suffix
monotonic time
AgentMemory observation_count/decision_count progression
last_selected_action chain
tool error count
candidate action evidence
selected attack/defense event coverage
```

검증 결과:

```text
agent_runtime_invariant_audit rows: 9
status: pass=9
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
tool_error_count: 0
```

해석:

- AgentRuntime, AgentMemory, Tool, DecisionTrace가 실제 실험 로그에서 같은 loop contract로 움직였음을 별도 산출물로 증명한다.
- 이 audit도 closed simulation log만 읽으며 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

### 50. Safety Boundary Audit를 추가한 이유

안전 경계 문구는 README, agent docs, COA, incident, collaboration graph에 이미 있다. 하지만 제출 직전에는 "정말 operational core code에 네트워크/RF/exploit primitive가 없는가"를 기계적으로 확인하는 산출물이 있으면 더 명확하다.

이번 변경은 Python AST 기반 정적 감사를 추가했다.

추가한 것:

```text
src/experiments/safety_boundary_audit.py
outputs/report_tables/safety_boundary_audit.csv
outputs/report_tables/safety_boundary_audit.md
```

검증 항목:

```text
operational core source network primitive hits
operational core source shell primitive hits
automation exception allowlist
AURA simulated AttackCandidate/AttackEvent schema
safety-boundary text coverage
submission package binary/cache exclusion policy
```

검증 결과:

```text
safety_boundary_audit rows: 5
status: pass=5
operational core network_hits: 0
operational core shell_hits: 0
unexpected automation network/shell hits: 0
```

해석:

- `src/agents`, `src/aura`, `src/tsra_r`, `src/simulator`, `src/shared`, `src/ml`에는 live-network나 shell execution primitive가 없음을 별도 증거로 남겼다.
- `scripts/verify_external_package_link.py`의 `urllib`은 제출 ZIP 링크 검증용으로만 허용하고, release/Git 검증의 `subprocess`도 allowlist로 분리했다.
- 실제 공격 기능은 추가하지 않았다.

### 51. ML Contribution Audit를 추가한 이유

ML 모델 성능 파일, tool usage audit, metric gate, E7 event log가 각각 존재해도 그것만으로는 "ML이 실제 에이전트 판단에 기여했는가"를 한 번에 확인하기 어렵다. 특히 AURA-ML은 후보 impact 예측을 ranking에 넣고, TSRA-R-ML은 anomaly probability로 reactive defense window를 여는 구조라서 모델 품질과 agent loop 증거를 함께 봐야 한다.

이번 변경은 ML 기여도를 하나의 audit로 묶었다.

추가한 것:

```text
src/experiments/ml_contribution_audit.py
outputs/report_tables/ml_contribution_audit.csv
outputs/report_tables/ml_contribution_audit.md
```

검증 항목:

```text
AURA-ML model quality
TSRA-R-ML detector quality
AURA-ML predict_candidate_impact tool invocation
TSRA-R-ML predict_attack_probability tool invocation
E6/E7 closed-loop separation
E7 ML attack diversity and ml_attack_alert actions
Mac MPS sample-pass scale framing
```

검증 결과:

```text
ml_contribution_audit rows: 7
status: pass=7
AURA-ML predict_candidate_impact invocations: 52
TSRA-R-ML predict_attack_probability invocations: 61
E6/E7 mission impact gap: 0.0162307
Mac MPS sample_passes: 20000000
```

해석:

- ML은 offline metric으로만 남아 있지 않고 AURA-ML과 TSRA-R-ML의 DecisionTrace tool call에 연결된다.
- E7은 E6와 다른 폐루프 결과를 만들기 때문에 ML TSRA-R이 no-op copy가 아님을 확인한다.
- Mac GPU 실험은 "서로 다른 2천만 후보"가 아니라 "100만 샘플 x 20 epoch = 2천만 sample-pass"로 기록한다.
- 실제 공격 기능은 추가하지 않고 closed simulation log와 metrics만 감사한다.

### 52. Reactive Defense Tradeoff Audit를 추가한 이유

E7은 E6보다 mission impact가 낮다고 주장하면 안 된다. E6는 full rule TSRA-R이고 E7은 ML detector가 threshold를 넘을 때 reactive defense window를 여는 구조다. 따라서 E7의 가치는 "항상 더 낮은 impact"가 아니라 "탐지 기반 개입의 장점과 비용을 투명하게 보여주는 것"으로 잡아야 한다.

이번 변경은 E6/E7 차이를 tradeoff audit로 분리했다.

추가한 것:

```text
src/experiments/reactive_defense_tradeoff_audit.py
outputs/report_tables/reactive_defense_tradeoff_audit.csv
outputs/report_tables/reactive_defense_tradeoff_audit.md
```

검증 항목:

```text
E6/E7 policy separation
pre-attack defense suppression
first-response latency cost
ML alert overlap with active attack windows
core defense action preservation
bounded mission-impact tradeoff
below/above-threshold detector trace evidence
```

검증 결과:

```text
reactive_defense_tradeoff_audit rows: 7
status: pass=7
E6 pre-first defense events: 2
E7 pre-first defense events: 0
E7 first ML alert latency: 20 sec
ML alerts overlapping active attack: 9/9
E7 minus E6 mission impact mean: 0.0162307
```

해석:

- E7은 pre-attack 방어 이벤트를 억제하고, 탐지 확률이 높아진 뒤 방어창을 연다.
- 그 비용으로 첫 alert가 20초 늦고, repeated metric에서 E7 impact가 E6보다 0.0162307 높다.
- core defense action은 유지되므로 E7은 방어 기능 축소가 아니라 reactive trigger 구조의 차이를 보여준다.
- 실제 공격 기능은 추가하지 않고 closed simulation trace, event log, batch metric만 읽는다.

### 53. ML Threshold Sweep을 추가한 이유

`MLTSRAR(threshold=0.75)`는 코드상 명시되어 있지만, 왜 그 값이 말이 되는지 별도 산출물이 없으면 임의 상수처럼 보인다. E7을 강화하려면 threshold를 숨기지 말고 운영 파라미터로 노출하고, 낮은 threshold와 높은 threshold의 tradeoff를 수치로 보여줘야 한다.

이번 변경은 TSRA-R-ML anomaly threshold sweep을 추가했다.

추가한 것:

```text
src/experiments/run_ml_threshold_sweep.py
outputs/batch/ml_threshold_sweep_raw.csv
outputs/batch/ml_threshold_sweep_summary.csv
outputs/report_tables/ml_threshold_sweep.csv
outputs/report_tables/ml_threshold_sweep.md
```

실험 설정:

```text
thresholds: 0.55, 0.65, 0.75, 0.85, 0.95
runs per threshold: 10 deterministic seeds
agent pair: AURA-ML + TSRA-R-ML
```

검증 결과:

```text
ml_threshold_sweep_raw rows: 50
ml_threshold_sweep_summary rows: 5
0.55 impact_mean: 0.161111, status: usable
0.65 impact_mean: 0.161111, status: usable
0.75 impact_mean: 0.161111, status: usable
0.85 impact_mean: 0.161111, status: usable
0.95 impact_mean: 0.184434, status: watch
```

해석:

- 0.55~0.85 구간은 같은 impact plateau를 보인다.
- 0.95는 alert 수가 줄고 first alert latency가 늘며 mission impact가 올라간다.
- 현재 E7 baseline threshold 0.75는 plateau 안에 있고, 너무 높은 0.95는 watch로 분리된다.
- 실제 공격 기능은 추가하지 않고 closed simulation threshold tuning만 수행한다.

### 54. TSRA-R Detector Calibration Audit를 추가한 이유

threshold sweep은 어떤 threshold가 closed-loop에서 어떤 결과를 내는지 보여준다. 하지만 TSRA-R-ML은 `predict_attack_probability` 값을 직접 threshold에 넣기 때문에, 그 확률 자체가 threshold 의사결정에 쓸 만한지도 별도로 확인해야 한다.

이번 변경은 detector probability calibration audit를 추가했다.

추가한 것:

```text
src/experiments/tsra_detector_calibration_audit.py
outputs/report_tables/tsra_detector_calibration_audit.csv
outputs/report_tables/tsra_detector_calibration_audit.md
outputs/report_tables/tsra_detector_calibration_bins.csv
```

검증 설정:

```text
holdout rows: 4000
seed: 9100
model: outputs/models/tsra_detector.pkl
thresholds checked: 0.55, 0.65, 0.75, 0.85, 0.95
```

검증 결과:

```text
brier_score: 0.0351619
expected_calibration_error: 0.093589
threshold 0.75 precision: 1.0
threshold 0.75 recall: 0.833417
threshold 0.75 false_positive_rate: 0.0
positive_median_probability: 0.956382
negative_median_probability: 0.106435
```

해석:

- Brier score는 강하고 ECE는 thresholding에 허용 가능한 수준이다.
- 확률이 완벽히 calibrated truth라고 주장하지 않는다. 다만 고신뢰 threshold decision input으로는 충분한 근거가 있다.
- 0.75는 false positive를 0으로 묶는 보수적 기준이며, 0.95는 recall이 0.532까지 떨어져 closed-loop sweep의 watch 결과와 일치한다.
- 실제 공격 기능은 추가하지 않고 synthetic holdout과 closed simulation 결과만 감사한다.

### 55. Agent Goal Alignment Audit를 추가한 이유

AgentRuntime, Memory, Tool, DecisionTrace, causality, margin audit까지는 "에이전트가 어떤 근거로 행동을 골랐는가"를 보여준다. 하지만 한 단계 더 중요한 질문이 남아 있었다.

```text
그 행동이 각 에이전트의 목표와 실제 관측 위험에 맞는가?
```

이번 변경은 이 질문을 별도 audit로 고정했다.

추가한 것:

```text
src/experiments/agent_goal_alignment_audit.py
outputs/report_tables/agent_goal_alignment_audit.csv
outputs/report_tables/agent_goal_alignment_audit.md
```

검증 기준:

```text
AURA attack_event
-> selected_score >= attack_threshold
-> selected_score == top candidate score
-> predicted_mission_impact > 0

AURA no_op
-> min_start, cooldown, max_events, no candidate, or below-threshold reason이 있어야 한다.

TSRA-R defense_events
-> priority_reroute: critical_pending > 0 and video_queue_kb > 500
-> video_throttle: video_queue_kb > 1500
-> stale_badge: stale_data_ratio > 0.25
-> pace_switch: active link degradation threshold 초과
-> ml_attack_alert: probability >= threshold

TSRA-R no_op
-> ready defense action이 없거나 ML defense window 유지 상태여야 한다.
```

검증 결과:

```text
agent_goal_alignment_audit rows: 399
status counts: pass=399
agents: AURA, AURA-ML, TSRA-R, TSRA-R-ML
selected types: no_op=290, defense_events=84, attack_event=25
```

해석:

- 공격 에이전트는 단순히 후보를 고른 것이 아니라 mission-impact goal score와 threshold를 통과한 행동을 선택한다.
- 방어 에이전트는 단순히 룰을 실행한 것이 아니라 관측된 priority, video load, stale data, PACE degradation, ML probability 조건에 맞춰 행동한다.
- no-op도 "아무것도 안 함"이 아니라 cadence, cooldown, threshold, active defense window 근거가 있는 판단으로 검증된다.
- 실제 공격 기능은 추가하지 않고 closed simulation trace audit만 추가했다.

### 56. Defense Action Attribution Audit를 추가한 이유

`defense_effectiveness_ledger`는 각 DefenseEvent 전후 metric 변화를 보여준다. 하지만 event row가 56개라서, 심사나 팀 리뷰에서 "그래서 priority_reroute, stale_badge, video_throttle, pace_switch, ml_attack_alert 각각은 어떤 근거로 가치가 있나?"를 바로 보기 어렵다.

이번 변경은 방어 action별 attribution audit를 추가했다.

추가한 것:

```text
src/experiments/defense_action_attribution_audit.py
outputs/report_tables/defense_action_attribution_audit.csv
outputs/report_tables/defense_action_attribution_audit.md
```

검증 기준:

```text
input ledger rows: 56
output attribution rows: 5
actions: priority_reroute, video_throttle, stale_badge, pace_switch, ml_attack_alert
status: pass=5
```

핵심 결과:

```text
priority_reroute:
  improved_or_held_rate: 0.818182
  mean_delta_priority_inversion_rate: -0.0347756
  ablation_delta_priority_inversion_rate_mean: 0.410888

stale_badge:
  improved_or_held_rate: 0.875
  mean_delta_trusted_stale_exposure: -0.00390625
  ablation_delta_trusted_stale_exposure_mean: 0.38125

video_throttle:
  improved_or_held_rate: 0.785714
  mean_delta_p95_critical_latency_sec: -0.567857
  attribution_class: local_metric_supported

pace_switch:
  improved_or_held_rate: 0.666667
  mean_delta_mission_impact: -0.0232876
  mean_delta_p95_critical_latency_sec: -1.06667
  attribution_class: bounded_tradeoff_supported

ml_attack_alert:
  improved_or_held_rate: 0.888889
  active_attack_overlap: 9/9
  attribution_class: reactive_window_supported
```

해석:

- `priority_reroute`와 `stale_badge`는 ablation으로 직접 가치가 강하게 보인다.
- `video_throttle`은 scalar mission impact 하나로 팔면 약하지만, local latency/priority relief로 보면 의미가 있다.
- `pace_switch`는 recovery/fallback 문맥이 있어 scalar ablation만으로 가치를 판단하면 왜곡될 수 있으므로 bounded tradeoff로 분류했다.
- `ml_attack_alert`는 직접 metric 조작 action이 아니라 reactive defense window trigger로 attribution했다.
- 실제 공격 기능은 추가하지 않고 closed simulation event/metric attribution만 감사한다.

### 57. Mission Thread Summary를 추가한 이유

`closed_loop_episode_replay`, `agent_engagement_scorecard`, `defense_action_attribution_audit`는 각각 필요한 증거를 제공하지만, 한 공격 episode를 처음부터 끝까지 검토하려면 여러 CSV를 넘나들어야 했다. 공격 판단 근거, TSRA-R 반응, defense action attribution, operator alert, metric movement, residual risk가 흩어져 있으면 협업자가 공방 루프를 빠르게 확인하기 어렵다.

이번 변경은 공격 episode별 mission thread summary를 추가했다.

추가한 것:

```text
src/experiments/mission_thread_summary.py
outputs/report_tables/mission_thread_summary.csv
outputs/report_tables/mission_thread_summary.md
```

검증 기준:

```text
input closed_loop_episode_replay rows: 10
input agent_engagement_scorecard rows: 10
input defense_action_attribution_audit rows: 5
output mission_thread_summary rows: 10
thread_status: pass=10
experiments: E5_rule_aura_tsra_r=5, E7_ml_aura_ml_tsra_r=5
operator_signal_count range: 3-7
```

해석:

- 한 row에서 AURA attack decision, TSRA-R response coverage, defense action attribution, operator signal count, metric reduction, outcome, residual risk를 같이 볼 수 있다.
- E5와 E7의 closed-loop episode가 같은 기준으로 비교된다.
- 공격-방어 협력 구조를 단순 표 개수보다 mission thread 단위로 설명할 수 있다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않고 closed simulation mission-thread summary만 생성한다.

### 58. Agent Decision Feedback Audit를 추가한 이유

`agent_decision_margin_audit`와 `agent_goal_alignment_audit`는 선택 시점의 후보, 점수, threshold, 목표 정렬을 검증한다. 하지만 그것만으로는 "선택 이후 실제 시뮬레이션 feedback까지 연결됐는가"를 바로 증명하지 못한다.

이번 변경은 E5/E7 closed-loop run에서 선택된 attack/defense event를 DecisionTrace에서 뽑아 실제 event log, metric snapshot, closed-loop outcome, defense ledger, action attribution과 연결했다.

추가한 것:

```text
src/experiments/agent_decision_feedback_audit.py
outputs/report_tables/agent_decision_feedback_audit.csv
outputs/report_tables/agent_decision_feedback_audit.md
```

검증 기준:

```text
agent_decision_feedback_audit rows: 66
feedback_status: pass=66
experiments: E5_rule_aura_tsra_r=28, E7_ml_aura_ml_tsra_r=38
selected_event_type: attack_event=10, defense_event=56
feedback_class:
  attack_contained_by_defense=5
  attack_pressure_observed=5
  defense_bounded_or_lagged=9
  defense_held=27
  defense_improved=19
  ml_window_triggered=1
```

해석:

- 에이전트가 선택한 action이 실제 event log에 존재하는지 확인한다.
- 선택 전후 mission metric feedback window를 붙인다.
- 공격 선택은 pressure observed 또는 defense containment로 분류한다.
- 방어 선택은 improved/held/bounded attribution/ML window trigger로 분류한다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않고 closed simulation decision-feedback audit만 생성한다.

### 59. Agent Memory Influence Audit를 추가한 이유

`agent_memory_belief_audit`는 memory가 존재하고 변화하며 이전 selected action을 다음 loop로 넘기는지 검증한다. 하지만 그것만으로는 memory가 실제 선택을 바꾸는 decision gate인지 충분히 드러나지 않는다.

이번 변경은 memory가 행동에 영향을 주는 대표 경로를 별도 audit로 고정했다.

추가한 것:

```text
src/experiments/agent_memory_influence_audit.py
outputs/report_tables/agent_memory_influence_audit.csv
outputs/report_tables/agent_memory_influence_audit.md
```

검증 기준:

```text
agent_memory_influence_audit rows: 6
influence_status: pass=6
MI01 AURA cooldown_noops=48, max_event_noops=12
MI02 AURA-ML cooldown_noops=32, max_event_noops=8
MI03 TSRA-R eligible_not_ready actions present for priority_reroute, video_throttle, stale_badge, pace_switch
MI04 TSRA-R-ML opened_windows=45, active_window_noops=22
MI05 Adaptive TSRA-R delta_mission_impact_mean=-0.0479341, delta_defense_count_mean=-4.93333
MI06 memory chain rows=9, pass_rows=9, min_last_selected_chain_match_rate=1
```

해석:

- AURA/AURA-ML은 공격 후보가 있어도 cadence memory 때문에 공격을 보류한다.
- TSRA-R은 조건이 맞아도 action cooldown memory 때문에 반복 방어를 억제한다.
- TSRA-R-ML은 active defense window를 memory로 유지한다.
- Adaptive TSRA-R은 recent memory window로 optional defense를 줄이면서 mission impact도 낮춘다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않고 closed simulation memory-influence audit만 생성한다.

### 60. Agent Coordination Latency Audit를 추가한 이유

`closed_loop_episode_replay`와 `mission_thread_summary`는 공격-방어-알림-지표를 묶어 보여준다. 하지만 협력 구조의 시간 품질, 즉 공격 이후 방어 반응과 operator alert가 response window 안에 실제로 이어졌는지는 별도 수치로 고정하는 편이 더 명확하다.

이번 변경은 E5/E7 closed-loop episode별 coordination latency audit를 추가했다.

추가한 것:

```text
src/experiments/agent_coordination_latency_audit.py
outputs/report_tables/agent_coordination_latency_audit.csv
outputs/report_tables/agent_coordination_latency_audit.md
```

검증 기준:

```text
agent_coordination_latency_audit rows: 10
coordination_status: pass=10
experiments: E5_rule_aura_tsra_r=5, E7_ml_aura_ml_tsra_r=5
coordination_class:
  prepositioned_defense=9
  ml_reactive_window=1
first_operator_alert_latency_sec <= 40 for all rows
impact_reduction_from_peak > 0 for all rows
```

해석:

- 방어가 이미 active였거나 response window 안에서 이어졌는지 episode 단위로 확인한다.
- operator-facing alert가 response window 안에 나왔는지 확인한다.
- metric peak 이후 impact reduction이 있었는지 확인한다.
- E7 첫 공격은 ML reactive window로 분류되어 ML 방어자의 시간상 역할을 따로 보여준다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않고 closed simulation coordination-latency audit만 생성한다.

### 61. ML Defense Decision Path Audit를 추가한 이유

이전 상태에서는 ML contribution audit와 reactive defense tradeoff audit가 있었지만, E7 TSRA-R-ML의 내부 판단 흐름을 한눈에 따라가기에는 간격이 있었다. 즉, `predict_attack_probability`가 호출되고 E7 결과가 E6와 다르다는 증거는 있었지만, 확률이 threshold를 넘는 순간이 어떤 defense window, alert, no-op cooldown, core defense action으로 이어지는지 별도 산출물로 분해되어 있지 않았다.

그래서 `src/experiments/ml_defense_decision_path_audit.py`를 추가했다. 이 감사는 기존 실험을 바꾸지 않고 `outputs/experiments/E7_ml_aura_ml_tsra_r/tsra_r_decision_traces.jsonl`, `defense_events.jsonl`, `attack_events.jsonl`, `agent_coordination_latency_audit.csv`만 읽어서 ML 방어 decision path를 검증한다.

검증 결과는 다음과 같다.

```text
ml_defense_decision_path_audit rows: 6
status: pass=6
pre_threshold_noop_count: 16
pre_threshold_defense_events: 0
first_response_latency_sec: 20
above_threshold_event_traces: 23
above_threshold_no_event_refresh_traces: 22
ml_attack_alerts: 9
min_alert_gap_sec: 25
memory_mismatches: 0
threshold_window_nondecreasing: true
```

이 보강의 의미는 E7 ML 방어자가 단순한 모델 성능 숫자나 장식적 이벤트가 아니라, threshold 판단을 통해 active defense window를 열고, alert cooldown으로 과잉 알림을 막고, 그 window 안에서 core TSRA-R action을 실행하며, memory로 window 상태를 유지한다는 점을 검증 가능한 형태로 만든 것이다.

### 62. ML Attack Decision Path Audit를 추가한 이유

방어 쪽은 `ml_defense_decision_path_audit`로 probability threshold에서 defense window까지 이어지는 흐름을 검증했다. 같은 수준으로 공격 쪽도 AURA-ML이 실제로 후보를 만들고, ML impact prediction과 detectability penalty로 top candidate를 고르고, cooldown과 event budget을 지키며, attack event와 closed-loop feedback까지 연결되는지 분해할 필요가 있었다.

그래서 `src/experiments/ml_attack_decision_path_audit.py`를 추가했다. 이 감사는 E7의 `aura_decision_traces.jsonl`, `attack_events.jsonl`, `agent_engagement_scorecard.csv`를 읽어서 AURA-ML decision path를 검증한다.

검증 결과는 다음과 같다.

```text
ml_attack_decision_path_audit rows: 6
status: pass=6
pre_start_noop_count: 6
candidate_total: 27
predict_candidate_impact: 27
estimate_candidate_effect: 27
estimate_detectability: 27
selected_matches_top_candidate: 5
score_formula_matches: 27
cooldown_noops: 16
max_event_noops: 4
min_attack_gap_sec: 50
complete_responses: 5
positive_reductions: 5
```

이 보강의 의미는 AURA-ML이 단순히 attack event 5개를 만든 것이 아니라, AgentRuntime tool path와 scoring formula, memory gate, post-action feedback을 갖춘 공격 에이전트로 검증된다는 점이다. 실제 공격 기능, RF, exploit, live network action은 추가하지 않는다.

### 63. ML Red-Blue Interaction Audit를 추가한 이유

ML attack decision path와 ML defense decision path는 각각 공격 에이전트와 방어 에이전트의 내부 판단 흐름을 증명한다. 하지만 E7 전체를 보면 더 중요한 질문은 "AURA-ML이 고른 공격이 TSRA-R-ML의 probability/window/alert/core defense로 같은 response window 안에서 이어졌는가"다.

그래서 `src/experiments/ml_red_blue_interaction_audit.py`를 추가했다. 이 감사는 E7의 AURA trace, TSRA-R trace, attack event, defense event, coordination latency audit를 한 row로 묶는다.

검증 결과는 다음과 같다.

```text
ml_red_blue_interaction_audit rows: 5
interaction_status: pass=5
interaction_class:
  ml_triggered_after_attack=1
  active_window_immediate_core_defense=2
  active_window_bounded_refresh=2
first_ml_alert_latency_sec: 20 for all rows
first_core_defense_latency_sec <= 20 for all rows
impact_reduction_from_peak > 0 for all rows
```

해석:

- 첫 E7 공격은 AURA-ML 선택 이후 TSRA-R-ML이 20초 뒤 probability threshold를 넘고 alert/core defense를 낸다.
- 이후 공격들은 이미 열린 ML defense window 안에서 즉시 또는 10초 안에 core defense로 이어진다.
- 이 산출물은 "공격 에이전트"와 "방어 에이전트"가 각각 존재한다는 수준을 넘어, 같은 closed-loop episode 안에서 서로 맞물려 작동했다는 증거다.

### 64. Reproduction Order Audit를 추가한 이유

기존 `Full Reproduction` 명령은 필요한 명령을 대부분 포함했지만, 일부 감사가 자신이 읽는 입력 산출물보다 먼저 실행되는 순서였다. 예를 들어 defense action attribution은 reactive defense tradeoff를 읽고, mission thread summary는 engagement scorecard를 읽으며, ML red-blue interaction audit는 ML attack/defense path와 coordination latency를 함께 읽는다. 순서가 어긋나면 로컬에 남아 있던 이전 CSV를 읽어서 겉으로는 통과하는 상태가 될 수 있다.

이번 변경은 `src/experiments/reproduction_order_audit.py`를 추가해서 README `Full Reproduction` 블록의 command order를 별도로 감사한다.

추가한 것:

```text
src/experiments/reproduction_order_audit.py
outputs/report_tables/reproduction_order_audit.csv
outputs/report_tables/reproduction_order_audit.md
```

검증 기준:

```text
reproduction_order_audit rows: 13
RO01 defense_action_attribution_audit prerequisites pass
RO05 mission_thread_summary prerequisites pass
RO06/RO07/RO08 ML path and red-blue interaction prerequisites pass
RO09 agent stress scenario prerequisites pass
RO11 package build prerequisites pass
RO13 final verifier after release freeze pass
```

해석:

- 새 팀원이 처음부터 실행해도 downstream audit가 stale output에 기대지 않는다.
- `submission_readiness_audit`, `competition_alignment`, `verify_submission_state`, package manifest가 모두 reproduction order evidence를 참조한다.
- package manifest와 release handoff는 packaging 이후에 생성되는 산출물이므로, readiness audit은 그 파일을 선행 요구하지 않도록 순환 의존성을 제거했다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않고 closed simulation reproduction-order evidence만 생성한다.

### 65. Agent Stress Scenario Audit를 추가한 이유

기존 E1~E7, 30-seed batch, ML red-blue interaction audit는 평균적인 실험 체계와 E7 episode 연결을 잘 보여준다. 하지만 방어 에이전트 품질을 더 높이려면 "평균적으로 좋다"를 넘어 특정 작전 압박 상황에서도 TSRA-R이 버티는지 확인해야 한다.

이번 변경은 `src/experiments/agent_stress_scenario_audit.py`를 추가했다. 이 감사는 세 가지 폐쇄형 stress fixture를 생성한다.

```text
stress_air_defense_queue_saturation
stress_stale_cop_latency_chain
stress_pace_failover_pressure
```

각 fixture는 5개 seed에서 attack-only 결과와 `tsra_r_full`, `tsra_r_ml` 결과를 비교한다. 임시 실행 로그는 `outputs/tmp_agent_stress_scenario/`에 남고, 검토용 산출물은 report table로 생성된다.

추가한 것:

```text
src/experiments/agent_stress_scenario_audit.py
outputs/report_tables/agent_stress_scenario_audit.csv
outputs/report_tables/agent_stress_scenario_audit.md
```

검증 결과:

```text
agent_stress_scenario_audit rows: 6
status: pass=6
scenarios: air_defense_queue_saturation, stale_cop_latency_chain, pace_failover_pressure
defender variants: tsra_r_full, tsra_r_ml
seed_count: 5 per row
tsra_r_full resilience_gain_mean range: 0.775357-0.842876
tsra_r_ml resilience_gain_mean range: 0.754937-0.833690
tsra_r_full resilience_gain_min floor: 0.710987
tsra_r_ml stressed stale-COP gain_min: 0.699806
defended_mission_impact_mean max: 0.174011
stale-COP mission_guard_trigger_count_mean: 3.2
stale-COP mission_guard_event_trace_count_mean: 1.0
```

해석:

- TSRA-R full은 세 stress fixture 모두에서 평균 0.75 이상의 resilience gain을 유지한다.
- TSRA-R-ML은 세 stress fixture 모두에서 평균 0.65 이상의 resilience gain을 유지한다.
- TSRA-R-ML은 stale-COP chain에서 residual mission-risk guard를 사용해 window 종료 시점의 `stale_badge` 갱신 누락을 줄인다.
- 모든 stress row에서 평균 P95 latency, trusted stale exposure, priority inversion이 attack-only 대비 감소한다.
- 이 보강은 방어 에이전트가 일반 실험뿐 아니라 특정 임무 압박 조건에서도 작동한다는 증거를 추가한다.
- 실제 공격 기능, RF, exploit, live network action은 추가하지 않고 closed simulation stress evidence만 생성한다.

### 66. TSRA-R-ML Residual Mission-Risk Guard를 추가한 이유

stress audit에서 가장 약했던 지점은 `stress_stale_cop_latency_chain`의 TSRA-R-ML seed 편차였다. 원인은 detector가 첫 공격 구간에서는 방어 window를 열지만, 공격 효과가 약해진 뒤 probability가 threshold 아래로 내려가면서 window가 닫히고, stale COP 위험이 남은 시점의 `stale_badge` refresh를 놓치는 구조였다.

이번 변경은 `MLTSRAR`에 두 번째 tool을 추가했다.

```text
assess_mission_risk_guard
```

작동 기준:

```text
1. 이전에 ML detector가 방어 window를 연 적이 있어야 한다.
2. active_defense_until이 가까워졌거나 지났어야 한다.
3. residual_stale_cop, critical_queue_pressure, residual_link_degradation 중 하나가 있어야 한다.
4. probability가 threshold 아래일 때만 mission guard extension으로 해석한다.
```

중요한 설계 선택:

- 새 `DefenseEvent` action을 만들지 않았다.
- guard는 기존 core action을 실행할 수 있는 짧은 window만 연장한다.
- 기본 E7에서는 `mission_guard_triggered=0`으로 기존 threshold decision path를 바꾸지 않았다.
- stress audit에는 `mission_guard_trigger_count_mean`, `mission_guard_event_trace_count_mean` 컬럼을 추가해 guard 작동 여부를 산출물에서 바로 볼 수 있게 했다.

검증 결과:

```text
stress_stale_cop_latency_chain TSRA-R-ML
gain_mean: 0.675561 -> 0.754937
gain_min:  0.486689 -> 0.699806
impact_mean: 0.229527 -> 0.174011
mission_guard_trigger_count_mean: 3.2
mission_guard_event_trace_count_mean: 1.0
```

해석:

- 이번 변경은 ML 방어자를 full rule 방어자로 되돌린 것이 아니다.
- detector probability가 닫히는 경계에서 residual mission risk만 확인해 방어 window를 제한적으로 연장한다.
- Agent Runtime 관점에서는 `predict_attack_probability`와 `assess_mission_risk_guard`가 모두 ToolCallRecord에 남고, Memory에는 `last_mission_guard_reason`, `last_mission_guard_score`가 남는다.
