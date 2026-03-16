# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Main frameline renderer for generating FDL visualization images.

This module provides the FramelineRenderer class that composes all drawing
primitives and text rendering to create complete frameline overlay images.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from fdl import (
    FDL,
    Canvas,
    Context,
    FramingDecision,
    find_by_id,
    find_by_label,
    read_from_file,
)
from OpenImageIO import FLOAT, ImageBuf, ImageBufAlgo, ImageSpec

from fdl_frameline_generator.colors import (
    COLOR_GRID,
    DASH_PATTERN_PROTECTION,
    LINE_WIDTH_GRID,
    RGBA,
)
from fdl_frameline_generator.config import RenderConfig
from fdl_frameline_generator.primitives import (
    draw_corner_triangle,
    draw_crosshair,
    draw_ellipse,
    draw_frame_region,
    draw_grid,
    draw_rect_corner_triangles,
    draw_rect_edge_arrows_single,
    draw_single_edge_arrow,
)
from fdl_frameline_generator.resources import DEFAULT_LOGO_PATH
from fdl_frameline_generator.text import (
    TextAlignment,
    render_squeeze_label,
    render_text,
    render_text_bold,
)

if TYPE_CHECKING:
    from fdl_frameline_generator.svg_backend import SvgDocument


@dataclass
class LayerRect:
    """
    A rectangle layer with its properties.

    Attributes
    ----------
    name : str
        The layer name (e.g., "canvas", "effective", "protection", "framing").
    x : int
        X coordinate of the top-left corner.
    y : int
        Y coordinate of the top-left corner.
    width : int
        Width of the rectangle in pixels.
    height : int
        Height of the rectangle in pixels.
    color : RGBA
        Color of the layer as (r, g, b, a) tuple.
    """

    name: str
    x: int
    y: int
    width: int
    height: int
    color: RGBA


