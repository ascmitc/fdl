# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Tests for the custom attributes API on all handle types."""

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

    d = FDL.parse(json.dumps(_MINIMAL_FDL).encode())
    yield d
    d.close()


# ---------------------------------------------------------------------------
# FDL document-level custom attrs
# ---------------------------------------------------------------------------


class TestDocCustomAttrs:
    def test_initially_empty(self, doc):
        assert doc.custom_attrs_count() == 0
        assert doc.custom_attrs == {}
        assert not doc.has_custom_attr("note")

    def test_set_get_string(self, doc):
        doc.set_custom_attr("note", "hello")
        assert doc.has_custom_attr("note")
        assert doc.get_custom_attr("note") == "hello"

    def test_set_get_int(self, doc):
        doc.set_custom_attr("count", 42)
        assert doc.get_custom_attr("count") == 42

    def test_set_get_float(self, doc):
        doc.set_custom_attr("ratio", 1.5)
        assert doc.get_custom_attr("ratio") == 1.5

    def test_update_same_type(self, doc):
        doc.set_custom_attr("note", "first")
        doc.set_custom_attr("note", "second")
        assert doc.get_custom_attr("note") == "second"

    def test_type_mismatch_raises(self, doc):
        doc.set_custom_attr("x", 10)
        with pytest.raises(ValueError, match="type mismatch"):
            doc.set_custom_attr("x", "nope")
        # Original value preserved
        assert doc.get_custom_attr("x") == 10

    def test_set_get_bool(self, doc):
        doc.set_custom_attr("active", True)
        assert doc.get_custom_attr("active") is True
        doc.set_custom_attr("disabled", False)
        assert doc.get_custom_attr("disabled") is False

    def test_bool_type_mismatch(self, doc):
        doc.set_custom_attr("flag", True)
        with pytest.raises(ValueError, match="type mismatch"):
            doc.set_custom_attr("flag", 42)
        with pytest.raises(ValueError, match="type mismatch"):
            doc.set_custom_attr("flag", "yes")
        # Original preserved
        assert doc.get_custom_attr("flag") is True

    def test_bad_type_raises(self, doc):
        with pytest.raises(TypeError):
            doc.set_custom_attr("items", [1, 2, 3])

    def test_remove(self, doc):
        doc.set_custom_attr("tmp", "gone")
        assert doc.custom_attrs_count() == 1
        assert doc.remove_custom_attr("tmp") is True
        assert doc.custom_attrs_count() == 0
        assert not doc.has_custom_attr("tmp")
        # Removing non-existent returns False
        assert doc.remove_custom_attr("tmp") is False

    def test_get_missing_returns_none(self, doc):
        assert doc.get_custom_attr("nope") is None

    def test_custom_attrs_property(self, doc):
        doc.set_custom_attr("alpha", "a")
        doc.set_custom_attr("beta", 2)
        doc.set_custom_attr("gamma", 3.14)
        doc.set_custom_attr("delta", True)
        attrs = doc.custom_attrs
        assert attrs["alpha"] == "a"
        assert attrs["beta"] == 2
        assert attrs["gamma"] == 3.14
        assert attrs["delta"] is True
        assert len(attrs) == 4


# ---------------------------------------------------------------------------
# Sub-handle custom attrs
# ---------------------------------------------------------------------------


class TestContextCustomAttrs:
    def test_set_get(self, doc):
        ctx = doc.contexts[0]
        ctx.set_custom_attr("shot", "A001")
        assert ctx.has_custom_attr("shot")
        assert ctx.get_custom_attr("shot") == "A001"
        assert ctx.custom_attrs_count() == 1


class TestCanvasCustomAttrs:
    def test_set_get(self, doc):
        cvs = doc.contexts[0].canvases[0]
        cvs.set_custom_attr("layer", 5)
        assert cvs.get_custom_attr("layer") == 5


class TestFramingDecisionCustomAttrs:
    def test_set_get(self, doc):
        fd = doc.contexts[0].canvases[0].framing_decisions[0]
        fd.set_custom_attr("weight", 0.75)
        assert fd.get_custom_attr("weight") == 0.75


class TestFramingIntentCustomAttrs:
    def test_set_get(self, doc):
        fi = doc.framing_intents[0]
        fi.set_custom_attr("origin", "camera")
        assert fi.get_custom_attr("origin") == "camera"


# ---------------------------------------------------------------------------
# ClipID and FileSequence custom attrs
# ---------------------------------------------------------------------------


