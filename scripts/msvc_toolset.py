#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Resolve and report the pinned MSVC toolset for Windows fdl_core builds.

The required toolset is HARDCODED below. Pin to 14.36: it predates VS 17.10 /
toolset 14.40's breaking constexpr std::mutex constructor change, so a DLL built
with it binds correctly to the older MSVCP140.dll/VCRUNTIME140.dll that some host
applications bundle, and remains forward-compatible with the newer system runtime
in standalone use.

MSVC runtimes are backward-compatible (a binary built against an older toolset
runs on newer runtimes) but not forward-compatible, so building against the
older toolset is the fix.

Importable:  from msvc_toolset import resolve_windows_toolset, REQUIRED_MSVC_TOOLSET
Runnable:    python scripts/msvc_toolset.py --print-required-toolset
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

# The single source of truth. Bump only if the oldest runtime we must stay
# compatible with moves. 14.36 == VS 2022 17.6 == platform toolset v143.
REQUIRED_MSVC_TOOLSET = "14.36"


def find_installed_toolset(major_minor: str) -> Path | None:
    """Return the VC/Tools/MSVC/<version> dir matching ``major_minor`` that
    contains cl.exe, or None. ``.name`` is the full version, e.g. '14.36.32532'.
    """
    if platform.system() != "Windows":
        return None
    search_roots = [
        Path(r"C:\Program Files\Microsoft Visual Studio"),
        Path(r"C:\Program Files (x86)\Microsoft Visual Studio"),
    ]
    for vs_root in search_roots:
        if not vs_root.is_dir():
            continue
        for ts_dir in vs_root.glob(f"*/*/VC/Tools/MSVC/{major_minor}.*"):
            if (ts_dir / "bin" / "Hostx64" / "x64" / "cl.exe").is_file():
                return ts_dir
    return None


def msvc_platform_toolset(major_minor: str) -> str:
    """Map an MSVC major.minor to its CMake VS toolset name.

    '14.36' -> 'v143' (v{major}{minor // 10}). The platform group bumps with
    each tens-digit of the minor: 14.2x -> v142, 14.3x -> v143, 14.4x -> v144.
    """
    m = re.match(r"(\d+)\.(\d+)", major_minor)
    if not m:
        return "v143"
    return f"v{int(m.group(1))}{int(m.group(2)) // 10}"


def vs_component_for_toolset(major_minor: str) -> str | None:
    """Map an MSVC toolset major.minor to its VS Installer component id.

    For v143 toolsets (14.30-14.49, shipped with VS 2022 17.x) the VS minor
    equals the MSVC minor minus 30: 14.36 -> 17.6, 14.40 -> 17.10. Returns the
    id to pass to ``vs_installer --add``, or None if the mapping is unknown.
    """
    m = re.match(r"(\d+)\.(\d+)$", major_minor)
    if not m:
        return None
    major, minor = int(m.group(1)), int(m.group(2))
    if major == 14 and 30 <= minor <= 49:
        return f"Microsoft.VisualStudio.Component.VC.{major}.{minor}.17.{minor - 30}.x86.x64"
    return None


def vs_installation_path() -> str | None:
    """Return the latest installed VS instance path via vswhere (used for
    -DCMAKE_GENERATOR_INSTANCE), or None if unavailable."""
    vswhere = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    if not vswhere.is_file():
        return None
    try:
        out = subprocess.run(
            [str(vswhere), "-latest", "-property", "installationPath"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        return (out or "").strip() or None
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def print_toolset_install_help(major_minor: str) -> None:
    """Print actionable instructions when the pinned toolset isn't installed."""
    comp = vs_component_for_toolset(major_minor) or "<unknown component>"
    print()
    print("=" * 78)
    print(f"  ERROR: Required MSVC toolset v{major_minor} is not installed.")
    print("=" * 78)
    print(f"  fdl_core.dll must be built with MSVC toolset v{major_minor} so it stays")
    print("  binary-compatible with the older MSVCP140.dll/VCRUNTIME140.dll that")
    print("  some host applications bundle. A newer toolset crashes on the older")
    print("  runtime (e.g. std::mutex ABI).")
    print()
    print("  Install via the Visual Studio Installer GUI:")
    print("    1. Open the Visual Studio Installer, click 'Modify'")
    print("    2. Open the 'Individual components' tab")
    print(f"    3. Search:  MSVC v143 ... (v{major_minor}-...)")
    print("    4. Check it and click 'Modify' to install (~1.5 GB)")
    print()
    print("  Or silently from the command line:")
    vsi = (
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft Visual Studio" / "Installer" / "vs_installer.exe"
    )
    print(f'    "{vsi}" modify ^')
    print('      --installPath "<your VS install path>" ^')
    print(f"      --add {comp} ^")
    print("      --quiet --norestart")
    print("=" * 78)
    print()


def resolve_windows_toolset() -> tuple[str, str, str | None]:
    """Resolve the pinned toolset for build_native.py.

    Returns (platform_toolset, full_version, vs_instance_path), e.g.
    ('v143', '14.36.32532', 'C:\\...\\2022\\Enterprise'). Prints install help
    and exits(2) if the toolset is not installed. Windows-only caller.
    """
    mm = REQUIRED_MSVC_TOOLSET
    installed = find_installed_toolset(mm)
    if installed is None:
        print_toolset_install_help(mm)
        sys.exit(2)
    return msvc_platform_toolset(mm), installed.name, vs_installation_path()


def main() -> int:
    parser = argparse.ArgumentParser(description="Report the pinned MSVC toolset.")
    parser.add_argument(
        "--print-required-toolset",
        action="store_true",
        help="Print TOOLSET_MAJOR_MINOR / VS_COMPONENT for CI, then exit.",
    )
    args = parser.parse_args()
    if args.print_required_toolset:
        mm = REQUIRED_MSVC_TOOLSET
        print(f"TOOLSET_MAJOR_MINOR={mm}")
        print(f"VS_COMPONENT={vs_component_for_toolset(mm) or 'unknown'}")
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
