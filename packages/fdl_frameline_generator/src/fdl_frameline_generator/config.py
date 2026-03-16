# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Configuration dataclasses for the frameline renderer.
"""

from dataclasses import dataclass, field
from pathlib import Path

from fdl_frameline_generator.colors import (
    COLOR_ARROW_CANVAS,
    COLOR_ARROW_EFFECTIVE,
    COLOR_ARROW_FRAMING,
    COLOR_ARROW_PROTECTION,
    COLOR_BACKGROUND,
    COLOR_CANVAS,
    COLOR_EFFECTIVE,
    COLOR_FRAMING,
    COLOR_PROTECTION,
    COLOR_SQUEEZE_CIRCLE,
    COLOR_TEXT,
    FONT_SIZE_ANCHOR,
    FONT_SIZE_DIMENSION,
    LINE_WIDTH_CANVAS,
    LINE_WIDTH_EFFECTIVE,
    LINE_WIDTH_FRAMING,
    LINE_WIDTH_PROTECTION,
    RGBA,
)


@dataclass
class LayerVisibility:
    """
    Controls which layers are rendered in the frameline image.

    Attributes
    ----------
    canvas : bool
        Show the canvas outline (outermost boundary)
    effective : bool
        Show the effective dimensions rectangle
    protection : bool
        Show the protection area (dashed rectangle)
    framing : bool
        Show the framing decision rectangle
    squeeze_circle : bool
        Show the anamorphic squeeze reference circle
    dimension_labels : bool
        Show dimension labels (width x height)
    anchor_labels : bool
        Show anchor point coordinates
    crosshair : bool
        Show crosshair at framing center
    grid : bool
        Show grid overlay
    """

    canvas: bool = True
    effective: bool = True
    protection: bool = True
    framing: bool = True
    squeeze_circle: bool = True
    dimension_labels: bool = True
    anchor_labels: bool = True
    crosshair: bool = True
    grid: bool = False


@dataclass
class RenderConfig:
    """
    Configuration for rendering frameline images.

    Attributes
    ----------
    visibility : LayerVisibility
        Controls which layers are visible
    line_width_canvas : int
        Line width for canvas outline in pixels
    line_width_effective : int
        Line width for effective dimensions in pixels
    line_width_protection : int
        Line width for protection area in pixels
    line_width_framing : int
        Line width for framing decision in pixels
    color_canvas : RGBA
        Color for canvas outline
    color_effective : RGBA
        Color for effective dimensions
    color_protection : RGBA
        Color for protection area
    color_framing : RGBA
        Color for framing decision
    color_squeeze : RGBA
        Color for squeeze reference circle
    color_background : RGBA
        Background color (transparent by default)
    font_size_dimension : int
        Font size for dimension labels
    font_size_anchor : int
        Font size for anchor point labels
    font_path : str or None
        Path to custom font file (uses system default if None)
    grid_spacing : int
        Grid line spacing in pixels
    """

    visibility: LayerVisibility = field(default_factory=LayerVisibility)

    # Line widths
    line_width_canvas: int = LINE_WIDTH_CANVAS
    line_width_effective: int = LINE_WIDTH_EFFECTIVE
    line_width_protection: int = LINE_WIDTH_PROTECTION
    line_width_framing: int = LINE_WIDTH_FRAMING

    # Colors for dimension areas
    color_canvas: RGBA = COLOR_CANVAS
    color_effective: RGBA = COLOR_EFFECTIVE
    color_protection: RGBA = COLOR_PROTECTION
    color_framing: RGBA = COLOR_FRAMING
    color_squeeze: RGBA = COLOR_SQUEEZE_CIRCLE
    color_background: RGBA = COLOR_BACKGROUND

    # Colors for arrows/indicators on each layer
    color_arrow_canvas: RGBA = COLOR_ARROW_CANVAS
    color_arrow_effective: RGBA = COLOR_ARROW_EFFECTIVE
    color_arrow_protection: RGBA = COLOR_ARROW_PROTECTION
    color_arrow_framing: RGBA = COLOR_ARROW_FRAMING

    # Color for text labels
    color_text: RGBA = COLOR_TEXT

    # Font settings
    font_size_dimension: int = FONT_SIZE_DIMENSION
    font_size_anchor: int = FONT_SIZE_ANCHOR
    font_path: str | None = None

    # Grid settings
    grid_spacing: int = 100

    # Logo settings
    show_logo: bool = True
    logo_path: str | Path | None = None  # None means use default logo
    logo_scale: float = 1.0 / 3.0  # Pre-scale factor (default: 1/3)

    # Metadata overlay settings
    show_metadata: bool = True
    metadata_camera: str | None = None  # Camera Make & Model, defaults to "Unknown"
    metadata_show: str | None = None  # Show name
    metadata_dop: str | None = None  # DOP name
    metadata_sensor_mode: str | None = None  # Sensor mode
