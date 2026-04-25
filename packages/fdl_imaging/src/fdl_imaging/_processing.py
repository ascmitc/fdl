# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Image processing module using OpenImageIO for FDL-based transformations.

This module provides functions to process images according to FDL (Framing
Decision List) specifications, applying transformations such as cropping,
resizing, and extraction.

Float-precision pipeline
------------------------
Per the FDL spec, framing and protection dimensions / anchors are float.
Rather than truncating them to integers at the OIIO boundary (which loses
sub-pixel alignment), this module uses :func:`OpenImageIO.ImageBufAlgo.warp`
to carry float source coordinates through the filter kernel.  Output buffers
must still be sized as integers; widths and heights are rounded up with
``math.ceil`` to match the frameline generator's display convention (every
sub-pixel of a region is preserved in the output; the last column/row may be
a partial sample filtered against ``wrap="black"``).

Fast path for integer-aligned crops
-----------------------------------
When the anchor and dimensions are already whole pixels, a plain
``ImageBufAlgo.cut`` is used instead of ``warp``.  ``cut`` is a memcpy-style
pixel copy that avoids the reconstruction filter entirely, so pixel-perfect
sources (v1 FDLs, templates that produce integer geometry) are bit-preserving
through the pipeline and do not incur a spurious lanczos pass.

