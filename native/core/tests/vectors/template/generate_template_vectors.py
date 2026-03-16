# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Generate golden vectors for fdl_apply_canvas_template end-to-end tests."""

import json
import sys

sys.path.insert(0, "../../../../../packages/fdl/src")

from fdl.canvas import Canvas
from fdl.canvastemplate import CanvasTemplate
from fdl.config import set_rounding
from fdl.context import Context
from fdl.framingdecision import FramingDecision
from fdl.rounding import RoundStrategy
from fdl.fdl_types import DimensionsFloat, DimensionsInt, PointFloat


def make_vector(label, tmpl, source_canvas, source_framing, source_context=None, context_creator=None, new_fd_name=""):
    """Generate a single end-to-end test vector."""
    # Set global rounding to match template
    rnd = tmpl.round
    set_rounding(rnd)

    result = tmpl.apply(
        source_canvas=source_canvas,
        source_framing=source_framing,
        new_fd_name=new_fd_name,
        source_context=source_context,
        context_creator=context_creator,
    )

    # The output FDL context has source canvas at [0] and new canvas at [1]
    out_ctx = result.fdl.contexts[0]
    out_new_canvas = out_ctx.canvases[1]
    out_fd = out_new_canvas.framing_decisions[0]

    return {
        "label": label,
        # Source canvas (inline JSON)
        "source_canvas": {
            "id": source_canvas.id,
            "label": source_canvas.label,
            "source_canvas_id": source_canvas.source_canvas_id,
            "dimensions": {"width": source_canvas.dimensions.width, "height": source_canvas.dimensions.height},
            "effective_dimensions": (
                {"width": source_canvas.effective_dimensions.width, "height": source_canvas.effective_dimensions.height}
                if source_canvas.effective_dimensions
                else None
            ),
            "effective_anchor_point": (
                {"x": source_canvas.effective_anchor_point.x, "y": source_canvas.effective_anchor_point.y}
                if source_canvas.effective_anchor_point
                else None
            ),
            "anamorphic_squeeze": source_canvas.anamorphic_squeeze,
        },
        # Source framing decision (inline JSON)
        "source_framing": {
            "id": source_framing.id,
            "label": source_framing.label,
            "framing_intent_id": source_framing.framing_intent_id,
            "dimensions": {"width": source_framing.dimensions.width, "height": source_framing.dimensions.height},
            "anchor_point": {"x": source_framing.anchor_point.x, "y": source_framing.anchor_point.y},
            "protection_dimensions": (
                {"width": source_framing.protection_dimensions.width, "height": source_framing.protection_dimensions.height}
                if source_framing.protection_dimensions
                else None
            ),
            "protection_anchor_point": (
                {"x": source_framing.protection_anchor_point.x, "y": source_framing.protection_anchor_point.y}
                if source_framing.protection_anchor_point
                else None
            ),
        },
        # Template config (inline JSON)
        "template": {
            "id": tmpl.id,
            "label": tmpl.label,
            "target_dimensions": {"width": tmpl.target_dimensions.width, "height": tmpl.target_dimensions.height},
            "target_anamorphic_squeeze": tmpl.target_anamorphic_squeeze,
            "fit_source": tmpl.fit_source,
            "fit_method": tmpl.fit_method,
            "alignment_method_horizontal": tmpl.alignment_method_horizontal,
            "alignment_method_vertical": tmpl.alignment_method_vertical,
            "preserve_from_source_canvas": tmpl.preserve_from_source_canvas,
            "has_maximum_dimensions": tmpl.maximum_dimensions is not None,
            "maximum_dimensions": (
                {"width": tmpl.maximum_dimensions.width, "height": tmpl.maximum_dimensions.height} if tmpl.maximum_dimensions else None
            ),
            "pad_to_maximum": tmpl.pad_to_maximum,
            "round": {"even": tmpl.round.even, "mode": tmpl.round.mode},
        },
        "new_fd_name": new_fd_name,
        "context_creator": context_creator,
        "source_context_label": source_context.label if source_context else None,
        # Expected outputs
        "expected": {
            "scale_factor": out_new_canvas.get_custom_attr("scale_factor"),
            "scaled_bounding_box": {
                "width": out_new_canvas.get_custom_attr("scaled_bounding_box").width,
                "height": out_new_canvas.get_custom_attr("scaled_bounding_box").height,
            },
            "content_translation": {
                "x": out_new_canvas.get_custom_attr("content_translation").x,
                "y": out_new_canvas.get_custom_attr("content_translation").y,
            },
            # Output canvas geometry
            "output_canvas_dims": {
                "width": float(out_new_canvas.dimensions.width),
                "height": float(out_new_canvas.dimensions.height),
            },
            "output_effective_dims": {
                "width": float(out_new_canvas.effective_dimensions.width),
                "height": float(out_new_canvas.effective_dimensions.height),
            }
            if out_new_canvas.effective_dimensions
            else None,
            "output_effective_anchor": {
                "x": out_new_canvas.effective_anchor_point.x,
                "y": out_new_canvas.effective_anchor_point.y,
            }
            if out_new_canvas.effective_anchor_point
            else None,
            "output_fd_dims": {
                "width": out_fd.dimensions.width,
                "height": out_fd.dimensions.height,
            },
            "output_fd_anchor": {
                "x": out_fd.anchor_point.x,
                "y": out_fd.anchor_point.y,
            },
            "output_has_protection": out_fd.protection_dimensions is not None,
            "output_protection_dims": (
                {"width": out_fd.protection_dimensions.width, "height": out_fd.protection_dimensions.height}
                if out_fd.protection_dimensions
                else None
            ),
            "output_protection_anchor": (
                {"x": out_fd.protection_anchor_point.x, "y": out_fd.protection_anchor_point.y} if out_fd.protection_anchor_point else None
            ),
        },
    }


