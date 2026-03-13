# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
FDL Frameline Generator - Generate frameline overlay images from FDL files.

This package provides tools to create frameline overlay images from
ASC FDL (Framing Decision List) files.  Raster formats (EXR, PNG, TIFF)
are supported via OpenImageIO, and SVG vector output is also available.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("asc-fdl-frameline-generator")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback if package is not installed

__author__ = "FDL Frameline Generator Contributors"

from fdl_frameline_generator.config import LayerVisibility, RenderConfig
from fdl_frameline_generator.renderer import FramelineRenderer
from fdl_frameline_generator.svg_backend import SvgDocument

__all__ = [
    "FramelineRenderer",
    "LayerVisibility",
    "RenderConfig",
    "SvgDocument",
    "__version__",
]
