#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Verify that all version-bearing files match an expected version.

Checks every file that set_version.py updates and reports mismatches.
Intended to run in CI on tag pushes to catch cases where set_version.py
was not run before tagging.

Usage:
    python scripts/verify_version.py 1.0.1
    python scripts/verify_version.py "$TAG"
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PYPROJECT_FILES = [
    "pyproject.toml",
    "native/bindings/python/pyproject.toml",
    "packages/fdl_imaging/pyproject.toml",
    "packages/fdl_viewer/pyproject.toml",
    "packages/fdl_frameline_generator/pyproject.toml",
]

PACKAGE_JSON_FILES = [
    "native/bindings/node/package.json",
    "examples/web_viewer/server/package.json",
    "examples/web_viewer/client/package.json",
]

CMAKE_VERSION_FILE = "native/core/cmake/FDLVersion.cmake"


def read_pyproject_version(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"(.*?)"', text, re.MULTILINE)
    return m.group(1) if m else None


def read_package_json_version(path: Path) -> str | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("version")


def read_cmake_version_full(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'set\(FDL_CORE_VERSION_FULL\s+"(.*?)"\)', text)
    return m.group(1) if m else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify all repo package versions match the expected version.")
    parser.add_argument("version", help="Expected version string, e.g. 1.0.1 (without leading 'v')")
    args = parser.parse_args()

    expected = args.version.lstrip("v")
    errors = 0

    print(f"Expected version: {expected}\n")

    # --- pyproject.toml files ---
    for rel in PYPROJECT_FILES:
        path = REPO_ROOT / rel
        actual = read_pyproject_version(path)
        if actual != expected:
            print(f"  MISMATCH  {rel}: {actual!r} (expected {expected!r})")
            errors += 1
        else:
            print(f"  OK        {rel}: {actual}")

    # --- package.json files ---
    for rel in PACKAGE_JSON_FILES:
        path = REPO_ROOT / rel
        actual = read_package_json_version(path)
        if actual != expected:
            print(f"  MISMATCH  {rel}: {actual!r} (expected {expected!r})")
            errors += 1
        else:
            print(f"  OK        {rel}: {actual}")

    # --- CMake ---
    path = REPO_ROOT / CMAKE_VERSION_FILE
    actual = read_cmake_version_full(path)
    if actual != expected:
        print(f"  MISMATCH  {CMAKE_VERSION_FILE}: {actual!r} (expected {expected!r})")
        errors += 1
    else:
        print(f"  OK        {CMAKE_VERSION_FILE}: {actual}")

    print()
    if errors:
        print(f"FAILED: {errors} version mismatch(es) found.")
        print(f"Run 'python scripts/set_version.py {expected}' and commit before tagging.")
        sys.exit(1)

    print(f"All versions match {expected}")


if __name__ == "__main__":
    main()
