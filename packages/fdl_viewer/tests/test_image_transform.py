# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Focused tests for the viewer's image transform and image export paths.

``test_ui_scenarios`` covers these paths across every scenario, but that class
is skipped in CI/CD (``CICD=1``), so a break in the image pipeline can reach
``dev`` unnoticed. These tests use a single scenario and run everywhere.

Both call sites in ``MainWindow`` (the output-tab preview and
``export_output_image``) must pass ``scale_factor`` to
``fdl_imaging.transform_image_with_computed_values``.
"""

from pathlib import Path

import pytest
from fdl import ATTR_SCALE_FACTOR
from fdl.testing import SCENARIO_CONFIGS, get_scenario_paths
from fdl_imaging import transform_image_with_computed_values

from fdl_viewer.views import main_window as main_window_module
from utils.ui_test_helper import UITestHelper

# Scenario 1 variant B has a source image and a template with a non-trivial scale.
SCENARIO_NUMBER = 1
VARIANT_LETTER = "B"


@pytest.fixture
def transformed_window(main_window, qtbot, reset_app_state, sample_files_dir, monkeypatch):
    """
    Load scenario 1-B, with a spy on the image transform, and click Transform.

    Returns (window, helper, calls) where ``calls`` records the keyword
    arguments of every ``transform_image_with_computed_values`` call.
    """
    config = SCENARIO_CONFIGS[SCENARIO_NUMBER]
    variant = next(v for v in config.variants if v.letter == VARIANT_LETTER)
    paths = get_scenario_paths(sample_files_dir, config, variant)
    assert paths["source_tif"].exists(), f"missing source image: {paths['source_tif']}"

    calls: list[dict] = []

    def spy(*args, **kwargs):
        calls.append(kwargs)
        return transform_image_with_computed_values(*args, **kwargs)

    monkeypatch.setattr(main_window_module, "transform_image_with_computed_values", spy)

    helper = UITestHelper(main_window, qtbot)
    helper.load_source_fdl(paths["source_fdl"])
    helper.load_source_image(paths["source_tif"])
    helper.load_template_fdl(paths["template"])
    helper.select_context(0)
    helper.select_canvas(0)
    helper.select_framing_decision(0)
    assert helper.is_transform_button_enabled()
    helper.click_transform()
    assert main_window._app_state.transform_result is not None
    return main_window, helper, calls


class TestImageTransform:
    def test_preview_transform_produces_output_image(self, transformed_window):
        """The output-tab preview renders an image after Transform."""
        window, _helper, calls = transformed_window
        assert calls, "Transform should run the image transform for the preview"
        pixmap = window._output_image_pixmap
        assert pixmap is not None and not pixmap.isNull(), "Preview transform failed; no output image was produced"

    def test_preview_transform_receives_scale_factor(self, transformed_window):
        """The preview call passes the template's computed scale factor."""
        window, _helper, calls = transformed_window
        expected = window._app_state.transform_result.canvas.get_custom_attr(ATTR_SCALE_FACTOR)
        assert expected is not None
        assert calls, "Transform should run the image transform for the preview"
        assert "scale_factor" in calls[0], "Preview transform call is missing scale_factor"
        assert calls[0]["scale_factor"] == pytest.approx(expected)

    def test_export_output_image_succeeds(self, transformed_window, tmp_path: Path):
        """Exporting the output image writes a file."""
        _window, helper, _calls = transformed_window
        out = tmp_path / "export.exr"
        assert helper.export_output_image_programmatically(out), "Image export should succeed"
        assert out.exists()
        assert out.stat().st_size > 0

    def test_export_receives_scale_factor(self, transformed_window, tmp_path: Path):
        """The export call passes the template's computed scale factor."""
        window, helper, calls = transformed_window
        expected = window._app_state.transform_result.canvas.get_custom_attr(ATTR_SCALE_FACTOR)
        calls.clear()
        helper.export_output_image_programmatically(tmp_path / "export.exr")
        assert calls, "Export should run the image transform"
        assert "scale_factor" in calls[0], "Export transform call is missing scale_factor"
        assert calls[0]["scale_factor"] == pytest.approx(expected)
