# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Image processing module using OpenImageIO for FDL-based transformations.

This module provides functions to process images according to FDL (Framing Decision List)
specifications, applying transformations such as cropping, resizing, and extraction.

Note: This module operates on raster image data.  SVG (vector) output is not
supported — use the frameline generator's SVG backend for vector output.
"""

from pathlib import Path

from fdl import (
    FDL,
    Canvas,
    Context,
    FramingDecision,
    find_by_id,
    find_by_label,
    get_anchor_from_path,
    get_dimensions_from_path,
    read_from_file,
)
from OpenImageIO import HALF, ROI, ImageBuf, ImageBufAlgo, ImageSpec

#: File extensions that require raster (pixel) data and cannot be SVG.
_VECTOR_ONLY_EXTENSIONS = {".svg"}


def _check_raster_output(output_path: Path) -> None:
    """Raise ValueError if the output format is vector-only (e.g. SVG)."""
    if output_path.suffix.lower() in _VECTOR_ONLY_EXTENSIONS:
        raise ValueError(
            f"Cannot write raster image data to vector format '{output_path.suffix}'. "
            "Use a raster format (.exr, .png, .tiff, etc.) for pixel-level transforms, "
            "or use the frameline generator's SVG backend for vector output."
        )


def get_fdl_components(
    fdl: FDL,
    context_id: str,
    canvas_id: str,
    framing_decision_id: str,
) -> tuple[Context, Canvas, FramingDecision]:
    """
    Extract context, canvas, and framing decision from an FDL using IDs.

    Parameters
    ----------
    fdl : FDL
        The FDL object to search in
    context_id : str
        The context label (contexts use label as identifier)
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
    # Context uses label as identifier
    context = find_by_label(fdl.contexts, context_id)
    if context is None:
        raise ValueError(f"No context with label '{context_id}'")

    # Find canvas by ID
    canvas = find_by_id(context.canvases, canvas_id)
    if canvas is None:
        raise ValueError(f"No canvas with id '{canvas_id}' in context '{context_id}'")

    # Find framing decision by ID
    framing_decision = find_by_id(canvas.framing_decisions, framing_decision_id)
    if framing_decision is None:
        raise ValueError(f"Canvas '{canvas.label}' (id: {canvas_id}) lacks framing decision with id '{framing_decision_id}'")

    return context, canvas, framing_decision


