# SPDX-License-Identifier: Apache-2.0
"""Scenario inputs for the web viewer tests, shared by the Python and Node suites.

``bridge_inputs()`` builds, for every scenario variant with a source image and golden
EXR, the parameters the web client would send to the server (template parameters read
from the template FDL, canvas and framing selected the way the core scenario tests do).

The Node tests cannot import the Python scenario config, so the same data is committed as
``scenario_inputs.json``. ``test_scenario_inputs.py`` fails if the JSON is out of date;
regenerate it with:

    python examples/web_viewer/server/tests/scenario_inputs.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fdl import read_from_file
from fdl.testing import SCENARIO_CONFIGS, BaseFDLTestCase, build_test_params, get_scenario_paths, get_scenario_test_id

SCENARIOS_DIR = BaseFDLTestCase.get_resources_folder() / "Scenarios_For_Implementers"
REPO_ROOT = Path(__file__).resolve().parents[4]
JSON_PATH = Path(__file__).resolve().parent / "scenario_inputs.json"


def _enum_value(value):
    """Return the schema string for an FDL enum (or None)."""
    return getattr(value, "value", value)


def template_params(template) -> dict:
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


def bridge_inputs() -> list[dict]:
    """One entry per scenario variant that has a source image and a golden EXR."""
    entries = []
    for scen_num, letter in build_test_params():
        config = SCENARIO_CONFIGS[scen_num]
        if config.is_error_test:
            continue
        variant = next(v for v in config.variants if v.letter == letter)
        paths = get_scenario_paths(SCENARIOS_DIR, config, variant)
        if not (variant.has_tif and paths["source_tif"].exists() and paths["expected_exr"].exists()):
            continue

        source_fdl = read_from_file(paths["source_fdl"])
        template = next(t for t in read_from_file(paths["template"]).canvas_templates if t.label == config.template_label)
        context_label = variant.context_label or config.context_label
        canvas_label = variant.canvas_label or config.canvas_label
        context = next(c for c in source_fdl.contexts if c.label == context_label)
        canvas = next(c for c in context.canvases if c.label == canvas_label)
        framing = next(fd for fd in canvas.framing_decisions if fd.framing_intent_id == config.framing_intent_id)

        def rel(p):
            return Path(p).resolve().relative_to(REPO_ROOT).as_posix()

        entries.append(
            {
                "id": get_scenario_test_id((scen_num, letter)),
                "sourceFdl": rel(paths["source_fdl"]),
                "sourceImage": rel(paths["source_tif"]),
                "expectedFdl": rel(paths["expected_fdl"]),
                "expectedImage": rel(paths["expected_exr"]),
                "contextLabel": context.label,
                "canvasId": canvas.id,
                "framingId": framing.id,
                "template": template_params(template),
            }
        )
    return entries


if __name__ == "__main__":
    JSON_PATH.write_text(json.dumps(bridge_inputs(), indent=2) + "\n")
    print(f"wrote {JSON_PATH}")
