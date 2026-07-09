# DAH 2026 보고서 작성자 가이드

이 문서는 보고서 담당자가 `LIG_DAH_AGI` 결과물을 이해하고 예선 보고서에 바로 반영할 수 있도록 만든 작성 가이드입니다. 핵심 목적은 코드 설명을 길게 반복하는 것이 아니라, **보고서에 써도 되는 주장**, **근거 파일**, **수치**, **안전 경계**, **복붙 가능한 문장**을 한곳에 정리하는 것입니다.

## 한 줄 결론

이 결과물은 실제 SATCOM 공격 도구가 아니라, 폐쇄형 synthetic mission-event simulator 안에서 AURA 공격 효과와 TSRA-R/TSRA-ML 방어 판단을 검증하는 AI 공방 에이전트 프로토타입입니다.

보고서의 핵심 주장은 다음처럼 잡으면 됩니다.

> 본 구현은 Hybrid SATCOM Disruption 상황에서 C4ISR 데이터 신뢰성 붕괴를 모사하고, AURA-lite 공격 에이전트와 TSRA-R/TSRA-ML 방어 에이전트의 판단 및 대응 효과를 폐쇄형 mission-event simulator로 검증한다. 5개 seed 기준 공격 단독 mission impact는 평균 82.162였고, TSRA-R/TSRA-ML 적용 후 15.306으로 감소하여 baseline-adjusted resilience gain 90.374%를 기록했다. 각 에이전트의 판단 과정은 DecisionTrace로 남겨 observation, memory, tool call, candidate action, selected action, feedback을 감사 가능하게 했다.

## 어디에 무엇을 쓰면 되는가

| 보고서 파트 | 써야 할 내용 | 근거 파일 |
|---|---|---|
| 공격 시나리오 | Hybrid SATCOM Disruption으로 인한 지연, 손실, failover chasing, critical traffic 지연 | `docs/architecture.md`, `src/tsra_agent/agents.py`, `src/tsra_agent/simulator.py` |
| 방어 전략 | risk fusion, priority boost, minimum mode, PACE routing, stale badge, quarantine flag | `docs/architecture.md`, `src/tsra_agent/agents.py`, `src/tsra_agent/simulator.py` |
| AI 에이전트 설계 | AURA-lite, TSRA-R-lite, TSRA-ML의 역할과 판단 loop | `src/tsra_agent/runtime.py`, `docs/agent_branch_comparison.md` |
| 실험/평가 | E1 baseline, E2 attacked, rule defense, TSRA-R, TSRA-ML, false alarm check | `examples/summary_multi_seed.json`, `examples/incident_report_multi_seed.md` |
| 안전 경계 | 실제 RF, SATCOM 장비 공격, exploit code, 장비별 침투 절차 없음 | `docs/safety_boundary.md`, `README.md` |
| 제출 부가자료 설명 | 실행 방법, 테스트, ZIP 구성, 산출 파일 | `README.md`, `scripts/build_submission_zip.py`, `tests/test_simulation.py` |
| 팀 결과물 비교 | `GubikoDev` 실행 안정성 + `hbin` 판단 trace 개념을 통합 | `docs/agent_branch_comparison.md` |

## 시스템 구성 설명

보고서에서는 세 개의 구성요소로 설명하면 가장 명확합니다.

### 1. AURA-lite

AURA-lite는 red-team 역할의 공격 효과 생성 에이전트입니다. 실제 공격 코드를 실행하지 않고, simulator 안에서 다음과 같은 추상 mission effect만 발생시킵니다.

- `link_degradation`: SATCOM 링크의 health, loss, jitter를 악화
- `mission_aware_delay`: critical traffic이 밀리는 시점에 지연을 유도
- `failover_chasing`: 방어자가 fallback 링크로 전환하면 해당 링크까지 추적해 회복 안정성을 흔듦
- `hybrid`: 위 세 가지를 phase별로 조합

보고서 표현:

> AURA-lite는 실제 위성망이나 RF 장비를 공격하지 않는다. 대신 폐쇄형 시뮬레이터 내부에서 링크 상태, 큐 혼잡, critical traffic latency에 영향을 주는 추상 공격 효과를 선택한다. 이를 통해 실제 공격 절차를 제공하지 않으면서도 SATCOM disruption이 C4ISR 데이터 신뢰성에 미치는 영향을 정량적으로 평가할 수 있다.

### 2. TSRA-R-lite

TSRA-R-lite는 rule/risk-fusion 기반 방어 에이전트입니다. 링크 상태, 큐 깊이, stale data, critical latency, priority inversion, terminal/source trust pressure를 보고 방어 행동을 선택합니다.

