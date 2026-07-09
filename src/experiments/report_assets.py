from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


FIGURE_DIR = Path("outputs/figures")
REPORT_TABLE_DIR = Path("outputs/report_tables")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_summary_figures(summary_path: Path) -> None:
    df = pd.read_csv(summary_path)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    chart_specs = [
        ("mission_impact", "Mission Impact Score", "mission_impact.png"),
        ("p95_critical_latency_sec", "P95 Critical Latency (sec)", "critical_latency.png"),
        ("priority_inversion_rate", "Priority Inversion Rate", "priority_inversion.png"),
        ("stale_data_ratio", "Raw Stale Data Ratio", "stale_data_ratio.png"),
        ("trusted_stale_exposure", "Trusted Stale Exposure", "trusted_stale_exposure.png"),
    ]
    for column, title, filename in chart_specs:
        if column not in df:
            continue
        plt.figure(figsize=(10, 4.8))
        plt.bar(df["experiment"], df[column])
        plt.title(title)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(FIGURE_DIR / filename, dpi=160)
        plt.close()


def write_timeline_figures(experiment_root: Path, experiments: list[str]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    for experiment in experiments:
        exp_dir = experiment_root / experiment
        metrics_path = exp_dir / "metric_snapshots.jsonl"
        if not metrics_path.exists():
            continue
        metrics = pd.DataFrame(_read_jsonl(metrics_path))
        if metrics.empty:
            continue
        attacks = _read_jsonl(exp_dir / "attack_events.jsonl")
        defenses = _read_jsonl(exp_dir / "defense_events.jsonl")

        fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
        series = [
            ("mission_impact", "Mission Impact"),
            ("p95_critical_latency_sec", "P95 Critical Latency"),
            ("priority_inversion_rate", "Priority Inversion"),
            ("trusted_stale_exposure", "Trusted Stale Exposure"),
        ]
        for ax, (column, label) in zip(axes, series, strict=False):
            if column in metrics:
                ax.plot(metrics["time_sec"], metrics[column], linewidth=2)
            ax.set_ylabel(label)
            ax.grid(True, alpha=0.25)
            for attack in attacks:
                ax.axvline(float(attack.get("selected_at", 0)), color="#c43c35", alpha=0.25)
            for defense in defenses:
                ax.axvline(float(defense.get("time_sec", 0)), color="#2f6fc2", alpha=0.15)
        axes[0].set_title(f"{experiment}: AURA attack and TSRA-R defense timeline")
        axes[-1].set_xlabel("Time (sec)")
        fig.tight_layout()
        fig.savefig(FIGURE_DIR / f"{experiment}_timeline.png", dpi=160)
        plt.close(fig)


def write_event_table(experiment_root: Path, experiment: str) -> None:
    REPORT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    exp_dir = experiment_root / experiment
    rows: list[dict[str, Any]] = []
    for attack in _read_jsonl(exp_dir / "attack_events.jsonl"):
        candidate = attack.get("candidate", {})
        expected = attack.get("expected_impact", {})
        rows.append(
            {
                "time_sec": float(attack.get("selected_at", 0)),
                "side": "AURA",
                "action": candidate.get("attack_type", ""),
                "target": candidate.get("target_link", ""),
                "reason": attack.get("reason", ""),
                "expected_or_observed": f"expected impact={expected.get('mission_impact', '')}",
            }
        )
    for defense in _read_jsonl(exp_dir / "defense_events.jsonl"):
        details = defense.get("details", {})
        rows.append(
            {
                "time_sec": float(defense.get("time_sec", 0)),
                "side": "TSRA-R",
                "action": defense.get("action", ""),
                "target": details.get("target_link", ""),
                "reason": details.get("reason", ""),
                "expected_or_observed": f"until={details.get('until_sec', '')}",
            }
        )
    rows = sorted(rows, key=lambda row: row["time_sec"])
    csv_path = REPORT_TABLE_DIR / f"{experiment}_event_timeline.csv"
    md_path = REPORT_TABLE_DIR / f"{experiment}_event_timeline.md"
    fieldnames = ["time_sec", "side", "action", "target", "reason", "expected_or_observed"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    with md_path.open("w", encoding="utf-8") as f:
        f.write("| time_sec | side | action | target | reason | expected_or_observed |\n")
        f.write("|---:|---|---|---|---|---|\n")
        for row in rows:
            f.write(
                f"| {row['time_sec']:.0f} | {row['side']} | {row['action']} | "
                f"{row['target']} | {row['reason']} | {row['expected_or_observed']} |\n"
            )


def write_architecture_diagram() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axis("off")
    boxes = {
        "AURA\nAttack Agent": (0.08, 0.65),
        "Attack Event\nJSONL": (0.29, 0.65),
        "Mission SATCOM\nSimulator": (0.50, 0.65),
        "Telemetry / Queue /\nCOP Metrics": (0.50, 0.34),
        "TSRA-R\nDefense Agent": (0.72, 0.34),
        "Defense Event\nJSONL": (0.72, 0.65),
        "Mission Impact\nScore": (0.29, 0.34),
    }
    for label, (x, y) in boxes.items():
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=12,
            bbox={"boxstyle": "round,pad=0.45", "fc": "#f7f9fb", "ec": "#3d5266"},
        )
    arrows = [
        ("AURA\nAttack Agent", "Attack Event\nJSONL"),
        ("Attack Event\nJSONL", "Mission SATCOM\nSimulator"),
        ("Mission SATCOM\nSimulator", "Telemetry / Queue /\nCOP Metrics"),
        ("Telemetry / Queue /\nCOP Metrics", "TSRA-R\nDefense Agent"),
        ("TSRA-R\nDefense Agent", "Defense Event\nJSONL"),
        ("Defense Event\nJSONL", "Mission SATCOM\nSimulator"),
        ("Telemetry / Queue /\nCOP Metrics", "Mission Impact\nScore"),
        ("Mission Impact\nScore", "AURA\nAttack Agent"),
    ]
    for src, dst in arrows:
        x1, y1 = boxes[src]
        x2, y2 = boxes[dst]
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "#546a7b"},
        )
    ax.set_title("AURA-TSRA-R Closed Simulation Architecture", fontsize=15, pad=20)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "aura_tsra_architecture.png", dpi=160)
    plt.close(fig)


