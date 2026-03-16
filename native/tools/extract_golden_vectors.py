#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Extract golden test vectors from the Python FDL implementation.

Generates JSON files that the C++ Catch2 tests load to verify the C++ port
produces identical results to the Python reference implementation.

Usage:
    python extract_golden_vectors.py [--verify] [--output-dir DIR]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure fdl package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages" / "fdl" / "src"))

from fdl.canvas import Canvas
from fdl.common import Dimensions, Point
from fdl.constants import RoundingEven, RoundingMode
from fdl.context import Context
from fdl.fdl import FDL
from fdl.framingdecision import FramingDecision
from fdl.framingintent import FramingIntent
from fdl.rounding import fdl_round
from fdl.fdl_types import DimensionsFloat, DimensionsInt, PointFloat

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "core" / "tests" / "vectors"


# ---------------------------------------------------------------------------
# Rounding vectors
# ---------------------------------------------------------------------------


def generate_rounding_vectors() -> dict:
    """Generate rounding vectors for all combinations of value x mode x even."""
    test_values = [
        0.0,
        1.0,
        1.5,
        2.0,
        2.5,
        3.0,
        19.0,
        19.456,
        19.5,
        20.5,
        79.0,
        79.456,
        79.5,
        80.5,
        -3.5,
        -19.0,
        -19.456,
        -19.5,
        -20.5,
        0.1,
        0.9,
        1.1,
        1.9,
        100.0,
        100.5,
        101.5,
    ]

    modes = [
        (RoundingMode.UP, "up"),
        (RoundingMode.DOWN, "down"),
        (RoundingMode.ROUND, "round"),
    ]
    evens = [
        (RoundingEven.WHOLE, "whole"),
        (RoundingEven.EVEN, "even"),
    ]

    vectors = []
    for value in test_values:
        for mode_enum, mode_name in modes:
            for even_enum, even_name in evens:
                result = fdl_round(value, even_enum, mode_enum)
                vectors.append(
                    {
                        "input": {"value": value},
                        "params": {"mode": mode_name, "even": even_name},
                        "expected": result,
                    }
                )

    return {
        "description": "fdl_round() golden vectors — all combos of value x mode x even",
        "version": "1.0",
        "vectors": vectors,
    }


# ---------------------------------------------------------------------------
# Dimensions math vectors
# ---------------------------------------------------------------------------


def _dims_dict(d: Dimensions) -> dict:
    return {"width": float(d.width), "height": float(d.height)}


