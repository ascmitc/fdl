#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Regenerate all source TIFF images from their paired FDL files.

Uses the fdl_frameline_generator to render frameline visualizations for each
source FDL file. Run this script whenever the FDL files or the frameline
renderer change.

Usage:
    python packages/fdl/scripts/regenerate_source_tiffs.py              # regenerate all
    python packages/fdl/scripts/regenerate_source_tiffs.py --dry-run    # show what would be done
"""

import sys
import time
from pathlib import Path

from fdl.testing import BaseFDLTestCase
from fdl_frameline_generator.config import RenderConfig
from fdl_frameline_generator.renderer import FramelineRenderer

FDL_RESOURCES = BaseFDLTestCase.get_resources_folder()

# Source directories and their image extensions
SOURCE_DIRS: list[tuple[Path, str]] = [
    (FDL_RESOURCES / "Original_Source_Files", ".tif"),
    (FDL_RESOURCES / "New_Source_Files", ".tiff"),
    (FDL_RESOURCES / "EdgeCases" / "alignment_combos" / "source", ".tiff"),
    (FDL_RESOURCES / "EdgeCases" / "generated" / "source", ".tiff"),
]


def find_fdl_image_pairs(source_dir: Path, ext: str) -> list[tuple[Path, Path]]:
    """Find all FDL files that have a paired image file."""
    pairs = []
    for fdl_path in sorted(source_dir.glob("*.fdl")):
        image_path = fdl_path.with_suffix(ext)
        if image_path.exists():
            pairs.append((fdl_path, image_path))
        else:
            print(f"  WARNING: No image found for {fdl_path.name} (expected {image_path.name})")
    return pairs


def regenerate_all(dry_run: bool = False) -> tuple[int, int]:
    """Regenerate all source TIFF images.

    Returns (success_count, error_count).
    """
    renderer = FramelineRenderer(RenderConfig())
    success = 0
    errors = 0

    for source_dir, ext in SOURCE_DIRS:
        if not source_dir.exists():
            print(f"WARNING: Directory not found: {source_dir}")
            continue

        pairs = find_fdl_image_pairs(source_dir, ext)
        print(f"\n{source_dir.relative_to(FDL_RESOURCES)}: {len(pairs)} pairs found")

        for fdl_path, image_path in pairs:
            if dry_run:
                print(f"  [DRY RUN] {image_path.name}")
                success += 1
                continue

            try:
                renderer.render_from_fdl(fdl_path=fdl_path, output_path=image_path)
                print(f"  OK: {image_path.name}")
                success += 1
            except Exception as e:
                print(f"  ERROR: {image_path.name} - {e}")
                errors += 1

    return success, errors


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    start = time.time()
    success, errors = regenerate_all(dry_run=dry_run)
    elapsed = time.time() - start

    print(f"\nDone in {elapsed:.1f}s: {success} succeeded, {errors} failed")
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
