from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/adaptive_defense_decision_path_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/adaptive_defense_decision_path_audit.md"
ADAPTIVE_SUMMARY = "outputs/batch/adaptive_memory_summary.csv"
ADAPTIVE_TRACE_GLOB = "outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/tsra_r_decision_traces.jsonl"
ADAPTIVE_DEFENSE_GLOB = "outputs/tmp_adaptive_memory/seed_*/adaptive_memory_adaptive_tsra_r/defense_events.jsonl"

CORE_ACTIONS = {"priority_reroute", "stale_badge"}
OPTIONAL_ACTIONS = {"video_throttle", "pace_switch"}
ALL_ACTIONS = ["priority_reroute", "video_throttle", "stale_badge", "pace_switch"]
SAFETY_BOUNDARY = (
    "closed simulation adaptive-defense decision-path audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "area",
    "requirement",
    "evidence",
    "observed",
    "status",
    "interpretation",
    "safety_boundary",
]


def read_csv(rel: str) -> list[dict[str, str]]:
    path = ROOT / rel
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_all_jsonl(pattern: str) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(ROOT.glob(pattern)):
        rows.extend(read_jsonl(path))
    return rows


def trace_paths() -> list[Path]:
    return sorted(ROOT.glob(ADAPTIVE_TRACE_GLOB))


def defense_events() -> list[dict[str, Any]]:
    return read_all_jsonl(ADAPTIVE_DEFENSE_GLOB)


def f(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "0") or 0.0)
    except ValueError:
        return 0.0


def fmt(value: float) -> str:
    return f"{value:.6g}"


def action_candidate(trace: dict[str, Any], action: str) -> dict[str, Any]:
    for candidate in trace.get("candidate_actions") or []:
        if candidate.get("action") == action:
            return candidate
    return {}


def selected_events(trace: dict[str, Any]) -> list[dict[str, Any]]:
    selected = trace.get("selected_action") or {}
    if selected.get("type") != "defense_events":
        return []
    return selected.get("events") or []


def tool_count(traces: list[dict[str, Any]], tool_name: str) -> int:
    return sum(
        1
        for trace in traces
        for call in (trace.get("tool_calls") or [])
        if call.get("tool_name") == tool_name
    )


def tool_errors(traces: list[dict[str, Any]]) -> int:
    return sum(
        1
        for trace in traces
        for call in (trace.get("tool_calls") or [])
        if call.get("status") != "ok"
    )


def policy_feedback_count(traces: list[dict[str, Any]]) -> int:
    return sum(1 for trace in traces if (trace.get("feedback") or {}).get("adaptive_policy"))


def candidate_total(traces: list[dict[str, Any]]) -> int:
    return sum(len(trace.get("candidate_actions") or []) for trace in traces)


def action_stats(traces: list[dict[str, Any]], action: str) -> dict[str, int]:
    candidates = [action_candidate(trace, action) for trace in traces]
    candidates = [candidate for candidate in candidates if candidate]
    emitted = sum(
        1
        for trace in traces
        for event in selected_events(trace)
        if event.get("action") == action
    )
    return {
        "candidate_count": len(candidates),
        "adaptive_enabled": sum(1 for candidate in candidates if candidate.get("adaptive_enabled") is True),
        "adaptive_held": sum(1 for candidate in candidates if candidate.get("adaptive_enabled") is False),
        "eligible": sum(1 for candidate in candidates if candidate.get("eligible") is True),
        "eligible_held": sum(
            1
            for candidate in candidates
            if candidate.get("eligible") is True and candidate.get("adaptive_enabled") is False
        ),
        "ready_enabled": sum(
            1
            for candidate in candidates
            if candidate.get("ready") is True and candidate.get("adaptive_enabled") is True
        ),
        "gate_reason_count": sum(1 for candidate in candidates if candidate.get("adaptive_gate_reason")),
        "memory_evidence_count": sum(1 for candidate in candidates if candidate.get("adaptive_memory_evidence")),
        "emitted": emitted,
    }


def event_action_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    counts = {action: 0 for action in ALL_ACTIONS}
    for event in events:
        action = str(event.get("action", ""))
        if action in counts:
            counts[action] += 1
    return counts


def emission_gate_violations(traces: list[dict[str, Any]]) -> int:
    violations = 0
    for trace in traces:
        candidates = {
            candidate.get("action"): candidate
            for candidate in (trace.get("candidate_actions") or [])
        }
        for event in selected_events(trace):
            action = event.get("action")
            candidate = candidates.get(action, {})
            if action in CORE_ACTIONS | OPTIONAL_ACTIONS and candidate.get("adaptive_enabled") is not True:
                violations += 1
    return violations


