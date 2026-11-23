# SPDX-License-Identifier: Apache-2.0
"""Tests for the web viewer's Python image bridge (``scripts/transform_image.py``).

The Express server runs the bridge as a subprocess and sends it JSON on stdin.
These tests build that JSON from the shared scenario files exactly as the client
would (template parameters taken from the template FDL), run the real bridge, and
require the output image to be pixel-identical to the scenario's golden EXR.

Run from the repository root:

    python -m pytest examples/web_viewer/server/tests -v
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import OpenImageIO as oiio
import pytest

from fdl import read_from_file
from fdl.testing import SCENARIO_CONFIGS, BaseFDLTestCase, build_test_params, get_scenario_paths, get_scenario_test_id

BRIDGE_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "transform_image.py"
SCENARIOS_DIR = BaseFDLTestCase.get_resources_folder() / "Scenarios_For_Implementers"

# The golden EXRs are generated with the "triangle" (bilinear) filter.
GOLDEN_FILTER = "triangle"


def _enum_value(value):
    """Return the schema string for an FDL enum (or None)."""
    return getattr(value, "value", value)


def _template_params(template) -> dict:
    """Template parameters as the web client sends them to the server."""
    max_dims = template.maximum_dimensions
    return {
        "targetWidth": template.target_dimensions.width,
        "targetHeight": template.target_dimensions.height,
        "targetAnamorphicSqueeze": template.target_anamorphic_squeeze,
        "fitSource": _enum_value(template.fit_source),
        "fitMethod": _enum_value(template.fit_method),
        "alignmentMethodHorizontal": _enum_value(template.alignment_method_horizontal),
        "alignmentMethodVertical": _enum_value(template.alignment_method_vertical),
        "preserveFromSourceCanvas": _enum_value(template.preserve_from_source_canvas),
        "maximumDimensions": {"width": max_dims.width, "height": max_dims.height} if max_dims else None,
        "padToMaximum": template.pad_to_maximum,
        "roundEven": _enum_value(template.round.even),
        "roundMode": _enum_value(template.round.mode),
    }


def _bridge_input(config, variant, paths: dict, output_path: Path) -> dict:
    """Build the bridge's stdin payload for a scenario variant."""
    source_fdl = read_from_file(paths["source_fdl"])
    template = next(t for t in read_from_file(paths["template"]).canvas_templates if t.label == config.template_label)

    context_label = variant.context_label or config.context_label
    canvas_label = variant.canvas_label or config.canvas_label
    context = next(c for c in source_fdl.contexts if c.label == context_label)
    canvas = next(c for c in context.canvases if c.label == canvas_label)
    framing = next(fd for fd in canvas.framing_decisions if fd.framing_intent_id == config.framing_intent_id)

    return {
        "sourceFdlJson": Path(paths["source_fdl"]).read_text(),
        "contextLabel": context.label,
        "canvasId": canvas.id,
        "framingId": framing.id,
        "template": _template_params(template),
        "inputImagePath": str(paths["source_tif"]),
        "outputImagePath": str(output_path),
        "filterName": GOLDEN_FILTER,
    }


def _run_bridge(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BRIDGE_SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )


def _pixels(path: Path) -> np.ndarray:
    return oiio.ImageBuf(str(path)).get_pixels()


def _scenarios_with_golden_image():
    params = []
    for scen_num, letter in build_test_params():
        config = SCENARIO_CONFIGS[scen_num]
        if config.is_error_test:
            continue
        variant = next(v for v in config.variants if v.letter == letter)
        paths = get_scenario_paths(SCENARIOS_DIR, config, variant)
        if variant.has_tif and paths["source_tif"].exists() and paths["expected_exr"].exists():
            params.append(pytest.param(scen_num, letter, id=get_scenario_test_id((scen_num, letter))))
    return params


@pytest.mark.parametrize(("scen_num", "letter"), _scenarios_with_golden_image())
def test_bridge_output_matches_golden(scen_num: int, letter: str, tmp_path: Path):
    config = SCENARIO_CONFIGS[scen_num]
    variant = next(v for v in config.variants if v.letter == letter)
    paths = get_scenario_paths(SCENARIOS_DIR, config, variant)
    output_path = tmp_path / "out.exr"

    result = _run_bridge(_bridge_input(config, variant, paths, output_path))

    assert result.returncode == 0, f"bridge failed: {result.stdout.strip()} {result.stderr.strip()}"
    response = json.loads(result.stdout)
    assert response.get("success") is True, response

    expected = _pixels(paths["expected_exr"])
    actual = _pixels(output_path)
    assert actual.shape == expected.shape, f"size mismatch: {actual.shape} vs {expected.shape}"
    max_diff = float(np.abs(actual.astype(np.float64) - expected.astype(np.float64)).max())
    assert max_diff == 0.0, f"output differs from golden EXR (max abs diff {max_diff})"
