# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Generate golden vectors for fdl_geometry_t operations."""

import json
import sys

sys.path.insert(0, "../../../../packages/fdl/src")

from fdl.canvastemplate import Geometry
from fdl.common import DimensionsFloat, PointFloat
from fdl.rounding import RoundStrategy


def dims(w: float, h: float) -> DimensionsFloat:
    return DimensionsFloat(width=w, height=h)


def pt(x: float, y: float) -> PointFloat:
    return PointFloat(x=x, y=y)


def ser_dims(d: DimensionsFloat) -> dict:
    return {"width": d.width, "height": d.height}


def ser_pt(p: PointFloat) -> dict:
    return {"x": p.x, "y": p.y}


def ser_geo(g: Geometry) -> dict:
    return {
        "canvas_dims": ser_dims(g.canvas_dims),
        "effective_dims": ser_dims(g.effective_dims),
        "protection_dims": ser_dims(g.protection_dims),
        "framing_dims": ser_dims(g.framing_dims),
        "effective_anchor": ser_pt(g.effective_anchor),
        "protection_anchor": ser_pt(g.protection_anchor),
        "framing_anchor": ser_pt(g.framing_anchor),
    }


# ---- fill_hierarchy_gaps vectors ----
def generate_fill_hierarchy_gaps():
    vectors = []

    # Case 1: All populated - no changes except anchor offset subtraction
    g = Geometry(
        canvas_dims=dims(4096, 2160),
        effective_dims=dims(4000, 2100),
        protection_dims=dims(3900, 1700),
        framing_dims=dims(3800, 1600),
        effective_anchor=pt(48, 30),
        protection_anchor=pt(50, 200),
        framing_anchor=pt(100, 250),
    )
    offset = pt(48, 30)
    result = g.fill_hierarchy_gaps(offset)
    vectors.append(
        {
            "label": "all_populated",
            "input": ser_geo(g),
            "anchor_offset": ser_pt(offset),
            "expected": ser_geo(result),
        }
    )

    # Case 2: Only framing populated - canvas and effective filled from framing, protection stays zero
    g = Geometry(
        canvas_dims=dims(0, 0),
        effective_dims=dims(0, 0),
        protection_dims=dims(0, 0),
        framing_dims=dims(1920, 1080),
        effective_anchor=pt(0, 0),
        protection_anchor=pt(0, 0),
        framing_anchor=pt(100, 50),
    )
    offset = pt(0, 0)
    result = g.fill_hierarchy_gaps(offset)
    vectors.append(
        {
            "label": "only_framing_populated",
            "input": ser_geo(g),
            "anchor_offset": ser_pt(offset),
            "expected": ser_geo(result),
        }
    )

    # Case 3: Only effective populated - canvas filled from effective
    g = Geometry(
        canvas_dims=dims(0, 0),
        effective_dims=dims(3840, 2160),
        protection_dims=dims(0, 0),
        framing_dims=dims(0, 0),
        effective_anchor=pt(100, 50),
        protection_anchor=pt(0, 0),
        framing_anchor=pt(0, 0),
    )
    offset = pt(0, 0)
    result = g.fill_hierarchy_gaps(offset)
    vectors.append(
        {
            "label": "only_effective_populated",
            "input": ser_geo(g),
            "anchor_offset": ser_pt(offset),
            "expected": ser_geo(result),
        }
    )

    # Case 4: Only protection populated - canvas and effective filled from protection
    g = Geometry(
        canvas_dims=dims(0, 0),
        effective_dims=dims(0, 0),
        protection_dims=dims(3000, 1600),
        framing_dims=dims(0, 0),
        effective_anchor=pt(0, 0),
        protection_anchor=pt(200, 100),
        framing_anchor=pt(0, 0),
    )
    offset = pt(0, 0)
    result = g.fill_hierarchy_gaps(offset)
    vectors.append(
        {
            "label": "only_protection_populated",
            "input": ser_geo(g),
            "anchor_offset": ser_pt(offset),
            "expected": ser_geo(result),
        }
    )

    # Case 5: Canvas and framing only - effective filled from canvas, protection stays zero
    g = Geometry(
        canvas_dims=dims(4096, 2160),
        effective_dims=dims(0, 0),
        protection_dims=dims(0, 0),
        framing_dims=dims(1920, 1080),
        effective_anchor=pt(0, 0),
        protection_anchor=pt(0, 0),
        framing_anchor=pt(500, 300),
    )
    offset = pt(0, 0)
    result = g.fill_hierarchy_gaps(offset)
    vectors.append(
        {
            "label": "canvas_and_framing_only",
            "input": ser_geo(g),
            "anchor_offset": ser_pt(offset),
            "expected": ser_geo(result),
        }
    )

    # Case 6: Anchor offset causes clamping
    g = Geometry(
        canvas_dims=dims(4096, 2160),
        effective_dims=dims(4000, 2100),
        protection_dims=dims(0, 0),
        framing_dims=dims(3800, 1600),
        effective_anchor=pt(48, 30),
        protection_anchor=pt(10, 10),
        framing_anchor=pt(100, 250),
    )
    offset = pt(200, 300)  # Large offset causing negative anchors
    result = g.fill_hierarchy_gaps(offset)
    vectors.append(
        {
            "label": "anchor_offset_clamp",
            "input": ser_geo(g),
            "anchor_offset": ser_pt(offset),
            "expected": ser_geo(result),
        }
    )

    return vectors


