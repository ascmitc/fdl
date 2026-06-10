#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Build the native fdl_core shared library via CMake."""

import argparse
import platform
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "native" / "core"
BUILD_DIR = SOURCE_DIR / "build"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fdl_core native library")
    parser.add_argument(
        "--build-type",
        default="Release",
        choices=["Debug", "Release", "RelWithDebInfo"],
    )
    parser.add_argument("--no-tests", action="store_true", help="Disable building tests")
    parser.add_argument("--run-tests", action="store_true", help="Run CTest after build")
    args = parser.parse_args()

    # Configure
    cmake_args = [
        "cmake",
        "-S",
        str(SOURCE_DIR),
        "-B",
        str(BUILD_DIR),
        f"-DCMAKE_BUILD_TYPE={args.build_type}",
    ]

    # Windows: pin the MSVC toolset so fdl_core.dll is binary-compatible with
    # the older MSVC runtime that some host applications bundle. The pinned
    # toolset (14.36) lives in scripts/msvc_toolset.py. The Visual Studio
    # generator (not Ninja/NMake) is required for -T version=... to take effect.
    if platform.system() == "Windows":
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from msvc_toolset import REQUIRED_MSVC_TOOLSET, resolve_windows_toolset

        platform_toolset, full_version, vs_instance = resolve_windows_toolset()
        print(f"=== Pinning MSVC toolset {platform_toolset} v{full_version} (target {REQUIRED_MSVC_TOOLSET}) ===")
        cmake_args += [
            "-G",
            "Visual Studio 17 2022",
            "-A",
            "x64",
            "-T",
            f"{platform_toolset},version={full_version}",
        ]
        if vs_instance:
            cmake_args.append(f"-DCMAKE_GENERATOR_INSTANCE={vs_instance}")

    if args.no_tests:
        cmake_args.append("-DFDL_BUILD_TESTS=OFF")

    print("=== CMake configure ===")
    result = subprocess.run(cmake_args)
    if result.returncode != 0:
        return result.returncode

    # Build
    print("=== CMake build ===")
    result = subprocess.run(
        [
            "cmake",
            "--build",
            str(BUILD_DIR),
            "--config",
            args.build_type,
            "--parallel",
        ]
    )
    if result.returncode != 0:
        return result.returncode

    # Optionally run C++ tests
    if args.run_tests:
        print("=== CTest ===")
        result = subprocess.run(
            [
                "ctest",
                "--test-dir",
                str(BUILD_DIR),
                "--output-on-failure",
                "-C",
                args.build_type,
            ]
        )
        if result.returncode != 0:
            return result.returncode

    print(f"=== Build complete: {BUILD_DIR} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