Note: This module operates on raster image data.  SVG (vector) output is not
supported — use the frameline generator's SVG backend for vector output.
"""

import math
from pathlib import Path

from fdl import (
    FDL,
    Canvas,
    Context,
    FramingDecision,
    find_by_id,
    get_anchor_from_path,
    get_dimensions_from_path,
    read_from_file,
)
from OpenImageIO import HALF, ROI, ImageBuf, ImageBufAlgo, ImageSpec

#: File extensions that require raster (pixel) data and cannot be SVG.
_VECTOR_ONLY_EXTENSIONS = {".svg"}

#: Tolerance (in pixels) for treating a float coordinate as integer-aligned.
#: Half an ULP of a 4K dimension is ~1e-12, but canvas template math can drift
#: by 1e-9 due to float division; 1e-6 is comfortably below "visible" and well
#: above numerical noise.
_INT_ALIGNMENT_TOL = 1e-6


def _check_raster_output(output_path: Path) -> None:
    """Raise ValueError if the output format is vector-only (e.g. SVG)."""
    if output_path.suffix.lower() in _VECTOR_ONLY_EXTENSIONS:
        raise ValueError(
            f"Cannot write raster image data to vector format '{output_path.suffix}'. "
            "Use a raster format (.exr, .png, .tiff, etc.) for pixel-level transforms, "
            "or use the frameline generator's SVG backend for vector output."
        )


def _is_integer_aligned(*values: float) -> bool:
    """True if every value is within ``_INT_ALIGNMENT_TOL`` of an integer."""
    return all(abs(v - round(v)) < _INT_ALIGNMENT_TOL for v in values)


def _warp_matrix(
    anchor_x: float,
    anchor_y: float,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    translate_x: float = 0.0,
    translate_y: float = 0.0,
) -> tuple[float, float, float, float, float, float, float, float, float]:
    """
    Build a column-major 3x3 matrix for ``ImageBufAlgo.warp``.

    OIIO's ``warp`` takes ``M`` as an ``Imath::M33f`` (column-major) where the
    transform is applied as ``v_dst = v_src · M`` (row-vector on the left,
    src → dst direction).  This helper composes a pure crop+scale+translate
    chain in that space:

    .. code-block:: text

        dst_x = scale_x * (src_x - anchor_x) + translate_x
        dst_y = scale_y * (src_y - anchor_y) + translate_y

    Returned as a flat 9-tuple in column-major order (OIIO accepts
    tuple/list/numpy; tuple keeps this module free of numpy as a runtime dep).

    Parameters
    ----------
    anchor_x, anchor_y : float
        Source anchor point to place at the output origin (post-translate).
    scale_x, scale_y : float, optional
        Axis scale factors (1.0 = no scale).  Defaults to 1.0.
    translate_x, translate_y : float, optional
        Output-space translation applied after scale (e.g. content_translation
        or a paste offset).  Defaults to 0.0.
    """
    # Column 0: (sx, 0, -sx*ax + tx)
    # Column 1: (0, sy, -sy*ay + ty)
    # Column 2: (0, 0, 1)
    # Flat column-major: col0 || col1 || col2.
    return (
        scale_x,
        0.0,
        0.0,
        0.0,
        scale_y,
        0.0,
        -scale_x * anchor_x + translate_x,
        -scale_y * anchor_y + translate_y,
        1.0,
    )


def _warp_crop(
    src: ImageBuf,
    src_spec: ImageSpec,
    anchor_x: float,
    anchor_y: float,
    crop_width: float,
    crop_height: float,
    filter_name: str,
) -> ImageBuf:
    """
    Crop ``src`` to a region defined by float anchor and dimensions.

    If the region is integer-aligned, uses :func:`ImageBufAlgo.cut` (lossless
    pixel copy; identical output to the pre-warp implementation).  Otherwise
    uses :func:`ImageBufAlgo.warp` with the configured reconstruction filter,
    which filters the sub-pixel source offset into the integer output grid.
    Output size is ``ceil(crop_width) x ceil(crop_height)`` so that every
    sub-pixel of the region is preserved in the raster (matches the frameline
    generator's display convention).

    Raises
    ------
    OSError
        If OIIO fails the cut or warp.
    """
    out_width = math.ceil(crop_width)
    out_height = math.ceil(crop_height)

    if _is_integer_aligned(anchor_x, anchor_y, crop_width, crop_height):
        ax_i = round(anchor_x)
        ay_i = round(anchor_y)
        roi = ROI(ax_i, ax_i + out_width, ay_i, ay_i + out_height)
        dst = ImageBuf()
        ImageBufAlgo.cut(dst, src, roi)
        if dst.has_error:
            raise OSError(f"Failed to cut image: {dst.geterror()}")
        return dst

    M = _warp_matrix(anchor_x=anchor_x, anchor_y=anchor_y)
    dst_spec = ImageSpec(out_width, out_height, src_spec.nchannels, src_spec.format)
    dst = ImageBuf(dst_spec)
    ImageBufAlgo.warp(dst, src, M, filtername=filter_name, wrap="black")
    if dst.has_error:
        raise OSError(f"Failed to warp image: {dst.geterror()}")
    return dst


def _warp_compose(
    src: ImageBuf,
    src_spec: ImageSpec,
    anchor_x: float,
    anchor_y: float,
    crop_width: float,
    crop_height: float,
    scale_width: float,
    scale_height: float,
    final_width: int,
    final_height: int,
    offset_x: float,
    offset_y: float,
    filter_name: str,
) -> ImageBuf:
    """
    Single-pass crop + scale + translate (paste) via one ``warp`` call.

    Replaces the three-step ``cut → resize → paste`` pipeline with a single
    reconstruction-filter pass.  This eliminates two intermediate filter
    roundings and keeps float source coordinates precise end-to-end.

    Parameters
    ----------
    src : ImageBuf
        Source image.
    src_spec : ImageSpec
        Spec of ``src`` (captured once to avoid repeated ``.spec()`` calls).
    anchor_x, anchor_y : float
        Source anchor of the region to preserve (top-left of the crop).
    crop_width, crop_height : float
        Float dimensions of the source region to preserve.  Used only to
        compute the scale factor; the actual area read is determined by
        the output grid size and the filter footprint.
    scale_width, scale_height : float
        Target dimensions of the scaled (resized) content.  May be float; the
        scale factor is ``scale_dim / crop_dim`` and is applied in float.
    final_width, final_height : int
        Size of the output canvas (``new_canvas.dimensions``, already int).
    offset_x, offset_y : float
        Output-space translation to place the scaled content (``0, 0`` to
        center at origin; otherwise ``content_translation``).
    filter_name : str
        Reconstruction filter (``"lanczos3"``, ``"triangle"``, etc.).

    Returns
    -------
    ImageBuf
        Output buffer of size ``final_width x final_height``, pixels outside
        the warped region filled with black (``wrap="black"``).
    """
    scale_x = scale_width / crop_width if crop_width != 0 else 1.0
    scale_y = scale_height / crop_height if crop_height != 0 else 1.0

    M = _warp_matrix(
        anchor_x=anchor_x,
        anchor_y=anchor_y,
        scale_x=scale_x,
        scale_y=scale_y,
        translate_x=offset_x,
        translate_y=offset_y,
    )
    dst_spec = ImageSpec(final_width, final_height, src_spec.nchannels, src_spec.format)
    dst = ImageBuf(dst_spec)
    ImageBufAlgo.warp(dst, src, M, filtername=filter_name, wrap="black")
    if dst.has_error:
        raise OSError(f"Failed to warp image: {dst.geterror()}")
    return dst


def get_fdl_components(
    fdl: FDL,
    context_index: int,
    canvas_id: str,
    framing_decision_id: str,
) -> tuple[Context, Canvas, FramingDecision]:
    """
    Extract context, canvas, and framing decision from an FDL using IDs.

    Parameters
    ----------
    fdl : FDL
        The FDL object to search in
    context_index : int
        The context index in the contexts array
    canvas_id : str
        The canvas ID to find
    framing_decision_id : str
        The framing decision ID to find

    Returns
    -------
    Tuple[Context, Canvas, FramingDecision]
        The resolved context, canvas, and framing decision

    Raises
    ------
    ValueError
        If any component is not found
    """
    contexts = fdl.contexts
    if context_index < 0 or context_index >= len(contexts):
        raise ValueError(f"Context index {context_index} out of range")
    context = contexts[context_index]

    canvas = find_by_id(context.canvases, canvas_id)
    if canvas is None:
        raise ValueError(f"No canvas with id '{canvas_id}' in context index {context_index}")

    framing_decision = find_by_id(canvas.framing_decisions, framing_decision_id)
    if framing_decision is None:
        raise ValueError(f"Canvas '{canvas.label}' (id: {canvas_id}) lacks framing decision with id '{framing_decision_id}'")

    return context, canvas, framing_decision


def process_image_with_fdl(
    input_path: str | Path,
    output_path: str | Path,
    fdl: str | Path | FDL,
    context_index: int,
    canvas_id: str,
    framing_decision_id: str,
    use_protection: bool = True,
    filter_name: str = "lanczos3",
) -> bool:
    """
    Process an image according to FDL specifications.

    Crops the source image to the protection (or framing) region defined by
    the FDL and writes the result to ``output_path``.  The crop uses
    :func:`_warp_crop`, which falls back to :func:`ImageBufAlgo.cut` when the
    FDL geometry is already integer-aligned (pixel-perfect, lossless) and
    engages :func:`ImageBufAlgo.warp` only when the anchor or dimensions
    carry sub-pixel offsets.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image file
    output_path : str or Path
        Path where the processed image will be saved
    fdl : str, Path, or FDL
        The FDL file path or FDL object containing framing decisions
    context_index : int
        The context index in the contexts array
    canvas_id : str
        The canvas ID to use
    framing_decision_id : str
        The framing decision ID to use
    use_protection : bool, optional
        If True, crop to protection dimensions; if False, crop to framing decision dimensions.
        Default is True.
    filter_name : str, optional
        The reconstruction filter to use for any required sub-pixel warp.
        Integer-aligned crops bypass filtering entirely.  Default is "lanczos3".

    Returns
    -------
    bool
        True if processing succeeded, False otherwise

    Raises
    ------
    ValueError
        If the FDL components cannot be found or image dimensions don't match
    IOError
        If the input image cannot be read or output cannot be written
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    _check_raster_output(output_path)

    if isinstance(fdl, str | Path):
        fdl = read_from_file(fdl)

    _context, canvas, framing_decision = get_fdl_components(fdl, context_index, canvas_id, framing_decision_id)

    input_buf = ImageBuf(str(input_path))
    if input_buf.has_error:
        raise OSError(f"Failed to read input image: {input_buf.geterror()}")

    input_spec = input_buf.spec()
    input_width = input_spec.width
    input_height = input_spec.height

    if input_width != canvas.dimensions.width or input_height != canvas.dimensions.height:
        raise ValueError(
            f"Input image dimensions ({input_width}x{input_height}) do not match "
            f"canvas dimensions ({canvas.dimensions.width}x{canvas.dimensions.height})"
        )

    if use_protection and framing_decision.protection_dimensions:
        crop_width = float(framing_decision.protection_dimensions.width)
        crop_height = float(framing_decision.protection_dimensions.height)
        anchor_x = float(framing_decision.protection_anchor_point.x) if framing_decision.protection_anchor_point else 0.0
        anchor_y = float(framing_decision.protection_anchor_point.y) if framing_decision.protection_anchor_point else 0.0
    else:
        crop_width = float(framing_decision.dimensions.width)
        crop_height = float(framing_decision.dimensions.height)
        anchor_x = float(framing_decision.anchor_point.x)
        anchor_y = float(framing_decision.anchor_point.y)

    cropped_buf = _warp_crop(
        src=input_buf,
        src_spec=input_spec,
        anchor_x=anchor_x,
        anchor_y=anchor_y,
        crop_width=crop_width,
        crop_height=crop_height,
        filter_name=filter_name,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cropped_buf.write(str(output_path))
    if cropped_buf.has_error:
        raise OSError(f"Failed to write output image: {cropped_buf.geterror()}")

    return True


def process_image_with_fdl_template(
    input_path: str | Path,
    output_path: str | Path,
    source_fdl: str | Path | FDL,
    template_fdl: str | Path | FDL,
    template_id: str,
    context_index: int,
    canvas_id: str,
    framing_decision_id: str,
    filter_name: str = "lanczos3",
) -> bool:
    """
    Process an image according to FDL template specifications.

    Applies the canvas template to derive the new canvas (and associated
    scaled bounding box + content translation), then transforms the source
    image in a single ``warp`` pass:

    1. Crop to the template's ``preserve_from_source_canvas`` region.
    2. Scale that region to the scaled bounding box.
    3. Translate by ``content_translation`` into the output canvas.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image file
    output_path : str or Path
        Path where the processed image will be saved
    source_fdl : str, Path, or FDL
        The source FDL file path or object
    template_fdl : str, Path, or FDL
        The template FDL file path or object containing canvas templates
    template_id : str
        The template ID to use
    context_index : int
        The context index in the contexts array
    canvas_id : str
        The canvas ID to use
    framing_decision_id : str
        The framing decision ID to use
    filter_name : str, optional
        The reconstruction filter to use.  Default is "lanczos3".

    Returns
    -------
    bool
        True if processing succeeded, False otherwise
    """
    _check_raster_output(Path(output_path))

    if isinstance(source_fdl, str | Path):
        source_fdl = read_from_file(source_fdl)
    if isinstance(template_fdl, str | Path):
        template_fdl = read_from_file(template_fdl)

    context, canvas, framing_decision = get_fdl_components(source_fdl, context_index, canvas_id, framing_decision_id)

    template = find_by_id(template_fdl.canvas_templates, template_id)
    if template is None:
        raise ValueError(f"Template with id '{template_id}' not found")

    import uuid as _uuid

    new_canvas_id = _uuid.uuid4().hex[:30]
    result = template.apply(
        source_canvas=canvas,
        source_framing=framing_decision,
        new_canvas_id=new_canvas_id,
        new_fd_name="",
        source_context_label=context.label,
        context_creator=context.context_creator,
    )

    from fdl import ATTR_CONTENT_TRANSLATION, ATTR_SCALED_BOUNDING_BOX

    return transform_image_with_computed_values(
        input_path=input_path,
        output_path=output_path,
        source_canvas=canvas,
        source_framing=framing_decision,
        template=template,
        new_canvas=result.canvas,
        scaled_bounding_box=result.canvas.get_custom_attr(ATTR_SCALED_BOUNDING_BOX),
        content_translation=result.canvas.get_custom_attr(ATTR_CONTENT_TRANSLATION),
        filter_name=filter_name,
    )


def extract_framing_region(
    input_path: str | Path,
    output_path: str | Path,
    fdl: str | Path | FDL,
    context_index: int,
    canvas_id: str,
    framing_decision_id: str,
    output_width: int | None = None,
    output_height: int | None = None,
    filter_name: str = "lanczos3",
) -> bool:
    """
    Extract the framing decision region from an image and optionally resize.

    Uses :func:`_warp_crop` for the crop (fast-path ``cut`` for integer
    geometry, ``warp`` for sub-pixel).  When ``output_width`` or
    ``output_height`` is provided, a second pass through ``ImageBufAlgo.resize``
    scales the crop to the requested size.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image file
    output_path : str or Path
        Path where the processed image will be saved
    fdl : str, Path, or FDL
        The FDL file path or FDL object
    context_index : int
        The context index in the contexts array
    canvas_id : str
        The canvas ID to use
    framing_decision_id : str
        The framing decision ID to use
    output_width : int, optional
        Desired output width. If None, uses framing decision width (ceil'd).
    output_height : int, optional
        Desired output height. If None, uses framing decision height (ceil'd).
    filter_name : str, optional
        The reconstruction filter to use. Default is "lanczos3".

    Returns
    -------
    bool
        True if processing succeeded, False otherwise
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    _check_raster_output(output_path)

    if isinstance(fdl, str | Path):
        fdl = read_from_file(fdl)

    _context, _canvas, framing_decision = get_fdl_components(fdl, context_index, canvas_id, framing_decision_id)

    input_buf = ImageBuf(str(input_path))
    if input_buf.has_error:
        raise OSError(f"Failed to read input image: {input_buf.geterror()}")

    input_spec = input_buf.spec()

    fd_width = float(framing_decision.dimensions.width)
    fd_height = float(framing_decision.dimensions.height)
    anchor_x = float(framing_decision.anchor_point.x)
    anchor_y = float(framing_decision.anchor_point.y)

    cropped_buf = _warp_crop(
        src=input_buf,
        src_spec=input_spec,
        anchor_x=anchor_x,
        anchor_y=anchor_y,
        crop_width=fd_width,
        crop_height=fd_height,
        filter_name=filter_name,
    )

    if output_width is not None or output_height is not None:
        final_width = output_width if output_width is not None else math.ceil(fd_width)
        final_height = output_height if output_height is not None else math.ceil(fd_height)

        output_spec = ImageSpec(final_width, final_height, input_spec.nchannels, input_spec.format)
        resized_buf = ImageBuf(output_spec)
        ImageBufAlgo.resize(resized_buf, cropped_buf, filtername=filter_name)
        if resized_buf.has_error:
            raise OSError(f"Failed to resize image: {resized_buf.geterror()}")

        output_buf = resized_buf
    else:
        output_buf = cropped_buf

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_buf.write(str(output_path))
    if output_buf.has_error:
        raise OSError(f"Failed to write output image: {output_buf.geterror()}")

    return True


def transform_image_with_computed_values(
    input_path: str | Path,
    output_path: str | Path,
    source_canvas: Canvas,
    source_framing: FramingDecision,
    template,
    new_canvas: Canvas,
    scaled_bounding_box,
    content_translation,
    filter_name: str = "lanczos3",
) -> bool:
    """
    Transform an image using pre-computed FDL template values in a single warp pass.

    Composes the three-step template pipeline (crop → scale → translate/paste)
    into one column-major 3x3 matrix and executes a single
    :func:`ImageBufAlgo.warp` call.  This eliminates two intermediate filter
    passes (``resize`` + ``paste``) and keeps the float ``preserve_anchor``,
    ``preserve_dims``, ``scaled_bounding_box`` and ``content_translation``
    precise end-to-end.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image file
    output_path : str or Path
        Path where the processed image will be saved
    source_canvas : Canvas
        The source canvas
    source_framing : FramingDecision
        The source framing decision
    template : CanvasTemplate
        The template with preserve_from_source_canvas path
    new_canvas : Canvas
        The output canvas (for output dimensions)
    scaled_bounding_box : DimensionsFloat
        The scaled bounding box dimensions (biggest canvas)
    content_translation : Point
        The content translation offset
    filter_name : str, optional
        The reconstruction filter to use.  Default is "lanczos3".

    Returns
    -------
    bool
        True if processing succeeded, False otherwise
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    _check_raster_output(output_path)

    input_buf = ImageBuf(str(input_path))
    if input_buf.has_error:
        raise OSError(f"Failed to read input image: {input_buf.geterror()}")

    input_spec = input_buf.spec()
    input_width = input_spec.width
    input_height = input_spec.height

    if input_width != source_canvas.dimensions.width or input_height != source_canvas.dimensions.height:
        raise ValueError(
            f"Input image dimensions ({input_width}x{input_height}) do not match "
            f"canvas dimensions ({source_canvas.dimensions.width}x{source_canvas.dimensions.height})"
        )

    preserve_path = template.preserve_from_source_canvas
    if not preserve_path:
        preserve_path = template.fit_source

    preserve_dims = get_dimensions_from_path(source_canvas, source_framing, preserve_path)
    preserve_anchor = get_anchor_from_path(source_canvas, source_framing, preserve_path)

    crop_width = float(preserve_dims.width)
    crop_height = float(preserve_dims.height)
    anchor_x = float(preserve_anchor.x)
    anchor_y = float(preserve_anchor.y)

    scale_width = float(scaled_bounding_box.width)
    scale_height = float(scaled_bounding_box.height)

    # new_canvas.dimensions is integer-typed post-round; cast defensively.
    final_width = int(new_canvas.dimensions.width)
    final_height = int(new_canvas.dimensions.height)

    # Output placement.  Historical behavior (pre-warp): when
    # content_translation is zero, the scaled content is pasted at origin
    # (0, 0); when non-zero, at int(content_translation).  Preserving this
    # verbatim — the docstring in the old code mentioned "center" but the
    # code pinned top-left.  Keep float translation for sub-pixel precision.
    if content_translation.is_zero():
        offset_x = 0.0
        offset_y = 0.0
    else:
        offset_x = float(content_translation.x)
        offset_y = float(content_translation.y)

    final_buf = _warp_compose(
        src=input_buf,
        src_spec=input_spec,
        anchor_x=anchor_x,
        anchor_y=anchor_y,
        crop_width=crop_width,
        crop_height=crop_height,
        scale_width=scale_width,
        scale_height=scale_height,
        final_width=final_width,
        final_height=final_height,
        offset_x=offset_x,
        offset_y=offset_y,
        filter_name=filter_name,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".exr":
        final_buf.set_write_format(HALF)
    final_buf.write(str(output_path))
    if final_buf.has_error:
        raise OSError(f"Failed to write output image: {final_buf.geterror()}")

    return True
