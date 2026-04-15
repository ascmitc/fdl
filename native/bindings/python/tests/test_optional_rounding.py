# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Tests for optional rounding in FDL canvas templates.

Verifies that templates can omit the ``round`` field to preserve fractional
pixel values for inner geometry (framing dimensions, protection dimensions,
and their anchors), while canvas dimensions remain integer.

See: https://github.com/ascmitc/fdl/issues/36
"""

from __future__ import annotations

import json

import pytest
from fdl import (
    FDL,
    Canvas,
    CanvasTemplate,
    Context,
    DimensionsFloat,
    DimensionsInt,
    FramingDecision,
    FramingIntent,
    PointFloat,
    RoundStrategy,
    read_from_string,
)
from fdl.constants import (
    FitMethod,
    GeometryPath,
    HAlign,
    RoundingEven,
    RoundingMode,
    VAlign,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_source_fdl() -> FDL:
    """Build a minimal source FDL modelling an ARRI Alexa LF open gate (4448x3096)
    with a spherical 2.39:1 framing decision at 4096x1716."""
    doc = FDL.create(
        uuid="00000000-0000-0000-0000-000000000099",
        fdl_creator="optional-rounding-test",
        default_framing_intent="1",
    )
    doc.add_framing_intent(
        id="1",
        label="2.39:1 Theatrical",
        aspect_ratio=DimensionsInt(width=239, height=100),
        protection=0.0,
    )
    ctx = doc.add_context(label="Source Camera", context_creator="Test")
    canvas = ctx.add_canvas(
        id="C1",
        label="4.5K LF Open Gate",
        source_canvas_id="C1",
        dimensions=DimensionsInt(width=4448, height=3096),
        anamorphic_squeeze=1.0,
    )
    canvas.add_framing_decision(
        id="1",
        label="2.39:1 Theatrical",
        framing_intent_id="1",
        dimensions=DimensionsFloat(width=4096.0, height=1714.6443514644),
        anchor_point=PointFloat(x=176.0, y=690.6778242678),
    )
    return doc


def _apply_template(doc: FDL, template: CanvasTemplate) -> FramingDecision:
    """Apply a CanvasTemplate to the first canvas/FD in doc, return the result FD."""
    ctx = doc.contexts[0]
    canvas = ctx.canvases[0]
    fd = canvas.framing_decisions[0]
    result = template.apply(canvas, fd, "OUT", "1", ctx.label, "Test")
    return result.framing_decision


# ---------------------------------------------------------------------------
# RoundStrategy NONE
# ---------------------------------------------------------------------------

class TestRoundStrategyNone:

    def test_none_sentinel_is_falsy(self):
        assert not RoundStrategy.NONE
        assert RoundStrategy.NONE.is_none

    def test_active_strategy_is_truthy(self):
        s = RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.UP)
        assert s
        assert not s.is_none

    def test_none_mode_enum(self):
        assert RoundingMode.NONE == "none"

    def test_none_repr(self):
        assert "NONE" in repr(RoundStrategy.NONE)


# ---------------------------------------------------------------------------
# CanvasTemplate default is NONE
# ---------------------------------------------------------------------------

class TestCanvasTemplateDefaultRound:

    def test_default_round_is_none(self):
        ct = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
        )
        assert ct.round.is_none

    def test_explicit_round_is_preserved(self):
        ct = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        assert not ct.round.is_none
        assert ct.round.even == RoundingEven.EVEN
        assert ct.round.mode == RoundingMode.ROUND

    def test_no_round_omitted_from_as_dict(self):
        ct = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
        )
        d = ct.as_dict()
        assert "round" not in d

    def test_explicit_round_in_as_dict(self):
        ct = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.UP),
        )
        d = ct.as_dict()
        assert "round" in d
        assert d["round"]["even"] == "even"
        assert d["round"]["mode"] == "up"


# ---------------------------------------------------------------------------
# Template application: NO rounding preserves float inner dimensions
# ---------------------------------------------------------------------------

class TestApplyTemplateNoRounding:
    """John Quartel's scenario from issue #36: Alexa LF → HD dailies, no rounding."""

    def test_framing_dimensions_are_float(self):
        """With no rounding, framing dimensions should have fractional values."""
        doc = _build_source_fdl()
        template = CanvasTemplate(
            id="E",
            label="Editorial",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=1920, height=1080),
            pad_to_maximum=True,
        )
        fd = _apply_template(doc, template)

        assert fd.dimensions.width == pytest.approx(1920.0, abs=0.01)
        assert fd.dimensions.height != int(fd.dimensions.height), (
            "Framing height should be fractional (not rounded)"
        )

    def test_framing_anchor_is_float(self):
        """With no rounding, anchor y should be fractional."""
        doc = _build_source_fdl()
        template = CanvasTemplate(
            id="E",
            label="Editorial",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=1920, height=1080),
            pad_to_maximum=True,
        )
        fd = _apply_template(doc, template)

        assert fd.anchor_point.y != int(fd.anchor_point.y), (
            "Framing anchor Y should be fractional (not rounded)"
        )


# ---------------------------------------------------------------------------
# Template application: WITH rounding rounds all geometry fields
# ---------------------------------------------------------------------------

