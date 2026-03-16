# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
# ruff: noqa: I001
"""FDL Core FDL facade."""

from __future__ import annotations

from fdl_ffi import ffi
import json

from .fdl_types import DimensionsFloat, DimensionsInt, PointFloat
from .rounding import RoundStrategy

from .base import (
    CollectionWrapper,
    OwnedHandle,
    _decode_str,
    _encode_str,
)
from .converters import (
    _to_c_round_strategy,
)
from .enum_maps import (
    FIT_METHOD_TO_C,
    GEOMETRY_PATH_TO_C,
    H_ALIGN_TO_C,
    V_ALIGN_TO_C,
)
from .header import Version
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
    from .constants import (
        FitMethod,
        GeometryPath,
        HAlign,
        VAlign,
    )
    from .canvas_template import CanvasTemplate
    from .context import Context
    from .framing_intent import FramingIntent
    from .models import FramingDecisionList


class FDL(OwnedHandle):
    """FDL facade wrapping a C fdl_doc_t handle."""

    def __init__(
        self,
        *,
        uuid: str | None = None,
        version_major: int = 2,
        version_minor: int = 0,
        fdl_creator: str = "",
        default_framing_intent: str | None = None,
    ) -> None:
        from fdl_ffi import get_lib

        lib = get_lib()
        import uuid as _uuid_mod

        if uuid is None:
            uuid = str(_uuid_mod.uuid4())
        handle = lib.fdl_doc_create_with_header(
            uuid.encode("utf-8"),
            int(version_major),
            int(version_minor),
            fdl_creator.encode("utf-8"),
            default_framing_intent.encode("utf-8") if default_framing_intent else ffi.NULL,
        )
        if not handle:
            raise RuntimeError("fdl_doc_create_with_header returned NULL")
        OwnedHandle.__init__(self, handle, lib)

    @property
    def uuid(self) -> str | None:
        self._check_handle()
        raw = self._lib.fdl_doc_get_uuid(self._handle)
        return _decode_str(raw)

    @uuid.setter
    def uuid(self, value: str) -> None:
        self._check_handle()
        self._lib.fdl_doc_set_uuid(self._handle, _encode_str(value))

    @property
    def fdl_creator(self) -> str | None:
        self._check_handle()
        raw = self._lib.fdl_doc_get_fdl_creator(self._handle)
        return _decode_str(raw)

    @fdl_creator.setter
    def fdl_creator(self, value: str) -> None:
        self._check_handle()
        self._lib.fdl_doc_set_fdl_creator(self._handle, _encode_str(value))

    @property
    def default_framing_intent(self) -> str | None:
        self._check_handle()
        raw = self._lib.fdl_doc_get_default_framing_intent(self._handle)
        return _decode_str(raw)

    @default_framing_intent.setter
    def default_framing_intent(self, value: str) -> None:
        self._check_handle()
        self._lib.fdl_doc_set_default_framing_intent(self._handle, _encode_str(value))

    @property
    def version_major(self) -> int:
        self._check_handle()
        raw = self._lib.fdl_doc_get_version_major(self._handle)
        return int(raw)

    @property
    def version_minor(self) -> int:
        self._check_handle()
        raw = self._lib.fdl_doc_get_version_minor(self._handle)
        return int(raw)

    @property
    def contexts(self) -> CollectionWrapper[Context]:
        self._check_handle()
        from .context import Context

        return CollectionWrapper(
            lib=self._lib,
            parent_handle=self._handle,
            item_cls=Context,
            count_fn=self._lib.fdl_doc_contexts_count,
            at_fn=self._lib.fdl_doc_context_at,
            find_by_id_fn=None,
            find_by_label_fn=self._lib.fdl_doc_context_find_by_label,
            doc_ref=self._doc_ref,
        )

    @property
    def framing_intents(self) -> CollectionWrapper[FramingIntent]:
        self._check_handle()
        from .framing_intent import FramingIntent

        return CollectionWrapper(
            lib=self._lib,
            parent_handle=self._handle,
            item_cls=FramingIntent,
            count_fn=self._lib.fdl_doc_framing_intents_count,
            at_fn=self._lib.fdl_doc_framing_intent_at,
            find_by_id_fn=self._lib.fdl_doc_framing_intent_find_by_id,
            find_by_label_fn=None,
            doc_ref=self._doc_ref,
        )

    @property
    def canvas_templates(self) -> CollectionWrapper[CanvasTemplate]:
        self._check_handle()
        from .canvas_template import CanvasTemplate

        return CollectionWrapper(
            lib=self._lib,
            parent_handle=self._handle,
            item_cls=CanvasTemplate,
            count_fn=self._lib.fdl_doc_canvas_templates_count,
            at_fn=self._lib.fdl_doc_canvas_template_at,
            find_by_id_fn=self._lib.fdl_doc_canvas_template_find_by_id,
            find_by_label_fn=None,
            doc_ref=self._doc_ref,
        )

    def as_dict(self) -> dict:
        self._check_handle()
        json_ptr = self._lib.fdl_doc_to_json(self._handle, 0)
        if not json_ptr:
            raise RuntimeError("fdl_doc_to_json returned NULL")
        result = json.loads(ffi.string(json_ptr))
        self._lib.fdl_free(json_ptr)
        return result

    def to_model(self) -> FramingDecisionList:
        """Convert to a Pydantic ``FramingDecisionList`` instance.

        Returns a pure-data Pydantic model suitable for serialization,
        API responses, and interoperability with web frameworks.
        """
        from .models import FramingDecisionList

        return FramingDecisionList.model_validate(self.as_dict())

    @classmethod
    def from_model(cls, model: FramingDecisionList) -> FDL:
        """Create an ``FDL`` facade from a Pydantic model.

        Parses the model's JSON representation through the C core,
        producing a fully validated, handle-backed facade object.
        """
        json_bytes = model.model_dump_json(by_alias=True).encode("utf-8")
        return cls.parse(json_bytes)

    def add_framing_intent(
        self,
        id: str,
        label: str,
        aspect_ratio: DimensionsInt,
        protection: float,
    ) -> FramingIntent:
        """Add a framing intent to the document."""
        self._check_handle()
        from .framing_intent import FramingIntent

        handle = self._lib.fdl_doc_add_framing_intent(
            self._handle,
            id.encode("utf-8"),
            label.encode("utf-8"),
            int(aspect_ratio.width),
            int(aspect_ratio.height),
            float(protection),
        )
        if not handle:
            raise RuntimeError("fdl_doc_add_framing_intent returned NULL")
        return FramingIntent._from_handle(handle, self._lib, self._doc_ref)

    def add_context(
        self,
        label: str,
        context_creator: str | None = None,
    ) -> Context:
        """Add a context to the document."""
        self._check_handle()
        from .context import Context

        handle = self._lib.fdl_doc_add_context(
            self._handle,
            label.encode("utf-8"),
            context_creator.encode("utf-8") if context_creator else ffi.NULL,
        )
        if not handle:
            raise RuntimeError("fdl_doc_add_context returned NULL")
        return Context._from_handle(handle, self._lib, self._doc_ref)

    def add_canvas_template(
        self,
        id: str,
        label: str,
        target_dimensions: DimensionsInt,
        target_anamorphic_squeeze: float,
        fit_source: GeometryPath,
        fit_method: FitMethod,
        alignment_method_horizontal: HAlign,
        alignment_method_vertical: VAlign,
        round: RoundStrategy,
    ) -> CanvasTemplate:
        """Add a canvas template to the document."""
        self._check_handle()
        from .canvas_template import CanvasTemplate

        handle = self._lib.fdl_doc_add_canvas_template(
            self._handle,
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
        return CanvasTemplate._from_handle(handle, self._lib, self._doc_ref)

    @classmethod
    def parse(
        cls,
        json_bytes: bytes,
    ) -> FDL:
        """Parse JSON bytes into a facade FDL document."""
        from fdl_ffi import get_lib

        lib = get_lib()
        result = lib.fdl_doc_parse_json(
            json_bytes,
            len(json_bytes),
        )
        if result.error:
            msg = ffi.string(result.error).decode("utf-8")
            lib.fdl_free(result.error)
            raise ValueError(msg)
        return cls._from_handle(result.doc, lib)

    @classmethod
    def create(
        cls,
        uuid: str,
        version_major: int = 2,
        version_minor: int = 0,
        fdl_creator: str = "",
        default_framing_intent: str | None = None,
    ) -> FDL:
        """Create a new empty FDL document with header fields."""
        from fdl_ffi import get_lib

        lib = get_lib()
        handle = lib.fdl_doc_create_with_header(
            uuid.encode("utf-8"),
            version_major,
            version_minor,
            fdl_creator.encode("utf-8"),
            default_framing_intent.encode("utf-8") if default_framing_intent else ffi.NULL,
        )
        if not handle:
            raise RuntimeError("fdl_doc_create_with_header returned NULL")
        return cls._from_handle(handle, lib)

    def validate(self) -> None:
        """Run C-core schema + semantic validation."""
        self._check_handle()
        vr = self._lib.fdl_doc_validate(self._handle)
        try:
            count = self._lib.fdl_validation_result_error_count(vr)
            if count > 0:
                errors = []
                for i in range(count):
                    msg_ptr = self._lib.fdl_validation_result_error_at(vr, i)
                    if msg_ptr:
                        errors.append(ffi.string(msg_ptr).decode("utf-8"))
                from .errors import FDLValidationError

                raise FDLValidationError("Validation failed!\n" + "\n".join(errors))
        finally:
            self._lib.fdl_validation_result_free(vr)

    def as_json(
        self,
        indent: int | None = 2,
        **kwargs,
    ) -> str:
        """Serialize to JSON string via C core."""
        self._check_handle()
        json_ptr = self._lib.fdl_doc_to_json(
            self._handle,
            indent or 0,
        )
        if not json_ptr:
            raise RuntimeError("fdl_doc_to_json returned NULL")
        result = ffi.string(json_ptr).decode("utf-8")
        self._lib.fdl_free(json_ptr)
        return result

    @property
    def version(self) -> Version:
        """Composite property — FDL version from major/minor."""
        return Version(
            major=self.version_major,
            minor=self.version_minor,
        )

    _CA_PREFIX = "fdl_doc_"

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
