#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Build the Node.js N-API addon and TypeScript facade.

Prerequisites:
    - libfdl_core must be built first (python scripts/build_native.py)
    - Node.js >= 20, npm, cmake-js (installed via npm)

Usage:
    python scripts/build_node.py              # build addon + TypeScript
    python scripts/build_node.py --run-tests  # build + run vitest
    python scripts/build_node.py --addon-only # build only the N-API addon
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NODE_DIR = REPO_ROOT / "native" / "bindings" / "node"
CORE_BUILD_DIR = REPO_ROOT / "native" / "core" / "build"


def _core_lib_search_dirs() -> list[Path]:
    """Directories that may contain the built fdl_core library.

    On Windows/MSVC (multi-config generators) the DLL lands in a per-config
    subdir (Release/), so search it in addition to the base build dir.
    """
    return [CORE_BUILD_DIR, CORE_BUILD_DIR / "Release"]


def check_prerequisites() -> list[str]:
    """Check that required tools are available. Returns list of errors."""
    errors = []
    if not shutil.which("node"):
        errors.append("node not found — install Node.js >= 20")
    if not shutil.which("npm"):
        errors.append("npm not found — install Node.js >= 20")
    if not shutil.which("cmake"):
        errors.append("cmake not found — install cmake")

    # Check that libfdl_core exists (search base build dir + Windows Release/ subdir)
    core_lib = None
    for search_dir in _core_lib_search_dirs():
        for pattern in ["libfdl_core.dylib", "libfdl_core.so", "fdl_core.dll", "libfdl_core.a"]:
            candidates = list(search_dir.glob(pattern))
            if candidates:
                core_lib = candidates[0]
                break
        if core_lib is not None:
            break
    if core_lib is None:
        errors.append(f"libfdl_core not found in {CORE_BUILD_DIR}.\n  Build it first: python scripts/build_native.py")

    return errors


def npm_install() -> int:
    """Install Node.js dependencies."""
    print("=== npm install ===")
    # Use --ignore-scripts to avoid triggering cmake-js during install
    result = subprocess.run(
        ["npm", "install", "--ignore-scripts"],
        cwd=NODE_DIR,
    )
    return result.returncode


def build_addon() -> int:
    """Build the N-API addon via cmake-js."""
    print("=== Building N-API addon (cmake-js) ===")
    result = subprocess.run(
        ["npx", "cmake-js", "compile", "-d", str(NODE_DIR)],
        cwd=NODE_DIR,
        env={
            **__import__("os").environ,
            "FDL_CORE_LIB_DIR": str(CORE_BUILD_DIR),
        },
    )
    if result.returncode != 0:
        return result.returncode

    # Verify the .node file was produced
    addon_path = NODE_DIR / "build" / "fdl_addon.node"
    if not addon_path.exists():
        # cmake-js may put it in build/Release on some platforms
        addon_path = NODE_DIR / "build" / "Release" / "fdl_addon.node"
    if addon_path.exists():
        print(f"  Addon built: {addon_path}")
    else:
        print("WARNING: fdl_addon.node not found in expected locations", file=sys.stderr)

    # Bundle libfdl_core next to the addon so the rpath (@loader_path / $ORIGIN)
    # resolves at runtime without needing the source tree.
    _bundle_libfdl_core(addon_path.parent if addon_path.exists() else NODE_DIR / "build")

    return 0


def _bundle_libfdl_core(dest_dir: Path) -> None:
    """Copy the shared libfdl_core library into *dest_dir* next to the addon."""
    lib_patterns = [
        "libfdl_core.dylib",  # macOS unversioned symlink  → binary copy
        "libfdl_core.*.dylib",  # macOS versioned: libfdl_core.0.dylib, libfdl_core.0.6.0.dylib
        "libfdl_core.so",  # Linux unversioned symlink  → binary copy
        "libfdl_core.so.*",  # Linux versioned: libfdl_core.so.0, libfdl_core.so.0.6.0
        "fdl_core.dll",
    ]
    for search_dir in _core_lib_search_dirs():
        for pattern in lib_patterns:
            for src in search_dir.glob(pattern):
                dst = dest_dir / src.name
                if dst.resolve() == src.resolve():
                    continue
                shutil.copy2(src, dst)
                print(f"  Bundled: {src.name} -> {dst}")


def build_typescript() -> int:
    """Compile TypeScript to JavaScript."""
    print("=== Compiling TypeScript ===")
    result = subprocess.run(
        ["npx", "tsc"],
        cwd=NODE_DIR,
    )
    return result.returncode


def run_tests() -> int:
    """Run vitest test suite."""
    print("=== Running vitest ===")
    result = subprocess.run(
        ["npx", "vitest", "run"],
        cwd=NODE_DIR,
    )
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-tests", action="store_true", help="Run vitest after build")
    parser.add_argument("--addon-only", action="store_true", help="Only build the N-API addon (skip TypeScript)")
    parser.add_argument("--skip-install", action="store_true", help="Skip npm install (use if node_modules already present)")
    args = parser.parse_args()

    # Check prerequisites
    errors = check_prerequisites()
    if errors:
        print("Missing prerequisites:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    # Install deps
    if not args.skip_install:
        rc = npm_install()
        if rc != 0:
            print("FAILED: npm install", file=sys.stderr)
            return rc

    # Build addon
    rc = build_addon()
    if rc != 0:
        print("FAILED: addon build", file=sys.stderr)
        return rc

    if args.addon_only:
        print("=== Addon build complete ===")
        return 0

    # Build TypeScript
    rc = build_typescript()
    if rc != 0:
        print("FAILED: TypeScript compilation", file=sys.stderr)
        return rc

    # Optionally run tests
    if args.run_tests:
        rc = run_tests()
        if rc != 0:
            print("FAILED: tests", file=sys.stderr)
            return rc

    print("=== Node.js build complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