class TestClipIDCustomAttrs:
    def test_set_get(self, doc):
        ctx = doc.contexts[0]
        ctx.clip_id = {"clip_name": "A001", "file": "A001C001.ari"}
        clip = ctx.clip_id
        assert clip is not None
        clip.set_custom_attr("reel", "A001")
        assert clip.has_custom_attr("reel")
        assert clip.get_custom_attr("reel") == "A001"
        assert clip.custom_attrs == {"reel": "A001"}


class TestFileSequenceCustomAttrs:
    def test_set_get(self, doc):
        ctx = doc.contexts[0]
        ctx.clip_id = {
            "clip_name": "B001",
            "sequence": {"value": "B001.####.exr", "idx": "#", "min": 0, "max": 100},
        }
        clip = ctx.clip_id
        seq = clip.sequence
        assert seq is not None
        seq.set_custom_attr("fps", 24)
        assert seq.get_custom_attr("fps") == 24
        assert seq.custom_attrs_count() == 1


# ---------------------------------------------------------------------------
# Roundtrip tests
# ---------------------------------------------------------------------------


class TestRoundtrip:
    def test_custom_attrs_survive_roundtrip(self, doc):
        """Add custom attrs on every object type, roundtrip, verify."""
        doc.set_custom_attr("tool", "test-suite")
        doc.set_custom_attr("version_num", 1)
        doc.set_custom_attr("scale", 2.5)
        doc.set_custom_attr("approved", True)

        ctx = doc.contexts[0]
        ctx.set_custom_attr("note", "ctx-note")

        cvs = ctx.canvases[0]
        cvs.set_custom_attr("order", 1)

        fd = cvs.framing_decisions[0]
        fd.set_custom_attr("confidence", 0.95)

        fi = doc.framing_intents[0]
        fi.set_custom_attr("source", "director")

        # Add clip_id with custom attrs
        ctx.clip_id = {"clip_name": "A001", "file": "A001.ari"}
        clip = ctx.clip_id
        clip.set_custom_attr("reel", "reel_A")

        # Serialize and re-parse
        json_bytes = doc.as_json().encode()
        from fdl import FDL

        doc2 = FDL.parse(json_bytes)

        assert doc2.get_custom_attr("tool") == "test-suite"
        assert doc2.get_custom_attr("version_num") == 1
        assert doc2.get_custom_attr("scale") == 2.5
        assert doc2.get_custom_attr("approved") is True

        ctx2 = doc2.contexts[0]
        assert ctx2.get_custom_attr("note") == "ctx-note"

        cvs2 = ctx2.canvases[0]
        assert cvs2.get_custom_attr("order") == 1

        fd2 = cvs2.framing_decisions[0]
        assert fd2.get_custom_attr("confidence") == 0.95

        fi2 = doc2.framing_intents[0]
        assert fi2.get_custom_attr("source") == "director"

        clip2 = ctx2.clip_id
        assert clip2 is not None
        assert clip2.get_custom_attr("reel") == "reel_A"

        doc2.close()

    def test_fixture_roundtrip(self):
        """Parse the fixture JSON, verify pre-existing custom attrs, roundtrip."""
        import pathlib

        fixture_path = pathlib.Path(__file__).resolve().parents[3] / "core" / "tests" / "vectors" / "document" / "custom_attrs_fixture.json"
        raw = fixture_path.read_bytes()
        from fdl import FDL

        doc = FDL.parse(raw)

        # Verify pre-existing attrs
        assert doc.get_custom_attr("vendor_note") == "This is a doc-level custom attr"
        assert doc.get_custom_attr("vendor_count") == 42

        fi = doc.framing_intents[0]
        assert fi.get_custom_attr("fi_tag") == "intent-custom"

        ctx = doc.contexts[0]
        assert ctx.get_custom_attr("ctx_priority") == 1

        cvs = ctx.canvases[0]
        assert cvs.get_custom_attr("canvas_vendor") == "test-tool"

        fd = cvs.framing_decisions[0]
        assert fd.get_custom_attr("fd_note") == "hero framing"

        clip = ctx.clip_id
        assert clip is not None
        assert clip.get_custom_attr("cid_reel") == "reel_A"

        # Roundtrip
        json_bytes = doc.as_json().encode()
        doc2 = FDL.parse(json_bytes)

        assert doc2.get_custom_attr("vendor_note") == "This is a doc-level custom attr"
        assert doc2.get_custom_attr("vendor_count") == 42

        clip2 = doc2.contexts[0].clip_id
        assert clip2 is not None
        assert clip2.get_custom_attr("cid_reel") == "reel_A"

        doc2.close()
        doc.close()
