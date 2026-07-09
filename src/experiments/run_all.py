from __future__ import annotations

import csv
from pathlib import Path

from src.aura.ml_impact_predictor import MLAURA
from src.aura.rule_decision_engine import RuleAURA
from src.experiments.report_assets import (
    write_architecture_diagram,
    write_event_table,
    write_ml_comparison,
    write_summary_figures,
    write_timeline_figures,
)
from src.simulator.mission_simulator import MissionSimulator, fixed_attack_event
from src.tsra_r.ml_defender import MLTSRAR
from src.tsra_r.rule_defender import RuleTSRAR


OUTPUT_ROOT = Path("outputs/experiments")


def run_experiment(
    name: str,
    seed: int,
    aura=None,
    defender=None,
    fixed_attacks=None,
    output_root: Path = OUTPUT_ROOT,
) -> dict[str, float | str]:
    sim = MissionSimulator(
        duration_sec=300,
        seed=seed,
        output_dir=output_root / name,
    )
    summary = sim.run(aura=aura, defender=defender, fixed_attacks=fixed_attacks)
    row: dict[str, float | str] = {"experiment": name}
    row.update(summary)
    return row


def build_experiments(seed: int):
    experiments = [
        ("E1_baseline", seed, None, None, None),
        ("E2_fixed_attack", seed, None, None, [fixed_attack_event()]),
        ("E3_rule_aura", seed, RuleAURA(), None, None),
        ("E4_rule_aura_basic_defense", seed, RuleAURA(), RuleTSRAR(mode="basic"), None),
        ("E5_rule_aura_tsra_r", seed, RuleAURA(), RuleTSRAR(mode="full"), None),
    ]
    model_path = Path("outputs/models/aura_impact_model.pkl")
    if model_path.exists():
        experiments.append(
            ("E6_ml_aura_tsra_r", seed, MLAURA(model_path=model_path), RuleTSRAR(mode="full"), None)
        )
    detector_path = Path("outputs/models/tsra_detector.pkl")
    if model_path.exists() and detector_path.exists():
        experiments.append(
            ("E7_ml_aura_ml_tsra_r", seed, MLAURA(model_path=model_path), MLTSRAR(detector_path), None)
        )
    return experiments


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    seed = 2026
    experiments = build_experiments(seed)

    rows = []
    for name, seed, aura, defender, fixed_attacks in experiments:
        rows.append(run_experiment(name, seed, aura, defender, fixed_attacks))

    summary_path = OUTPUT_ROOT / "experiment_summary.csv"
    fieldnames = list(rows[0].keys())
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    write_summary_figures(summary_path)
    write_timeline_figures(OUTPUT_ROOT, ["E3_rule_aura", "E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"])
    write_event_table(OUTPUT_ROOT, "E5_rule_aura_tsra_r")
    write_architecture_diagram()
    write_ml_comparison()

    print(f"Wrote {summary_path}")
    for row in rows:
        print(
            f"{row['experiment']}: impact={float(row['mission_impact']):.3f}, "
            f"p95={float(row['p95_critical_latency_sec']):.2f}s, "
            f"stale={float(row['stale_data_ratio']):.2f}, "
            f"trusted_stale={float(row['trusted_stale_exposure']):.2f}, "
            f"inv={float(row['priority_inversion_rate']):.2f}"
        )


if __name__ == "__main__":
    main()
