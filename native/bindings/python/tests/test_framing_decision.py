# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
import pytest
from fdl.canvas import Canvas
from fdl.fdl_types import DimensionsFloat, DimensionsInt, PointFloat
from fdl.framing_decision import FramingDecision
from fdl.rounding import RoundStrategy

from fdl import set_rounding


@pytest.mark.parametrize(
    ("intent_ratio", "canvas_dim", "canvas_eff", "canvas_sqz", "protection", "expected_dim", "expected_prot"),
    [
        # one to one
        ({"width": 16, "height": 9}, {"width": 1920, "height": 1080}, None, 1, 0, {"width": 1920, "height": 1080}, None),
        # one to one squeeze 2
        ({"width": 16, "height": 9}, {"width": 960, "height": 1080}, None, 2, 0, {"width": 960, "height": 1080}, None),
        # 10% protection
        (
            {"width": 16, "height": 9},
            {"width": 1920, "height": 1080},
            {"width": 1920, "height": 1080},
            1,
            0.1,
            {"width": 1920 - 192, "height": 1080 - 108},
            {"width": 1920, "height": 1080},
        ),
        # effective canvas and 10% protection
        (
            {"width": 16, "height": 9},
            {"width": 1920, "height": 1080},
            {"width": 1920 - 192, "height": 1080 - 108},
            1,
            0.1,
            {"width": 1556, "height": 874},
            {"width": 1920 - 192, "height": 1080 - 108},
        ),
        # Wide intent
        (
            {"width": 235, "height": 100},
            {"width": 1920, "height": 1080},
            {"width": 1920, "height": 1080},
            1,
            0,
            {"width": 1920, "height": 818},
            None,
        ),
        # Tall intent
        (
            {"width": 4, "height": 3},
            {"width": 1920, "height": 1080},
            {"width": 1920, "height": 1080},
            1,
            0,
            {"width": 1440, "height": 1080},
            None,
        ),
    ],
)
def test_from_framing_intent(
    sample_framing_intent_obj,
    sample_canvas_obj,
    intent_ratio,
    canvas_dim,
    canvas_eff,
    canvas_sqz,
    protection,
    expected_dim,
    expected_prot,
):
    intent = sample_framing_intent_obj
    intent.aspect_ratio = DimensionsInt(**intent_ratio)
    intent.protection = protection
    canvas = sample_canvas_obj
    canvas.dimensions = DimensionsInt(**canvas_dim)
    canvas.anamorphic_squeeze = canvas_sqz
    if canvas_eff is not None:
        canvas.effective_dimensions = DimensionsInt(**canvas_eff)
    else:
        canvas.effective_dimensions = None

    # Override rounding to match values in samples
    set_rounding(RoundStrategy(even="even", mode="round"))
    result = FramingDecision.from_framing_intent(canvas=canvas, framing_intent=intent)
    assert result.dimensions == DimensionsFloat(**expected_dim)

    if expected_prot is not None:
        assert result.protection_dimensions == DimensionsFloat(**expected_prot)
    else:
        assert result.protection_dimensions is None


@pytest.mark.parametrize(
    ("h_method", "v_method", "protection_dim", "protection_pnt", "expected"),
    [
        ("left", "top", None, None, {"x": 0, "y": 0}),
        ("left", "top", {"width": 550, "height": 550}, {"x": 0, "y": 0}, {"x": 0, "y": 0}),
        ("left", "center", None, None, {"x": 0, "y": 250}),
        ("left", "center", {"width": 550, "height": 550}, {"x": 0, "y": 255}, {"x": 0, "y": 250}),
        ("left", "bottom", None, None, {"x": 0, "y": 500}),
        ("left", "bottom", {"width": 550, "height": 550}, {"x": 0, "y": 450}, {"x": 0, "y": 500}),
        ("center", "top", None, None, {"x": 250, "y": 0}),
        ("center", "top", {"width": 550, "height": 550}, {"x": 225, "y": 0}, {"x": 250, "y": 0}),
        ("center", "center", None, None, {"x": 250, "y": 250}),
        ("center", "center", {"width": 550, "height": 550}, {"x": 225, "y": 225}, {"x": 250, "y": 250}),
        ("center", "bottom", None, None, {"x": 250, "y": 500}),
        ("center", "bottom", {"width": 550, "height": 550}, {"x": 225, "y": 450}, {"x": 250, "y": 500}),
        ("right", "top", None, None, {"x": 500, "y": 0}),
        ("right", "top", {"width": 550, "height": 550}, {"x": 450, "y": 0}, {"x": 500, "y": 0}),
        ("right", "center", None, None, {"x": 500, "y": 250}),
        ("right", "center", {"width": 550, "height": 550}, {"x": 450, "y": 225}, {"x": 500, "y": 250}),
        ("right", "bottom", None, None, {"x": 500, "y": 500}),
        ("right", "bottom", {"width": 550, "height": 550}, {"x": 450, "y": 450}, {"x": 500, "y": 500}),
    ],
)
def test_adjust_anchor_point(h_method, v_method, protection_dim, protection_pnt, expected):
    canvas = Canvas(id="test_canvas", source_canvas_id="test_canvas", dimensions=DimensionsInt(width=1000, height=1000))
    framing_decision = FramingDecision(
        id="test_decision", framing_intent_id="test_intent", dimensions=DimensionsFloat(width=500, height=500)
    )
    if protection_dim is not None:
        framing_decision.protection_dimensions = DimensionsFloat(**protection_dim)
        framing_decision.protection_anchor_point = PointFloat(**protection_pnt)

    framing_decision.adjust_anchor_point(canvas=canvas, h_method=h_method, v_method=v_method)
    assert framing_decision.anchor_point == PointFloat(**expected)


@pytest.mark.parametrize(
    ("h_method", "v_method", "expected"),
    [
        ("left", "top", {"x": 0, "y": 0}),
        ("left", "center", {"x": 0, "y": 225}),
        ("left", "bottom", {"x": 0, "y": 450}),
        ("center", "top", {"x": 225, "y": 0}),
        ("center", "center", {"x": 225, "y": 225}),
        ("center", "bottom", {"x": 225, "y": 450}),
        ("right", "top", {"x": 450, "y": 0}),
        ("right", "center", {"x": 450, "y": 225}),
        ("right", "bottom", {"x": 450, "y": 450}),
    ],
)
def test_adjust_protection_anchor_point(h_method, v_method, expected):
    canvas = Canvas(id="test_canvas", source_canvas_id="test_canvas", dimensions=DimensionsInt(width=1000, height=1000))
    framing_decision = FramingDecision(
        id="test_decision", framing_intent_id="test_intent", protection_dimensions=DimensionsFloat(width=550, height=550)
    )

    framing_decision.adjust_protection_anchor_point(canvas=canvas, h_method=h_method, v_method=v_method)
    assert framing_decision.protection_anchor_point == PointFloat(**expected)
