# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
"""FDL Core constants — standalone StrEnum definitions."""

from __future__ import annotations

from enum import Enum


class _StrEnum(str, Enum):
    """str Enum base that formats as the value, not ``ClassName.MEMBER``."""

    __str__ = str.__str__


class RoundingMode(_StrEnum):
    UP = "up"
    DOWN = "down"
    ROUND = "round"


class RoundingEven(_StrEnum):
    WHOLE = "whole"
    EVEN = "even"


class GeometryPath(_StrEnum):
    CANVAS_DIMENSIONS = "canvas.dimensions"
    CANVAS_EFFECTIVE_DIMENSIONS = "canvas.effective_dimensions"
    FRAMING_PROTECTION_DIMENSIONS = "framing_decision.protection_dimensions"
    FRAMING_DIMENSIONS = "framing_decision.dimensions"


class FitMethod(_StrEnum):
    WIDTH = "width"
    HEIGHT = "height"
    FIT_ALL = "fit_all"
    FILL = "fill"


class HAlign(_StrEnum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VAlign(_StrEnum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


# ---------------------------------------------------------------------------
# Floating-point comparison
# ---------------------------------------------------------------------------

FP_REL_TOL = 1e-9
FP_ABS_TOL = 1e-6

# ---------------------------------------------------------------------------
# First-class custom attribute name constants
# ---------------------------------------------------------------------------

ATTR_SCALE_FACTOR: str = "scale_factor"
"""Custom attribute name for the template scale factor (float)."""

ATTR_CONTENT_TRANSLATION: str = "content_translation"
"""Custom attribute name for the template content translation (PointFloat)."""

ATTR_SCALED_BOUNDING_BOX: str = "scaled_bounding_box"
"""Custom attribute name for the template scaled bounding box (DimensionsFloat)."""
