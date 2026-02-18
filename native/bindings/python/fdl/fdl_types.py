# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
"""FDL Core value types — lightweight data classes (no Pydantic)."""

from __future__ import annotations

import math


def _load_fp_tolerances() -> tuple[float, float]:
    from fdl_ffi import get_lib

    lib = get_lib()
    return lib.fdl_fp_rel_tol(), lib.fdl_fp_abs_tol()


_FP_REL_TOL, _FP_ABS_TOL = _load_fp_tolerances()
del _load_fp_tolerances


class DimensionsInt:
    """Lightweight DimensionsInt value type."""

    __slots__ = ("height", "width")

    def __init__(self, *, width: int = 0, height: int = 0) -> None:
        self.width: int = int(width)
        self.height: int = int(height)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DimensionsFloat):
            return math.isclose(float(self.width), float(other.width), rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL) and math.isclose(
                float(self.height), float(other.height), rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL
            )
        if not isinstance(other, DimensionsInt):
            return NotImplemented
        return self.width == other.width and self.height == other.height

    def __hash__(self) -> int:
        return hash((self.width, self.height))

    def __iter__(self):
        return iter((self.width, self.height))

    def __repr__(self) -> str:
        return f"DimensionsInt(width={self.width!r}, height={self.height!r})"

    def is_zero(self) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_i64_t

        _c = fdl_dimensions_i64_t(width=self.width, height=self.height)
        return bool(get_lib().fdl_dimensions_i64_is_zero(_c))

    def normalize(self, squeeze: float) -> DimensionsFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_i64_t

        _c = fdl_dimensions_i64_t(width=self.width, height=self.height)
        _r = get_lib().fdl_dimensions_i64_normalize(_c, float(squeeze))
        return DimensionsFloat(width=_r.width, height=_r.height)

    def duplicate(self) -> DimensionsInt:
        """Create a duplicate of this value."""
        return DimensionsInt(width=self.width, height=self.height)

    def format(self) -> str:
        """Format as 'W x H', using ints when whole numbers, else 2 decimal places."""
        w, h = self.width, self.height
        if w == int(w) and h == int(h):
            return f"{int(w)} x {int(h)}"
        return f"{w:.2f} x {h:.2f}"

    def __gt__(self, other: DimensionsInt) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_i64_t

        _c = fdl_dimensions_i64_t(width=self.width, height=self.height)
        _c_other = fdl_dimensions_i64_t(width=other.width, height=other.height)
        _r = get_lib().fdl_dimensions_i64_gt(_c, _c_other)
        return bool(_r)

    def __lt__(self, other: DimensionsInt) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_i64_t

        _c = fdl_dimensions_i64_t(width=self.width, height=self.height)
        _c_other = fdl_dimensions_i64_t(width=other.width, height=other.height)
        _r = get_lib().fdl_dimensions_i64_lt(_c, _c_other)
        return bool(_r)

    def __bool__(self) -> bool:
        return not self.is_zero()


