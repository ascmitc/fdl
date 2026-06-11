#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Build the WebAssembly (Emscripten) bindings.

Prerequisites:
    - Emscripten SDK active in the environment (emcc, emcmake on PATH).
      Use emsdk 3.1.73 — the version pinned in CI (.github/workflows/main.yml).
      Other versions may produce subtly different Embind output.
    - cmake, make

Activates emsdk:
    source <emsdk>/emsdk_env.sh

Usage:
    python scripts/build_wasm.py                  # configure + build (Release)
    python scripts/build_wasm.py --debug          # build with debug symbols
    python scripts/build_wasm.py --clean          # remove build directory first
    python scripts/build_wasm.py --regen          # run codegen for wasm-bindings first

Output:
    native/bindings/wasm/build/dist/fdl_module.{mjs,wasm}
    -> copied to native/bindings/node/wasm/  (consumed by the @asc-mitc/fdl/wasm
       package entry at runtime)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WASM_DIR = REPO_ROOT / "native" / "bindings" / "wasm"
BUILD_DIR = WASM_DIR / "build"
NODE_WASM_OUT = REPO_ROOT / "native" / "bindings" / "node" / "wasm"


def check_prerequisites() -> list[str]:
    errors: list[str] = []
    if not shutil.which("emcmake"):
        errors.append("emcmake not found — activate the Emscripten SDK first (source <emsdk>/emsdk_env.sh)")
    if not shutil.which("cmake"):
        errors.append("cmake not found — install cmake")
    bindings_cpp = WASM_DIR / "src" / "bindings.cpp"
    if not bindings_cpp.exists():
        errors.append(f"{bindings_cpp} not found — run `python scripts/run_codegen.py` or pass --regen")
    return errors


def run_codegen() -> int:
    print("=== Generating WASM Embind bindings ===")
    tools_dir = REPO_ROOT / "native" / "tools"
    result = subprocess.run(
        [sys.executable, "-m", "codegen.generate", "--target", "wasm-bindings"],
        cwd=tools_dir,
    )
    return result.returncode


def configure(build_type: str) -> int:
    print(f"=== emcmake configure ({build_type}) ===")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [
            "emcmake",
            "cmake",
            "-S",
            str(WASM_DIR),
            "-B",
            str(BUILD_DIR),
            f"-DCMAKE_BUILD_TYPE={build_type}",
        ],
        cwd=REPO_ROOT,
    ).returncode


def build() -> int:
    print("=== cmake --build ===")
    return subprocess.run(
        [
            "cmake",
            "--build",
            str(BUILD_DIR),
            "-j",
            str(os.cpu_count() or 2),
        ],
        cwd=REPO_ROOT,
    ).returncode


def copy_artifacts() -> int:
    src_dist = BUILD_DIR / "dist"
    if not src_dist.exists():
        print(f"ERROR: build output dir not found: {src_dist}", file=sys.stderr)
        return 1
    NODE_WASM_OUT.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for pattern in ("fdl_module.mjs", "fdl_module.wasm", "fdl_module.wasm.map"):
        for f in src_dist.glob(pattern):
            dst = NODE_WASM_OUT / f.name
            shutil.copy2(f, dst)
            copied.append(str(dst))
    if not copied:
        print(f"ERROR: no WASM artifacts produced in {src_dist}", file=sys.stderr)
        return 1
    print("=== Copied artifacts ===")
    for c in copied:
        print(f"  {c}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--debug", action="store_true", help="Build with debug symbols")
    parser.add_argument("--clean", action="store_true", help="Remove build dir first")
    parser.add_argument("--regen", action="store_true", help="Run codegen before building")
    args = parser.parse_args()

    if args.regen:
        rc = run_codegen()
        if rc != 0:
            return rc

    errors = check_prerequisites()
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.clean and BUILD_DIR.exists():
        print(f"=== Removing {BUILD_DIR} ===")
        shutil.rmtree(BUILD_DIR)

    build_type = "Debug" if args.debug else "Release"
    rc = configure(build_type)
    if rc != 0:
        return rc

    rc = build()
    if rc != 0:
        return rc

    return copy_artifacts()


if __name__ == "__main__":
    sys.exit(main())
