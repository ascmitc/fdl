# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""FDL Core Canvas facade."""

from __future__ import annotations

from fdl_ffi import ffi
import json

from .fdl_types import DimensionsFloat, DimensionsInt, PointFloat, Rect

from .base import (
    CollectionWrapper,
    HandleWrapper,
    _decode_str,
)
from .converters import (
    _dims_f64,
    _dims_i64,
    _point_f64,
    _rect,
    _to_c_dims_f64,
    _to_c_dims_i64,
    _to_c_point_f64,
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
    from .framing_decision import FramingDecision
    from .models import CanvasModel


class Canvas(HandleWrapper):
    """Canvas facade wrapping a C fdl_canvas_t handle."""

    def __init__(
        self,
        *,
        id: str,
        label: str = "",
        source_canvas_id: str,
        dimensions: DimensionsInt,
        anamorphic_squeeze: float = 1.0,
        effective_dimensions: DimensionsInt | None = None,
        effective_anchor_point: PointFloat | None = None,
        photosite_dimensions: DimensionsInt | None = None,
        physical_dimensions: DimensionsFloat | None = None,
        framing_decisions: object = None,
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
        _ctx_h = lib.fdl_doc_add_context(_doc_h, b"_", ffi.NULL)
        handle = lib.fdl_context_add_canvas(
            _ctx_h,
            id.encode("utf-8"),
            label.encode("utf-8"),
            source_canvas_id.encode("utf-8"),
            int(dimensions.width),
            int(dimensions.height),
            float(anamorphic_squeeze),
        )
        if not handle:
            raise RuntimeError("fdl_context_add_canvas returned NULL")
        HandleWrapper.__init__(self, handle, lib, _backing)
        if effective_dimensions is not None:
            self.set_effective(
                dims=effective_dimensions or DimensionsInt(width=0, height=0),
                anchor=effective_anchor_point or PointFloat(x=0.0, y=0.0),
            )
        if photosite_dimensions is not None:
            self.photosite_dimensions = photosite_dimensions
        if physical_dimensions is not None:
            self.physical_dimensions = physical_dimensions

    @property
    def id(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_canvas_get_id(self._handle)
        return _decode_str(raw)

    @property
    def label(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_canvas_get_label(self._handle)
        return _decode_str(raw)

    @property
    def source_canvas_id(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_canvas_get_source_canvas_id(self._handle)
        return _decode_str(raw)

    @property
    def dimensions(self) -> DimensionsInt:
        self._check_handle()
        raw = self._lib.fdl_canvas_get_dimensions(self._handle)
        return _dims_i64(raw)

    @dimensions.setter
    def dimensions(self, value: DimensionsInt) -> None:
        self._check_handle()
        self._lib.fdl_canvas_set_dimensions(self._handle, _to_c_dims_i64(value))

    @property
    def anamorphic_squeeze(self) -> float:
        self._check_handle()
        raw = self._lib.fdl_canvas_get_anamorphic_squeeze(self._handle)
        return float(raw)

    @anamorphic_squeeze.setter
    def anamorphic_squeeze(self, value: float) -> None:
        self._check_handle()
        self._lib.fdl_canvas_set_anamorphic_squeeze(self._handle, float(value))

    @property
    def effective_dimensions(self) -> DimensionsInt | None:
        self._check_handle()
        if not self._lib.fdl_canvas_has_effective_dimensions(self._handle):
            return None
        raw = self._lib.fdl_canvas_get_effective_dimensions(self._handle)
        return _dims_i64(raw)

    @effective_dimensions.setter
    def effective_dimensions(self, value: DimensionsInt | None) -> None:
        self._check_handle()
        if value is None:
            self._lib.fdl_canvas_remove_effective(self._handle)
            return
        self._lib.fdl_canvas_set_effective_dims_only(self._handle, _to_c_dims_i64(value))

    @property
    def effective_anchor_point(self) -> PointFloat | None:
        self._check_handle()
        if not self._lib.fdl_canvas_has_effective_dimensions(self._handle):
            return None
        raw = self._lib.fdl_canvas_get_effective_anchor_point(self._handle)
        return _point_f64(raw)

    @property
    def photosite_dimensions(self) -> DimensionsInt | None:
        self._check_handle()
        if not self._lib.fdl_canvas_has_photosite_dimensions(self._handle):
            return None
        raw = self._lib.fdl_canvas_get_photosite_dimensions(self._handle)
        return _dims_i64(raw)

    @photosite_dimensions.setter
    def photosite_dimensions(self, value: DimensionsInt) -> None:
        self._check_handle()
        self._lib.fdl_canvas_set_photosite_dimensions(self._handle, _to_c_dims_i64(value))

    @property
    def physical_dimensions(self) -> DimensionsFloat | None:
        self._check_handle()
        if not self._lib.fdl_canvas_has_physical_dimensions(self._handle):
            return None
        raw = self._lib.fdl_canvas_get_physical_dimensions(self._handle)
        return _dims_f64(raw)

    @physical_dimensions.setter
    def physical_dimensions(self, value: DimensionsFloat) -> None:
        self._check_handle()
        self._lib.fdl_canvas_set_physical_dimensions(self._handle, _to_c_dims_f64(value))

    @property
    def framing_decisions(self) -> CollectionWrapper[FramingDecision]:
        self._check_handle()
        from .framing_decision import FramingDecision

        return CollectionWrapper(
            lib=self._lib,
            parent_handle=self._handle,
            item_cls=FramingDecision,
            count_fn=self._lib.fdl_canvas_framing_decisions_count,
            at_fn=self._lib.fdl_canvas_framing_decision_at,
            find_by_id_fn=self._lib.fdl_canvas_find_framing_decision_by_id,
            find_by_label_fn=None,
            doc_ref=self._doc_ref,
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Canvas):
            return self.id == other.id
        if isinstance(other, str):
            return self.id == other
        return NotImplemented

    def __hash__(self):
        return hash((self.id,))

    def as_dict(self) -> dict:
        self._check_handle()
        json_ptr = self._lib.fdl_canvas_to_json(self._handle, 0)
        if not json_ptr:
            raise RuntimeError("fdl_canvas_to_json returned NULL")
        result = json.loads(ffi.string(json_ptr))
        self._lib.fdl_free(json_ptr)
        return result

    def to_model(self) -> CanvasModel:
        """Convert to a Pydantic ``CanvasModel`` instance.

        Returns a pure-data Pydantic model suitable for serialization,
        API responses, and interoperability with web frameworks.
        """
        from .models import CanvasModel

        return CanvasModel.model_validate(self.as_dict())

    @classmethod
    def from_model(cls, model: CanvasModel) -> Canvas:
        """Create a standalone ``Canvas`` facade from a Pydantic model.

        Note: Creates a temporary backing document. The returned object
        is self-contained but not attached to any parent FDL document.
        """
        d = model.model_dump(exclude_none=True)
        if "dimensions" in d:
            d["dimensions"] = DimensionsInt(**d["dimensions"])
        if "effective_dimensions" in d:
            d["effective_dimensions"] = DimensionsInt(**d["effective_dimensions"])
        if "effective_anchor_point" in d:
            d["effective_anchor_point"] = PointFloat(**d["effective_anchor_point"])
        if "photosite_dimensions" in d:
            d["photosite_dimensions"] = DimensionsInt(**d["photosite_dimensions"])
        if "physical_dimensions" in d:
            d["physical_dimensions"] = DimensionsFloat(**d["physical_dimensions"])
        return cls(**d)

    def add_framing_decision(
        self,
        id: str,
        label: str,
        framing_intent_id: str,
        dimensions: DimensionsFloat,
        anchor_point: PointFloat,
    ) -> FramingDecision:
        """Add a framing decision to this canvas."""
        self._check_handle()
        from .framing_decision import FramingDecision

        handle = self._lib.fdl_canvas_add_framing_decision(
            self._handle,
            id.encode("utf-8"),
            label.encode("utf-8"),
            framing_intent_id.encode("utf-8"),
            float(dimensions.width),
            float(dimensions.height),
            float(anchor_point.x),
            float(anchor_point.y),
        )
        if not handle:
            raise RuntimeError("fdl_canvas_add_framing_decision returned NULL")
        return FramingDecision._from_handle(handle, self._lib, self._doc_ref)

    def set_effective(
        self,
        dims: DimensionsInt,
        anchor: PointFloat,
    ) -> None:
        """Set effective dimensions and anchor point on this canvas."""
        self._check_handle()
        self._lib.fdl_canvas_set_effective_dimensions(
            self._handle,
            _to_c_dims_i64(dims),
            _to_c_point_f64(anchor),
        )

    def get_rect(self) -> Rect:
        """Get canvas rect as (0, 0, width, height)."""
        self._check_handle()
        raw = self._lib.fdl_canvas_get_rect(self._handle)
        return _rect(raw)

    def get_effective_rect(self) -> Rect | None:
        """Get effective rect or None if not defined."""
        self._check_handle()
        out = ffi.new("fdl_rect_t*")
        if not self._lib.fdl_canvas_get_effective_rect(self._handle, out):
            return None
        return _rect(out)

    _CA_PREFIX = "fdl_canvas_"

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
