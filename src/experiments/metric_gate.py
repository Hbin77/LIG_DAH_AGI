from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/metric_gate_summary.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/metric_gate_summary.md")

FIELDNAMES = [
    "gate_id",
    "area",
    "metric",
    "observed",
    "threshold",
    "status",
    "interpretation",
]


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    area: str
    metric: str
    observed: float
    threshold: str
    passed: bool
    interpretation: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def f(row: dict[str, str], column: str) -> float:
    value = row.get(column, "")
    if value in ("", None):
        return 0.0
    return float(value)


def build_gate_results(root: Path = Path(".")) -> list[GateResult]:
    repeated = index_by(read_csv(root / "outputs/batch/repeated_experiment_summary.csv"), "experiment")
    resilience = index_by(read_csv(root / "outputs/batch/resilience_gain_summary.csv"), "experiment")
    ablation = index_by(read_csv(root / "outputs/batch/tsra_action_ablation_summary.csv"), "condition")
    adaptive = index_by(read_csv(root / "outputs/batch/adaptive_memory_summary.csv"), "condition")

    e1 = repeated["E1_baseline"]
    e2 = repeated["E2_fixed_attack"]
    e3 = repeated["E3_rule_aura"]
    e5 = repeated["E5_rule_aura_tsra_r"]
    e6 = repeated["E6_ml_aura_tsra_r"]
    e7 = repeated["E7_ml_aura_ml_tsra_r"]

    full = ablation["full"]
    no_priority = ablation["no_priority_reroute"]
    no_stale = ablation["no_stale_badge"]
    full_adaptive = adaptive["full_tsra_r"]
    adaptive_tsra = adaptive["adaptive_tsra_r"]

    gates = [
        make_gate(
            gate_id="G01",
            area="AURA attack effectiveness",
            metric="E3 mission_impact_mean - E1 mission_impact_mean",
            observed=f(e3, "mission_impact_mean") - f(e1, "mission_impact_mean"),
            threshold=">= 0.35",
            predicate=lambda value: value >= 0.35,
            interpretation="AURA should create substantially higher simulated mission impact than baseline.",
        ),
        make_gate(
            gate_id="G02",
            area="AURA adaptive selection",
            metric="E3 mission_impact_mean - E2 mission_impact_mean",
            observed=f(e3, "mission_impact_mean") - f(e2, "mission_impact_mean"),
            threshold=">= 0.10",
            predicate=lambda value: value >= 0.10,
            interpretation="AURA should outperform the fixed attack baseline in mission impact.",
        ),
        make_gate(
            gate_id="G03",
            area="TSRA-R resilience",
            metric="E5 resilience_gain_mean",
            observed=f(resilience["E5_rule_aura_tsra_r"], "mean"),
            threshold=">= 0.80",
            predicate=lambda value: value >= 0.80,
            interpretation="TSRA-R should recover at least 80% of AURA-induced impact in repeated runs.",
        ),
        make_gate(
            gate_id="G04",
            area="TSRA-R impact containment",
            metric="E5 mission_impact_mean / E3 mission_impact_mean",
            observed=f(e5, "mission_impact_mean") / max(f(e3, "mission_impact_mean"), 1e-9),
            threshold="<= 0.20",
            predicate=lambda value: value <= 0.20,
            interpretation="Defended mission impact should stay below one fifth of undefended AURA impact.",
        ),
        make_gate(
            gate_id="G05",
            area="Trusted stale protection",
            metric="E5 trusted_stale_exposure_mean",
            observed=f(e5, "trusted_stale_exposure_mean"),
            threshold="<= 0.15",
            predicate=lambda value: value <= 0.15,
            interpretation="TSRA-R stale_badge should keep trusted stale exposure bounded.",
        ),
        make_gate(
            gate_id="G06",
            area="Priority reroute ablation",
            metric="no_priority_reroute delta_priority_inversion_rate_mean",
            observed=f(no_priority, "delta_priority_inversion_rate_mean"),
            threshold=">= 0.25",
            predicate=lambda value: value >= 0.25,
            interpretation="Removing priority_reroute should materially increase priority inversion.",
        ),
        make_gate(
            gate_id="G07",
            area="Stale badge ablation",
            metric="no_stale_badge delta_trusted_stale_exposure_mean",
            observed=f(no_stale, "delta_trusted_stale_exposure_mean"),
            threshold=">= 0.25",
            predicate=lambda value: value >= 0.25,
            interpretation="Removing stale_badge should materially increase trusted stale exposure.",
        ),
        make_gate(
            gate_id="G08",
            area="Adaptive memory improvement",
            metric="adaptive mission impact improvement over full TSRA-R",
            observed=f(full_adaptive, "mission_impact_mean") - f(adaptive_tsra, "mission_impact_mean"),
            threshold=">= 0.005",
            predicate=lambda value: value >= 0.005,
            interpretation="AdaptiveTSRA-R should improve mission impact versus full TSRA-R baseline.",
        ),
        make_gate(
            gate_id="G09",
            area="Adaptive memory action economy",
            metric="full video_throttle_count_mean - adaptive video_throttle_count_mean",
            observed=f(full_adaptive, "video_throttle_count_mean") - f(adaptive_tsra, "video_throttle_count_mean"),
            threshold=">= 1.0",
            predicate=lambda value: value >= 1.0,
            interpretation="AdaptiveTSRA-R should reduce optional video throttle actions while preserving core defenses.",
        ),
        make_gate(
            gate_id="G10",
            area="ML defender separation",
            metric="abs(E7 mission_impact_mean - E6 mission_impact_mean)",
            observed=abs(f(e7, "mission_impact_mean") - f(e6, "mission_impact_mean")),
            threshold=">= 0.005",
            predicate=lambda value: value >= 0.005,
            interpretation="E7 should remain behaviorally distinct from E6 so ML TSRA-R is not a no-op copy.",
        ),
        make_gate(
            gate_id="G11",
            area="Repeated-run stability",
            metric="max(E5/E7 mission_impact_std)",
            observed=max(f(e5, "mission_impact_std"), f(e7, "mission_impact_std")),
            threshold="<= 0.03",
            predicate=lambda value: value <= 0.03,
            interpretation="Defended repeated-run mission impact should remain stable across seeds.",
        ),
        make_gate(
            gate_id="G12",
            area="PACE reselection discipline",
            metric="full TSRA-R recovery_instability_mean",
            observed=f(full, "recovery_instability_mean"),
            threshold="<= 2.20",
            predicate=lambda value: value <= 2.20,
            interpretation=(
                "Full TSRA-R should avoid repeated fallback reselection unless residual mission "
                "pressure justifies the extra recovery instability."
            ),
        ),
    ]

    return gates


