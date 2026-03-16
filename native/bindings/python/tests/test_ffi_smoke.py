# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
FFI smoke tests — verify CFFI correctly marshals data to/from libfdl_core.

Requires: FDL_CORE_LIB_PATH pointing to built libfdl_core.dylib
          (or the library in a discoverable location).
"""

from __future__ import annotations

import json

import pytest

try:
    from fdl_ffi import (
        FDL_FIT_METHOD_FIT_ALL,
        FDL_FIT_METHOD_WIDTH,
        FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS,
        FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS,
        FDL_HALIGN_CENTER,
        FDL_ROUNDING_EVEN_EVEN,
        FDL_ROUNDING_EVEN_WHOLE,
        FDL_ROUNDING_MODE_ROUND,
        FDL_ROUNDING_MODE_UP,
        FDL_VALIGN_CENTER,
        ffi,
        get_lib,
        is_available,
    )

    HAS_CORE = is_available()
except ImportError:
    HAS_CORE = False

pytestmark = pytest.mark.skipif(not HAS_CORE, reason="fdl_core library not available")


@pytest.fixture
def lib():
    return get_lib()


# -----------------------------------------------------------------------
# ABI version
# -----------------------------------------------------------------------


class TestABIVersion:
    def test_abi_version(self, lib):
        ver = lib.fdl_abi_version()
        assert ver.major == 0
        assert ver.minor >= 4

    def test_abi_version_fields(self, lib):
        ver = lib.fdl_abi_version()
        assert isinstance(ver.major, int)
        assert isinstance(ver.minor, int)
        assert isinstance(ver.patch, int)


# -----------------------------------------------------------------------
# Rounding
# -----------------------------------------------------------------------


class TestRounding:
    def test_round_half_even(self, lib):
        """Banker's rounding: 2.5 → 2, 3.5 → 4."""
        assert lib.fdl_round(2.5, FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND) == 2
        assert lib.fdl_round(3.5, FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND) == 4

    def test_round_up(self, lib):
        assert lib.fdl_round(2.1, FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_UP) == 3

    def test_round_even(self, lib):
        """Even rounding: round to nearest even integer."""
        assert lib.fdl_round(3.0, FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND) == 4
        assert lib.fdl_round(4.0, FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND) == 4

    def test_round_dimensions(self, lib):
        d = ffi.new("fdl_dimensions_f64_t*", {"width": 1920.5, "height": 1080.5})[0]
        r = lib.fdl_round_dimensions(d, FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND)
        assert r.width == 1920.0
        assert r.height == 1080.0

    def test_round_point(self, lib):
        p = ffi.new("fdl_point_f64_t*", {"x": 100.5, "y": 200.5})[0]
        r = lib.fdl_round_point(p, FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND)
        assert r.x == 100.0
        assert r.y == 200.0


# -----------------------------------------------------------------------
# Dimensions operations
# -----------------------------------------------------------------------


class TestDimensions:
    def test_normalize(self, lib):
        d = ffi.new("fdl_dimensions_f64_t*", {"width": 1920.0, "height": 1080.0})[0]
        n = lib.fdl_dimensions_normalize(d, 2.0)
        assert n.width == pytest.approx(3840.0)
        assert n.height == pytest.approx(1080.0)

    def test_scale(self, lib):
        d = ffi.new("fdl_dimensions_f64_t*", {"width": 3840.0, "height": 1080.0})[0]
        s = lib.fdl_dimensions_scale(d, 0.5, 1.0)
        assert s.width == pytest.approx(1920.0)
        assert s.height == pytest.approx(540.0)

    def test_sub(self, lib):
        a = ffi.new("fdl_dimensions_f64_t*", {"width": 1920.0, "height": 1080.0})[0]
        b = ffi.new("fdl_dimensions_f64_t*", {"width": 100.0, "height": 50.0})[0]
        r = lib.fdl_dimensions_sub(a, b)
        assert r.width == pytest.approx(1820.0)
        assert r.height == pytest.approx(1030.0)

    def test_equal(self, lib):
        a = ffi.new("fdl_dimensions_f64_t*", {"width": 1920.0, "height": 1080.0})[0]
        b = ffi.new("fdl_dimensions_f64_t*", {"width": 1920.0, "height": 1080.0})[0]
        assert lib.fdl_dimensions_equal(a, b) == 1

    def test_is_zero(self, lib):
        z = ffi.new("fdl_dimensions_f64_t*", {"width": 0.0, "height": 0.0})[0]
        assert lib.fdl_dimensions_is_zero(z) == 1


