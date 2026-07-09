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
