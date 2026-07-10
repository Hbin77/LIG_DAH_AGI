# DAH 2026 보고서 작성자 가이드

이 문서는 보고서 담당자가 `LIG_DAH_AGI` 결과물을 이해하고 예선 보고서에 바로 반영할 수 있도록 만든 작성 가이드입니다. 핵심 목적은 코드 설명을 길게 반복하는 것이 아니라, **보고서에 써도 되는 주장**, **근거 파일**, **수치**, **안전 경계**, **복붙 가능한 문장**을 한곳에 정리하는 것입니다.

## 한 줄 결론

이 결과물은 실제 SATCOM 공격 도구가 아니라, 폐쇄형 synthetic mission-event simulator 안에서 rule 기반 AURA-lite와 학습 기반 AURA-ML의 공격 효과, TSRA-R/TSRA-ML의 방어 판단을 각각 검증하는 AI 공방 에이전트 프로토타입입니다.

보고서의 핵심 주장은 다음처럼 잡으면 됩니다.

> 본 구현은 Hybrid SATCOM Disruption 상황에서 C4ISR 데이터 신뢰성 붕괴를 모사하고, AURA-lite 공격 에이전트와 TSRA-R/TSRA-ML 방어 에이전트의 판단 및 대응 효과를 폐쇄형 mission-event simulator로 검증한다. 독립 30-seed post-tuning holdout에서 공격 단독 mission impact는 평균 82.3653, TSRA-R은 16.2180, TSRA-ML은 15.3187이었고, TSRA-ML baseline-adjusted resilience gain은 91.0330%였다. 각 에이전트의 판단 과정은 DecisionTrace로 남겨 observation, memory, 실제 tool call, candidate action, selected action, environment feedback을 감사 가능하게 했다.

## 어디에 무엇을 쓰면 되는가

| 보고서 파트 | 써야 할 내용 | 근거 파일 |
|---|---|---|
| 공격 시나리오 | Hybrid SATCOM Disruption으로 인한 지연, 손실, failover chasing, critical traffic 지연 | `docs/architecture.md`, `src/tsra_agent/agents.py`, `src/tsra_agent/simulator.py` |
| 방어 전략 | risk fusion, priority boost, minimum mode, PACE routing, stale badge, quarantine flag | `docs/architecture.md`, `src/tsra_agent/agents.py`, `src/tsra_agent/simulator.py` |
| AI 에이전트 설계 | AURA-lite, AURA-ML, TSRA-R-lite, TSRA-ML의 역할과 판단 loop | `src/tsra_agent/runtime.py`, `docs/agent_engineering_notes.md` |
| 방어 모델 실험 | E1 baseline, E2 attacked, rule defense, TSRA-R, TSRA-ML, false alarm check | `examples/holdout_30_seed_summary.json`, `models/tsra_final_selection_report.json` |
| 공격 모델 실험 | rule/ML/zero-model AURA를 4개 방어 맥락에서 비교 | `models/aura_final_selection_report.json`, `examples/aura_ml_holdout_30_seed_summary.json`, `docs/aura_ml_engineering_record.md` |
| 안전 경계 | 실제 RF, SATCOM 장비 공격, exploit code, 장비별 침투 절차 없음 | `docs/safety_boundary.md`, `README.md` |
| 제출 부가자료 설명 | 실행 방법, 테스트, ZIP 구성, 산출 파일 | `README.md`, `scripts/build_submission_zip.py`, `tests/test_simulation.py` |
| 팀 결과물 비교 | `GubikoDev` 실행 안정성 + `hbin` 판단 trace 개념을 통합 | `docs/agent_branch_comparison.md` |

## 시스템 구성 설명

보고서에서는 네 개의 구성요소로 설명하면 가장 명확합니다.

### 1. AURA-lite

AURA-lite는 red-team 역할의 공격 효과 생성 에이전트입니다. 실제 공격 코드를 실행하지 않고, simulator 안에서 다음과 같은 추상 mission effect만 발생시킵니다.

- `link_degradation`: SATCOM 링크의 health, loss, jitter를 악화
- `mission_aware_delay`: critical traffic이 밀리는 시점에 지연을 유도
- `failover_chasing`: 방어자가 fallback 링크로 전환하면 해당 링크까지 추적해 회복 안정성을 흔듦
- `hybrid`: 위 세 가지를 phase별로 조합

