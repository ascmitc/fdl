#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Check that documentation files contain only ASCII characters.

Windows CI uses cp1252 encoding by default, and mktestdocs calls
pathlib.Path.read_text() without specifying encoding. Non-ASCII
characters (em-dashes, arrows, box-drawing, etc.) cause
UnicodeDecodeError on Windows.

Usage:
    python scripts/check_docs_ascii.py                  # check all docs
    python scripts/check_docs_ascii.py docs/codegen.md  # check specific files
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"


def check_file(path: Path) -> list[str]:
    """Return a list of error messages for non-ASCII characters in *path*."""
    errors = []
    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        for col, ch in enumerate(line, start=1):
            if ord(ch) > 127:
                errors.append(f"{path}:{lineno}:{col}: non-ASCII character U+{ord(ch):04X} {ch!r}")
    return errors


def main() -> int:
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        files = sorted(DOCS_DIR.glob("**/*.md"))

    all_errors = []
    for f in files:
        all_errors.extend(check_file(f))

    if all_errors:
        print(f"Found {len(all_errors)} non-ASCII character(s) in docs:\n")
        for err in all_errors:
            print(f"  {err}")
        print("\nReplace with ASCII equivalents (-- for em-dash, -> for arrow, etc.).")
        return 1

    print(f"All {len(files)} doc files are ASCII-clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
