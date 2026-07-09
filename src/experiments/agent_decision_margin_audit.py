from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_decision_margin_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_decision_margin_audit.md")

TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
    "tsra_r_rule_delegate_traces.jsonl",
]

SAFETY_BOUNDARY = (
    "closed simulation decision-margin audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "trace_id",
    "time_sec",
    "agent",
    "policy",
    "selected_type",
    "selected_actions",
    "decision_basis",
    "selected_value",
    "runner_up_value",
    "selection_margin",
    "threshold",
    "threshold_margin",
    "eligible_ready_count",
    "unselected_ready_count",
    "no_op_basis",
    "margin_status",
    "issues",
    "safety_boundary",
]


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


def discover_traces(root: Path) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    if not root.exists():
        return rows
    for exp_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        for filename in TRACE_FILES:
            for trace in read_jsonl(exp_dir / filename):
                rows.append((exp_dir.name, trace))
    return rows


def collect_rows(experiment_root: Path) -> list[dict[str, str]]:
    rows = [
        audit_trace(experiment, trace)
        for experiment, trace in discover_traces(experiment_root)
    ]
    return sorted(
        rows,
        key=lambda row: (
            row["experiment"],
            as_float(row["time_sec"]),
            row["agent"],
            row["trace_id"],
        ),
    )


def audit_trace(experiment: str, trace: dict[str, Any]) -> dict[str, str]:
    selected = trace.get("selected_action") or {}
    selected_type = str(selected.get("type") or "")
    agent = str(trace.get("agent") or "")
    candidates = trace.get("candidate_actions") or []
    if agent.startswith("AURA"):
        values = audit_aura(selected, candidates, trace)
    elif agent == "TSRA-R-ML":
        values = audit_ml_tsra_r(selected, candidates, trace)
    elif agent.startswith("TSRA-R"):
        values = audit_rule_tsra_r(selected, candidates)
    else:
        values = {
            "decision_basis": "unknown_agent",
            "selected_value": "",
            "runner_up_value": "",
            "selection_margin": "",
            "threshold": "",
            "threshold_margin": "",
            "eligible_ready_count": "0",
            "unselected_ready_count": "0",
            "no_op_basis": "",
            "margin_status": "fail",
            "issues": f"unsupported agent {agent}",
        }

    return {
        "experiment": experiment,
        "trace_id": str(trace.get("trace_id") or ""),
        "time_sec": format_number(trace.get("time_sec")),
        "agent": agent,
        "policy": str(trace.get("policy") or ""),
        "selected_type": selected_type,
        "selected_actions": ", ".join(selected_action_names(selected)) or "none",
        "safety_boundary": SAFETY_BOUNDARY,
        **values,
    }


def audit_aura(
    selected: dict[str, Any],
    candidates: list[dict[str, Any]],
    trace: dict[str, Any],
) -> dict[str, str]:
    threshold = as_float((trace.get("feedback") or {}).get("attack_threshold"))
    scored = [candidate for candidate in candidates if "score" in candidate]
    selected_type = selected.get("type")
    if selected_type == "no_op":
        if not scored:
            return status_row(
                decision_basis="pre_start_or_cooldown_no_candidates",
                threshold=threshold,
                no_op_basis="no scored attack candidates available",
            )
        max_score = max(as_float(candidate.get("score")) for candidate in scored)
        margin = max_score - threshold
        ok = max_score < threshold
        return status_row(
            decision_basis="score_below_attack_threshold",
            selected_value=max_score,
            runner_up_value="",
            selection_margin="",
            threshold=threshold,
            threshold_margin=margin,
            no_op_basis=f"best candidate score {format_number(max_score)} below threshold {format_number(threshold)}",
            ok=ok,
            issues="" if ok else "no_op despite candidate score above threshold",
        )

    if selected_type != "attack_event":
        return status_row(
            decision_basis="unsupported_aura_selection",
            threshold=threshold,
            ok=False,
            issues=f"unsupported selected_type {selected_type}",
        )

    selected_score = as_float(selected.get("score"))
    selected_action = str(selected.get("attack_type") or "")
    selected_link = str(selected.get("target_link") or "")
    runner_up = runner_up_score(
        scored,
        selected_action=selected_action,
        selected_link=selected_link,
        selected_score=selected_score,
    )
    max_score = max([as_float(candidate.get("score")) for candidate in scored], default=selected_score)
    selection_margin = selected_score - runner_up if runner_up is not None else selected_score
    threshold_margin = selected_score - threshold
    ok = selected_score >= max_score - 1e-6 and selected_score >= threshold
    issues = []
    if selected_score < max_score - 1e-6:
        issues.append("selected attack is not top-scored")
    if selected_score < threshold:
        issues.append("selected attack below attack threshold")
    return status_row(
        decision_basis="top_attack_score_minus_runner_up_and_threshold",
        selected_value=selected_score,
        runner_up_value=runner_up,
        selection_margin=selection_margin,
        threshold=threshold,
        threshold_margin=threshold_margin,
        ok=ok,
        issues=" || ".join(issues),
    )


