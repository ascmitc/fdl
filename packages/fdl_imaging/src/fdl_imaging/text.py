# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Text rendering utilities using OpenImageIO.

This module provides functions for rendering dimension labels, anchor point
coordinates, and custom text annotations onto image buffers.

When an anamorphic squeeze compensation factor (``squeeze_comp``) is supplied
and differs from 1.0, text is rendered into a temporary RGBA buffer, resized
horizontally by *squeeze_comp*, then alpha-composited onto the destination.
This mirrors the treatment applied to crosshairs, arrows, circles and all
other geometric overlays so that every element appears geometrically correct
once the image is de-squeezed for viewing.
"""

from enum import Enum

from fdl.fdl_types import DimensionsFloat, PointFloat
from OpenImageIO import ImageBuf, ImageBufAlgo

from fdl_imaging.colors import RGBA

# Default text color (black)
COLOR_TEXT: RGBA = (0.0, 0.0, 0.0, 1.0)


class TextAlignment(Enum):
    """Text alignment options."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlignment(Enum):
    """Vertical alignment options."""

    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_rgba(color: RGBA) -> tuple[float, float, float, float]:
    """Return *color* as a 4-component RGBA tuple."""
    if len(color) >= 4:
        return (color[0], color[1], color[2], color[3])
    return (color[0], color[1], color[2], 1.0)


def _squeeze_composite_text(
    buf: ImageBuf,
    tmp: ImageBuf,
    baseline_x: int,
    baseline_y: int,
    target_x: int,
    target_y: int,
    squeeze_comp: float,
) -> None:
    """Resize *tmp* horizontally by *squeeze_comp* and alpha-composite onto *buf*.

    Parameters
    ----------
    buf : ImageBuf
        Destination image buffer.
    tmp : ImageBuf
        Temporary RGBA buffer containing the rendered text.
    baseline_x, baseline_y : int
        Text baseline position inside *tmp* (before resize).
    target_x, target_y : int
        Desired text baseline position on *buf* (after alignment adjustment).
    squeeze_comp : float
        Horizontal scale factor (1.0 / anamorphic_squeeze).
    """
    from OpenImageIO import ROI

    tmp_w = tmp.spec().width
    tmp_h = tmp.spec().height
    new_w = max(1, int(tmp_w * squeeze_comp))

    stretched = ImageBuf()
    ImageBufAlgo.resize(stretched, tmp, roi=ROI(0, new_w, 0, tmp_h, 0, 1, 0, tmp.nchannels))

    paste_x = int(target_x - baseline_x * squeeze_comp)
    paste_y = int(target_y - baseline_y)

    buf_w = buf.spec().width
    buf_h = buf.spec().height

    for py in range(tmp_h):
        dy = paste_y + py
        if dy < 0 or dy >= buf_h:
            continue
        for px in range(new_w):
            dx = paste_x + px
            if dx < 0 or dx >= buf_w:
                continue

            src = stretched.getpixel(px, py)
            if src is None or len(src) < 4 or src[3] < 0.01:
                continue

            dst = list(buf.getpixel(dx, dy))
            if dst is None:
                continue

            alpha = src[3]
            for c in range(min(3, len(dst))):
                dst[c] = src[c] * alpha + dst[c] * (1.0 - alpha)

            buf.setpixel(dx, dy, tuple(dst))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_text_size(
    text: str,
    font_size: int,
    font_path: str | None = None,
) -> tuple[int, int]:
    """
    Get the dimensions of text without rendering it.

    Parameters
    ----------
    text : str
        The text string to measure
    font_size : int
        Font size in pixels
    font_path : str, optional
        Path to a TrueType font file. If None, uses system default.

    Returns
    -------
    Tuple[int, int]
        The (width, height) of the text bounding box
    """
    try:
        # Try to use OIIO's text_size function for accurate measurement
        font_name = font_path if font_path else ""
        roi = ImageBufAlgo.text_size(text, font_size, font_name)
        if roi and roi.width > 0:
            return (roi.width, roi.height)
    except (AttributeError, TypeError):
        # text_size might not be available in all OIIO versions
        pass

    # Fallback to estimation
    estimated_width = len(text) * font_size * 0.55
    estimated_height = font_size
    return (int(estimated_width), int(estimated_height))