class DimensionsFloat:
    """Lightweight DimensionsFloat value type."""

    __slots__ = ("height", "width")

    def __init__(self, *, width: float = 0.0, height: float = 0.0) -> None:
        self.width: float = float(width)
        self.height: float = float(height)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DimensionsInt):
            return math.isclose(float(self.width), float(other.width), rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL) and math.isclose(
                float(self.height), float(other.height), rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL
            )
        if not isinstance(other, DimensionsFloat):
            return NotImplemented
        return math.isclose(self.width, other.width, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL) and math.isclose(
            self.height, other.height, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL
        )

    def __hash__(self) -> int:
        return hash((self.width, self.height))

    def __iter__(self):
        return iter((self.width, self.height))

    def __repr__(self) -> str:
        return f"DimensionsFloat(width={self.width!r}, height={self.height!r})"

    def is_zero(self) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        return bool(get_lib().fdl_dimensions_is_zero(_c))

    def normalize(self, squeeze: float) -> DimensionsFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        _r = get_lib().fdl_dimensions_normalize(_c, float(squeeze))
        return DimensionsFloat(width=_r.width, height=_r.height)

    def scale(self, scale_factor: float, target_squeeze: float) -> DimensionsFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        _r = get_lib().fdl_dimensions_scale(_c, float(scale_factor), float(target_squeeze))
        return DimensionsFloat(width=_r.width, height=_r.height)

    def normalize_and_scale(self, input_squeeze: float, scale_factor: float, target_squeeze: float) -> DimensionsFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        _r = get_lib().fdl_dimensions_normalize_and_scale(_c, float(input_squeeze), float(scale_factor), float(target_squeeze))
        return DimensionsFloat(width=_r.width, height=_r.height)

    def round(self, even: str, mode: str) -> DimensionsFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t

        from .enum_maps import ROUNDING_EVEN_TO_C, ROUNDING_MODE_TO_C

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        _r = get_lib().fdl_round_dimensions(_c, ROUNDING_EVEN_TO_C[even], ROUNDING_MODE_TO_C[mode])
        return DimensionsFloat(width=_r.width, height=_r.height)

    def clamp_to_dims(self, clamp_dims: DimensionsFloat) -> tuple[DimensionsFloat, PointFloat]:
        import ctypes

        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t, fdl_point_f64_t

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        _c_clamp_dims = fdl_dimensions_f64_t(width=clamp_dims.width, height=clamp_dims.height)
        _out_delta = fdl_point_f64_t()
        _r = get_lib().fdl_dimensions_clamp_to_dims(_c, _c_clamp_dims, ctypes.byref(_out_delta))
        return DimensionsFloat(width=_r.width, height=_r.height), PointFloat(x=_out_delta.x, y=_out_delta.y)

    def duplicate(self) -> DimensionsFloat:
        """Create a duplicate of this value."""
        return DimensionsFloat(width=self.width, height=self.height)

    def format(self) -> str:
        """Format as 'W x H', using ints when whole numbers, else 2 decimal places."""
        w, h = self.width, self.height
        if w == int(w) and h == int(h):
            return f"{int(w)} x {int(h)}"
        return f"{w:.2f} x {h:.2f}"

    def to_int(self) -> DimensionsInt:
        """Convert to integer dimensions by truncation."""
        return DimensionsInt(width=int(self.width), height=int(self.height))

    @classmethod
    def from_dimensions(cls, dims: DimensionsFloat) -> DimensionsFloat:
        """Create DimensionsFloat from any Dimensions instance."""
        return cls(width=float(dims.width), height=float(dims.height))

    def scale_by(self, factor: float) -> None:
        """Scale the dimensions by the provided factor (in-place)."""
        self.width = self.width * factor
        self.height = self.height * factor

    def __sub__(self, other: DimensionsFloat) -> DimensionsFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        _c_other = fdl_dimensions_f64_t(width=other.width, height=other.height)
        _r = get_lib().fdl_dimensions_sub(_c, _c_other)
        return DimensionsFloat(width=_r.width, height=_r.height)

    def __lt__(self, other: DimensionsFloat) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        _c_other = fdl_dimensions_f64_t(width=other.width, height=other.height)
        _r = get_lib().fdl_dimensions_f64_lt(_c, _c_other)
        return bool(_r)

    def __gt__(self, other: DimensionsFloat) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_dimensions_f64_t

        _c = fdl_dimensions_f64_t(width=self.width, height=self.height)
        _c_other = fdl_dimensions_f64_t(width=other.width, height=other.height)
        _r = get_lib().fdl_dimensions_f64_gt(_c, _c_other)
        return bool(_r)

    def __bool__(self) -> bool:
        return not self.is_zero()


