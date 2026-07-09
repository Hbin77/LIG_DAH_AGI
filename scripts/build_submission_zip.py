from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE_DIRS = ["src", "docs", "examples", "models", "scripts", "tests"]
PACKAGE_FILES = ["README.md", "requirements.txt"]


def main() -> None:
    DIST.mkdir(exist_ok=True)
    zip_path = DIST / f"DAH2026_sourcecode_TSRA-X_{datetime.now():%Y%m%d_%H%M%S}.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for filename in PACKAGE_FILES:
            add_file(archive, ROOT / filename)
        for dirname in PACKAGE_DIRS:
            add_tree(archive, ROOT / dirname)
    print(zip_path)


def add_tree(archive: ZipFile, directory: Path) -> None:
    for path in sorted(directory.rglob("*")):
        if path.is_file() and should_include(path):
            add_file(archive, path)


def add_file(archive: ZipFile, path: Path) -> None:
    archive.write(path, path.relative_to(ROOT))


def should_include(path: Path) -> bool:
    parts = set(path.parts)
    if "__pycache__" in parts:
        return False
    if path.suffix in {".pyc", ".pyo"}:
        return False
    return True


if __name__ == "__main__":
    main()