def generate_dimensions_vectors() -> dict:
    """Generate dimensions math test vectors."""
    test_dims = [
        (4096.0, 2160.0),
        (3840.0, 2160.0),
        (1920.0, 1080.0),
        (2048.0, 858.0),
        (4096.0, 1716.0),
        (0.0, 0.0),
        (100.0, 200.0),
    ]

    vectors = []

    # normalize
    for w, h in test_dims:
        for squeeze in [1.0, 2.0, 1.3]:
            d = Dimensions[float]()
            d.width, d.height = w, h
            result = d.normalize(squeeze)
            vectors.append(
                {
                    "op": "normalize",
                    "input": {"width": w, "height": h},
                    "params": {"squeeze": squeeze},
                    "expected": _dims_dict(result),
                }
            )

    # scale
    for w, h in test_dims:
        for sf, tsq in [(1.0, 1.0), (0.5, 1.0), (2.0, 1.3), (0.75, 2.0)]:
            d = Dimensions[float]()
            d.width, d.height = w, h
            result = d.scale(sf, tsq)
            vectors.append(
                {
                    "op": "scale",
                    "input": {"width": w, "height": h},
                    "params": {"scale_factor": sf, "target_squeeze": tsq},
                    "expected": _dims_dict(result),
                }
            )

    # normalize_and_scale
    for w, h in [(4096.0, 2160.0), (1920.0, 1080.0)]:
        for isq, sf, tsq in [(2.0, 0.5, 1.0), (1.3, 1.0, 1.3), (1.0, 2.0, 2.0)]:
            d = Dimensions[float]()
            d.width, d.height = w, h
            result = d.normalize_and_scale(isq, sf, tsq)
            vectors.append(
                {
                    "op": "normalize_and_scale",
                    "input": {"width": w, "height": h},
                    "params": {"input_squeeze": isq, "scale_factor": sf, "target_squeeze": tsq},
                    "expected": _dims_dict(result),
                }
            )

    # sub
    pairs = [
        ((4096.0, 2160.0), (3840.0, 2160.0)),
        ((1920.0, 1080.0), (1920.0, 1080.0)),
        ((100.0, 200.0), (50.0, 100.0)),
    ]
    for (aw, ah), (bw, bh) in pairs:
        a = Dimensions[float]()
        a.width, a.height = aw, ah
        b = Dimensions[float]()
        b.width, b.height = bw, bh
        result = a - b
        vectors.append(
            {
                "op": "sub",
                "input": {"a": {"width": aw, "height": ah}, "b": {"width": bw, "height": bh}},
                "expected": _dims_dict(result),
            }
        )

    # is_zero
    for w, h in [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]:
        d = Dimensions[float]()
        d.width, d.height = w, h
        vectors.append(
            {
                "op": "is_zero",
                "input": {"width": w, "height": h},
                "expected": d.is_zero(),
            }
        )

    # equal
    eq_pairs = [
        ((4096.0, 2160.0), (4096.0, 2160.0), True),
        ((4096.0, 2160.0), (4096.0 + 1e-7, 2160.0), True),  # within abs_tol
        ((4096.0, 2160.0), (4096.001, 2160.0), False),  # outside abs_tol
        ((0.0, 0.0), (0.0, 0.0), True),
        ((1920.0, 1080.0), (1920.0, 1080.5), False),
    ]
    for (aw, ah), (bw, bh), expected in eq_pairs:
        a = Dimensions[float]()
        a.width, a.height = aw, ah
        b = Dimensions[float]()
        b.width, b.height = bw, bh
        actual = a == b
        assert actual == expected, f"Dims equal mismatch: ({aw},{ah}) vs ({bw},{bh}): got {actual}, expected {expected}"
        vectors.append(
            {
                "op": "equal",
                "input": {"a": {"width": aw, "height": ah}, "b": {"width": bw, "height": bh}},
                "expected": expected,
            }
        )

    return {
        "description": "Dimensions math golden vectors",
        "version": "1.0",
        "vectors": vectors,
    }


# ---------------------------------------------------------------------------
# Point math vectors
# ---------------------------------------------------------------------------


def _point_dict(p: Point) -> dict:
    return {"x": float(p.x), "y": float(p.y)}


