# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Color scheme constants for FDL frameline rendering.

Generic color utilities (RGBA, hex_to_rgba) are provided by fdl_imaging.colors.
This module re-exports them and defines frameline-specific color constants.
"""

from fdl_imaging.colors import RGBA, hex_to_rgba  # noqa: F401

# Dimension area colors (grayscale gradient from inner to outer)
COLOR_FRAMING: RGBA = (0.55, 0.55, 0.55, 1.0)  # Medium gray - innermost
COLOR_PROTECTION: RGBA = (0.22, 0.22, 0.22, 1.0)  # Dark gray
COLOR_EFFECTIVE: RGBA = (0.12, 0.12, 0.12, 1.0)  # Darker gray
COLOR_CANVAS: RGBA = (0.02, 0.02, 0.02, 1.0)  # Near black - outermost

# Arrow/indicator colors for each layer type
COLOR_ARROW_FRAMING: RGBA = (0.2, 0.02, 0.02, 1.0)  # Dark red on framing
COLOR_ARROW_PROTECTION: RGBA = (0.05, 0.05, 0.05, 1.0)  # Very dark gray on protection
COLOR_ARROW_EFFECTIVE: RGBA = (0.3, 0.3, 0.3, 1.0)  # Medium gray on effective
COLOR_ARROW_CANVAS: RGBA = (1.0, 1.0, 1.0, 1.0)  # White on canvas

# Other UI elements
COLOR_GRID: RGBA = (0.3, 0.3, 0.3, 1.0)  # Medium gray
COLOR_TEXT: RGBA = (0.0, 0.0, 0.0, 1.0)  # Black for text
COLOR_SQUEEZE_CIRCLE: RGBA = (0.8, 0.8, 0.8, 1.0)  # Light gray for squeeze reference

# Background color (solid, matches framing since it's the innermost visible area)
COLOR_BACKGROUND: RGBA = (0.55, 0.55, 0.55, 1.0)

# Line widths in pixels
LINE_WIDTH_CANVAS: int = 3
LINE_WIDTH_EFFECTIVE: int = 2
LINE_WIDTH_PROTECTION: int = 2
LINE_WIDTH_FRAMING: int = 3
LINE_WIDTH_GRID: int = 1

# Dash pattern for protection lines (on_pixels, off_pixels)
DASH_PATTERN_PROTECTION: tuple[int, int] = (10, 5)

# Text sizes
FONT_SIZE_DIMENSION: int = 24
FONT_SIZE_ANCHOR: int = 18