def make_gate(
    *,
    gate_id: str,
    area: str,
    metric: str,
    observed: float,
    threshold: str,
    predicate: Callable[[float], bool],
    interpretation: str,
) -> GateResult:
    return GateResult(
        gate_id=gate_id,
        area=area,
        metric=metric,
        observed=observed,
        threshold=threshold,
        passed=predicate(observed),
        interpretation=interpretation,
    )


def rows_from_results(results: list[GateResult]) -> list[dict[str, str]]:
    return [
        {
            "gate_id": result.gate_id,
            "area": result.area,
            "metric": result.metric,
            "observed": format_float(result.observed),
            "threshold": result.threshold,
            "status": "pass" if result.passed else "fail",
            "interpretation": result.interpretation,
        }
        for result in results
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Metric Gate Summary",
        "",
        "This table checks whether the generated experiment metrics still support the intended AURA/TSRA-R development direction.",
        "",
        "| gate_id | area | metric | observed | threshold | status | interpretation |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(row["gate_id"]),
                    markdown_cell(row["area"]),
                    markdown_cell(row["metric"]),
                    markdown_cell(row["observed"]),
                    markdown_cell(row["threshold"]),
                    markdown_cell(row["status"]),
                    markdown_cell(row["interpretation"]),
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_cell(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def format_float(value: float) -> str:
    return f"{value:.6g}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check experiment metrics against project quality gates.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any metric gate fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = rows_from_results(build_gate_results())
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failures = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} gates)")
    print(f"Wrote {args.output_md} ({len(rows)} gates)")
    if failures:
        print(f"Failed metric gates: {', '.join(row['gate_id'] for row in failures)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