def row(
    *,
    check_id: str,
    area: str,
    requirement: str,
    evidence: list[str],
    observed: str,
    ok: bool,
    interpretation: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "requirement": requirement,
        "evidence": " | ".join(evidence),
        "observed": observed,
        "status": "pass" if ok else "fail",
        "interpretation": interpretation,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def build_rows() -> list[dict[str, str]]:
    summary_rows = {row["condition"]: row for row in read_csv(ADAPTIVE_SUMMARY)}
    full = summary_rows.get("full_tsra_r", {})
    adaptive = summary_rows.get("adaptive_tsra_r", {})
    traces = read_all_jsonl(ADAPTIVE_TRACE_GLOB)
    paths = trace_paths()
    events = defense_events()
    emitted_counts = event_action_counts(events)

    mission_improvement = f(full, "mission_impact_mean") - f(adaptive, "mission_impact_mean")
    defense_reduction = f(full, "defense_count_mean") - f(adaptive, "defense_count_mean")
    video_reduction = f(full, "video_throttle_count_mean") - f(adaptive, "video_throttle_count_mean")
    pace_reduction = f(full, "pace_switch_count_mean") - f(adaptive, "pace_switch_count_mean")
    trusted_stale_delta = f(adaptive, "trusted_stale_exposure_mean") - f(full, "trusted_stale_exposure_mean")

    priority = action_stats(traces, "priority_reroute")
    stale = action_stats(traces, "stale_badge")
    video = action_stats(traces, "video_throttle")
    pace = action_stats(traces, "pace_switch")
    total_candidates = candidate_total(traces)
    update_policy_calls = tool_count(traces, "update_adaptive_action_policy")
    errors = tool_errors(traces)
    feedback_count = policy_feedback_count(traces)
    violations = emission_gate_violations(traces)

    return [
        row(
            check_id="ADP01",
            area="Batch-level adaptive effect",
            requirement="Adaptive TSRA-R should reduce mission impact and optional action load without increasing trusted stale exposure.",
            evidence=[ADAPTIVE_SUMMARY],
            observed=(
                f"mission_improvement={fmt(mission_improvement)}; "
                f"defense_count_reduction={fmt(defense_reduction)}; "
                f"video_throttle_reduction={fmt(video_reduction)}; "
                f"pace_switch_reduction={fmt(pace_reduction)}; "
                f"trusted_stale_delta={fmt(trusted_stale_delta)}"
            ),
            ok=(
                mission_improvement >= 0.02
                and defense_reduction >= 2.0
                and video_reduction >= 2.0
                and pace_reduction >= 0.5
                and trusted_stale_delta <= 0.001
            ),
            interpretation=(
                "The adaptive policy improves mission impact by reducing optional defensive load "
                "while keeping stale-COP protection intact."
            ),
        ),
        row(
            check_id="ADP02",
            area="Adaptive policy tool path",
            requirement="Every adaptive TSRA-R decision should call the memory policy tool and keep candidate evidence.",
            evidence=[ADAPTIVE_TRACE_GLOB],
            observed=(
                f"trace_files={len(paths)}; trace_count={len(traces)}; "
                f"update_adaptive_action_policy={update_policy_calls}; "
                f"candidate_total={total_candidates}; policy_feedback_count={feedback_count}; "
                f"tool_errors={errors}"
            ),
            ok=(
                len(paths) >= 30
                and len(traces) >= 30 * 61
                and update_policy_calls == len(traces)
                and total_candidates == len(traces) * 4
                and feedback_count == len(traces)
                and errors == 0
            ),
            interpretation=(
                "Adaptive TSRA-R is not a post-hoc metric filter: each decision calls the policy "
                "tool and records four defense candidates."
            ),
        ),
        row(
            check_id="ADP03",
            area="Core defense preservation",
            requirement="Memory gating should keep priority reroute and stale badge available as core protections.",
            evidence=[ADAPTIVE_TRACE_GLOB, ADAPTIVE_DEFENSE_GLOB],
            observed=(
                f"priority_enabled={priority['adaptive_enabled']}/{priority['candidate_count']}; "
                f"stale_enabled={stale['adaptive_enabled']}/{stale['candidate_count']}; "
                f"priority_emitted={emitted_counts['priority_reroute']}; "
                f"stale_emitted={emitted_counts['stale_badge']}"
            ),
            ok=(
                bool(traces)
                and priority["adaptive_enabled"] == priority["candidate_count"] == len(traces)
                and stale["adaptive_enabled"] == stale["candidate_count"] == len(traces)
                and emitted_counts["priority_reroute"] > 0
                and emitted_counts["stale_badge"] > 0
            ),
            interpretation=(
                "The adaptive layer preserves the defenses that ablation proved essential: "
                "priority ordering and stale-COP trust marking."
            ),
        ),
        row(
            check_id="ADP04",
            area="Video throttle memory gate",
            requirement="Video throttling should be held until repeated critical/video pressure appears in memory.",
            evidence=[ADAPTIVE_TRACE_GLOB, ADAPTIVE_DEFENSE_GLOB],
            observed=(
                f"video_candidates={video['candidate_count']}; "
                f"video_enabled={video['adaptive_enabled']}; "
                f"video_held={video['adaptive_held']}; "
                f"video_eligible_held={video['eligible_held']}; "
                f"video_gate_reasons={video['gate_reason_count']}; "
                f"video_emitted={emitted_counts['video_throttle']}"
            ),
            ok=(
                video["candidate_count"] == len(traces)
                and video["adaptive_held"] > video["adaptive_enabled"]
                and video["eligible_held"] > 0
                and video["gate_reason_count"] == video["candidate_count"]
                and 0 < emitted_counts["video_throttle"] < video["candidate_count"]
            ),
            interpretation=(
                "Video throttle remains available, but the agent withholds it on many eligible "
                "single-window spikes until memory confirms repeated pressure."
            ),
        ),
        row(
            check_id="ADP05",
            area="PACE switch memory gate",
            requirement="PACE switching should require persistent SATCOM degradation and severe queue evidence.",
            evidence=[ADAPTIVE_TRACE_GLOB, ADAPTIVE_DEFENSE_GLOB],
            observed=(
                f"pace_candidates={pace['candidate_count']}; "
                f"pace_enabled={pace['adaptive_enabled']}; "
                f"pace_held={pace['adaptive_held']}; "
                f"pace_eligible_held={pace['eligible_held']}; "
                f"pace_gate_reasons={pace['gate_reason_count']}; "
                f"pace_emitted={emitted_counts['pace_switch']}"
            ),
            ok=(
                pace["candidate_count"] == len(traces)
                and pace["adaptive_held"] > pace["adaptive_enabled"]
                and pace["eligible_held"] > 0
                and pace["gate_reason_count"] == pace["candidate_count"]
                and 0 < emitted_counts["pace_switch"] < pace["candidate_count"]
            ),
            interpretation=(
                "PACE remains a real option, but memory prevents fallback switching from becoming "
                "a repeated recovery-instability source."
            ),
        ),
        row(
            check_id="ADP06",
            area="Gate-to-event consistency",
            requirement="Emitted adaptive defense events must be backed by enabled candidate gates and memory evidence.",
            evidence=[ADAPTIVE_TRACE_GLOB],
            observed=(
                f"emission_gate_violations={violations}; "
                f"memory_evidence_candidates="
                f"{sum(action_stats(traces, action)['memory_evidence_count'] for action in ALL_ACTIONS)}; "
                f"selected_optional_events={emitted_counts['video_throttle'] + emitted_counts['pace_switch']}"
            ),
            ok=(
                violations == 0
                and sum(action_stats(traces, action)["memory_evidence_count"] for action in ALL_ACTIONS)
                == total_candidates
                and emitted_counts["video_throttle"] + emitted_counts["pace_switch"] > 0
            ),
            interpretation=(
                "Selected adaptive events are consistent with the candidate-level memory gate, "
                "so the trace can explain both action and restraint."
            ),
        ),
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
        "# Adaptive Defense Decision Path Audit",
        "",
        "This audit verifies that Adaptive TSRA-R uses AgentMemory to gate optional defense actions while preserving core protections.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| check_id | area | status | observed | interpretation |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(item["check_id"]),
                    md(item["area"]),
                    md(item["status"]),
                    md(item["observed"]),
                    md(item["interpretation"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for item in rows:
        lines.extend(
            [
                f"### {item['check_id']} {item['area']}",
                "",
                f"- Requirement: {item['requirement']}",
                f"- Evidence: {item['evidence']}",
                f"- Observed: {item['observed']}",
                f"- Status: {item['status']}",
                f"- Interpretation: {item['interpretation']}",
                f"- Safety boundary: {item['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Adaptive TSRA-R defense decision path.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any adaptive defense path row fails.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [item for item in rows if item["status"] != "pass"]
    print(f"Wrote {display_path(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.output_md)} ({len(rows)} rows)")
    if failed:
        print(
            "Failed adaptive defense decision path rows: "
            + ", ".join(item["check_id"] for item in failed)
        )
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
