from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.aura.rule_decision_engine import RuleAURA
from src.experiments.run_all import run_experiment
from src.tsra_r.rule_defender import RuleTSRAR


BATCH_ROOT = Path("outputs/batch")
RAW_PATH = BATCH_ROOT / "tsra_action_ablation_raw.csv"
SUMMARY_PATH = BATCH_ROOT / "tsra_action_ablation_summary.csv"
FIGURE_PATH = Path("outputs/figures/tsra_action_ablation.png")
TEMP_ROOT = Path("outputs/tmp_tsra_ablation")

ACTION_SET = {"priority_reroute", "video_throttle", "stale_badge", "pace_switch"}
CONDITIONS = [
    ("full", None),
    ("no_priority_reroute", ACTION_SET - {"priority_reroute"}),
    ("no_video_throttle", ACTION_SET - {"video_throttle"}),
    ("no_stale_badge", ACTION_SET - {"stale_badge"}),
    ("no_pace_switch", ACTION_SET - {"pace_switch"}),
]
METRIC_COLS = [
    "mission_impact",
    "p95_critical_latency_sec",
    "trusted_stale_exposure",
    "priority_inversion_rate",
    "kill_chain_delay_sec",
    "recovery_instability",
    "delivered_count",
    "critical_delivered_count",
    "defense_count",
]


def run_tsra_ablation(start_seed: int = 2026, runs: int = 30) -> None:
    rows: list[dict[str, Any]] = []
    BATCH_ROOT.mkdir(parents=True, exist_ok=True)

    for offset in range(runs):
        seed = start_seed + offset
        output_root = TEMP_ROOT / f"seed_{seed}"
        for condition, enabled_actions in CONDITIONS:
            row = run_experiment(
                name=f"tsra_ablation_{condition}",
                seed=seed,
                aura=RuleAURA(),
                defender=RuleTSRAR(mode="full", enabled_actions=enabled_actions),
                fixed_attacks=None,
                output_root=output_root,
            )
            row["seed"] = seed
            row["condition"] = condition
            row["disabled_action"] = disabled_action(condition)
            rows.append(row)

    write_raw(rows)
    summary = summarize(rows)
    summary.to_csv(SUMMARY_PATH, index=False)
    write_figure(summary)

    print(f"Wrote {RAW_PATH}")
    print(f"Wrote {SUMMARY_PATH}")
    print(f"Wrote {FIGURE_PATH}")
    print(
        summary[
            [
                "condition",
                "mission_impact_mean",
                "delta_mission_impact_mean",
                "trusted_stale_exposure_mean",
                "delta_trusted_stale_exposure_mean",
                "priority_inversion_rate_mean",
                "delta_priority_inversion_rate_mean",
            ]
        ].to_string(index=False)
    )


def write_raw(rows: list[dict[str, Any]]) -> None:
    fieldnames = ["seed", "condition", "disabled_action"] + [
        key for key in rows[0] if key not in {"seed", "condition", "disabled_action"}
    ]
    with RAW_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    for metric in METRIC_COLS:
        df[metric] = df[metric].astype(float)

    full_by_seed = (
        df[df["condition"] == "full"]
        .set_index("seed")[METRIC_COLS]
        .rename(columns={metric: f"full_{metric}" for metric in METRIC_COLS})
    )
    df = df.join(full_by_seed, on="seed")
    for metric in METRIC_COLS:
        df[f"delta_{metric}"] = df[metric] - df[f"full_{metric}"]

    aggregate_cols = METRIC_COLS + [f"delta_{metric}" for metric in METRIC_COLS]
    summary = (
        df.groupby(["condition", "disabled_action"], dropna=False)[aggregate_cols]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary.columns = [
        col[0] if col[1] == "" else f"{col[0]}_{col[1]}"
        for col in summary.columns.to_flat_index()
    ]
    summary["condition_order"] = summary["condition"].map(
        {condition: idx for idx, (condition, _) in enumerate(CONDITIONS)}
    )
    return summary.sort_values("condition_order").drop(columns=["condition_order"])


def write_figure(summary: pd.DataFrame) -> None:
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    labels = summary["condition"].tolist()
    specs = [
        ("mission_impact", "Mission Impact", "lower is better"),
        ("trusted_stale_exposure", "Trusted Stale Exposure", "lower is better"),
        ("priority_inversion_rate", "Priority Inversion", "lower is better"),
        ("p95_critical_latency_sec", "P95 Critical Latency", "seconds"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for ax, (metric, title, ylabel) in zip(axes.flatten(), specs):
        ax.bar(
            labels,
            summary[f"{metric}_mean"],
            yerr=summary[f"{metric}_std"],
            capsize=4,
        )
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", labelrotation=25)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment("right")
    fig.suptitle("TSRA-R Action Ablation")
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=160)
    plt.close(fig)


def disabled_action(condition: str) -> str:
    if condition == "full":
        return "none"
    return condition.removeprefix("no_")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TSRA-R action ablation experiments.")
    parser.add_argument("--start-seed", type=int, default=2026)
    parser.add_argument("--runs", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_tsra_ablation(start_seed=args.start_seed, runs=args.runs)


if __name__ == "__main__":
    main()
