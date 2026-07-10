from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE_DIRS = ["src", "docs", "examples", "models", "scripts", "tests"]
PACKAGE_FILES = ["README.md", "requirements.txt"]
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
SUBMISSION_FILENAME = "DAH2026_\uc18c\uc2a4\ucf54\ub4dc_TSRA-X.zip"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic TSRA-X submission ZIP.")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    zip_path = (
        Path(args.output)
        if args.output
        else DIST / SUBMISSION_FILENAME
    )
    build_zip(zip_path)
    print(zip_path)


def build_zip(zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for filename in PACKAGE_FILES:
            add_file(archive, ROOT / filename)
        for dirname in PACKAGE_DIRS:
            add_tree(archive, ROOT / dirname)
    return zip_path


def add_tree(archive: ZipFile, directory: Path) -> None:
    for path in sorted(directory.rglob("*")):
        if path.is_file() and should_include(path):
            add_file(archive, path)


def add_file(archive: ZipFile, path: Path) -> None:
    info = ZipInfo(str(path.relative_to(ROOT)), date_time=FIXED_ZIP_TIMESTAMP)
    info.create_system = 3
    info.external_attr = (0o100644 & 0xFFFF) << 16
    info.compress_type = ZIP_DEFLATED
    archive.writestr(info, path.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)


def should_include(path: Path) -> bool:
    parts = set(path.parts)
    if ".DS_Store" in parts:
        return False
    if "__pycache__" in parts:
        return False
    if path.suffix in {".pyc", ".pyo"}:
        return False
    return True


if __name__ == "__main__":
    main()
