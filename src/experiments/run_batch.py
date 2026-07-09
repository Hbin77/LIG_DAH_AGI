from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.experiments.run_all import build_experiments, run_experiment


BATCH_ROOT = Path("outputs/batch")
RAW_PATH = BATCH_ROOT / "repeated_experiment_raw.csv"
SUMMARY_PATH = BATCH_ROOT / "repeated_experiment_summary.csv"
RESILIENCE_PATH = BATCH_ROOT / "resilience_gain_summary.csv"


def run_batch(start_seed: int = 2026, runs: int = 30) -> None:
    BATCH_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for offset in range(runs):
        seed = start_seed + offset
        output_root = BATCH_ROOT / f"seed_{seed}"
        for name, exp_seed, aura, defender, fixed_attacks in build_experiments(seed):
            row = run_experiment(name, exp_seed, aura, defender, fixed_attacks, output_root=output_root)
            row["seed"] = seed
            rows.append(row)

    fieldnames = ["seed"] + [key for key in rows[0] if key != "seed"]
    with RAW_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    df = pd.DataFrame(rows)
    metric_cols = [
        "mission_impact",
        "p95_critical_latency_sec",
        "stale_data_ratio",
        "trusted_stale_exposure",
        "priority_inversion_rate",
        "kill_chain_delay_sec",
        "recovery_instability",
        "delivered_count",
        "dropped_count",
        "critical_delivered_count",
    ]
    summary = (
        df.groupby("experiment")[metric_cols]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary.columns = [
        col[0] if col[1] == "" else f"{col[0]}_{col[1]}"
        for col in summary.columns.to_flat_index()
    ]
    summary.to_csv(SUMMARY_PATH, index=False)

    resilience_rows = []
    for seed, group in df.groupby("seed"):
        attack = group[group["experiment"] == "E3_rule_aura"]
        if attack.empty:
            continue
        attack_impact = float(attack.iloc[0]["mission_impact"])
        for _, row in group.iterrows():
            if not str(row["experiment"]).startswith(("E4", "E5", "E6", "E7")):
                continue
            gain = (attack_impact - float(row["mission_impact"])) / attack_impact
            resilience_rows.append(
                {
                    "seed": seed,
                    "experiment": row["experiment"],
                    "aura_attack_impact": attack_impact,
                    "defended_impact": row["mission_impact"],
                    "resilience_gain": gain,
                }
            )
    resilience_df = pd.DataFrame(resilience_rows)
    resilience_summary = (
        resilience_df.groupby("experiment")["resilience_gain"]
        .agg(["mean", "std"])
        .reset_index()
    )
    resilience_summary.to_csv(RESILIENCE_PATH, index=False)
    _write_batch_figures(summary, resilience_summary)

    print(f"Wrote {RAW_PATH}")
    print(f"Wrote {SUMMARY_PATH}")
    print(f"Wrote {RESILIENCE_PATH}")
    print(summary[["experiment", "mission_impact_mean", "mission_impact_std"]].to_string(index=False))
    print(resilience_summary.to_string(index=False))


def _write_batch_figures(summary: pd.DataFrame, resilience_summary: pd.DataFrame) -> None:
    figure_dir = Path("outputs/figures")
    figure_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("mission_impact", "Mission Impact Mean +- Std", "batch_mission_impact_errorbar.png"),
        ("p95_critical_latency_sec", "P95 Critical Latency Mean +- Std", "batch_critical_latency_errorbar.png"),
        ("trusted_stale_exposure", "Trusted Stale Exposure Mean +- Std", "batch_trusted_stale_errorbar.png"),
        ("priority_inversion_rate", "Priority Inversion Mean +- Std", "batch_priority_inversion_errorbar.png"),
    ]
    for metric, title, filename in specs:
        plt.figure(figsize=(11, 5))
        plt.bar(summary["experiment"], summary[f"{metric}_mean"], yerr=summary[f"{metric}_std"], capsize=4)
        plt.title(title)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(figure_dir / filename, dpi=160)
        plt.close()

    plt.figure(figsize=(9, 4.8))
    plt.bar(
        resilience_summary["experiment"],
        resilience_summary["mean"],
        yerr=resilience_summary["std"],
        capsize=4,
    )
    plt.title("Resilience Gain vs AURA Attack")
    plt.ylabel("Gain")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(figure_dir / "batch_resilience_gain.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    run_batch()

