# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Generate golden vectors for pipeline helper functions."""

import json
import sys

sys.path.insert(0, "../../../../packages/fdl/src")

from fdl.canvastemplate import _alignment_shift, _output_size_for_axis, calculate_scale_factor
from fdl.common import DimensionsFloat


def dims(w: float, h: float) -> DimensionsFloat:
    return DimensionsFloat(width=w, height=h)


def ser_dims(d: DimensionsFloat) -> dict:
    return {"width": d.width, "height": d.height}


# ---- calculate_scale_factor vectors ----
def generate_scale_factor():
    vectors = []

    cases = [
        # label, fit_norm, target_norm, fit_method
        ("width_wider", dims(4096, 2160), dims(1920, 1080), "width"),
        ("width_narrower", dims(1920, 1080), dims(3840, 2160), "width"),
        ("height_taller", dims(4096, 2160), dims(1920, 1080), "height"),
        ("fit_all_letterbox", dims(4096, 1714), dims(1920, 1080), "fit_all"),
        ("fit_all_pillarbox", dims(2048, 2160), dims(1920, 1080), "fit_all"),
        ("fill_letterbox", dims(4096, 1714), dims(1920, 1080), "fill"),
        ("fill_pillarbox", dims(2048, 2160), dims(1920, 1080), "fill"),
        ("width_identity", dims(1920, 1080), dims(1920, 1080), "width"),
        ("fit_all_exact", dims(1920, 1080), dims(1920, 1080), "fit_all"),
        # Anamorphic case (already normalized)
        ("anamorphic_norm", dims(5782.4, 3096), dims(3840, 2160), "width"),
    ]

    for label, fit, target, method in cases:
        result = calculate_scale_factor(fit, target, method)
        vectors.append(
            {
                "label": label,
                "fit_norm": ser_dims(fit),
                "target_norm": ser_dims(target),
                "fit_method": method,
                "expected": result,
            }
        )

    return vectors


# ---- output_size_for_axis vectors ----
def generate_output_size():
    vectors = []

    cases = [
        # label, canvas_size, max_size, has_max, pad_to_max
        ("fit_no_max", 1920.0, 0.0, False, False),
        ("pad_to_max", 1920.0, 3840.0, True, True),
        ("crop_to_max", 3840.0, 1920.0, True, False),
        ("fit_within_max", 1920.0, 3840.0, True, False),
        ("pad_exact", 1920.0, 1920.0, True, True),
        ("crop_exact", 1920.0, 1920.0, True, False),
    ]

    for label, canvas, max_s, has, pad in cases:
        result = _output_size_for_axis(canvas, max_s, has, pad)
        vectors.append(
            {
                "label": label,
                "canvas_size": canvas,
                "max_size": max_s,
                "has_max": has,
                "pad_to_max": pad,
                "expected": result,
            }
        )

    return vectors


