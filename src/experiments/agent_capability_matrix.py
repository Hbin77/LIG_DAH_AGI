from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_capability_matrix.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_capability_matrix.md")

FIELDNAMES = [
    "capability_id",
    "side",
    "agent_family",
    "capability",
    "runtime_actions",
    "decision_source",
    "trigger_or_selection_logic",
    "evidence_count",
    "evidence_experiments",
    "observed_effect",
    "validation_gate",
    "safety_boundary",
]

SAFETY_BOUNDARY = (
    "closed simulation capability matrix only; no RF, exploit, or live network action"
)

DEFENSE_EXPERIMENTS = {
    "E5_rule_aura_tsra_r": "TSRA-R",
    "E7_ml_aura_ml_tsra_r": "TSRA-R-ML",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def f(row: dict[str, str], column: str) -> float:
    value = row.get(column, "")
    if value in ("", None):
        return 0.0
    return float(value)


def build_rows(root: Path = Path(".")) -> list[dict[str, str]]:
    rows = []
    rows.extend(build_attack_rows(root))
    rows.extend(build_defense_rows(root))
    rows.extend(build_adaptive_rows(root))
    return rows


def build_attack_rows(root: Path) -> list[dict[str, str]]:
    coa_rows = read_csv(root / "outputs/report_tables/aura_coa_cards.csv")
    by_action: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in coa_rows:
        action = row.get("attack_type", "")
        if action:
            by_action[action].append(row)

    output_rows = []
    for idx, action in enumerate(sorted(by_action), start=1):
        group = by_action[action]
        agents = sorted({row.get("agent", "") for row in group if row.get("agent")})
        experiments = sorted({row.get("experiment", "") for row in group if row.get("experiment")})
        targets = sorted({row.get("target_link", "") for row in group if row.get("target_link")})
        max_impact = max(f(row, "expected_mission_impact") for row in group)
        avg_score = sum(f(row, "attack_score") for row in group) / max(len(group), 1)
        reasons = Counter(row.get("selection_reason", "") for row in group if row.get("selection_reason"))
        reason = reasons.most_common(1)[0][0] if reasons else "selected by attack policy"
        gate = "G01/G02" if action in {"queue_pressure", "bandwidth_limit", "stale_cop_induction"} else "G02/G10"
        output_rows.append(
            {
                "capability_id": f"ATK-{idx:02d}",
                "side": "attack",
                "agent_family": ", ".join(agents),
                "capability": action,
                "runtime_actions": "attack_event",
                "decision_source": attack_decision_source(agents),
                "trigger_or_selection_logic": reason,
                "evidence_count": str(len(group)),
                "evidence_experiments": ", ".join(experiments),
                "observed_effect": (
                    f"targets={','.join(targets)}; max_expected_impact={format_float(max_impact)}; "
                    f"avg_attack_score={format_float(avg_score)}"
                ),
                "validation_gate": gate,
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return output_rows


def attack_decision_source(agents: list[str]) -> str:
    base = ["generate_attack_candidates", "estimate_candidate_effect", "estimate_detectability"]
    if any(agent == "AURA-ML" for agent in agents):
        base.append("predict_candidate_impact")
    return ", ".join(base)


def build_defense_rows(root: Path) -> list[dict[str, str]]:
    defense_events: list[tuple[str, str, dict[str, Any]]] = []
    for experiment, agent in DEFENSE_EXPERIMENTS.items():
        path = root / "outputs/experiments" / experiment / "defense_events.jsonl"
        for event in read_jsonl(path):
            defense_events.append((experiment, agent, event))

    by_action: dict[str, list[tuple[str, str, dict[str, Any]]]] = defaultdict(list)
    for item in defense_events:
        action = item[2].get("action", "")
        if action:
            by_action[action].append(item)

    ablation = {
        row["condition"]: row
        for row in read_csv(root / "outputs/batch/tsra_action_ablation_summary.csv")
        if row.get("condition")
    }

    output_rows = []
    for idx, action in enumerate(sorted(by_action), start=1):
        group = by_action[action]
        agents = sorted({agent for _, agent, _ in group})
        experiments = sorted({experiment for experiment, _, _ in group})
        output_rows.append(
            {
                "capability_id": f"DEF-{idx:02d}",
                "side": "defense",
                "agent_family": ", ".join(agents),
                "capability": action,
                "runtime_actions": "defense_events",
                "decision_source": defense_decision_source(action, agents),
                "trigger_or_selection_logic": defense_trigger(action),
                "evidence_count": str(len(group)),
                "evidence_experiments": ", ".join(experiments),
                "observed_effect": defense_observed_effect(action, ablation),
                "validation_gate": defense_gate(action),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return output_rows


def defense_decision_source(action: str, agents: list[str]) -> str:
    if action == "ml_attack_alert":
        return "predict_attack_probability"
    sources = []
    if "TSRA-R" in agents:
        sources.append(
            "TSRA-R: evaluate_defense_conditions"
            + (", select_fallback_link" if action == "pace_switch" else "")
        )
    if "TSRA-R-ML" in agents:
        sources.append(
            "TSRA-R-ML: predict_attack_probability, assess_mission_risk_guard, reactive defense window"
        )
    return "; ".join(sources) if sources else "evaluate_defense_conditions"


def defense_trigger(action: str) -> str:
    triggers = {
        "ml_attack_alert": "detector probability exceeds threshold",
        "priority_reroute": "critical traffic waits behind video or queue pressure",
        "stale_badge": "COP stale ratio exceeds trust threshold",
        "video_throttle": "video load threatens critical traffic capacity",
        "pace_switch": "active link degradation crosses mission threshold",
    }
    return triggers.get(action, "defense policy selected action")


def defense_observed_effect(action: str, ablation: dict[str, dict[str, str]]) -> str:
    if action == "priority_reroute":
        row = ablation.get("no_priority_reroute", {})
        return (
            f"removal_delta_priority_inversion={format_float(f(row, 'delta_priority_inversion_rate_mean'))}; "
            f"removal_delta_impact={format_float(f(row, 'delta_mission_impact_mean'))}"
        )
    if action == "stale_badge":
        row = ablation.get("no_stale_badge", {})
        return (
            f"removal_delta_trusted_stale={format_float(f(row, 'delta_trusted_stale_exposure_mean'))}; "
            f"removal_delta_impact={format_float(f(row, 'delta_mission_impact_mean'))}"
        )
    if action == "video_throttle":
        row = ablation.get("no_video_throttle", {})
        return (
            f"removal_delta_impact={format_float(f(row, 'delta_mission_impact_mean'))}; "
            f"used as optional capacity control"
        )
    if action == "pace_switch":
        row = ablation.get("no_pace_switch", {})
        return (
            f"removal_delta_recovery_instability={format_float(f(row, 'delta_recovery_instability_mean'))}; "
            f"used as bounded fallback path control"
        )
    if action == "ml_attack_alert":
        return "ML detector opens or maintains reactive defense window; validated by E6/E7 separation gate"
    return "observed in defense_events.jsonl"


def defense_gate(action: str) -> str:
    gates = {
        "ml_attack_alert": "G10",
        "priority_reroute": "G03/G04/G06",
        "stale_badge": "G03/G05/G07",
        "video_throttle": "G03/G09",
        "pace_switch": "G03/G04",
    }
    return gates.get(action, "G03/G04")


def build_adaptive_rows(root: Path) -> list[dict[str, str]]:
    adaptive = {
        row["condition"]: row
        for row in read_csv(root / "outputs/batch/adaptive_memory_summary.csv")
        if row.get("condition")
    }
    if not {"full_tsra_r", "adaptive_tsra_r"}.issubset(adaptive):
        return []
    full = adaptive["full_tsra_r"]
    adapted = adaptive["adaptive_tsra_r"]
    impact_improvement = f(full, "mission_impact_mean") - f(adapted, "mission_impact_mean")
    throttle_reduction = f(full, "video_throttle_count_mean") - f(adapted, "video_throttle_count_mean")
    return [
        {
            "capability_id": "DEF-ADAPT-01",
            "side": "defense",
            "agent_family": "TSRA-R-ADAPTIVE",
            "capability": "adaptive_optional_action_gating",
            "runtime_actions": "memory-backed policy gate",
            "decision_source": "AgentMemory, update_adaptive_action_policy",
            "trigger_or_selection_logic": "optional actions require repeated memory evidence before activation",
            "evidence_count": "30 seeds",
            "evidence_experiments": "adaptive_memory_summary",
            "observed_effect": (
                f"mission_impact_improvement={format_float(impact_improvement)}; "
                f"video_throttle_reduction={format_float(throttle_reduction)}"
            ),
            "validation_gate": "G08/G09",
            "safety_boundary": SAFETY_BOUNDARY,
        }
    ]


def format_float(value: float) -> str:
    return f"{value:.6g}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Capability Matrix",
        "",
        "This matrix maps AURA/TSRA-R capabilities to runtime actions and validation evidence.",
        "",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| capability_id | side | agent_family | capability | evidence_count | observed_effect | validation_gate |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["capability_id"]),
                    md(row["side"]),
                    md(row["agent_family"]),
                    md(row["capability"]),
                    md(row["evidence_count"]),
                    md(row["observed_effect"]),
                    md(row["validation_gate"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['capability_id']} {row['capability']}",
                "",
                f"- Side: {row['side']}",
                f"- Agent family: {row['agent_family']}",
                f"- Runtime actions: {row['runtime_actions']}",
                f"- Decision source: {row['decision_source']}",
                f"- Trigger or selection logic: {row['trigger_or_selection_logic']}",
                f"- Evidence count: {row['evidence_count']}",
                f"- Evidence experiments: {row['evidence_experiments']}",
                f"- Observed effect: {row['observed_effect']}",
                f"- Validation gate: {row['validation_gate']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AURA/TSRA-R capability matrix.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} capabilities)")
    print(f"Wrote {args.output_md} ({len(rows)} capabilities)")


if __name__ == "__main__":
    main()