보고서 표현:

> AURA-lite는 실제 위성망이나 RF 장비를 공격하지 않는다. 대신 폐쇄형 시뮬레이터 내부에서 링크 상태, 큐 혼잡, critical traffic latency에 영향을 주는 추상 공격 효과를 선택한다. 이를 통해 실제 공격 절차를 제공하지 않으면서도 SATCOM disruption이 C4ISR 데이터 신뢰성에 미치는 영향을 정량적으로 평가할 수 있다.

### 2. AURA-ML

AURA-ML은 paired simulator rollout에서 후보별 no-op 대비 mission-impact 증가량을 학습한 27-feature ExtraTrees 공격 후보 ranker입니다. defender 내부 alert 상태는 입력에서 제외되며, Hybrid·180 tick 범위에서만 실행됩니다. rule AURA와 같은 `AgentRuntime`과 안전 경계를 사용하며, zero-model ablation과 rule counterfactual을 trace에 함께 남깁니다.

- seed-grouped candidate validation top-1은 `0.736111`, rule ranker는 `0.326389`입니다.
- 독립 30-seed에서 rule defense 대비 평균 `+21.213`, TSRA-R 대비 `+3.0667`, TSRA-ML 대비 `+5.1033` impact point였고 각 bootstrap 95% CI는 0보다 높았습니다.
- 무방어 negative control은 평균 `+0.0373`, CI `[-0.975, 0.919]`로 4000번대 실행 전에 고정한 1.0-point 비열등성 gate를 통과했지만 우월성을 주장하지 않습니다.
- 초기 3000번대 holdout은 무방어 평균 `-0.0017`로 기존 gate에 실패해 폐기 보존했고, 모델·정책을 바꾸지 않은 채 새 4000번대 seed로 최종 gate를 수행했습니다.

보고서 표현:

> AURA-ML은 실제 공격 절차가 아니라 synthetic simulator의 네 가지 추상 공격 후보가 만들 mission-impact 증가량을 예측한다. 독립 holdout의 방어 적용 맥락에서는 rule AURA보다 높은 평균 impact를 보였지만, 무방어 맥락의 신뢰구간은 0을 포함하므로 모든 조건에서 우월하다고 주장하지 않는다.

### 3. TSRA-R-lite

TSRA-R-lite는 rule/risk-fusion 기반 방어 에이전트입니다. 링크 상태, 큐 깊이, stale data, critical latency, priority inversion, terminal/source trust pressure를 보고 방어 행동을 선택합니다.

주요 방어 행동:

- `priority_boost`: critical traffic 우선순위 상승
- `minimum_mode`: 위험 상황에서 UAV video 같은 noncritical traffic 압축/지연
- `PACE routing`: SATCOM이 불안정하면 radio/LTE/mesh 중 더 안정적인 경로 선택
- `stale_badge`: stale COP data를 낮은 신뢰도로 표시
- `quarantine flag`: terminal/source trust pressure가 높을 때 격리 플래그 부여

보고서 표현:

> TSRA-R-lite는 단순 탐지기가 아니라 mission impact를 낮추기 위한 대응 정책을 수행한다. 위험 점수가 높거나 SATCOM health가 낮아지면 critical traffic 우선순위를 올리고, 필요 시 minimum mode와 PACE routing을 적용한다. 또한 stale data를 그대로 신뢰하지 않도록 stale badge를 부여해 C4ISR 상황도 공유의 신뢰성을 보전한다.

### 4. TSRA-ML

TSRA-ML은 scikit-learn 기반 trained policy를 사용하는 방어 에이전트입니다. `models/tsra_sklearn_policy.joblib`에 훈련된 모델이 포함되어 있고, fallback logistic model도 유지됩니다.

주의할 점:

- 독립 30-seed holdout에서 TSRA-ML은 TSRA-R보다 mission impact가 평균 `0.8993` 낮았고 bootstrap 95% CI는 `[0.1500, 1.6387]`입니다.
- 30개 seed 중 `22개`에서는 우세하고 `8개`에서는 열세였으므로 모든 조건에서 우월하다고 표현하면 안 됩니다.
- 정확한 표현은 “이 synthetic simulator와 holdout seed 범위에서 TSRA-ML이 평균적으로 개선됐다”입니다.

