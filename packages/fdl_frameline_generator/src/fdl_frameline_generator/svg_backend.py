# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
SVG rendering backend for the frameline generator.

Provides an SvgDocument class that accumulates drawing operations as SVG elements,
producing a vector output equivalent to the raster OIIO pipeline.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from fdl_frameline_generator.colors import RGBA


def _rgba_to_css(color: RGBA) -> str:
    """Convert RGBA float tuple to CSS rgb() string."""
    r, g, b = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
    return f"rgb({r},{g},{b})"


def _rgba_opacity(color: RGBA) -> float:
    """Extract opacity from RGBA tuple (4th element, default 1.0)."""
    return color[3] if len(color) > 3 else 1.0


@dataclass
class SvgDocument:
    """
    Accumulates SVG elements and writes the final document.

    Usage::

        doc = SvgDocument(width=3840, height=2160)
        doc.fill_background((0.55, 0.55, 0.55, 1.0))
        doc.draw_rect(100, 200, 500, 300, stroke_color=(1,1,1,1), stroke_width=2)
        doc.draw_text("Hello", 120, 220, font_size=24, color=(0,0,0,1))
        doc.write("output.svg")
    """

    width: int
    height: int
    _elements: list[ET.Element] = field(default_factory=list, init=False, repr=False)

    # -----------------------------------------------------------------------
    # Primitive drawing operations
    # -----------------------------------------------------------------------

    def fill_background(self, color: RGBA) -> None:
        """Fill the entire canvas with a solid color."""
        rect = ET.Element(
            "rect",
            x="0",
            y="0",
            width=str(self.width),
            height=str(self.height),
            fill=_rgba_to_css(color),
            opacity=str(_rgba_opacity(color)),
        )
        self._elements.append(rect)

    def draw_filled_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: RGBA,
    ) -> None:
        """Draw a filled rectangle (no stroke)."""
        rect = ET.Element(
            "rect",
            x=str(x),
            y=str(y),
            width=str(width),
            height=str(height),
            fill=_rgba_to_css(color),
            opacity=str(_rgba_opacity(color)),
        )
        self._elements.append(rect)

    def draw_rect_outline(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        stroke_width: int,
        color: RGBA,
        dash_pattern: tuple[int, int] | None = None,
    ) -> None:
        """Draw a rectangle outline (no fill)."""
        attrs: dict[str, str] = {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "fill": "none",
            "stroke": _rgba_to_css(color),
            "stroke-width": str(stroke_width),
            "opacity": str(_rgba_opacity(color)),
        }
        if dash_pattern:
            attrs["stroke-dasharray"] = f"{dash_pattern[0]},{dash_pattern[1]}"
        self._elements.append(ET.Element("rect", **attrs))

    def draw_frame_region(
        self,
        outer_x: int,
        outer_y: int,
        outer_w: int,
        outer_h: int,
        inner_x: int,
        inner_y: int,
        inner_w: int,
        inner_h: int,
        color: RGBA,
    ) -> None:
        """Draw the region between an outer and inner rectangle (frame border)."""
        # Use a path with even-odd fill rule to create a hollow rectangle
        d = f"M{outer_x},{outer_y} h{outer_w} v{outer_h} h{-outer_w} Z M{inner_x},{inner_y} h{inner_w} v{inner_h} h{-inner_w} Z"
        path = ET.Element(
            "path",
            d=d,
            fill=_rgba_to_css(color),
            opacity=str(_rgba_opacity(color)),
        )
        path.set("fill-rule", "evenodd")
        self._elements.append(path)

    def draw_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        stroke_width: int,
        color: RGBA,
    ) -> None:
        """Draw a straight line."""
        line = ET.Element(
            "line",
            x1=str(x1),
            y1=str(y1),
            x2=str(x2),
            y2=str(y2),
            stroke=_rgba_to_css(color),
        )
        line.set("stroke-width", str(stroke_width))
        line.set("opacity", str(_rgba_opacity(color)))
        self._elements.append(line)

    def draw_ellipse(
        self,
        cx: int,
        cy: int,
        rx: int,
        ry: int,
        stroke_width: int,
        color: RGBA,
    ) -> None:
        """Draw an ellipse outline."""
        el = ET.Element(
            "ellipse",
            cx=str(cx),
            cy=str(cy),
            rx=str(rx),
            ry=str(ry),
            fill="none",
            stroke=_rgba_to_css(color),
        )
        el.set("stroke-width", str(stroke_width))
        el.set("opacity", str(_rgba_opacity(color)))
        self._elements.append(el)

    def draw_polygon(self, points: list[tuple[int, int]], color: RGBA) -> None:
        """Draw a filled polygon."""
        pts = " ".join(f"{x},{y}" for x, y in points)
        poly = ET.Element(
            "polygon",
            points=pts,
            fill=_rgba_to_css(color),
            opacity=str(_rgba_opacity(color)),
        )
        self._elements.append(poly)

    def draw_crosshair(
        self,
        cx: int,
        cy: int,
        size: int,
        stroke_width: int,
        color: RGBA,
    ) -> None:
        """Draw a crosshair at the specified center."""
        half = size // 2
        self.draw_line(cx - half, cy, cx + half, cy, stroke_width, color)
        self.draw_line(cx, cy - half, cx, cy + half, stroke_width, color)

    def draw_grid(
        self,
        width: int,
        height: int,
        spacing: int,
        stroke_width: int,
        color: RGBA,
    ) -> None:
        """Draw a grid overlay."""
        for x in range(0, width, spacing):
            self.draw_line(x, 0, x, height, stroke_width, color)
        for y in range(0, height, spacing):
            self.draw_line(0, y, width, y, stroke_width, color)

    # -----------------------------------------------------------------------
    # Arrow / triangle primitives
    # -----------------------------------------------------------------------

    def draw_corner_triangle(
        self,
        corner_x: int,
        corner_y: int,
        size_x: int,
        size_y: int,
        corner: str,
        color: RGBA,
    ) -> None:
        """
        Draw a small filled triangle at a rectangle corner.

        corner is one of: "top_left", "top_right", "bottom_left", "bottom_right".
        """
        if corner == "top_left":
            pts = [(corner_x, corner_y), (corner_x + size_x, corner_y), (corner_x, corner_y + size_y)]
        elif corner == "top_right":
            pts = [(corner_x, corner_y), (corner_x - size_x, corner_y), (corner_x, corner_y + size_y)]
        elif corner == "bottom_left":
            pts = [(corner_x, corner_y), (corner_x + size_x, corner_y), (corner_x, corner_y - size_y)]
        elif corner == "bottom_right":
            pts = [(corner_x, corner_y), (corner_x - size_x, corner_y), (corner_x, corner_y - size_y)]
        else:
            return
        self.draw_polygon(pts, color)

    def draw_edge_arrow(
        self,
        mid_x: int,
        mid_y: int,
        size_along: int,
        size_perp: int,
        edge: str,
        color: RGBA,
        offset: int = 0,
    ) -> None:
        """
        Draw an inward-pointing arrow at the midpoint of an edge.

        edge is one of: "top", "bottom", "left", "right".
        """
        if edge == "top":
            ax, ay = mid_x + offset, mid_y
            pts = [(ax - size_along, ay), (ax + size_along, ay), (ax, ay + size_perp)]
        elif edge == "bottom":
            ax, ay = mid_x + offset, mid_y
            pts = [(ax - size_along, ay), (ax + size_along, ay), (ax, ay - size_perp)]
        elif edge == "left":
            ax, ay = mid_x, mid_y + offset
            pts = [(ax, ay - size_along), (ax, ay + size_along), (ax + size_perp, ay)]
        elif edge == "right":
            ax, ay = mid_x, mid_y + offset
            pts = [(ax, ay - size_along), (ax, ay + size_along), (ax - size_perp, ay)]
        else:
            return
        self.draw_polygon(pts, color)

    # -----------------------------------------------------------------------
    # Text rendering
    # -----------------------------------------------------------------------

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        font_size: int,
        color: RGBA,
        font_family: str = "monospace",
        anchor: str = "start",
        bold: bool = False,
        squeeze_comp: float = 1.0,
    ) -> None:
        """
        Draw text at the specified position.

        Parameters
        ----------
        anchor : str
            SVG text-anchor: "start" (left), "middle" (center), "end" (right).
        squeeze_comp : float
            Horizontal scale factor (1.0 / anamorphic_squeeze).  When not 1.0
            a ``scale(squeeze_comp, 1)`` transform is applied around the
            text's anchor point so the text appears correct after de-squeeze.
        """
        el = ET.Element("text", x=str(x), y=str(y + font_size))
        el.set("font-size", str(font_size))
        el.set("font-family", font_family)
        el.set("fill", _rgba_to_css(color))
        el.set("opacity", str(_rgba_opacity(color)))
        el.set("text-anchor", anchor)
        if bold:
            el.set("font-weight", "bold")
        # Apply horizontal squeeze compensation around the anchor point
        if abs(squeeze_comp - 1.0) > 0.001:
            ty = y + font_size
            el.set(
                "transform",
                f"translate({x},{ty}) scale({squeeze_comp:.6f},1) translate({-x},{-ty})",
            )
        el.text = text
        self._elements.append(el)

    # -----------------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------------

    def to_string(self) -> str:
        """Serialize the SVG document to a string."""
        svg = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            viewBox=f"0 0 {self.width} {self.height}",
            width=str(self.width),
            height=str(self.height),
        )
        svg.set("font-family", "'Courier New', Courier, monospace")
        for el in self._elements:
            svg.append(el)
        ET.indent(svg, space="  ")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(svg, encoding="unicode")

    def write(self, path: str | Path) -> None:
        """Write the SVG document to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_string(), encoding="utf-8")
