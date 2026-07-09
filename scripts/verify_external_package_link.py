from __future__ import annotations

import argparse
import hashlib
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "outputs/package/submission_manifest.md"
DEFAULT_TIMEOUT_SEC = 30
DEFAULT_MAX_BYTES = 200 * 1024 * 1024


@dataclass(frozen=True)
class ExpectedPackage:
    zip_path: str
    zip_sha256: str
    zip_bytes: int
    zip_file_count: int


@dataclass(frozen=True)
class DownloadResult:
    url: str
    final_url: str
    status: str
    content_type: str
    content_length: str
    bytes_read: int
    sha256: str
    zip_file_count: int


def manifest_value(manifest_text: str, key: str) -> str:
    match = re.search(rf"^- {re.escape(key)}: `?([^`\n]+)`?$", manifest_text, re.MULTILINE)
    if not match:
        raise ValueError(f"manifest missing {key}")
    return match.group(1).strip()


def manifest_int(manifest_text: str, key: str) -> int:
    value = manifest_value(manifest_text, key)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"manifest {key} is not an integer: {value}") from exc


def read_expected_package(path: Path = MANIFEST_PATH) -> ExpectedPackage:
    manifest_text = path.read_text(encoding="utf-8")
    return ExpectedPackage(
        zip_path=manifest_value(manifest_text, "zip_path"),
        zip_sha256=manifest_value(manifest_text, "zip_sha256"),
        zip_bytes=manifest_int(manifest_text, "zip_bytes"),
        zip_file_count=manifest_int(manifest_text, "zip_file_count"),
    )


def validate_url(url: str, allow_file_url: bool) -> None:
    parsed = urllib.parse.urlsplit(url)
    allowed_schemes = {"http", "https"} | ({"file"} if allow_file_url else set())
    if parsed.scheme not in allowed_schemes:
        raise ValueError(
            f"unsupported URL scheme '{parsed.scheme}'. Use https:// for submitted links."
        )
    if parsed.username or parsed.password:
        raise ValueError("URL must not embed username or password")


def download_and_hash(
    url: str,
    *,
    timeout_sec: int,
    max_bytes: int,
) -> DownloadResult:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "LIG-DAH-AGI-package-link-verifier/1.0"},
        method="GET",
    )
    digest = hashlib.sha256()
    bytes_read = 0
    with urllib.request.urlopen(request, timeout=timeout_sec) as response:
        final_url = response.geturl()
        status = str(getattr(response, "status", None) or "ok")
        content_type = response.headers.get("Content-Type", "")
        content_length = response.headers.get("Content-Length", "")
        with tempfile.NamedTemporaryFile(prefix="dah-package-", suffix=".zip") as tmp:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                bytes_read += len(chunk)
                if bytes_read > max_bytes:
                    raise ValueError(
                        f"download exceeded max bytes: {bytes_read} > {max_bytes}"
                    )
                digest.update(chunk)
                tmp.write(chunk)
            tmp.flush()
            zip_count = count_zip_entries(Path(tmp.name))
    return DownloadResult(
        url=url,
        final_url=final_url,
        status=status,
        content_type=content_type,
        content_length=content_length,
        bytes_read=bytes_read,
        sha256=digest.hexdigest(),
        zip_file_count=zip_count,
    )


def count_zip_entries(path: Path) -> int:
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
    except zipfile.BadZipFile as exc:
        raise ValueError("downloaded payload is not a readable ZIP file") from exc
    if len(names) != len(set(names)):
        raise ValueError("downloaded ZIP contains duplicate paths")
    return len(names)


def compare(expected: ExpectedPackage, result: DownloadResult) -> list[str]:
    issues = []
    if result.bytes_read != expected.zip_bytes:
        issues.append(f"bytes mismatch: {result.bytes_read} != {expected.zip_bytes}")
    if result.sha256 != expected.zip_sha256:
        issues.append(f"sha256 mismatch: {result.sha256} != {expected.zip_sha256}")
    if result.zip_file_count != expected.zip_file_count:
        issues.append(
            f"zip entry count mismatch: {result.zip_file_count} != {expected.zip_file_count}"
        )
    if result.content_length:
        try:
            header_length = int(result.content_length)
        except ValueError:
            header_length = -1
        if header_length >= 0 and header_length != expected.zip_bytes:
            issues.append(
                f"content-length mismatch: {header_length} != {expected.zip_bytes}"
            )
    return issues


def print_result(expected: ExpectedPackage, result: DownloadResult, issues: list[str]) -> None:
    print("External package link verification")
    print(f"- url: {result.url}")
    print(f"- final_url: {result.final_url}")
    print(f"- http_status: {result.status}")
    print(f"- content_type: {result.content_type or 'unknown'}")
    print(f"- content_length: {result.content_length or 'unknown'}")
    print(f"- bytes_read: {result.bytes_read}")
    print(f"- sha256: {result.sha256}")
    print(f"- zip_file_count: {result.zip_file_count}")
    print(f"- expected_zip_path: {expected.zip_path}")
    print(f"- expected_zip_bytes: {expected.zip_bytes}")
    print(f"- expected_zip_sha256: {expected.zip_sha256}")
    print(f"- expected_zip_file_count: {expected.zip_file_count}")
    if issues:
        print("- status: fail")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("- status: pass")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that an externally shared package link downloads the same ZIP "
            "recorded in outputs/package/submission_manifest.md."
        )
    )
    parser.add_argument("url", help="Public download URL to verify.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help="Manifest path. Defaults to outputs/package/submission_manifest.md.",
    )
    parser.add_argument("--timeout-sec", type=int, default=DEFAULT_TIMEOUT_SEC)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument(
        "--allow-file-url",
        action="store_true",
        help="Allow file:// URLs for local self-test only. Submitted links should be https://.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        validate_url(args.url, allow_file_url=args.allow_file_url)
        expected = read_expected_package(args.manifest)
        result = download_and_hash(
            args.url,
            timeout_sec=args.timeout_sec,
            max_bytes=args.max_bytes,
        )
    except urllib.error.URLError as exc:
        raise SystemExit(f"download failed: {exc}") from exc
    except (OSError, ValueError) as exc:
        raise SystemExit(f"verification failed: {exc}") from exc
    issues = compare(expected, result)
    print_result(expected, result, issues)
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
