# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""FDL Core FramingIntent facade."""

from __future__ import annotations

import ctypes
import json

from .fdl_types import DimensionsFloat, DimensionsInt, PointFloat

from .base import (
    HandleWrapper,
    _decode_str,
)
from .converters import (
    _dims_i64,
    _to_c_dims_i64,
)
from ._custom_attrs import (
    _all as _ca_all,
    _count as _ca_count,
    _get as _ca_get,
    _has as _ca_has,
    _remove as _ca_remove,
    _set as _ca_set,
)


class FramingIntent(HandleWrapper):
    """FramingIntent facade wrapping a C fdl_framing_intent_t handle."""

    def __init__(
        self,
        *,
        id: str,
        label: str = "",
        aspect_ratio: DimensionsInt,
        protection: float = 0.0,
    ) -> None:
        from fdl_ffi import get_lib

        lib = get_lib()
        from .fdl import FDL

        _doc_h = lib.fdl_doc_create_with_header(
            b"00000000-0000-0000-0000-000000000000",
            2,
            0,
            b"_",
            None,
        )
        _backing = FDL._from_handle(_doc_h, lib)
        handle = lib.fdl_doc_add_framing_intent(
            _doc_h,
            id.encode("utf-8"),
            label.encode("utf-8"),
            int(aspect_ratio.width),
            int(aspect_ratio.height),
            float(protection),
        )
        if not handle:
            raise RuntimeError("fdl_doc_add_framing_intent returned NULL")
        HandleWrapper.__init__(self, handle, lib, _backing)

    @property
    def id(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_framing_intent_get_id(self._handle)
        return _decode_str(raw)

    @property
    def label(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_framing_intent_get_label(self._handle)
        return _decode_str(raw)

    @property
    def aspect_ratio(self) -> DimensionsInt:
        self._check_handle()
        raw = self._lib.fdl_framing_intent_get_aspect_ratio(self._handle)
        return _dims_i64(raw)

    @aspect_ratio.setter
    def aspect_ratio(self, value: DimensionsInt) -> None:
        self._check_handle()
        self._lib.fdl_framing_intent_set_aspect_ratio(self._handle, _to_c_dims_i64(value))

    @property
    def protection(self) -> float:
        self._check_handle()
        raw = self._lib.fdl_framing_intent_get_protection(self._handle)
        return float(raw)

    @protection.setter
    def protection(self, value: float) -> None:
        self._check_handle()
        self._lib.fdl_framing_intent_set_protection(self._handle, ctypes.c_double(value))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FramingIntent):
            return self.id == other.id
        if isinstance(other, str):
            return self.id == other
        return NotImplemented

    def __hash__(self):
        return hash((self.id,))

    def as_dict(self) -> dict:
        self._check_handle()
        json_ptr = self._lib.fdl_framing_intent_to_json(self._handle, 0)
        if not json_ptr:
            raise RuntimeError("fdl_framing_intent_to_json returned NULL")
        result = json.loads(ctypes.string_at(json_ptr))
        self._lib.fdl_free(json_ptr)
        return result

    _CA_PREFIX = "fdl_framing_intent_"

    def set_custom_attr(self, name: str, value: str | int | float | bool | PointFloat | DimensionsFloat | DimensionsInt) -> None:
        """Set a custom attribute. Type is inferred from value.

        Args:
            name: Attribute name (without ``_`` prefix).
            value: Attribute value (str, int, float, bool, PointFloat, DimensionsFloat, or DimensionsInt).

        Raises:
            TypeError: If value is not str, int, float, bool, PointFloat, DimensionsFloat, or DimensionsInt.
            ValueError: If an attribute with the same name exists with a different type.
        """
        self._check_handle()
        _ca_set(self._lib, self._handle, self._CA_PREFIX, name, value)

    def get_custom_attr(self, name: str) -> str | int | float | bool | PointFloat | DimensionsFloat | DimensionsInt | None:
        """Get a custom attribute value by name.

        Args:
            name: Attribute name (without ``_`` prefix).

        Returns:
            The attribute value, or None if not found.
        """
        self._check_handle()
        return _ca_get(self._lib, self._handle, self._CA_PREFIX, name)

    def has_custom_attr(self, name: str) -> bool:
        """Check if a custom attribute exists.

        Args:
            name: Attribute name (without ``_`` prefix).
        """
        self._check_handle()
        return _ca_has(self._lib, self._handle, self._CA_PREFIX, name)

    def remove_custom_attr(self, name: str) -> bool:
        """Remove a custom attribute.

        Args:
            name: Attribute name (without ``_`` prefix).

        Returns:
            True if the attribute was removed, False if it was not found.
        """
        self._check_handle()
        return _ca_remove(self._lib, self._handle, self._CA_PREFIX, name)

    def custom_attrs_count(self) -> int:
        """Return the number of custom attributes on this object."""
        self._check_handle()
        return _ca_count(self._lib, self._handle, self._CA_PREFIX)

    @property
    def custom_attrs(self) -> dict[str, str | int | float | bool | PointFloat | DimensionsFloat | DimensionsInt]:
        """Return all custom attributes as a dictionary."""
        self._check_handle()
        return _ca_all(self._lib, self._handle, self._CA_PREFIX)