def audit_ml_tsra_r(
    selected: dict[str, Any],
    candidates: list[dict[str, Any]],
    trace: dict[str, Any],
) -> dict[str, str]:
    candidate = next(
        (item for item in candidates if item.get("action") == "open_defense_window"),
        {},
    )
    feedback = trace.get("feedback") or {}
    probability = as_float(candidate.get("probability", feedback.get("probability")))
    threshold = as_float(candidate.get("threshold", feedback.get("threshold")))
    active_until = as_float(candidate.get("active_defense_until", feedback.get("active_defense_until")))
    time_sec = as_float(trace.get("time_sec"))
    threshold_margin = probability - threshold
    active_window = time_sec < active_until
    selected_type = selected.get("type")

    if selected_type == "no_op":
        ok = probability < threshold or active_window
        basis = (
            "active_window_without_downstream_event"
            if active_window
            else "probability_below_threshold_no_window"
        )
        no_op_basis = (
            "active defense window is maintained, but no downstream rule action emitted"
            if active_window
            else "probability below threshold and no active defense window"
        )
        return status_row(
            decision_basis=basis,
            selected_value=probability,
            threshold=threshold,
            threshold_margin=threshold_margin,
            no_op_basis=no_op_basis,
            ok=ok,
            issues="" if ok else "no_op without threshold, active-window, or below-threshold support",
        )

    if selected_type == "defense_events":
        ok = probability >= threshold or active_window
        basis = "probability_above_threshold" if probability >= threshold else "maintained_active_defense_window"
        return status_row(
            decision_basis=basis,
            selected_value=probability,
            threshold=threshold,
            threshold_margin=threshold_margin,
            ok=ok,
            issues="" if ok else "defense event without threshold or active-window support",
        )

    return status_row(
        decision_basis="unsupported_ml_tsra_r_selection",
        selected_value=probability,
        threshold=threshold,
        threshold_margin=threshold_margin,
        ok=False,
        issues=f"unsupported selected_type {selected_type}",
    )


