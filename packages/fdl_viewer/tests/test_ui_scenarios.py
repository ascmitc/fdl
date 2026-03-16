# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Parameterized UI Integration tests for Scenarios 1-31.

This module uses data-driven testing to run the same test logic across
all scenario/variant combinations. Each test is parameterized with
(scenario_number, variant_letter) tuples.

Note: Scenarios 21 and 22 are error validation tests (expecting ValueError)
and are not included in UI tests - they remain as unit tests only.

Each variant runs a single consolidated test that:
1. Opens the UI once
2. Loads source FDL and image
3. Captures source scene visual
4. Loads template, configures, and transforms
5. Captures output scene visual
6. Exports FDL and processed image
7. Closes the UI
8. Runs all comparisons (FDL, image, source visual, output visual)

This approach is ~5x faster than running separate tests for each comparison.
"""

import os
from pathlib import Path

import pytest

# Import scenario configuration from central testing module
from fdl.testing import (
    SCENARIO_CONFIGS,
    FDLComparison,
    ScenarioConfig,
    SourceVariant,
    build_test_params,
    get_scenario_test_id,
)
from fdl_imaging.testing import ImageComparison

from utils.ui_test_helper import UITestHelper
from utils.visual_comparison import VisualComparison, get_outputs_folder

# Tolerance for visual scene comparisons (anti-aliasing can cause minor pixel differences)
VISUAL_ALLOWED_FAILED_PIXELS = 3500  # Allow up to 3500 pixels to differ (Qt anti-aliasing jitter)
VISUAL_FAIL_THRESHOLD = 0.01  # Per-pixel threshold (1% difference)


def get_expected_folder() -> Path:
    """
    Get the expected baselines folder for visual comparison.

    Returns
    -------
    Path
        Path to the expected folder.
    """
    return Path(__file__).parent / "expected"


# Build parameter list for all scenario/variant combinations (excluding error tests)
SCENARIO_PARAMS = [p for p in build_test_params() if not SCENARIO_CONFIGS[p[0]].is_error_test]


@pytest.mark.skipif(os.environ.get("CICD") == "1", reason="UI tests require a display; skipped in CI/CD")
class TestUIScenarios:
    """Parameterized UI workflow tests for Scenarios 1-31 (excluding 21-22 error tests)."""

    @pytest.mark.parametrize(
        "scenario_config,variant_config",
        SCENARIO_PARAMS,
        indirect=True,
        ids=[get_scenario_test_id(p) for p in SCENARIO_PARAMS],
    )
    def test_scenario_workflow(
        self,
        main_window,
        qtbot,
        reset_app_state,
        scenario_config: ScenarioConfig,
        variant_config: SourceVariant,
        scenario_paths: dict[str, Path],
        tmp_path: Path,
    ):
        """
        Test complete workflow for a scenario variant.

        This consolidated test runs the full UI workflow once and performs
        all comparisons, optimizing for speed by avoiding repeated UI cycles.

        Assertion order (most stable first):
        1. FDL export comparison
        2. Image export comparison
        3. Source scene visual comparison
        4. Output scene visual comparison
        """
        helper = UITestHelper(main_window, qtbot)
        scen_num = scenario_config.number
        variant_letter = variant_config.letter

        # Setup output directories
        outputs_dir = get_outputs_folder()
        scene_output_dir = outputs_dir / "scenes" / f"scen{scen_num}"
        scene_output_dir.mkdir(parents=True, exist_ok=True)
        diffs_dir = outputs_dir / "diffs" / f"scen{scen_num}"
        diffs_dir.mkdir(parents=True, exist_ok=True)

        # Expected paths
        expected_dir = get_expected_folder() / f"scen{scen_num}"

        # =================================================================
        # PHASE 1: Load source and capture source scene
        # =================================================================
        helper.load_source_fdl(scenario_paths["source_fdl"])
        assert main_window._app_state.source_fdl is not None

        has_source_image = variant_config.has_tif and scenario_paths["source_tif"].exists()
        if has_source_image:
            helper.load_source_image(scenario_paths["source_tif"])

        # Capture source scene
        source_scene_pixmap = helper.capture_tab_scene(0)
        source_scene_path = scene_output_dir / f"source_scene_{variant_letter}.png"
        helper.save_pixmap_as_image(source_scene_pixmap, source_scene_path)

        # =================================================================
        # PHASE 2: Load template, transform, capture output scene
        # =================================================================
        helper.load_template_fdl(scenario_paths["template"])
        assert main_window._app_state.template_fdl is not None

        helper.select_context(0)
        helper.select_canvas(0)
        helper.select_framing_decision(0)

        assert helper.is_transform_button_enabled(), "Transform button should be enabled"
        helper.click_transform()
        assert main_window._app_state.output_fdl is not None

        # Enable HUD for visual QC
        main_window._app_state.set_hud_visible(True)
        qtbot.wait(7)  # Allow refresh

        # Capture output scene
        output_scene_pixmap = helper.capture_tab_scene(1)
        output_scene_path = scene_output_dir / f"output_scene_{variant_letter}.png"
        helper.save_pixmap_as_image(output_scene_pixmap, output_scene_path)

        # Disable HUD after capture (reset for next test)
        main_window._app_state.set_hud_visible(False)

        # =================================================================
        # PHASE 3: Export FDL and image
        # =================================================================
        export_fdl_path = tmp_path / f"scen{scen_num}_{variant_letter}_export.fdl"
        fdl_export_success = helper.export_fdl_programmatically(export_fdl_path)
        assert fdl_export_success, "FDL export should succeed"
        assert export_fdl_path.exists(), "Exported FDL should exist"

        export_image_path: Path | None = None
        if has_source_image and scenario_paths["expected_exr"].exists():
            export_image_path = tmp_path / f"scen{scen_num}_{variant_letter}_export.exr"
            image_export_success = helper.export_output_image_programmatically(export_image_path)
            assert image_export_success, "Image export should succeed"
            assert export_image_path.exists(), "Exported image should exist"

        # =================================================================
        # PHASE 4: Run comparisons (FDL first, then image, then visuals)
        # =================================================================

        # 1. FDL comparison (most likely to pass)
        self._compare_fdl_results(
            export_fdl_path,
            scenario_paths["expected_fdl"],
            scenario_config.template_label,
            scenario_config.canvas_label,
        )

        # 2. Image export comparison
        if export_image_path is not None:
            image_comparator = ImageComparison(outputs_dir=diffs_dir)
            image_comparator.compare_images(
                expected_path=scenario_paths["expected_exr"],
                actual_path=export_image_path,
            )

        # 3. Source scene visual comparison (with tolerance for anti-aliasing)
        source_expected_path = expected_dir / f"source_scene_{variant_letter}.png"
        if source_expected_path.exists():
            source_comparator = VisualComparison(outputs_dir=scene_output_dir)
            source_comparator.compare_images(
                expected_path=source_expected_path,
                actual_path=source_scene_path,
                fail_thresh=VISUAL_FAIL_THRESHOLD,
                allowed_failed_pixels=VISUAL_ALLOWED_FAILED_PIXELS,
            )

        # 4. Output scene visual comparison (with tolerance for anti-aliasing)
        output_expected_path = expected_dir / f"output_scene_{variant_letter}.png"
        if output_expected_path.exists():
            output_comparator = VisualComparison(outputs_dir=scene_output_dir)
            output_comparator.compare_images(
                expected_path=output_expected_path,
                actual_path=output_scene_path,
                fail_thresh=VISUAL_FAIL_THRESHOLD,
                allowed_failed_pixels=VISUAL_ALLOWED_FAILED_PIXELS,
            )

    def _compare_fdl_results(
        self,
        actual_path: Path,
        expected_path: Path,
        context_label: str,
        canvas_label: str,
    ):
        """
        Compare FDL output using FDLComparison.

        Parameters
        ----------
        actual_path : Path
            Path to actual FDL file.
        expected_path : Path
            Path to expected FDL file.
        context_label : str
            Context label for comparison.
        canvas_label : str
            Canvas label for comparison.
        """
        from fdl import read_from_file

        actual_fdl = read_from_file(actual_path)
        expected_fdl = read_from_file(expected_path)

        comparator = FDLComparison()
        comparator.compare_fdl_output(
            expected_fdl=expected_fdl,
            actual_fdl=actual_fdl,
            context_label=context_label,
            canvas_label=canvas_label,
        )
