# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
FDL Viewer - A PySide6 application for viewing and transforming Framing Decision List files.

This package provides a graphical user interface for loading, viewing, and transforming
FDL files using the fdl and fdl_imaging libraries.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("asc-fdl-viewer")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback if package is not installed

__author__ = "FDL Viewer Contributors"

from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel

__all__ = [
    "AppState",
    "FDLModel",
    "__version__",
]