vectors = []

# --- Scenario 1: Simple width fit, framing.dimensions as fit_source ---
canvas1 = Canvas(
    id="CVS_OCF",
    source_canvas_id="CVS_OCF",
    label="OCF",
    dimensions=DimensionsInt(width=4096, height=2160),
    anamorphic_squeeze=1.0,
)
fd1 = FramingDecision(
    id="CVS_OCF-FI_239",
    label="2.39:1",
    framing_intent_id="FI_239",
    dimensions=DimensionsFloat(width=4096.0, height=1714.0),
    anchor_point=PointFloat(x=0.0, y=223.0),
)
tmpl_hd = CanvasTemplate(
    id="CT_HD",
    label="HD",
    target_dimensions=DimensionsInt(width=1920, height=1080),
    target_anamorphic_squeeze=1.0,
    fit_source="framing_decision.dimensions",
    fit_method="width",
    alignment_method_horizontal="center",
    alignment_method_vertical="center",
    round=RoundStrategy(even="even", mode="up"),
)
ctx1 = Context(label="Camera A")
vectors.append(
    make_vector("width_fit_framing_dims", tmpl_hd, canvas1, fd1, source_context=ctx1, context_creator="test", new_fd_name="2.39:1")
)

# --- Scenario 2: fit_all, canvas.dimensions as fit_source ---
tmpl_uhd = CanvasTemplate(
    id="CT_UHD",
    label="UHD",
    target_dimensions=DimensionsInt(width=3840, height=2160),
    target_anamorphic_squeeze=1.0,
    fit_source="canvas.dimensions",
    fit_method="fit_all",
    alignment_method_horizontal="center",
    alignment_method_vertical="center",
    round=RoundStrategy(even="even", mode="up"),
)
vectors.append(
    make_vector("fit_all_canvas_dims", tmpl_uhd, canvas1, fd1, source_context=ctx1, context_creator="test", new_fd_name="2.39:1")
)

# --- Scenario 3: With effective dimensions ---
canvas_eff = Canvas(
    id="CVS_EFF",
    source_canvas_id="CVS_EFF",
    label="OCF with effective",
    dimensions=DimensionsInt(width=5184, height=4320),
    effective_dimensions=DimensionsInt(width=4096, height=2160),
    effective_anchor_point=PointFloat(x=544.0, y=1080.0),
    anamorphic_squeeze=1.0,
)
fd_eff = FramingDecision(
    id="CVS_EFF-FI_239",
    label="2.39:1",
    framing_intent_id="FI_239",
    dimensions=DimensionsFloat(width=4096.0, height=1714.0),
    anchor_point=PointFloat(x=544.0, y=1303.0),
)
tmpl_eff = CanvasTemplate(
    id="CT_EFF",
    label="HD from effective",
    target_dimensions=DimensionsInt(width=1920, height=1080),
    target_anamorphic_squeeze=1.0,
    fit_source="framing_decision.dimensions",
    fit_method="width",
    preserve_from_source_canvas="canvas.effective_dimensions",
    alignment_method_horizontal="center",
    alignment_method_vertical="center",
    round=RoundStrategy(even="even", mode="up"),
)
vectors.append(
    make_vector("effective_dims_preserve", tmpl_eff, canvas_eff, fd_eff, source_context=ctx1, context_creator="test", new_fd_name="2.39:1")
)

# --- Scenario 4: With maximum dimensions and padding ---
tmpl_max_pad = CanvasTemplate(
    id="CT_PAD",
    label="HD padded",
    target_dimensions=DimensionsInt(width=1920, height=1080),
    target_anamorphic_squeeze=1.0,
    fit_source="framing_decision.dimensions",
    fit_method="width",
    alignment_method_horizontal="center",
    alignment_method_vertical="center",
    maximum_dimensions=DimensionsInt(width=1920, height=1080),
    pad_to_maximum=True,
    round=RoundStrategy(even="even", mode="up"),
)
vectors.append(
    make_vector("max_dims_with_padding", tmpl_max_pad, canvas1, fd1, source_context=ctx1, context_creator="test", new_fd_name="2.39:1")
)

