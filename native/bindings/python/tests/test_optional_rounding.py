# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Tests for optional rounding in FDL canvas templates.

Per FDL spec 7.4.12, ``round`` applies only to ``canvas.dimensions``; inner
geometry (framing dimensions, protection dimensions, anchors) is never rounded
and remains float. ``canvas.effective_dimensions`` is ceiled to integer where
present. When ``round`` is omitted from JSON, the C accessor returns the spec
default ``even`` / ``up``. When ``pad_to_maximum=true`` with ``maximum_dimensions``,
``round`` has no effect on sizing (canvas is already integer from max dims).

See: https://github.com/ascmitc/fdl/issues/36
"""

from __future__ import annotations

import json

import pytest
from fdl import (
    FDL,
    Canvas,
    CanvasTemplate,
    DimensionsFloat,
    DimensionsInt,
    FramingDecision,
    PointFloat,
    RoundStrategy,
    TemplateResult,
    read_from_string,
)
from fdl.constants import (
    FitMethod,
    GeometryPath,
    RoundingEven,
    RoundingMode,
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


def _apply_template(doc: FDL, template: CanvasTemplate) -> TemplateResult:
    """Apply a CanvasTemplate to the first canvas/FD in doc; return full result."""
    ctx = doc.contexts[0]
    canvas = ctx.canvases[0]
    fd = canvas.framing_decisions[0]
    return template.apply(canvas, fd, "OUT", "1", ctx.label, "Test")


def _assert_canvas_dimensions_integer(canvas: Canvas) -> None:
    assert canvas.dimensions.width == int(canvas.dimensions.width)
    assert canvas.dimensions.height == int(canvas.dimensions.height)


def _assert_framing_float(fd: FramingDecision) -> None:
    assert fd.dimensions.height != int(fd.dimensions.height), (
        "Framing height should be fractional (inner geometry is not rounded)"
    )


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
# CanvasTemplate: accessor spec default when round omitted
# ---------------------------------------------------------------------------

class TestCanvasTemplateDefaultRound:

    def test_accessor_spec_default_when_round_omitted(self):
        """C accessor returns even/up (spec 7.4.12 default) when round is omitted."""
        ct = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
        )
        assert not ct.round.is_none
        assert ct.round.even == RoundingEven.EVEN
        assert ct.round.mode == RoundingMode.UP

    def test_explicit_round_is_preserved(self):
        ct = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        assert not ct.round.is_none
        assert ct.round.even == RoundingEven.EVEN
        assert ct.round.mode == RoundingMode.ROUND

    def test_round_omitted_from_as_dict_when_canonical_default(self):
        """Serialization may omit ``round`` when it matches the spec default; accessor still reports even/up."""
        ct = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
        )
        assert ct.round.even == RoundingEven.EVEN
        assert ct.round.mode == RoundingMode.UP
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
# Template application: inner geometry stays float
# ---------------------------------------------------------------------------

class TestApplyTemplateNoRounding:
    """John Quartel's scenario from issue #36: Alexa LF → HD dailies, pad to max."""

    def test_framing_dimensions_are_float(self):
        """Framing dimensions stay fractional (round does not affect inner geometry)."""
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
        result = _apply_template(doc, template)
        fd = result.framing_decision

        assert fd.dimensions.width == pytest.approx(1920.0, abs=0.01)
        _assert_framing_float(fd)

    def test_framing_anchor_is_float(self):
        """Anchors stay fractional when inner geometry is not rounded."""
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
        result = _apply_template(doc, template)
        fd = result.framing_decision

        assert fd.anchor_point.y != int(fd.anchor_point.y), (
            "Framing anchor Y should be fractional (not rounded)"
        )


# ---------------------------------------------------------------------------
# pad_to_max + max_dims: explicit round does not change sizing (inner still float)
# ---------------------------------------------------------------------------

class TestApplyTemplateWithRounding:
    """With pad_to_maximum + maximum_dimensions, round is ignored for canvas sizing."""

    def test_framing_dimensions_are_float_even_with_explicit_round(self):
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
        result = _apply_template(doc, template)
        fd = result.framing_decision

        assert fd.dimensions.width == pytest.approx(1920.0, abs=0.01)
        _assert_framing_float(fd)

    def test_framing_anchor_is_float_even_with_explicit_round(self):
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
        result = _apply_template(doc, template)
        fd = result.framing_decision

        assert fd.anchor_point.y != int(fd.anchor_point.y), (
            "Framing anchor Y should stay fractional (inner geometry is not rounded)"
        )


# ---------------------------------------------------------------------------
# Canvas dimensions integer; framing dimensions float
# ---------------------------------------------------------------------------