주요 방어 행동:

- `priority_boost`: critical traffic 우선순위 상승
- `minimum_mode`: 위험 상황에서 UAV video 같은 noncritical traffic 압축/지연
- `PACE routing`: SATCOM이 불안정하면 radio/LTE/mesh 중 더 안정적인 경로 선택
- `stale_badge`: stale COP data를 낮은 신뢰도로 표시
- `quarantine flag`: terminal/source trust pressure가 높을 때 격리 플래그 부여

보고서 표현:

> TSRA-R-lite는 단순 탐지기가 아니라 mission impact를 낮추기 위한 대응 정책을 수행한다. 위험 점수가 높거나 SATCOM health가 낮아지면 critical traffic 우선순위를 올리고, 필요 시 minimum mode와 PACE routing을 적용한다. 또한 stale data를 그대로 신뢰하지 않도록 stale badge를 부여해 C4ISR 상황도 공유의 신뢰성을 보전한다.

### 3. TSRA-ML

TSRA-ML은 scikit-learn 기반 trained policy를 사용하는 방어 에이전트입니다. `models/tsra_sklearn_policy.joblib`에 훈련된 모델이 포함되어 있고, fallback logistic model도 유지됩니다.

주의할 점:

- TSRA-ML은 TSRA-R보다 수치가 더 좋아졌다고 과장하면 안 됩니다.
- 현재 5-seed 기준 TSRA-R과 TSRA-ML의 mission impact는 동일하게 `15.306`입니다.
- 따라서 “ML이 더 강하다”가 아니라 “ML 기반 risk estimate와 deterministic guardrail을 결합해 TSRA-R 수준의 안정적 방어 성능을 재현했다”라고 쓰는 편이 안전합니다.

보고서 표현:

> TSRA-ML은 synthetic mission-state feature를 입력으로 위험 확률을 추정하고, 튜닝된 action gate와 deterministic guardrail을 함께 사용한다. 실험상 TSRA-ML은 TSRA-R과 동일한 평균 mission impact 15.306 및 resilience gain 90.374%를 기록했으며, 폐쇄형 synthetic simulator 안에서 TSRA-R 수준의 방어 성능을 재현했다.

## DecisionTrace 설명

이번 통합에서 제출용 설득력이 올라간 핵심은 `DecisionTrace`입니다. 기존에는 “결과가 좋아졌다”가 중심이었다면, 이제는 “에이전트가 어떤 관측을 바탕으로 어떤 후보 행동 중 무엇을 골랐는지”까지 설명할 수 있습니다.

DecisionTrace는 `src/tsra_agent/runtime.py`가 만들고, CLI 실행 시 seed별 폴더에 다음 파일로 저장됩니다.

- `<experiment>_aura_decision_traces.jsonl`
- `<experiment>_tsra_decision_traces.jsonl`

각 trace의 주요 필드:

| 필드 | 의미 | 보고서 활용 |
|---|---|---|
| `observation` | tick, active link, SATCOM health, queue depth, stale ratio 등 관측값 | “에이전트 입력” 설명 |
| `memory` | 최근 관측/판단 수, belief state | “상태 기억 기반 판단” 설명 |
| `tool_calls` | 위험 융합, PACE 선택 등 내부 판단 도구 호출 | “도구 기반 agent loop” 설명 |
| `candidate_actions` | 가능한 공격/방어 후보 행동 | “후보 평가” 설명 |
| `selected_action` | 실제 선택된 action | “최종 판단” 설명 |
| `reason` | 선택 이유 | “설명 가능성” 설명 |
| `feedback` | detection/recovery tick 등 판단 후 상태 | “closed-loop feedback” 설명 |
| `safety_boundary` | 폐쇄형 simulation임을 명시 | “안전성” 설명 |

보고서 표현:

> 각 에이전트 판단은 DecisionTrace로 기록된다. DecisionTrace는 observation, memory, tool call, candidate action, selected action, feedback을 포함하므로, 결과 수치뿐 아니라 에이전트가 왜 특정 공격 효과 또는 방어 행동을 선택했는지도 추적할 수 있다. 이는 AI 에이전트 설계 항목에서 설명 가능성과 감사 가능성을 입증하는 근거로 사용된다.

## 실험 구성

보고서에서는 아래 실험군으로 정리하면 됩니다.