class PointFloat:
    """Lightweight PointFloat value type."""

    __slots__ = ("x", "y")

    def __init__(self, *, x: float = 0.0, y: float = 0.0) -> None:
        self.x: float = float(x)
        self.y: float = float(y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PointFloat):
            return NotImplemented
        return math.isclose(self.x, other.x, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL) and math.isclose(
            self.y, other.y, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL
        )

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __iter__(self):
        return iter((self.x, self.y))

    def __repr__(self) -> str:
        return f"PointFloat(x={self.x!r}, y={self.y!r})"

    def is_zero(self) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        return bool(get_lib().fdl_point_is_zero(_c))

    def normalize(self, squeeze: float) -> PointFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _r = get_lib().fdl_point_normalize(_c, float(squeeze))
        return PointFloat(x=_r.x, y=_r.y)

    def scale(self, scale_factor: float, target_squeeze: float) -> PointFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _r = get_lib().fdl_point_scale(_c, float(scale_factor), float(target_squeeze))
        return PointFloat(x=_r.x, y=_r.y)

    def normalize_and_scale(self, input_squeeze: float, scale_factor: float, target_squeeze: float) -> PointFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _r = get_lib().fdl_point_normalize_and_scale(_c, float(input_squeeze), float(scale_factor), float(target_squeeze))
        return PointFloat(x=_r.x, y=_r.y)

    def clamp(self, min_val: float | None = None, max_val: float | None = None) -> PointFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _min_val_val = float(min_val) if min_val is not None else 0.0
        _min_val_has = 1 if min_val is not None else 0
        _max_val_val = float(max_val) if max_val is not None else 0.0
        _max_val_has = 1 if max_val is not None else 0
        _r = get_lib().fdl_point_clamp(_c, _min_val_val, _min_val_has, _max_val_val, _max_val_has)
        return PointFloat(x=_r.x, y=_r.y)

    def round(self, even: str, mode: str) -> PointFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        from .enum_maps import ROUNDING_EVEN_TO_C, ROUNDING_MODE_TO_C

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _r = get_lib().fdl_round_point(_c, ROUNDING_EVEN_TO_C[even], ROUNDING_MODE_TO_C[mode])
        return PointFloat(x=_r.x, y=_r.y)

    def format(self) -> str:
        """Format as '(X, Y)', using ints when whole numbers, else 2 decimal places."""
        if self.x == int(self.x) and self.y == int(self.y):
            return f"({int(self.x)}, {int(self.y)})"
        return f"({self.x:.2f}, {self.y:.2f})"

    def __add__(self, other: PointFloat) -> PointFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _c_other = fdl_point_f64_t(x=other.x, y=other.y)
        _r = get_lib().fdl_point_add(_c, _c_other)
        return PointFloat(x=_r.x, y=_r.y)

    def __iadd__(self, other: PointFloat) -> PointFloat:
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: PointFloat) -> PointFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _c_other = fdl_point_f64_t(x=other.x, y=other.y)
        _r = get_lib().fdl_point_sub(_c, _c_other)
        return PointFloat(x=_r.x, y=_r.y)

    def __mul__(self, other: PointFloat | float) -> PointFloat:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        if isinstance(other, int | float):
            _r = get_lib().fdl_point_mul_scalar(_c, float(other))
        elif isinstance(other, PointFloat):
            return PointFloat(x=float(self.x) * float(other.x), y=float(self.y) * float(other.y))
        else:
            raise TypeError(f"Cannot multiply PointFloat with {type(other)}")
        return PointFloat(x=_r.x, y=_r.y)

    def __lt__(self, other: PointFloat) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _c_other = fdl_point_f64_t(x=other.x, y=other.y)
        _r = get_lib().fdl_point_f64_lt(_c, _c_other)
        return bool(_r)

    def __gt__(self, other: PointFloat) -> bool:
        from fdl_ffi import get_lib
        from fdl_ffi._structs import fdl_point_f64_t

        _c = fdl_point_f64_t(x=self.x, y=self.y)
        _c_other = fdl_point_f64_t(x=other.x, y=other.y)
        _r = get_lib().fdl_point_f64_gt(_c, _c_other)
        return bool(_r)


class Rect:
    """Lightweight Rect value type."""

    __slots__ = ("height", "width", "x", "y")

    def __init__(self, *, x: float = 0.0, y: float = 0.0, width: float = 0.0, height: float = 0.0) -> None:
        self.x: float = float(x)
        self.y: float = float(y)
        self.width: float = float(width)
        self.height: float = float(height)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rect):
            return NotImplemented
        return (
            math.isclose(self.x, other.x, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL)
            and math.isclose(self.y, other.y, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL)
            and math.isclose(self.width, other.width, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL)
            and math.isclose(self.height, other.height, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL)
        )

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.width, self.height))

    def __iter__(self):
        return iter((self.x, self.y, self.width, self.height))

    def __repr__(self) -> str:
        return f"Rect(x={self.x!r}, y={self.y!r}, width={self.width!r}, height={self.height!r})"
