#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bridge script: apply FDL image transform using OpenImageIO.

Called by the Node.js web viewer server via child_process.
Accepts JSON on stdin, outputs JSON on stdout.
"""

from __future__ import annotations

import json
import sys

from fdl import (
    CanvasTemplate,
    DimensionsInt,
    FitMethod,
    GeometryPath,
    HAlign,
    RoundStrategy,
    RoundingEven,
    RoundingMode,
    VAlign,
    read_from_string,
    ATTR_CONTENT_TRANSLATION,
    ATTR_SCALED_BOUNDING_BOX,
)
from fdl_imaging import transform_image_with_computed_values


GEOMETRY_PATH_MAP: dict[str, GeometryPath] = {
    "canvas.dimensions": GeometryPath.CANVAS_DIMENSIONS,
    "canvas.effective_dimensions": GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
    "framing_decision.dimensions": GeometryPath.FRAMING_DIMENSIONS,
    "framing_decision.protection_dimensions": GeometryPath.FRAMING_PROTECTION_DIMENSIONS,
}

FIT_METHOD_MAP: dict[str, FitMethod] = {
    "width": FitMethod.WIDTH,
    "height": FitMethod.HEIGHT,
    "fit_all": FitMethod.FIT_ALL,
    "fill": FitMethod.FILL,
}

H_ALIGN_MAP: dict[str, HAlign] = {
    "left": HAlign.LEFT,
    "center": HAlign.CENTER,
    "right": HAlign.RIGHT,
}

V_ALIGN_MAP: dict[str, VAlign] = {
    "top": VAlign.TOP,
    "center": VAlign.CENTER,
    "bottom": VAlign.BOTTOM,
}

ROUND_EVEN_MAP: dict[str, RoundingEven] = {
    "whole": RoundingEven.WHOLE,
    "even": RoundingEven.EVEN,
}

ROUND_MODE_MAP: dict[str, RoundingMode] = {
    "up": RoundingMode.UP,
    "down": RoundingMode.DOWN,
    "round": RoundingMode.ROUND,
}


def main() -> None:
    params = json.loads(sys.stdin.read())

    source_fdl_json: str = params["sourceFdlJson"]
    context_label: str = params["contextLabel"]
    canvas_id: str = params["canvasId"]
    framing_id: str = params["framingId"]
    tpl: dict = params["template"]
    input_path: str = params["inputImagePath"]
    output_path: str = params["outputImagePath"]

    # Parse source FDL
    fdl = read_from_string(source_fdl_json)

    # Find source canvas and framing
    source_canvas = None
    source_framing = None
    for ctx in fdl.contexts:
        if ctx.label == context_label:
            for c in ctx.canvases:
                if c.id == canvas_id:
                    source_canvas = c
                    for fd in c.framing_decisions:
                        if fd.id == framing_id:
                            source_framing = fd
                            break
                    break
            break

    if source_canvas is None:
        raise ValueError(f"Canvas '{canvas_id}' not found in context '{context_label}'")
    if source_framing is None:
        raise ValueError(f"Framing '{framing_id}' not found in canvas '{canvas_id}'")

    # Build CanvasTemplate from params
    preserve = GEOMETRY_PATH_MAP.get(tpl.get("preserveFromSourceCanvas") or "") if tpl.get("preserveFromSourceCanvas") else None
    max_dims = None
    if tpl.get("maximumDimensions"):
        max_dims = DimensionsInt(width=tpl["maximumDimensions"]["width"], height=tpl["maximumDimensions"]["height"])

    template = CanvasTemplate(
        id="web_template",
        label="Web Viewer Template",
        target_dimensions=DimensionsInt(width=tpl["targetWidth"], height=tpl["targetHeight"]),
        target_anamorphic_squeeze=float(tpl.get("targetAnamorphicSqueeze", 1.0)),
        fit_source=GEOMETRY_PATH_MAP.get(tpl["fitSource"], GeometryPath.FRAMING_DIMENSIONS),
        fit_method=FIT_METHOD_MAP.get(tpl["fitMethod"], FitMethod.FIT_ALL),
        alignment_method_horizontal=H_ALIGN_MAP.get(tpl.get("alignmentMethodHorizontal", "center"), HAlign.CENTER),
        alignment_method_vertical=V_ALIGN_MAP.get(tpl.get("alignmentMethodVertical", "center"), VAlign.CENTER),
        round=RoundStrategy(
            even=ROUND_EVEN_MAP.get(tpl.get("roundEven", "even"), RoundingEven.EVEN),
            mode=ROUND_MODE_MAP.get(tpl.get("roundMode", "up"), RoundingMode.UP),
        ),
        preserve_from_source_canvas=preserve,
        maximum_dimensions=max_dims,
        pad_to_maximum=bool(tpl.get("padToMaximum", False)),
    )

    # Apply template
    result = template.apply(
        source_canvas,
        source_framing,
        f"{canvas_id}_output",
        f"{framing_id}_output",
        source_context_label=context_label,
    )

    new_canvas = result.canvas
    scaled_bb = new_canvas.get_custom_attr(ATTR_SCALED_BOUNDING_BOX)
    content_tr = new_canvas.get_custom_attr(ATTR_CONTENT_TRANSLATION)

    # Transform the image
    transform_image_with_computed_values(
        input_path=input_path,
        output_path=output_path,
        source_canvas=source_canvas,
        source_framing=source_framing,
        template=template,
        new_canvas=new_canvas,
        scaled_bounding_box=scaled_bb,
        content_translation=content_tr,
    )

    # Read output dimensions
    from OpenImageIO import ImageBuf

    out_buf = ImageBuf(output_path)
    out_spec = out_buf.spec()

    print(
        json.dumps(
            {
                "success": True,
                "width": out_spec.width,
                "height": out_spec.height,
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
