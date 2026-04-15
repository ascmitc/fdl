# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Struct-by-value ABI tests for CFFI on ARM64.

CFFI ABI mode (ffi.dlopen) has a known issue marshaling structs by value on
ARM64/Apple Silicon.  Small structs whose fields pack into a single register
(e.g. two uint32_t in a 64-bit GPR) may have their fields swapped.

The fix: widen rounding enum typedefs from uint32_t → uint64_t so each field
in fdl_round_strategy_t gets its own register (same as fdl_dimensions_i64_t).

These tests exercise every struct type used through CFFI to:
  1. Verify the uint64_t widening fix works on the current platform.
  2. Serve as regression guards against future struct-by-value issues.
"""

from __future__ import annotations

import pytest

try:
    from fdl_ffi import (
        FDL_FIT_METHOD_WIDTH,
        FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS,
        FDL_HALIGN_CENTER,
        FDL_ROUNDING_EVEN_EVEN,
        FDL_ROUNDING_EVEN_WHOLE,
        FDL_ROUNDING_MODE_DOWN,
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


# -- Helpers ------------------------------------------------------------------

_UUID = b"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _make_doc(lib):
    """Create a minimal FDL document."""
    doc = lib.fdl_doc_create_with_header(_UUID, 2, 0, b"test", ffi.NULL)
    assert doc != ffi.NULL
    return doc


def _make_canvas(lib, doc, dim_w=3840, dim_h=2160):
    """Create a context + canvas inside *doc*."""
    ctx = lib.fdl_doc_add_context(doc, b"CTX", ffi.NULL)
    canvas = lib.fdl_context_add_canvas(ctx, b"C1", b"Canvas", b"", dim_w, dim_h, 1.0)
    return canvas


def _add_canvas_template(lib, doc, even=FDL_ROUNDING_EVEN_WHOLE, mode=FDL_ROUNDING_MODE_UP):
    """Add a canvas template with specified rounding and return the handle."""
    rounding = ffi.new("fdl_round_strategy_t*", {"even": even, "mode": mode})[0]
    ct = lib.fdl_doc_add_canvas_template(
        doc,
        b"CT1",
        b"Test Template",
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
    return ct


# =============================================================================
# Struct RETURN value tests
# =============================================================================


class TestStructReturnValues:
    """Verify CFFI correctly returns struct-by-value on this platform."""

    def test_round_strategy_fields_not_swapped(self, lib):
        """fdl_round_strategy_t — verify uint64_t widening fixes the ARM64 bug.

        Previously (with uint32_t fields), CFFI packed both fields into a
        single ARM64 register and swapped them.  With uint64_t fields, each
        gets its own register.
        """
        doc = _make_doc(lib)
        ct = _add_canvas_template(lib, doc, even=FDL_ROUNDING_EVEN_EVEN, mode=FDL_ROUNDING_MODE_DOWN)

        raw = lib.fdl_canvas_template_get_round(ct)
        assert raw.even == FDL_ROUNDING_EVEN_EVEN, f"even: expected {FDL_ROUNDING_EVEN_EVEN}, got {raw.even}"
        assert raw.mode == FDL_ROUNDING_MODE_DOWN, f"mode: expected {FDL_ROUNDING_MODE_DOWN}, got {raw.mode}"

        lib.fdl_doc_free(doc)

    def test_round_strategy_struct_getter_round_trip(self, lib):
        """Struct-by-value getter returns correct fields after struct-by-value set."""
        doc = _make_doc(lib)
        ct = _add_canvas_template(lib, doc, even=FDL_ROUNDING_EVEN_WHOLE, mode=FDL_ROUNDING_MODE_DOWN)

        raw = lib.fdl_canvas_template_get_round(ct)
        assert raw.even == FDL_ROUNDING_EVEN_WHOLE, f"even: expected WHOLE(0), got {raw.even}"
        assert raw.mode == FDL_ROUNDING_MODE_DOWN, f"mode: expected DOWN(1), got {raw.mode}"

        lib.fdl_doc_free(doc)

    def test_abi_version_field_order(self, lib):
        """fdl_abi_version_t (3 x uint32_t) — potentially affected.

        ABI version is 0.N.x (major=0, minor>=4).  If fields are rotated,
        we'd see major=4+, minor=0 or similar.
        """
        ver = lib.fdl_abi_version()
        assert ver.major == 0, f"ABI major={ver.major} (expected 0) — fields may be swapped"
        assert ver.minor >= 4, f"ABI minor={ver.minor} (expected >= 4)"
        assert ver.patch >= 0, f"ABI patch={ver.patch} should be non-negative"

    def test_dimensions_i64_return(self, lib):
        """fdl_dimensions_i64_t (2 x int64_t) — expected unaffected (own registers)."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc, dim_w=3840, dim_h=2160)

        dims = lib.fdl_canvas_get_dimensions(canvas)
        assert dims.width == 3840, f"width: expected 3840, got {dims.width}"
        assert dims.height == 2160, f"height: expected 2160, got {dims.height}"

        lib.fdl_doc_free(doc)

    def test_dimensions_i64_asymmetric(self, lib):
        """Use clearly asymmetric values to detect any field swap."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc, dim_w=7680, dim_h=1080)

        dims = lib.fdl_canvas_get_dimensions(canvas)
        assert dims.width == 7680
        assert dims.height == 1080

        lib.fdl_doc_free(doc)

    def test_dimensions_f64_return(self, lib):
        """fdl_dimensions_f64_t (2 x double) — expected unaffected (HFA)."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc)

        phys = ffi.new("fdl_dimensions_f64_t*", {"width": 36.0, "height": 24.0})[0]
        lib.fdl_canvas_set_physical_dimensions(canvas, phys)

        result = lib.fdl_canvas_get_physical_dimensions(canvas)
        assert result.width == pytest.approx(36.0), f"width: expected 36.0, got {result.width}"
        assert result.height == pytest.approx(24.0), f"height: expected 24.0, got {result.height}"

        lib.fdl_doc_free(doc)

    def test_point_f64_return(self, lib):
        """fdl_point_f64_t (2 x double) — expected unaffected (HFA)."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc)

        dims = ffi.new("fdl_dimensions_i64_t*", {"width": 3840, "height": 2160})[0]
        anchor = ffi.new("fdl_point_f64_t*", {"x": 100.5, "y": 200.75})[0]
        lib.fdl_canvas_set_effective_dimensions(canvas, dims, anchor)

        result = lib.fdl_canvas_get_effective_anchor_point(canvas)
        assert result.x == pytest.approx(100.5), f"x: expected 100.5, got {result.x}"
        assert result.y == pytest.approx(200.75), f"y: expected 200.75, got {result.y}"

        lib.fdl_doc_free(doc)

    def test_rect_return(self, lib):
        """fdl_rect_t (4 x double) — expected unaffected (HFA)."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc, dim_w=1920, dim_h=1080)

        rect = lib.fdl_canvas_get_rect(canvas)
        assert rect.x == pytest.approx(0.0)
        assert rect.y == pytest.approx(0.0)
        assert rect.width == pytest.approx(1920.0)
        assert rect.height == pytest.approx(1080.0)

        lib.fdl_doc_free(doc)


