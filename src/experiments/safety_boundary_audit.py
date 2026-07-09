from __future__ import annotations

import argparse
import ast
import csv
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/safety_boundary_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/safety_boundary_audit.md"

CORE_DIRS = [
    "src/agents",
    "src/aura",
    "src/tsra_r",
    "src/simulator",
    "src/shared",
    "src/ml",
]

AUTOMATION_DIRS = [
    "scripts",
    "src/experiments",
]

ALLOWED_NETWORK_AUTOMATION = {
    "scripts/verify_external_package_link.py",
}

ALLOWED_SUBPROCESS_AUTOMATION = {
    "scripts/freeze_release_candidate.py",
    "scripts/generate_release_handoff.py",
    "scripts/verify_submission_state.py",
    "src/experiments/submission_readiness_audit.py",
}

BLOCKED_IMPORT_ROOTS = {
    "ftplib",
    "nmap",
    "paramiko",
    "pcap",
    "pyshark",
    "requests",
    "scapy",
    "socket",
    "telnetlib",
}

NETWORK_IMPORT_ROOTS = BLOCKED_IMPORT_ROOTS | {
    "urllib",
}

SHELL_IMPORT_ROOTS = {
    "subprocess",
}

NETWORK_CALL_PREFIXES = (
    "ftplib.FTP",
    "nmap.PortScanner",
    "paramiko.",
    "pyshark.",
    "requests.",
    "scapy.",
    "socket.",
    "telnetlib.Telnet",
    "urllib.request.urlopen",
)

SHELL_CALLS = {
    "os.popen",
    "os.system",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.run",
}

EXCLUDED_ZIP_SUFFIXES = (
    ".DS_Store",
    ".pkl",
    ".pt",
    ".pyc",
)

EXCLUDED_ZIP_PARTS = {
    "__pycache__",
}

SAFETY_BOUNDARY = (
    "closed simulation safety-boundary audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "area",
    "requirement",
    "evidence",
    "observed",
    "status",
    "allowed_exceptions",
    "next_gate",
    "safety_boundary",
]


@dataclass(frozen=True)
class PrimitiveHit:
    path: str
    line: int
    kind: str
    value: str

    def display(self) -> str:
        return f"{self.path}:{self.line}:{self.kind}:{self.value}"


def python_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for rel in paths:
        root = ROOT / rel
        if not root.exists():
            continue
        if root.is_file() and root.suffix == ".py":
            files.append(root)
            continue
        files.extend(sorted(path for path in root.rglob("*.py") if path.is_file()))
    return sorted(files)