# ---- normalize_and_scale vectors ----
def generate_normalize_and_scale():
    vectors = []

    # Case 1: No squeeze (1.0), scale factor 0.5
    g = Geometry(
        canvas_dims=dims(4096, 2160),
        effective_dims=dims(4000, 2100),
        protection_dims=dims(3900, 1700),
        framing_dims=dims(3800, 1600),
        effective_anchor=pt(48, 30),
        protection_anchor=pt(50, 200),
        framing_anchor=pt(100, 250),
    )
    result = g.normalize_and_scale(1.0, 0.5, 1.0)
    vectors.append(
        {
            "label": "no_squeeze_half_scale",
            "input": ser_geo(g),
            "source_squeeze": 1.0,
            "scale_factor": 0.5,
            "target_squeeze": 1.0,
            "expected": ser_geo(result),
        }
    )

    # Case 2: With anamorphic squeeze 1.3, scale to 1.0
    g = Geometry(
        canvas_dims=dims(4448, 3096),
        effective_dims=dims(4448, 3096),
        protection_dims=dims(0, 0),
        framing_dims=dims(4448, 2418),
        effective_anchor=pt(0, 0),
        protection_anchor=pt(0, 0),
        framing_anchor=pt(0, 339),
    )
    result = g.normalize_and_scale(1.3, 0.664251207729469, 1.0)
    vectors.append(
        {
            "label": "squeeze_1_3_to_1_0",
            "input": ser_geo(g),
            "source_squeeze": 1.3,
            "scale_factor": 0.664251207729469,
            "target_squeeze": 1.0,
            "expected": ser_geo(result),
        }
    )

    # Case 3: Scale factor 1.0 (identity with squeeze 2.0 -> 1.0)
    g = Geometry(
        canvas_dims=dims(2048, 1080),
        effective_dims=dims(2048, 1080),
        protection_dims=dims(0, 0),
        framing_dims=dims(2048, 858),
        effective_anchor=pt(0, 0),
        protection_anchor=pt(0, 0),
        framing_anchor=pt(0, 111),
    )
    result = g.normalize_and_scale(2.0, 1.0, 1.0)
    vectors.append(
        {
            "label": "squeeze_2_0_scale_1",
            "input": ser_geo(g),
            "source_squeeze": 2.0,
            "scale_factor": 1.0,
            "target_squeeze": 1.0,
            "expected": ser_geo(result),
        }
    )

    return vectors


# ---- round vectors ----
def generate_round():
    vectors = []

    # Case 1: Round with even/up
    g = Geometry(
        canvas_dims=dims(4096.7, 2160.3),
        effective_dims=dims(4000.5, 2100.5),
        protection_dims=dims(3900.1, 1700.9),
        framing_dims=dims(3800.3, 1600.7),
        effective_anchor=pt(48.5, 30.5),
        protection_anchor=pt(50.3, 200.7),
        framing_anchor=pt(100.1, 250.9),
    )
    rs = RoundStrategy(even="even", mode="up")
    result = g.round(rs)
    vectors.append(
        {
            "label": "round_even_up",
            "input": ser_geo(g),
            "even": "even",
            "mode": "up",
            "expected": ser_geo(result),
        }
    )

    # Case 2: Round with whole/down
    result2 = g.round(RoundStrategy(even="whole", mode="down"))
    vectors.append(
        {
            "label": "round_whole_down",
            "input": ser_geo(g),
            "even": "whole",
            "mode": "down",
            "expected": ser_geo(result2),
        }
    )

    # Case 3: Round with even/round
    result3 = g.round(RoundStrategy(even="even", mode="round"))
    vectors.append(
        {
            "label": "round_even_round",
            "input": ser_geo(g),
            "even": "even",
            "mode": "round",
            "expected": ser_geo(result3),
        }
    )

    return vectors


