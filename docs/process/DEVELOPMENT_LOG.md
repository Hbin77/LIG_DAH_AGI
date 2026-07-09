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
E6/E7 impact separation: 0.0167761
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
agent_tool_usage_audit.csv: 23 rows
status: pass=23
tools:
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
- TSRA-R-ML은 anomaly probability prediction tool을 실제 호출한다.
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
  "file://$(pwd)/outputs/package/DAH2026_source_LIG_DAH_AGI.zip" \
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
