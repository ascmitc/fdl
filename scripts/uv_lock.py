#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Regenerate uv.lock using public PyPI index.

Overrides any internal/corporate index URL so the lock file is portable.

Usage:
    python scripts/uv_lock.py
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_URL = "https://pypi.org/simple"


def main() -> int:
    print(f"Regenerating uv.lock with index: {INDEX_URL}")
    # Build a clean env that overrides any global/user uv.toml index config.
    # UV_DEFAULT_INDEX overrides the [tool.uv] and global config index-url.
    env = {k: v for k, v in subprocess.os.environ.items()}
    env["UV_DEFAULT_INDEX"] = INDEX_URL
    env["UV_INDEX_URL"] = INDEX_URL
    result = subprocess.run(
        ["uv", "lock", "--default-index", INDEX_URL],
        cwd=REPO_ROOT,
        env=env,
    )
    if result.returncode == 0:
        print("uv.lock regenerated successfully.")
    else:
        print("uv lock failed.", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