보고서 표현:

> TSRA-ML은 12개 synthetic mission-state feature를 입력으로 선제 개입 확률을 추정하고, 튜닝된 action gate와 deterministic guardrail을 함께 사용한다. 독립 30-seed holdout에서 평균 mission impact 15.3187과 resilience gain 91.0330%를 기록했다. TSRA-R 대비 평균 개선은 0.8993 point, 모델 출력을 제거한 ablation 대비 평균 개선은 1.6623 point였다. 단, 이 결과는 실제 운용 환경이 아니라 simulator seed 불확실성에 한정된다.

## DecisionTrace 설명

이번 통합에서 제출용 설득력이 올라간 핵심은 `DecisionTrace`입니다. 기존에는 “결과가 좋아졌다”가 중심이었다면, 이제는 “에이전트가 어떤 관측을 바탕으로 어떤 후보 행동 중 무엇을 골랐는지”까지 설명할 수 있습니다.

DecisionTrace는 `src/tsra_agent/runtime.py`가 만들고, CLI 실행 시 seed별 폴더에 다음 파일로 저장됩니다.

- `<experiment>_aura_decision_traces.jsonl`
- `<experiment>_tsra_decision_traces.jsonl`

JSONL을 직접 열지 않고 표로 확인하려면 CLI 실행 뒤 아래 명령을 사용합니다.

```bash
python scripts/summarize_decision_traces.py \
  --input-dir outputs/final_run \
  --output-csv outputs/final_run/report_tables/decision_trace_summary.csv \
  --output-md outputs/final_run/report_tables/decision_trace_summary.md
```

`decision_trace_summary.md`는 seed, 실험군, tick, agent, 선택 행동, 후보 수, tool call, 판단 이유를 한 표로 제공하므로 보고서의 AI agent 설명 또는 부록 표를 빠르게 작성할 때 사용합니다. 이 파일도 폐쇄형 synthetic simulation 결과를 요약한 것이므로 실제 운용 로그로 표현하면 안 됩니다.

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

방어 모델의 최종 제출 성능 근거는 `examples/holdout_30_seed_summary.json`, 공격 모델의 별도 근거는 `examples/aura_ml_holdout_30_seed_summary.json`입니다. `models/tsra_final_selection_report.json`은 최종 방어 모델 정의와 5-seed 개발 결과, `examples/summary_multi_seed.json`은 로컬 개발·회귀 기준으로 사용합니다. 두 30-seed 실험은 seed와 평가 목적이 다르므로 하나의 실험처럼 합치면 안 됩니다. `outputs/` 아래 파일은 로컬 재실행 산출물이며 클린 체크아웃에는 포함되지 않습니다.

독립 30-seed 제출 기준:

| 지표 | 값 | 해석 |
|---|---:|---|
| attacked mission impact | `82.3653` | 방어 없는 공격 조건 |
| TSRA-R mission impact | `16.2180` | risk fusion + guardrail 결과 |
| TSRA-ML mission impact | `15.3187` | learned model + guardrail 결과 |
| zero-model ablation impact | `16.9810` | 학습 모델 출력을 제거한 대조군 |
| TSRA-ML resilience gain | `91.0330%` | baseline-adjusted holdout 평균 |
| TSRA-R 대비 ML 평균 개선 | `0.8993` | bootstrap 95% CI `[0.1500, 1.6387]` |
| ablation 대비 ML 평균 개선 | `1.6623` | bootstrap 95% CI `[0.7063, 2.7050]` |
| guarded baseline false alarm | `0.0` | 30-seed no-attack 조건 |

AURA-ML 별도 30-seed holdout:

| 비교 맥락 | AURA-ML 평균 개선 | Bootstrap 95% CI | 해석 |
|---|---:|---:|---|
| rule defense | `+21.213` | `[20.0533, 22.3977]` | 방어 적용 맥락에서 유의한 증가 |
| TSRA-R | `+3.0667` | `[2.2703, 3.8340]` | 방어 적용 맥락에서 유의한 증가 |
| TSRA-ML | `+5.1033` | `[4.4097, 5.7633]` | 방어 적용 맥락에서 유의한 증가 |
| no defense | `+0.0373` | `[-0.975, 0.919]` | 1.0-point 비열등성, 우월성 주장 불가 |

