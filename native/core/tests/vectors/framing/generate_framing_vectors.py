# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Generate golden vectors for fdl_compute_framing_from_intent."""

import json
import sys

sys.path.insert(0, "../../../../../packages/fdl/src")

from fdl.canvas import Canvas
from fdl.config import set_rounding
from fdl.framingdecision import FramingDecision
from fdl.framingintent import FramingIntent
from fdl.rounding import RoundStrategy
from fdl.fdl_types import DimensionsInt, PointFloat


def make_vector(label, canvas, fi, rounding):
    """Generate a single test vector."""
    # Set global rounding (used by from_framing_intent internally)
    set_rounding(rounding)

    fd = FramingDecision.from_framing_intent(canvas, fi)

    # Determine what working dims were used
    working_dims = canvas.effective_dimensions or canvas.dimensions

    return {
        "label": label,
        "canvas_dims": {"width": canvas.dimensions.width, "height": canvas.dimensions.height},
        "working_dims": {"width": float(working_dims.width), "height": float(working_dims.height)},
        "squeeze": canvas.anamorphic_squeeze,
        "aspect_ratio": {"width": fi.aspect_ratio.width, "height": fi.aspect_ratio.height},
        "protection": fi.protection,
        "rounding": {"even": rounding.even, "mode": rounding.mode},
        "expected": {
            "dimensions": {"width": fd.dimensions.width, "height": fd.dimensions.height},
            "anchor_point": {"x": fd.anchor_point.x, "y": fd.anchor_point.y},
            "has_protection": fd.protection_dimensions is not None,
            "protection_dimensions": (
                {"width": fd.protection_dimensions.width, "height": fd.protection_dimensions.height}
                if fd.protection_dimensions
                else {"width": 0.0, "height": 0.0}
            ),
            "protection_anchor_point": (
                {"x": fd.protection_anchor_point.x, "y": fd.protection_anchor_point.y}
                if fd.protection_anchor_point
                else {"x": 0.0, "y": 0.0}
            ),
        },
    }


vectors = []

# --- Wider framing intent (letterbox), no protection ---
canvas1 = Canvas(
    id="CVS_1",
    source_canvas_id="CVS_1",
    dimensions=DimensionsInt(width=4096, height=2160),
    anamorphic_squeeze=1.0,
)
fi_239 = FramingIntent(id="FI_239", label="2.39:1", aspect_ratio=DimensionsInt(width=239, height=100), protection=0.0)
rnd_even_up = RoundStrategy(even="even", mode="up")
vectors.append(make_vector("letterbox_no_protection_even_up", canvas1, fi_239, rnd_even_up))

# --- Wider intent, with protection ---
fi_239p = FramingIntent(id="FI_239P", label="2.39:1+prot", aspect_ratio=DimensionsInt(width=239, height=100), protection=0.1)
vectors.append(make_vector("letterbox_with_protection", canvas1, fi_239p, rnd_even_up))

# --- Narrower intent (pillarbox), no protection ---
fi_133 = FramingIntent(id="FI_133", label="1.33:1", aspect_ratio=DimensionsInt(width=133, height=100), protection=0.0)
vectors.append(make_vector("pillarbox_no_protection", canvas1, fi_133, rnd_even_up))

# --- Narrower intent, with protection ---
fi_133p = FramingIntent(id="FI_133P", label="1.33:1+prot", aspect_ratio=DimensionsInt(width=133, height=100), protection=0.05)
vectors.append(make_vector("pillarbox_with_protection", canvas1, fi_133p, rnd_even_up))

# --- Square intent ---
fi_sq = FramingIntent(id="FI_SQ", label="1:1", aspect_ratio=DimensionsInt(width=1, height=1), protection=0.0)
vectors.append(make_vector("square_intent", canvas1, fi_sq, rnd_even_up))

# --- Anamorphic canvas ---
canvas_ana = Canvas(
    id="CVS_ANA",
    source_canvas_id="CVS_ANA",
    dimensions=DimensionsInt(width=4096, height=3432),
    anamorphic_squeeze=2.0,
)
vectors.append(make_vector("anamorphic_canvas", canvas_ana, fi_239, rnd_even_up))

# --- Canvas with effective dimensions ---
canvas_eff = Canvas(
    id="CVS_EFF",
    source_canvas_id="CVS_EFF",
    dimensions=DimensionsInt(width=5184, height=4320),
    effective_dimensions=DimensionsInt(width=4096, height=2160),
    effective_anchor_point=PointFloat(x=544.0, y=1080.0),
    anamorphic_squeeze=1.0,
)
vectors.append(make_vector("effective_dims_letterbox", canvas_eff, fi_239, rnd_even_up))

# --- 16:9 intent in 16:9 canvas (exact match) ---
fi_178 = FramingIntent(id="FI_178", label="1.78:1", aspect_ratio=DimensionsInt(width=16, height=9), protection=0.0)
canvas_hd = Canvas(
    id="CVS_HD",
    source_canvas_id="CVS_HD",
    dimensions=DimensionsInt(width=1920, height=1080),
    anamorphic_squeeze=1.0,
)
vectors.append(make_vector("exact_match_16_9", canvas_hd, fi_178, rnd_even_up))

# --- Whole/round rounding ---
rnd_whole_round = RoundStrategy(even="whole", mode="round")
vectors.append(make_vector("letterbox_whole_round", canvas1, fi_239, rnd_whole_round))

# --- Even/down rounding ---
rnd_even_down = RoundStrategy(even="even", mode="down")
vectors.append(make_vector("letterbox_even_down", canvas1, fi_239, rnd_even_down))

# --- High protection factor ---
fi_high_prot = FramingIntent(id="FI_HIGH_P", label="2.39:1+50%", aspect_ratio=DimensionsInt(width=239, height=100), protection=0.5)
vectors.append(make_vector("high_protection_factor", canvas1, fi_high_prot, rnd_even_up))

result = {"description": "from_framing_intent golden vectors", "version": "1.0", "vectors": vectors}

output_path = "from_intent_vectors.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Generated {len(vectors)} vectors to {output_path}")