# ---- apply_offset vectors ----
def generate_apply_offset():
    vectors = []

    # Case 1: Positive offset (standard case)
    g = Geometry(
        canvas_dims=dims(1920, 1080),
        effective_dims=dims(1800, 1000),
        protection_dims=dims(1700, 950),
        framing_dims=dims(1600, 900),
        effective_anchor=pt(60, 40),
        protection_anchor=pt(110, 65),
        framing_anchor=pt(160, 90),
    )
    offset = pt(50, 30)
    geo_result, theo_eff, theo_prot, theo_fram = g.apply_offset(offset)
    vectors.append(
        {
            "label": "positive_offset",
            "input": ser_geo(g),
            "offset": ser_pt(offset),
            "expected_geometry": ser_geo(geo_result),
            "expected_theo_eff": ser_pt(theo_eff),
            "expected_theo_prot": ser_pt(theo_prot),
            "expected_theo_fram": ser_pt(theo_fram),
        }
    )

    # Case 2: Negative offset causing clamping
    g2 = Geometry(
        canvas_dims=dims(1920, 1080),
        effective_dims=dims(1800, 1000),
        protection_dims=dims(0, 0),
        framing_dims=dims(1600, 900),
        effective_anchor=pt(60, 40),
        protection_anchor=pt(0, 0),
        framing_anchor=pt(160, 90),
    )
    offset = pt(-200, -150)
    geo_result2, theo_eff2, theo_prot2, theo_fram2 = g2.apply_offset(offset)
    vectors.append(
        {
            "label": "negative_offset_clamp",
            "input": ser_geo(g2),
            "offset": ser_pt(offset),
            "expected_geometry": ser_geo(geo_result2),
            "expected_theo_eff": ser_pt(theo_eff2),
            "expected_theo_prot": ser_pt(theo_prot2),
            "expected_theo_fram": ser_pt(theo_fram2),
        }
    )

    # Case 3: Zero offset
    offset_zero = pt(0, 0)
    geo_result3, theo_eff3, theo_prot3, theo_fram3 = g.apply_offset(offset_zero)
    vectors.append(
        {
            "label": "zero_offset",
            "input": ser_geo(g),
            "offset": ser_pt(offset_zero),
            "expected_geometry": ser_geo(geo_result3),
            "expected_theo_eff": ser_pt(theo_eff3),
            "expected_theo_prot": ser_pt(theo_prot3),
            "expected_theo_fram": ser_pt(theo_fram3),
        }
    )

    return vectors


