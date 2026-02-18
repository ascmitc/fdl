# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""FDL Core ClipID facade."""

from __future__ import annotations

import ctypes
import json

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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .file_sequence import FileSequence


class ClipID(HandleWrapper):
    """ClipID facade wrapping a C fdl_clip_id_t handle."""

    @property
    def clip_name(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_clip_id_get_clip_name(self._handle)
        return _decode_str(raw)

    @property
    def file(self) -> str | None:
        self._check_handle()
        if not self._lib.fdl_clip_id_has_file(self._handle):
            return None
        raw = self._lib.fdl_clip_id_get_file(self._handle)
        return _decode_str(raw)

    @property
    def sequence(self) -> FileSequence | None:
        self._check_handle()
        if not self._lib.fdl_clip_id_has_sequence(self._handle):
            return None
        from .file_sequence import FileSequence

        handle = self._lib.fdl_clip_id_sequence(self._handle)
        if not handle:
            return None
        return FileSequence._from_handle(handle, self._lib, self._doc_ref)

    def as_dict(self) -> dict:
        self._check_handle()
        json_ptr = self._lib.fdl_clip_id_to_json(self._handle, 0)
        if not json_ptr:
            raise RuntimeError("fdl_clip_id_to_json returned NULL")
        result = json.loads(ctypes.string_at(json_ptr))
        self._lib.fdl_free(json_ptr)
        return result

    def validate(self) -> None:
        """Validate this clip_id for mutual exclusion rules."""
        self._check_handle()
        json_ptr = self._lib.fdl_clip_id_to_json(self._handle, 0)
        if not json_ptr:
            raise RuntimeError("fdl_clip_id_to_json returned NULL")
        _json_bytes = ctypes.string_at(json_ptr)
        self._lib.fdl_free(json_ptr)
        _err = self._lib.fdl_clip_id_validate_json(_json_bytes, len(_json_bytes))
        if _err:
            _msg = ctypes.string_at(_err).decode("utf-8")
            self._lib.fdl_free(_err)
            from .errors import FDLValidationError

            raise FDLValidationError(_msg)

    _CA_PREFIX = "fdl_clip_id_"

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
