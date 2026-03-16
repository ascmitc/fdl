# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Facade mutation tests — verify builders, setters, and apply work correctly.

Requires: libfdl_core built and discoverable.
"""

from __future__ import annotations

import json

import pytest

from fdl import DimensionsFloat, DimensionsInt, FitMethod, GeometryPath, HAlign, PointFloat, RoundStrategy, VAlign

try:
    from fdl_ffi import is_available

    HAS_CORE = is_available()
except ImportError:
    HAS_CORE = False

pytestmark = pytest.mark.skipif(not HAS_CORE, reason="fdl_core library not available")


# -----------------------------------------------------------------------
# Document.create
# -----------------------------------------------------------------------


class TestDocumentCreate:
    def test_create_empty_document(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", fdl_creator="test") as doc:
            assert doc.uuid == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
            assert doc.version_major == 2
            assert doc.version_minor == 0
            assert doc.fdl_creator == "test"
            assert doc.default_framing_intent is None
            assert len(doc.contexts) == 0
            assert len(doc.framing_intents) == 0
            assert len(doc.canvas_templates) == 0

    def test_create_with_default_fi(self):
        from fdl import FDL

        with FDL.create(
            uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            fdl_creator="test",
            default_framing_intent="FI_01",
        ) as doc:
            assert doc.default_framing_intent == "FI_01"


# -----------------------------------------------------------------------
# String property setters
# -----------------------------------------------------------------------


class TestPropertySetters:
    def test_set_uuid(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            doc.uuid = "11111111-2222-3333-4444-555555555555"
            assert doc.uuid == "11111111-2222-3333-4444-555555555555"

    def test_set_fdl_creator(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            doc.fdl_creator = "updated_creator"
            assert doc.fdl_creator == "updated_creator"

    def test_set_default_framing_intent(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            doc.default_framing_intent = "FI_NEW"
            assert doc.default_framing_intent == "FI_NEW"


# -----------------------------------------------------------------------
# Collection builders (add methods)
# -----------------------------------------------------------------------


class TestAddFramingIntent:
    def test_add_framing_intent(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            fi = doc.add_framing_intent(
                id="FI_01",
                label="Default",
                aspect_ratio=DimensionsInt(width=16, height=9),
                protection=0.0,
            )
            assert fi.id == "FI_01"
            assert fi.label == "Default"
            assert fi.aspect_ratio.width == 16
            assert fi.aspect_ratio.height == 9
            assert fi.protection == 0.0
            assert len(doc.framing_intents) == 1

    def test_add_multiple_framing_intents(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            doc.add_framing_intent("FI_01", "Default", DimensionsInt(width=16, height=9), 0.0)
            doc.add_framing_intent("FI_02", "Alt", DimensionsInt(width=4, height=3), 0.05)
            assert len(doc.framing_intents) == 2
            assert doc.framing_intents[1].id == "FI_02"
            assert doc.framing_intents[1].protection == pytest.approx(0.05)


class TestAddContext:
    def test_add_context(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            ctx = doc.add_context(label="Source", context_creator="test")
            assert ctx.label == "Source"
            assert ctx.context_creator == "test"
            assert len(doc.contexts) == 1

    def test_add_context_no_creator(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            ctx = doc.add_context(label="Source")
            assert ctx.label == "Source"
            assert ctx.context_creator is None


class TestAddCanvas:
    def test_add_canvas_to_context(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            ctx = doc.add_context("Source")
            canvas = ctx.add_canvas(
                id="CV_01",
                label="Source Canvas",
                source_canvas_id="CV_01",
                dimensions=DimensionsInt(width=3840, height=2160),
                anamorphic_squeeze=1.0,
            )
            assert canvas.id == "CV_01"
            assert canvas.label == "Source Canvas"
            assert canvas.source_canvas_id == "CV_01"
            assert canvas.dimensions.width == 3840
            assert canvas.dimensions.height == 2160
            assert canvas.anamorphic_squeeze == 1.0
            assert len(ctx.canvases) == 1


class TestAddFramingDecision:
    def test_add_framing_decision(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            doc.add_framing_intent("FI_01", "Default", DimensionsInt(width=16, height=9), 0.0)
            ctx = doc.add_context("Source")
            canvas = ctx.add_canvas("CV_01", "Source Canvas", "CV_01", DimensionsInt(width=3840, height=2160), 1.0)
            fd = canvas.add_framing_decision(
                id="CV_01-FI_01",
                label="Default FD",
                framing_intent_id="FI_01",
                dimensions=DimensionsFloat(width=3840.0, height=2160.0),
                anchor_point=PointFloat(x=0.0, y=0.0),
            )
            assert fd.id == "CV_01-FI_01"
            assert fd.label == "Default FD"
            assert fd.framing_intent_id == "FI_01"
            assert fd.dimensions.width == pytest.approx(3840.0)
            assert fd.dimensions.height == pytest.approx(2160.0)
            assert fd.anchor_point.x == pytest.approx(0.0)
            assert fd.anchor_point.y == pytest.approx(0.0)
            assert len(canvas.framing_decisions) == 1


# -----------------------------------------------------------------------
# Compound setters
# -----------------------------------------------------------------------


class TestCompoundSetters:
    def test_set_effective_dimensions(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            ctx = doc.add_context("Source")
            canvas = ctx.add_canvas("CV_01", "Source", "CV_01", DimensionsInt(width=3840, height=2160), 1.0)
            assert canvas.effective_dimensions is None
            assert canvas.effective_anchor_point is None

            canvas.set_effective(
                dims=DimensionsInt(width=3000, height=1688),
                anchor=PointFloat(x=420.0, y=236.0),
            )
            assert canvas.effective_dimensions.width == 3000
            assert canvas.effective_dimensions.height == 1688
            assert canvas.effective_anchor_point.x == pytest.approx(420.0)
            assert canvas.effective_anchor_point.y == pytest.approx(236.0)

    def test_set_protection(self):
        from fdl import FDL

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            doc.add_framing_intent("FI_01", "Default", DimensionsInt(width=16, height=9), 0.05)
            ctx = doc.add_context("Source")
            canvas = ctx.add_canvas("CV_01", "Source", "CV_01", DimensionsInt(width=3840, height=2160), 1.0)
            fd = canvas.add_framing_decision(
                "CV_01-FI_01",
                "Default FD",
                "FI_01",
                DimensionsFloat(width=3840.0, height=2160.0),
                PointFloat(x=0.0, y=0.0),
            )
            assert fd.protection_dimensions is None

            fd.set_protection(
                dims=DimensionsFloat(width=4032.0, height=2268.0),
                anchor=PointFloat(x=-96.0, y=-54.0),
            )
            assert fd.protection_dimensions.width == pytest.approx(4032.0)
            assert fd.protection_dimensions.height == pytest.approx(2268.0)
            assert fd.protection_anchor_point.x == pytest.approx(-96.0)
            assert fd.protection_anchor_point.y == pytest.approx(-54.0)


# -----------------------------------------------------------------------
# CanvasTemplate
# -----------------------------------------------------------------------


class TestCanvasTemplate:
    def test_add_canvas_template(self):
        from fdl import FDL, RoundingEven, RoundingMode

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            ct = doc.add_canvas_template(
                id="CT_01",
                label="HD Delivery",
                target_dimensions=DimensionsInt(width=1920, height=1080),
                target_anamorphic_squeeze=1.0,
                fit_source=GeometryPath.CANVAS_DIMENSIONS,
                fit_method=FitMethod.WIDTH,
                alignment_method_horizontal=HAlign.CENTER,
                alignment_method_vertical=VAlign.CENTER,
                round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
            )
            assert ct.id == "CT_01"
            assert ct.label == "HD Delivery"
            assert ct.target_dimensions.width == 1920
            assert ct.target_dimensions.height == 1080
            assert ct.target_anamorphic_squeeze == 1.0
            assert ct.fit_source == GeometryPath.CANVAS_DIMENSIONS
            assert ct.fit_method == FitMethod.WIDTH
            assert ct.alignment_method_horizontal == HAlign.CENTER
            assert ct.alignment_method_vertical == VAlign.CENTER
            assert len(doc.canvas_templates) == 1

    def test_set_optional_properties(self):
        from fdl import FDL, RoundingEven, RoundingMode

        with FDL.create(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") as doc:
            ct = doc.add_canvas_template(
                id="CT_01",
                label="HD Delivery",
                target_dimensions=DimensionsInt(width=1920, height=1080),
                target_anamorphic_squeeze=1.0,
                fit_source=GeometryPath.CANVAS_DIMENSIONS,
                fit_method=FitMethod.WIDTH,
                alignment_method_horizontal=HAlign.CENTER,
                alignment_method_vertical=VAlign.CENTER,
                round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
            )
            assert ct.preserve_from_source_canvas is None
            assert ct.maximum_dimensions is None
            assert ct.pad_to_maximum is False

            ct.preserve_from_source_canvas = GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS
            ct.maximum_dimensions = DimensionsInt(width=4096, height=2160)
            ct.pad_to_maximum = True

            assert ct.preserve_from_source_canvas == GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS
            assert ct.maximum_dimensions.width == 4096
            assert ct.maximum_dimensions.height == 2160
            assert ct.pad_to_maximum is True


# -----------------------------------------------------------------------
# Apply canvas template
# -----------------------------------------------------------------------


class TestApplyCanvasTemplate:
    def test_apply_canvas_template(self):
        from fdl import FDL, RoundingEven, RoundingMode

        with FDL.create(
            uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            fdl_creator="test",
            default_framing_intent="FI_01",
        ) as doc:
            doc.add_framing_intent("FI_01", "Default", DimensionsInt(width=16, height=9), 0.0)
            ctx = doc.add_context("Source", "test")
            canvas = ctx.add_canvas("CV_01", "Source Canvas", "CV_01", DimensionsInt(width=3840, height=2160), 1.0)
            fd = canvas.add_framing_decision(
                "CV_01-FI_01",
                "Default FD",
                "FI_01",
                DimensionsFloat(width=3840.0, height=2160.0),
                PointFloat(x=0.0, y=0.0),
            )
            ct = doc.add_canvas_template(
                id="CT_01",
                label="HD Delivery",
                target_dimensions=DimensionsInt(width=1920, height=1080),
                target_anamorphic_squeeze=1.0,
                fit_source=GeometryPath.CANVAS_DIMENSIONS,
                fit_method=FitMethod.WIDTH,
                alignment_method_horizontal=HAlign.CENTER,
                alignment_method_vertical=VAlign.CENTER,
                round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
            )

            result = ct.apply(
                source_canvas=canvas,
                source_framing=fd,
                new_canvas_id="CV_02",
                new_fd_name="HD FD",
                source_context_label="Source",
                context_creator="test",
            )

            assert result.canvas.get_custom_attr("scale_factor") == pytest.approx(0.5)
            assert result.fdl is not None
            result.fdl.close()

    def test_apply_template_squeeze_zero_inherits_source(self):
        """target_anamorphic_squeeze=0 should inherit squeeze from source canvas."""
        from fdl import FDL, RoundingEven, RoundingMode

        with FDL.create(
            uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            fdl_creator="test",
            default_framing_intent="FI_01",
        ) as doc:
            doc.add_framing_intent("FI_01", "Default", DimensionsInt(width=16, height=9), 0.0)
            ctx = doc.add_context("Source", "test")
            # Anamorphic source canvas with squeeze=2.0
            canvas = ctx.add_canvas("CV_01", "Anamorphic", "CV_01", DimensionsInt(width=4096, height=3432), 2.0)
            fd = canvas.add_framing_decision(
                "CV_01-FI_01",
                "Default FD",
                "FI_01",
                DimensionsFloat(width=4096.0, height=1714.0),
                PointFloat(x=0.0, y=859.0),
            )
            ct = doc.add_canvas_template(
                id="CT_01",
                label="Squeeze Zero",
                target_dimensions=DimensionsInt(width=1920, height=1080),
                target_anamorphic_squeeze=0.0,
                fit_source=GeometryPath.FRAMING_DIMENSIONS,
                fit_method=FitMethod.WIDTH,
                alignment_method_horizontal=HAlign.CENTER,
                alignment_method_vertical=VAlign.CENTER,
                round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.UP),
            )

            result = ct.apply(
                source_canvas=canvas,
                source_framing=fd,
                new_canvas_id="CV_02",
                new_fd_name="Inherited Squeeze",
                source_context_label="Source",
                context_creator="test",
            )

            # Output canvas should have squeeze=2.0 inherited from source, not 0
            assert result.canvas.anamorphic_squeeze == pytest.approx(2.0)
            assert result.fdl is not None
            result.fdl.close()


# -----------------------------------------------------------------------
# as_dict after mutation
# -----------------------------------------------------------------------


class TestModelDumpAfterMutation:
    def test_as_dict_roundtrip(self):
        from fdl import FDL

        with FDL.create(
            uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            fdl_creator="test",
            default_framing_intent="FI_01",
        ) as doc:
            doc.add_framing_intent("FI_01", "Default", DimensionsInt(width=16, height=9), 0.0)
            ctx = doc.add_context("Source", "test")
            canvas = ctx.add_canvas("CV_01", "Source Canvas", "CV_01", DimensionsInt(width=3840, height=2160), 1.0)
            canvas.add_framing_decision(
                "CV_01-FI_01",
                "Default FD",
                "FI_01",
                DimensionsFloat(width=3840.0, height=2160.0),
                PointFloat(x=0.0, y=0.0),
            )

            data = doc.as_dict()
            assert data["uuid"] == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
            assert data["fdl_creator"] == "test"
            assert data["default_framing_intent"] == "FI_01"
            assert len(data["framing_intents"]) == 1
            assert len(data["contexts"]) == 1
            assert len(data["contexts"][0]["canvases"]) == 1
            assert len(data["contexts"][0]["canvases"][0]["framing_decisions"]) == 1

            # Roundtrip through JSON
            json_str = doc.as_json(indent=2)
            reparsed = json.loads(json_str)
            assert reparsed["uuid"] == data["uuid"]
            assert reparsed["framing_intents"][0]["id"] == "FI_01"