| 실험 이름 | 의미 | 목적 |
|---|---|---|
| `baseline` | 공격 없음, 기본 routing | 정상 임무 기준선 |
| `attacked` | AURA-lite hybrid attack, 방어 없음 | 공격 효과 측정 |
| `rule_defended` | 단순 rule defense | TSRA-R 대비 기준 방어 |
| `defended` | TSRA-R-lite 적용 | 주 방어 성능 측정 |
| `ml_defended` | TSRA-ML 적용 | ML 기반 방어 안정성 측정 |
| `guarded_baseline` | 공격 없음 + TSRA-R 감시 | false alarm 확인 |
| `ml_guarded_baseline` | 공격 없음 + TSRA-ML 감시 | ML false alarm 확인 |

## 핵심 수치

현재 제출 기준 수치는 Git에 포함된 `examples/summary_multi_seed.json`를 canonical 근거로 사용합니다. `outputs/integration_check/summary.json`는 로컬 재실행 검증 산출물이며, 클린 체크아웃에는 포함되지 않습니다.

| 지표 | 값 | 해석 |
|---|---:|---|
| attacked mission impact | `82.162` | 공격 단독 시 임무 영향이 크게 상승 |
| rule defense mission impact | `61.228` | 단순 rule 방어는 일부 완화하나 충분하지 않음 |
| TSRA-R mission impact | `15.306` | TSRA-R 적용 후 영향 크게 감소 |
| TSRA-ML mission impact | `15.306` | ML 방어도 동일 수준의 안정적 완화 |
| attacked priority inversion rate | `0.0629` | 공격 시 critical traffic 우선순위 역전 발생 |
| TSRA-R priority inversion rate | `0.0` | 5개 seed synthetic 실험에서 priority inversion이 관측되지 않음 |
| TSRA-ML priority inversion rate | `0.0` | 5개 seed synthetic 실험에서 priority inversion이 관측되지 않음 |
| TSRA-R detection time | `1 tick` | 최초 공격 후 빠른 탐지 |
| TSRA-R recovery time | `3 ticks` | 경보 안정화 후 회복 |
| TSRA-ML recovery time | `2 ticks` | ML 방어의 빠른 회복 |
| false alarm rate | `0.0` | 5개 seed synthetic guarded-baseline에서 false alarm이 관측되지 않음 |
| resilience gain | `90.374%` | 공격으로 인한 mission impact 대부분 회복 |
| TSRA-ML validation F1 | `0.9956` | synthetic validation 기준 높은 분류 성능 |
| TSRA-ML ROC-AUC | `1.0` | synthetic validation 기준 분리 성능 우수 |

보고서 표현:

> 5개 seed 반복 synthetic 실험에서 AURA-lite 공격 단독 조건의 평균 mission impact는 82.162였다. 단순 rule defense는 이를 61.228로 낮췄지만, TSRA-R 적용 시 15.306까지 감소했다. 이는 baseline-adjusted resilience gain 90.374%에 해당한다. 또한 priority inversion rate는 공격 조건에서 0.0629였으나 TSRA-R/TSRA-ML 적용 조건에서는 0.0으로 관측됐고, no-attack guarded baseline의 false alarm rate도 0.0으로 관측됐다.

## 보고서에 넣을 표 예시

### 실험 결과 요약표

| 조건 | Mission Impact | Priority Inversion | Detection Time | Recovery Time | 해석 |
|---|---:|---:|---:|---:|---|
| Baseline | `8.18` | `0.0` | N/A | N/A | 정상 기준 |
| AURA attacked | `82.162` | `0.0629` | N/A | N/A | 공격 효과 확인 |
| Rule defense | `61.228` | `0.0` | `1` | N/A | 단순 방어는 제한적 |
| TSRA-R | `15.306` | `0.0` | `1` | `3` | 주 방어 성능 |
| TSRA-ML | `15.306` | `0.0` | `1` | `2` | ML+guardrail 안정성 |

### 에이전트 기능표

| 에이전트 | 입력 | 판단 | 출력 | 근거 |
|---|---|---|---|---|
| AURA-lite | link health, active link, queue state, attack phase | hybrid schedule과 mission effect 선택 | abstract attack action | `*_aura_decision_traces.jsonl` |
| TSRA-R-lite | health, stale ratio, critical latency, priority inversion, trust pressure | risk fusion + PACE/action gate | defense action | `*_tsra_decision_traces.jsonl` |
| TSRA-ML | mission-state feature vector | trained risk probability + deterministic guardrail | ML-guided defense action | `models/`, `tests/test_simulation.py` |

## 안전 경계

반드시 아래처럼 써야 합니다.

쓸 수 있는 표현:

- 폐쇄형 synthetic mission-event simulator
- mission effect simulation
- abstract attack action
- C4ISR data trust degradation
- SATCOM disruption scenario modeling
- no exploit code
- no operational RF parameter
- no equipment-specific intrusion step

