# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
FDL-based image processing using OpenImageIO.

Provides functions to process images according to FDL (Framing Decision List)
specifications, applying transformations such as cropping, resizing, and extraction.
Also provides drawing primitives, text rendering, and color utilities.
"""

from fdl_imaging._processing import (
    extract_framing_region,
    get_fdl_components,
    process_image_with_fdl,
    process_image_with_fdl_template,
    transform_image_with_computed_values,
)
from fdl_imaging.colors import DEFAULT_DASH_PATTERN, RGBA, hex_to_rgba

__all__ = [
    "DEFAULT_DASH_PATTERN",
    "RGBA",
    "extract_framing_region",
    "get_fdl_components",
    "hex_to_rgba",
    "process_image_with_fdl",
    "process_image_with_fdl_template",
    "transform_image_with_computed_values",
]
