# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""Enum forward/reverse maps between C uint32 constants and Python StrEnum values."""

from __future__ import annotations

from .constants import (
    RoundingMode,
    RoundingEven,
    GeometryPath,
    FitMethod,
    HAlign,
    VAlign,
)
from fdl_ffi import (
    FDL_ROUNDING_MODE_UP,
    FDL_ROUNDING_MODE_DOWN,
    FDL_ROUNDING_MODE_ROUND,
    FDL_ROUNDING_EVEN_WHOLE,
    FDL_ROUNDING_EVEN_EVEN,
    FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS,
    FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS,
    FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS,
    FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS,
    FDL_FIT_METHOD_WIDTH,
    FDL_FIT_METHOD_HEIGHT,
    FDL_FIT_METHOD_FIT_ALL,
    FDL_FIT_METHOD_FILL,
    FDL_HALIGN_LEFT,
    FDL_HALIGN_CENTER,
    FDL_HALIGN_RIGHT,
    FDL_VALIGN_TOP,
    FDL_VALIGN_CENTER,
    FDL_VALIGN_BOTTOM,
)


# fdl_rounding_mode_t ↔ RoundingMode
ROUNDING_MODE_FROM_C: dict[int, RoundingMode] = {
    FDL_ROUNDING_MODE_UP: RoundingMode.UP,
    FDL_ROUNDING_MODE_DOWN: RoundingMode.DOWN,
    FDL_ROUNDING_MODE_ROUND: RoundingMode.ROUND,
}
ROUNDING_MODE_TO_C: dict[RoundingMode, int] = {v: k for k, v in ROUNDING_MODE_FROM_C.items()}

# fdl_rounding_even_t ↔ RoundingEven
ROUNDING_EVEN_FROM_C: dict[int, RoundingEven] = {
    FDL_ROUNDING_EVEN_WHOLE: RoundingEven.WHOLE,
    FDL_ROUNDING_EVEN_EVEN: RoundingEven.EVEN,
}
ROUNDING_EVEN_TO_C: dict[RoundingEven, int] = {v: k for k, v in ROUNDING_EVEN_FROM_C.items()}

# fdl_geometry_path_t ↔ GeometryPath
GEOMETRY_PATH_FROM_C: dict[int, GeometryPath] = {
    FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS: GeometryPath.CANVAS_DIMENSIONS,
    FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS: GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
    FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS: GeometryPath.FRAMING_PROTECTION_DIMENSIONS,
    FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS: GeometryPath.FRAMING_DIMENSIONS,
}
GEOMETRY_PATH_TO_C: dict[GeometryPath, int] = {v: k for k, v in GEOMETRY_PATH_FROM_C.items()}

# fdl_fit_method_t ↔ FitMethod
FIT_METHOD_FROM_C: dict[int, FitMethod] = {
    FDL_FIT_METHOD_WIDTH: FitMethod.WIDTH,
    FDL_FIT_METHOD_HEIGHT: FitMethod.HEIGHT,
    FDL_FIT_METHOD_FIT_ALL: FitMethod.FIT_ALL,
    FDL_FIT_METHOD_FILL: FitMethod.FILL,
}
FIT_METHOD_TO_C: dict[FitMethod, int] = {v: k for k, v in FIT_METHOD_FROM_C.items()}

# fdl_halign_t ↔ HAlign
H_ALIGN_FROM_C: dict[int, HAlign] = {
    FDL_HALIGN_LEFT: HAlign.LEFT,
    FDL_HALIGN_CENTER: HAlign.CENTER,
    FDL_HALIGN_RIGHT: HAlign.RIGHT,
}
H_ALIGN_TO_C: dict[HAlign, int] = {v: k for k, v in H_ALIGN_FROM_C.items()}

# fdl_valign_t ↔ VAlign
V_ALIGN_FROM_C: dict[int, VAlign] = {
    FDL_VALIGN_TOP: VAlign.TOP,
    FDL_VALIGN_CENTER: VAlign.CENTER,
    FDL_VALIGN_BOTTOM: VAlign.BOTTOM,
}
V_ALIGN_TO_C: dict[VAlign, int] = {v: k for k, v in V_ALIGN_FROM_C.items()}
