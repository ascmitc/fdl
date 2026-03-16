# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Intermediate Representation (IR) for code generation.

Transforms parsed IDL object model into a language-neutral IR that
Jinja2 templates consume. Each IRClass represents an idiomatic class
in the target language, with properties backed by C ABI getters/setters
and collections backed by count/at/find patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# -----------------------------------------------------------------------
# DefaultDescriptor — structured representation of default values
# -----------------------------------------------------------------------


@dataclass
class DefaultDescriptor:
    """Language-neutral representation of a parameter default value.

    Replaces raw syntax strings (e.g. ``"FitMethod.WIDTH"``) with
    a structured form that each language adapter can render independently.
    """

    kind: str  # "none", "literal", "enum_member", "constructor"
    value: str | None = None  # For "literal": the raw value (e.g. "2", "0.0", "False")
    enum_class: str | None = None  # For "enum_member": e.g. "FitMethod"
    member: str | None = None  # For "enum_member": e.g. "WIDTH"
    constructor_class: str | None = None  # For "constructor": e.g. "DimensionsFloat"
    constructor_kwargs: dict[str, str] | None = None  # For "constructor": e.g. {"width": "0.0"}


_ENUM_MEMBER_RE = re.compile(r"^([A-Z][A-Za-z]+)\.([A-Z_]+)$")
_CONSTRUCTOR_RE = re.compile(r"^([A-Z][A-Za-z]+)\((.*)\)$", re.DOTALL)
_KWARG_RE = re.compile(r"(\w+)=([\w.]+)")


def parse_default(raw: str) -> DefaultDescriptor:
    """Parse a raw default value string into a DefaultDescriptor."""
    if raw == "None":
        return DefaultDescriptor(kind="none")

    m = _ENUM_MEMBER_RE.match(raw)
    if m:
        return DefaultDescriptor(kind="enum_member", enum_class=m.group(1), member=m.group(2))

    m = _CONSTRUCTOR_RE.match(raw)
    if m:
        cls_name, args_str = m.group(1), m.group(2).strip()
        kwargs = dict(_KWARG_RE.findall(args_str)) if args_str else None
        return DefaultDescriptor(kind="constructor", constructor_class=cls_name, constructor_kwargs=kwargs)

    return DefaultDescriptor(kind="literal", value=raw)


# -----------------------------------------------------------------------
# IR dataclasses
# -----------------------------------------------------------------------


@dataclass
class IRProperty:
    """A readable (and optionally writable) property on a class."""

    name: str
    type_key: str  # Language-neutral key resolved by language adapters
    getter_fn: str
    setter_fn: str | None = None
    remover_fn: str | None = None
    has_fn: str | None = None
    nullable: bool = False
    handle_class: str | None = None  # For handle_ref: target facade class name

    @property
    def read_only(self) -> bool:
        return self.setter_fn is None


@dataclass
class IRCollection:
    """A typed collection (list-like) exposed on a class."""

    name: str
    item_class: str  # Name of the IRClass for the item type
    count_fn: str
    at_fn: str
    find_by_id_fn: str | None = None
    find_by_label_fn: str | None = None
    add_fn: str | None = None


@dataclass
class IRMethodParam:
    """A parameter for a method."""

    name: str
    type_key: str  # Language-neutral key resolved by language adapters
    nullable: bool = False
    default: DefaultDescriptor | None = None  # Structured default value
    expand: bool = False  # Expand value type fields as separate C args
    source_class: str | None = None  # For handle params: which facade class
    global_fallback: str | None = None  # For nullable params: fallback function name


@dataclass
class IRResultField:
    """A field in a multi-field result struct extraction."""

    name: str  # field name (e.g. "doc")
    source: str  # C struct field name (e.g. "output_doc")
    extract: str  # "handle", "scalar", "value_type", "string"
    wrap_class: str | None = None  # For extract=handle
    converter: str | None = None  # For extract=value_type
    scalar_type: str | None = None  # For extract=scalar (e.g. "bool", "int")
    private: bool = False  # If True, prefix field name with _ in constructor call


@dataclass
class IRErrorHandling:
    """Error handling pattern for a method."""

    pattern: str  # "null_check", "result_struct", "result_struct_multi", "validation"
    error_field: str | None = None
    success_field: str | None = None
    error_class: str | None = None
    free_fn: str | None = None
    count_fn: str | None = None  # For validation: error count function
    at_fn: str | None = None  # For validation: error-at function
    result_fields: list[IRResultField] | None = None  # For result_struct_multi


@dataclass
class IRMethod:
    """A method on a class (instance, static_factory, builder, compound_setter, etc.)."""

    name: str
    function: str  # C ABI function name
    kind: str  # "instance", "static_factory", "builder", "compound_setter", "alias"
    params: list[IRMethodParam] = field(default_factory=list)
    returns: str | None = None  # Return class/type name
    error_handling: IRErrorHandling | None = None
    doc: str = ""
    alias_of: str | None = None  # For "alias" kind: target method name
    compose_from: dict[str, str] | None = None  # For "composite_property" kind: {field: source_prop}
    factory_kwargs: list[dict] | None = None  # For "class_factory" kind: [{name, value}]


@dataclass
class IRInitParam:
    """A parameter for a keyword-argument constructor."""

    name: str
    type_key: str  # Language-neutral key resolved by language adapters
    nullable: bool = False
    default: DefaultDescriptor | None = None  # Structured default value


@dataclass
class IRInitPostSetter:
    """A post-construction setter call."""

    kind: str  # "property" or "compound"
    property: str | None = None
    method: str | None = None
    condition: str | None = None
    args: dict[str, str] | None = None
    always: bool = False


@dataclass
class IRInit:
    """Keyword-argument constructor definition for a facade class."""

    depth: int  # scaffolding depth: 1=doc->obj, 2=doc->ctx->obj, 3=doc->ctx->canvas->obj
    builder_method: str  # name of builder method on parent class
    params: list[IRInitParam] = field(default_factory=list)
    post_setters: list[IRInitPostSetter] = field(default_factory=list)


@dataclass
class IRClass:
    """A class in the facade, backed by an opaque C handle."""

    name: str
    handle_type: str  # C opaque handle type, e.g. "fdl_doc_t"
    owns_handle: bool
    parent: str | None = None
    factory: str | None = None
    destructor: str | None = None
    identity_attr: str | None = None  # "id" for Canvas/FD/FI/CT, "label" for Context, None for FDL
    custom_attrs: bool = False  # True if this class supports custom attributes
    pydantic_model: str | None = None  # Pydantic model class name for to_model/from_model bridge
    properties: list[IRProperty] = field(default_factory=list)
    collections: list[IRCollection] = field(default_factory=list)
    methods: list[IRMethod] = field(default_factory=list)
    init: IRInit | None = None


@dataclass
class IR:
    """Complete intermediate representation for facade generation."""

    classes: list[IRClass] = field(default_factory=list)