# =============================================================================
# Struct PARAMETER passing tests
# =============================================================================


class TestStructPassByValue:
    """Verify CFFI correctly passes struct-by-value parameters."""

    def test_set_and_get_dimensions_i64(self, lib):
        """Round-trip fdl_dimensions_i64_t through setter and getter."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc)

        new_dims = ffi.new("fdl_dimensions_i64_t*", {"width": 4096, "height": 2048})[0]
        lib.fdl_canvas_set_dimensions(canvas, new_dims)

        result = lib.fdl_canvas_get_dimensions(canvas)
        assert result.width == 4096
        assert result.height == 2048

        lib.fdl_doc_free(doc)

    def test_set_and_get_dimensions_f64(self, lib):
        """Round-trip fdl_dimensions_f64_t through setter and getter."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc)

        phys = ffi.new("fdl_dimensions_f64_t*", {"width": 48.0, "height": 36.0})[0]
        lib.fdl_canvas_set_physical_dimensions(canvas, phys)

        result = lib.fdl_canvas_get_physical_dimensions(canvas)
        assert result.width == pytest.approx(48.0)
        assert result.height == pytest.approx(36.0)

        lib.fdl_doc_free(doc)

    def test_set_and_get_point_f64(self, lib):
        """Round-trip fdl_point_f64_t through setter and getter."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc)
        lib.fdl_doc_add_framing_intent(doc, b"FI1", b"Intent", 16, 9, 0.0)
        fd = lib.fdl_canvas_add_framing_decision(canvas, b"FD1", b"Decision", b"FI1", 1920.0, 1080.0, 0.0, 0.0)

        anchor = ffi.new("fdl_point_f64_t*", {"x": 123.456, "y": 789.012})[0]
        lib.fdl_framing_decision_set_anchor_point(fd, anchor)

        result = lib.fdl_framing_decision_get_anchor_point(fd)
        assert result.x == pytest.approx(123.456)
        assert result.y == pytest.approx(789.012)

        lib.fdl_doc_free(doc)

    def test_two_struct_params(self, lib):
        """Pass two different struct types in a single call."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc)

        dims = ffi.new("fdl_dimensions_i64_t*", {"width": 3000, "height": 1800})[0]
        anchor = ffi.new("fdl_point_f64_t*", {"x": 50.0, "y": 75.0})[0]
        lib.fdl_canvas_set_effective_dimensions(canvas, dims, anchor)

        result_dims = lib.fdl_canvas_get_effective_dimensions(canvas)
        result_anchor = lib.fdl_canvas_get_effective_anchor_point(canvas)

        assert result_dims.width == 3000
        assert result_dims.height == 1800
        assert result_anchor.x == pytest.approx(50.0)
        assert result_anchor.y == pytest.approx(75.0)

        lib.fdl_doc_free(doc)

    def test_add_canvas_template_round_strategy(self, lib):
        """The original bug: fdl_round_strategy_t passed to builder.

        With uint64_t widening, the struct param should round-trip correctly.
        """
        doc = _make_doc(lib)
        ct = _add_canvas_template(lib, doc, even=FDL_ROUNDING_EVEN_EVEN, mode=FDL_ROUNDING_MODE_ROUND)

        raw = lib.fdl_canvas_template_get_round(ct)
        assert raw.even == FDL_ROUNDING_EVEN_EVEN, f"even: expected EVEN, got {raw.even}"
        assert raw.mode == FDL_ROUNDING_MODE_ROUND, f"mode: expected ROUND, got {raw.mode}"

        lib.fdl_doc_free(doc)

    def test_round_strategy_all_combos(self, lib):
        """Every even x mode combination passes correctly as struct param."""
        all_even = [FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_EVEN_EVEN]
        all_mode = [FDL_ROUNDING_MODE_UP, FDL_ROUNDING_MODE_DOWN, FDL_ROUNDING_MODE_ROUND]

        for even in all_even:
            for mode in all_mode:
                doc = _make_doc(lib)
                ct = _add_canvas_template(lib, doc, even=even, mode=mode)
                raw = lib.fdl_canvas_template_get_round(ct)
                assert raw.even == even, f"even={even}: got {raw.even}"
                assert raw.mode == mode, f"mode={mode}: got {raw.mode}"
                lib.fdl_doc_free(doc)

    def test_compute_framing_from_intent_rounding(self, lib):
        """fdl_compute_framing_from_intent passes fdl_round_strategy_t correctly."""
        canvas_dims = ffi.new("fdl_dimensions_f64_t*", {"width": 3840.0, "height": 2160.0})[0]
        working_dims = ffi.new("fdl_dimensions_f64_t*", {"width": 3840.0, "height": 2160.0})[0]
        aspect_ratio = ffi.new("fdl_dimensions_i64_t*", {"width": 16, "height": 9})[0]
        rounding = ffi.new("fdl_round_strategy_t*", {"even": FDL_ROUNDING_EVEN_EVEN, "mode": FDL_ROUNDING_MODE_UP})[0]

        result = lib.fdl_compute_framing_from_intent(
            canvas_dims,
            working_dims,
            1.0,
            aspect_ratio,
            0.0,
            rounding,
        )
        # With even=EVEN + mode=UP, dimensions should be even integers
        assert result.dimensions.width == pytest.approx(3840.0)
        assert result.dimensions.height == pytest.approx(2160.0)

    def test_populate_from_intent_rounding(self, lib):
        """fdl_framing_decision_populate_from_intent passes rounding correctly."""
        doc = _make_doc(lib)
        canvas = _make_canvas(lib, doc, dim_w=3840, dim_h=2160)
        fi = lib.fdl_doc_add_framing_intent(doc, b"FI1", b"Intent", 16, 9, 0.0)
        fd = lib.fdl_canvas_add_framing_decision(canvas, b"FD1", b"Decision", b"FI1", 1920.0, 1080.0, 0.0, 0.0)

        rounding = ffi.new("fdl_round_strategy_t*", {"even": FDL_ROUNDING_EVEN_EVEN, "mode": FDL_ROUNDING_MODE_DOWN})[0]
        lib.fdl_framing_decision_populate_from_intent(fd, canvas, fi, rounding)

        # After populate, framing dimensions should be set (even integers due to EVEN rounding)
        dims = lib.fdl_framing_decision_get_dimensions(fd)
        assert dims.width > 0
        assert dims.height > 0
        # With EVEN rounding, both should be even numbers
        assert int(dims.width) % 2 == 0, f"width {dims.width} not even"
        assert int(dims.height) % 2 == 0, f"height {dims.height} not even"

        lib.fdl_doc_free(doc)


