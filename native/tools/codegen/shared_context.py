# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Language-neutral context builders and shared helpers for code generation.

These functions transform the parsed IDL into template-ready dictionaries
consumed by Jinja2 templates for *all* target languages.  Nothing here
references Python types, converters, or adapters.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .fdl_idl import IDL, EnumType, ValueType


# -----------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------


def camel_to_upper_snake(name: str) -> str:
    """Convert CamelCase to UPPER_SNAKE: GeometryPath → GEOMETRY_PATH."""
    result = ""
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            result += "_"
        result += ch.upper()
    return result


# -----------------------------------------------------------------------
# IDL lookup helpers (used by multiple language context builders)
# -----------------------------------------------------------------------


def vt_field_names_for_type(idl_type: str, idl: IDL) -> list[str]:
    """Return field names for a value type by its IDL type name."""
    for vt in idl.value_types:
        if vt.name == idl_type:
            return [f.name for f in vt.fields]
    return []


# Short enum names used as parameter types in VT methods and free functions
# (e.g. "rounding_even" instead of the full IDL enum name "fdl_rounding_even_t").
ENUM_SHORT_NAMES: set[str] = {
    "rounding_even",
    "rounding_mode",
    "fit_method",
    "geometry_path",
    "halign",
    "valign",
}

# Short enum name → facade class name (used for type resolution and TO_C maps).
ENUM_SHORT_TO_CLASS: dict[str, str] = {
    "rounding_even": "RoundingEven",
    "rounding_mode": "RoundingMode",
    "fit_method": "FitMethod",
    "geometry_path": "GeometryPath",
    "halign": "HAlign",
    "valign": "VAlign",
}


def build_enum_to_c_maps(idl: IDL) -> dict[str, str]:
    """Build lookup from IDL enum name / short name → TO_C map constant name.

    Covers both the full IDL enum names (e.g. "fdl_halign_t") and the short
    names used in value type methods and free functions (e.g. "halign").
    """
    m: dict[str, str] = {}
    for e in idl.enums:
        if e.facade_class:
            m[e.name] = f"{camel_to_upper_snake(e.facade_class)}_TO_C"
    for short_name, cls_name in ENUM_SHORT_TO_CLASS.items():
        m[short_name] = f"{camel_to_upper_snake(cls_name)}_TO_C"
    return m


def build_converter_lookup(idl: IDL) -> dict[str, str]:
    """Map value type name → facade converter function name."""
    return {vt.name: vt.facade_converter for vt in idl.value_types if vt.facade_converter}


def build_expand_map(idl: IDL) -> dict[str, list[dict]]:
    """Map value type name → list of field dicts with name and coerce type.

    Used by builder/lifecycle/free-function context builders to expand
    value type parameters into individual field arguments.
    """
    expand_map: dict[str, list[dict]] = {}
    for vt in idl.value_types:
        if vt.facade_class:
            fields = []
            for f in vt.fields:
                coerce = "int" if f.c_type in ("int64_t", "int", "uint32_t") else "float" if f.c_type == "double" else None
                fields.append({"name": f.name, "coerce": coerce})
            expand_map[vt.name] = fields
    return expand_map


def build_enum_facade_map(idl: IDL) -> dict[str, str]:
    """Map IDL enum name → facade class name for enums with facade metadata."""
    return {e.name: e.facade_class for e in idl.enums if e.facade_class}


def build_enum_info(idl: IDL) -> dict[str, dict]:
    """Build enum metadata lookup: IDL enum name → {facade_class, map_name}.

    Used by converter context builders across all language targets.
    """
    info: dict[str, dict] = {}
    for e in idl.enums:
        if e.facade_class:
            info[e.name] = {
                "facade_class": e.facade_class,
                "map_name": camel_to_upper_snake(e.facade_class),
            }
    return info


def build_enum_context_lookups(enum_contexts: list[dict]) -> tuple[dict[str, str], dict[str, str]]:
    """Build FROM_C / TO_C map name lookups from enum context dicts.

    Returns (type_key_to_from_c, type_key_to_to_c).
    """
    type_key_to_from_c = {ectx["idl_name"]: f"{ectx['map_name']}_FROM_C" for ectx in enum_contexts}
    type_key_to_to_c = {ectx["idl_name"]: f"{ectx['map_name']}_TO_C" for ectx in enum_contexts}
    return type_key_to_from_c, type_key_to_to_c


def resolve_cross_eq_class(vt: ValueType, idl: IDL) -> str | None:
    """Resolve the cross-type equality sibling facade class name.

    E.g. DimensionsInt ↔ DimensionsFloat.
    """
    if not vt.cross_eq:
        return None
    for other_vt in idl.value_types:
        if other_vt.name == vt.cross_eq:
            return other_vt.facade_class
    return None


def find_builder_method(ir_cls, init, ir_class_by_name: dict) -> object | None:
    """Find the IR builder method for an init definition.

    For depth 0 (root/OwnedHandle), searches on the class itself.
    For deeper levels, searches on the parent class.
    """
    if init.depth == 0:
        for m in ir_cls.methods:
            if m.name == init.builder_method:
                return m
    else:
        parent_ir = ir_class_by_name.get(ir_cls.parent)
        if not parent_ir:
            return None
        for m in parent_ir.methods:
            if m.name == init.builder_method:
                return m
    return None


# -----------------------------------------------------------------------
# Lifecycle method filtering
# -----------------------------------------------------------------------

LIFECYCLE_KINDS = frozenset(
    {
        "static_factory",
        "class_factory",
        "alias",
        "compound_setter",
        "composite_property",
        "instance_getter",
        "instance_getter_optional",
        "validate_json",
    }
)


def is_lifecycle_method(method, *, skip_instance_names: set[str] | None = None) -> bool:
    """Check if an IR method should be included in lifecycle contexts.

    Args:
        method: An IRMethod instance.
        skip_instance_names: Instance method names to exclude (default: {"to_json"}).
    """
    if skip_instance_names is None:
        skip_instance_names = {"to_json"}
    if method.kind in LIFECYCLE_KINDS:
        return True
    return method.kind == "instance" and method.name not in skip_instance_names and (method.params or method.error_handling)


# -----------------------------------------------------------------------
# Jinja2 environment factory
# -----------------------------------------------------------------------

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _to_camel(name: str) -> str:
    """Convert a snake_case or _snake_case identifier to camelCase.

    Examples: '_context_label' -> 'contextLabel', 'canvas_id' -> 'canvasId'
    """
    parts = name.lstrip("_").split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def make_jinja_env() -> Environment:
    """Create a Jinja2 environment pointing at the templates directory."""
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["to_camel"] = _to_camel
    return env


# -----------------------------------------------------------------------
# Enum context builders
# -----------------------------------------------------------------------


def build_enum_context(idl_enum: EnumType) -> dict:
    """Build template context for one enum's forward/reverse maps."""
    prefix = idl_enum.facade_prefix
    values = []
    for ev in idl_enum.values:
        member = ev.name[len(prefix) :]  # strip prefix to get member name
        values.append({"name": ev.name, "member": member, "value": ev.value})

    facade_class = idl_enum.facade_class
    map_name = camel_to_upper_snake(facade_class)

    return {
        "idl_name": idl_enum.name,
        "facade_class": facade_class,
        "prefix": prefix,
        "map_name": map_name,
        "entries": values,
    }