# ---- crop vectors ----
def generate_crop():
    vectors = []

    # Case 1: No crop needed (all within canvas)
    g = Geometry(
        canvas_dims=dims(1920, 1080),
        effective_dims=dims(1800, 1000),
        protection_dims=dims(1700, 950),
        framing_dims=dims(1600, 900),
        effective_anchor=pt(60, 40),
        protection_anchor=pt(110, 65),
        framing_anchor=pt(160, 90),
    )
    theo_eff = pt(60, 40)
    theo_prot = pt(110, 65)
    theo_fram = pt(160, 90)
    result = g.crop(theo_eff, theo_prot, theo_fram)
    vectors.append(
        {
            "label": "no_crop_needed",
            "input": ser_geo(g),
            "theo_eff": ser_pt(theo_eff),
            "theo_prot": ser_pt(theo_prot),
            "theo_fram": ser_pt(theo_fram),
            "expected": ser_geo(result),
        }
    )

    # Case 2: Negative theoretical anchors (content shifted left/up)
    g2 = Geometry(
        canvas_dims=dims(1920, 1080),
        effective_dims=dims(2400, 1400),
        protection_dims=dims(2200, 1300),
        framing_dims=dims(2000, 1200),
        effective_anchor=pt(0, 0),
        protection_anchor=pt(100, 50),
        framing_anchor=pt(200, 100),
    )
    theo_eff2 = pt(-200, -100)
    theo_prot2 = pt(-100, -50)
    theo_fram2 = pt(0, 0)
    result2 = g2.crop(theo_eff2, theo_prot2, theo_fram2)
    vectors.append(
        {
            "label": "negative_anchors_crop",
            "input": ser_geo(g2),
            "theo_eff": ser_pt(theo_eff2),
            "theo_prot": ser_pt(theo_prot2),
            "theo_fram": ser_pt(theo_fram2),
            "expected": ser_geo(result2),
        }
    )

    # Case 3: No protection (zero dims)
    g3 = Geometry(
        canvas_dims=dims(1920, 1080),
        effective_dims=dims(2400, 1400),
        protection_dims=dims(0, 0),
        framing_dims=dims(2000, 1200),
        effective_anchor=pt(0, 0),
        protection_anchor=pt(0, 0),
        framing_anchor=pt(200, 100),
    )
    theo_eff3 = pt(-200, -100)
    theo_prot3 = pt(0, 0)
    theo_fram3 = pt(0, 0)
    result3 = g3.crop(theo_eff3, theo_prot3, theo_fram3)
    vectors.append(
        {
            "label": "no_protection_crop",
            "input": ser_geo(g3),
            "theo_eff": ser_pt(theo_eff3),
            "theo_prot": ser_pt(theo_prot3),
            "theo_fram": ser_pt(theo_fram3),
            "expected": ser_geo(result3),
        }
    )

    # Case 4: Right-edge crop (content extends past canvas right edge)
    g4 = Geometry(
        canvas_dims=dims(1920, 1080),
        effective_dims=dims(2400, 1080),
        protection_dims=dims(0, 0),
        framing_dims=dims(2000, 900),
        effective_anchor=pt(0, 0),
        protection_anchor=pt(0, 0),
        framing_anchor=pt(200, 90),
    )
    theo_eff4 = pt(0, 0)
    theo_prot4 = pt(0, 0)
    theo_fram4 = pt(200, 90)
    result4 = g4.crop(theo_eff4, theo_prot4, theo_fram4)
    vectors.append(
        {
            "label": "right_edge_crop",
            "input": ser_geo(g4),
            "theo_eff": ser_pt(theo_eff4),
            "theo_prot": ser_pt(theo_prot4),
            "theo_fram": ser_pt(theo_fram4),
            "expected": ser_geo(result4),
        }
    )

    return vectors


# ---- get_dims_anchor_from_path vectors ----
def generate_get_dims_anchor():
    vectors = []

    g = Geometry(
        canvas_dims=dims(4096, 2160),
        effective_dims=dims(4000, 2100),
        protection_dims=dims(3900, 1700),
        framing_dims=dims(3800, 1600),
        effective_anchor=pt(48, 30),
        protection_anchor=pt(50, 200),
        framing_anchor=pt(100, 250),
    )

    paths = [
        ("canvas.dimensions", "canvas_dims"),
        ("canvas.effective_dimensions", "effective_dims"),
        ("framing_decision.protection_dimensions", "protection_dims"),
        ("framing_decision.dimensions", "framing_dims"),
    ]

    for path_str, label in paths:
        d, a = g.get_dimensions_and_anchors_from_path(path_str)
        vectors.append(
            {
                "label": f"path_{label}",
                "input": ser_geo(g),
                "path": path_str,
                "expected_dims": ser_dims(d),
                "expected_anchor": ser_pt(a) if a else {"x": 0.0, "y": 0.0},
            }
        )

    return vectors


def main():
    all_vectors = {
        "description": "FDL Geometry golden vectors",
        "version": "1.0",
        "fill_hierarchy_gaps": generate_fill_hierarchy_gaps(),
        "normalize_and_scale": generate_normalize_and_scale(),
        "round": generate_round(),
        "apply_offset": generate_apply_offset(),
        "crop": generate_crop(),
        "get_dims_anchor_from_path": generate_get_dims_anchor(),
    }

    output_path = "geometry_vectors.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_vectors, f, indent=2)
    print(f"Generated {output_path}")

    # Count vectors
    total = 0
    for key, val in all_vectors.items():
        if isinstance(val, list):
            total += len(val)
            print(f"  {key}: {len(val)} vectors")
    print(f"Total: {total} vectors")


if __name__ == "__main__":
    main()