# ---- alignment_shift vectors ----
def generate_alignment_shift():
    vectors = []

    cases = [
        # FIT regime: output matches canvas, no shift
        {
            "label": "fit_no_shift",
            "fit_size": 1920.0,
            "fit_anchor": 0.0,
            "output_size": 1920.0,
            "canvas_size": 1920.0,
            "target_size": 1920.0,
            "is_center": True,
            "align_factor": 0.5,
            "pad_to_max": False,
        },
        # PAD regime: center alignment
        {
            "label": "pad_center",
            "fit_size": 1600.0,
            "fit_anchor": 160.0,
            "output_size": 3840.0,
            "canvas_size": 1920.0,
            "target_size": 1920.0,
            "is_center": True,
            "align_factor": 0.5,
            "pad_to_max": True,
        },
        # PAD regime: left alignment with gap
        {
            "label": "pad_left_gap",
            "fit_size": 1600.0,
            "fit_anchor": 160.0,
            "output_size": 3840.0,
            "canvas_size": 1920.0,
            "target_size": 1920.0,
            "is_center": False,
            "align_factor": 0.0,
            "pad_to_max": True,
        },
        # PAD regime: right alignment with gap
        {
            "label": "pad_right_gap",
            "fit_size": 1600.0,
            "fit_anchor": 160.0,
            "output_size": 3840.0,
            "canvas_size": 1920.0,
            "target_size": 1920.0,
            "is_center": False,
            "align_factor": 1.0,
            "pad_to_max": True,
        },
        # CROP regime: fit at origin and visible
        {
            "label": "crop_fit_at_origin",
            "fit_size": 1920.0,
            "fit_anchor": 0.0,
            "output_size": 1920.0,
            "canvas_size": 2400.0,
            "target_size": 1920.0,
            "is_center": True,
            "align_factor": 0.5,
            "pad_to_max": False,
        },
        # CROP regime: fit overflows output
        {
            "label": "crop_fit_overflows",
            "fit_size": 2400.0,
            "fit_anchor": 0.0,
            "output_size": 1920.0,
            "canvas_size": 2400.0,
            "target_size": 1920.0,
            "is_center": True,
            "align_factor": 0.5,
            "pad_to_max": False,
        },
        # CROP regime: only bounding box overflows, center
        {
            "label": "crop_bbox_overflow_center",
            "fit_size": 1600.0,
            "fit_anchor": 400.0,
            "output_size": 1920.0,
            "canvas_size": 2400.0,
            "target_size": 1920.0,
            "is_center": True,
            "align_factor": 0.5,
            "pad_to_max": False,
        },
        # CROP regime: only bounding box overflows, right
        {
            "label": "crop_bbox_overflow_right",
            "fit_size": 1600.0,
            "fit_anchor": 400.0,
            "output_size": 1920.0,
            "canvas_size": 2400.0,
            "target_size": 1920.0,
            "is_center": False,
            "align_factor": 1.0,
            "pad_to_max": False,
        },
        # FIT regime: tiny overflow (within threshold 0.01)
        {
            "label": "fit_tiny_overflow",
            "fit_size": 1920.0,
            "fit_anchor": 0.0,
            "output_size": 1920.0,
            "canvas_size": 1920.005,
            "target_size": 1920.0,
            "is_center": True,
            "align_factor": 0.5,
            "pad_to_max": False,
        },
        # PAD: center when no gap (fit >= target)
        {
            "label": "pad_center_no_gap",
            "fit_size": 1920.0,
            "fit_anchor": 0.0,
            "output_size": 3840.0,
            "canvas_size": 1920.0,
            "target_size": 1800.0,
            "is_center": False,
            "align_factor": 0.5,
            "pad_to_max": True,
        },
    ]

    for case in cases:
        result = _alignment_shift(
            case["fit_size"],
            case["fit_anchor"],
            case["output_size"],
            case["canvas_size"],
            case["target_size"],
            case["is_center"],
            case["align_factor"],
            case["pad_to_max"],
        )
        case["expected"] = result
        vectors.append(case)

    return vectors


# ---- clamp_to_dims vectors ----
def generate_clamp_to_dims():
    vectors = []

    cases = [
        ("no_clamp", dims(1920, 1080), dims(3840, 2160)),
        ("clamp_both", dims(3840, 2160), dims(1920, 1080)),
        ("clamp_width_only", dims(3840, 1080), dims(1920, 2160)),
        ("clamp_height_only", dims(1920, 2160), dims(3840, 1080)),
        ("exact_match", dims(1920, 1080), dims(1920, 1080)),
    ]

    for label, d, clamp in cases:
        result_dims, delta = d.clamp_to_dims(clamp)
        vectors.append(
            {
                "label": label,
                "dims": ser_dims(d),
                "clamp_dims": ser_dims(clamp),
                "expected_dims": ser_dims(result_dims),
                "expected_delta": {"x": delta.x, "y": delta.y},
            }
        )

    return vectors


def main():
    all_vectors = {
        "description": "FDL Pipeline helper function golden vectors",
        "version": "1.0",
        "scale_factor": generate_scale_factor(),
        "output_size": generate_output_size(),
        "alignment_shift": generate_alignment_shift(),
        "clamp_to_dims": generate_clamp_to_dims(),
    }

    output_path = "pipeline_vectors.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_vectors, f, indent=2)
    print(f"Generated {output_path}")

    total = 0
    for key, val in all_vectors.items():
        if isinstance(val, list):
            total += len(val)
            print(f"  {key}: {len(val)} vectors")
    print(f"Total: {total} vectors")


if __name__ == "__main__":
    main()
