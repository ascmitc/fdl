# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""FDL Core FramingDecision facade."""

from __future__ import annotations

from fdl_ffi import ffi
import json

from .fdl_types import DimensionsFloat, DimensionsInt, PointFloat, Rect
from .rounding import RoundStrategy

from .base import (
    HandleWrapper,
    _decode_str,
)
from .converters import (
    _dims_f64,
    _point_f64,
    _rect,
    _to_c_dims_f64,
    _to_c_point_f64,
    _to_c_round_strategy,
)
from .enum_maps import (
    H_ALIGN_TO_C,
    V_ALIGN_TO_C,
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
    from .canvas import Canvas
    from .framing_intent import FramingIntent
    from .models import FramingDecisionModel


class FramingDecision(HandleWrapper):
    """FramingDecision facade wrapping a C fdl_framing_decision_t handle."""

    def __init__(
        self,
        *,
        id: str,
        label: str = "",
        framing_intent_id: str,
        dimensions: DimensionsFloat = DimensionsFloat(width=0.0, height=0.0),
        anchor_point: PointFloat = PointFloat(x=0.0, y=0.0),
        protection_dimensions: DimensionsFloat | None = None,
        protection_anchor_point: PointFloat | None = None,
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
        _canvas_h = lib.fdl_context_add_canvas(_ctx_h, b"_", b"_", b"_", 1, 1, 1.0)
        handle = lib.fdl_canvas_add_framing_decision(
            _canvas_h,
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
        HandleWrapper.__init__(self, handle, lib, _backing)
        if protection_dimensions is not None:
            self.set_protection(
                dims=protection_dimensions or DimensionsFloat(width=0.0, height=0.0),
                anchor=protection_anchor_point or PointFloat(x=0.0, y=0.0),
            )

    @property
    def id(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_framing_decision_get_id(self._handle)
        return _decode_str(raw)

    @property
    def label(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_framing_decision_get_label(self._handle)
        return _decode_str(raw)

    @property
    def framing_intent_id(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_framing_decision_get_framing_intent_id(self._handle)
        return _decode_str(raw)

    @property
    def dimensions(self) -> DimensionsFloat:
        self._check_handle()
        raw = self._lib.fdl_framing_decision_get_dimensions(self._handle)
        return _dims_f64(raw)

    @dimensions.setter
    def dimensions(self, value: DimensionsFloat) -> None:
        self._check_handle()
        self._lib.fdl_framing_decision_set_dimensions(self._handle, _to_c_dims_f64(value))

    @property
    def anchor_point(self) -> PointFloat:
        self._check_handle()
        raw = self._lib.fdl_framing_decision_get_anchor_point(self._handle)
        return _point_f64(raw)

    @anchor_point.setter
    def anchor_point(self, value: PointFloat) -> None:
        self._check_handle()
        self._lib.fdl_framing_decision_set_anchor_point(self._handle, _to_c_point_f64(value))

    @property
    def protection_dimensions(self) -> DimensionsFloat | None:
        self._check_handle()
        if not self._lib.fdl_framing_decision_has_protection(self._handle):
            return None
        raw = self._lib.fdl_framing_decision_get_protection_dimensions(self._handle)
        return _dims_f64(raw)

    @protection_dimensions.setter
    def protection_dimensions(self, value: DimensionsFloat | None) -> None:
        self._check_handle()
        if value is None:
            self._lib.fdl_framing_decision_remove_protection(self._handle)
            return
        self._lib.fdl_framing_decision_set_protection_dimensions(self._handle, _to_c_dims_f64(value))

    @property
    def protection_anchor_point(self) -> PointFloat | None:
        self._check_handle()
        if not self._lib.fdl_framing_decision_has_protection(self._handle):
            return None
        raw = self._lib.fdl_framing_decision_get_protection_anchor_point(self._handle)
        return _point_f64(raw)

    @protection_anchor_point.setter
    def protection_anchor_point(self, value: PointFloat) -> None:
        self._check_handle()
        self._lib.fdl_framing_decision_set_protection_anchor_point(self._handle, _to_c_point_f64(value))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FramingDecision):
            return self.id == other.id
        if isinstance(other, str):
            return self.id == other
        return NotImplemented

    def __hash__(self):
        return hash((self.id,))

    def as_dict(self) -> dict:
        self._check_handle()
        json_ptr = self._lib.fdl_framing_decision_to_json(self._handle, 0)
        if not json_ptr:
            raise RuntimeError("fdl_framing_decision_to_json returned NULL")
        result = json.loads(ffi.string(json_ptr))
        self._lib.fdl_free(json_ptr)
        return result

    def to_model(self) -> FramingDecisionModel:
        """Convert to a Pydantic ``FramingDecisionModel`` instance.

        Returns a pure-data Pydantic model suitable for serialization,
        API responses, and interoperability with web frameworks.
        """
        from .models import FramingDecisionModel

        return FramingDecisionModel.model_validate(self.as_dict())

    @classmethod
    def from_model(cls, model: FramingDecisionModel) -> FramingDecision:
        """Create a standalone ``FramingDecision`` facade from a Pydantic model.

        Note: Creates a temporary backing document. The returned object
        is self-contained but not attached to any parent FDL document.
        """
        d = model.model_dump(exclude_none=True)
        if "dimensions" in d:
            d["dimensions"] = DimensionsFloat(**d["dimensions"])
        if "anchor_point" in d:
            d["anchor_point"] = PointFloat(**d["anchor_point"])
        if "protection_dimensions" in d:
            d["protection_dimensions"] = DimensionsFloat(**d["protection_dimensions"])
        if "protection_anchor_point" in d:
            d["protection_anchor_point"] = PointFloat(**d["protection_anchor_point"])
        return cls(**d)

    def get_rect(self) -> Rect:
        """Get framing rect as (anchor_x, anchor_y, width, height)."""
        self._check_handle()
        raw = self._lib.fdl_framing_decision_get_rect(self._handle)
        return _rect(raw)

    def get_protection_rect(self) -> Rect | None:
        """Get protection rect or None if not defined."""
        self._check_handle()
        out = ffi.new("fdl_rect_t*")
        if not self._lib.fdl_framing_decision_get_protection_rect(self._handle, out):
            return None
        return _rect(out)

    def set_protection(
        self,
        dims: DimensionsFloat,
        anchor: PointFloat,
    ) -> None:
        """Set protection dimensions and anchor point on this framing decision."""
        self._check_handle()
        self._lib.fdl_framing_decision_set_protection(
            self._handle,
            _to_c_dims_f64(dims),
            _to_c_point_f64(anchor),
        )

    def adjust_anchor_point(
        self,
        canvas: Canvas,
        h_method: str,
        v_method: str,
    ) -> None:
        """Adjust anchor point based on alignment within canvas."""
        self._check_handle()
        self._lib.fdl_framing_decision_adjust_anchor(
            self._handle,
            canvas._handle,
            H_ALIGN_TO_C[h_method],
            V_ALIGN_TO_C[v_method],
        )

    def adjust_protection_anchor_point(
        self,
        canvas: Canvas,
        h_method: str,
        v_method: str,
    ) -> None:
        """Adjust protection anchor point based on alignment within canvas."""
        self._check_handle()
        self._lib.fdl_framing_decision_adjust_protection_anchor(
            self._handle,
            canvas._handle,
            H_ALIGN_TO_C[h_method],
            V_ALIGN_TO_C[v_method],
        )

    @classmethod
    def from_framing_intent(
        cls,
        canvas: Canvas,
        framing_intent: FramingIntent,
        rounding: RoundStrategy | None = None,
    ) -> FramingDecision:
        """Create a FramingDecision from a canvas and framing intent."""
        if rounding is None:
            from .utils import get_rounding

            rounding = get_rounding()
        instance = cls(
            id="",
            framing_intent_id=framing_intent.id,
        )
        instance._lib.fdl_framing_decision_populate_from_intent(
            instance._handle,
            canvas._handle,
            framing_intent._handle,
            _to_c_round_strategy(rounding),
        )
        return instance

    def populate_from_intent(
        self,
        canvas: Canvas,
        framing_intent: FramingIntent,
        rounding: RoundStrategy | None = None,
    ) -> None:
        """Populate this framing decision from a canvas and framing intent (in-place)."""
        self._check_handle()
        if rounding is None:
            from .utils import get_rounding

            rounding = get_rounding()
        self._lib.fdl_framing_decision_populate_from_intent(
            self._handle,
            canvas._handle,
            framing_intent._handle,
            _to_c_round_strategy(rounding),
        )

    _CA_PREFIX = "fdl_framing_decision_"

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
