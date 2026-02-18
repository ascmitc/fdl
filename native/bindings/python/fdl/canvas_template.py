# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""FDL Core CanvasTemplate facade."""

from __future__ import annotations

import ctypes
import json

from .fdl_types import DimensionsFloat, DimensionsInt, PointFloat
from .rounding import RoundStrategy

from .base import (
    HandleWrapper,
    _decode_str,
)
from .converters import (
    _dims_i64,
    _round_strategy,
    _to_c_dims_i64,
    _to_c_round_strategy,
)
from .enum_maps import (
    FIT_METHOD_FROM_C,
    FIT_METHOD_TO_C,
    GEOMETRY_PATH_FROM_C,
    GEOMETRY_PATH_TO_C,
    H_ALIGN_FROM_C,
    H_ALIGN_TO_C,
    V_ALIGN_FROM_C,
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
from dataclasses import dataclass
from .constants import (
    FitMethod,
    GeometryPath,
    HAlign,
    VAlign,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .canvas import Canvas
    from .framing_decision import FramingDecision


@dataclass
class TemplateResult:
    """Result of applying a canvas template."""

    fdl: object
    _context_label: str
    _canvas_id: str
    _framing_decision_id: str

    @property
    def context(self):
        """The new context created by the template apply."""
        for item in self.fdl.contexts:
            if item.label == self._context_label:
                return item
        return None

    @property
    def canvas(self):
        """The new canvas created by the template apply."""
        for item in self.context.canvases:
            if item.id == self._canvas_id:
                return item
        return None

    @property
    def framing_decision(self):
        """The new framing decision created by the template apply."""
        for item in self.canvas.framing_decisions:
            if item.id == self._framing_decision_id:
                return item
        return None


class CanvasTemplate(HandleWrapper):
    """CanvasTemplate facade wrapping a C fdl_canvas_template_t handle."""

    def __init__(
        self,
        *,
        id: str,
        label: str = "",
        target_dimensions: DimensionsInt,
        target_anamorphic_squeeze: float = 1.0,
        fit_source: GeometryPath = GeometryPath.FRAMING_DIMENSIONS,
        fit_method: FitMethod = FitMethod.WIDTH,
        alignment_method_horizontal: HAlign = HAlign.CENTER,
        alignment_method_vertical: VAlign = VAlign.CENTER,
        round: RoundStrategy = RoundStrategy(),
        preserve_from_source_canvas: GeometryPath | None = None,
        maximum_dimensions: DimensionsInt | None = None,
        pad_to_maximum: bool = False,
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
        handle = lib.fdl_doc_add_canvas_template(
            _doc_h,
            id.encode("utf-8"),
            label.encode("utf-8"),
            int(target_dimensions.width),
            int(target_dimensions.height),
            float(target_anamorphic_squeeze),
            GEOMETRY_PATH_TO_C[fit_source],
            FIT_METHOD_TO_C[fit_method],
            H_ALIGN_TO_C[alignment_method_horizontal],
            V_ALIGN_TO_C[alignment_method_vertical],
            _to_c_round_strategy(round),
        )
        if not handle:
            raise RuntimeError("fdl_doc_add_canvas_template returned NULL")
        HandleWrapper.__init__(self, handle, lib, _backing)
        if preserve_from_source_canvas is not None:
            self.preserve_from_source_canvas = preserve_from_source_canvas
        if maximum_dimensions is not None:
            self.maximum_dimensions = maximum_dimensions
        self.pad_to_maximum = pad_to_maximum

    @property
    def id(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_id(self._handle)
        return _decode_str(raw)

    @property
    def label(self) -> str:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_label(self._handle)
        return _decode_str(raw)

    @property
    def target_dimensions(self) -> DimensionsInt:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_target_dimensions(self._handle)
        return _dims_i64(raw)

    @property
    def target_anamorphic_squeeze(self) -> float:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_target_anamorphic_squeeze(self._handle)
        return float(raw)

    @property
    def fit_source(self) -> GeometryPath:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_fit_source(self._handle)
        return GEOMETRY_PATH_FROM_C[raw]

    @property
    def fit_method(self) -> FitMethod:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_fit_method(self._handle)
        return FIT_METHOD_FROM_C[raw]

    @property
    def alignment_method_horizontal(self) -> HAlign:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_alignment_method_horizontal(self._handle)
        return H_ALIGN_FROM_C[raw]

    @property
    def alignment_method_vertical(self) -> VAlign:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_alignment_method_vertical(self._handle)
        return V_ALIGN_FROM_C[raw]

    @property
    def round(self) -> RoundStrategy:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_round(self._handle)
        return _round_strategy(raw)

    @property
    def preserve_from_source_canvas(self) -> GeometryPath | None:
        self._check_handle()
        if not self._lib.fdl_canvas_template_has_preserve_from_source_canvas(self._handle):
            return None
        raw = self._lib.fdl_canvas_template_get_preserve_from_source_canvas(self._handle)
        return GEOMETRY_PATH_FROM_C[raw]

    @preserve_from_source_canvas.setter
    def preserve_from_source_canvas(self, value: GeometryPath) -> None:
        self._check_handle()
        self._lib.fdl_canvas_template_set_preserve_from_source_canvas(self._handle, GEOMETRY_PATH_TO_C[value])

    @property
    def maximum_dimensions(self) -> DimensionsInt | None:
        self._check_handle()
        if not self._lib.fdl_canvas_template_has_maximum_dimensions(self._handle):
            return None
        raw = self._lib.fdl_canvas_template_get_maximum_dimensions(self._handle)
        return _dims_i64(raw)

    @maximum_dimensions.setter
    def maximum_dimensions(self, value: DimensionsInt) -> None:
        self._check_handle()
        self._lib.fdl_canvas_template_set_maximum_dimensions(self._handle, _to_c_dims_i64(value))

    @property
    def pad_to_maximum(self) -> bool:
        self._check_handle()
        raw = self._lib.fdl_canvas_template_get_pad_to_maximum(self._handle)
        return bool(raw)

    @pad_to_maximum.setter
    def pad_to_maximum(self, value: bool) -> None:
        self._check_handle()
        self._lib.fdl_canvas_template_set_pad_to_maximum(self._handle, int(value))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CanvasTemplate):
            return self.id == other.id
        if isinstance(other, str):
            return self.id == other
        return NotImplemented

    def __hash__(self):
        return hash((self.id,))

    def as_dict(self) -> dict:
        self._check_handle()
        json_ptr = self._lib.fdl_canvas_template_to_json(self._handle, 0)
        if not json_ptr:
            raise RuntimeError("fdl_canvas_template_to_json returned NULL")
        result = json.loads(ctypes.string_at(json_ptr))
        self._lib.fdl_free(json_ptr)
        return result

    def apply(
        self,
        source_canvas: Canvas,
        source_framing: FramingDecision,
        new_canvas_id: str,
        new_fd_name: str,
        source_context_label: str | None = None,
        context_creator: str | None = None,
    ) -> TemplateResult:
        """Apply this canvas template to a source canvas/framing decision."""
        self._check_handle()
        from .fdl import FDL

        result = self._lib.fdl_apply_canvas_template(
            self._handle,
            source_canvas._handle,
            source_framing._handle,
            new_canvas_id.encode("utf-8"),
            new_fd_name.encode("utf-8"),
            source_context_label.encode("utf-8") if source_context_label else None,
            context_creator.encode("utf-8") if context_creator else None,
        )
        if result.error:
            msg = ctypes.string_at(result.error).decode("utf-8")
            self._lib.fdl_free(result.error)
            raise ValueError(msg)
        _fdl = FDL._from_handle(result.output_fdl, self._lib)
        _context_label = ctypes.string_at(result.context_label).decode("utf-8")
        self._lib.fdl_free(result.context_label)
        _canvas_id = ctypes.string_at(result.canvas_id).decode("utf-8")
        self._lib.fdl_free(result.canvas_id)
        _framing_decision_id = ctypes.string_at(result.framing_decision_id).decode("utf-8")
        self._lib.fdl_free(result.framing_decision_id)
        return TemplateResult(
            fdl=_fdl,
            _context_label=_context_label,
            _canvas_id=_canvas_id,
            _framing_decision_id=_framing_decision_id,
        )

    _CA_PREFIX = "fdl_canvas_template_"

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