아래 표는 최종 모델 선택 과정에서 사용한 5-seed 개발 결과입니다. 최종 제출 성능 주장에는 위 30-seed holdout을 우선 사용합니다.

| 지표 | 값 | 해석 |
|---|---:|---|
| attacked mission impact | `82.162` | 공격 단독 시 임무 영향이 크게 상승 |
| rule defense mission impact | `61.228` | 단순 rule 방어는 일부 완화하나 충분하지 않음 |
| TSRA-R mission impact | `15.306` | TSRA-R 적용 후 영향 크게 감소 |
| TSRA-ML mission impact | `12.926` | trained model + tuned guardrail 결과 |
| zero-model ablation impact | `15.180` | 같은 config에서 learned risk만 제거 |
| attacked priority inversion rate | `0.0629` | 공격 시 critical traffic 우선순위 역전 발생 |
| TSRA-R priority inversion rate | `0.0` | 5개 seed synthetic 실험에서 priority inversion이 관측되지 않음 |
| TSRA-ML priority inversion rate | `0.0` | 5개 seed synthetic 실험에서 priority inversion이 관측되지 않음 |
| TSRA-R detection time | `1 tick` | 최초 공격 후 빠른 탐지 |
| TSRA-R recovery time | `3 ticks` | 경보 안정화 후 회복 |
| TSRA-ML recovery time | `1 tick` | 탐지 후 recovery 판정까지 걸린 개발 실험 평균 |
| false alarm rate | `0.0` | 5개 seed synthetic guarded-baseline에서 false alarm이 관측되지 않음 |
| TSRA-R resilience gain | `90.374%` | 공격으로 인한 mission impact 대부분 회복 |
| TSRA-ML resilience gain | `93.600%` | 5-seed 개발 기준이며 최종 주장은 30-seed 우선 |
| learned-model contribution | `2.254` | TSRA-ML과 zero-model ablation의 impact 차이 |
| TSRA-ML synthetic holdout F1 | `0.9884` | overlap-balanced synthetic oracle 기준 |
| TSRA-ML attacked-trajectory oracle F1 | `0.9972` | 독립 seed simulator trajectory 기준이며 실데이터 정확도가 아님 |

보고서 표현:

> 독립 30-seed post-tuning holdout에서 AURA-lite 공격 단독 조건의 평균 mission impact는 82.3653이었다. TSRA-R은 16.2180, TSRA-ML은 15.3187로 낮췄고 TSRA-ML baseline-adjusted resilience gain은 91.0330%였다. TSRA-ML은 TSRA-R보다 평균 0.8993 point 개선됐지만 30개 seed 중 8개에서는 열세였으며, 이 결과는 synthetic simulator seed 불확실성에 한정된다.

## 보고서에 넣을 표 예시

### 5-seed 개발 결과 요약표

| 조건 | Mission Impact | Priority Inversion | Detection Time | Recovery Time | 해석 |
|---|---:|---:|---:|---:|---|
| Baseline | `8.18` | `0.0` | N/A | N/A | 정상 기준 |
| AURA attacked | `82.162` | `0.0629` | N/A | N/A | 공격 효과 확인 |
| Rule defense | `61.228` | `0.0` | `1` | N/A | 단순 방어는 제한적 |
| TSRA-R | `15.306` | `0.0` | `1` | `3` | 주 방어 성능 |
| TSRA-ML | `12.926` | `0.0` | `1` | `1` | ML+guardrail 선제 대응 |

### 에이전트 기능표

| 에이전트 | 입력 | 판단 | 출력 | 근거 |
|---|---|---|---|---|
| AURA-lite | link health, active link, queue state, attack phase | hybrid schedule과 mission effect 선택 | abstract attack action | `*_aura_decision_traces.jsonl` |
| AURA-ML | 27-feature observable mission/candidate vector | learned rollout impact + commitment guardrail | ML-ranked abstract attack action | `examples/aura_ml_holdout_30_seed_summary.json` |
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
- AURA-ML은 방어 적용 holdout 맥락에서 평균 개선