def audit_rule_tsra_r(
    selected: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> dict[str, str]:
    selected_actions = set(selected_action_names(selected))
    selected_type = selected.get("type")
    ready_actions = {
        str(candidate.get("action"))
        for candidate in candidates
        if candidate.get("enabled") is True
        and candidate.get("eligible") is True
        and candidate.get("ready") is True
    }
    if selected_type == "no_op":
        ok = not ready_actions
        return status_row(
            decision_basis="eligible_ready_defense_conditions",
            eligible_ready_count=len(ready_actions),
            unselected_ready_count=len(ready_actions),
            no_op_basis="no enabled defense candidate was both eligible and ready",
            ok=ok,
            issues="" if ok else f"no_op skipped ready actions: {', '.join(sorted(ready_actions))}",
        )

    if selected_type == "defense_events":
        unselected_ready = ready_actions - selected_actions
        missing_selected = selected_actions - ready_actions
        ok = not unselected_ready and not missing_selected
        issues = []
        if unselected_ready:
            issues.append(f"ready actions not selected: {', '.join(sorted(unselected_ready))}")
        if missing_selected:
            issues.append(f"selected actions lacked eligible/ready support: {', '.join(sorted(missing_selected))}")
        return status_row(
            decision_basis="selected_all_eligible_ready_defense_actions",
            selected_value=len(selected_actions),
            selection_margin=len(selected_actions) - len(unselected_ready),
            eligible_ready_count=len(ready_actions),
            unselected_ready_count=len(unselected_ready),
            ok=ok,
            issues=" || ".join(issues),
        )

    return status_row(
        decision_basis="unsupported_rule_tsra_r_selection",
        eligible_ready_count=len(ready_actions),
        unselected_ready_count=len(ready_actions),
        ok=False,
        issues=f"unsupported selected_type {selected_type}",
    )


def status_row(
    *,
    decision_basis: str,
    selected_value: Any = "",
    runner_up_value: Any = "",
    selection_margin: Any = "",
    threshold: Any = "",
    threshold_margin: Any = "",
    eligible_ready_count: Any = 0,
    unselected_ready_count: Any = 0,
    no_op_basis: str = "",
    ok: bool = True,
    issues: str = "",
) -> dict[str, str]:
    return {
        "decision_basis": decision_basis,
        "selected_value": format_number(selected_value),
        "runner_up_value": format_number(runner_up_value),
        "selection_margin": format_number(selection_margin),
        "threshold": format_number(threshold),
        "threshold_margin": format_number(threshold_margin),
        "eligible_ready_count": str(eligible_ready_count),
        "unselected_ready_count": str(unselected_ready_count),
        "no_op_basis": no_op_basis,
        "margin_status": "pass" if ok else "fail",
        "issues": issues,
    }


def selected_action_names(selected: dict[str, Any]) -> list[str]:
    selected_type = selected.get("type")
    if selected_type == "attack_event":
        return [str(selected.get("attack_type") or "attack_event")]
    if selected_type == "defense_events":
        return [
            str(event.get("action"))
            for event in selected.get("events") or []
            if event.get("action")
        ]
    if selected_type == "no_op":
        return ["no_op"]
    return [str(selected_type or "unknown")]


def runner_up_score(
    candidates: list[dict[str, Any]],
    *,
    selected_action: str,
    selected_link: str,
    selected_score: float,
) -> float | None:
    other_scores = []
    skipped_selected = False
    for candidate in candidates:
        score = as_float(candidate.get("score"))
        is_selected = (
            str(candidate.get("action") or "") == selected_action
            and str(candidate.get("target_link") or "") == selected_link
            and abs(score - selected_score) <= 1e-6
        )
        if is_selected and not skipped_selected:
            skipped_selected = True
            continue
        other_scores.append(score)
    if not other_scores:
        return None
    return max(other_scores)


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_number(value: Any) -> str:
    if value in ("", None):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    failures = [row for row in rows if row["margin_status"] != "pass"]
    action_rows = [row for row in rows if row["selected_type"] != "no_op"]
    threshold_rows = [row for row in rows if row["threshold_margin"] not in ("", None)]
    lines = [
        "# Agent Decision Margin Audit",
        "",
        "This audit explains how much decision support existed for each AURA/TSRA-R selected action.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Action rows: {len(action_rows)}",
        f"- Threshold rows: {len(threshold_rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'margin_status'))}",
        f"- Agents: {', '.join(sorted({row['agent'] for row in rows}))}",
        "",
        "## Sample Action Margins",
        "",
    ]
    for row in action_rows[:20]:
        lines.append(
            "- "
            f"{row['experiment']} {row['time_sec']}s {row['agent']} "
            f"{row['selected_actions']}: basis={row['decision_basis']}, "
            f"selected={row['selected_value'] or 'n/a'}, "
            f"runner_up={row['runner_up_value'] or 'n/a'}, "
            f"margin={row['selection_margin'] or 'n/a'}, "
            f"threshold_margin={row['threshold_margin'] or 'n/a'}"
        )
    lines.extend(["", "## Failures", ""])
    if not failures:
        lines.append("None.")
    else:
        for row in failures[:20]:
            lines.append(
                f"- {row['experiment']} {row['trace_id']} {row['agent']} "
                f"{row['selected_actions']}: {row['issues']}"
            )
    lines.extend(["", "## Audit Table", ""])
    visible_fields = [
        "experiment",
        "time_sec",
        "agent",
        "selected_actions",
        "decision_basis",
        "selection_margin",
        "threshold_margin",
        "margin_status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row[field]
        counts[value] = counts.get(value, 0) + 1
    return counts


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def markdown_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value) for value in values) + " |"


def markdown_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit DecisionTrace decision margins.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} margin audit rows)")
    print(f"Wrote {args.output_md} ({len(rows)} margin audit rows)")


if __name__ == "__main__":
    main()
