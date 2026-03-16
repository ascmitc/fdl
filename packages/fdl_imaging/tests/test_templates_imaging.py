# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Imaging-level parameterized template scenario tests.

Extends the pure FDL template tests with image processing and comparison.
For each scenario/variant, this:
1. Validates the FDL template application (via super class)
2. Processes the source image through the FDL template pipeline
3. Compares the processed image pixel-for-pixel against the expected golden EXR

Uses "triangle" (bilinear) filter for deterministic cross-platform results.
Parameterized via pytest_generate_tests hook in conftest.py.
"""

from fdl.testing.template_tests import TestFDLTemplatesParameterized as _FDLBase

from fdl_imaging.testing import BaseFDLImagingTestCase


class TestFDLTemplatesParameterized(_FDLBase):
    """Imaging-aware template tests with image comparison."""

    def _create_test_case(self):
        return BaseFDLImagingTestCase()

    def _build_run_kwargs(self, config, variant, paths, test_name):
        kwargs = super()._build_run_kwargs(config, variant, paths, test_name)
        if variant.has_tif and paths["source_tif"].exists():
            kwargs["source_image"] = paths["source_tif"]
        if paths["expected_exr"].exists():
            kwargs["expected_image_path"] = paths["expected_exr"]
        return kwargs
