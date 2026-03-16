# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Generic color utilities for OIIO-based image operations.

Provides RGBA type alias and color conversion functions.
"""

# Type alias for RGBA color tuple
RGBA = tuple[float, float, float, float]

# Default dash pattern (on_pixels, off_pixels)
DEFAULT_DASH_PATTERN: tuple[int, int] = (10, 5)


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> RGBA:
    """
    Convert a hex color string to RGBA tuple.

    Parameters
    ----------
    hex_color : str
        Hex color string (e.g., "#808080" or "808080")
    alpha : float, optional
        Alpha value (0.0 to 1.0), default is 1.0

    Returns
    -------
    RGBA
        Tuple of (r, g, b, a) with values in [0.0, 1.0]
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b, alpha)