def render_text(
    buf: ImageBuf,
    text: str,
    x: int,
    y: int,
    font_size: int,
    color: RGBA = COLOR_TEXT,
    font_path: str | None = None,
    alignment: TextAlignment = TextAlignment.LEFT,
    vertical_alignment: VerticalAlignment = VerticalAlignment.TOP,
    squeeze_comp: float = 1.0,
) -> tuple[int, int]:
    """
    Render text onto an image buffer.

    Parameters
    ----------
    buf : ImageBuf
        The image buffer to draw on
    text : str
        The text string to render
    x : int
        X coordinate for text placement
    y : int
        Y coordinate for text placement
    font_size : int
        Font size in pixels
    color : RGBA, optional
        Text color as (r, g, b, a) tuple
    font_path : str, optional
        Path to a TrueType font file. If None, uses system default.
    alignment : TextAlignment, optional
        Horizontal text alignment relative to x coordinate
    vertical_alignment : VerticalAlignment, optional
        Vertical text alignment relative to y coordinate
    squeeze_comp : float, optional
        Squeeze compensation factor (1.0 / anamorphic_squeeze).  When not 1.0
        the text is rendered into a temporary buffer, resized horizontally by
        this factor, and alpha-composited onto *buf*.

    Returns
    -------
    Tuple[int, int]
        The (width, height) of the rendered text bounding box
    """
    # Get accurate text dimensions for alignment
    text_width, text_height = get_text_size(text, font_size, font_path)

    # Effective width after squeeze compensation
    needs_squeeze = abs(squeeze_comp - 1.0) > 0.001
    eff_width = int(text_width * squeeze_comp) if needs_squeeze else text_width

    # Adjust x based on horizontal alignment (using effective width)
    if alignment == TextAlignment.CENTER:
        x = int(x - eff_width / 2)
    elif alignment == TextAlignment.RIGHT:
        x = int(x - eff_width)

    # Adjust y based on vertical alignment
    # OIIO render_text uses baseline, so we need to adjust
    if vertical_alignment == VerticalAlignment.TOP:
        y = y + font_size  # Move down by font size to position at top
    elif vertical_alignment == VerticalAlignment.MIDDLE:
        y = int(y + font_size / 2)
    # BOTTOM is the default baseline behavior

    if not needs_squeeze:
        # Direct render (existing fast path)
        font_name = font_path if font_path else ""
        ImageBufAlgo.render_text(buf, x, y, text, font_size, font_name, color)
    else:
        # Render to temp buffer, squeeze, composite
        from OpenImageIO import ImageSpec, TypeDesc

        pad = font_size
        tmp_w = text_width + 2 * pad
        tmp_h = font_size * 3

        spec = ImageSpec(tmp_w, tmp_h, 4, TypeDesc("float"))
        tmp = ImageBuf(spec)
        ImageBufAlgo.fill(tmp, (0.0, 0.0, 0.0, 0.0))

        color_rgba = _ensure_rgba(color)
        font_name = font_path or ""
        ImageBufAlgo.render_text(tmp, pad, pad + font_size, text, font_size, font_name, color_rgba)

        _squeeze_composite_text(buf, tmp, pad, pad + font_size, x, y, squeeze_comp)

    return (eff_width, text_height)


def render_dimension_label(
    buf: ImageBuf,
    width: float,
    height: float,
    x: int,
    y: int,
    font_size: int,
    color: RGBA = COLOR_TEXT,
    font_path: str | None = None,
    alignment: TextAlignment = TextAlignment.CENTER,
) -> tuple[int, int]:
    """
    Render a dimension label (e.g., "1920 x 1080") onto an image buffer.

    Parameters
    ----------
    buf : ImageBuf
        The image buffer to draw on
    width : float
        The width value to display
    height : float
        The height value to display
    x : int
        X coordinate for label placement
    y : int
        Y coordinate for label placement
    font_size : int
        Font size in pixels
    color : RGBA, optional
        Text color
    font_path : str, optional
        Path to a TrueType font file
    alignment : TextAlignment, optional
        Text alignment

    Returns
    -------
    Tuple[int, int]
        The (width, height) of the rendered text bounding box
    """
    text = DimensionsFloat(width=width, height=height).format()
    return render_text(buf, text, x, y, font_size, color, font_path, alignment)


def render_anchor_label(
    buf: ImageBuf,
    anchor_x: float,
    anchor_y: float,
    x: int,
    y: int,
    font_size: int,
    color: RGBA = COLOR_TEXT,
    font_path: str | None = None,
    alignment: TextAlignment = TextAlignment.LEFT,
) -> tuple[int, int]:
    """
    Render an anchor point label (e.g., "(100, 200)") onto an image buffer.

    Parameters
    ----------
    buf : ImageBuf
        The image buffer to draw on
    anchor_x : float
        The x anchor coordinate to display
    anchor_y : float
        The y anchor coordinate to display
    x : int
        X coordinate for label placement
    y : int
        Y coordinate for label placement
    font_size : int
        Font size in pixels
    color : RGBA, optional
        Text color
    font_path : str, optional
        Path to a TrueType font file
    alignment : TextAlignment, optional
        Text alignment

    Returns
    -------
    Tuple[int, int]
        The (width, height) of the rendered text bounding box
    """
    text = PointFloat(x=anchor_x, y=anchor_y).format()
    return render_text(buf, text, x, y, font_size, color, font_path, alignment)


