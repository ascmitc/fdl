# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
"""Shared helpers for custom attribute access on all handle types."""

from __future__ import annotations

from fdl_ffi import ffi

from .base import _decode_str
from .fdl_types import DimensionsFloat, DimensionsInt, PointFloat


def _set(lib, handle, prefix: str, name: str, value: str | int | float | bool | PointFloat | DimensionsFloat | DimensionsInt) -> None:
    """Set a custom attribute, dispatching to the typed C setter.

    Args:
        lib: The loaded FFI library.
        handle: The opaque C handle.
        prefix: C function name prefix (e.g. ``"fdl_canvas_"``).
        name: Attribute name (without ``_`` prefix).
        value: Attribute value (str, int, float, bool, PointFloat, DimensionsFloat, or DimensionsInt).

    Raises:
        TypeError: If value is not str, int, float, bool, PointFloat, DimensionsFloat, or DimensionsInt.
        ValueError: If an attribute with the same name exists with a different type.
    """
    _name = name.encode("utf-8")
    if isinstance(value, PointFloat):
        c = ffi.new("fdl_point_f64_t*", {"x": float(value.x), "y": float(value.y)})[0]
        rc = getattr(lib, f"{prefix}set_custom_attr_point_f64")(handle, _name, c)
    elif isinstance(value, DimensionsFloat):
        c = ffi.new("fdl_dimensions_f64_t*", {"width": float(value.width), "height": float(value.height)})[0]
        rc = getattr(lib, f"{prefix}set_custom_attr_dims_f64")(handle, _name, c)
    elif isinstance(value, DimensionsInt):
        c = ffi.new("fdl_dimensions_i64_t*", {"width": int(value.width), "height": int(value.height)})[0]
        rc = getattr(lib, f"{prefix}set_custom_attr_dims_i64")(handle, _name, c)
    elif isinstance(value, bool):
        rc = getattr(lib, f"{prefix}set_custom_attr_bool")(handle, _name, 1 if value else 0)
    elif isinstance(value, str):
        rc = getattr(lib, f"{prefix}set_custom_attr_string")(handle, _name, value.encode("utf-8"))
    elif isinstance(value, int):
        rc = getattr(lib, f"{prefix}set_custom_attr_int")(handle, _name, value)
    elif isinstance(value, float):
        rc = getattr(lib, f"{prefix}set_custom_attr_float")(handle, _name, value)
    else:
        raise TypeError(
            f"Custom attribute value must be str, int, float, bool, "
            f"PointFloat, DimensionsFloat, or DimensionsInt, got {type(value).__name__}"
        )
    if rc != 0:
        raise ValueError(f"Failed to set custom attribute '{name}' — type mismatch with existing value")


def _get(lib, handle, prefix: str, name: str) -> str | int | float | bool | PointFloat | DimensionsFloat | DimensionsInt | None:
    """Get a custom attribute value by name.

    Args:
        lib: The loaded FFI library.
        handle: The opaque C handle.
        prefix: C function name prefix.
        name: Attribute name (without ``_`` prefix).

    Returns:
        The attribute value, or None if not found.
    """
    _name = name.encode("utf-8")
    attr_type = getattr(lib, f"{prefix}get_custom_attr_type")(handle, _name)
    if attr_type == 0:
        return None
    if attr_type == 1:
        raw = getattr(lib, f"{prefix}get_custom_attr_string")(handle, _name)
        return _decode_str(raw)
    if attr_type == 2:
        out = ffi.new("int64_t*")
        getattr(lib, f"{prefix}get_custom_attr_int")(handle, _name, out)
        return out[0]
    if attr_type == 3:
        out = ffi.new("double*")
        getattr(lib, f"{prefix}get_custom_attr_float")(handle, _name, out)
        return out[0]
    if attr_type == 4:
        out = ffi.new("int*")
        getattr(lib, f"{prefix}get_custom_attr_bool")(handle, _name, out)
        return bool(out[0])
    if attr_type == 5:  # POINT_F64
        out = ffi.new("fdl_point_f64_t*")
        getattr(lib, f"{prefix}get_custom_attr_point_f64")(handle, _name, out)
        return PointFloat(x=out.x, y=out.y)
    if attr_type == 6:  # DIMS_F64
        out = ffi.new("fdl_dimensions_f64_t*")
        getattr(lib, f"{prefix}get_custom_attr_dims_f64")(handle, _name, out)
        return DimensionsFloat(width=out.width, height=out.height)
    if attr_type == 7:  # DIMS_I64
        out = ffi.new("fdl_dimensions_i64_t*")
        getattr(lib, f"{prefix}get_custom_attr_dims_i64")(handle, _name, out)
        return DimensionsInt(width=out.width, height=out.height)
    return None


def _has(lib, handle, prefix: str, name: str) -> bool:
    """Check if a custom attribute exists."""
    return bool(getattr(lib, f"{prefix}has_custom_attr")(handle, name.encode("utf-8")))


def _remove(lib, handle, prefix: str, name: str) -> bool:
    """Remove a custom attribute. Returns True if removed, False if not found."""
    return getattr(lib, f"{prefix}remove_custom_attr")(handle, name.encode("utf-8")) == 0


def _count(lib, handle, prefix: str) -> int:
    """Return the number of custom attributes."""
    return int(getattr(lib, f"{prefix}custom_attrs_count")(handle))


def _all(lib, handle, prefix: str) -> dict[str, str | int | float | bool | PointFloat | DimensionsFloat | DimensionsInt]:
    """Return all custom attributes as a dictionary."""
    result: dict = {}
    count = getattr(lib, f"{prefix}custom_attrs_count")(handle)
    for i in range(count):
        name_ptr = getattr(lib, f"{prefix}custom_attr_name_at")(handle, i)
        if name_ptr == ffi.NULL:
            continue
        name = _decode_str(name_ptr)
        value = _get(lib, handle, prefix, name)
        if value is not None:
            result[name] = value
    return result