def generate_point_vectors() -> dict:
    """Generate point math test vectors."""
    test_points = [
        (0.0, 0.0),
        (100.0, 200.0),
        (-50.0, 75.0),
        (1920.0, 1080.0),
        (2048.0, 858.0),
    ]

    vectors = []

    # normalize
    for x, y in test_points:
        for squeeze in [1.0, 2.0, 1.3]:
            p = Point[float]()
            p.x, p.y = x, y
            result = p.normalize(squeeze)
            vectors.append(
                {
                    "op": "normalize",
                    "input": {"x": x, "y": y},
                    "params": {"squeeze": squeeze},
                    "expected": _point_dict(result),
                }
            )

    # scale
    for x, y in test_points:
        for sf, tsq in [(1.0, 1.0), (0.5, 1.0), (2.0, 1.3)]:
            p = Point[float]()
            p.x, p.y = x, y
            result = p.scale(sf, tsq)
            vectors.append(
                {
                    "op": "scale",
                    "input": {"x": x, "y": y},
                    "params": {"scale_factor": sf, "target_squeeze": tsq},
                    "expected": _point_dict(result),
                }
            )

    # add
    add_pairs = [
        ((100.0, 200.0), (50.0, 75.0)),
        ((0.0, 0.0), (100.0, 200.0)),
        ((-50.0, 75.0), (50.0, -75.0)),
    ]
    for (ax, ay), (bx, by) in add_pairs:
        a = Point[float]()
        a.x, a.y = ax, ay
        b = Point[float]()
        b.x, b.y = bx, by
        result = a + b
        vectors.append(
            {
                "op": "add",
                "input": {"a": {"x": ax, "y": ay}, "b": {"x": bx, "y": by}},
                "expected": _point_dict(result),
            }
        )

    # sub
    for (ax, ay), (bx, by) in add_pairs:
        a = Point[float]()
        a.x, a.y = ax, ay
        b = Point[float]()
        b.x, b.y = bx, by
        result = a - b
        vectors.append(
            {
                "op": "sub",
                "input": {"a": {"x": ax, "y": ay}, "b": {"x": bx, "y": by}},
                "expected": _point_dict(result),
            }
        )

    # mul_scalar
    for x, y in test_points:
        for scalar in [0.0, 1.0, 2.0, -1.0, 0.5]:
            p = Point[float]()
            p.x, p.y = x, y
            result = p * scalar
            vectors.append(
                {
                    "op": "mul_scalar",
                    "input": {"x": x, "y": y},
                    "params": {"scalar": scalar},
                    "expected": _point_dict(result),
                }
            )

    # clamp
    clamp_cases = [
        ((100.0, 200.0), None, None),
        ((100.0, 200.0), 0.0, None),
        ((100.0, 200.0), None, 150.0),
        ((100.0, 200.0), 0.0, 150.0),
        ((-50.0, 75.0), 0.0, 100.0),
        ((-50.0, 75.0), -100.0, 50.0),
    ]
    for (x, y), min_val, max_val in clamp_cases:
        p = Point[float]()
        p.x, p.y = x, y
        result = p.clamp(min_val, max_val)
        vectors.append(
            {
                "op": "clamp",
                "input": {"x": x, "y": y},
                "params": {
                    "min_val": min_val if min_val is not None else 0.0,
                    "max_val": max_val if max_val is not None else 0.0,
                    "has_min": min_val is not None,
                    "has_max": max_val is not None,
                },
                "expected": _point_dict(result),
            }
        )

    # equal
    eq_cases = [
        ((100.0, 200.0), (100.0, 200.0), True),
        ((100.0, 200.0), (100.0 + 1e-7, 200.0), True),
        ((100.0, 200.0), (100.001, 200.0), False),
        ((0.0, 0.0), (0.0, 0.0), True),
    ]
    for (ax, ay), (bx, by), expected in eq_cases:
        a = Point[float]()
        a.x, a.y = ax, ay
        b = Point[float]()
        b.x, b.y = bx, by
        actual = a == b
        assert actual == expected, f"Point equal mismatch: ({ax},{ay}) vs ({bx},{by})"
        vectors.append(
            {
                "op": "equal",
                "input": {"a": {"x": ax, "y": ay}, "b": {"x": bx, "y": by}},
                "expected": expected,
            }
        )

    return {
        "description": "Point math golden vectors",
        "version": "1.0",
        "vectors": vectors,
    }


# ---------------------------------------------------------------------------
# Document roundtrip vectors
# ---------------------------------------------------------------------------


def _scramble_keys(d: dict) -> dict:
    """Reverse the key order of a dict (recursively) for testing reordering."""
    result = {}
    keys = list(d.keys())
    for k in reversed(keys):
        v = d[k]
        if isinstance(v, dict):
            result[k] = _scramble_keys(v)
        elif isinstance(v, list):
            result[k] = [_scramble_keys(item) if isinstance(item, dict) else item for item in v]
        else:
            result[k] = v
    return result


