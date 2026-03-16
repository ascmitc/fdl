# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Regression tests for frameline source image generation.

Verifies that FramelineRenderer produces identical output for each source FDL
file. If the renderer changes, run `packages/fdl/scripts/regenerate_source_tiffs.py`
from the project root to update the expected images.
"""

import tempfile
from pathlib import Path

import pytest
from fdl.testing import BaseFDLTestCase
from fdl_imaging.testing import ImageComparison

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


def collect_fdl_image_pairs() -> list[tuple[Path, Path, str]]:
    """Collect all FDL/TIFF pairs for parametrization.

    Returns list of (fdl_path, image_path, test_id) tuples.
    """
    pairs = []
    for source_dir, ext in SOURCE_DIRS:
        if not source_dir.exists():
            continue
        parent_name = source_dir.name
        for fdl_path in sorted(source_dir.glob("*.fdl")):
            image_path = fdl_path.with_suffix(ext)
            if image_path.exists():
                test_id = f"{parent_name}/{fdl_path.stem}"
                pairs.append((fdl_path, image_path, test_id))
    return pairs


_PAIRS = collect_fdl_image_pairs()

_image_comparator = ImageComparison()


@pytest.mark.parametrize(
    "fdl_path,expected_image_path",
    [(p[0], p[1]) for p in _PAIRS],
    ids=[p[2] for p in _PAIRS],
)
def test_frameline_regression(fdl_path: Path, expected_image_path: Path) -> None:
    """Test that FramelineRenderer produces identical output for a source FDL."""
    renderer = FramelineRenderer(RenderConfig())

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / f"output{expected_image_path.suffix}"
        renderer.render_from_fdl(fdl_path=fdl_path, output_path=output_path)

        # Allow a small number of failed pixels for cross-platform differences
        # in OIIO text rendering and anti-aliasing (e.g. Linux vs macOS).
        _image_comparator.compare_images(
            expected_path=expected_image_path,
            actual_path=output_path,
            allowed_failed_pixels=100,
        )
