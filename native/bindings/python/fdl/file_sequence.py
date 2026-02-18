# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""FDL Core FileSequence facade."""

from __future__ import annotations


from .fdl_types import DimensionsFloat, DimensionsInt, PointFloat

from .base import (
    HandleWrapper,
    _decode_str,
)
from ._custom_attrs import (
    _all as _ca_all,
    _count as _ca_count,
    _get as _ca_get,
    _has as _ca_has,
    _remove as _ca_remove,
    _set as _ca_set,
)


class FileSequence(HandleWrapper):
    """FileSequence facade wrapping a C fdl_file_sequence_t handle."""

    @property
    def value(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_file_sequence_get_value(self._handle)
        return _decode_str(raw)

    @property
    def idx(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_file_sequence_get_idx(self._handle)
        return _decode_str(raw)

    @property
    def min(self) -> int:
        self._check_handle()
        raw = self._lib.fdl_file_sequence_get_min(self._handle)
        return int(raw)

    @property
    def max(self) -> int:
        self._check_handle()
        raw = self._lib.fdl_file_sequence_get_max(self._handle)
        return int(raw)

    def as_dict(self) -> dict:
        d: dict = {}
        v = self.value
        d["value"] = v
        v = self.idx
        d["idx"] = v
        v = self.min
        d["min"] = v
        v = self.max
        d["max"] = v
        return d

    _CA_PREFIX = "fdl_file_sequence_"

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
