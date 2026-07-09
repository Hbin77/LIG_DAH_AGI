# ML Attack Decision Path Audit

This audit traces the E7 AURA-ML path from startup no-op to candidate scoring, selected attack events, cadence gates, and closed-loop feedback.
Safety boundary: closed simulation ML attack decision-path audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| MAP01 | Pre-start no-op gate | pass | trace_count=31; first_attack_time=60; pre_start_traces=6; pre_start_noop_count=6; pre_start_attack_events=0 | The attack agent waits for mission context instead of emitting simulated attack effects immediately at startup. |
| MAP02 | Candidate scoring toolchain | pass | attack_traces=5; candidate_total=27; generate_attack_candidates=5; predict_candidate_impact=27; estimate_candidate_effect=27; estimate_detectability=27; tool_errors=0 | AURA-ML uses a real tool path for selection: candidate generation, ML prediction, effect estimation, and detectability scoring all appear in DecisionTrace. |
| MAP03 | Top-score selection link | pass | attack_traces=5; attack_events=5; selected_matches_top_candidate=5; score_event_matches=5; time_event_matches=5; threshold_passes=5; attack_threshold=0.12 | The chosen attack is not hand-picked after the fact; it is the top candidate in the trace and is linked to the attack event log. |
| MAP04 | Detectability-adjusted score | pass | candidate_total=27; score_formula_matches=27; selected_detectability_min=0.15; selected_detectability_max=0.5 | The attack score balances mission effect and detectability instead of maximizing impact blindly. |
| MAP05 | Cadence and event budget gate | pass | attack_events=5; cooldown_noops=16; max_event_noops=4; min_attack_gap_sec=50; attacks_after_budget=0 | AURA-ML is an agent with cadence memory and an event budget, not a loop that fires every time step. |
| MAP06 | Closed-loop attack feedback | pass | attack_types=failover_chasing,queue_pressure; target_links=LTE,MESH,SATCOM; scorecard_rows=5; scorecard_attack_links=5; complete_responses=5; positive_reductions=5; scorecard_passes=5 | The ML attack path reaches closed-loop evidence: selected attacks vary by tactic and link, then receive complete defense and metric feedback. |

## Detail

### MAP01 Pre-start no-op gate

- Requirement: AURA-ML should not generate candidates or attack events before the configured start time.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/aura_decision_traces.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl
- Observed: trace_count=31; first_attack_time=60; pre_start_traces=6; pre_start_noop_count=6; pre_start_attack_events=0
- Status: pass
- Interpretation: The attack agent waits for mission context instead of emitting simulated attack effects immediately at startup.
- Safety boundary: closed simulation ML attack decision-path audit only; no RF, exploit, or live network action

### MAP02 Candidate scoring toolchain

- Requirement: Every selected attack decision should generate candidates and evaluate each candidate through ML impact, analytic effect, and detectability tools.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/aura_decision_traces.jsonl
- Observed: attack_traces=5; candidate_total=27; generate_attack_candidates=5; predict_candidate_impact=27; estimate_candidate_effect=27; estimate_detectability=27; tool_errors=0
- Status: pass
- Interpretation: AURA-ML uses a real tool path for selection: candidate generation, ML prediction, effect estimation, and detectability scoring all appear in DecisionTrace.
- Safety boundary: closed simulation ML attack decision-path audit only; no RF, exploit, or live network action

### MAP03 Top-score selection link

- Requirement: Selected attack events must match the highest scored candidate and the persisted attack event log.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/aura_decision_traces.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl
- Observed: attack_traces=5; attack_events=5; selected_matches_top_candidate=5; score_event_matches=5; time_event_matches=5; threshold_passes=5; attack_threshold=0.12
- Status: pass
- Interpretation: The chosen attack is not hand-picked after the fact; it is the top candidate in the trace and is linked to the attack event log.
- Safety boundary: closed simulation ML attack decision-path audit only; no RF, exploit, or live network action

### MAP04 Detectability-adjusted score

- Requirement: Candidate score must equal predicted mission impact minus the configured detectability penalty.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/aura_decision_traces.jsonl | src/shared/metrics.py
- Observed: candidate_total=27; score_formula_matches=27; selected_detectability_min=0.15; selected_detectability_max=0.5
- Status: pass
- Interpretation: The attack score balances mission effect and detectability instead of maximizing impact blindly.
- Safety boundary: closed simulation ML attack decision-path audit only; no RF, exploit, or live network action

### MAP05 Cadence and event budget gate

- Requirement: AURA-ML should respect cooldown and max-event memory gates between attack events.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/aura_decision_traces.jsonl | outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl
- Observed: attack_events=5; cooldown_noops=16; max_event_noops=4; min_attack_gap_sec=50; attacks_after_budget=0
- Status: pass
- Interpretation: AURA-ML is an agent with cadence memory and an event budget, not a loop that fires every time step.
- Safety boundary: closed simulation ML attack decision-path audit only; no RF, exploit, or live network action

### MAP06 Closed-loop attack feedback

- Requirement: Selected AURA-ML attack events should cover multiple tactics and connect to complete closed-loop feedback.
- Evidence: outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl | outputs/report_tables/agent_engagement_scorecard.csv
- Observed: attack_types=failover_chasing,queue_pressure; target_links=LTE,MESH,SATCOM; scorecard_rows=5; scorecard_attack_links=5; complete_responses=5; positive_reductions=5; scorecard_passes=5
- Status: pass
- Interpretation: The ML attack path reaches closed-loop evidence: selected attacks vary by tactic and link, then receive complete defense and metric feedback.
- Safety boundary: closed simulation ML attack decision-path audit only; no RF, exploit, or live network action