def render_text_bold(
    buf: ImageBuf,
    text: str,
    x: int,
    y: int,
    font_size: int,
    color: RGBA = COLOR_TEXT,
    font_path: str | None = None,
    alignment: TextAlignment = TextAlignment.LEFT,
    vertical_alignment: VerticalAlignment = VerticalAlignment.TOP,
    squeeze_comp: float = 1.0,
) -> tuple[int, int]:
    """
    Render bold text onto an image buffer by drawing multiple offset copies.

    Parameters
    ----------
    buf : ImageBuf
        The image buffer to draw on
    text : str
        The text string to render
    x : int
        X coordinate for text placement
    y : int
        Y coordinate for text placement
    font_size : int
        Font size in pixels
    color : RGBA, optional
        Text color as (r, g, b, a) tuple
    font_path : str, optional
        Path to a TrueType font file. If None, uses system default.
    alignment : TextAlignment, optional
        Horizontal text alignment relative to x coordinate
    vertical_alignment : VerticalAlignment, optional
        Vertical text alignment relative to y coordinate
    squeeze_comp : float, optional
        Squeeze compensation factor (1.0 / anamorphic_squeeze).

    Returns
    -------
    Tuple[int, int]
        The (width, height) of the rendered text bounding box
    """
    # Render multiple copies with slight offsets to simulate bold
    # The offset amount scales with font size
    offset = max(1, font_size // 24)

    offsets = [
        (0, 0),
        (offset, 0),
        (0, offset),
        (offset, offset),
    ]

    needs_squeeze = abs(squeeze_comp - 1.0) > 0.001

    if not needs_squeeze:
        # Fast path: render directly (existing behaviour)
        result = (0, 0)
        for dx, dy in offsets:
            result = render_text(buf, text, x + dx, y + dy, font_size, color, font_path, alignment, vertical_alignment)
        return result

    # ---- Squeeze path: render all bold copies into ONE temp buffer, ----
    # ---- then squeeze + composite once for efficiency.               ----
    from OpenImageIO import ImageSpec, TypeDesc

    text_width, text_height = get_text_size(text, font_size, font_path)
    eff_width = int(text_width * squeeze_comp)

    # Alignment adjustments (done once, not per-offset)
    target_x = x
    if alignment == TextAlignment.CENTER:
        target_x = int(x - eff_width / 2)
    elif alignment == TextAlignment.RIGHT:
        target_x = int(x - eff_width)

    target_y = y
    if vertical_alignment == VerticalAlignment.TOP:
        target_y = y + font_size
    elif vertical_alignment == VerticalAlignment.MIDDLE:
        target_y = int(y + font_size / 2)

    # Temp buffer — extra room for bold offsets
    pad = font_size
    tmp_w = text_width + 2 * pad + offset
    tmp_h = font_size * 3 + offset

    spec = ImageSpec(tmp_w, tmp_h, 4, TypeDesc("float"))
    tmp = ImageBuf(spec)
    ImageBufAlgo.fill(tmp, (0.0, 0.0, 0.0, 0.0))

    color_rgba = _ensure_rgba(color)
    font_name = font_path or ""

    for dx, dy in offsets:
        ImageBufAlgo.render_text(tmp, pad + dx, pad + font_size + dy, text, font_size, font_name, color_rgba)

    _squeeze_composite_text(buf, tmp, pad, pad + font_size, target_x, target_y, squeeze_comp)

    return (eff_width, text_height)


def render_squeeze_label(
    buf: ImageBuf,
    squeeze_factor: float,
    x: int,
    y: int,
    font_size: int,
    color: RGBA = COLOR_TEXT,
    font_path: str | None = None,
    alignment: TextAlignment = TextAlignment.CENTER,
    squeeze_comp: float = 1.0,
) -> tuple[int, int]:
    """
    Render an anamorphic squeeze factor label.

    Parameters
    ----------
    buf : ImageBuf
        The image buffer to draw on
    squeeze_factor : float
        The anamorphic squeeze factor
    x : int
        X coordinate for label placement
    y : int
        Y coordinate for label placement
    font_size : int
        Font size in pixels
    color : RGBA, optional
        Text color
    font_path : str, optional
        Path to a TrueType font file
    alignment : TextAlignment, optional
        Text alignment
    squeeze_comp : float, optional
        Squeeze compensation factor (1.0 / anamorphic_squeeze).

    Returns
    -------
    Tuple[int, int]
        The (width, height) of the rendered text bounding box
    """
    if squeeze_factor == 1.0:
        text = "Spherical (1.0x)"
    else:
        text = f"Squeeze: {squeeze_factor:.2f}x"

    return render_text(buf, text, x, y, font_size, color, font_path, alignment, squeeze_comp=squeeze_comp)
