# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
"""FDL Core rounding — RoundStrategy value type and rounding functions."""

from __future__ import annotations

from .constants import RoundingEven, RoundingMode
from .fdl_types import DimensionsFloat


class RoundStrategy:
    """Lightweight RoundStrategy value type."""

    __slots__ = ("even", "mode")

    def __init__(self, *, even: RoundingEven = RoundingEven.EVEN, mode: RoundingMode = RoundingMode.UP) -> None:
        self.even: RoundingEven = even
        self.mode: RoundingMode = mode

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoundStrategy):
            return NotImplemented
        return self.even == other.even and self.mode == other.mode

    def __hash__(self) -> int:
        return hash((self.even, self.mode))

    def __iter__(self):
        return iter((self.even, self.mode))

    def __repr__(self) -> str:
        return f"RoundStrategy(even={self.even!r}, mode={self.mode!r})"


def fdl_round(value: float, even: str, mode: str) -> int:
    """Round a single float value according to FDL rounding rules."""
    from fdl_ffi import get_lib

    from .enum_maps import ROUNDING_EVEN_TO_C, ROUNDING_MODE_TO_C

    return int(get_lib().fdl_round(float(value), ROUNDING_EVEN_TO_C[even], ROUNDING_MODE_TO_C[mode]))


def calculate_scale_factor(fit_norm: DimensionsFloat, target_norm: DimensionsFloat, fit_method: str) -> float:
    """Calculate scale factor based on fit method."""
    from fdl_ffi import ffi, get_lib

    from .enum_maps import FIT_METHOD_TO_C

    _c_fit_norm = ffi.new("fdl_dimensions_f64_t*", {"width": fit_norm.width, "height": fit_norm.height})[0]
    _c_target_norm = ffi.new("fdl_dimensions_f64_t*", {"width": target_norm.width, "height": target_norm.height})[0]
    return float(get_lib().fdl_calculate_scale_factor(_c_fit_norm, _c_target_norm, FIT_METHOD_TO_C[fit_method]))