def process_image_with_fdl(
    input_path: str | Path,
    output_path: str | Path,
    fdl: str | Path | FDL,
    context_id: str,
    canvas_id: str,
    framing_decision_id: str,
    use_protection: bool = True,
    filter_name: str = "lanczos3",
) -> bool:
    """
    Process an image according to FDL specifications.

    This function loads an image, applies the transformations defined in the FDL
    (crop to framing decision or protection dimensions), and writes the result
    to the output path while preserving the input file format.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image file
    output_path : str or Path
        Path where the processed image will be saved
    fdl : str, Path, or FDL
        The FDL file path or FDL object containing framing decisions
    context_id : str
        The context label to use
    canvas_id : str
        The canvas ID to use
    framing_decision_id : str
        The framing decision ID to use
    use_protection : bool, optional
        If True, crop to protection dimensions; if False, crop to framing decision dimensions.
        Default is True.
    filter_name : str, optional
        The filter to use for resizing operations. Default is "lanczos3".

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

    # Load FDL if needed
    if isinstance(fdl, str | Path):
        fdl = read_from_file(fdl)

    # Get FDL components
    _context, canvas, framing_decision = get_fdl_components(fdl, context_id, canvas_id, framing_decision_id)

    # Load the input image
    input_buf = ImageBuf(str(input_path))
    if input_buf.has_error:
        raise OSError(f"Failed to read input image: {input_buf.geterror()}")

    # Verify input dimensions match canvas dimensions
    input_spec = input_buf.spec()
    input_width = input_spec.width
    input_height = input_spec.height

    if input_width != canvas.dimensions.width or input_height != canvas.dimensions.height:
        raise ValueError(
            f"Input image dimensions ({input_width}x{input_height}) do not match "
            f"canvas dimensions ({canvas.dimensions.width}x{canvas.dimensions.height})"
        )

    # Determine crop region based on protection or framing decision
    if use_protection and framing_decision.protection_dimensions:
        crop_width = int(framing_decision.protection_dimensions.width)
        crop_height = int(framing_decision.protection_dimensions.height)
        anchor_x = int(framing_decision.protection_anchor_point.x) if framing_decision.protection_anchor_point else 0
        anchor_y = int(framing_decision.protection_anchor_point.y) if framing_decision.protection_anchor_point else 0
    else:
        crop_width = int(framing_decision.dimensions.width)
        crop_height = int(framing_decision.dimensions.height)
        anchor_x = int(framing_decision.anchor_point.x)
        anchor_y = int(framing_decision.anchor_point.y)

    # FDL and OIIO both use top-left origin with y increasing downward
    # ROI: (xbegin, xend, ybegin, yend)
    roi = ROI(
        anchor_x,  # xbegin
        anchor_x + crop_width,  # xend
        anchor_y,  # ybegin
        anchor_y + crop_height,  # yend
    )

    # Cut the image (cut resets origin to 0,0 unlike crop which preserves offset)
    cropped_buf = ImageBuf()
    ImageBufAlgo.cut(cropped_buf, input_buf, roi)

    if cropped_buf.has_error:
        raise OSError(f"Failed to cut image: {cropped_buf.geterror()}")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the output image, preserving format from input
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
    context_id: str,
    canvas_id: str,
    framing_decision_id: str,
    filter_name: str = "lanczos3",
) -> bool:
    """
    Process an image according to FDL template specifications.

    This function loads an image, applies the template transformations to derive
    a new canvas, and writes the result to the output path.

    The workflow matches the Nuke importer logic:
    1. Crop to preserve/fit dimensions from source
    2. Scale (distort) to scaled_bounding_box dimensions (the "biggest canvas")
    3. Apply content_translation for alignment (if not zero)
    4. Format to output canvas dimensions (center if no translation)

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
    context_id : str
        The context label to use
    canvas_id : str
        The canvas ID to use
    framing_decision_id : str
        The framing decision ID to use
    filter_name : str, optional
        The filter to use for resizing operations. Default is "lanczos3".

    Returns
    -------
    bool
        True if processing succeeded, False otherwise
    """
    _check_raster_output(Path(output_path))

    # Load FDLs if needed
    if isinstance(source_fdl, str | Path):
        source_fdl = read_from_file(source_fdl)
    if isinstance(template_fdl, str | Path):
        template_fdl = read_from_file(template_fdl)

    # Get source FDL components
    context, canvas, framing_decision = get_fdl_components(source_fdl, context_id, canvas_id, framing_decision_id)

    # Find template
    template = find_by_id(template_fdl.canvas_templates, template_id)
    if template is None:
        raise ValueError(f"Template with id '{template_id}' not found")

    # Apply template to get computed values
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

    # Read computed values from canvas custom attrs
    from fdl import ATTR_CONTENT_TRANSLATION, ATTR_SCALED_BOUNDING_BOX

    # Delegate to the core transformation function
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
    context_id: str,
    canvas_id: str,
    framing_decision_id: str,
    output_width: int | None = None,
    output_height: int | None = None,
    filter_name: str = "lanczos3",
) -> bool:
    """
    Extract the framing decision region from an image and optionally resize.

    This extracts just the framing decision area (the blue rectangle in visualizations)
    and optionally resizes it to specified dimensions.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image file
    output_path : str or Path
        Path where the processed image will be saved
    fdl : str, Path, or FDL
        The FDL file path or FDL object
    context_id : str
        The context label to use
    canvas_id : str
        The canvas ID to use
    framing_decision_id : str
        The framing decision ID to use
    output_width : int, optional
        Desired output width. If None, uses framing decision width.
    output_height : int, optional
        Desired output height. If None, uses framing decision height.
    filter_name : str, optional
        The filter to use for resizing. Default is "lanczos3".

    Returns
    -------
    bool
        True if processing succeeded, False otherwise
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    _check_raster_output(output_path)

    # Load FDL if needed
    if isinstance(fdl, str | Path):
        fdl = read_from_file(fdl)

    # Get FDL components
    _context, _canvas, framing_decision = get_fdl_components(fdl, context_id, canvas_id, framing_decision_id)

    # Load the input image
    input_buf = ImageBuf(str(input_path))
    if input_buf.has_error:
        raise OSError(f"Failed to read input image: {input_buf.geterror()}")

    input_spec = input_buf.spec()

    # Get framing decision dimensions and anchor
    fd_width = int(framing_decision.dimensions.width)
    fd_height = int(framing_decision.dimensions.height)
    anchor_x = int(framing_decision.anchor_point.x)
    anchor_y = int(framing_decision.anchor_point.y)

    # FDL and OIIO both use top-left origin with y increasing downward
    roi = ROI(
        anchor_x,
        anchor_x + fd_width,
        anchor_y,
        anchor_y + fd_height,
    )

    # Cut to framing decision region (cut resets origin to 0,0 unlike crop)
    cropped_buf = ImageBuf()
    ImageBufAlgo.cut(cropped_buf, input_buf, roi)

    if cropped_buf.has_error:
        raise OSError(f"Failed to cut image: {cropped_buf.geterror()}")

    # Resize if output dimensions specified
    if output_width is not None or output_height is not None:
        final_width = output_width if output_width is not None else fd_width
        final_height = output_height if output_height is not None else fd_height

        output_spec = ImageSpec(final_width, final_height, input_spec.nchannels, input_spec.format)
        resized_buf = ImageBuf(output_spec)

        ImageBufAlgo.resize(resized_buf, cropped_buf, filtername=filter_name)

        if resized_buf.has_error:
            raise OSError(f"Failed to resize image: {resized_buf.geterror()}")

        output_buf = resized_buf
    else:
        output_buf = cropped_buf

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the output
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
    Transform an image using pre-computed FDL template values.

    This function applies the same transformation as process_image_with_fdl_template
    but uses pre-computed values from apply_fdl_template, avoiding redundant computation.

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
        The filter to use for resizing operations. Default is "lanczos3".

    Returns
    -------
    bool
        True if processing succeeded, False otherwise
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    _check_raster_output(output_path)

    # Load the input image
    input_buf = ImageBuf(str(input_path))
    if input_buf.has_error:
        raise OSError(f"Failed to read input image: {input_buf.geterror()}")

    input_spec = input_buf.spec()
    input_width = input_spec.width
    input_height = input_spec.height

    # Verify input dimensions match source canvas dimensions
    if input_width != source_canvas.dimensions.width or input_height != source_canvas.dimensions.height:
        raise ValueError(
            f"Input image dimensions ({input_width}x{input_height}) do not match "
            f"canvas dimensions ({source_canvas.dimensions.width}x{source_canvas.dimensions.height})"
        )

    # Step 1: Get the region to extract from source based on template preserve_from_source_canvas
    preserve_path = template.preserve_from_source_canvas
    if not preserve_path:
        preserve_path = template.fit_source

    preserve_dims = get_dimensions_from_path(source_canvas, source_framing, preserve_path)
    preserve_anchor = get_anchor_from_path(source_canvas, source_framing, preserve_path)

    # Crop to the preserve dimensions from source
    crop_width = int(preserve_dims.width)
    crop_height = int(preserve_dims.height)
    anchor_x = int(preserve_anchor.x)
    anchor_y = int(preserve_anchor.y)

    # FDL and OIIO both use top-left origin with y increasing downward
    roi = ROI(
        anchor_x,
        anchor_x + crop_width,
        anchor_y,
        anchor_y + crop_height,
    )

    # Cut the source region
    cropped_buf = ImageBuf()
    ImageBufAlgo.cut(cropped_buf, input_buf, roi)

    if cropped_buf.has_error:
        raise OSError(f"Failed to cut image: {cropped_buf.geterror()}")

    # Step 2: Scale to scaled_bounding_box dimensions
    scale_width = int(scaled_bounding_box.width)
    scale_height = int(scaled_bounding_box.height)

    scale_spec = ImageSpec(scale_width, scale_height, input_spec.nchannels, input_spec.format)
    scaled_buf = ImageBuf(scale_spec)

    ImageBufAlgo.resize(scaled_buf, cropped_buf, filtername=filter_name)

    if scaled_buf.has_error:
        raise OSError(f"Failed to scale image: {scaled_buf.geterror()}")

    # Step 3 & 4: Apply content_translation and format to output canvas
    final_width = int(new_canvas.dimensions.width)
    final_height = int(new_canvas.dimensions.height)

    # Create final canvas with black background
    final_spec = ImageSpec(final_width, final_height, input_spec.nchannels, input_spec.format)
    final_buf = ImageBuf(final_spec)
    ImageBufAlgo.zero(final_buf)

    # Calculate position for placing the scaled content
    if content_translation.is_zero():
        # Center the content
        offset_x = 0
        offset_y = 0
    else:
        # Apply content translation as absolute position
        # FDL and OIIO both use top-left origin with Y increasing downward
        offset_x = int(content_translation.x)
        offset_y = int(content_translation.y)

    # Paste the scaled image at the calculated position
    ImageBufAlgo.paste(final_buf, offset_x, offset_y, 0, 0, scaled_buf)

    if final_buf.has_error:
        raise OSError(f"Failed to create output image: {final_buf.geterror()}")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the output image (use half precision for EXR)
    if output_path.suffix.lower() == ".exr":
        final_buf.set_write_format(HALF)
    final_buf.write(str(output_path))

    if final_buf.has_error:
        raise OSError(f"Failed to write output image: {final_buf.geterror()}")

    return True