def primitive_hits(path: Path) -> list[PrimitiveHit]:
    rel = path.relative_to(ROOT).as_posix()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
    except SyntaxError as exc:
        return [PrimitiveHit(rel, exc.lineno or 0, "syntax_error", str(exc))]

    hits: list[PrimitiveHit] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in NETWORK_IMPORT_ROOTS or root in SHELL_IMPORT_ROOTS:
                    hits.append(PrimitiveHit(rel, node.lineno, "import", alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            if root in NETWORK_IMPORT_ROOTS or root in SHELL_IMPORT_ROOTS:
                hits.append(PrimitiveHit(rel, node.lineno, "import_from", module))
        elif isinstance(node, ast.Call):
            name = qualified_name(node.func)
            if not name:
                continue
            if name in SHELL_CALLS or any(
                name == prefix or name.startswith(prefix)
                for prefix in NETWORK_CALL_PREFIXES
            ):
                hits.append(PrimitiveHit(rel, node.lineno, "call", name))
    return hits


def qualified_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = qualified_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
        return node.attr
    return ""


def classify_hits(hits: list[PrimitiveHit]) -> tuple[list[PrimitiveHit], list[PrimitiveHit]]:
    network_hits = []
    shell_hits = []
    for hit in hits:
        root = hit.value.split(".", 1)[0]
        if root in SHELL_IMPORT_ROOTS or hit.value in SHELL_CALLS:
            shell_hits.append(hit)
        elif root in NETWORK_IMPORT_ROOTS or any(
            hit.value == prefix or hit.value.startswith(prefix)
            for prefix in NETWORK_CALL_PREFIXES
        ):
            network_hits.append(hit)
    return network_hits, shell_hits


def read_text(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def latest_zip_path() -> Path:
    manifest = read_text("outputs/package/submission_manifest.md")
    for line in manifest.splitlines():
        if line.startswith("- zip_path:"):
            value = line.split(":", 1)[1].strip().strip("`")
            return ROOT / value
    return ROOT / "outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip"


def zip_exclusion_hits(zip_path: Path) -> list[str]:
    if not zip_path.exists():
        return [f"missing:{zip_path.relative_to(ROOT).as_posix()}"]
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    hits = []
    for name in names:
        if any(part in name.split("/") for part in EXCLUDED_ZIP_PARTS):
            hits.append(name)
        elif name.endswith(EXCLUDED_ZIP_SUFFIXES):
            hits.append(name)
    return hits


def row(
    *,
    check_id: str,
    area: str,
    requirement: str,
    evidence: list[str],
    observed: str,
    ok: bool,
    allowed_exceptions: str,
    next_gate: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "requirement": requirement,
        "evidence": " | ".join(evidence),
        "observed": observed,
        "status": "pass" if ok else "fail",
        "allowed_exceptions": allowed_exceptions,
        "next_gate": next_gate,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def build_rows() -> list[dict[str, str]]:
    core_files = python_files(CORE_DIRS)
    core_hits = [hit for path in core_files for hit in primitive_hits(path)]
    core_network_hits, core_shell_hits = classify_hits(core_hits)

    automation_files = python_files(AUTOMATION_DIRS)
    automation_hits = [hit for path in automation_files for hit in primitive_hits(path)]
    automation_network_hits, automation_shell_hits = classify_hits(automation_hits)
    unexpected_network_hits = [
        hit for hit in automation_network_hits if hit.path not in ALLOWED_NETWORK_AUTOMATION
    ]
    unexpected_shell_hits = [
        hit for hit in automation_shell_hits if hit.path not in ALLOWED_SUBPROCESS_AUTOMATION
    ]

    aura_text = read_text("src/aura/candidate_generator.py")
    schema_text = read_text("src/shared/schemas.py")
    boundary_sources = [
        "README.md",
        "docs/agents/AURA_ATTACK_AGENT.md",
        "docs/agents/TSRA_R_DEFENSE_AGENT.md",
        "docs/agents/AGENT_RUNTIME.md",
        "outputs/report_tables/aura_coa_cards.csv",
        "outputs/report_tables/incident_summary.csv",
        "outputs/report_tables/agent_collaboration_graph.csv",
    ]
    boundary_text = "\n".join(read_text(path) for path in boundary_sources)
    manifest_text = read_text("outputs/package/submission_manifest.md")
    zip_path = latest_zip_path()
    zip_exists = zip_path.exists()
    excluded_zip_hits = zip_exclusion_hits(zip_path) if zip_exists else []
    manifest_has_exclusion_policy = all(
        token in manifest_text
        for token in ["__pycache__", "*.pyc", "*.pkl", "*.pt", "outputs/datasets/"]
    )

    return [
        row(
            check_id="S01",
            area="Operational core source",
            requirement="Core agent/simulator/model code must not import or call live network, RF, exploit, or shell primitives.",
            evidence=CORE_DIRS,
            observed=(
                f"files_scanned={len(core_files)}; "
                f"network_hits={len(core_network_hits)}; "
                f"shell_hits={len(core_shell_hits)}"
            ),
            ok=not core_network_hits and not core_shell_hits,
            allowed_exceptions="none in operational core",
            next_gate="Any future core primitive hit must be removed or moved into an explicitly documented verifier-only path.",
        ),
        row(
            check_id="S02",
            area="Automation exceptions",
            requirement="External access primitives may appear only in package-link or Git/local verification automation.",
            evidence=["scripts", "src/experiments"],
            observed=(
                f"network_hits={format_hits(automation_network_hits)}; "
                f"shell_hits={format_hits(automation_shell_hits)}; "
                f"unexpected_network_hits={len(unexpected_network_hits)}; "
                f"unexpected_shell_hits={len(unexpected_shell_hits)}"
            ),
            ok=not unexpected_network_hits and not unexpected_shell_hits,
            allowed_exceptions=(
                "urllib only in scripts/verify_external_package_link.py; "
                "subprocess only in release/Git verification scripts"
            ),
            next_gate="New automation that touches network or subprocess must be listed in this allowlist and justified.",
        ),
        row(
            check_id="S03",
            area="Attack-effect schema",
            requirement="AURA must emit simulated AttackCandidate/AttackEvent effects, not operational commands.",
            evidence=["src/aura/candidate_generator.py", "src/shared/schemas.py"],
            observed=(
                f"uses_AttackCandidate={'AttackCandidate(' in aura_text}; "
                f"uses_AttackEvent={'class AttackEvent' in schema_text}; "
                f"simulated_effect_fields={all(field in schema_text for field in ['latency_ms_add', 'jitter_ms_add', 'packet_loss_add', 'bandwidth_limit_mbps', 'queue_pressure'])}"
            ),
            ok=(
                "AttackCandidate(" in aura_text
                and "class AttackEvent" in schema_text
                and all(
                    field in schema_text
                    for field in [
                        "latency_ms_add",
                        "jitter_ms_add",
                        "packet_loss_add",
                        "bandwidth_limit_mbps",
                        "queue_pressure",
                    ]
                )
                and not core_network_hits
            ),
            allowed_exceptions="packet_loss_add is a simulator metric field, not packet generation",
            next_gate="Attack changes must stay as simulator effect fields and regenerate COA/safety evidence.",
        ),
        row(
            check_id="S04",
            area="Safety-boundary text",
            requirement="Core handoff artifacts must explicitly state closed simulation, no RF, no exploit, and no live network action.",
            evidence=boundary_sources,
            observed=(
                f"closed_simulation={'closed simulation' in boundary_text.lower() or '폐쇄형' in boundary_text}; "
                f"no_rf={'no RF' in boundary_text or '실제 RF' in boundary_text}; "
                f"no_exploit={'no exploit' in boundary_text or 'exploit' in boundary_text}; "
                f"no_live_network={'live network' in boundary_text or '실제 네트워크' in boundary_text}"
            ),
            ok=(
                ("closed simulation" in boundary_text.lower() or "폐쇄형" in boundary_text)
                and ("no RF" in boundary_text or "실제 RF" in boundary_text)
                and ("no exploit" in boundary_text or "exploit" in boundary_text)
                and ("live network" in boundary_text or "실제 네트워크" in boundary_text)
            ),
            allowed_exceptions="safety terms may appear in negative boundary statements",
            next_gate="New user-facing artifacts must carry the same closed-simulation boundary.",
        ),
        row(
            check_id="S05",
            area="Submission package safety",
            requirement="Submission ZIP must exclude caches, generated model binaries, and other non-source execution artifacts.",
            evidence=["outputs/package/submission_manifest.md", zip_path.relative_to(ROOT).as_posix()],
            observed=(
                f"zip_path={zip_path.relative_to(ROOT).as_posix()}; "
                f"zip_exists={zip_exists}; "
                f"manifest_has_exclusion_policy={manifest_has_exclusion_policy}; "
                f"excluded_artifact_hits={len(excluded_zip_hits)}"
            ),
            ok=manifest_has_exclusion_policy and not excluded_zip_hits,
            allowed_exceptions="model metric JSON is included; .pkl/.pt binaries are excluded",
            next_gate="Any package rule change must keep binary/cache exclusions passing.",
        ),
    ]


def format_hits(hits: list[PrimitiveHit]) -> str:
    if not hits:
        return "none"
    paths = sorted({hit.path for hit in hits})
    return ",".join(paths)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Safety Boundary Audit",
        "",
        "This audit checks that the project remains a closed simulation prototype.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| check_id | area | status | observed | allowed_exceptions |",
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
                    md(item["allowed_exceptions"]),
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
                f"- Allowed exceptions: {item['allowed_exceptions']}",
                f"- Next gate: {item['next_gate']}",
                f"- Safety boundary: {item['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit closed-simulation safety boundaries.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any safety row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failures = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} rows)")
    print(f"Wrote {args.output_md} ({len(rows)} rows)")
    if failures:
        print(f"Failed safety boundary rows: {len(failures)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