class TestApplyTemplateWithRounding:
    """Same scenario but with explicit even/round — all values should be integer."""

    def test_framing_dimensions_are_integer(self):
        doc = _build_source_fdl()
        template = CanvasTemplate(
            id="E",
            label="Editorial",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=1920, height=1080),
            pad_to_maximum=True,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        fd = _apply_template(doc, template)

        assert fd.dimensions.width == int(fd.dimensions.width)
        assert fd.dimensions.height == int(fd.dimensions.height)

    def test_framing_anchor_is_integer(self):
        doc = _build_source_fdl()
        template = CanvasTemplate(
            id="E",
            label="Editorial",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=1920, height=1080),
            pad_to_maximum=True,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        fd = _apply_template(doc, template)

        assert fd.anchor_point.x == int(fd.anchor_point.x)
        assert fd.anchor_point.y == int(fd.anchor_point.y)


# ---------------------------------------------------------------------------
# Different rounding modes produce distinct results
# ---------------------------------------------------------------------------

class TestRoundingModeVariations:
    """Verify that different rounding strategies produce different results."""

    @pytest.fixture
    def source_fdl(self):
        return _build_source_fdl()

    def _apply_with_rounding(self, doc, even, mode):
        template = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=1920, height=1080),
            pad_to_maximum=True,
            round=RoundStrategy(even=even, mode=mode),
        )
        return _apply_template(doc, template)

    def test_even_up_vs_even_down(self, source_fdl):
        fd_up = self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.UP)
        fd_down = self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.DOWN)
        assert fd_up.dimensions.height >= fd_down.dimensions.height

    def test_whole_up_vs_whole_down(self, source_fdl):
        fd_up = self._apply_with_rounding(source_fdl, RoundingEven.WHOLE, RoundingMode.UP)
        fd_down = self._apply_with_rounding(source_fdl, RoundingEven.WHOLE, RoundingMode.DOWN)
        assert fd_up.dimensions.height >= fd_down.dimensions.height

    def test_none_vs_even_round_differ(self, source_fdl):
        """No-rounding result should differ from even/round for fractional values."""
        template_none = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=1920, height=1080),
            pad_to_maximum=True,
        )
        fd_none = _apply_template(source_fdl, template_none)
        fd_round = self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.ROUND)
        assert fd_none.dimensions.height != fd_round.dimensions.height

    @pytest.mark.parametrize(
        ("even", "mode"),
        [
            (RoundingEven.EVEN, RoundingMode.UP),
            (RoundingEven.EVEN, RoundingMode.DOWN),
            (RoundingEven.EVEN, RoundingMode.ROUND),
            (RoundingEven.WHOLE, RoundingMode.UP),
            (RoundingEven.WHOLE, RoundingMode.DOWN),
            (RoundingEven.WHOLE, RoundingMode.ROUND),
        ],
    )
    def test_all_rounding_modes_produce_integer_dimensions(self, source_fdl, even, mode):
        """All rounding modes should round dimensions to integers."""
        fd = self._apply_with_rounding(source_fdl, even, mode)
        assert fd.dimensions.width == int(fd.dimensions.width)
        assert fd.dimensions.height == int(fd.dimensions.height)

    @pytest.mark.parametrize(
        ("even", "mode"),
        [
            (RoundingEven.EVEN, RoundingMode.UP),
            (RoundingEven.EVEN, RoundingMode.DOWN),
            (RoundingEven.EVEN, RoundingMode.ROUND),
        ],
    )
    def test_even_rounding_produces_integer_anchors(self, source_fdl, even, mode):
        """Even rounding produces even dimensions, so (canvas - dim)/2 is integer."""
        fd = self._apply_with_rounding(source_fdl, even, mode)
        assert fd.anchor_point.x == int(fd.anchor_point.x)
        assert fd.anchor_point.y == int(fd.anchor_point.y)


# ---------------------------------------------------------------------------
# JSON round-trip: template without round field
# ---------------------------------------------------------------------------

class TestJsonRoundTrip:

    def test_parse_template_without_round(self):
        """An FDL JSON with a canvas_template that omits 'round' should parse OK."""
        fdl_json = {
            "uuid": "00000000-0000-0000-0000-000000000001",
            "version": {"major": 2, "minor": 0},
            "fdl_creator": "test",
            "default_framing_intent": "1",
            "framing_intents": [
                {"id": "1", "label": "Test", "aspect_ratio": {"width": 16, "height": 9}, "protection": 0.0}
            ],
            "canvas_templates": [
                {
                    "id": "T",
                    "label": "No-Round Template",
                    "target_dimensions": {"width": 1920, "height": 1080},
                    "target_anamorphic_squeeze": 1.0,
                    "fit_source": "framing_decision.dimensions",
                    "fit_method": "width",
                }
            ],
        }
        doc = read_from_string(json.dumps(fdl_json))
        templates = doc.canvas_templates
        assert len(templates) == 1
        assert templates[0].round.is_none

    def test_parse_template_with_round(self):
        """An FDL JSON with an explicit 'round' field should parse it."""
        fdl_json = {
            "uuid": "00000000-0000-0000-0000-000000000002",
            "version": {"major": 2, "minor": 0},
            "fdl_creator": "test",
            "default_framing_intent": "1",
            "framing_intents": [
                {"id": "1", "label": "Test", "aspect_ratio": {"width": 16, "height": 9}, "protection": 0.0}
            ],
            "canvas_templates": [
                {
                    "id": "T",
                    "label": "Rounded Template",
                    "target_dimensions": {"width": 1920, "height": 1080},
                    "target_anamorphic_squeeze": 1.0,
                    "fit_source": "framing_decision.dimensions",
                    "fit_method": "width",
                    "round": {"even": "even", "mode": "round"},
                }
            ],
        }
        doc = read_from_string(json.dumps(fdl_json))
        templates = doc.canvas_templates
        assert len(templates) == 1
        assert not templates[0].round.is_none
        assert templates[0].round.even == RoundingEven.EVEN
        assert templates[0].round.mode == RoundingMode.ROUND
