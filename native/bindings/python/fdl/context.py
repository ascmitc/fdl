# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""FDL Core Context facade."""

from __future__ import annotations

from fdl_ffi import ffi
import json

from .fdl_types import DimensionsFloat, DimensionsInt, PointFloat

from .base import (
    CollectionWrapper,
    HandleWrapper,
    _decode_str,
)
from .converters import (
    _to_c_dims_f64,
)
from ._custom_attrs import (
    _all as _ca_all,
    _count as _ca_count,
    _get as _ca_get,
    _has as _ca_has,
    _remove as _ca_remove,
    _set as _ca_set,
)
from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .canvas import Canvas
    from .clip_id import ClipID
    from .framing_decision import FramingDecision
    from .models import ContextModel


@dataclass
class ResolveCanvasResult:
    """Result of resolving canvas for given input dimensions."""

    canvas: Canvas
    framing_decision: FramingDecision
    was_resolved: bool


class Context(HandleWrapper):
    """Context facade wrapping a C fdl_context_t handle."""

    def __init__(
        self,
        *,
        label: str,
        context_creator: str | None = None,
        canvases: object = None,
    ) -> None:
        from fdl_ffi import get_lib

        lib = get_lib()
        from .fdl import FDL

        _doc_h = lib.fdl_doc_create_with_header(
            b"00000000-0000-0000-0000-000000000000",
            2,
            0,
            b"_",
            ffi.NULL,
        )
        _backing = FDL._from_handle(_doc_h, lib)
        handle = lib.fdl_doc_add_context(
            _doc_h,
            label.encode("utf-8"),
            context_creator.encode("utf-8") if context_creator else ffi.NULL,
        )
        if not handle:
            raise RuntimeError("fdl_doc_add_context returned NULL")
        HandleWrapper.__init__(self, handle, lib, _backing)

    @property
    def label(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_context_get_label(self._handle)
        return _decode_str(raw)

    @property
    def context_creator(self) -> str | None:
        self._check_handle()
        raw = self._lib.fdl_context_get_context_creator(self._handle)
        return _decode_str(raw)

    @property
    def clip_id(self) -> ClipID | None:
        self._check_handle()
        if not self._lib.fdl_context_has_clip_id(self._handle):
            return None
        from .clip_id import ClipID

        handle = self._lib.fdl_context_clip_id(self._handle)
        if not handle:
            return None
        return ClipID._from_handle(handle, self._lib, self._doc_ref)

    @clip_id.setter
    def clip_id(self, value: ClipID | dict | None) -> None:
        self._check_handle()
        if value is None:
            self._lib.fdl_context_remove_clip_id(self._handle)
            return
        if isinstance(value, dict):
            _json = json.dumps(value).encode("utf-8")
        else:
            _json = json.dumps(value.as_dict()).encode("utf-8")
        _err = self._lib.fdl_context_set_clip_id_json(self._handle, _json, len(_json))
        if _err:
            _msg = ffi.string(_err).decode("utf-8")
            self._lib.fdl_free(_err)
            raise ValueError(_msg)

    @property
    def canvases(self) -> CollectionWrapper[Canvas]:
        self._check_handle()
        from .canvas import Canvas

        return CollectionWrapper(
            lib=self._lib,
            parent_handle=self._handle,
            item_cls=Canvas,
            count_fn=self._lib.fdl_context_canvases_count,
            at_fn=self._lib.fdl_context_canvas_at,
            find_by_id_fn=self._lib.fdl_context_find_canvas_by_id,
            find_by_label_fn=None,
            doc_ref=self._doc_ref,
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Context):
            return self.label == other.label
        if isinstance(other, str):
            return self.label == other
        return NotImplemented

    def __hash__(self):
        return hash((self.label,))

    def as_dict(self) -> dict:
        self._check_handle()
        json_ptr = self._lib.fdl_context_to_json(self._handle, 0)
        if not json_ptr:
            raise RuntimeError("fdl_context_to_json returned NULL")
        result = json.loads(ffi.string(json_ptr))
        self._lib.fdl_free(json_ptr)
        return result

    def to_model(self) -> ContextModel:
        """Convert to a Pydantic ``ContextModel`` instance.

        Returns a pure-data Pydantic model suitable for serialization,
        API responses, and interoperability with web frameworks.
        """
        from .models import ContextModel

        return ContextModel.model_validate(self.as_dict())

    @classmethod
    def from_model(cls, model: ContextModel) -> Context:
        """Create a standalone ``Context`` facade from a Pydantic model.

        Note: Creates a temporary backing document. The returned object
        is self-contained but not attached to any parent FDL document.
        """
        d = model.model_dump(exclude_none=True)
        return cls(**d)

    def add_canvas(
        self,
        id: str,
        label: str,
        source_canvas_id: str,
        dimensions: DimensionsInt,
        anamorphic_squeeze: float,
    ) -> Canvas:
        """Add a canvas to this context."""
        self._check_handle()
        from .canvas import Canvas

        handle = self._lib.fdl_context_add_canvas(
            self._handle,
            id.encode("utf-8"),
            label.encode("utf-8"),
            source_canvas_id.encode("utf-8"),
            int(dimensions.width),
            int(dimensions.height),
            float(anamorphic_squeeze),
        )
        if not handle:
            raise RuntimeError("fdl_context_add_canvas returned NULL")
        return Canvas._from_handle(handle, self._lib, self._doc_ref)

    def resolve_canvas_for_dimensions(
        self,
        input_dims: DimensionsFloat,
        canvas: Canvas,
        framing: FramingDecision,
    ) -> ResolveCanvasResult:
        """Find matching canvas when input dimensions differ from selected canvas."""
        self._check_handle()
        from .canvas import Canvas
        from .framing_decision import FramingDecision

        result = self._lib.fdl_context_resolve_canvas_for_dimensions(
            self._handle,
            _to_c_dims_f64(input_dims),
            canvas._handle,
            framing._handle,
        )
        if result.error:
            msg = ffi.string(result.error).decode("utf-8")
            self._lib.fdl_free(result.error)
            raise ValueError(msg)
        _canvas = Canvas._from_handle(result.canvas, self._lib, self._doc_ref)
        _framing_decision = FramingDecision._from_handle(result.framing_decision, self._lib, self._doc_ref)
        _was_resolved = bool(result.was_resolved)
        return ResolveCanvasResult(
            canvas=_canvas,
            framing_decision=_framing_decision,
            was_resolved=_was_resolved,
        )

    _CA_PREFIX = "fdl_context_"

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
