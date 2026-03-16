#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Update expected EXR golden images from test outputs.

After regenerating source TIFFs and running the parameterized tests, this
script copies the processed test outputs to the expected EXR locations.

Prerequisites:
    1. Run packages/fdl/scripts/regenerate_source_tiffs.py
    2. Run: python -m pytest tests/test_templates_parameterized.py -v

Usage:
    python packages/fdl/scripts/update_expected_exrs.py                            # update all
    python packages/fdl/scripts/update_expected_exrs.py --dry-run                  # show what would be done
    python packages/fdl/scripts/update_expected_exrs.py --outputs-dir tests/outputs # custom outputs dir
"""

import argparse
import shutil
import sys
from pathlib import Path

from fdl.testing import (
    SCENARIO_CONFIGS,
    BaseFDLTestCase,
    get_scenario_paths,
)

RESOURCES_DIR = BaseFDLTestCase.get_resources_folder()
SAMPLE_FILES_DIR = RESOURCES_DIR / "Scenarios_For_Implementers"


def update_expected_exrs(outputs_dir: Path, dry_run: bool = False) -> tuple[int, int, int]:
    """Update expected EXR files from test outputs.

    Returns (updated, skipped, missing) counts.
    """
    updated = 0
    skipped = 0
    missing = 0

    for scen_num, config in sorted(SCENARIO_CONFIGS.items()):
        if config.is_error_test:
            continue

        for variant in config.variants:
            # Build test name matching test_templates_parameterized.py:72
            suffix = variant.test_name_suffix if variant.test_name_suffix else variant.letter.lower()
            test_name = f"test_apply_fdl_template_scen{scen_num}_{suffix}"

            # Get expected EXR path
            paths = get_scenario_paths(SAMPLE_FILES_DIR, config, variant)
            expected_exr = paths["expected_exr"]

            # Skip if no expected EXR exists (scenario doesn't have golden images)
            if not expected_exr.exists():
                skipped += 1
                continue

            # Find the processed output
            actual_output = outputs_dir / f"{test_name}_processed.exr"
            if not actual_output.exists():
                print(f"  MISSING: {actual_output.name} (scen{scen_num} {variant.letter})")
                missing += 1
                continue

            if dry_run:
                print(f"  [DRY RUN] {actual_output.name} -> {expected_exr}")
            else:
                shutil.copy2(actual_output, expected_exr)
                print(f"  OK: {expected_exr}")
            updated += 1

    return updated, skipped, missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Update expected EXR golden images from test outputs.")
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=Path.cwd() / "tests" / "outputs",
        help="Directory containing processed test outputs",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    args = parser.parse_args()

    updated, skipped, missing = update_expected_exrs(outputs_dir=args.outputs_dir, dry_run=args.dry_run)

    print(f"\nUpdated: {updated}, Skipped (no expected): {skipped}, Missing output: {missing}")
    sys.exit(1 if missing > 0 else 0)


if __name__ == "__main__":
    main()