# -----------------------------------------------------------------------
# Point operations
# -----------------------------------------------------------------------


class TestPoint:
    def test_add(self, lib):
        a = ffi.new("fdl_point_f64_t*", {"x": 10.0, "y": 20.0})[0]
        b = ffi.new("fdl_point_f64_t*", {"x": 5.0, "y": 3.0})[0]
        r = lib.fdl_point_add(a, b)
        assert r.x == pytest.approx(15.0)
        assert r.y == pytest.approx(23.0)

    def test_sub(self, lib):
        a = ffi.new("fdl_point_f64_t*", {"x": 10.0, "y": 20.0})[0]
        b = ffi.new("fdl_point_f64_t*", {"x": 5.0, "y": 3.0})[0]
        r = lib.fdl_point_sub(a, b)
        assert r.x == pytest.approx(5.0)
        assert r.y == pytest.approx(17.0)

    def test_mul_scalar(self, lib):
        a = ffi.new("fdl_point_f64_t*", {"x": 10.0, "y": 20.0})[0]
        r = lib.fdl_point_mul_scalar(a, 2.0)
        assert r.x == pytest.approx(20.0)
        assert r.y == pytest.approx(40.0)

    def test_equal(self, lib):
        a = ffi.new("fdl_point_f64_t*", {"x": 100.0, "y": 200.0})[0]
        b = ffi.new("fdl_point_f64_t*", {"x": 100.0, "y": 200.0})[0]
        assert lib.fdl_point_equal(a, b) == 1


# -----------------------------------------------------------------------
# FP constants
# -----------------------------------------------------------------------


class TestFPConstants:
    def test_rel_tol(self, lib):
        assert lib.fdl_fp_rel_tol() == pytest.approx(1e-9)

    def test_abs_tol(self, lib):
        assert lib.fdl_fp_abs_tol() == pytest.approx(1e-6)


# -----------------------------------------------------------------------
# Pipeline helpers
# -----------------------------------------------------------------------


class TestPipeline:
    def test_calculate_scale_factor_fit_all(self, lib):
        src = ffi.new("fdl_dimensions_f64_t*", {"width": 3840.0, "height": 2160.0})[0]
        tgt = ffi.new("fdl_dimensions_f64_t*", {"width": 1920.0, "height": 1080.0})[0]
        sf = lib.fdl_calculate_scale_factor(src, tgt, FDL_FIT_METHOD_FIT_ALL)
        assert sf == pytest.approx(0.5)

    def test_output_size_for_axis_no_max(self, lib):
        result = lib.fdl_output_size_for_axis(1920.0, 0.0, 0, 0)
        assert result == pytest.approx(1920.0)


# -----------------------------------------------------------------------
# Document lifecycle
# -----------------------------------------------------------------------

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


class TestDocumentLifecycle:
    def test_parse_valid(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))
        assert result.doc != ffi.NULL
        assert not result.error
        lib.fdl_doc_free(result.doc)

    def test_parse_malformed_json(self, lib):
        """Malformed JSON returns an error without crashing."""
        for bad_input in [b'{"string" : }', b"not json at all", b"", b"[", b'{"key": "val"']:
            result = lib.fdl_doc_parse_json(bad_input, len(bad_input))
            assert not result.doc, f"Expected NULL doc for input: {bad_input}"
            assert result.error, f"Expected error for input: {bad_input}"
            lib.fdl_free(result.error)

    def test_parse_empty_object(self, lib):
        """An empty JSON object parses but produces a doc with no collections."""
        json_bytes = b"{}"
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))
        assert result.doc != ffi.NULL
        # Should validate with errors (missing required fields)
        vr = lib.fdl_doc_validate(result.doc)
        assert lib.fdl_validation_result_error_count(vr) > 0
        lib.fdl_validation_result_free(vr)
        lib.fdl_doc_free(result.doc)

    def test_roundtrip(self, lib):
        """Parse → serialize → parse roundtrip."""
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))

        json_ptr = lib.fdl_doc_to_json(result.doc, 2)
        json_str = ffi.string(json_ptr).decode()
        lib.fdl_free(json_ptr)

        roundtripped = json.loads(json_str)
        assert roundtripped["uuid"] == _MINIMAL_FDL["uuid"]
        assert roundtripped["version"] == _MINIMAL_FDL["version"]
        assert len(roundtripped["contexts"]) == 1

        lib.fdl_doc_free(result.doc)

    def test_get_uuid(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))
        uuid = lib.fdl_doc_get_uuid(result.doc)
        assert ffi.string(uuid) == b"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        lib.fdl_doc_free(result.doc)

    def test_get_fdl_creator(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))
        creator = lib.fdl_doc_get_fdl_creator(result.doc)
        assert ffi.string(creator) == b"test"
        lib.fdl_doc_free(result.doc)


