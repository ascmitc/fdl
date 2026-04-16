# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Regression test for floating-point precision bug in template application.

Source: 6560x2747 framing, 6560x3100 canvas
Template: 3840x1608 target, fit_method=width, fit_source=framing_decision.dimensions
Round: even=even, mode=down

The scale factor 3840/6560 = 24/41 has no exact IEEE 754 binary representation.
Computing value * (target/fit) produces 3839.999... which with round(even=even,
mode=down) yields 3838 instead of the correct 3840.
"""

import uuid
from pathlib import Path

import pytest

from fdl import read_from_file

RESOURCES = Path(__file__).parents[4] / "resources" / "FDL"
FDL_PATH = RESOURCES / "Simple_FDL2.0.1_Failure_Example.fdl"


@pytest.fixture()
def template_result():
    """Load the failing FDL and apply the template, returning the result."""
    fdl = read_from_file(FDL_PATH)

    template = None
    for t in fdl.canvas_templates:
        if t.label == "Custom Template":
            template = t
            break
    assert template is not None, "Template 'Custom Template' not found"

    context = None
    for c in fdl.contexts:
        if c.label == "Custom Template":
            context = c
            break
    assert context is not None, "Context 'Custom Template' not found"

    canvas = None
    for cv in context.canvases:
        if cv.id == "1":
            canvas = cv
            break
    assert canvas is not None, "Canvas '1' not found"

    fd = None
    for f in canvas.framing_decisions:
        if f.framing_intent_id == "A":
            fd = f
            break
    assert fd is not None, "Framing decision with intent_id 'A' not found"

    deterministic_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    new_canvas_id = deterministic_uuid.hex[:30]

    result = template.apply(
        source_canvas=canvas,
        source_framing=fd,
        new_canvas_id=new_canvas_id,
        new_fd_name="",
        source_context_label=context.label,
        context_creator="Test",
    )
    return result


def test_output_canvas_dimensions(template_result):
    """Output canvas width must be 3840 (not 3838) and height 1608."""
    canvas = template_result.canvas
    assert canvas.dimensions.width == 3840, f"Expected canvas width 3840, got {canvas.dimensions.width}"
    assert canvas.dimensions.height == 1608, f"Expected canvas height 1608, got {canvas.dimensions.height}"


def test_output_framing_decision_dimensions(template_result):
    """Output framing decision width must be 3840 (not 3838) and height 1608."""
    fd = template_result.framing_decision
    assert fd.dimensions.width == 3840, f"Expected framing width 3840, got {fd.dimensions.width}"
    assert fd.dimensions.height == 1608, f"Expected framing height 1608, got {fd.dimensions.height}"
