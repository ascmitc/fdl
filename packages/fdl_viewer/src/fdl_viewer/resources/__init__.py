# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Resources package for FDL Viewer.

Contains icons, stylesheets, and other static resources.
"""

import sys
from pathlib import Path


def _get_resources_dir() -> Path:
    """
    Get the resources directory, handling both frozen and non-frozen cases.

    When running as a PyInstaller frozen app, resources are extracted to
    sys._MEIPASS. Otherwise, use the package directory.

    Returns
    -------
    Path
        The path to the resources directory.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as frozen app - resources are in _MEIPASS/resources
        return Path(sys._MEIPASS) / "resources"
    else:
        # Running from source - resources are in this package
        return Path(__file__).parent


RESOURCES_DIR = _get_resources_dir()


def get_resource_path(filename: str) -> Path:
    """
    Get the path to a resource file.

    Parameters
    ----------
    filename : str
        The name of the resource file.

    Returns
    -------
    Path
        The full path to the resource file.
    """
    return RESOURCES_DIR / filename


def get_icon_path(icon_name: str) -> Path:
    """
    Get the path to an icon file.

    Parameters
    ----------
    icon_name : str
        The name of the icon file.

    Returns
    -------
    Path
        The full path to the icon file.
    """
    return RESOURCES_DIR / "icons" / icon_name


def get_stylesheet_path(style_name: str) -> Path:
    """
    Get the path to a stylesheet file.

    Parameters
    ----------
    style_name : str
        The name of the stylesheet file.

    Returns
    -------
    Path
        The full path to the stylesheet file.
    """
    return RESOURCES_DIR / "styles" / style_name


def load_stylesheet(style_name: str) -> str:
    """
    Load a stylesheet file and return its contents.

    Replaces {{ICONS_DIR}} placeholder with the actual icons directory path.

    Parameters
    ----------
    style_name : str
        The name of the stylesheet file.

    Returns
    -------
    str
        The contents of the stylesheet file with paths resolved.
    """
    content = ""

    # Try the standard path first
    path = get_stylesheet_path(style_name)
    if path.exists():
        content = path.read_text(encoding="utf-8")

    # For frozen apps, try additional fallback paths
    if not content and getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        meipass = Path(sys._MEIPASS)
        fallback_paths = [
            meipass / "resources" / "styles" / style_name,
            meipass / "styles" / style_name,
            meipass / style_name,
            # macOS app bundle paths
            meipass.parent / "Resources" / "resources" / "styles" / style_name,
            meipass.parent / "Resources" / "styles" / style_name,
        ]
        for fallback in fallback_paths:
            if fallback.exists():
                content = fallback.read_text(encoding="utf-8")
                break

    # Replace icon path placeholder with actual path
    if content:
        icons_dir = RESOURCES_DIR / "icons"
        # Convert to forward slashes for Qt and escape for URL
        icons_path = str(icons_dir).replace("\\", "/")
        content = content.replace("{{ICONS_DIR}}", icons_path)

    return content