# -----------------------------------------------------------------------
# Collection traversal
# -----------------------------------------------------------------------


class TestCollectionTraversal:
    def test_contexts(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))

        assert lib.fdl_doc_contexts_count(result.doc) == 1
        ctx = lib.fdl_doc_context_at(result.doc, 0)
        assert ctx != ffi.NULL

        label = lib.fdl_context_get_label(ctx)
        assert ffi.string(label) == b"Source"

        assert lib.fdl_context_canvases_count(ctx) == 1
        canvas = lib.fdl_context_canvas_at(ctx, 0)
        canvas_id = lib.fdl_canvas_get_id(canvas)
        assert ffi.string(canvas_id) == b"CV_01"

        dims = lib.fdl_canvas_get_dimensions(canvas)
        assert dims.width == 3840
        assert dims.height == 2160

        assert lib.fdl_canvas_framing_decisions_count(canvas) == 1
        fd = lib.fdl_canvas_framing_decision_at(canvas, 0)
        fd_id = lib.fdl_framing_decision_get_id(fd)
        assert ffi.string(fd_id) == b"CV_01-FI_01"

        lib.fdl_doc_free(result.doc)

    def test_framing_intents(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))

        assert lib.fdl_doc_framing_intents_count(result.doc) == 1
        fi = lib.fdl_doc_framing_intent_at(result.doc, 0)
        assert ffi.string(lib.fdl_framing_intent_get_id(fi)) == b"FI_01"
        ar = lib.fdl_framing_intent_get_aspect_ratio(fi)
        assert ar.width == 16
        assert ar.height == 9

        lib.fdl_doc_free(result.doc)


# -----------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------


class TestValidation:
    def test_validate_valid_doc(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))
        vr = lib.fdl_doc_validate(result.doc)
        assert lib.fdl_validation_result_error_count(vr) == 0
        lib.fdl_validation_result_free(vr)
        lib.fdl_doc_free(result.doc)

    def test_validate_detects_errors(self, lib):
        """An FDL with duplicate canvas IDs should fail validation."""
        bad_fdl = {
            "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "version": {"major": 2, "minor": 0},
            "fdl_creator": "test",
            "framing_intents": [{"id": "FI_01", "label": "FI", "aspect_ratio": {"width": 16, "height": 9}, "protection": 0.0}],
            "contexts": [
                {
                    "label": "Ctx",
                    "canvases": [
                        {
                            "id": "CV_01",
                            "label": "C1",
                            "source_canvas_id": "CV_01",
                            "dimensions": {"width": 1920, "height": 1080},
                            "anamorphic_squeeze": 1.0,
                            "framing_decisions": [
                                {
                                    "id": "CV_01-FI_01",
                                    "label": "FD1",
                                    "framing_intent_id": "FI_01",
                                    "dimensions": {"width": 1920.0, "height": 1080.0},
                                    "anchor_point": {"x": 0.0, "y": 0.0},
                                }
                            ],
                        },
                        {
                            "id": "CV_01",
                            "label": "C2-duplicate",
                            "source_canvas_id": "CV_01",
                            "dimensions": {"width": 1920, "height": 1080},
                            "anamorphic_squeeze": 1.0,
                            "framing_decisions": [
                                {
                                    "id": "CV_01-FI_01",
                                    "label": "FD2",
                                    "framing_intent_id": "FI_01",
                                    "dimensions": {"width": 1920.0, "height": 1080.0},
                                    "anchor_point": {"x": 0.0, "y": 0.0},
                                }
                            ],
                        },
                    ],
                }
            ],
            "canvas_templates": [],
        }
        json_bytes = json.dumps(bad_fdl).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))
        vr = lib.fdl_doc_validate(result.doc)
        assert lib.fdl_validation_result_error_count(vr) > 0
        lib.fdl_validation_result_free(vr)
        lib.fdl_doc_free(result.doc)