def generate_roundtrip_vectors() -> dict:
    """Generate FDL document roundtrip test vectors.

    Each vector has:
      - 'label': description of the test case
      - 'input': FDL JSON (potentially with scrambled key order)
      - 'expected': canonical serialization from Python model_dump_json
    """
    vectors = []

    # 1. Minimal FDL — header + empty collections
    fdl = FDL(
        uuid="00000000-0000-0000-0000-000000000001",
        fdl_creator="test-roundtrip",
    )
    canonical = json.loads(fdl.as_json(indent=2, exclude_none=True))
    scrambled = _scramble_keys(canonical)
    vectors.append(
        {
            "label": "minimal_fdl",
            "input": scrambled,
            "expected": canonical,
        }
    )

    # 2. FDL with framing intents
    fdl = FDL(
        uuid="00000000-0000-0000-0000-000000000002",
        fdl_creator="test-roundtrip",
        default_framing_intent="FI_239",
    )
    fdl.framing_intents.append(
        FramingIntent(
            label="2.39:1",
            id="FI_239",
            aspect_ratio=DimensionsInt(width=239, height=100),
            protection=0.1,
        )
    )
    fdl.framing_intents.append(
        FramingIntent(
            label="1.78:1",
            id="FI_178",
            aspect_ratio=DimensionsInt(width=16, height=9),
        )
    )
    canonical = json.loads(fdl.as_json(indent=2, exclude_none=True))
    scrambled = _scramble_keys(canonical)
    vectors.append(
        {
            "label": "fdl_with_framing_intents",
            "input": scrambled,
            "expected": canonical,
        }
    )

    # 3. FDL with context + canvas + framing decisions (no protection)
    fdl = FDL(
        uuid="00000000-0000-0000-0000-000000000003",
        fdl_creator="test-roundtrip",
    )
    fi = FramingIntent(
        label="2.39:1",
        id="FI_239",
        aspect_ratio=DimensionsInt(width=239, height=100),
    )
    fdl.framing_intents.append(fi)

    canvas = Canvas(
        label="OCF",
        id="CVS_OCF",
        source_canvas_id="CVS_OCF",
        dimensions=DimensionsInt(width=4096, height=2160),
        anamorphic_squeeze=1.0,
    )
    fd = FramingDecision(
        label="2.39:1",
        id="CVS_OCF-FI_239",
        framing_intent_id="FI_239",
        dimensions=DimensionsFloat(width=4096.0, height=1714.0),
        anchor_point=PointFloat(x=0.0, y=223.0),
    )
    canvas.framing_decisions.append(fd)

    ctx = Context(label="Camera A")
    ctx.canvases.append(canvas)
    fdl.contexts.append(ctx)

    canonical = json.loads(fdl.as_json(indent=2, exclude_none=True))
    scrambled = _scramble_keys(canonical)
    vectors.append(
        {
            "label": "fdl_with_context_canvas_fd",
            "input": scrambled,
            "expected": canonical,
        }
    )

    # 4. FDL with effective dimensions + anchor points
    fdl = FDL(
        uuid="00000000-0000-0000-0000-000000000004",
        fdl_creator="test-roundtrip",
    )
    fi = FramingIntent(
        label="2.39:1",
        id="FI_239",
        aspect_ratio=DimensionsInt(width=239, height=100),
        protection=0.1,
    )
    fdl.framing_intents.append(fi)

    canvas = Canvas(
        label="OCF with effective area",
        id="CVS_EFF",
        source_canvas_id="CVS_EFF",
        dimensions=DimensionsInt(width=5184, height=4320),
        effective_dimensions=DimensionsInt(width=4096, height=2160),
        effective_anchor_point=PointFloat(x=544.0, y=1080.0),
        anamorphic_squeeze=1.0,
    )
    fd = FramingDecision(
        label="2.39:1",
        id="CVS_EFF-FI_239",
        framing_intent_id="FI_239",
        dimensions=DimensionsFloat(width=3686.4, height=1542.68),
        anchor_point=PointFloat(x=749.0, y=1388.66),
        protection_dimensions=DimensionsFloat(width=4096.0, height=1714.0),
        protection_anchor_point=PointFloat(x=544.0, y=1303.0),
    )
    canvas.framing_decisions.append(fd)

    ctx = Context(label="Camera B")
    ctx.canvases.append(canvas)
    fdl.contexts.append(ctx)

    canonical = json.loads(fdl.as_json(indent=2, exclude_none=True))
    scrambled = _scramble_keys(canonical)
    vectors.append(
        {
            "label": "fdl_with_effective_dims_and_protection",
            "input": scrambled,
            "expected": canonical,
        }
    )

    # 5. FDL with anamorphic squeeze
    fdl = FDL(
        uuid="00000000-0000-0000-0000-000000000005",
        fdl_creator="test-roundtrip",
    )
    fi = FramingIntent(
        label="2.39:1",
        id="FI_239",
        aspect_ratio=DimensionsInt(width=239, height=100),
    )
    fdl.framing_intents.append(fi)

    canvas = Canvas(
        label="Anamorphic",
        id="CVS_ANA",
        source_canvas_id="CVS_ANA",
        dimensions=DimensionsInt(width=4096, height=3432),
        anamorphic_squeeze=2.0,
    )
    fd = FramingDecision(
        label="2.39:1",
        id="CVS_ANA-FI_239",
        framing_intent_id="FI_239",
        dimensions=DimensionsFloat(width=4096.0, height=1714.0),
        anchor_point=PointFloat(x=0.0, y=859.0),
    )
    canvas.framing_decisions.append(fd)

    ctx = Context(label="Camera C", context_creator="DIT Station")
    ctx.canvases.append(canvas)
    fdl.contexts.append(ctx)

    canonical = json.loads(fdl.as_json(indent=2, exclude_none=True))
    scrambled = _scramble_keys(canonical)
    vectors.append(
        {
            "label": "fdl_with_anamorphic_squeeze",
            "input": scrambled,
            "expected": canonical,
        }
    )

    # 6. Identity roundtrip — already canonical input
    fdl = FDL(
        uuid="00000000-0000-0000-0000-000000000006",
        fdl_creator="test-identity",
    )
    fdl.framing_intents.append(
        FramingIntent(
            label="1.85:1",
            id="FI_185",
            aspect_ratio=DimensionsInt(width=185, height=100),
        )
    )
    canonical = json.loads(fdl.as_json(indent=2, exclude_none=True))
    vectors.append(
        {
            "label": "identity_roundtrip",
            "input": canonical,  # already canonical
            "expected": canonical,
        }
    )

    # 7. FDL with null default_framing_intent (should be stripped)
    raw = {
        "uuid": "00000000-0000-0000-0000-000000000007",
        "version": {"major": 2, "minor": 0},
        "fdl_creator": "test-null-strip",
        "default_framing_intent": None,
        "framing_intents": [],
        "contexts": [],
        "canvas_templates": [],
    }
    # Expected: null stripped
    expected = {k: v for k, v in raw.items() if v is not None}
    vectors.append(
        {
            "label": "null_default_framing_intent_stripped",
            "input": raw,
            "expected": expected,
        }
    )

    # 8. FDL with context containing clip_id
    from fdl.clipid import ClipID

    fdl = FDL(
        uuid="00000000-0000-0000-0000-000000000008",
        fdl_creator="test-clip-id",
    )
    ctx = Context(
        label="Camera D",
        clip_id=ClipID(clip_name="A001", file="A001C001_220101_R1AB.ari"),
    )
    canvas = Canvas(
        label="OCF",
        id="CVS_CLIP",
        source_canvas_id="CVS_CLIP",
        dimensions=DimensionsInt(width=3840, height=2160),
    )
    ctx.canvases.append(canvas)
    fdl.contexts.append(ctx)

    canonical = json.loads(fdl.as_json(indent=2, exclude_none=True))
    scrambled = _scramble_keys(canonical)
    vectors.append(
        {
            "label": "fdl_with_clip_id",
            "input": scrambled,
            "expected": canonical,
        }
    )

    return {
        "description": "FDL document roundtrip golden vectors — parse and re-serialize canonically",
        "version": "1.0",
        "vectors": vectors,
    }


