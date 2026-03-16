# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Drawing primitives using OpenImageIO.

This module provides low-level drawing functions for rectangles, lines,
arrows, triangles, and circles using OIIO's ImageBufAlgo operations.
"""

import math

from OpenImageIO import ROI, ImageBuf, ImageBufAlgo

from fdl_imaging.colors import DEFAULT_DASH_PATTERN, RGBA


def draw_filled_rect(
    buf: ImageBuf,
    x: int,
    y: int,
    width: int,
    height: int,
    color: RGBA,
) -> None:
    """
    Draw a filled rectangle on the image buffer.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    x : int
        X coordinate of the top-left corner.
    y : int
        Y coordinate of the top-left corner.
    width : int
        Width of the rectangle in pixels.
    height : int
        Height of the rectangle in pixels.
    color : RGBA
        Fill color as (r, g, b, a) tuple with values in [0.0, 1.0].
    """
    spec = buf.spec()
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(spec.width, x + width)
    y2 = min(spec.height, y + height)

    if x2 > x1 and y2 > y1:
        roi = ROI(x1, x2, y1, y2)
        ImageBufAlgo.fill(buf, color, roi=roi)


def draw_horizontal_line(
    buf: ImageBuf,
    x1: int,
    x2: int,
    y: int,
    thickness: int,
    color: RGBA,
    dashed: bool = False,
    dash_pattern: tuple[int, int] = DEFAULT_DASH_PATTERN,
) -> None:
    """
    Draw a horizontal line on the image buffer.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    x1 : int
        Starting X coordinate.
    x2 : int
        Ending X coordinate.
    y : int
        Y coordinate of the line.
    thickness : int
        Line thickness in pixels.
    color : RGBA
        Line color as (r, g, b, a) tuple.
    dashed : bool, optional
        If True, draw a dashed line. Default is False.
    dash_pattern : Tuple[int, int], optional
        Dash pattern as (on_pixels, off_pixels). Default is (10, 5).
    """
    if x1 > x2:
        x1, x2 = x2, x1

    half_thick = thickness // 2
    y_start = y - half_thick
    y_end = y + thickness - half_thick

    if not dashed:
        roi = ROI(x1, x2, y_start, y_end)
        ImageBufAlgo.fill(buf, color, roi=roi)
    else:
        dash_on, dash_off = dash_pattern
        x = x1
        while x < x2:
            dash_end = min(x + dash_on, x2)
            roi = ROI(x, dash_end, y_start, y_end)
            ImageBufAlgo.fill(buf, color, roi=roi)
            x += dash_on + dash_off


def draw_vertical_line(
    buf: ImageBuf,
    x: int,
    y1: int,
    y2: int,
    thickness: int,
    color: RGBA,
    dashed: bool = False,
    dash_pattern: tuple[int, int] = DEFAULT_DASH_PATTERN,
) -> None:
    """
    Draw a vertical line on the image buffer.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    x : int
        X coordinate of the line.
    y1 : int
        Starting Y coordinate.
    y2 : int
        Ending Y coordinate.
    thickness : int
        Line thickness in pixels.
    color : RGBA
        Line color as (r, g, b, a) tuple.
    dashed : bool, optional
        If True, draw a dashed line. Default is False.
    dash_pattern : Tuple[int, int], optional
        Dash pattern as (on_pixels, off_pixels). Default is (10, 5).
    """
    if y1 > y2:
        y1, y2 = y2, y1

    half_thick = thickness // 2
    x_start = x - half_thick
    x_end = x + thickness - half_thick

    if not dashed:
        roi = ROI(x_start, x_end, y1, y2)
        ImageBufAlgo.fill(buf, color, roi=roi)
    else:
        dash_on, dash_off = dash_pattern
        y = y1
        while y < y2:
            dash_end = min(y + dash_on, y2)
            roi = ROI(x_start, x_end, y, dash_end)
            ImageBufAlgo.fill(buf, color, roi=roi)
            y += dash_on + dash_off


def draw_rect_outline(
    buf: ImageBuf,
    x: int,
    y: int,
    width: int,
    height: int,
    thickness: int,
    color: RGBA,
    dashed: bool = False,
    dash_pattern: tuple[int, int] = DEFAULT_DASH_PATTERN,
) -> None:
    """
    Draw a rectangle outline on the image buffer.

    Rectangle bounds are [x, x+width) and [y, y+height), so the last
    pixel is at x+width-1 and y+height-1.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    x : int
        X coordinate of the top-left corner.
    y : int
        Y coordinate of the top-left corner.
    width : int
        Width of the rectangle in pixels.
    height : int
        Height of the rectangle in pixels.
    thickness : int
        Line thickness in pixels.
    color : RGBA
        Line color as (r, g, b, a) tuple.
    dashed : bool, optional
        If True, draw dashed lines. Default is False.
    dash_pattern : Tuple[int, int], optional
        Dash pattern as (on_pixels, off_pixels). Default is (10, 5).
    """
    # Top edge at y, from x to x+width-1
    draw_horizontal_line(buf, x, x + width - 1, y, thickness, color, dashed, dash_pattern)
    # Bottom edge at y+height-1, from x to x+width-1
    draw_horizontal_line(buf, x, x + width - 1, y + height - 1, thickness, color, dashed, dash_pattern)
    # Left edge at x, from y to y+height-1
    draw_vertical_line(buf, x, y, y + height - 1, thickness, color, dashed, dash_pattern)
    # Right edge at x+width-1, from y to y+height-1
    draw_vertical_line(buf, x + width - 1, y, y + height - 1, thickness, color, dashed, dash_pattern)


def draw_filled_triangle(
    buf: ImageBuf,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    x3: int,
    y3: int,
    color: RGBA,
) -> None:
    """
    Draw a filled triangle using scanline fill algorithm.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    x1 : int
        X coordinate of the first vertex.
    y1 : int
        Y coordinate of the first vertex.
    x2 : int
        X coordinate of the second vertex.
    y2 : int
        Y coordinate of the second vertex.
    x3 : int
        X coordinate of the third vertex.
    y3 : int
        Y coordinate of the third vertex.
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    """
    vertices = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda v: v[1])
    (vx1, vy1), (vx2, vy2), (vx3, vy3) = vertices

    def interpolate_x(y: int, xa: int, ya: int, xb: int, yb: int) -> float:
        if ya == yb:
            return xa
        return xa + (xb - xa) * (y - ya) / (yb - ya)

    height = buf.spec().height
    width = buf.spec().width

    for y in range(max(0, vy1), min(height, vy3 + 1)):
        x_intersects = []

        if vy1 != vy2 and vy1 <= y <= vy2:
            x_intersects.append(interpolate_x(y, vx1, vy1, vx2, vy2))
        if vy2 != vy3 and vy2 <= y <= vy3:
            x_intersects.append(interpolate_x(y, vx2, vy2, vx3, vy3))
        if vy1 != vy3 and vy1 <= y <= vy3:
            x_intersects.append(interpolate_x(y, vx1, vy1, vx3, vy3))

        if len(x_intersects) >= 2:
            x_min = int(max(0, min(x_intersects)))
            x_max = int(min(width, max(x_intersects) + 1))
            if x_min < x_max:
                roi = ROI(x_min, x_max, y, y + 1)
                ImageBufAlgo.fill(buf, color, roi=roi)


def draw_corner_triangle(
    buf: ImageBuf,
    corner_x: int,
    corner_y: int,
    size_x: int,
    size_y: int,
    corner: str,
    color: RGBA,
) -> None:
    """
    Draw a corner indicator triangle inside the rectangle, pointing outward.

    The triangle tip sits exactly at the corner.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    corner_x : int
        X coordinate of the corner.
    corner_y : int
        Y coordinate of the corner.
    size_x : int
        Size of the triangle along the X axis.
    size_y : int
        Size of the triangle along the Y axis.
    corner : str
        Which corner: "top_left", "top_right", "bottom_left", or "bottom_right".
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    """
    if corner == "top_left":
        draw_filled_triangle(buf, corner_x, corner_y, corner_x + size_x, corner_y, corner_x, corner_y + size_y, color)
    elif corner == "top_right":
        draw_filled_triangle(buf, corner_x, corner_y, corner_x - size_x, corner_y, corner_x, corner_y + size_y, color)
    elif corner == "bottom_left":
        draw_filled_triangle(buf, corner_x, corner_y, corner_x + size_x, corner_y, corner_x, corner_y - size_y, color)
    elif corner == "bottom_right":
        draw_filled_triangle(buf, corner_x, corner_y, corner_x - size_x, corner_y, corner_x, corner_y - size_y, color)


def draw_edge_arrow_inward(
    buf: ImageBuf,
    tip_x: int,
    tip_y: int,
    size_along: int,
    size_perp: int,
    edge: str,
    color: RGBA,
) -> None:
    """
    Draw an edge indicator arrow inside the rectangle, pointing outward toward the edge.

    The arrow tip sits exactly at the edge.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    tip_x : int
        X coordinate of the arrow tip.
    tip_y : int
        Y coordinate of the arrow tip.
    size_along : int
        Size of the arrow along the edge direction.
    size_perp : int
        Size of the arrow perpendicular to the edge.
    edge : str
        Which edge: "top", "bottom", "left", or "right".
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    """
    if edge == "top":
        draw_filled_triangle(buf, tip_x, tip_y, tip_x - size_along, tip_y + size_perp, tip_x + size_along, tip_y + size_perp, color)
    elif edge == "bottom":
        draw_filled_triangle(buf, tip_x, tip_y, tip_x - size_along, tip_y - size_perp, tip_x + size_along, tip_y - size_perp, color)
    elif edge == "left":
        draw_filled_triangle(buf, tip_x, tip_y, tip_x + size_perp, tip_y - size_along, tip_x + size_perp, tip_y + size_along, color)
    elif edge == "right":
        draw_filled_triangle(buf, tip_x, tip_y, tip_x - size_perp, tip_y - size_along, tip_x - size_perp, tip_y + size_along, color)


def draw_rect_corner_triangles(
    buf: ImageBuf,
    x: int,
    y: int,
    width: int,
    height: int,
    triangle_size_x: int,
    triangle_size_y: int,
    color: RGBA,
) -> None:
    """
    Draw corner indicator triangles for a rectangle.

    Rectangle bounds are [x, x+width) and [y, y+height), so the last
    pixel is at x+width-1 and y+height-1. Corner triangles sit exactly
    at the corner pixels.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    x : int
        X coordinate of the rectangle's top-left corner.
    y : int
        Y coordinate of the rectangle's top-left corner.
    width : int
        Width of the rectangle in pixels.
    height : int
        Height of the rectangle in pixels.
    triangle_size_x : int
        Size of the triangles along the X axis.
    triangle_size_y : int
        Size of the triangles along the Y axis.
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    """
    # Top-left corner is at (x, y)
    draw_corner_triangle(buf, x, y, triangle_size_x, triangle_size_y, "top_left", color)
    # Top-right corner is at (x + width - 1, y)
    draw_corner_triangle(buf, x + width - 1, y, triangle_size_x, triangle_size_y, "top_right", color)
    # Bottom-left corner is at (x, y + height - 1)
    draw_corner_triangle(buf, x, y + height - 1, triangle_size_x, triangle_size_y, "bottom_left", color)
    # Bottom-right corner is at (x + width - 1, y + height - 1)
    draw_corner_triangle(buf, x + width - 1, y + height - 1, triangle_size_x, triangle_size_y, "bottom_right", color)


def draw_rect_edge_arrows_single(
    buf: ImageBuf,
    x: int,
    y: int,
    width: int,
    height: int,
    arrow_size_along: int,
    arrow_size_perp: int,
    color: RGBA,
    offset: int = 0,
) -> None:
    """
    Draw 1 edge indicator arrow per side (4 total) at edge centers.

    Arrows are inside the rectangle, pointing outward. Rectangle bounds
    are [x, x+width) and [y, y+height), so the last pixel is at x+width-1
    and y+height-1. Arrow tips sit exactly at edge pixels.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    x : int
        X coordinate of the rectangle's top-left corner.
    y : int
        Y coordinate of the rectangle's top-left corner.
    width : int
        Width of the rectangle in pixels.
    height : int
        Height of the rectangle in pixels.
    arrow_size_along : int
        Size of the arrows along the edge direction.
    arrow_size_perp : int
        Size of the arrows perpendicular to the edge.
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    offset : int, optional
        Offset for arrow placement. Default is 0.
    """
    center_x = x + width // 2 + offset
    center_y = y + height // 2 + offset

    # Top edge at y
    draw_edge_arrow_inward(buf, center_x, y, arrow_size_along, arrow_size_perp, "top", color)
    # Bottom edge at y + height - 1 (last pixel row)
    draw_edge_arrow_inward(buf, center_x, y + height - 1, arrow_size_along, arrow_size_perp, "bottom", color)
    # Left edge at x
    draw_edge_arrow_inward(buf, x, center_y, arrow_size_perp, arrow_size_along, "left", color)
    # Right edge at x + width - 1 (last pixel column)
    draw_edge_arrow_inward(buf, x + width - 1, center_y, arrow_size_perp, arrow_size_along, "right", color)


def draw_single_edge_arrow(
    buf: ImageBuf,
    rect_x: int,
    rect_y: int,
    rect_w: int,
    rect_h: int,
    edge: str,
    arrow_size_along: int,
    arrow_size_perp: int,
    color: RGBA,
    edge_offset: int = 0,
) -> None:
    """
    Draw a single edge arrow at the midpoint of a specified edge.

    The arrow points outward from inside the rectangle toward the edge.
    An optional edge_offset slides the arrow along the edge axis (positive
    offset moves right/down, negative moves left/up).

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    rect_x : int
        X coordinate of the rectangle's top-left corner.
    rect_y : int
        Y coordinate of the rectangle's top-left corner.
    rect_w : int
        Width of the rectangle in pixels.
    rect_h : int
        Height of the rectangle in pixels.
    edge : str
        Which edge: "top", "bottom", "left", or "right".
    arrow_size_along : int
        Size of the arrow along the edge direction.
    arrow_size_perp : int
        Size of the arrow perpendicular to the edge.
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    edge_offset : int, optional
        Offset along the edge axis. For horizontal edges (top/bottom),
        positive moves right. For vertical edges (left/right), positive
        moves down. Default is 0.
    """
    center_x = rect_x + rect_w // 2
    center_y = rect_y + rect_h // 2

    if edge == "top":
        tip_x = center_x + edge_offset
        tip_y = rect_y
        draw_edge_arrow_inward(buf, tip_x, tip_y, arrow_size_along, arrow_size_perp, "top", color)
    elif edge == "bottom":
        tip_x = center_x + edge_offset
        tip_y = rect_y + rect_h - 1
        draw_edge_arrow_inward(buf, tip_x, tip_y, arrow_size_along, arrow_size_perp, "bottom", color)
    elif edge == "left":
        tip_x = rect_x
        tip_y = center_y + edge_offset
        draw_edge_arrow_inward(buf, tip_x, tip_y, arrow_size_perp, arrow_size_along, "left", color)
    elif edge == "right":
        tip_x = rect_x + rect_w - 1
        tip_y = center_y + edge_offset
        draw_edge_arrow_inward(buf, tip_x, tip_y, arrow_size_perp, arrow_size_along, "right", color)


def draw_circle(
    buf: ImageBuf,
    center_x: int,
    center_y: int,
    radius: int,
    thickness: int,
    color: RGBA,
    filled: bool = False,
) -> None:
    """
    Draw a circle outline or filled circle.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    center_x : int
        X coordinate of the circle center.
    center_y : int
        Y coordinate of the circle center.
    radius : int
        Radius of the circle in pixels.
    thickness : int
        Line thickness in pixels (for outline mode).
    color : RGBA
        Color as (r, g, b, a) tuple.
    filled : bool, optional
        If True, draw a filled circle. Default is False (outline only).
    """
    if filled:
        _draw_filled_circle(buf, center_x, center_y, radius, color)
    else:
        _draw_circle_outline(buf, center_x, center_y, radius, thickness, color)


def _draw_filled_circle(
    buf: ImageBuf,
    center_x: int,
    center_y: int,
    radius: int,
    color: RGBA,
) -> None:
    """
    Draw a filled circle using horizontal scanlines.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    center_x : int
        X coordinate of the circle center.
    center_y : int
        Y coordinate of the circle center.
    radius : int
        Radius of the circle in pixels.
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    """
    for dy in range(-radius, radius + 1):
        dx = int(math.sqrt(radius * radius - dy * dy))
        y = center_y + dy
        x1 = center_x - dx
        x2 = center_x + dx

        if 0 <= y < buf.spec().height:
            roi = ROI(max(0, x1), min(buf.spec().width, x2 + 1), y, y + 1)
            ImageBufAlgo.fill(buf, color, roi=roi)


def _draw_circle_outline(
    buf: ImageBuf,
    center_x: int,
    center_y: int,
    radius: int,
    thickness: int,
    color: RGBA,
) -> None:
    """
    Draw a circle outline using parametric approach.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    center_x : int
        X coordinate of the circle center.
    center_y : int
        Y coordinate of the circle center.
    radius : int
        Radius of the circle in pixels.
    thickness : int
        Line thickness in pixels.
    color : RGBA
        Line color as (r, g, b, a) tuple.
    """
    num_points = max(360, int(2 * math.pi * radius))
    half_thick = max(1, thickness // 2)

    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        px = int(center_x + radius * math.cos(angle))
        py = int(center_y + radius * math.sin(angle))

        roi = ROI(
            max(0, px - half_thick),
            min(buf.spec().width, px + half_thick + 1),
            max(0, py - half_thick),
            min(buf.spec().height, py + half_thick + 1),
        )
        ImageBufAlgo.fill(buf, color, roi=roi)


def draw_ellipse(
    buf: ImageBuf,
    center_x: int,
    center_y: int,
    radius_x: int,
    radius_y: int,
    thickness: int,
    color: RGBA,
    filled: bool = False,
) -> None:
    """
    Draw an ellipse outline or filled ellipse.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    center_x : int
        X coordinate of the ellipse center.
    center_y : int
        Y coordinate of the ellipse center.
    radius_x : int
        Radius of the ellipse along the X axis.
    radius_y : int
        Radius of the ellipse along the Y axis.
    thickness : int
        Line thickness in pixels (for outline mode).
    color : RGBA
        Color as (r, g, b, a) tuple.
    filled : bool, optional
        If True, draw a filled ellipse. Default is False (outline only).
    """
    if filled:
        _draw_filled_ellipse(buf, center_x, center_y, radius_x, radius_y, color)
    else:
        _draw_ellipse_outline(buf, center_x, center_y, radius_x, radius_y, thickness, color)


def _draw_filled_ellipse(
    buf: ImageBuf,
    center_x: int,
    center_y: int,
    radius_x: int,
    radius_y: int,
    color: RGBA,
) -> None:
    """
    Draw a filled ellipse using horizontal scanlines.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    center_x : int
        X coordinate of the ellipse center.
    center_y : int
        Y coordinate of the ellipse center.
    radius_x : int
        Radius of the ellipse along the X axis.
    radius_y : int
        Radius of the ellipse along the Y axis.
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    """
    for dy in range(-radius_y, radius_y + 1):
        y_ratio = dy / radius_y if radius_y > 0 else 0
        if abs(y_ratio) <= 1:
            dx = int(radius_x * math.sqrt(1 - y_ratio * y_ratio))
            y = center_y + dy
            x1 = center_x - dx
            x2 = center_x + dx

            if 0 <= y < buf.spec().height:
                roi = ROI(max(0, x1), min(buf.spec().width, x2 + 1), y, y + 1)
                ImageBufAlgo.fill(buf, color, roi=roi)


def _draw_ellipse_outline(
    buf: ImageBuf,
    center_x: int,
    center_y: int,
    radius_x: int,
    radius_y: int,
    thickness: int,
    color: RGBA,
) -> None:
    """
    Draw an ellipse outline using parametric approach.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    center_x : int
        X coordinate of the ellipse center.
    center_y : int
        Y coordinate of the ellipse center.
    radius_x : int
        Radius of the ellipse along the X axis.
    radius_y : int
        Radius of the ellipse along the Y axis.
    thickness : int
        Line thickness in pixels.
    color : RGBA
        Line color as (r, g, b, a) tuple.
    """
    num_points = max(360, int(math.pi * (radius_x + radius_y)))
    half_thick = max(1, thickness // 2)

    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        px = int(center_x + radius_x * math.cos(angle))
        py = int(center_y + radius_y * math.sin(angle))

        roi = ROI(
            max(0, px - half_thick),
            min(buf.spec().width, px + half_thick + 1),
            max(0, py - half_thick),
            min(buf.spec().height, py + half_thick + 1),
        )
        ImageBufAlgo.fill(buf, color, roi=roi)


def draw_crosshair(
    buf: ImageBuf,
    center_x: int,
    center_y: int,
    size_x: int,
    size_y: int,
    thickness: int,
    color: RGBA,
) -> None:
    """
    Draw a crosshair (+ shape) with squeeze-compensated sizes.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    center_x : int
        X coordinate of the crosshair center.
    center_y : int
        Y coordinate of the crosshair center.
    size_x : int
        Half-length of the horizontal line.
    size_y : int
        Half-length of the vertical line.
    thickness : int
        Line thickness in pixels.
    color : RGBA
        Line color as (r, g, b, a) tuple.
    """
    draw_horizontal_line(buf, center_x - size_x, center_x + size_x, center_y, thickness, color)
    draw_vertical_line(buf, center_x, center_y - size_y, center_y + size_y, thickness, color)


def draw_grid(
    buf: ImageBuf,
    width: int,
    height: int,
    spacing: int,
    thickness: int,
    color: RGBA,
) -> None:
    """
    Draw a grid overlay on the image buffer.

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    width : int
        Width of the grid area in pixels.
    height : int
        Height of the grid area in pixels.
    spacing : int
        Spacing between grid lines in pixels.
    thickness : int
        Line thickness in pixels.
    color : RGBA
        Line color as (r, g, b, a) tuple.
    """
    x = 0
    while x <= width:
        draw_vertical_line(buf, x, 0, height, thickness, color)
        x += spacing

    y = 0
    while y <= height:
        draw_horizontal_line(buf, 0, width, y, thickness, color)
        y += spacing


def draw_frame_region(
    buf: ImageBuf,
    outer_x: int,
    outer_y: int,
    outer_width: int,
    outer_height: int,
    inner_x: int,
    inner_y: int,
    inner_width: int,
    inner_height: int,
    color: RGBA,
) -> None:
    """
    Draw a frame region (area between outer and inner rectangle).

    Parameters
    ----------
    buf : ImageBuf
        The OpenImageIO image buffer to draw on.
    outer_x : int
        X coordinate of the outer rectangle's top-left corner.
    outer_y : int
        Y coordinate of the outer rectangle's top-left corner.
    outer_width : int
        Width of the outer rectangle in pixels.
    outer_height : int
        Height of the outer rectangle in pixels.
    inner_x : int
        X coordinate of the inner rectangle's top-left corner.
    inner_y : int
        Y coordinate of the inner rectangle's top-left corner.
    inner_width : int
        Width of the inner rectangle in pixels.
    inner_height : int
        Height of the inner rectangle in pixels.
    color : RGBA
        Fill color as (r, g, b, a) tuple.
    """
    if inner_y > outer_y:
        draw_filled_rect(buf, outer_x, outer_y, outer_width, inner_y - outer_y, color)

    inner_bottom = inner_y + inner_height
    outer_bottom = outer_y + outer_height
    if inner_bottom < outer_bottom:
        draw_filled_rect(buf, outer_x, inner_bottom, outer_width, outer_bottom - inner_bottom, color)

    if inner_x > outer_x:
        draw_filled_rect(buf, outer_x, inner_y, inner_x - outer_x, inner_height, color)

    inner_right = inner_x + inner_width
    outer_right = outer_x + outer_width
    if inner_right < outer_right:
        draw_filled_rect(buf, inner_right, inner_y, outer_right - inner_right, inner_height, color)