피해야 할 표현:

- 실제 SATCOM 공격 구현
- 실제 RF jamming 구현
- 실제 장비 침투 절차
- exploit 또는 침투 코드
- 실전 환경에서 검증된 성능

보고서 표현:

> 본 부가자료는 실제 SATCOM, RF, 네트워크 장비를 대상으로 한 공격 도구가 아니다. 모든 공격 효과는 폐쇄형 synthetic simulator 안에서만 발생하며, exploit code, 장비별 침투 절차, 운용 가능한 RF parameter는 포함하지 않는다.

## 재현 명령

Python은 Conda base 환경 기준으로 실행합니다.

주의: 포함된 `models/tsra_sklearn_policy.joblib`는 `scikit-learn 1.9.x` 계열 로드를 기준으로 합니다. 실행 환경은 `requirements.txt`를 설치한 상태로 맞추는 것이 안전합니다.

```bash
conda run -n base python -m unittest discover -s tests -v
```

다중 seed 실험:

```bash
conda run -n base python -m src.tsra_agent.cli \
  --scenario hybrid \
  --ticks 180 \
  --seeds 7,11,19,23,31 \
  --output-dir outputs/report_check
```

제출 ZIP 생성:

```bash
conda run -n base python scripts/build_submission_zip.py
```

최종 제출 전 전체 검증:

```bash
conda run -n base python scripts/verify_submission_state.py --require-dev --require-clean
```

이 검증은 unit test, CLI smoke run, DecisionTrace schema, canonical example metrics, model report metrics, 안전 경계 문구, 제출 ZIP 구성, DEV 브랜치 상태를 함께 확인합니다.

## 산출물 읽는 법

CLI 실행 후 `outputs/report_check` 안에 아래 파일이 생깁니다.

| 파일 | 용도 |
|---|---|
| `summary.json` | seed별/평균 지표 원본 |
| `incident_report.md` | 보고서에 붙일 수 있는 요약 문서 |
| `run_manifest.json` | 실행 산출물과 안전 경계 |
| `seed_<seed>/*_events.jsonl` | 시뮬레이션 이벤트 로그 |
| `seed_<seed>/*_aura_decision_traces.jsonl` | AURA 판단 trace |
| `seed_<seed>/*_tsra_decision_traces.jsonl` | TSRA-R/TSRA-ML 판단 trace |

## 작성 순서 추천

1. 문제 정의: Hybrid SATCOM Disruption이 C4ISR 데이터 신뢰성을 무너뜨리는 시나리오라고 정의한다.
2. 공격 설계: AURA-lite가 실제 공격이 아니라 abstract mission effect를 선택한다고 설명한다.
3. 방어 설계: TSRA-R이 risk fusion, PACE, priority boost, stale badge로 mission impact를 낮춘다고 설명한다.
4. AI 에이전트성: DecisionTrace 기반 observe-memory-tool-candidate-decision-feedback loop를 보여준다.
5. 실험 결과: mission impact, resilience gain, priority inversion, false alarm을 표로 제시한다.
6. 안전 경계: 실제 공격 도구가 아니며 synthetic simulator 한정임을 명확히 쓴다.
7. 부가자료: README, src, docs, models, scripts, examples, tests가 포함된 ZIP을 제출한다고 적는다.

## 최종 보고서용 짧은 요약

아래 문단은 보고서 결론 또는 부가자료 설명에 그대로 사용할 수 있습니다.

> 본 부가자료는 DAH 2026 예선 주제인 Hybrid SATCOM Disruption 기반 C4ISR 데이터 신뢰성 붕괴 시나리오를 폐쇄형 mission-event simulator로 구현한 AI 공방 에이전트 프로토타입이다. AURA-lite는 실제 공격 코드 없이 link degradation, mission-aware delay, failover chasing과 같은 추상 공격 효과를 선택하고, TSRA-R/TSRA-ML은 risk fusion, priority boost, PACE routing, stale badge, minimum mode를 통해 mission impact를 완화한다. 5개 seed 반복 실험에서 공격 단독 mission impact는 평균 82.162였고, TSRA-R/TSRA-ML 적용 후 15.306으로 감소했으며, baseline-adjusted resilience gain은 90.374%였다. 또한 각 에이전트의 판단 과정은 DecisionTrace로 기록되어 관측, 기억, 도구 호출, 후보 행동, 선택 행동, 피드백을 감사할 수 있다. 모든 실험은 synthetic simulator 내부에서만 수행되며 실제 RF parameter, exploit code, 장비별 침투 절차는 포함하지 않는다.