# =============================================================================
# Python facade-level round-trip tests
# =============================================================================


class TestFacadeRoundTrip:
    """Verify the Python facade correctly handles struct types end-to-end."""

    def test_canvas_template_rounding_facade(self):
        """Full facade round-trip for RoundStrategy (the original bug)."""
        from fdl.constants import FitMethod, GeometryPath, HAlign, RoundingEven, RoundingMode, VAlign
        from fdl.rounding import RoundStrategy

        from fdl import FDL, DimensionsInt

        doc = FDL(uuid="test-uuid")
        ct = doc.add_canvas_template(
            id="CT1",
            label="Test",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            target_anamorphic_squeeze=1.0,
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            alignment_method_horizontal=HAlign.CENTER,
            alignment_method_vertical=VAlign.CENTER,
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.DOWN),
        )

        result = ct.round
        assert result.even == RoundingEven.EVEN, f"even: expected EVEN, got {result.even}"
        assert result.mode == RoundingMode.DOWN, f"mode: expected DOWN, got {result.mode}"

    def test_canvas_template_rounding_all_combos(self):
        """Test every combination of RoundingEven x RoundingMode."""
        from fdl.constants import FitMethod, GeometryPath, HAlign, RoundingEven, RoundingMode, VAlign
        from fdl.rounding import RoundStrategy

        from fdl import FDL, DimensionsInt

        for even in RoundingEven:
            for mode in RoundingMode:
                if mode == RoundingMode.NONE:
                    continue
                doc = FDL(uuid="test-uuid")
                ct = doc.add_canvas_template(
                    id=f"CT_{even}_{mode}",
                    label="Test",
                    target_dimensions=DimensionsInt(width=1920, height=1080),
                    target_anamorphic_squeeze=1.0,
                    fit_source=GeometryPath.FRAMING_DIMENSIONS,
                    fit_method=FitMethod.WIDTH,
                    alignment_method_horizontal=HAlign.CENTER,
                    alignment_method_vertical=VAlign.CENTER,
                    round=RoundStrategy(even=even, mode=mode),
                )

                result = ct.round
                assert result.even == even, f"even={even}: got {result.even}"
                assert result.mode == mode, f"mode={mode}: got {result.mode}"

        # NONE mode: round field is omitted from JSON, read-back returns NONE sentinel
        doc = FDL(uuid="test-uuid-none")
        ct = doc.add_canvas_template(
            id="CT_none",
            label="Test",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            target_anamorphic_squeeze=1.0,
            fit_source=GeometryPath.FRAMING_DIMENSIONS,
            fit_method=FitMethod.WIDTH,
            alignment_method_horizontal=HAlign.CENTER,
            alignment_method_vertical=VAlign.CENTER,
            round=RoundStrategy(even=RoundingEven.WHOLE, mode=RoundingMode.NONE),
        )
        result = ct.round
        assert result.mode == RoundingMode.NONE, f"NONE mode: got {result.mode}"

    def test_dimensions_i64_facade(self):
        """Facade round-trip for DimensionsInt."""
        from fdl import FDL, DimensionsInt

        doc = FDL(uuid="test-uuid")
        ctx = doc.add_context(label="CTX")
        canvas = ctx.add_canvas(
            id="C1",
            label="Canvas",
            source_canvas_id="",
            dimensions=DimensionsInt(width=7680, height=4320),
            anamorphic_squeeze=1.0,
        )

        assert canvas.dimensions == DimensionsInt(width=7680, height=4320)

    def test_dimensions_f64_facade(self):
        """Facade round-trip for DimensionsFloat (physical dimensions)."""
        from fdl import FDL, DimensionsFloat, DimensionsInt

        doc = FDL(uuid="test-uuid")
        ctx = doc.add_context(label="CTX")
        canvas = ctx.add_canvas(
            id="C1",
            label="Canvas",
            source_canvas_id="",
            dimensions=DimensionsInt(width=3840, height=2160),
            anamorphic_squeeze=1.0,
        )

        canvas.physical_dimensions = DimensionsFloat(width=48.0, height=36.0)
        result = canvas.physical_dimensions
        assert result.width == pytest.approx(48.0)
        assert result.height == pytest.approx(36.0)