피해야 할 표현:

- 실제 SATCOM 공격 구현
- 실제 RF jamming 구현
- 실제 장비 침투 절차
- exploit 또는 침투 코드
- 실전 환경에서 검증된 성능
- AURA-ML이 모든 조건에서 rule AURA보다 우월

보고서 표현:

> 본 부가자료는 실제 SATCOM, RF, 네트워크 장비를 대상으로 한 공격 도구가 아니다. 모든 공격 효과는 폐쇄형 synthetic simulator 안에서만 발생하며, exploit code, 장비별 침투 절차, 운용 가능한 RF parameter는 포함하지 않는다.

## 재현 명령

Python은 Conda base 환경 기준으로 실행합니다.

주의: 포함된 `models/aura_rollout_policy.joblib`과 `models/tsra_sklearn_policy.joblib`는 `scikit-learn 1.9.x` 계열 로드를 기준으로 합니다. 실행 환경은 `requirements.txt`를 설치한 상태로 맞추는 것이 안전합니다.

```bash
python -m unittest discover -s tests -v
```

다중 seed 실험:

```bash
python -m src.tsra_agent.cli \
  --scenario hybrid \
  --ticks 180 \
  --seeds 7,11,19,23,31 \
  --output-dir outputs/report_check
```

제출 ZIP 생성:

```bash
python scripts/build_submission_zip.py
```

주의: `dist/*.zip`는 생성 산출물입니다. GitHub에 남아 있는 오래된 ZIP을 제출 대상으로 삼지 말고, 최종 검증 직전에 새로 생성된 ZIP을 사용해야 합니다.

최종 제출 전 전체 검증:

```bash
python scripts/verify_submission_state.py --require-dev --require-clean
```

이 검증은 unit test, CLI smoke run, DecisionTrace schema, canonical example/model 해시와 acceptance, 안전 경계 문구, 제출 ZIP 구성, DEV 브랜치 상태를 함께 확인합니다. 전체 30-seed holdout을 매번 재실행하는 명령은 아닙니다.

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
2. 공격 설계: AURA-lite와 AURA-ML이 실제 공격이 아니라 abstract mission effect를 선택한다고 설명한다.
3. 공격 모델 근거: AURA-ML의 방어 적용 holdout 개선과 무방어 조건의 비유의 결과를 함께 제시한다.
4. 방어 설계: TSRA-R이 risk fusion, PACE, priority boost, stale badge로 mission impact를 낮춘다고 설명한다.
5. AI 에이전트성: DecisionTrace 기반 observe-memory-tool-candidate-decision-feedback loop를 보여준다.
6. 실험 결과: mission impact, resilience gain, priority inversion, false alarm을 표로 제시한다.
7. 안전 경계: 실제 공격 도구가 아니며 synthetic simulator 한정임을 명확히 쓴다.
8. 부가자료: README, src, docs, models, scripts, examples, tests가 포함된 ZIP을 제출한다고 적는다.

## 최종 보고서용 짧은 요약

아래 문단은 보고서 결론 또는 부가자료 설명에 그대로 사용할 수 있습니다.

> 본 부가자료는 DAH 2026 예선 주제인 Hybrid SATCOM Disruption 기반 C4ISR 데이터 신뢰성 붕괴 시나리오를 폐쇄형 mission-event simulator로 구현한 AI 공방 에이전트 프로토타입이다. AURA-lite는 rule 기반으로, AURA-ML은 learned rollout impact를 이용해 link degradation, mission-aware delay, failover chasing 같은 추상 공격 효과를 선택한다. 별도 30-seed 공격 holdout에서 AURA-ML은 rule/TSRA-R/TSRA-ML 방어 맥락의 rule AURA보다 평균 impact가 높았지만, 무방어 비교의 신뢰구간은 0을 포함했다. 방어 30-seed holdout에서는 공격 단독 mission impact 82.3653, TSRA-R 16.2180, TSRA-ML 15.3187과 TSRA-ML resilience gain 91.0330%를 기록했다. 각 판단은 DecisionTrace로 기록되며 모든 실험은 synthetic simulator 내부로 한정되고 실제 RF parameter, exploit code, 장비별 침투 절차는 포함하지 않는다.
