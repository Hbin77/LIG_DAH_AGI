from __future__ import annotations

import argparse
import csv
from pathlib import Path

from src.shared.metrics import normalize_metric_values


DEFAULT_INPUT = Path("outputs/batch/repeated_experiment_summary.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/mission_impact_decomposition.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/mission_impact_decomposition.md")

SAFETY_BOUNDARY = (
    "closed simulation metric decomposition only; no RF, exploit, or live network action"
)

COMPONENTS = [
    (
        "critical_latency",
        "p95_critical_latency_sec_mean",
        "critical_latency_score",
        0.35,
        "critical message latency pressure",
    ),
    (
        "trusted_stale_exposure",
        "trusted_stale_exposure_mean",
        "stale_data_score",
        0.25,
        "stale COP still trusted after defense annotations",
    ),
    (
        "priority_inversion",
        "priority_inversion_rate_mean",
        "priority_inversion_score",
        0.20,
        "critical traffic waiting behind lower-priority load",
    ),
    (
        "kill_chain_delay",
        "kill_chain_delay_sec_mean",
        "kill_chain_delay_score",
        0.15,
        "mission execution delay",
    ),
    (
        "recovery_instability",
        "recovery_instability_mean",
        "recovery_instability_score",
        0.05,
        "PACE recovery churn and switching instability",
    ),
]

FIELDNAMES = [
    "experiment",
    "component",
    "raw_metric_mean",
    "normalized_score",
    "weight",
    "weighted_contribution",
    "reported_mission_impact_mean",
    "reconstructed_mission_impact_from_means",
    "reconstruction_delta",
    "share_of_reconstructed_impact",
    "interpretation",
    "safety_boundary",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value in ("", None):
        return 0.0
    return float(value)


def build_rows(input_path: Path = DEFAULT_INPUT) -> list[dict[str, str]]:
    summary_rows = read_csv(input_path)
    output_rows = []
    for summary in summary_rows:
        scores = normalize_metric_values(
            p95_critical_latency_sec=f(summary, "p95_critical_latency_sec_mean"),
            stale_data_ratio=f(summary, "trusted_stale_exposure_mean"),
            priority_inversion_rate=f(summary, "priority_inversion_rate_mean"),
            kill_chain_delay_sec=f(summary, "kill_chain_delay_sec_mean"),
            recovery_instability=f(summary, "recovery_instability_mean"),
        )
        contributions = {
            component: weight * scores[score_key]
            for component, _, score_key, weight, _ in COMPONENTS
        }
        reconstructed = sum(contributions.values())
        reported = f(summary, "mission_impact_mean")
        delta = reported - reconstructed
        for component, raw_key, score_key, weight, interpretation in COMPONENTS:
            contribution = contributions[component]
            share = contribution / reconstructed if reconstructed else 0.0
            output_rows.append(
                {
                    "experiment": summary["experiment"],
                    "component": component,
                    "raw_metric_mean": fmt(f(summary, raw_key)),
                    "normalized_score": fmt(scores[score_key]),
                    "weight": fmt(weight),
                    "weighted_contribution": fmt(contribution),
                    "reported_mission_impact_mean": fmt(reported),
                    "reconstructed_mission_impact_from_means": fmt(reconstructed),
                    "reconstruction_delta": fmt(delta),
                    "share_of_reconstructed_impact": fmt(share),
                    "interpretation": interpretation,
                    "safety_boundary": SAFETY_BOUNDARY,
                }
            )
    return output_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Mission Impact Decomposition",
        "",
        "This table decomposes repeated-run Mission Impact into the five weighted components used by `compute_full_mission_impact`.",
        "The stale component uses `trusted_stale_exposure`, not raw `stale_data_ratio`, because TSRA-R may mark stale COP objects as untrusted rather than removing them.",
        "The reconstruction uses mean component values, so it may differ slightly from the reported mean of per-run mission impact.",
        "",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| experiment | component | raw_metric_mean | normalized_score | weight | weighted_contribution | share |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["experiment"]),
                    md(row["component"]),
                    md(row["raw_metric_mean"]),
                    md(row["normalized_score"]),
                    md(row["weight"]),
                    md(row["weighted_contribution"]),
                    md(row["share_of_reconstructed_impact"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Experiment Summary", ""])
    for experiment in ordered_experiments(rows):
        subset = [row for row in rows if row["experiment"] == experiment]
        top = max(subset, key=lambda row: float(row["weighted_contribution"]))
        first = subset[0]
        lines.extend(
            [
                f"### {experiment}",
                "",
                f"- Reported mission impact mean: {first['reported_mission_impact_mean']}",
                f"- Reconstructed from mean components: {first['reconstructed_mission_impact_from_means']}",
                f"- Reconstruction delta: {first['reconstruction_delta']}",
                f"- Largest component: {top['component']} ({top['weighted_contribution']})",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def ordered_experiments(rows: list[dict[str, str]]) -> list[str]:
    seen = []
    for row in rows:
        experiment = row["experiment"]
        if experiment not in seen:
            seen.append(experiment)
    return seen


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def fmt(value: float) -> str:
    return f"{value:.6g}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Mission Impact decomposition table.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(args.input)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} decomposition rows)")
    print(f"Wrote {args.output_md} ({len(rows)} decomposition rows)")


if __name__ == "__main__":
    main()
