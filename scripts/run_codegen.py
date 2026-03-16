#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Run all codegen targets to regenerate bindings from fdl_api.yaml.

Usage:
    python scripts/run_codegen.py            # regenerate all targets
    python scripts/run_codegen.py --check    # regenerate and fail if output changed
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "native" / "tools"


def _project_python() -> str:
    """Return the Python interpreter inside the project .venv, falling back to sys.executable."""
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


TARGETS = ["python-facade", "python-models", "cpp-raii", "node-addon", "node-facade"]

GENERATED_PATHS = [
    "native/bindings/python/fdl/",
    "native/bindings/python/fdl_ffi/fdl_core_decl.h",
    "native/bindings/cpp/fdl/",
    "native/bindings/node/src/",
]

GENERATED_PYTHON_PATHS = [
    "native/bindings/python/fdl/",
]

GENERATED_CPP_PATHS = [
    "native/bindings/cpp/fdl/",
]

GENERATED_NODE_TS_PATHS = [
    "native/bindings/node/src/",
]

GENERATED_NODE_ADDON_PATHS = [
    "native/bindings/node/src/addon/",
]


def run_codegen() -> int:
    python = _project_python()

    # Generate CFFI declaration header from fdl_core.h (must run before Python targets)
    print("=== Generating: cffi-decl-header ===")
    result = subprocess.run([python, "scripts/generate_cffi_decl.py"], cwd=REPO_ROOT)
    if result.returncode != 0:
        print("FAILED: cffi decl header generation failed", file=sys.stderr)
        return result.returncode

    for target in TARGETS:
        print(f"=== Generating: {target} ===")
        result = subprocess.run(
            [python, "-m", "codegen.generate", "--target", target],
            cwd=TOOLS_DIR,
        )
        if result.returncode != 0:
            print(f"FAILED: codegen target '{target}' exited {result.returncode}", file=sys.stderr)
            return result.returncode
    print("=== All codegen targets completed ===")

    # Post-process: format generated Python with ruff
    print("=== Formatting generated Python ===")
    abs_py_paths = [str(REPO_ROOT / p) for p in GENERATED_PYTHON_PATHS]
    # Prefer uvx (used by lint.py), fall back to ruff on PATH
    if shutil.which("uvx"):
        ruff_cmd = ["uvx", "ruff"]
    elif shutil.which("ruff"):
        ruff_cmd = ["ruff"]
    else:
        ruff_cmd = [python, "-m", "ruff"]
    fmt = subprocess.run(
        [*ruff_cmd, "format", *abs_py_paths],
        cwd=REPO_ROOT,
    )
    if fmt.returncode != 0:
        print("WARNING: ruff format failed (is ruff installed?)", file=sys.stderr)

    # Post-process: format generated C++ with clang-format
    print("=== Formatting generated C++ ===")
    cpp_files = []
    for p in GENERATED_CPP_PATHS:
        d = REPO_ROOT / p
        if d.exists():
            cpp_files.extend(str(f) for f in d.rglob("*.hpp"))
            cpp_files.extend(str(f) for f in d.rglob("*.h"))
    if cpp_files:
        try:
            cfmt = subprocess.run(["clang-format", "-i", *cpp_files], cwd=REPO_ROOT)
            if cfmt.returncode != 0:
                print("WARNING: clang-format failed", file=sys.stderr)
        except FileNotFoundError:
            print("WARNING: clang-format not found, skipping C++ formatting", file=sys.stderr)

    # Post-process: format generated Node.js addon C++ with clang-format
    print("=== Formatting generated Node.js addon C++ ===")
    addon_files = []
    for p in GENERATED_NODE_ADDON_PATHS:
        d = REPO_ROOT / p
        if d.exists():
            addon_files.extend(str(f) for f in d.rglob("*.cc"))
            addon_files.extend(str(f) for f in d.rglob("*.h"))
    if addon_files:
        try:
            cfmt = subprocess.run(["clang-format", "-i", *addon_files], cwd=REPO_ROOT)
            if cfmt.returncode != 0:
                print("WARNING: clang-format failed on addon files", file=sys.stderr)
        except FileNotFoundError:
            print("WARNING: clang-format not found, skipping addon formatting", file=sys.stderr)

    # Post-process: format generated TypeScript with prettier
    print("=== Formatting generated TypeScript ===")
    ts_files = []
    for p in GENERATED_NODE_TS_PATHS:
        d = REPO_ROOT / p
        if d.exists():
            ts_files.extend(str(f) for f in d.rglob("*.ts"))
    if ts_files:
        node_dir = REPO_ROOT / "native" / "bindings" / "node"
        try:
            pfmt = subprocess.run(
                ["npx", "prettier", "--write", *ts_files],
                cwd=node_dir,
            )
            if pfmt.returncode != 0:
                print("WARNING: prettier failed", file=sys.stderr)
        except FileNotFoundError:
            print("WARNING: npx/prettier not found, skipping TS formatting", file=sys.stderr)

    return 0


def check_drift() -> int:
    print("=== Checking for codegen drift ===")
    result = subprocess.run(
        ["git", "diff", "--exit-code", "--stat", *GENERATED_PATHS],
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        print(
            "FAILED: generated files differ from committed versions.\nRun 'python scripts/run_codegen.py' and commit the result.",
            file=sys.stderr,
        )
        return 1

    # Also catch untracked generated files
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", *GENERATED_PATHS],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if untracked.stdout.strip():
        print(
            f"FAILED: untracked generated files found:\n{untracked.stdout}Run 'python scripts/run_codegen.py' and commit the result.",
            file=sys.stderr,
        )
        return 1

    print("=== No codegen drift detected ===")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="After regeneration, fail if generated files differ from committed versions.",
    )
    args = parser.parse_args()

    rc = run_codegen()
    if rc != 0:
        return rc

    if args.check:
        return check_drift()
    return 0


if __name__ == "__main__":
    sys.exit(main())
