# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Codegen round-trip tests.

Exercises generated facade classes, value types, and model bridge methods
to verify that code generation produces correct, functional output.
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


_SAMPLE = {
    "uuid": "11111111-2222-3333-4444-555555555555",
    "version": {"major": 2, "minor": 0},
    "fdl_creator": "codegen-test",
    "default_framing_intent": "FI_01",
    "framing_intents": [{"id": "FI_01", "aspect_ratio": {"width": 16, "height": 9}, "protection": 0.1}],
    "contexts": [
        {
            "label": "Src",
            "canvases": [
                {
                    "id": "C1",
                    "source_canvas_id": "C1",
                    "dimensions": {"width": 1920, "height": 1080},
                    "framing_decisions": [
                        {
                            "id": "C1-FI_01",
                            "framing_intent_id": "FI_01",
                            "dimensions": {"width": 1920.0, "height": 1080.0},
                            "anchor_point": {"x": 0.0, "y": 0.0},
                        }
                    ],
                }
            ],
        }
    ],
}


@pytest.fixture
def doc():
    from fdl import FDL

    d = FDL.parse(json.dumps(_SAMPLE).encode())
    yield d
    d.close()


class TestFacadeImports:
    """All facade classes importable."""

    def test_facade_classes(self):
        from fdl import (
            FDL,
            Canvas,
            CanvasTemplate,
            ClipID,
            Context,
            FileSequence,
            FramingDecision,
            FramingIntent,
        )

        for cls in (FDL, Canvas, CanvasTemplate, ClipID, Context, FileSequence, FramingDecision, FramingIntent):
            assert cls is not None

    def test_value_types(self):
        from fdl import DimensionsFloat, DimensionsInt, PointFloat, Rect

        for cls in (DimensionsInt, DimensionsFloat, PointFloat, Rect):
            assert cls is not None


class TestValueTypeOps:
    """Value type operations work on generated code."""

    def test_dimensions_int_zero(self):
        from fdl import DimensionsInt

        assert DimensionsInt(width=0, height=0).is_zero()
        assert not DimensionsInt(width=1, height=1).is_zero()

    def test_dimensions_int_compare(self):
        from fdl import DimensionsInt

        assert DimensionsInt(width=1920, height=1080) > DimensionsInt(width=1280, height=720)
        assert DimensionsInt(width=1280, height=720) < DimensionsInt(width=1920, height=1080)

    def test_dimensions_float_normalize(self):
        from fdl import DimensionsFloat

        d = DimensionsFloat(width=3840.0, height=2160.0)
        n = d.normalize(2.0)
        assert n.width == pytest.approx(7680.0)

    def test_point_ops(self):
        from fdl import PointFloat

        p = PointFloat(x=10.0, y=20.0)
        assert p.x == pytest.approx(10.0)
        assert p.y == pytest.approx(20.0)


class TestFacadeJsonRoundtrip:
    """Facade → JSON → facade round-trip preserves data."""

    def test_json_roundtrip(self, doc):
        from fdl import FDL

        json_str = doc.as_json()
        doc2 = FDL.parse(json_str.encode())
        assert doc2.uuid == doc.uuid
        assert doc2.fdl_creator == doc.fdl_creator
        assert len(list(doc2.framing_intents)) == 1
        assert len(list(doc2.contexts)) == 1
        doc2.close()


class TestFacadeModelRoundtrip:
    """Facade → model → facade round-trip preserves data."""

    def test_model_roundtrip(self, doc):
        from fdl import FDL

        model = doc.to_model()
        doc2 = FDL.from_model(model)
        assert doc2.uuid == doc.uuid
        assert doc2.fdl_creator == doc.fdl_creator
        fi = next(iter(doc2.framing_intents))
        assert fi.id == "FI_01"
        assert fi.aspect_ratio.width == 16
        doc2.close()

    def test_sub_object_model(self, doc):
        ctx = doc.contexts[0]
        m = ctx.to_model()
        assert m.label == "Src"

        canvas = ctx.canvases[0]
        cm = canvas.to_model()
        assert cm.dimensions.width == 1920

        fd = canvas.framing_decisions[0]
        fdm = fd.to_model()
        assert fdm.dimensions.width == pytest.approx(1920.0)

        fi = doc.framing_intents[0]
        fim = fi.to_model()
        assert fim.aspect_ratio.width == 16