# --- Scenario 5: Anamorphic source ---
canvas_ana = Canvas(
    id="CVS_ANA",
    source_canvas_id="CVS_ANA",
    label="Anamorphic",
    dimensions=DimensionsInt(width=4096, height=3432),
    anamorphic_squeeze=2.0,
)
fd_ana = FramingDecision(
    id="CVS_ANA-FI_239",
    label="2.39:1",
    framing_intent_id="FI_239",
    dimensions=DimensionsFloat(width=4096.0, height=1714.0),
    anchor_point=PointFloat(x=0.0, y=859.0),
)
vectors.append(
    make_vector("anamorphic_source", tmpl_hd, canvas_ana, fd_ana, source_context=ctx1, context_creator="test", new_fd_name="2.39:1")
)

# --- Scenario 6: Height fit ---
tmpl_height = CanvasTemplate(
    id="CT_H",
    label="Height fit",
    target_dimensions=DimensionsInt(width=1920, height=1080),
    target_anamorphic_squeeze=1.0,
    fit_source="framing_decision.dimensions",
    fit_method="height",
    alignment_method_horizontal="center",
    alignment_method_vertical="center",
    round=RoundStrategy(even="even", mode="up"),
)
vectors.append(make_vector("height_fit", tmpl_height, canvas1, fd1, source_context=ctx1, context_creator="test", new_fd_name="2.39:1"))

# --- Scenario 7: Fill fit (crop) ---
tmpl_fill = CanvasTemplate(
    id="CT_FILL",
    label="Fill fit",
    target_dimensions=DimensionsInt(width=1920, height=1080),
    target_anamorphic_squeeze=1.0,
    fit_source="framing_decision.dimensions",
    fit_method="fill",
    alignment_method_horizontal="center",
    alignment_method_vertical="center",
    round=RoundStrategy(even="even", mode="up"),
)
vectors.append(make_vector("fill_fit_crop", tmpl_fill, canvas1, fd1, source_context=ctx1, context_creator="test", new_fd_name="2.39:1"))

# --- Scenario 8: With protection dims ---
fd_prot = FramingDecision(
    id="CVS_OCF-FI_239P",
    label="2.39:1+prot",
    framing_intent_id="FI_239",
    dimensions=DimensionsFloat(width=3686.4, height=1542.68),
    anchor_point=PointFloat(x=204.8, y=308.66),
    protection_dimensions=DimensionsFloat(width=4096.0, height=1714.0),
    protection_anchor_point=PointFloat(x=0.0, y=223.0),
)
vectors.append(make_vector("with_protection", tmpl_hd, canvas1, fd_prot, source_context=ctx1, context_creator="test", new_fd_name="2.39:1"))

# --- Scenario 9: Non-center alignment (left/top) ---
tmpl_lt = CanvasTemplate(
    id="CT_LT",
    label="Left/Top",
    target_dimensions=DimensionsInt(width=1920, height=1080),
    target_anamorphic_squeeze=1.0,
    fit_source="framing_decision.dimensions",
    fit_method="width",
    alignment_method_horizontal="left",
    alignment_method_vertical="top",
    maximum_dimensions=DimensionsInt(width=1920, height=1080),
    pad_to_maximum=True,
    round=RoundStrategy(even="even", mode="up"),
)
vectors.append(make_vector("left_top_alignment", tmpl_lt, canvas1, fd1, source_context=ctx1, context_creator="test", new_fd_name="2.39:1"))

# --- Scenario 10: Non-center alignment (right/bottom) ---
tmpl_rb = CanvasTemplate(
    id="CT_RB",
    label="Right/Bottom",
    target_dimensions=DimensionsInt(width=1920, height=1080),
    target_anamorphic_squeeze=1.0,
    fit_source="framing_decision.dimensions",
    fit_method="width",
    alignment_method_horizontal="right",
    alignment_method_vertical="bottom",
    maximum_dimensions=DimensionsInt(width=1920, height=1080),
    pad_to_maximum=True,
    round=RoundStrategy(even="even", mode="up"),
)
vectors.append(
    make_vector("right_bottom_alignment", tmpl_rb, canvas1, fd1, source_context=ctx1, context_creator="test", new_fd_name="2.39:1")
)

result = {"description": "Canvas template apply() end-to-end golden vectors", "version": "1.0", "vectors": vectors}

output_path = "template_vectors.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Generated {len(vectors)} vectors to {output_path}")