# ---------------------------------------------------------------------------
# Validation vectors
# ---------------------------------------------------------------------------


def _make_minimal_fdl(uuid_suffix: str = "0001", **overrides) -> dict:
    """Build a minimal valid FDL dict."""
    fdl = {
        "uuid": f"00000000-0000-0000-0000-{uuid_suffix:>012s}",
        "version": {"major": 2, "minor": 0},
        "fdl_creator": "test-validation",
        "framing_intents": [{"label": "2.39:1", "id": "FI_239", "aspect_ratio": {"width": 239, "height": 100}, "protection": 0.0}],
        "contexts": [
            {
                "label": "Camera A",
                "canvases": [
                    {
                        "label": "OCF",
                        "id": "CVS_OCF",
                        "source_canvas_id": "CVS_OCF",
                        "dimensions": {"width": 4096, "height": 2160},
                        "anamorphic_squeeze": 1.0,
                        "framing_decisions": [
                            {
                                "label": "2.39:1",
                                "id": "CVS_OCF-FI_239",
                                "framing_intent_id": "FI_239",
                                "dimensions": {"width": 4096.0, "height": 1714.0},
                                "anchor_point": {"x": 0.0, "y": 223.0},
                            }
                        ],
                    }
                ],
            }
        ],
        "canvas_templates": [],
    }
    fdl.update(overrides)
    return fdl


