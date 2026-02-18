# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""Value type converter functions — C struct ↔ Python value type."""

from __future__ import annotations

from .fdl_types import (
    DimensionsFloat,
    DimensionsInt,
    PointFloat,
    Rect,
)
from .rounding import (
    RoundStrategy,
)

from .constants import (
    RoundingEven,
    RoundingMode,
)


def _dims_i64(c_struct) -> DimensionsInt:
    """Convert fdl_dimensions_i64_t to DimensionsInt."""
    return DimensionsInt(
        width=int(c_struct.width),
        height=int(c_struct.height),
    )


def _to_c_dims_i64(val: DimensionsInt):
    """Convert DimensionsInt to C fdl_dimensions_i64_t struct."""
    from fdl_ffi import fdl_dimensions_i64_t

    c = fdl_dimensions_i64_t()
    c.width = int(val.width)
    c.height = int(val.height)
    return c


def _dims_f64(c_struct) -> DimensionsFloat:
    """Convert fdl_dimensions_f64_t to DimensionsFloat."""
    return DimensionsFloat(
        width=c_struct.width,
        height=c_struct.height,
    )


def _to_c_dims_f64(val: DimensionsFloat):
    """Convert DimensionsFloat to C fdl_dimensions_f64_t struct."""
    from fdl_ffi import fdl_dimensions_f64_t

    c = fdl_dimensions_f64_t()
    c.width = float(val.width)
    c.height = float(val.height)
    return c


def _point_f64(c_struct) -> PointFloat:
    """Convert fdl_point_f64_t to PointFloat."""
    return PointFloat(
        x=c_struct.x,
        y=c_struct.y,
    )


def _to_c_point_f64(val: PointFloat):
    """Convert PointFloat to C fdl_point_f64_t struct."""
    from fdl_ffi import fdl_point_f64_t

    c = fdl_point_f64_t()
    c.x = float(val.x)
    c.y = float(val.y)
    return c


def _rect(c_struct) -> Rect:
    """Convert fdl_rect_t to Rect."""
    return Rect(
        x=c_struct.x,
        y=c_struct.y,
        width=c_struct.width,
        height=c_struct.height,
    )


def _to_c_rect(val: Rect):
    """Convert Rect to C fdl_rect_t struct."""
    from fdl_ffi import fdl_rect_t

    c = fdl_rect_t()
    c.x = float(val.x)
    c.y = float(val.y)
    c.width = float(val.width)
    c.height = float(val.height)
    return c


def _round_strategy(c_struct) -> RoundStrategy:
    """Convert fdl_round_strategy_t to RoundStrategy."""
    from .enum_maps import ROUNDING_EVEN_FROM_C, ROUNDING_MODE_FROM_C

    return RoundStrategy(
        even=ROUNDING_EVEN_FROM_C.get(c_struct.even, RoundingEven.EVEN),
        mode=ROUNDING_MODE_FROM_C.get(c_struct.mode, RoundingMode.UP),
    )


def _to_c_round_strategy(val: RoundStrategy):
    """Convert RoundStrategy to C fdl_round_strategy_t struct."""
    from fdl_ffi import fdl_round_strategy_t
    from .enum_maps import ROUNDING_EVEN_TO_C, ROUNDING_MODE_TO_C

    c = fdl_round_strategy_t()
    c.even = ROUNDING_EVEN_TO_C[val.even]
    c.mode = ROUNDING_MODE_TO_C[val.mode]
    return c
