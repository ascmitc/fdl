# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Command-line interface for FDL validation.

Validates FDL files using the handler system, which runs both
format-specific schema validation and semantic validation.
"""

import argparse
import sys
from pathlib import Path

from fdl import FDLValidationError, read_from_file


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fdl-validate",
        description="Validate FDL files against the schema and semantic rules.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="FDL file(s) to validate",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    parsed = parse_args(args)
    failed = False

    for path in parsed.files:
        if not path.exists():
            print(f"FAIL  {path}: file not found", file=sys.stderr)
            failed = True
            continue

        try:
            read_from_file(path, validate=True)
            print(f"OK    {path}")
        except FDLValidationError as e:
            print(f"FAIL  {path}:\n{e}", file=sys.stderr)
            failed = True
        except Exception as e:
            print(f"FAIL  {path}: {e}", file=sys.stderr)
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