def generate_validation_vectors() -> dict:
    """Generate validation golden vectors.

    Each vector has:
      - 'label': description
      - 'input': FDL JSON dict
      - 'expected_error_count': number of errors
      - 'expected_errors': list of exact error message strings
    """
    from fdl.fdlchecker import validate_fdl

    vectors = []

    # --- Valid FDLs (0 errors) ---

    # 1. Minimal valid FDL
    fdl = _make_minimal_fdl("val001")
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count == 0, f"Expected 0 errors for valid FDL, got {error_count}: {error_msgs}"
    vectors.append(
        {
            "label": "valid_minimal",
            "input": fdl,
            "expected_error_count": 0,
            "expected_errors": [],
        }
    )

    # 2. Valid FDL with effective dimensions (must be >= framing decision dims)
    fdl = _make_minimal_fdl("val002")
    fdl["contexts"][0]["canvases"][0]["effective_dimensions"] = {"width": 4096, "height": 2100}
    fdl["contexts"][0]["canvases"][0]["effective_anchor_point"] = {"x": 0.0, "y": 30.0}
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count == 0, f"Expected 0 errors, got {error_count}: {error_msgs}"
    vectors.append(
        {
            "label": "valid_with_effective_dims",
            "input": fdl,
            "expected_error_count": 0,
            "expected_errors": [],
        }
    )

    # 3. Valid FDL with protection
    fdl = _make_minimal_fdl("val003")
    fdl["contexts"][0]["canvases"][0]["framing_decisions"][0]["protection_dimensions"] = {"width": 4096.0, "height": 1714.0}
    fdl["contexts"][0]["canvases"][0]["framing_decisions"][0]["protection_anchor_point"] = {"x": 0.0, "y": 223.0}
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count == 0, f"Expected 0 errors, got {error_count}: {error_msgs}"
    vectors.append(
        {
            "label": "valid_with_protection",
            "input": fdl,
            "expected_error_count": 0,
            "expected_errors": [],
        }
    )

    # --- Invalid FDLs (errors) ---

    # 4. Duplicate framing intent ID
    fdl = _make_minimal_fdl("inv001")
    fdl["framing_intents"].append({"label": "Duplicate", "id": "FI_239", "aspect_ratio": {"width": 239, "height": 100}, "protection": 0.0})
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count == 1
    vectors.append(
        {
            "label": "duplicate_framing_intent_id",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 5. Default framing intent not in list
    fdl = _make_minimal_fdl("inv002")
    fdl["default_framing_intent"] = "NONEXISTENT"
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count == 1
    vectors.append(
        {
            "label": "default_fi_not_in_list",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 6. Duplicate canvas ID
    fdl = _make_minimal_fdl("inv003")
    fdl["contexts"].append(
        {
            "label": "Camera B",
            "canvases": [
                {
                    "label": "Duplicate",
                    "id": "CVS_OCF",
                    "source_canvas_id": "CVS_OCF",
                    "dimensions": {"width": 3840, "height": 2160},
                    "anamorphic_squeeze": 1.0,
                    "framing_decisions": [
                        {
                            "label": "2.39:1",
                            "id": "CVS_OCF-FI_239",
                            "framing_intent_id": "FI_239",
                            "dimensions": {"width": 3840.0, "height": 1607.0},
                            "anchor_point": {"x": 0.0, "y": 276.5},
                        }
                    ],
                }
            ],
        }
    )
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count >= 1
    vectors.append(
        {
            "label": "duplicate_canvas_id",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 7. FD ID doesn't match expected format
    fdl = _make_minimal_fdl("inv004")
    fdl["contexts"][0]["canvases"][0]["framing_decisions"][0]["id"] = "WRONG_ID"
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count >= 1
    vectors.append(
        {
            "label": "fd_id_mismatch",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 8. Source canvas ID not in canvases
    fdl = _make_minimal_fdl("inv005")
    fdl["contexts"][0]["canvases"][0]["source_canvas_id"] = "NONEXISTENT"
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count >= 1
    vectors.append(
        {
            "label": "source_canvas_not_found",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 9. Dimension hierarchy violation — FD dims exceed canvas dims
    fdl = _make_minimal_fdl("inv006")
    fdl["contexts"][0]["canvases"][0]["framing_decisions"][0]["dimensions"] = {"width": 5000.0, "height": 3000.0}
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count >= 1
    vectors.append(
        {
            "label": "dim_hierarchy_fd_exceeds_canvas",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 10. Negative anchor point
    fdl = _make_minimal_fdl("inv007")
    fdl["contexts"][0]["canvases"][0]["framing_decisions"][0]["anchor_point"] = {"x": -10.0, "y": 223.0}
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count >= 1
    vectors.append(
        {
            "label": "negative_anchor_point",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 11. Anchor exceeds canvas dimensions
    fdl = _make_minimal_fdl("inv008")
    fdl["contexts"][0]["canvases"][0]["framing_decisions"][0]["anchor_point"] = {"x": 5000.0, "y": 223.0}
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count >= 1
    vectors.append(
        {
            "label": "anchor_exceeds_canvas",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 12. Negative effective anchor point
    fdl = _make_minimal_fdl("inv009")
    fdl["contexts"][0]["canvases"][0]["effective_dimensions"] = {"width": 4000, "height": 2100}
    fdl["contexts"][0]["canvases"][0]["effective_anchor_point"] = {"x": -5.0, "y": 30.0}
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count >= 1
    vectors.append(
        {
            "label": "negative_effective_anchor",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    # 13. Framing intent ID referenced but not in list
    fdl = _make_minimal_fdl("inv010")
    fdl["contexts"][0]["canvases"][0]["framing_decisions"][0]["framing_intent_id"] = "MISSING_FI"
    error_count, error_msgs = validate_fdl(fdl)
    assert error_count >= 1
    vectors.append(
        {
            "label": "fd_references_missing_fi",
            "input": fdl,
            "expected_error_count": error_count,
            "expected_errors": error_msgs,
        }
    )

    return {
        "description": "FDL semantic validation golden vectors",
        "version": "1.0",
        "vectors": vectors,
    }


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def verify_vectors(data: dict, label: str) -> int:
    """Re-run all vectors against Python and count mismatches."""
    errors = 0
    for i, v in enumerate(data["vectors"]):
        op = v.get("op", "round")
        if op == "round" or "op" not in v:
            # Rounding vector
            mode_map = {"up": RoundingMode.UP, "down": RoundingMode.DOWN, "round": RoundingMode.ROUND}
            even_map = {"whole": RoundingEven.WHOLE, "even": RoundingEven.EVEN}
            result = fdl_round(
                v["input"]["value"],
                even_map[v["params"]["even"]],
                mode_map[v["params"]["mode"]],
            )
            if result != v["expected"]:
                print(f"  FAIL [{label}] vector {i}: got {result}, expected {v['expected']}")
                errors += 1
        # Dimensions and Point vectors are validated during generation (assertions)

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Extract golden test vectors from Python FDL implementation")
    parser.add_argument("--verify", action="store_true", help="Re-verify vectors after generation")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    args = parser.parse_args()

    output_dir = args.output_dir
    rounding_dir = output_dir / "rounding"
    value_types_dir = output_dir / "value_types"
    document_dir = output_dir / "document"
    validation_dir = output_dir / "validation"
    rounding_dir.mkdir(parents=True, exist_ok=True)
    value_types_dir.mkdir(parents=True, exist_ok=True)
    document_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)

    # Generate
    rounding = generate_rounding_vectors()
    dims = generate_dimensions_vectors()
    points = generate_point_vectors()
    roundtrip = generate_roundtrip_vectors()
    validation = generate_validation_vectors()

    # Write
    rounding_path = rounding_dir / "rounding_vectors.json"
    dims_path = value_types_dir / "dimensions_math_vectors.json"
    points_path = value_types_dir / "point_math_vectors.json"
    roundtrip_path = document_dir / "roundtrip_vectors.json"
    validation_path = validation_dir / "validation_vectors.json"

    for path, data in [
        (rounding_path, rounding),
        (dims_path, dims),
        (points_path, points),
        (roundtrip_path, roundtrip),
        (validation_path, validation),
    ]:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {len(data['vectors'])} vectors to {path}")

    # Verify
    if args.verify:
        print("\nVerifying...")
        errors = 0
        errors += verify_vectors(rounding, "rounding")
        if errors == 0:
            print("  All rounding vectors verified OK")
        print(f"\nTotal errors: {errors}")
        return errors

    return 0


if __name__ == "__main__":
    sys.exit(main())
