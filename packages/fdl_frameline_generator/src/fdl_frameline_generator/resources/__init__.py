# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Resource management for the frameline generator package.

Provides access to bundled resources like the default logo.
"""

from importlib import resources
from pathlib import Path


def get_default_logo_path() -> Path:
    """
    Get the path to the default ASC FDL logo.

    Returns
    -------
    Path
        Path to the ASCFDL_Logo.png file bundled with the package.
    """
    # Use importlib.resources for Python 3.9+
    try:
        with resources.files(__package__).joinpath("ASCFDL_Logo.png") as logo_path:
            return Path(logo_path)
    except (TypeError, AttributeError):
        # Fallback for older Python or if resources.files doesn't work
        return Path(__file__).parent / "ASCFDL_Logo.png"


# Default logo path constant
DEFAULT_LOGO_PATH: Path = get_default_logo_path()
