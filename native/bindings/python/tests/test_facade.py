# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Facade tests — verify handle-backed Python objects work correctly.

Requires: libfdl_core built and discoverable.
"""

from __future__ import annotations

import json

import pytest

try:
    from fdl_ffi import is_available

    HAS_CORE = is_available()
except ImportError:
    HAS_CORE = False

pytestmark = pytest.mark.skipif(not HAS_CORE, reason="fdl_core library not available")

_MINIMAL_FDL = {
    "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "version": {"major": 2, "minor": 0},
    "fdl_creator": "test",
    "default_framing_intent": "FI_01",
    "framing_intents": [
        {
            "id": "FI_01",
            "label": "Default",
            "aspect_ratio": {"width": 16, "height": 9},
            "protection": 0.0,
        }
    ],
    "contexts": [
        {
            "label": "Source",
            "canvases": [
                {
                    "id": "CV_01",
                    "label": "Source Canvas",
                    "source_canvas_id": "CV_01",
                    "dimensions": {"width": 3840, "height": 2160},
                    "anamorphic_squeeze": 1.0,
                    "framing_decisions": [
                        {
                            "id": "CV_01-FI_01",
                            "label": "Default FD",
                            "framing_intent_id": "FI_01",
                            "dimensions": {"width": 3840.0, "height": 2160.0},
                            "anchor_point": {"x": 0.0, "y": 0.0},
                        }
                    ],
                }
            ],
        }
    ],
    "canvas_templates": [],
}


@pytest.fixture
def doc():
    from fdl import FDL

    json_bytes = json.dumps(_MINIMAL_FDL).encode()
    d = FDL.parse(json_bytes)
    yield d
    d.close()


# -----------------------------------------------------------------------
# Document
# -----------------------------------------------------------------------


class TestDocument:
    def test_parse(self, doc):
        from fdl import FDL

        assert isinstance(doc, FDL)

    def test_uuid(self, doc):
        assert doc.uuid == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    def test_fdl_creator(self, doc):
        assert doc.fdl_creator == "test"

    def test_default_framing_intent(self, doc):
        assert doc.default_framing_intent == "FI_01"

    def test_version(self, doc):
        v = doc.version
        assert v.major == 2
        assert v.minor == 0

    def test_version_major_minor(self, doc):
        assert doc.version_major == 2
        assert doc.version_minor == 0

    def test_context_manager(self):
        from fdl import FDL

        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        with FDL.parse(json_bytes) as d:
            assert d.uuid == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        # After context manager, handle is freed
        with pytest.raises(RuntimeError):
            _ = d.uuid

    def test_double_close(self, doc):
        doc.close()
        doc.close()  # Should not raise

    def test_as_dict(self, doc):
        d = doc.as_dict()
        assert isinstance(d, dict)
        assert d["uuid"] == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        assert d["version"] == {"major": 2, "minor": 0}
        assert len(d["contexts"]) == 1
        assert len(d["framing_intents"]) == 1

    def test_as_dict_json(self, doc):
        s = doc.as_json(indent=2)
        assert isinstance(s, str)
        parsed = json.loads(s)
        assert parsed["uuid"] == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    def test_validate_valid(self, doc):
        doc.validate()  # Should not raise


# -----------------------------------------------------------------------
# Collections
# -----------------------------------------------------------------------


class TestCollections:
    def test_contexts_len(self, doc):
        assert len(doc.contexts) == 1

    def test_contexts_iter(self, doc):
        labels = [ctx.label for ctx in doc.contexts]
        assert labels == ["Source"]

    def test_contexts_getitem(self, doc):
        ctx = doc.contexts[0]
        assert ctx.label == "Source"

    def test_contexts_negative_index(self, doc):
        ctx = doc.contexts[-1]
        assert ctx.label == "Source"

    def test_contexts_index_error(self, doc):
        with pytest.raises(IndexError):
            doc.contexts[99]

    def test_contexts_get_by_id(self, doc):
        ctx = doc.contexts.get_by_id("Source")
        assert ctx is not None
        assert ctx.label == "Source"

    def test_contexts_get_by_id_not_found(self, doc):
        assert doc.contexts.get_by_id("Nonexistent") is None

    def test_contexts_contains(self, doc):
        ctx = doc.contexts[0]
        assert ctx in doc.contexts

    def test_contexts_bool(self, doc):
        assert bool(doc.contexts)

    def test_framing_intents_len(self, doc):
        assert len(doc.framing_intents) == 1

    def test_framing_intents_get_by_id(self, doc):
        fi = doc.framing_intents.get_by_id("FI_01")
        assert fi is not None
        assert fi.id == "FI_01"

    def test_canvas_templates_empty(self, doc):
        assert len(doc.canvas_templates) == 0
        assert not bool(doc.canvas_templates)


# -----------------------------------------------------------------------
# Context
# -----------------------------------------------------------------------


class TestContext:
    def test_label(self, doc):
        ctx = doc.contexts[0]
        assert ctx.label == "Source"

    def test_context_creator(self, doc):
        ctx = doc.contexts[0]
        assert ctx.context_creator is None

    def test_clip_id_none(self, doc):
        ctx = doc.contexts[0]
        assert ctx.clip_id is None

    def test_canvases(self, doc):
        ctx = doc.contexts[0]
        assert len(ctx.canvases) == 1

    def test_equality(self, doc):
        ctx = doc.contexts[0]
        assert ctx == "Source"

    def test_hash(self, doc):
        ctx = doc.contexts[0]
        assert hash(ctx) == hash(("Source",))

    def test_as_dict(self, doc):
        ctx = doc.contexts[0]
        d = ctx.as_dict()
        assert d["label"] == "Source"
        assert len(d["canvases"]) == 1

    def test_set_clip_id(self, doc):
        ctx = doc.contexts[0]
        assert ctx.clip_id is None
        ctx.clip_id = {"clip_name": "A001", "file": "A001C001.ari"}
        cid = ctx.clip_id
        assert cid is not None
        assert cid.clip_name == "A001"
        assert cid.file == "A001C001.ari"
        assert cid.sequence is None

    def test_set_clip_id_sequence(self, doc):
        ctx = doc.contexts[0]
        ctx.clip_id = {
            "clip_name": "B001",
            "sequence": {"value": "B001.####.exr", "idx": "#", "min": 0, "max": 100},
        }
        cid = ctx.clip_id
        assert cid is not None
        assert cid.clip_name == "B001"
        assert cid.file is None
        assert cid.sequence is not None
        assert cid.sequence.value == "B001.####.exr"

    def test_remove_clip_id(self, doc):
        ctx = doc.contexts[0]
        ctx.clip_id = {"clip_name": "A001", "file": "A001C001.ari"}
        assert ctx.clip_id is not None
        ctx.clip_id = None
        assert ctx.clip_id is None


# -----------------------------------------------------------------------
# Canvas
# -----------------------------------------------------------------------


class TestCanvas:
    def test_id(self, doc):
        canvas = doc.contexts[0].canvases[0]
        assert canvas.id == "CV_01"

    def test_label(self, doc):
        canvas = doc.contexts[0].canvases[0]
        assert canvas.label == "Source Canvas"

    def test_source_canvas_id(self, doc):
        canvas = doc.contexts[0].canvases[0]
        assert canvas.source_canvas_id == "CV_01"

    def test_dimensions(self, doc):
        canvas = doc.contexts[0].canvases[0]
        dims = canvas.dimensions
        assert dims.width == 3840
        assert dims.height == 2160

    def test_anamorphic_squeeze(self, doc):
        canvas = doc.contexts[0].canvases[0]
        assert canvas.anamorphic_squeeze == 1.0

    def test_optional_none(self, doc):
        canvas = doc.contexts[0].canvases[0]
        assert canvas.effective_dimensions is None
        assert canvas.effective_anchor_point is None
        assert canvas.photosite_dimensions is None
        assert canvas.physical_dimensions is None

    def test_equality(self, doc):
        canvas = doc.contexts[0].canvases[0]
        assert canvas == "CV_01"

    def test_hash(self, doc):
        canvas = doc.contexts[0].canvases[0]
        assert hash(canvas) == hash(("CV_01",))

    def test_as_dict(self, doc):
        canvas = doc.contexts[0].canvases[0]
        d = canvas.as_dict()
        assert d["id"] == "CV_01"
        assert d["dimensions"]["width"] == 3840


# -----------------------------------------------------------------------
# FramingDecision
# -----------------------------------------------------------------------


class TestFramingDecision:
    def test_properties(self, doc):
        fd = doc.contexts[0].canvases[0].framing_decisions[0]
        assert fd.id == "CV_01-FI_01"
        assert fd.label == "Default FD"
        assert fd.framing_intent_id == "FI_01"

    def test_dimensions(self, doc):
        fd = doc.contexts[0].canvases[0].framing_decisions[0]
        assert fd.dimensions.width == 3840.0
        assert fd.dimensions.height == 2160.0

    def test_anchor_point(self, doc):
        fd = doc.contexts[0].canvases[0].framing_decisions[0]
        assert fd.anchor_point.x == 0.0
        assert fd.anchor_point.y == 0.0

    def test_protection_none(self, doc):
        fd = doc.contexts[0].canvases[0].framing_decisions[0]
        assert fd.protection_dimensions is None
        assert fd.protection_anchor_point is None

    def test_equality(self, doc):
        fd = doc.contexts[0].canvases[0].framing_decisions[0]
        assert fd == "CV_01-FI_01"

    def test_as_dict(self, doc):
        fd = doc.contexts[0].canvases[0].framing_decisions[0]
        d = fd.as_dict()
        assert d["id"] == "CV_01-FI_01"
        assert d["dimensions"]["width"] == 3840.0


# -----------------------------------------------------------------------
# FramingIntent
# -----------------------------------------------------------------------


class TestFramingIntent:
    def test_properties(self, doc):
        fi = doc.framing_intents[0]
        assert fi.id == "FI_01"
        assert fi.label == "Default"

    def test_aspect_ratio(self, doc):
        fi = doc.framing_intents[0]
        assert fi.aspect_ratio.width == 16
        assert fi.aspect_ratio.height == 9

    def test_protection(self, doc):
        fi = doc.framing_intents[0]
        assert fi.protection == 0.0

    def test_equality(self, doc):
        fi = doc.framing_intents[0]
        assert fi == "FI_01"

    def test_as_dict(self, doc):
        fi = doc.framing_intents[0]
        d = fi.as_dict()
        assert d["id"] == "FI_01"
        assert d["aspect_ratio"]["width"] == 16


# -----------------------------------------------------------------------
# as_dict parity — facade vs Pydantic
# -----------------------------------------------------------------------


class TestModelDumpParity:
    def test_document_as_dict_matches(self, doc):
        """Verify FDL.as_dict() matches original parsed JSON structure."""
        d = doc.as_dict()
        assert d["uuid"] == _MINIMAL_FDL["uuid"]
        assert d["version"] == _MINIMAL_FDL["version"]
        assert d["fdl_creator"] == _MINIMAL_FDL["fdl_creator"]
        assert d["default_framing_intent"] == _MINIMAL_FDL["default_framing_intent"]
        assert len(d["contexts"]) == len(_MINIMAL_FDL["contexts"])
        assert len(d["framing_intents"]) == len(_MINIMAL_FDL["framing_intents"])

    def test_context_as_dict_structure(self, doc):
        ctx_dump = doc.contexts[0].as_dict()
        assert "label" in ctx_dump
        assert "canvases" in ctx_dump

    def test_canvas_as_dict_structure(self, doc):
        canvas_dump = doc.contexts[0].canvases[0].as_dict()
        assert "id" in canvas_dump
        assert "dimensions" in canvas_dump
        assert "framing_decisions" in canvas_dump

    def test_exclude_none(self, doc):
        canvas_dump = doc.contexts[0].canvases[0].as_dict()
        # Optional None fields should be excluded
        assert "effective_dimensions" not in canvas_dump
        assert "photosite_dimensions" not in canvas_dump
        assert "physical_dimensions" not in canvas_dump
        # Required fields still present
        assert "id" in canvas_dump
        assert "dimensions" in canvas_dump


# -----------------------------------------------------------------------
# ResolveCanvasForDimensions
# -----------------------------------------------------------------------


class TestResolveCanvas:
    """Tests for Context.resolve_canvas_for_dimensions."""

    @pytest.fixture
    def resolve_doc(self):
        """Build an FDL with two canvases: a source and a derived sibling."""
        from fdl import FDL, DimensionsFloat, DimensionsInt, PointFloat

        fdl_doc = FDL(fdl_creator="test")
        fdl_doc.add_framing_intent(
            id="fi_main",
            label="Main FI",
            aspect_ratio=DimensionsInt(width=16, height=9),
            protection=0.0,
        )
        ctx = fdl_doc.add_context(label="ctx", context_creator="tester")

        # Source canvas (1920x1080) - id == source_canvas_id
        canvas1 = ctx.add_canvas(
            id="cvs1",
            label="Canvas 1920x1080",
            source_canvas_id="cvs1",
            dimensions=DimensionsInt(width=1920, height=1080),
            anamorphic_squeeze=1.0,
        )
        fd1 = canvas1.add_framing_decision(
            id="fd1",
            label="Main",
            framing_intent_id="fi_main",
            dimensions=DimensionsFloat(width=1920.0, height=1080.0),
            anchor_point=PointFloat(x=0.0, y=0.0),
        )

        # Derived canvas (3840x2160) - source_canvas_id points to cvs1
        canvas2 = ctx.add_canvas(
            id="cvs2",
            label="Canvas 3840x2160",
            source_canvas_id="cvs1",
            dimensions=DimensionsInt(width=3840, height=2160),
            anamorphic_squeeze=1.0,
        )
        fd2 = canvas2.add_framing_decision(
            id="fd2",
            label="Main",
            framing_intent_id="fi_main",
            dimensions=DimensionsFloat(width=3840.0, height=2160.0),
            anchor_point=PointFloat(x=0.0, y=0.0),
        )

        yield {
            "doc": fdl_doc,
            "ctx": ctx,
            "canvas1": canvas1,
            "fd1": fd1,
            "canvas2": canvas2,
            "fd2": fd2,
        }
        fdl_doc.close()

    def test_exact_match(self, resolve_doc):
        """Canvas dims match input dims -- no resolution needed."""
        from fdl import DimensionsFloat

        ctx = resolve_doc["ctx"]
        canvas1 = resolve_doc["canvas1"]
        fd1 = resolve_doc["fd1"]

        result = ctx.resolve_canvas_for_dimensions(
            input_dims=DimensionsFloat(width=1920.0, height=1080.0),
            canvas=canvas1,
            framing=fd1,
        )
        assert result.was_resolved is False
        assert result.canvas.id == "cvs1"

    def test_resolution_via_sibling(self, resolve_doc):
        """Derived canvas dims differ from input -- resolves to sibling source canvas."""
        from fdl import DimensionsFloat

        ctx = resolve_doc["ctx"]
        canvas2 = resolve_doc["canvas2"]
        fd2 = resolve_doc["fd2"]

        # canvas2 is 3840x2160 but input is 1920x1080.
        # canvas2 is derived (source_canvas_id="cvs1" != id="cvs2"), so sibling
        # search kicks in and finds canvas1 (1920x1080).
        result = ctx.resolve_canvas_for_dimensions(
            input_dims=DimensionsFloat(width=1920.0, height=1080.0),
            canvas=canvas2,
            framing=fd2,
        )
        assert result.was_resolved is True
        assert result.canvas.id == "cvs1"
        assert result.framing_decision.id == "fd1"

    def test_no_match(self, resolve_doc):
        """No sibling matches the input dims -- raises ValueError."""
        from fdl import DimensionsFloat

        ctx = resolve_doc["ctx"]
        canvas2 = resolve_doc["canvas2"]
        fd2 = resolve_doc["fd2"]

        # canvas2 is derived, so sibling search runs, but no canvas has 9999x9999.
        with pytest.raises(ValueError):
            ctx.resolve_canvas_for_dimensions(
                input_dims=DimensionsFloat(width=9999.0, height=9999.0),
                canvas=canvas2,
                framing=fd2,
            )