def write_ml_comparison() -> None:
    REPORT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    aura_path = Path("outputs/models/aura_impact_model_metrics.json")
    if aura_path.exists():
        metrics = json.loads(aura_path.read_text(encoding="utf-8"))
        for model, values in metrics.get("models", {}).items():
            rows.append(
                {
                    "task": "AURA impact regression",
                    "model": model,
                    "mae": values.get("mae", ""),
                    "r2_or_f1": values.get("r2", ""),
                    "top1_or_precision": values.get("top1_action_match_rate", ""),
                }
            )
    tsra_path = Path("outputs/models/tsra_detector_metrics.json")
    if tsra_path.exists():
        metrics = json.loads(tsra_path.read_text(encoding="utf-8"))
        for model, values in metrics.get("models", {}).items():
            rows.append(
                {
                    "task": "TSRA-R anomaly detection",
                    "model": model,
                    "mae": "",
                    "r2_or_f1": values.get("f1", ""),
                    "top1_or_precision": values.get("precision", ""),
                }
            )
    gpu_path = Path("outputs/models/aura_mps_mlp_metrics.json")
    if gpu_path.exists():
        values = json.loads(gpu_path.read_text(encoding="utf-8"))
        rows.append(
            {
                "task": "AURA GPU-scale MPS regression",
                "model": "PyTorch MPS MLP",
                "mae": values.get("mae", ""),
                "r2_or_f1": values.get("r2", ""),
                "top1_or_precision": values.get("top1_action_match_rate", ""),
            }
        )
    csv_path = REPORT_TABLE_DIR / "ml_model_comparison.csv"
    md_path = REPORT_TABLE_DIR / "ml_model_comparison.md"
    fieldnames = ["task", "model", "mae", "r2_or_f1", "top1_or_precision"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    with md_path.open("w", encoding="utf-8") as f:
        f.write("| task | model | MAE | R2/F1 | Top-1/Precision |\n")
        f.write("|---|---|---:|---:|---:|\n")
        for row in rows:
            f.write(
                f"| {row['task']} | {row['model']} | {row['mae']} | "
                f"{row['r2_or_f1']} | {row['top1_or_precision']} |\n"
            )

