#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Setup and launch the FDL Web Viewer.

Usage:
    python examples/web_viewer/run.py              # Setup + launch
    python examples/web_viewer/run.py --setup-only # Setup only, don't launch
    python examples/web_viewer/run.py --skip-build # Skip native addon build
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WEB_VIEWER_DIR = REPO_ROOT / "examples" / "web_viewer"
VENV_DIR = REPO_ROOT / ".venv"
VENV_PYTHON = VENV_DIR / "bin" / "python"


def check_python() -> None:
    ver = sys.version_info
    if ver < (3, 10):
        print(f"Error: Python >= 3.10 required, got {ver.major}.{ver.minor}")
        sys.exit(1)
    print(f"Python {ver.major}.{ver.minor}.{ver.micro}")


def check_node() -> None:
    node = shutil.which("node")
    if not node:
        print("Error: Node.js not found. Install Node.js >= 20.")
        sys.exit(1)
    result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
    version = result.stdout.strip()
    major = int(version.lstrip("v").split(".")[0])
    if major < 20:
        print(f"Error: Node.js >= 20 required, got {version}")
        sys.exit(1)
    print(f"Node.js {version}")


def check_uv() -> None:
    uv = shutil.which("uv")
    if not uv:
        print("Error: uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
    print(f"uv {result.stdout.strip()}")


def setup_python_venv() -> None:
    """Run uv sync to install fdl + fdl-imaging + OpenImageIO into .venv."""
    print("\n--- Setting up Python environment ---")
    subprocess.run(
        ["uv", "sync"],
        cwd=REPO_ROOT,
        check=True,
    )

    # Verify imports
    print("Verifying fdl_imaging and OpenImageIO...")
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", "import fdl; import fdl_imaging; import OpenImageIO; print('OK')"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Warning: Import check failed: {result.stderr.strip()}")
        print("Image transforms may not work. Ensure OpenImageIO is installed.")
    else:
        print("Python dependencies verified.")


def build_node_addon(skip: bool) -> None:
    """Build the Node.js native addon."""
    if skip:
        print("\n--- Skipping native addon build ---")
        return

    dist_dir = REPO_ROOT / "native" / "bindings" / "node" / "dist"
    if dist_dir.exists() and any(dist_dir.iterdir()):
        print("\n--- Native addon already built, skipping (use --force-build to rebuild) ---")
        return

    print("\n--- Building Node.js native addon ---")
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build_node.py")],
        cwd=REPO_ROOT,
        check=True,
    )


def install_npm_deps() -> None:
    """Run npm install in the web viewer directory."""
    print("\n--- Installing npm dependencies ---")
    subprocess.run(
        ["npm", "install"],
        cwd=WEB_VIEWER_DIR,
        check=True,
    )


def launch() -> None:
    """Launch the dev servers."""
    print("\n--- Launching FDL Web Viewer ---")
    print(f"  PYTHON_PATH={VENV_PYTHON}")
    print("  Client: http://localhost:5173")
    print("  Server: http://localhost:3001")
    print()

    env = os.environ.copy()
    env["PYTHON_PATH"] = str(VENV_PYTHON)

    try:
        subprocess.run(
            ["npm", "run", "dev"],
            cwd=WEB_VIEWER_DIR,
            env=env,
            check=True,
        )
    except KeyboardInterrupt:
        print("\nShutting down.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup and launch the FDL Web Viewer")
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only run setup steps, don't launch the server",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip building the Node.js native addon",
    )
    parser.add_argument(
        "--force-build",
        action="store_true",
        help="Force rebuild of the Node.js native addon",
    )
    args = parser.parse_args()

    print("=== FDL Web Viewer Setup ===\n")

    # Check prerequisites
    print("Checking prerequisites...")
    check_python()
    check_node()
    check_uv()

    # Setup steps
    setup_python_venv()
    skip_build = args.skip_build and not args.force_build
    build_node_addon(skip_build)
    install_npm_deps()

    if args.setup_only:
        print("\n=== Setup complete ===")
        print("\nTo launch manually:")
        print(f"  cd {WEB_VIEWER_DIR}")
        print(f"  PYTHON_PATH={VENV_PYTHON} npm run dev")
        return

    launch()


if __name__ == "__main__":
    main()
