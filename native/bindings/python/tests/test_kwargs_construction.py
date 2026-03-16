# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Tests for kwargs construction of fdl_core facade classes.

Each facade class should be constructible with keyword arguments matching
the Pydantic model API, creating an internal backing document transparently.
"""

from __future__ import annotations

import pytest
from fdl.constants import FitMethod, GeometryPath, HAlign, RoundingEven, RoundingMode, VAlign

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
)


class TestFramingIntentKwargs:
    """FramingIntent kwargs construction (depth 1: doc → FI)."""

    def test_basic_construction(self):
        fi = FramingIntent(
            id="FI-001",
            label="1.78-1 Framing",
            aspect_ratio=DimensionsInt(width=16, height=9),
            protection=0.088,
        )
        assert fi.id == "FI-001"
        assert fi.label == "1.78-1 Framing"
        assert fi.aspect_ratio.width == 16
        assert fi.aspect_ratio.height == 9
        assert fi.protection == pytest.approx(0.088)

    def test_as_dict(self):
        fi = FramingIntent(
            id="FI-002",
            label="Test FI",
            aspect_ratio=DimensionsInt(width=4, height=3),
            protection=0.1,
        )
        d = fi.as_dict()
        assert d["id"] == "FI-002"
        assert d["label"] == "Test FI"
        assert d["aspect_ratio"]["width"] == 4
        assert d["aspect_ratio"]["height"] == 3
        assert d["protection"] == pytest.approx(0.1)

    def test_equality(self):
        fi1 = FramingIntent(id="FI-X", label="A", aspect_ratio=DimensionsInt(width=1, height=1), protection=0.0)
        fi2 = FramingIntent(id="FI-X", label="B", aspect_ratio=DimensionsInt(width=2, height=2), protection=0.5)
        assert fi1 == fi2  # equality by id


class TestContextKwargs:
    """Context kwargs construction (depth 1: doc → Context)."""

    def test_basic_construction(self):
        ctx = Context(label="Primary")
        assert ctx.label == "Primary"
        assert ctx.context_creator is None

    def test_with_context_creator(self):
        ctx = Context(label="Secondary", context_creator="MyTool v1.0")
        assert ctx.label == "Secondary"
        assert ctx.context_creator == "MyTool v1.0"

    def test_canvases_ignored(self):
        """The canvases kwarg is accepted but ignored (API compat)."""
        ctx = Context(label="Test", canvases=["something"])
        assert ctx.label == "Test"
        assert len(ctx.canvases) == 0

    def test_as_dict(self):
        ctx = Context(label="Ctx1", context_creator="tool")
        d = ctx.as_dict()
        assert d["label"] == "Ctx1"
        assert d["context_creator"] == "tool"

    def test_equality(self):
        ctx1 = Context(label="Same")
        ctx2 = Context(label="Same", context_creator="different")
        assert ctx1 == ctx2  # equality by label


class TestCanvasKwargs:
    """Canvas kwargs construction (depth 2: doc → Context → Canvas)."""

    def test_basic_construction(self):
        canvas = Canvas(
            id="CNV-001",
            label="Main Canvas",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=5184, height=4320),
        )
        assert canvas.id == "CNV-001"
        assert canvas.label == "Main Canvas"
        assert canvas.source_canvas_id == "SRC-001"
        assert canvas.dimensions.width == 5184
        assert canvas.dimensions.height == 4320
        assert canvas.anamorphic_squeeze == pytest.approx(1.0)

    def test_with_anamorphic_squeeze(self):
        canvas = Canvas(
            id="CNV-002",
            label="Anamorphic",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=3840, height=2160),
            anamorphic_squeeze=2.0,
        )
        assert canvas.anamorphic_squeeze == pytest.approx(2.0)

    def test_with_effective_dimensions(self):
        canvas = Canvas(
            id="CNV-003",
            label="Effective",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=5184, height=4320),
            effective_dimensions=DimensionsInt(width=4728, height=3456),
            effective_anchor_point=PointFloat(x=228.0, y=432.0),
        )
        assert canvas.effective_dimensions is not None
        assert canvas.effective_dimensions.width == 4728
        assert canvas.effective_dimensions.height == 3456
        assert canvas.effective_anchor_point is not None
        assert canvas.effective_anchor_point.x == pytest.approx(228.0)
        assert canvas.effective_anchor_point.y == pytest.approx(432.0)

    def test_optional_fields_none(self):
        canvas = Canvas(
            id="CNV-004",
            label="Minimal",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=1920, height=1080),
        )
        assert canvas.effective_dimensions is None
        assert canvas.effective_anchor_point is None
        assert canvas.photosite_dimensions is None
        assert canvas.physical_dimensions is None

    def test_with_photosite_dimensions(self):
        canvas = Canvas(
            id="CNV-005",
            label="Photosite",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=5184, height=4320),
            photosite_dimensions=DimensionsInt(width=6000, height=5000),
        )
        assert canvas.photosite_dimensions is not None
        assert canvas.photosite_dimensions.width == 6000
        assert canvas.photosite_dimensions.height == 5000

    def test_with_physical_dimensions(self):
        canvas = Canvas(
            id="CNV-006",
            label="Physical",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=5184, height=4320),
            physical_dimensions=DimensionsFloat(width=36.0, height=24.0),
        )
        assert canvas.physical_dimensions is not None
        assert canvas.physical_dimensions.width == pytest.approx(36.0)
        assert canvas.physical_dimensions.height == pytest.approx(24.0)

    def test_framing_decisions_ignored(self):
        """The framing_decisions kwarg is accepted but ignored."""
        canvas = Canvas(
            id="CNV-007",
            label="FD test",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=1920, height=1080),
            framing_decisions=["ignored"],
        )
        assert len(canvas.framing_decisions) == 0

    def test_as_dict(self):
        canvas = Canvas(
            id="CNV-008",
            label="Dump Test",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=3840, height=2160),
            effective_dimensions=DimensionsInt(width=3000, height=2000),
            effective_anchor_point=PointFloat(x=420.0, y=80.0),
        )
        d = canvas.as_dict()
        assert d["id"] == "CNV-008"
        assert d["dimensions"]["width"] == 3840
        assert d["effective_dimensions"]["width"] == 3000
        assert d["effective_anchor_point"]["x"] == pytest.approx(420.0)

    def test_all_optional_fields(self):
        """Construct with ALL optional fields provided."""
        canvas = Canvas(
            id="CNV-009",
            label="Full",
            source_canvas_id="SRC-001",
            dimensions=DimensionsInt(width=5184, height=4320),
            anamorphic_squeeze=1.5,
            effective_dimensions=DimensionsInt(width=4000, height=3000),
            effective_anchor_point=PointFloat(x=100.0, y=200.0),
            photosite_dimensions=DimensionsInt(width=6000, height=5000),
            physical_dimensions=DimensionsFloat(width=36.0, height=24.0),
        )
        assert canvas.anamorphic_squeeze == pytest.approx(1.5)
        assert canvas.effective_dimensions.width == 4000
        assert canvas.photosite_dimensions.width == 6000
        assert canvas.physical_dimensions.width == pytest.approx(36.0)


class TestFramingDecisionKwargs:
    """FramingDecision kwargs construction (depth 3: doc → Context → Canvas → FD)."""

    def test_basic_construction(self):
        fd = FramingDecision(
            id="FD-001",
            label="1.78-1 Framing",
            framing_intent_id="FI-001",
            dimensions=DimensionsFloat(width=4728.0, height=3456.0),
            anchor_point=PointFloat(x=228.0, y=432.0),
        )
        assert fd.id == "FD-001"
        assert fd.label == "1.78-1 Framing"
        assert fd.framing_intent_id == "FI-001"
        assert fd.dimensions.width == pytest.approx(4728.0)
        assert fd.dimensions.height == pytest.approx(3456.0)
        assert fd.anchor_point.x == pytest.approx(228.0)
        assert fd.anchor_point.y == pytest.approx(432.0)
        assert fd.protection_dimensions is None
        assert fd.protection_anchor_point is None

    def test_with_protection(self):
        fd = FramingDecision(
            id="FD-002",
            label="Protected",
            framing_intent_id="FI-001",
            dimensions=DimensionsFloat(width=4728.0, height=3456.0),
            anchor_point=PointFloat(x=228.0, y=432.0),
            protection_dimensions=DimensionsFloat(width=5184.0, height=3790.0),
            protection_anchor_point=PointFloat(x=0.0, y=265.0),
        )
        assert fd.protection_dimensions is not None
        assert fd.protection_dimensions.width == pytest.approx(5184.0)
        assert fd.protection_dimensions.height == pytest.approx(3790.0)
        assert fd.protection_anchor_point is not None
        assert fd.protection_anchor_point.x == pytest.approx(0.0)
        assert fd.protection_anchor_point.y == pytest.approx(265.0)

    def test_as_dict(self):
        fd = FramingDecision(
            id="FD-003",
            label="Dump",
            framing_intent_id="FI-X",
            dimensions=DimensionsFloat(width=100.0, height=200.0),
            anchor_point=PointFloat(x=10.0, y=20.0),
        )
        d = fd.as_dict()
        assert d["id"] == "FD-003"
        assert d["dimensions"]["width"] == pytest.approx(100.0)
        assert d["anchor_point"]["x"] == pytest.approx(10.0)

    def test_as_dict_with_protection(self):
        fd = FramingDecision(
            id="FD-004",
            label="Dump Protected",
            framing_intent_id="FI-X",
            dimensions=DimensionsFloat(width=100.0, height=200.0),
            anchor_point=PointFloat(x=10.0, y=20.0),
            protection_dimensions=DimensionsFloat(width=150.0, height=250.0),
            protection_anchor_point=PointFloat(x=5.0, y=15.0),
        )
        d = fd.as_dict()
        assert d["protection_dimensions"]["width"] == pytest.approx(150.0)
        assert d["protection_anchor_point"]["x"] == pytest.approx(5.0)

    def test_equality(self):
        fd1 = FramingDecision(
            id="FD-SAME",
            label="A",
            framing_intent_id="FI-1",
            dimensions=DimensionsFloat(width=1.0, height=1.0),
            anchor_point=PointFloat(x=0.0, y=0.0),
        )
        fd2 = FramingDecision(
            id="FD-SAME",
            label="B",
            framing_intent_id="FI-2",
            dimensions=DimensionsFloat(width=2.0, height=2.0),
            anchor_point=PointFloat(x=1.0, y=1.0),
        )
        assert fd1 == fd2  # equality by id


class TestCanvasTemplateKwargs:
    """CanvasTemplate kwargs construction (depth 1: doc → CT)."""

    def test_basic_construction(self):
        ct = CanvasTemplate(
            id="CT-001",
            label="HD Template",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.CANVAS_DIMENSIONS,
            fit_method=FitMethod.FIT_ALL,
            alignment_method_horizontal=HAlign.CENTER,
            alignment_method_vertical=VAlign.CENTER,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        assert ct.id == "CT-001"
        assert ct.label == "HD Template"
        assert ct.target_dimensions.width == 1920
        assert ct.target_dimensions.height == 1080
        assert ct.target_anamorphic_squeeze == pytest.approx(1.0)
        assert ct.fit_source == GeometryPath.CANVAS_DIMENSIONS
        assert ct.fit_method == FitMethod.FIT_ALL
        assert ct.alignment_method_horizontal == HAlign.CENTER
        assert ct.alignment_method_vertical == VAlign.CENTER
        assert ct.preserve_from_source_canvas is None
        assert ct.maximum_dimensions is None
        assert ct.pad_to_maximum is False

    def test_with_optional_fields(self):
        ct = CanvasTemplate(
            id="CT-002",
            label="With Optionals",
            target_dimensions=DimensionsInt(width=3840, height=2160),
            fit_source=GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            alignment_method_horizontal=HAlign.LEFT,
            alignment_method_vertical=VAlign.TOP,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
            preserve_from_source_canvas=GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
            maximum_dimensions=DimensionsInt(width=4096, height=2304),
            pad_to_maximum=True,
        )
        assert ct.preserve_from_source_canvas == GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS
        assert ct.maximum_dimensions is not None
        assert ct.maximum_dimensions.width == 4096
        assert ct.maximum_dimensions.height == 2304
        assert ct.pad_to_maximum is True

    def test_with_anamorphic_squeeze(self):
        ct = CanvasTemplate(
            id="CT-003",
            label="Anamorphic",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            target_anamorphic_squeeze=2.0,
            fit_source=GeometryPath.CANVAS_DIMENSIONS,
            fit_method=FitMethod.FIT_ALL,
            alignment_method_horizontal=HAlign.CENTER,
            alignment_method_vertical=VAlign.CENTER,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        assert ct.target_anamorphic_squeeze == pytest.approx(2.0)

    def test_as_dict(self):
        ct = CanvasTemplate(
            id="CT-004",
            label="Dump Test",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.CANVAS_DIMENSIONS,
            fit_method=FitMethod.FIT_ALL,
            alignment_method_horizontal=HAlign.CENTER,
            alignment_method_vertical=VAlign.CENTER,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        d = ct.as_dict()
        assert d["id"] == "CT-004"
        assert d["target_dimensions"]["width"] == 1920
        assert d["fit_source"] == "canvas.dimensions"
        assert d["fit_method"] == "fit_all"

    def test_pad_to_maximum_default_false(self):
        """pad_to_maximum should always be set (even when default False)."""
        ct = CanvasTemplate(
            id="CT-005",
            label="Pad Default",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            fit_source=GeometryPath.CANVAS_DIMENSIONS,
            fit_method=FitMethod.FIT_ALL,
            alignment_method_horizontal=HAlign.CENTER,
            alignment_method_vertical=VAlign.CENTER,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        assert ct.pad_to_maximum is False
        d = ct.as_dict()
        assert d["pad_to_maximum"] is False

    def test_equality(self):
        ct1 = CanvasTemplate(
            id="CT-SAME",
            label="A",
            target_dimensions=DimensionsInt(width=1, height=1),
            fit_source=GeometryPath.CANVAS_DIMENSIONS,
            fit_method=FitMethod.FIT_ALL,
            alignment_method_horizontal=HAlign.CENTER,
            alignment_method_vertical=VAlign.CENTER,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        ct2 = CanvasTemplate(
            id="CT-SAME",
            label="B",
            target_dimensions=DimensionsInt(width=2, height=2),
            fit_source=GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
            fit_method=FitMethod.HEIGHT,
            alignment_method_horizontal=HAlign.RIGHT,
            alignment_method_vertical=VAlign.BOTTOM,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
        )
        assert ct1 == ct2  # equality by id


class TestBackingDocumentInvisibility:
    """The internal backing document should be invisible to users."""

    def test_framing_intent_backing_not_leaked(self):
        """Creating a standalone FI shouldn't expose its backing doc."""
        fi = FramingIntent(
            id="FI-BACK",
            label="Backing Test",
            aspect_ratio=DimensionsInt(width=16, height=9),
            protection=0.1,
        )
        # The FI should function normally — reads work
        assert fi.id == "FI-BACK"
        # as_dict works (this uses the C handle, not the backing doc directly)
        d = fi.as_dict()
        assert d["id"] == "FI-BACK"

    def test_canvas_backing_not_leaked(self):
        """A standalone Canvas's backing scaffolding shouldn't affect behavior."""
        canvas = Canvas(
            id="CNV-BACK",
            label="Backing",
            source_canvas_id="SRC",
            dimensions=DimensionsInt(width=1920, height=1080),
        )
        # framing_decisions should be empty (no FDs added to this canvas)
        assert len(canvas.framing_decisions) == 0
        d = canvas.as_dict()
        assert d["id"] == "CNV-BACK"
        assert d["framing_decisions"] == []

    def test_framing_decision_backing_not_leaked(self):
        """A standalone FD's scaffolding (doc+context+canvas) shouldn't show."""
        fd = FramingDecision(
            id="FD-BACK",
            label="Backing",
            framing_intent_id="FI-1",
            dimensions=DimensionsFloat(width=100.0, height=100.0),
            anchor_point=PointFloat(x=0.0, y=0.0),
        )
        d = fd.as_dict()
        assert d["id"] == "FD-BACK"
        # as_dict should only contain FD fields, not parent chain
        assert "canvases" not in d
        assert "contexts" not in d


