#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Build script for FDL Viewer application.

Creates a standalone executable using PyInstaller with optional
macOS code signing and DMG creation.

Usage:
    python compile.py [--no-sign] [--no-dmg]

Environment Variables:
    CODE_SIGNING_CERTIFICATE: Certificate name for macOS signing
    APPLE_TEAM_ID: Apple Team ID for notarization
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_version() -> str:
    """
    Get the application version from package.

    Returns
    -------
    str
        Version string.
    """
    try:
        from fdl_viewer import __version__

        return __version__
    except ImportError:
        return "0.1.0"


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns
    -------
    Path
        Project root path.
    """
    return Path(__file__).parent


def clean_build_dirs() -> None:
    """Clean previous build directories."""
    project_root = get_project_root()
    dirs_to_clean = ["build", "dist", "__pycache__"]

    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"Cleaning {dir_path}...")
            shutil.rmtree(dir_path)

    # Clean spec file
    spec_files = list(project_root.glob("*.spec"))
    for spec_file in spec_files:
        print(f"Removing {spec_file}...")
        spec_file.unlink()


def build_with_pyinstaller() -> Path:
    """
    Build the application with PyInstaller.

    Returns
    -------
    Path
        Path to the built application.
    """
    project_root = get_project_root()
    app_name = "FDL Viewer"
    entry_script = project_root / "src" / "fdl_viewer" / "main.py"

    # Check for resources
    resources_dir = project_root / "src" / "fdl_viewer" / "resources"

    # Build command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        app_name,
        "--onedir",
        "--windowed",
        "--noconfirm",
        "--clean",
    ]

    # Add icon if available
    if platform.system() == "Darwin":
        icon_path = resources_dir / "icons" / "fdl_viewer.icns"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
    elif platform.system() == "Windows":
        icon_path = resources_dir / "icons" / "fdl_viewer.ico"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])

    # Add resources as data
    if resources_dir.exists():
        if platform.system() == "Windows":
            cmd.extend(["--add-data", f"{resources_dir};resources"])
        else:
            cmd.extend(["--add-data", f"{resources_dir}:resources"])

    # Collect workspace packages — editable installs require --collect-all
    # to force PyInstaller to bundle the actual package files
    collect_all = [
        "fdl",
        "fdl_ffi",
        "fdl_imaging",
    ]
    for pkg in collect_all:
        cmd.extend(["--collect-all", pkg])

    # Hidden imports for dependencies not automatically detected
    hidden_imports = [
        # PySide6
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        # OpenImageIO requires numpy for pixel data
        "numpy",
        "numpy.core._methods",
        "numpy.lib.format",
        # OpenImageIO itself
        "OpenImageIO",
    ]
    for hidden in hidden_imports:
        cmd.extend(["--hidden-import", hidden])

    # Entry script
    cmd.append(str(entry_script))

    print("Building with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=project_root)
    if result.returncode != 0:
        raise RuntimeError("PyInstaller build failed")

    # Return path to built app
    if platform.system() == "Darwin":
        return project_root / "dist" / f"{app_name}.app"
    elif platform.system() == "Windows":
        return project_root / "dist" / app_name / f"{app_name}.exe"
    else:
        return project_root / "dist" / app_name / app_name


def sign_macos_app(app_path: Path) -> None:
    """
    Sign the macOS application.

    Parameters
    ----------
    app_path : Path
        Path to the .app bundle.
    """
    cert = os.environ.get("CODE_SIGNING_CERTIFICATE")
    if not cert:
        print("Warning: CODE_SIGNING_CERTIFICATE not set, skipping signing")
        return

    if not app_path.exists():
        raise FileNotFoundError(f"App not found: {app_path}")

    print(f"Signing {app_path}...")

    # Sign all nested frameworks and binaries first
    cmd = [
        "codesign",
        "--force",
        "--deep",
        "--timestamp",
        "--options",
        "runtime",
        "--sign",
        cert,
        str(app_path),
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("Code signing failed")

    # Verify signature
    verify_cmd = ["codesign", "--verify", "--deep", "--strict", str(app_path)]
    result = subprocess.run(verify_cmd)
    if result.returncode != 0:
        raise RuntimeError("Signature verification failed")

    print("Code signing complete")


def create_dmg(app_path: Path, version: str) -> Path:
    """
    Create a DMG disk image for macOS.

    Parameters
    ----------
    app_path : Path
        Path to the .app bundle.
    version : str
        Application version.

    Returns
    -------
    Path
        Path to the created DMG.
    """
    project_root = get_project_root()
    app_name = app_path.stem
    dmg_name = f"{app_name}-{version}.dmg"
    dmg_path = project_root / "dist" / dmg_name

    # Remove existing DMG
    if dmg_path.exists():
        dmg_path.unlink()

    print(f"Creating DMG: {dmg_path}")

    # Create DMG using hdiutil
    cmd = [
        "hdiutil",
        "create",
        "-volname",
        app_name,
        "-srcfolder",
        str(app_path),
        "-ov",
        "-format",
        "UDZO",
        str(dmg_path),
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("DMG creation failed")

    return dmg_path


def sign_dmg(dmg_path: Path) -> None:
    """
    Sign the DMG disk image.

    Parameters
    ----------
    dmg_path : Path
        Path to the DMG file.
    """
    cert = os.environ.get("CODE_SIGNING_CERTIFICATE")
    if not cert:
        print("Warning: CODE_SIGNING_CERTIFICATE not set, skipping DMG signing")
        return

    print(f"Signing DMG: {dmg_path}")

    cmd = [
        "codesign",
        "--force",
        "--timestamp",
        "--sign",
        cert,
        str(dmg_path),
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("DMG signing failed")

    print("DMG signing complete")


def notarize_app(dmg_path: Path) -> None:
    """
    Notarize the application with Apple.

    Parameters
    ----------
    dmg_path : Path
        Path to the DMG file.
    """
    apple_id = os.environ.get("APPLE_ID")
    app_password = os.environ.get("APPLE_APP_PASSWORD")
    team_id = os.environ.get("APPLE_TEAM_ID")

    if not all([apple_id, app_password, team_id]):
        print("Warning: Apple credentials not set, skipping notarization")
        print("Set APPLE_ID, APPLE_APP_PASSWORD, and APPLE_TEAM_ID for notarization")
        return

    print(f"Notarizing {dmg_path}...")

    cmd = [
        "xcrun",
        "notarytool",
        "submit",
        str(dmg_path),
        "--apple-id",
        apple_id,
        "--password",
        app_password,
        "--team-id",
        team_id,
        "--wait",
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("Notarization failed")

    # Staple the notarization ticket
    staple_cmd = ["xcrun", "stapler", "staple", str(dmg_path)]
    result = subprocess.run(staple_cmd)
    if result.returncode != 0:
        print("Warning: Stapling failed, but notarization succeeded")

    print("Notarization complete")


def main():
    """Main build entry point."""
    parser = argparse.ArgumentParser(description="Build FDL Viewer application")
    parser.add_argument("--no-clean", action="store_true", help="Skip cleaning build directories")
    parser.add_argument("--no-sign", action="store_true", help="Skip code signing")
    parser.add_argument("--no-dmg", action="store_true", help="Skip DMG creation (macOS only)")
    parser.add_argument("--notarize", action="store_true", help="Notarize the app (macOS only)")
    args = parser.parse_args()

    print("=" * 60)
    print("FDL Viewer Build Script")
    print("=" * 60)

    version = get_version()
    print(f"Version: {version}")
    print(f"Platform: {platform.system()}")

    # Clean
    if not args.no_clean:
        clean_build_dirs()

    # Build
    app_path = build_with_pyinstaller()
    print(f"Built: {app_path}")

    # macOS-specific steps
    if platform.system() == "Darwin":
        # Sign app
        if not args.no_sign:
            sign_macos_app(app_path)

        # Create DMG
        if not args.no_dmg:
            dmg_path = create_dmg(app_path, version)
            print(f"Created: {dmg_path}")

            # Sign DMG
            if not args.no_sign:
                sign_dmg(dmg_path)

            # Notarize
            if args.notarize:
                notarize_app(dmg_path)

    print("=" * 60)
    print("Build complete!")
    print("=" * 60)

    # Print output location
    dist_dir = get_project_root() / "dist"
    print(f"\nOutput directory: {dist_dir}")
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            print(f"  - {item.name}")


if __name__ == "__main__":
    main()
