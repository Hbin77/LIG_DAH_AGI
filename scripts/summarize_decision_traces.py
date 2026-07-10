from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


FIELDNAMES = [
    "seed",
    "experiment",
    "trace_file",
    "trace_id",
    "tick",
    "agent",
    "policy",
    "selected_action",
    "candidate_count",
    "tool_names",
    "reason",
    "safety_boundary",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL in {path} line {line_number}: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"trace row in {path} line {line_number} is not an object")
        rows.append(value)
    return rows


def trace_metadata(input_dir: Path, trace_path: Path) -> tuple[str, str, str]:
    relative = trace_path.relative_to(input_dir)
    filename = trace_path.name
    for suffix, agent_kind in (
        ("_aura_decision_traces.jsonl", "aura"),
        ("_tsra_decision_traces.jsonl", "tsra"),
    ):
        if filename.endswith(suffix):
            return relative.parts[0] if relative.parts else "", filename[: -len(suffix)], agent_kind
    return relative.parts[0] if relative.parts else "", trace_path.stem, "unknown"


def selected_action_summary(selected_action: Any) -> str:
    if not isinstance(selected_action, dict):
        return str(selected_action or "")
    action_type = str(selected_action.get("type", ""))
    action_name = str(
        selected_action.get("action")
        or selected_action.get("attack")
        or selected_action.get("mode")
        or selected_action.get("defense_mode")
        or ""
    )
    return ": ".join(value for value in [action_type, action_name] if value)


def collect_rows(input_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for trace_path in sorted(input_dir.rglob("*_decision_traces.jsonl")):
        seed, experiment, _ = trace_metadata(input_dir, trace_path)
        relative_path = str(trace_path.relative_to(input_dir))
        for trace in read_jsonl(trace_path):
            tool_names = ", ".join(
                str(call.get("tool_name", ""))
                for call in trace.get("tool_calls", [])
                if isinstance(call, dict) and call.get("tool_name")
            )
            rows.append(
                {
                    "seed": seed,
                    "experiment": experiment,
                    "trace_file": relative_path,
                    "trace_id": str(trace.get("trace_id", "")),
                    "tick": str(trace.get("tick", "")),
                    "agent": str(trace.get("agent", "")),
                    "policy": str(trace.get("policy", "")),
                    "selected_action": selected_action_summary(trace.get("selected_action")),
                    "candidate_count": str(len(trace.get("candidate_actions", []))),
                    "tool_names": tool_names,
                    "reason": str(trace.get("reason", "")),
                    "safety_boundary": str(trace.get("safety_boundary", "")),
                }
            )
    return sorted(
        rows,
        key=lambda row: (row["seed"], row["experiment"], int(row["tick"] or 0), row["agent"], row["trace_id"]),
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def markdown_cell(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    visible_fields = [
        "seed",
        "experiment",
        "tick",
        "agent",
        "policy",
        "selected_action",
        "candidate_count",
        "tool_names",
        "reason",
    ]
    lines = [
        "# DecisionTrace Summary",
        "",
        "Generated from closed synthetic mission-simulation DecisionTrace JSONL files.",
        "",
        "| " + " | ".join(visible_fields) + " |",
        "| " + " | ".join("---" for _ in visible_fields) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(markdown_cell(row[field]) for field in visible_fields) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Flatten DecisionTrace JSONL files into report-ready CSV and Markdown tables.")
    parser.add_argument("--input-dir", type=Path, required=True, help="CLI output directory containing seed_<seed> trace folders.")
    parser.add_argument("--output-csv", type=Path, required=True, help="Destination CSV summary path.")
    parser.add_argument("--output-md", type=Path, required=True, help="Destination Markdown summary path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input_dir.is_dir():
        raise SystemExit(f"input directory does not exist: {args.input_dir}")
    rows = collect_rows(args.input_dir)
    if not rows:
        raise SystemExit(f"no DecisionTrace files found under: {args.input_dir}")
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} trace rows)")
    print(f"Wrote {args.output_md} ({len(rows)} trace rows)")


if __name__ == "__main__":
    main()