class TestKwargsVsBuilderParity:
    """Kwargs-constructed objects should behave identically to builder-constructed ones."""

    def test_framing_intent_parity(self):
        # Builder path
        doc = FDL.create(uuid="test-uuid")
        fi_builder = doc.add_framing_intent(
            id="FI-P1",
            label="Parity",
            aspect_ratio=DimensionsInt(width=16, height=9),
            protection=0.088,
        )
        # Kwargs path
        fi_kwargs = FramingIntent(
            id="FI-P1",
            label="Parity",
            aspect_ratio=DimensionsInt(width=16, height=9),
            protection=0.088,
        )
        assert fi_builder.as_dict() == fi_kwargs.as_dict()

    def test_framing_decision_parity(self):
        # Builder path
        doc = FDL.create(uuid="test-uuid")
        ctx = doc.add_context(label="ctx")
        canvas = ctx.add_canvas(
            id="cnv",
            label="cnv",
            source_canvas_id="src",
            dimensions=DimensionsInt(width=5184, height=4320),
            anamorphic_squeeze=1.0,
        )
        fd_builder = canvas.add_framing_decision(
            id="FD-P1",
            label="Parity",
            framing_intent_id="FI-1",
            dimensions=DimensionsFloat(width=4728.0, height=3456.0),
            anchor_point=PointFloat(x=228.0, y=432.0),
        )
        # Kwargs path
        fd_kwargs = FramingDecision(
            id="FD-P1",
            label="Parity",
            framing_intent_id="FI-1",
            dimensions=DimensionsFloat(width=4728.0, height=3456.0),
            anchor_point=PointFloat(x=228.0, y=432.0),
        )
        assert fd_builder.as_dict() == fd_kwargs.as_dict()