class FramelineRenderer:
    """
    Renderer for generating FDL frameline overlay images.

    This class orchestrates the rendering of frameline visualizations from
    FDL data, including canvas, effective, protection, and framing layers,
    along with annotations and reference markers.

    Attributes
    ----------
    config : RenderConfig
        The rendering configuration.
    """

    # Layer priority for label sliding (lower = higher priority, stays in place)
    LAYER_PRIORITY: ClassVar[dict[str, int]] = {
        "canvas": 0,
        "effective": 1,
        "protection": 2,
        "framing": 3,
    }

    def __init__(self, config: RenderConfig | None = None) -> None:
        """
        Initialize the FramelineRenderer.

        Parameters
        ----------
        config : RenderConfig, optional
            Rendering configuration. If None, uses default configuration.
        """
        self.config = config or RenderConfig()

    def _check_label_overlap(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        existing_positions: list[tuple[int, int, int, int, str]],
        margin: int = 5,
    ) -> tuple[bool, tuple[int, int, int, int, str] | None]:
        """
        Check if a label at (x, y, width, height) overlaps any existing label.

        Parameters
        ----------
        x : int
            X coordinate of the label.
        y : int
            Y coordinate of the label.
        width : int
            Width of the label.
        height : int
            Height of the label.
        existing_positions : List[Tuple[int, int, int, int, str]]
            List of existing label positions as (x, y, width, height, layer_name).
        margin : int, optional
            Margin around labels for overlap detection. Default is 5.

        Returns
        -------
        Tuple[bool, Optional[Tuple[int, int, int, int, str]]]
            (overlaps, colliding_label_info) where colliding_label_info
            is the first overlapping label found, or None.
        """
        for tx, ty, tw, th, layer_name in existing_positions:
            # Check if bounding boxes overlap (with margin)
            if not (x + width + margin < tx or x > tx + tw + margin or y + height + margin < ty or y > ty + th + margin):
                return True, (tx, ty, tw, th, layer_name)
        return False, None

    def _find_non_overlapping_position(
        self,
        preferred_x: int,
        preferred_y: int,
        text_width: int,
        text_height: int,
        layer_name: str,
        existing_positions: list[tuple[int, int, int, int, str]],
        slide_direction: str = "horizontal",
        slide_amount: int = 50,
        max_attempts: int = 10,
    ) -> tuple[int, int]:
        """
        Find a non-overlapping position for a label, sliding horizontally first.

        For horizontal sliding:
        - If colliding with another layer's label, slide this one based on priority
        - Lower priority layers slide right, higher priority layers stay or slide left

        Falls back to vertical sliding if horizontal doesn't work.

        Parameters
        ----------
        preferred_x : int
            Preferred X coordinate for the label.
        preferred_y : int
            Preferred Y coordinate for the label.
        text_width : int
            Width of the text label.
        text_height : int
            Height of the text label.
        layer_name : str
            Name of the layer this label belongs to.
        existing_positions : List[Tuple[int, int, int, int, str]]
            List of existing label positions as (x, y, width, height, layer_name).
        slide_direction : str, optional
            Primary slide direction: "horizontal" or "vertical". Default is "horizontal".
        slide_amount : int, optional
            Amount to slide on each attempt. Default is 50.
        max_attempts : int, optional
            Maximum number of sliding attempts. Default is 10.

        Returns
        -------
        Tuple[int, int]
            The final (x, y) position for the label.
        """
        x, y = preferred_x, preferred_y

        # Check if initial position overlaps
        overlaps, colliding = self._check_label_overlap(x, y, text_width, text_height, existing_positions)

        if not overlaps:
            return x, y

        # Determine slide direction based on layer priority
        my_priority = self.LAYER_PRIORITY.get(layer_name, 99)

        if colliding:
            colliding_layer = colliding[4]
            colliding_priority = self.LAYER_PRIORITY.get(colliding_layer, 99)

            # Lower priority number = higher priority (stays in place)
            # If we have lower priority (higher number), we slide
            if my_priority > colliding_priority:
                # We slide right (or down for vertical)
                h_direction = 1
                v_direction = 1
            else:
                # They should have slid, but we can slide left (or up) as fallback
                h_direction = -1
                v_direction = -1
        else:
            # Default to sliding right/down
            h_direction = 1
            v_direction = 1

        # Try horizontal sliding first
        if slide_direction == "horizontal":
            for attempt in range(1, max_attempts + 1):
                test_x = x + (attempt * slide_amount * h_direction)
                overlaps, _ = self._check_label_overlap(test_x, y, text_width, text_height, existing_positions)
                if not overlaps:
                    return test_x, y

            # Horizontal didn't work, try vertical
            for attempt in range(1, max_attempts + 1):
                test_y = y + (attempt * text_height * v_direction)
                overlaps, _ = self._check_label_overlap(x, test_y, text_width, text_height, existing_positions)
                if not overlaps:
                    return x, test_y

        else:  # vertical first
            for attempt in range(1, max_attempts + 1):
                test_y = y + (attempt * text_height * v_direction)
                overlaps, _ = self._check_label_overlap(x, test_y, text_width, text_height, existing_positions)
                if not overlaps:
                    return x, test_y

            # Vertical didn't work, try horizontal
            for attempt in range(1, max_attempts + 1):
                test_x = x + (attempt * slide_amount * h_direction)
                overlaps, _ = self._check_label_overlap(test_x, y, text_width, text_height, existing_positions)
                if not overlaps:
                    return test_x, y

        # If all else fails, return the last attempted position
        return x, y

    def render_from_fdl(
        self,
        fdl_path: str | Path,
        output_path: str | Path,
        context_label: str | None = None,
        canvas_id: str | None = None,
        framing_id: str | None = None,
    ) -> bool:
        """
        Render a frameline image from an FDL file.

        Parameters
        ----------
        fdl_path : str or Path
            Path to the input FDL file.
        output_path : str or Path
            Path for the output image file.
        context_label : str, optional
            Context label to use. If None, uses the first context.
        canvas_id : str, optional
            Canvas ID to use. If None, uses the first canvas.
        framing_id : str, optional
            Framing decision ID to use. If None, uses the first framing decision.

        Returns
        -------
        bool
            True if rendering succeeded.

        Raises
        ------
        FileNotFoundError
            If the FDL file does not exist.
        ValueError
            If the specified context, canvas, or framing decision is not found.
        IOError
            If the output file cannot be written.
        """
        fdl_path = Path(fdl_path)
        output_path = Path(output_path)

        if not fdl_path.exists():
            raise FileNotFoundError(f"FDL file not found: {fdl_path}")

        fdl = read_from_file(fdl_path)
        _context, canvas, framing = self._get_fdl_components(fdl, context_label, canvas_id, framing_id)

        if output_path.suffix.lower() == ".svg":
            return self._render_and_write_svg(canvas, framing, output_path)
        else:
            buf = self._create_image_buffer(canvas)
            self._render_all_layers(buf, canvas, framing)
            return self._write_output(buf, output_path)

    def render_from_fdl_object(
        self,
        fdl: FDL,
        output_path: str | Path,
        context_label: str | None = None,
        canvas_id: str | None = None,
        framing_id: str | None = None,
    ) -> bool:
        """
        Render a frameline image from an FDL object.

        Parameters
        ----------
        fdl : FDL
            The FDL object containing framing data.
        output_path : str or Path
            Path for the output image file. Use .svg extension for vector output.
        context_label : str, optional
            Context label to use. If None, uses the first context.
        canvas_id : str, optional
            Canvas ID to use. If None, uses the first canvas.
        framing_id : str, optional
            Framing decision ID to use. If None, uses the first framing decision.

        Returns
        -------
        bool
            True if rendering succeeded.

        Raises
        ------
        ValueError
            If the specified context, canvas, or framing decision is not found.
        IOError
            If the output file cannot be written.
        """
        output_path = Path(output_path)

        _context, canvas, framing = self._get_fdl_components(fdl, context_label, canvas_id, framing_id)

        if output_path.suffix.lower() == ".svg":
            return self._render_and_write_svg(canvas, framing, output_path)
        else:
            buf = self._create_image_buffer(canvas)
            self._render_all_layers(buf, canvas, framing)
            return self._write_output(buf, output_path)

    def render_to_buffer(
        self,
        fdl: FDL,
        context_label: str | None = None,
        canvas_id: str | None = None,
        framing_id: str | None = None,
    ) -> ImageBuf:
        """
        Render a frameline image to an ImageBuf without saving.

        Parameters
        ----------
        fdl : FDL
            The FDL object containing framing data.
        context_label : str, optional
            Context label to use. If None, uses the first context.
        canvas_id : str, optional
            Canvas ID to use. If None, uses the first canvas.
        framing_id : str, optional
            Framing decision ID to use. If None, uses the first framing decision.

        Returns
        -------
        ImageBuf
            The rendered image buffer.

        Raises
        ------
        ValueError
            If the specified context, canvas, or framing decision is not found.
        """
        _context, canvas, framing = self._get_fdl_components(fdl, context_label, canvas_id, framing_id)

        buf = self._create_image_buffer(canvas)
        self._render_all_layers(buf, canvas, framing)

        return buf

    def render_to_svg(
        self,
        fdl: FDL,
        context_label: str | None = None,
        canvas_id: str | None = None,
        framing_id: str | None = None,
    ) -> str:
        """
        Render a frameline image as an SVG string.

        Parameters
        ----------
        fdl : FDL
            The FDL object containing framing data.
        context_label : str, optional
            Context label to use. If None, uses the first context.
        canvas_id : str, optional
            Canvas ID to use. If None, uses the first canvas.
        framing_id : str, optional
            Framing decision ID to use. If None, uses the first framing decision.

        Returns
        -------
        str
            The rendered SVG document as a string.
        """
        _context, canvas, framing = self._get_fdl_components(fdl, context_label, canvas_id, framing_id)
        doc = self._build_svg_document(canvas, framing)
        return doc.to_string()

    def _render_and_write_svg(
        self,
        canvas: Canvas,
        framing: FramingDecision,
        output_path: Path,
    ) -> bool:
        """
        Build an SVG document from FDL components and write to file.

        Parameters
        ----------
        canvas : Canvas
            The canvas containing dimension and effective area data.
        framing : FramingDecision
            The framing decision containing framing and protection data.
        output_path : Path
            The output file path.

        Returns
        -------
        bool
            True if writing succeeded.
        """
        doc = self._build_svg_document(canvas, framing)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.write(output_path)
        return True

    def _build_svg_document(
        self,
        canvas: Canvas,
        framing: FramingDecision,
    ) -> SvgDocument:
        """
        Build a complete SVG document from FDL canvas and framing data.

        This mirrors the logic of ``_render_all_layers`` but targets an
        :class:`SvgDocument` instead of an OIIO ``ImageBuf``.

        Parameters
        ----------
        canvas : Canvas
            The canvas providing dimensions and effective area data.
        framing : FramingDecision
            The framing decision providing framing and protection data.

        Returns
        -------
        SvgDocument
            The assembled SVG document ready for serialization.
        """
        from fdl_frameline_generator.svg_backend import SvgDocument

        vis = self.config.visibility
        width = canvas.dimensions.width
        height = canvas.dimensions.height
        squeeze = canvas.anamorphic_squeeze
        squeeze_comp = 1.0 / squeeze

        doc = SvgDocument(width=width, height=height)

        # Background
        doc.fill_background(self.config.color_background)

        # Build layer hierarchy (same geometry calculation as raster path)
        layers = self._get_layer_hierarchy(canvas, framing)

        # Calculate base sizes for arrows/triangles
        base_size = min(width, height)
        triangle_size_base = max(30, base_size // 40)
        triangle_size_x = int(triangle_size_base * squeeze_comp)
        triangle_size_y = triangle_size_base
        arrow_size_base = max(20, base_size // 50)
        arrow_size_along = int(arrow_size_base * squeeze_comp)
        arrow_size_perp = arrow_size_base

        # Grid (background layer)
        if vis.grid:
            doc.draw_grid(width, height, self.config.grid_spacing, LINE_WIDTH_GRID, COLOR_GRID)

        # --- Layer fills (outer to inner) ---
        for i, layer in enumerate(layers):
            if i < len(layers) - 1:
                next_inner = layers[i + 1]
                doc.draw_frame_region(
                    layer.x,
                    layer.y,
                    layer.width,
                    layer.height,
                    next_inner.x,
                    next_inner.y,
                    next_inner.width,
                    next_inner.height,
                    layer.color,
                )
            else:
                # Innermost layer — fill with background
                doc.draw_filled_rect(layer.x, layer.y, layer.width, layer.height, self.config.color_background)

        # --- Corner triangles and edge arrows for each layer ---
        seen_bounds: dict[tuple, int] = {}
        for layer in layers:
            bounds = (layer.x, layer.y, layer.width, layer.height)
            offset_index = seen_bounds.get(bounds, 0)
            seen_bounds[bounds] = offset_index + 1

            arrow_color = self._get_arrow_color(layer.name)

            # Corner triangles
            scale = max(0.55, 1.0 - offset_index * 0.15)
            ts_x = int(triangle_size_x * scale)
            ts_y = int(triangle_size_y * scale)
            doc.draw_corner_triangle(layer.x, layer.y, ts_x, ts_y, "top_left", arrow_color)
            doc.draw_corner_triangle(layer.x + layer.width - 1, layer.y, ts_x, ts_y, "top_right", arrow_color)
            doc.draw_corner_triangle(layer.x, layer.y + layer.height - 1, ts_x, ts_y, "bottom_left", arrow_color)
            doc.draw_corner_triangle(layer.x + layer.width - 1, layer.y + layer.height - 1, ts_x, ts_y, "bottom_right", arrow_color)

            # Edge arrows (midpoint of each side)
            mid_x = layer.x + layer.width // 2
            mid_y = layer.y + layer.height // 2
            edge_offset = offset_index * int(arrow_size_along * 1.5)
            doc.draw_edge_arrow(mid_x, layer.y, arrow_size_along, arrow_size_perp, "top", arrow_color, edge_offset)
            doc.draw_edge_arrow(mid_x, layer.y + layer.height - 1, arrow_size_along, arrow_size_perp, "bottom", arrow_color, edge_offset)
            doc.draw_edge_arrow(layer.x, mid_y, arrow_size_along, arrow_size_perp, "left", arrow_color, edge_offset)
            doc.draw_edge_arrow(layer.x + layer.width - 1, mid_y, arrow_size_along, arrow_size_perp, "right", arrow_color, edge_offset)

        # --- Protection dashed outline ---
        for layer in layers:
            if layer.name == "protection":
                doc.draw_rect_outline(
                    layer.x,
                    layer.y,
                    layer.width,
                    layer.height,
                    self.config.line_width_protection,
                    layer.color,
                    dash_pattern=DASH_PATTERN_PROTECTION,
                )

        # --- Crosshair ---
        framing_layer = next((ly for ly in layers if ly.name == "framing"), None)
        if vis.crosshair and framing_layer:
            center_x = framing_layer.x + framing_layer.width // 2
            center_y = framing_layer.y + framing_layer.height // 2
            base_ch = int(min(framing_layer.width, framing_layer.height) / 30)
            base_ch = max(base_ch, 15)
            size_x_ch = int(base_ch * squeeze_comp)
            doc.draw_crosshair(center_x, center_y, size_x_ch, 2, self.config.color_framing)

        # --- Reference circles (squeeze) ---
        if vis.squeeze_circle and framing_layer:
            center_x = framing_layer.x + framing_layer.width // 2
            center_y = framing_layer.y + framing_layer.height // 2
            max_radius = min(framing_layer.width, framing_layer.height) // 2 - 20
            if max_radius >= 50:
                num_circles = 1 if max_radius < 150 else (2 if max_radius < 300 else 3)
                for i in range(num_circles):
                    ratio = (i + 1) / num_circles
                    radius = int(max_radius * ratio)
                    doc.draw_ellipse(center_x, center_y, int(radius * squeeze_comp), radius, 2, self.config.color_squeeze)
                if squeeze != 1.0:
                    label_y = center_y + max_radius + 25
                    doc.draw_text(
                        f"Squeeze: {squeeze:.3f}x",
                        center_x,
                        label_y,
                        self.config.font_size_anchor,
                        self.config.color_squeeze,
                        anchor="middle",
                        squeeze_comp=squeeze_comp,
                    )

        # --- Dimension labels ---
        if vis.dimension_labels:
            for layer in layers:
                label = f"{layer.name.capitalize()}: {layer.width} x {layer.height}"
                lx = layer.x + 15
                ly = layer.y + 10
                doc.draw_text(label, lx, ly, self.config.font_size_dimension, self.config.color_text, bold=True, squeeze_comp=squeeze_comp)

        # --- Anchor labels ---
        if vis.anchor_labels:
            for layer in layers:
                if layer.name != "canvas":
                    label = f"({layer.x}, {layer.y})"
                    lx = layer.x + layer.width - 15
                    ly = layer.y + layer.height - 10 - self.config.font_size_anchor
                    doc.draw_text(
                        label,
                        lx,
                        ly,
                        self.config.font_size_anchor,
                        self.config.color_text,
                        anchor="end",
                        squeeze_comp=squeeze_comp,
                    )

        # --- Metadata overlay ---
        if self.config.show_metadata:
            meta_lines = []
            if self.config.metadata_show:
                meta_lines.append(self.config.metadata_show)
            if self.config.metadata_camera:
                meta_lines.append(f"Camera: {self.config.metadata_camera}")
            if self.config.metadata_dop:
                meta_lines.append(f"DOP: {self.config.metadata_dop}")
            if self.config.metadata_sensor_mode:
                meta_lines.append(f"Sensor: {self.config.metadata_sensor_mode}")
            if meta_lines:
                meta_y = 20
                for line in meta_lines:
                    doc.draw_text(
                        line,
                        width - 20,
                        meta_y,
                        self.config.font_size_anchor,
                        self.config.color_text,
                        anchor="end",
                        squeeze_comp=squeeze_comp,
                    )
                    meta_y += self.config.font_size_anchor + 8

        return doc

    def _get_fdl_components(
        self,
        fdl: FDL,
        context_label: str | None,
        canvas_id: str | None,
        framing_id: str | None,
    ) -> tuple[Context, Canvas, FramingDecision]:
        """
        Extract context, canvas, and framing decision from FDL.

        Parameters
        ----------
        fdl : FDL
            The FDL object to extract components from.
        context_label : str or None
            Context label to find. If None, uses first context.
        canvas_id : str or None
            Canvas ID to find. If None, uses first canvas.
        framing_id : str or None
            Framing decision ID to find. If None, uses first framing decision.

        Returns
        -------
        Tuple[Context, Canvas, FramingDecision]
            The extracted FDL components.

        Raises
        ------
        ValueError
            If the FDL has no contexts, or if specified components are not found.
        """
        if context_label:
            context = find_by_label(fdl.contexts, context_label)
            if context is None:
                raise ValueError(f"Context with label '{context_label}' not found")
        else:
            if not fdl.contexts:
                raise ValueError("FDL has no contexts")
            context = fdl.contexts[0]

        if canvas_id:
            canvas = find_by_id(context.canvases, canvas_id)
            if canvas is None:
                raise ValueError(f"Canvas with ID '{canvas_id}' not found")
        else:
            if not context.canvases:
                raise ValueError(f"Context '{context.label}' has no canvases")
            canvas = context.canvases[0]

        if framing_id:
            framing = find_by_id(canvas.framing_decisions, framing_id)
            if framing is None:
                raise ValueError(f"Framing decision with ID '{framing_id}' not found")
        else:
            if not canvas.framing_decisions:
                raise ValueError(f"Canvas '{canvas.id}' has no framing decisions")
            framing = canvas.framing_decisions[0]

        return context, canvas, framing

    def _create_image_buffer(self, canvas: Canvas) -> ImageBuf:
        """
        Create an RGB image buffer at canvas dimensions.

        Parameters
        ----------
        canvas : Canvas
            The canvas providing the image dimensions.

        Returns
        -------
        ImageBuf
            A new image buffer filled with the background color.
        """
        width = canvas.dimensions.width
        height = canvas.dimensions.height

        # Use 3 channels (RGB) instead of 4 (RGBA) for solid images
        spec = ImageSpec(width, height, 3, FLOAT)
        buf = ImageBuf(spec)

        # Extract RGB from background color (ignore alpha)
        bg_rgb = self.config.color_background[:3]
        ImageBufAlgo.fill(buf, bg_rgb)

        return buf

    def _get_arrow_color(self, layer_name: str) -> RGBA:
        """
        Get the arrow/indicator color for a specific layer.

        Parameters
        ----------
        layer_name : str
            The layer name ("canvas", "effective", "protection", "framing").

        Returns
        -------
        RGBA
            The arrow color for this layer.
        """
        if layer_name == "canvas":
            return self.config.color_arrow_canvas
        elif layer_name == "effective":
            return self.config.color_arrow_effective
        elif layer_name == "protection":
            return self.config.color_arrow_protection
        elif layer_name == "framing":
            return self.config.color_arrow_framing
        else:
            # Fallback to white
            return (1.0, 1.0, 1.0, 1.0)

    def _check_edge_arrow_overlap(
        self,
        layer1: LayerRect,
        layer2: LayerRect,
        arrow_size: int,
    ) -> dict:
        """
        Check which edges have overlapping midpoint arrows between two layers.

        Parameters
        ----------
        layer1 : LayerRect
            The first layer (e.g., protection).
        layer2 : LayerRect
            The second layer (e.g., framing).
        arrow_size : int
            The size of the arrows, used to determine overlap threshold.

        Returns
        -------
        dict
            Dictionary with keys 'top', 'bottom', 'left', 'right'.
            Each value is True if arrows on that edge would overlap.
        """
        # Calculate midpoints
        mid1_x = layer1.x + layer1.width // 2
        mid1_y = layer1.y + layer1.height // 2
        mid2_x = layer2.x + layer2.width // 2
        mid2_y = layer2.y + layer2.height // 2

        return {
            "top": abs(mid1_x - mid2_x) < arrow_size * 2 and layer1.y == layer2.y,
            "bottom": abs(mid1_x - mid2_x) < arrow_size * 2 and (layer1.y + layer1.height) == (layer2.y + layer2.height),
            "left": abs(mid1_y - mid2_y) < arrow_size * 2 and layer1.x == layer2.x,
            "right": abs(mid1_y - mid2_y) < arrow_size * 2 and (layer1.x + layer1.width) == (layer2.x + layer2.width),
        }

    def _check_corner_overlap(
        self,
        layer1: LayerRect,
        layer2: LayerRect,
    ) -> dict:
        """
        Check which corners overlap between two layers.

        Parameters
        ----------
        layer1 : LayerRect
            The first layer (e.g., protection).
        layer2 : LayerRect
            The second layer (e.g., framing).

        Returns
        -------
        dict
            Dictionary with keys 'top_left', 'top_right', 'bottom_left', 'bottom_right'.
            Each value is True if that corner is at the same position in both layers.
        """
        # Calculate corner positions for layer1
        l1_tl = (layer1.x, layer1.y)
        l1_tr = (layer1.x + layer1.width - 1, layer1.y)
        l1_bl = (layer1.x, layer1.y + layer1.height - 1)
        l1_br = (layer1.x + layer1.width - 1, layer1.y + layer1.height - 1)

        # Calculate corner positions for layer2
        l2_tl = (layer2.x, layer2.y)
        l2_tr = (layer2.x + layer2.width - 1, layer2.y)
        l2_bl = (layer2.x, layer2.y + layer2.height - 1)
        l2_br = (layer2.x + layer2.width - 1, layer2.y + layer2.height - 1)

        return {
            "top_left": l1_tl == l2_tl,
            "top_right": l1_tr == l2_tr,
            "bottom_left": l1_bl == l2_bl,
            "bottom_right": l1_br == l2_br,
        }

    def _render_all_layers(
        self,
        buf: ImageBuf,
        canvas: Canvas,
        framing: FramingDecision,
    ) -> None:
        """
        Render all enabled layers to the image buffer.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to render onto.
        canvas : Canvas
            The canvas containing dimension and effective area data.
        framing : FramingDecision
            The framing decision containing framing and protection data.
        """
        vis = self.config.visibility
        width = canvas.dimensions.width
        height = canvas.dimensions.height
        squeeze = canvas.anamorphic_squeeze

        # Squeeze compensation factor
        squeeze_comp = 1.0 / squeeze

        # Calculate base sizes
        base_size = min(width, height)
        triangle_size_base = max(30, base_size // 40)
        triangle_size_x = int(triangle_size_base * squeeze_comp)
        triangle_size_y = triangle_size_base

        arrow_size_base = max(20, base_size // 50)
        arrow_size_along = int(arrow_size_base * squeeze_comp)
        arrow_size_perp = arrow_size_base

        # Build layer hierarchy
        layers = self._get_layer_hierarchy(canvas, framing)

        # Grid (background layer)
        if vis.grid:
            self._render_grid(buf, width, height)

        # Drawing order for proper z-layering:
        # 1. Canvas fill + canvas arrows (outermost, at the bottom)
        # 2. All inner fills (effective, protection, framing) - these cover canvas arrows
        # 3. Inner arrows (effective, protection, framing) - drawn on top of fills
        #
        # This ensures outer layer arrows are hidden beneath inner layer fills,
        # and only the inner layer arrows are visible on top.

        # Track bounds for offset calculation
        seen_bounds: dict[tuple, int] = {}

        # --- PHASE 1: Draw canvas fill and canvas arrows ---
        canvas_layer = None
        for layer in layers:
            if layer.name == "canvas":
                canvas_layer = layer
                break

        if canvas_layer:
            # Find the next inner layer for the frame region
            canvas_idx = layers.index(canvas_layer)
            if canvas_idx < len(layers) - 1:
                inner = layers[canvas_idx + 1]
                draw_frame_region(
                    buf,
                    canvas_layer.x,
                    canvas_layer.y,
                    canvas_layer.width,
                    canvas_layer.height,
                    inner.x,
                    inner.y,
                    inner.width,
                    inner.height,
                    canvas_layer.color,
                )

            # Draw canvas arrows
            bounds = (canvas_layer.x, canvas_layer.y, canvas_layer.width, canvas_layer.height)
            seen_bounds[bounds] = 1
            arrow_color = self._get_arrow_color("canvas")
            draw_rect_corner_triangles(
                buf, canvas_layer.x, canvas_layer.y, canvas_layer.width, canvas_layer.height, triangle_size_x, triangle_size_y, arrow_color
            )
            draw_rect_edge_arrows_single(
                buf,
                canvas_layer.x,
                canvas_layer.y,
                canvas_layer.width,
                canvas_layer.height,
                arrow_size_along,
                arrow_size_perp,
                arrow_color,
                0,
            )

        # --- PHASE 2: Draw all inner layer fills (effective, protection, framing area) ---
        # These fills will cover the canvas arrows where they overlap
        inner_layers = [ly for ly in layers if ly.name != "canvas"]

        for i, layer in enumerate(inner_layers):
            # Draw fill for this layer
            if i < len(inner_layers) - 1:
                # Draw frame region between this layer and next inner layer
                next_inner = inner_layers[i + 1]
                draw_frame_region(
                    buf,
                    layer.x,
                    layer.y,
                    layer.width,
                    layer.height,
                    next_inner.x,
                    next_inner.y,
                    next_inner.width,
                    next_inner.height,
                    layer.color,
                )
            else:
                # This is the innermost layer (framing) - fill with background color
                # to cover any outer arrows that might be in this area
                from fdl_frameline_generator.primitives import draw_filled_rect

                draw_filled_rect(buf, layer.x, layer.y, layer.width, layer.height, self.config.color_background)

        # --- PHASE 3: Draw arrows for inner layers (effective, protection, framing) ---
        # Find effective, protection, and framing layers for overlap detection
        effective_layer = None
        protection_layer = None
        framing_layer_for_overlap = None
        for layer in inner_layers:
            if layer.name == "effective":
                effective_layer = layer
            elif layer.name == "protection":
                protection_layer = layer
            elif layer.name == "framing":
                framing_layer_for_overlap = layer

        # Check for all pairwise edge and corner overlaps
        # Effective vs Protection
        eff_prot_edge_overlap = {}
        eff_prot_corner_overlap = {}
        if effective_layer and protection_layer:
            eff_prot_edge_overlap = self._check_edge_arrow_overlap(effective_layer, protection_layer, arrow_size_base)
            eff_prot_corner_overlap = self._check_corner_overlap(effective_layer, protection_layer)

        # Effective vs Framing
        eff_framing_edge_overlap = {}
        eff_framing_corner_overlap = {}
        if effective_layer and framing_layer_for_overlap:
            eff_framing_edge_overlap = self._check_edge_arrow_overlap(effective_layer, framing_layer_for_overlap, arrow_size_base)
            eff_framing_corner_overlap = self._check_corner_overlap(effective_layer, framing_layer_for_overlap)

        # Protection vs Framing
        prot_framing_edge_overlap = {}
        prot_framing_corner_overlap = {}
        if protection_layer and framing_layer_for_overlap:
            prot_framing_edge_overlap = self._check_edge_arrow_overlap(protection_layer, framing_layer_for_overlap, arrow_size_base)
            prot_framing_corner_overlap = self._check_corner_overlap(protection_layer, framing_layer_for_overlap)

        # Edge offset for sliding arrows apart when overlapping
        edge_slide_offset = int(arrow_size_along * 1.5)

        # Smaller triangle sizes for inner layers when overlapping
        # Each inner layer uses progressively smaller triangles
        medium_triangle_size_x = int(triangle_size_x * 0.85)
        medium_triangle_size_y = int(triangle_size_y * 0.85)
        small_triangle_size_x = int(triangle_size_x * 0.70)
        small_triangle_size_y = int(triangle_size_y * 0.70)

        for layer in inner_layers:
            bounds = (layer.x, layer.y, layer.width, layer.height)

            # Use layer-specific arrow color
            arrow_color = self._get_arrow_color(layer.name)

            is_effective = layer.name == "effective"
            is_protection = layer.name == "protection"
            is_framing = layer.name == "framing"

            # Determine what this layer overlaps with
            if is_effective:
                # Effective can overlap with protection and/or framing
                has_prot_overlap = any(eff_prot_edge_overlap.values()) or any(eff_prot_corner_overlap.values())
                has_framing_overlap = any(eff_framing_edge_overlap.values()) or any(eff_framing_corner_overlap.values())
                has_any_overlap = has_prot_overlap or has_framing_overlap

                if has_any_overlap:
                    # Effective with overlap: draw corners individually
                    corner_info = [
                        ("top_left", layer.x, layer.y),
                        ("top_right", layer.x + layer.width - 1, layer.y),
                        ("bottom_left", layer.x, layer.y + layer.height - 1),
                        ("bottom_right", layer.x + layer.width - 1, layer.y + layer.height - 1),
                    ]
                    for corner_name, corner_x, corner_y in corner_info:
                        # Check if this corner overlaps with any inner layer
                        overlaps_prot = eff_prot_corner_overlap.get(corner_name, False)
                        overlaps_framing = eff_framing_corner_overlap.get(corner_name, False)
                        if overlaps_prot or overlaps_framing:
                            # Overlapping corner - use full size (effective has priority)
                            draw_corner_triangle(buf, corner_x, corner_y, triangle_size_x, triangle_size_y, corner_name, arrow_color)
                        else:
                            draw_corner_triangle(buf, corner_x, corner_y, triangle_size_x, triangle_size_y, corner_name, arrow_color)

                    # Draw edge arrows with negative offset (slide left/up) on overlapping edges
                    for edge in ["top", "bottom", "left", "right"]:
                        overlaps_prot = eff_prot_edge_overlap.get(edge, False)
                        overlaps_framing = eff_framing_edge_overlap.get(edge, False)
                        if overlaps_prot or overlaps_framing:
                            offset = -edge_slide_offset
                        else:
                            offset = 0
                        draw_single_edge_arrow(
                            buf, layer.x, layer.y, layer.width, layer.height, edge, arrow_size_along, arrow_size_perp, arrow_color, offset
                        )
                else:
                    # No overlap - use standard rendering
                    draw_rect_corner_triangles(
                        buf, layer.x, layer.y, layer.width, layer.height, triangle_size_x, triangle_size_y, arrow_color
                    )
                    draw_rect_edge_arrows_single(
                        buf, layer.x, layer.y, layer.width, layer.height, arrow_size_along, arrow_size_perp, arrow_color, 0
                    )

            elif is_protection:
                # Protection can overlap with effective (outer) and framing (inner)
                has_eff_overlap = any(eff_prot_edge_overlap.values()) or any(eff_prot_corner_overlap.values())
                has_framing_overlap = any(prot_framing_edge_overlap.values()) or any(prot_framing_corner_overlap.values())
                has_any_overlap = has_eff_overlap or has_framing_overlap

                if has_any_overlap:
                    # Protection with overlap: draw corners individually
                    corner_info = [
                        ("top_left", layer.x, layer.y),
                        ("top_right", layer.x + layer.width - 1, layer.y),
                        ("bottom_left", layer.x, layer.y + layer.height - 1),
                        ("bottom_right", layer.x + layer.width - 1, layer.y + layer.height - 1),
                    ]
                    for corner_name, corner_x, corner_y in corner_info:
                        overlaps_eff = eff_prot_corner_overlap.get(corner_name, False)
                        overlaps_framing = prot_framing_corner_overlap.get(corner_name, False)
                        if overlaps_eff and overlaps_framing:
                            # Overlaps both - use medium size
                            draw_corner_triangle(
                                buf, corner_x, corner_y, medium_triangle_size_x, medium_triangle_size_y, corner_name, arrow_color
                            )
                        elif overlaps_eff:
                            # Overlaps effective (outer) - use medium size
                            draw_corner_triangle(
                                buf, corner_x, corner_y, medium_triangle_size_x, medium_triangle_size_y, corner_name, arrow_color
                            )
                        elif overlaps_framing:
                            # Overlaps framing (inner) - use full size (protection has priority)
                            draw_corner_triangle(buf, corner_x, corner_y, triangle_size_x, triangle_size_y, corner_name, arrow_color)
                        else:
                            draw_corner_triangle(buf, corner_x, corner_y, triangle_size_x, triangle_size_y, corner_name, arrow_color)

                    # Draw edge arrows - slide based on what it overlaps with
                    for edge in ["top", "bottom", "left", "right"]:
                        overlaps_eff = eff_prot_edge_overlap.get(edge, False)
                        overlaps_framing = prot_framing_edge_overlap.get(edge, False)
                        if overlaps_eff and overlaps_framing:
                            # Overlaps both - no offset (stay in middle)
                            offset = 0
                        elif overlaps_eff:
                            # Overlaps effective - slide right/down (positive)
                            offset = edge_slide_offset
                        elif overlaps_framing:
                            # Overlaps framing - slide left/up (negative)
                            offset = -edge_slide_offset
                        else:
                            offset = 0
                        draw_single_edge_arrow(
                            buf, layer.x, layer.y, layer.width, layer.height, edge, arrow_size_along, arrow_size_perp, arrow_color, offset
                        )
                else:
                    # No overlap - use standard rendering
                    draw_rect_corner_triangles(
                        buf, layer.x, layer.y, layer.width, layer.height, triangle_size_x, triangle_size_y, arrow_color
                    )
                    draw_rect_edge_arrows_single(
                        buf, layer.x, layer.y, layer.width, layer.height, arrow_size_along, arrow_size_perp, arrow_color, 0
                    )

            elif is_framing:
                # Framing can overlap with effective and protection (both outer)
                has_eff_overlap = any(eff_framing_edge_overlap.values()) or any(eff_framing_corner_overlap.values())
                has_prot_overlap = any(prot_framing_edge_overlap.values()) or any(prot_framing_corner_overlap.values())
                has_any_overlap = has_eff_overlap or has_prot_overlap

                if has_any_overlap:
                    # Framing with overlap: draw corners individually with smaller triangles
                    corner_info = [
                        ("top_left", layer.x, layer.y),
                        ("top_right", layer.x + layer.width - 1, layer.y),
                        ("bottom_left", layer.x, layer.y + layer.height - 1),
                        ("bottom_right", layer.x + layer.width - 1, layer.y + layer.height - 1),
                    ]
                    for corner_name, corner_x, corner_y in corner_info:
                        overlaps_eff = eff_framing_corner_overlap.get(corner_name, False)
                        overlaps_prot = prot_framing_corner_overlap.get(corner_name, False)
                        if overlaps_eff and overlaps_prot:
                            # Overlaps both - use smallest size
                            draw_corner_triangle(
                                buf, corner_x, corner_y, small_triangle_size_x, small_triangle_size_y, corner_name, arrow_color
                            )
                        elif overlaps_eff or overlaps_prot:
                            # Overlaps one - use medium size
                            draw_corner_triangle(
                                buf, corner_x, corner_y, medium_triangle_size_x, medium_triangle_size_y, corner_name, arrow_color
                            )
                        else:
                            draw_corner_triangle(buf, corner_x, corner_y, triangle_size_x, triangle_size_y, corner_name, arrow_color)

                    # Draw edge arrows with positive offset (slide right/down) on overlapping edges
                    for edge in ["top", "bottom", "left", "right"]:
                        overlaps_eff = eff_framing_edge_overlap.get(edge, False)
                        overlaps_prot = prot_framing_edge_overlap.get(edge, False)
                        if overlaps_eff or overlaps_prot:
                            offset = edge_slide_offset
                        else:
                            offset = 0
                        draw_single_edge_arrow(
                            buf, layer.x, layer.y, layer.width, layer.height, edge, arrow_size_along, arrow_size_perp, arrow_color, offset
                        )
                else:
                    # No overlap - use standard rendering
                    draw_rect_corner_triangles(
                        buf, layer.x, layer.y, layer.width, layer.height, triangle_size_x, triangle_size_y, arrow_color
                    )
                    draw_rect_edge_arrows_single(
                        buf, layer.x, layer.y, layer.width, layer.height, arrow_size_along, arrow_size_perp, arrow_color, 0
                    )

            else:
                # Unknown layer type - use original logic with bounds tracking
                if bounds in seen_bounds:
                    offset_multiplier = seen_bounds[bounds]
                    seen_bounds[bounds] += 1
                else:
                    offset_multiplier = 0
                    seen_bounds[bounds] = 1

                # Calculate offset (move arrows inward when there's overlap)
                offset = offset_multiplier * int(arrow_size_base * 1.2)

                # Draw corner triangles (offset inward if needed)
                draw_rect_corner_triangles(
                    buf,
                    layer.x + offset,
                    layer.y + offset,
                    layer.width - 2 * offset,
                    layer.height - 2 * offset,
                    triangle_size_x,
                    triangle_size_y,
                    arrow_color,
                )

                # Draw 1 edge arrow per side (offset inward if needed)
                draw_rect_edge_arrows_single(
                    buf,
                    layer.x + offset,
                    layer.y + offset,
                    layer.width - 2 * offset,
                    layer.height - 2 * offset,
                    arrow_size_along,
                    arrow_size_perp,
                    arrow_color,
                    0,
                )

        # Get framing layer for circles/crosshair
        framing_layer = None
        for layer in layers:
            if layer.name == "framing":
                framing_layer = layer
                break

        if framing_layer:
            # Use the framing arrow color for crosshair and circles
            indicator_color = self._get_arrow_color("framing")

            # Crosshair inside framing
            if vis.crosshair:
                self._render_crosshair(buf, framing_layer, squeeze_comp, indicator_color)

            # Reference circles inside framing
            if vis.squeeze_circle:
                self._render_reference_circles(buf, canvas, framing_layer, squeeze_comp, indicator_color)

        # Shared label position tracker for both dimension and anchor labels
        # Format: (x, y, width, height, layer_name)
        label_positions: list[tuple[int, int, int, int, str]] = []

        # Dimension labels
        if vis.dimension_labels:
            self._render_dimension_labels(buf, canvas, framing, layers, label_positions, squeeze_comp)

        # Anchor labels
        if vis.anchor_labels:
            self._render_anchor_labels(buf, canvas, framing, layers, label_positions, squeeze_comp)

        # Logo (rendered last so it's on top)
        if self.config.show_logo and framing_layer:
            self._render_logo(buf, framing_layer, squeeze_comp)

        # Metadata overlay (below crosshair)
        if self.config.show_metadata and framing_layer:
            self._render_metadata(buf, canvas, framing, framing_layer, squeeze_comp)

    def _get_layer_hierarchy(self, canvas: Canvas, framing: FramingDecision) -> list[LayerRect]:
        """
        Get layer rectangles from outermost to innermost.

        Parameters
        ----------
        canvas : Canvas
            The canvas containing dimension and effective area data.
        framing : FramingDecision
            The framing decision containing framing and protection data.

        Returns
        -------
        List[LayerRect]
            List of layer rectangles ordered from outermost to innermost.
        """
        layers = []
        vis = self.config.visibility

        # Canvas (outermost, darkest)
        if vis.canvas:
            x, y, w, h = canvas.get_rect()
            layers.append(LayerRect("canvas", int(x), int(y), int(w), int(h), self.config.color_canvas))

        # Effective (dark)
        eff_rect = canvas.get_effective_rect()
        if vis.effective and eff_rect is not None:
            x, y, w, h = eff_rect
            layers.append(LayerRect("effective", int(x), int(y), int(w), int(h), self.config.color_effective))

        # Protection (medium)
        prot_rect = framing.get_protection_rect()
        if vis.protection and prot_rect is not None:
            x, y, w, h = prot_rect
            layers.append(LayerRect("protection", int(x), int(y), int(w), int(h), self.config.color_protection))

        # Framing (innermost, lightest)
        if vis.framing:
            x, y, w, h = framing.get_rect()
            layers.append(LayerRect("framing", int(x), int(y), int(w), int(h), self.config.color_framing))

        return layers

    def _render_grid(self, buf: ImageBuf, width: int, height: int) -> None:
        """
        Render grid overlay.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to render onto.
        width : int
            Width of the grid area.
        height : int
            Height of the grid area.
        """
        draw_grid(buf, width, height, self.config.grid_spacing, LINE_WIDTH_GRID, COLOR_GRID)

    def _render_crosshair(
        self,
        buf: ImageBuf,
        framing_layer: LayerRect,
        squeeze_comp: float,
        color: RGBA,
    ) -> None:
        """
        Render crosshair at framing center.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to render onto.
        framing_layer : LayerRect
            The framing layer rectangle.
        squeeze_comp : float
            Squeeze compensation factor (1.0 / anamorphic_squeeze).
        color : RGBA
            Color for the crosshair.
        """
        center_x = framing_layer.x + framing_layer.width // 2
        center_y = framing_layer.y + framing_layer.height // 2

        base_size = int(min(framing_layer.width, framing_layer.height) / 30)
        base_size = max(base_size, 15)

        size_x = int(base_size * squeeze_comp)
        size_y = base_size

        draw_crosshair(buf, center_x, center_y, size_x, size_y, 2, color)

    def _render_reference_circles(
        self,
        buf: ImageBuf,
        canvas: Canvas,
        framing_layer: LayerRect,
        squeeze_comp: float,
        color: RGBA,
    ) -> None:
        """
        Render 1-3 reference circles inside framing dimension.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to render onto.
        canvas : Canvas
            The canvas containing anamorphic squeeze data.
        framing_layer : LayerRect
            The framing layer rectangle.
        squeeze_comp : float
            Squeeze compensation factor (1.0 / anamorphic_squeeze).
        color : RGBA
            Color for the reference circles.
        """
        squeeze = canvas.anamorphic_squeeze

        center_x = framing_layer.x + framing_layer.width // 2
        center_y = framing_layer.y + framing_layer.height // 2

        max_radius = min(framing_layer.width, framing_layer.height) // 2 - 20

        if max_radius < 50:
            return

        # Number of circles based on size
        if max_radius < 150:
            num_circles = 1
        elif max_radius < 300:
            num_circles = 2
        else:
            num_circles = 3

        for i in range(num_circles):
            ratio = (i + 1) / num_circles
            radius = int(max_radius * ratio)

            radius_x = int(radius * squeeze_comp)
            radius_y = radius

            draw_ellipse(buf, center_x, center_y, radius_x, radius_y, 2, color)

        if squeeze != 1.0:
            label_y = center_y + max_radius + 25
            render_squeeze_label(
                buf,
                squeeze,
                center_x,
                label_y,
                self.config.font_size_anchor,
                color,
                self.config.font_path,
                TextAlignment.CENTER,
                squeeze_comp=squeeze_comp,
            )

    def _render_dimension_labels(
        self,
        buf: ImageBuf,
        canvas: Canvas,
        framing: FramingDecision,
        layers: list[LayerRect],
        label_positions: list[tuple[int, int, int, int, str]],
        squeeze_comp: float = 1.0,
    ) -> None:
        """
        Render dimension labels for all visible rectangles.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to render onto.
        canvas : Canvas
            The canvas (unused, kept for consistency).
        framing : FramingDecision
            The framing decision (unused, kept for consistency).
        layers : List[LayerRect]
            List of layer rectangles to label.
        label_positions : List[Tuple[int, int, int, int, str]]
            Shared position tracker for all labels (x, y, width, height, layer_name).
            This list is modified in place to add new label positions.
        squeeze_comp : float
            Squeeze compensation factor (1.0 / anamorphic_squeeze).
        """
        font_size = self.config.font_size_dimension
        line_height = font_size + 10
        slide_amount = int(font_size * 3)  # Horizontal slide amount

        for layer in layers:
            if layer.name == "canvas":
                label = f"Canvas: {layer.width} x {layer.height}"
                text_width = int(len(label) * font_size * 0.6 * squeeze_comp)
                preferred_x = 15
                preferred_y = 10
                final_x, final_y = self._find_non_overlapping_position(
                    preferred_x, preferred_y, text_width, line_height, layer.name, label_positions, "horizontal", slide_amount
                )
                render_text_bold(
                    buf,
                    label,
                    final_x,
                    final_y,
                    font_size,
                    self.config.color_text,
                    self.config.font_path,
                    TextAlignment.LEFT,
                    squeeze_comp=squeeze_comp,
                )
                label_positions.append((final_x, final_y, text_width, line_height, layer.name))

            elif layer.name == "effective":
                label = f"Effective: {layer.width} x {layer.height}"
                text_width = int(len(label) * font_size * 0.6 * squeeze_comp)
                preferred_x = layer.x + 15
                preferred_y = layer.y + 10
                final_x, final_y = self._find_non_overlapping_position(
                    preferred_x, preferred_y, text_width, line_height, layer.name, label_positions, "horizontal", slide_amount
                )
                render_text_bold(
                    buf,
                    label,
                    final_x,
                    final_y,
                    font_size,
                    self.config.color_text,
                    self.config.font_path,
                    TextAlignment.LEFT,
                    squeeze_comp=squeeze_comp,
                )
                label_positions.append((final_x, final_y, text_width, line_height, layer.name))

            elif layer.name == "protection":
                label = f"Protection: {layer.width} x {layer.height}"
                text_width = int(len(label) * font_size * 0.6 * squeeze_comp)
                preferred_x = layer.x + layer.width - text_width - 15
                preferred_y = layer.y + layer.height - line_height - 10
                final_x, final_y = self._find_non_overlapping_position(
                    preferred_x, preferred_y, text_width, line_height, layer.name, label_positions, "horizontal", slide_amount
                )
                render_text_bold(
                    buf,
                    label,
                    final_x,
                    final_y,
                    font_size,
                    self.config.color_text,
                    self.config.font_path,
                    TextAlignment.LEFT,
                    squeeze_comp=squeeze_comp,
                )
                label_positions.append((final_x, final_y, text_width, line_height, layer.name))

            elif layer.name == "framing":
                label = f"Framing: {layer.width} x {layer.height}"
                text_width = int(len(label) * font_size * 0.6 * squeeze_comp)
                preferred_x = layer.x + (layer.width - text_width) // 2
                preferred_y = layer.y + 15
                final_x, final_y = self._find_non_overlapping_position(
                    preferred_x, preferred_y, text_width, line_height, layer.name, label_positions, "horizontal", slide_amount
                )
                render_text_bold(
                    buf,
                    label,
                    final_x,
                    final_y,
                    font_size,
                    self.config.color_text,
                    self.config.font_path,
                    TextAlignment.LEFT,
                    squeeze_comp=squeeze_comp,
                )
                label_positions.append((final_x, final_y, text_width, line_height, layer.name))

    def _render_anchor_labels(
        self,
        buf: ImageBuf,
        canvas: Canvas,
        framing: FramingDecision,
        layers: list[LayerRect],
        label_positions: list[tuple[int, int, int, int, str]],
        squeeze_comp: float = 1.0,
    ) -> None:
        """
        Render anchor point labels.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to render onto.
        canvas : Canvas
            The canvas providing dimension data.
        framing : FramingDecision
            The framing decision (unused, kept for consistency).
        layers : List[LayerRect]
            List of layer rectangles to label.
        label_positions : List[Tuple[int, int, int, int, str]]
            Shared position tracker for all labels (x, y, width, height, layer_name).
            This list is modified in place to add new label positions.
        squeeze_comp : float
            Squeeze compensation factor (1.0 / anamorphic_squeeze).
        """
        font_size = self.config.font_size_anchor
        line_height = font_size + 8
        slide_amount = int(font_size * 3)  # Horizontal slide amount

        # Map layer names to display names for anchor labels
        layer_display_names = {
            "effective": "Effective",
            "protection": "Protection",
            "framing": "Framing",
        }

        for layer in layers:
            # Skip canvas - no anchor label needed
            if layer.name == "canvas":
                continue

            display_name = layer_display_names.get(layer.name, layer.name.capitalize())
            label = f"{display_name} Anchor: {layer.x}, {layer.y}"
            text_width = int(len(label) * font_size * 0.6 * squeeze_comp)

            if layer.name == "effective":
                # Top-left (matches effective dimension label position)
                preferred_x = layer.x + 15
                preferred_y = layer.y + 15
            elif layer.name == "protection":
                # Bottom-right (matches protection dimension label position)
                preferred_x = layer.x + layer.width - text_width - 15
                preferred_y = layer.y + layer.height - line_height - 15
            elif layer.name == "framing":
                # Left side, vertically centered
                preferred_x = layer.x + 15
                preferred_y = layer.y + layer.height // 2
            else:
                continue

            final_x, final_y = self._find_non_overlapping_position(
                preferred_x, preferred_y, text_width, line_height, layer.name, label_positions, "horizontal", slide_amount
            )
            render_text_bold(
                buf,
                label,
                final_x,
                final_y,
                font_size,
                self.config.color_text,
                self.config.font_path,
                TextAlignment.LEFT,
                squeeze_comp=squeeze_comp,
            )
            label_positions.append((final_x, final_y, text_width, line_height, layer.name))

    def _render_logo(
        self,
        buf: ImageBuf,
        framing_layer: LayerRect,
        squeeze_comp: float = 1.0,
    ) -> None:
        """
        Render the logo centered between the crosshair and the framing top edge.

        The logo is sized to cover no more than 50% of the vertical space between
        the crosshair center and the framing decision top edge. Width is calculated
        from this height while maintaining the logo's aspect ratio, then adjusted
        by the squeeze compensation factor (1/squeeze) so the logo appears
        geometrically correct in anamorphic content.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to render onto.
        framing_layer : LayerRect
            The framing layer rectangle for positioning reference.
        squeeze_comp : float
            Squeeze compensation factor (1.0 / anamorphic_squeeze).
        """
        # Determine logo path
        logo_path = self.config.logo_path
        if logo_path is None:
            logo_path = DEFAULT_LOGO_PATH
        else:
            logo_path = Path(logo_path)

        if not logo_path.exists():
            return

        # Load the logo image
        logo_buf = ImageBuf(str(logo_path))
        if logo_buf.has_error:
            return

        # Get original dimensions
        orig_width = logo_buf.spec().width
        orig_height = logo_buf.spec().height

        if orig_width <= 0 or orig_height <= 0:
            return

        # Calculate positioning reference points
        framing_top_y = framing_layer.y
        crosshair_y = framing_layer.y + framing_layer.height // 2
        center_x = framing_layer.x + framing_layer.width // 2

        # Distance from framing top to crosshair center
        available_height = crosshair_y - framing_top_y

        if available_height <= 0:
            return

        # Logo max height is 50% of the available space
        max_logo_height = available_height * 0.5

        # Calculate scale to fit within max height while maintaining aspect ratio,
        # then apply squeeze compensation so the logo appears correct in anamorphic content.
        aspect_ratio = orig_width / orig_height
        new_height = int(max_logo_height)
        new_width = int(new_height * aspect_ratio * squeeze_comp)

        if new_width <= 0 or new_height <= 0:
            return

        # Resize the logo using ROI
        from OpenImageIO import ROI

        dst_roi = ROI(0, new_width, 0, new_height, 0, 1, 0, logo_buf.nchannels)
        scaled_logo = ImageBuf()
        ImageBufAlgo.resize(scaled_logo, logo_buf, roi=dst_roi)

        # Position logo at center point between framing top and crosshair
        # Center point Y = framing_top_y + available_height / 2
        logo_center_y = framing_top_y + available_height // 2
        logo_x = center_x - new_width // 2
        logo_y = logo_center_y - new_height // 2

        # Ensure logo doesn't go off the top of the image
        if logo_y < 0:
            logo_y = 0

        # Paste the logo onto the buffer using over compositing
        # For RGB images, we need to handle alpha from the logo
        if scaled_logo.nchannels == 4:
            # Logo has alpha - composite it
            for y in range(new_height):
                for x in range(new_width):
                    dst_x = logo_x + x
                    dst_y = logo_y + y

                    # Skip if outside buffer bounds
                    if dst_x < 0 or dst_x >= buf.spec().width:
                        continue
                    if dst_y < 0 or dst_y >= buf.spec().height:
                        continue

                    # Get logo pixel (RGBA)
                    logo_pixel = scaled_logo.getpixel(x, y)
                    if logo_pixel is None or len(logo_pixel) < 4:
                        continue

                    alpha = logo_pixel[3]
                    if alpha < 0.01:
                        continue  # Fully transparent, skip

                    # Get destination pixel
                    dst_pixel = list(buf.getpixel(dst_x, dst_y))
                    if dst_pixel is None:
                        continue

                    # Alpha composite: result = src * alpha + dst * (1 - alpha)
                    for c in range(min(3, len(dst_pixel))):
                        dst_pixel[c] = logo_pixel[c] * alpha + dst_pixel[c] * (1.0 - alpha)

                    buf.setpixel(dst_x, dst_y, tuple(dst_pixel))
        else:
            # Logo is RGB - direct copy
            ImageBufAlgo.paste(buf, logo_x, logo_y, 0, 0, scaled_logo)

    def _render_metadata(
        self,
        buf: ImageBuf,
        canvas: Canvas,
        framing: FramingDecision,
        framing_layer: LayerRect,
        squeeze_comp: float = 1.0,
    ) -> None:
        """
        Render metadata overlay below the crosshair.

        Displays camera info, show name, DOP, sensor mode, framing decision
        dimensions, and aspect ratio.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to render onto.
        canvas : Canvas
            The canvas for squeeze information.
        framing : FramingDecision
            The framing decision for dimension and aspect ratio data.
        framing_layer : LayerRect
            The framing layer rectangle for positioning reference.
        squeeze_comp : float
            Squeeze compensation factor (1.0 / anamorphic_squeeze).
        """
        # Calculate positioning reference points
        crosshair_y = framing_layer.y + framing_layer.height // 2
        framing_bottom_y = framing_layer.y + framing_layer.height
        center_x = framing_layer.x + framing_layer.width // 2

        # Available space below crosshair
        available_height = framing_bottom_y - crosshair_y

        if available_height <= 0:
            return

        # Font sizes - base on available height
        # Camera name is largest (about 3% of framing height, min 24px)
        camera_font_size = max(24, int(framing_layer.height * 0.03))
        # Other text is smaller (about 2% of framing height, min 18px)
        detail_font_size = max(18, int(framing_layer.height * 0.02))
        line_spacing = int(detail_font_size * 1.4)

        # Get text color
        text_color = self.config.color_text

        # Prepare metadata lines
        lines = []

        # Camera Make & Model (largest, first line)
        camera = self.config.metadata_camera or "Unknown"
        lines.append(("camera", camera, camera_font_size))

        # Show name
        show_name = self.config.metadata_show or "Unknown"
        show_text = f"Show: {show_name}"
        lines.append(("detail", show_text, detail_font_size))

        # DOP
        dop = self.config.metadata_dop or "Unknown"
        dop_text = f"DOP: {dop}"
        lines.append(("detail", dop_text, detail_font_size))

        # Sensor Mode
        sensor_mode = self.config.metadata_sensor_mode or "Unknown"
        sensor_text = f"Sensor Mode: {sensor_mode}"
        lines.append(("detail", sensor_text, detail_font_size))

        # Framing Decision Dimensions (calculated from FDL)
        fd_width = int(framing.dimensions.width)
        fd_height = int(framing.dimensions.height)
        fd_text = f"Framing Decision: {fd_width} x {fd_height}"
        lines.append(("detail", fd_text, detail_font_size))

        # Aspect Ratio (calculated from FDL)
        aspect_ratio = framing.dimensions.width / framing.dimensions.height
        squeeze = canvas.anamorphic_squeeze

        if squeeze == 1.0:
            aspect_text = f"Aspect Ratio: {aspect_ratio:.2f}:1 Spherical"
        else:
            # For anamorphic, show the squeezed aspect ratio
            aspect_text = f"Aspect Ratio: {aspect_ratio:.2f}:1 Anamorphic ({squeeze:.2f}x)"
        lines.append(("detail", aspect_text, detail_font_size))

        # Calculate total height of all lines
        total_height = camera_font_size  # First line
        for line_type, _, font_size in lines[1:]:
            total_height += line_spacing

        # Position: center the text block in the space below crosshair
        # Start Y position - center the block vertically in available space
        start_y = crosshair_y + (available_height - total_height) // 2

        # Ensure we don't overlap with crosshair
        min_start_y = crosshair_y + int(detail_font_size * 1.5)
        if start_y < min_start_y:
            start_y = min_start_y

        # Render each line
        current_y = start_y
        for line_type, text, font_size in lines:
            render_text(
                buf,
                text,
                center_x,
                current_y,
                font_size,
                text_color,
                self.config.font_path,
                TextAlignment.CENTER,
                squeeze_comp=squeeze_comp,
            )
            if line_type == "camera":
                current_y += int(font_size * 1.5)  # More space after camera name
            else:
                current_y += line_spacing

    def _write_output(self, buf: ImageBuf, output_path: Path) -> bool:
        """
        Write the image buffer to file.

        Parameters
        ----------
        buf : ImageBuf
            The image buffer to write.
        output_path : Path
            The output file path.

        Returns
        -------
        bool
            True if writing succeeded.

        Raises
        ------
        IOError
            If the output file cannot be written.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        buf.write(str(output_path))

        if buf.has_error:
            raise OSError(f"Failed to write output image: {buf.geterror()}")

        return True