class TestContextDependentRoundingDefault:
    """Round applies to canvas.dimensions only; framing stays float."""

    def test_no_pad_no_round_canvas_integer_framing_float(self):
        doc = _build_source_fdl()
        template = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
        )
        result = _apply_template(doc, template)
        _assert_canvas_dimensions_integer(result.canvas)
        _assert_framing_float(result.framing_decision)

    def test_pad_to_max_no_round_preserves_floats(self):
        """With pad_to_max, omitting round should preserve fractional framing dims."""
        doc = _build_source_fdl()
        template = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=1920, height=1080),
            pad_to_maximum=True,
        )
        result = _apply_template(doc, template)
        fd = result.framing_decision
        assert fd.dimensions.height != int(fd.dimensions.height), (
            "pad_to_max with no effective round should preserve fractional inner dims"
        )

    def test_max_dims_without_pad_canvas_integer_framing_float(self):
        doc = _build_source_fdl()
        template = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=1920, height=1080),
            pad_to_maximum=False,
        )
        result = _apply_template(doc, template)
        _assert_canvas_dimensions_integer(result.canvas)
        _assert_framing_float(result.framing_decision)


# ---------------------------------------------------------------------------
# Different rounding modes affect canvas.dimensions (not inner geometry)
# ---------------------------------------------------------------------------

class TestRoundingModeVariations:
    """Use pad_to_maximum=False so round applies to canvas dimensions."""

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
            pad_to_maximum=False,
            round=RoundStrategy(even=even, mode=mode),
        )
        return _apply_template(doc, template)

    def test_even_up_vs_even_down_canvas_dims(self, source_fdl):
        r_up = self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.UP)
        r_down = self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.DOWN)
        assert r_up.canvas.dimensions.height >= r_down.canvas.dimensions.height

    def test_whole_up_vs_whole_down_canvas_dims(self, source_fdl):
        r_up = self._apply_with_rounding(source_fdl, RoundingEven.WHOLE, RoundingMode.UP)
        r_down = self._apply_with_rounding(source_fdl, RoundingEven.WHOLE, RoundingMode.DOWN)
        assert r_up.canvas.dimensions.height >= r_down.canvas.dimensions.height

    def test_default_even_up_matches_accessor_explicit_even_up_canvas(self, source_fdl):
        """Template without ``round`` uses spec default even/up; matches explicit even/up."""
        template_default = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            pad_to_maximum=False,
        )
        template_explicit_up = CanvasTemplate(
            id="T",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            preserve_from_source_canvas=GeometryPath.CANVAS_DIMENSIONS,
            pad_to_maximum=False,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.UP),
        )
        r_default = _apply_template(source_fdl, template_default)
        r_explicit = _apply_template(source_fdl, template_explicit_up)
        assert r_default.canvas.dimensions == r_explicit.canvas.dimensions
        assert r_default.framing_decision.dimensions.height == pytest.approx(
            r_explicit.framing_decision.dimensions.height, abs=1e-6
        )

    def test_even_up_vs_even_round_inner_geometry_matches(self, source_fdl):
        """Framing dims match across modes; canvas dims may or may not differ for a given fixture."""
        r_up = self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.UP)
        r_round = self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.ROUND)
        assert r_up.framing_decision.dimensions.height == pytest.approx(
            r_round.framing_decision.dimensions.height, abs=1e-6
        )
        _assert_canvas_dimensions_integer(r_up.canvas)
        _assert_canvas_dimensions_integer(r_round.canvas)

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
    def test_canvas_dimensions_integer_all_modes(self, source_fdl, even, mode):
        result = self._apply_with_rounding(source_fdl, even, mode)
        _assert_canvas_dimensions_integer(result.canvas)

    @pytest.mark.parametrize(
        ("even", "mode"),
        [
            (RoundingEven.EVEN, RoundingMode.UP),
            (RoundingEven.EVEN, RoundingMode.DOWN),
            (RoundingEven.EVEN, RoundingMode.ROUND),
        ],
    )
    def test_framing_dimensions_remain_float_all_modes(self, source_fdl, even, mode):
        result = self._apply_with_rounding(source_fdl, even, mode)
        _assert_framing_float(result.framing_decision)

    def test_distinct_rounding_modes_can_change_canvas_height(self, source_fdl):
        heights = {
            self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.UP).canvas.dimensions.height,
            self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.DOWN).canvas.dimensions.height,
            self._apply_with_rounding(source_fdl, RoundingEven.EVEN, RoundingMode.ROUND).canvas.dimensions.height,
        }
        assert len(heights) > 1


# ---------------------------------------------------------------------------
# JSON round-trip: template without round field
# ---------------------------------------------------------------------------

class TestJsonRoundTrip:

    def test_parse_template_without_round(self):
        """JSON omitting ``round`` yields spec default even/up on the accessor."""
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
        assert templates[0].round.even == RoundingEven.EVEN
        assert templates[0].round.mode == RoundingMode.UP

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
