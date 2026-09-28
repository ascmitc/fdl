#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Set the version across all packages in the repository.

Updates every version-bearing file to the given version string so that all
packages stay in sync before tagging and deploying.

Usage:
    python scripts/set_version.py 0.1.0
    python scripts/set_version.py 0.1.0-dev.3
    python scripts/set_version.py --dry-run 0.2.0-rc.1
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Regex: semver with optional pre-release (e.g. 1.2.3 or 1.2.3-dev.4)
_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].+)?$")


def parse_version(version: str) -> tuple[int, int, int]:
    """Return (major, minor, patch) integers from a semver string."""
    m = _SEMVER_RE.match(version)
    if not m:
        print(f"ERROR: '{version}' is not a valid semver string (e.g. 1.2.3 or 1.2.3-dev.4)", file=sys.stderr)
        sys.exit(1)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def update_pyproject(path: Path, new_version: str, dry_run: bool) -> str:
    """Update `version = "..."` in a pyproject.toml (first occurrence only)."""
    text = path.read_text(encoding="utf-8")
    new_text, count = re.subn(r'^version = ".*?"', f'version = "{new_version}"', text, count=1, flags=re.MULTILINE)
    if count == 0:
        print(f"  WARNING: version field not found in {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        return text
    old = re.search(r'^version = "(.*?)"', text, re.MULTILINE).group(1)
    print(f"  {path.relative_to(REPO_ROOT)}: {old} -> {new_version}")
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return new_text


def update_package_json(path: Path, new_version: str, dry_run: bool) -> None:
    """Update the top-level `version` key in a package.json."""
    data = json.loads(path.read_text(encoding="utf-8"))
    old = data.get("version", "<missing>")
    data["version"] = new_version
    print(f"  {path.relative_to(REPO_ROOT)}: {old} -> {new_version}")
    if not dry_run:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_fdl_version_cmake(path: Path, new_version: str, major: int, minor: int, patch: int, dry_run: bool) -> None:
    """Update FDL_CORE_VERSION and FDL_CORE_VERSION_FULL in FDLVersion.cmake.

    FDL_CORE_VERSION must be numeric-only (CMake project(VERSION) requirement).
    FDL_CORE_VERSION_FULL carries the full string including any pre-release suffix.

    NOTE: FDL_ABI_VERSION_MAJOR/MINOR/PATCH are NOT touched here. The C ABI version
    is independent of the package version and must be bumped manually by developers
    only when the C ABI changes.
    """
    base_version = f"{major}.{minor}.{patch}"
    text = path.read_text(encoding="utf-8")

    # Numeric-only version for project(VERSION ...) — strip pre-release
    text, n1 = re.subn(r'set\(FDL_CORE_VERSION\s+".*?"\)', f'set(FDL_CORE_VERSION      "{base_version}")', text)
    # Full version string including pre-release suffix
    text, n2 = re.subn(r'set\(FDL_CORE_VERSION_FULL\s+".*?"\)', f'set(FDL_CORE_VERSION_FULL "{new_version}")', text)

    if not all([n1, n2]):
        print(f"  WARNING: some cmake version fields not found in {path.relative_to(REPO_ROOT)}", file=sys.stderr)

    print(f"  {path.relative_to(REPO_ROOT)}: -> {base_version} / full={new_version}")
    if not dry_run:
        path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Set version across all repo packages.")
    parser.add_argument("version", help="New version string, e.g. 0.1.0 or 0.1.0-dev.3")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing files")
    args = parser.parse_args()

    version = args.version
    major, minor, patch = parse_version(version)
    dry_run = args.dry_run

    if dry_run:
        print(f"DRY RUN — would set version to {version} in:")
    else:
        print(f"Setting version to {version} in:")

    # --- pyproject.toml files ---
    for rel in [
        "pyproject.toml",
        "native/bindings/python/pyproject.toml",
        "packages/fdl_imaging/pyproject.toml",
        "packages/fdl_viewer/pyproject.toml",
        "packages/fdl_frameline_generator/pyproject.toml",
    ]:
        update_pyproject(REPO_ROOT / rel, version, dry_run)

    # --- package.json files ---
    for rel in [
        "native/bindings/node/package.json",
        "examples/web_viewer/server/package.json",
        "examples/web_viewer/client/package.json",
    ]:
        update_package_json(REPO_ROOT / rel, version, dry_run)

    # --- CMake version file ---
    update_fdl_version_cmake(
        REPO_ROOT / "native/core/cmake/FDLVersion.cmake",
        version,
        major,
        minor,
        patch,
        dry_run,
    )

    print("Done." if not dry_run else "Dry run complete — no files written.")


if __name__ == "__main__":
    main()
