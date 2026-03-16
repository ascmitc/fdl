# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Tests for Pydantic DTO models and to_model/from_model bridge methods."""

from __future__ import annotations

import copy
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
            "protection": 0.088,
        }
    ],
    "contexts": [
        {
            "label": "Source",
            "context_creator": "DIT",
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


# ---------------------------------------------------------------------------
# Model validation from dict
# ---------------------------------------------------------------------------


class TestModelValidation:
    """Test Pydantic model validation with and without C-core semantics."""

    def test_valid_dict(self):
        from fdl.models import FramingDecisionList

        model = FramingDecisionList.model_validate(_MINIMAL_FDL)
        assert str(model.uuid) == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        assert model.version.major == 2
        assert model.version.minor == 0
        assert model.fdl_creator == "test"
        assert len(model.framing_intents) == 1
        assert len(model.contexts) == 1

    def test_bad_type_rejected_by_pydantic(self):
        from fdl.models import FramingDecisionList
        from pydantic import ValidationError

        bad = copy.deepcopy(_MINIMAL_FDL)
        bad["uuid"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            FramingDecisionList.model_validate(bad)

    def test_semantic_validation_bad_reference(self):
        """C-core rejects framing_intent_id that doesn't exist."""
        from fdl.models import FramingDecisionList

        bad = copy.deepcopy(_MINIMAL_FDL)
        bad["contexts"][0]["canvases"][0]["framing_decisions"][0]["framing_intent_id"] = "NONEXISTENT"
        with pytest.raises(Exception):
            FramingDecisionList.model_validate(bad)

    def test_json_roundtrip(self):
        from fdl.models import FramingDecisionList

        model = FramingDecisionList.model_validate(_MINIMAL_FDL)
        json_str = model.model_dump_json()
        model2 = FramingDecisionList.model_validate_json(json_str)
        assert model2.uuid == model.uuid
        assert model2.fdl_creator == model.fdl_creator


# ---------------------------------------------------------------------------
# FDL to_model / from_model round-trip
# ---------------------------------------------------------------------------


class TestFDLBridge:
    """Test to_model/from_model on the root FDL class."""

    def test_to_model(self, doc):
        model = doc.to_model()
        assert str(model.uuid) == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        assert model.fdl_creator == "test"
        assert len(model.framing_intents) == 1
        assert model.framing_intents[0].id.root == "FI_01"
        assert model.framing_intents[0].aspect_ratio.width == 16

    def test_from_model(self, doc):
        from fdl import FDL

        model = doc.to_model()
        doc2 = FDL.from_model(model)
        assert doc2.uuid == doc.uuid
        assert doc2.fdl_creator == doc.fdl_creator
        assert len(list(doc2.framing_intents)) == 1
        doc2.close()

    def test_roundtrip_preserves_data(self, doc):
        from fdl import FDL

        original_dict = doc.as_dict()
        model = doc.to_model()
        doc2 = FDL.from_model(model)
        roundtripped_dict = doc2.as_dict()

        # Compare key fields
        assert roundtripped_dict["uuid"] == original_dict["uuid"]
        assert roundtripped_dict["fdl_creator"] == original_dict["fdl_creator"]
        assert roundtripped_dict["version"] == original_dict["version"]
        assert len(roundtripped_dict["framing_intents"]) == len(original_dict["framing_intents"])
        assert len(roundtripped_dict["contexts"]) == len(original_dict["contexts"])

        fi_orig = original_dict["framing_intents"][0]
        fi_rt = roundtripped_dict["framing_intents"][0]
        assert fi_rt["id"] == fi_orig["id"]
        assert fi_rt["aspect_ratio"] == fi_orig["aspect_ratio"]
        assert fi_rt["protection"] == pytest.approx(fi_orig["protection"])
        doc2.close()

    def test_model_mutation_reflected(self, doc):
        """Mutate a Pydantic model field, then from_model reflects the change."""
        from fdl import FDL

        model = doc.to_model()
        model.fdl_creator = "Modified Creator"
        doc2 = FDL.from_model(model)
        assert doc2.fdl_creator == "Modified Creator"
        doc2.close()


# ---------------------------------------------------------------------------
# Sub-object to_model
# ---------------------------------------------------------------------------


class TestSubObjectToModel:
    """Test to_model on sub-objects (Context, Canvas, FramingIntent, etc.)."""

    def test_context_to_model(self, doc):
        ctx = doc.contexts[0]
        model = ctx.to_model()
        assert model.label == "Source"
        assert model.context_creator == "DIT"

    def test_canvas_to_model(self, doc):
        canvas = doc.contexts[0].canvases[0]
        model = canvas.to_model()
        assert model.id.root == "CV_01"
        assert model.dimensions.width == 3840
        assert model.dimensions.height == 2160

    def test_framing_intent_to_model(self, doc):
        fi = doc.framing_intents[0]
        model = fi.to_model()
        assert model.id.root == "FI_01"
        assert model.aspect_ratio.width == 16
        assert model.aspect_ratio.height == 9

    def test_framing_decision_to_model(self, doc):
        fd = doc.contexts[0].canvases[0].framing_decisions[0]
        model = fd.to_model()
        assert model.id.root == "CV_01-FI_01"
        assert model.dimensions.width == pytest.approx(3840.0)
        assert model.anchor_point.x == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Sub-object from_model
# ---------------------------------------------------------------------------


class TestSubObjectFromModel:
    """Test from_model on sub-objects (standalone construction)."""

    def test_framing_intent_from_model(self, doc):
        from fdl import FramingIntent

        fi = doc.framing_intents[0]
        model = fi.to_model()
        fi2 = FramingIntent.from_model(model)
        assert fi2.id == fi.id
        assert fi2.aspect_ratio.width == 16
        assert fi2.protection == pytest.approx(0.088)

    def test_canvas_from_model(self, doc):
        from fdl import Canvas

        canvas = doc.contexts[0].canvases[0]
        model = canvas.to_model()
        canvas2 = Canvas.from_model(model)
        assert canvas2.id == canvas.id
        assert canvas2.dimensions.width == 3840
        assert canvas2.dimensions.height == 2160

    def test_context_from_model(self, doc):
        from fdl import Context

        ctx = doc.contexts[0]
        model = ctx.to_model()
        ctx2 = Context.from_model(model)
        assert ctx2.label == "Source"
        assert ctx2.context_creator == "DIT"


# ---------------------------------------------------------------------------
# Custom attributes preserved through models
# ---------------------------------------------------------------------------


class TestCustomAttributes:
    """Test that _-prefixed custom attributes survive the model round-trip."""

    def test_custom_attrs_roundtrip(self):
        from fdl import FDL

        fdl_with_custom = copy.deepcopy(_MINIMAL_FDL)
        fdl_with_custom["_vendor_note"] = "some custom data"
        fdl_with_custom["framing_intents"][0]["_custom_tag"] = 42

        json_bytes = json.dumps(fdl_with_custom).encode()
        doc = FDL.parse(json_bytes)
        model = doc.to_model()

        # The extra='allow' config preserves underscore-prefixed attrs
        d = model.model_dump()
        assert d.get("_vendor_note") == "some custom data"

        # Round-trip back
        doc2 = FDL.from_model(model)
        d2 = doc2.as_dict()
        assert d2.get("_vendor_note") == "some custom data"
        doc.close()
        doc2.close()


# ---------------------------------------------------------------------------
# Model exports
# ---------------------------------------------------------------------------


class TestModelExports:
    """Test that fdl.models exports all expected classes."""

    def test_all_models_importable(self):
        from fdl.models import (
            CanvasModel,
            CanvasTemplateModel,
            ClipIDModel,
            ContextModel,
            DimensionsFloatModel,
            DimensionsIntModel,
            FileSequenceModel,
            FramingDecisionList,
            FramingDecisionModel,
            FramingIntentModel,
            PointFloatModel,
            RoundModel,
            VersionModel,
        )

        assert FramingDecisionList is not None
        assert VersionModel is not None
        assert FramingIntentModel is not None
        assert ContextModel is not None
        assert CanvasModel is not None
        assert FramingDecisionModel is not None
        assert CanvasTemplateModel is not None
        assert ClipIDModel is not None
        assert FileSequenceModel is not None
        assert RoundModel is not None
        assert DimensionsIntModel is not None
        assert DimensionsFloatModel is not None
        assert PointFloatModel is not None
