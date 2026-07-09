from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "outputs/package/submission_manifest.md"
ZIP_PATH = ROOT / "outputs/package/DAH2026_source_LIG_DAH_AGI.zip"


def run_step(label: str, command: list[str]) -> None:
    print(f"== {label}", flush=True)
    print(" ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def manifest_value(manifest_text: str, key: str) -> str:
    match = re.search(rf"^- {re.escape(key)}: `?([^`\n]+)`?$", manifest_text, re.MULTILINE)
    if not match:
        raise ValueError(f"manifest missing {key}")
    return match.group(1).strip()


def print_summary() -> None:
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    print("== Release candidate summary", flush=True)
    for key in ["zip_path", "zip_file_count", "zip_bytes", "zip_sha256"]:
        print(f"{key}={manifest_value(manifest_text, key)}")
    print("release_handoff=outputs/package/release_handoff.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the local release-candidate freeze sequence: build package, "
            "generate handoff, verify state, and self-test the package link verifier."
        )
    )
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Pass --require-clean to verify_submission_state.py. Use after committing generated files.",
    )
    parser.add_argument(
        "--skip-link-self-test",
        action="store_true",
        help="Skip local file:// self-test for verify_external_package_link.py.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    python = sys.executable

    run_step("Build source package", [python, "scripts/build_submission_package.py"])
    run_step("Generate release handoff", [python, "scripts/generate_release_handoff.py"])

    verify_command = [python, "scripts/verify_submission_state.py"]
    if args.require_clean:
        verify_command.append("--require-clean")
    run_step("Verify submission state", verify_command)

    if not args.skip_link_self_test:
        run_step(
            "Verify local package link self-test",
            [
                python,
                "scripts/verify_external_package_link.py",
                f"file://{ZIP_PATH}",
                "--allow-file-url",
            ],
        )

    print_summary()
    print("freeze_status=pass")


if __name__ == "__main__":
    main()