# -----------------------------------------------------------------------
# New ABI 0.4.0 functions
# -----------------------------------------------------------------------


class TestVersionAccessors:
    def test_get_version_major(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))
        assert lib.fdl_doc_get_version_major(result.doc) == 2
        assert lib.fdl_doc_get_version_minor(result.doc) == 0
        lib.fdl_doc_free(result.doc)


class TestFindHelpers:
    def test_context_find_by_label(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))

        ctx = lib.fdl_doc_context_find_by_label(result.doc, b"Source")
        assert ctx != ffi.NULL
        assert ffi.string(lib.fdl_context_get_label(ctx)) == b"Source"

        # Not found
        ctx2 = lib.fdl_doc_context_find_by_label(result.doc, b"NONEXISTENT")
        assert ctx2 == ffi.NULL

        lib.fdl_doc_free(result.doc)

    def test_canvas_find_by_id(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))

        ctx = lib.fdl_doc_context_at(result.doc, 0)
        canvas = lib.fdl_context_find_canvas_by_id(ctx, b"CV_01")
        assert canvas != ffi.NULL
        assert ffi.string(lib.fdl_canvas_get_id(canvas)) == b"CV_01"

        # Not found
        canvas2 = lib.fdl_context_find_canvas_by_id(ctx, b"NONEXISTENT")
        assert canvas2 == ffi.NULL

        lib.fdl_doc_free(result.doc)

    def test_framing_decision_find_by_id(self, lib):
        json_bytes = json.dumps(_MINIMAL_FDL).encode()
        result = lib.fdl_doc_parse_json(json_bytes, len(json_bytes))

        ctx = lib.fdl_doc_context_at(result.doc, 0)
        canvas = lib.fdl_context_canvas_at(ctx, 0)
        fd = lib.fdl_canvas_find_framing_decision_by_id(canvas, b"CV_01-FI_01")
        assert fd != ffi.NULL
        assert ffi.string(lib.fdl_framing_decision_get_id(fd)) == b"CV_01-FI_01"

        # Not found
        fd2 = lib.fdl_canvas_find_framing_decision_by_id(canvas, b"NONEXISTENT")
        assert fd2 == ffi.NULL

        lib.fdl_doc_free(result.doc)


class TestCanvasTemplateBuilder:
    def test_add_canvas_template(self, lib):
        """Build a canvas template via FFI and verify with accessors."""
        doc = lib.fdl_doc_create_with_header(b"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, b"test", ffi.NULL)
        assert doc != ffi.NULL

        rounding = ffi.new("fdl_round_strategy_t*", {"even": FDL_ROUNDING_EVEN_EVEN, "mode": FDL_ROUNDING_MODE_UP})[0]
        ct = lib.fdl_doc_add_canvas_template(
            doc,
            b"CT_HD",
            b"HD",
            1920,
            1080,
            1.0,
            FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS,
            FDL_FIT_METHOD_WIDTH,
            FDL_HALIGN_CENTER,
            FDL_VALIGN_CENTER,
            rounding,
        )
        assert ct != ffi.NULL

        assert lib.fdl_doc_canvas_templates_count(doc) == 1
        assert ffi.string(lib.fdl_canvas_template_get_id(ct)) == b"CT_HD"
        assert ffi.string(lib.fdl_canvas_template_get_label(ct)) == b"HD"

        # Set optional fields
        lib.fdl_canvas_template_set_preserve_from_source_canvas(ct, FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS)
        lib.fdl_canvas_template_set_maximum_dimensions(ct, ffi.new("fdl_dimensions_i64_t*", {"width": 3840, "height": 2160})[0])
        lib.fdl_canvas_template_set_pad_to_maximum(ct, 1)

        assert lib.fdl_canvas_template_has_preserve_from_source_canvas(ct) == 1
        assert lib.fdl_canvas_template_has_maximum_dimensions(ct) == 1
        assert lib.fdl_canvas_template_get_pad_to_maximum(ct) == 1

        lib.fdl_doc_free(doc)
