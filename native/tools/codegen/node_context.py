# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Node.js/TypeScript-specific context builders for code generation.

These functions produce template-ready dictionaries for the TypeScript
facade layer.  Type resolution is delegated to NodeAdapter.
"""

from __future__ import annotations

import re

from .adapters import NodeAdapter
from .fdl_idl import IDL, EnumType, FreeFunctionDef, ValueType, VTMethod, VTOperator
from .ir import IRClass, IRCollection, IRMethod, IRProperty
from .shared_context import (
    ENUM_SHORT_TO_CLASS as _ENUM_SHORT_TO_TS,
    build_converter_lookup,
    build_enum_context_lookups,
    build_enum_facade_map,
    build_enum_info,
    build_enum_to_c_maps,
    build_expand_map,
    find_builder_method,
    is_lifecycle_method,
    resolve_cross_eq_class,
    vt_field_names_for_type as _vt_field_names_for_type,
)

_node = NodeAdapter()

# -----------------------------------------------------------------------
# Naming helpers
# -----------------------------------------------------------------------


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase.

    is_zero  -> isZero
    anchor_point -> anchorPoint
    """
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def class_to_module(class_name: str) -> str:
    """Map a facade class name to its kebab-case module file name.

    DimensionsInt -> dimensions-int
    FDL -> fdl
    CanvasTemplate -> canvas-template
    ClipID -> clip-id
    """
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", class_name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower().replace("_", "-")


# -----------------------------------------------------------------------
# TypeScript type resolution for value type methods
# -----------------------------------------------------------------------


def _resolve_vt_ts_type(idl_type: str, idl: IDL, *, for_self_class: str = "") -> str:
    """Resolve an IDL type used in value type methods to a TypeScript type."""
    if idl_type == "self":
        return for_self_class
    if idl_type == "bool":
        return "boolean"
    if idl_type == "string":
        return "string"
    if idl_type in ("double", "float", "f64", "int", "int64_t"):
        return "number"
    ts = _node.TYPES.get(idl_type)
    if ts:
        return ts
    if idl_type in _ENUM_SHORT_TO_TS:
        return _ENUM_SHORT_TO_TS[idl_type]
    return idl_type


# -----------------------------------------------------------------------
# C field type mappings for TypeScript value types
# -----------------------------------------------------------------------

# c_type: (ts_type, default_value)
_C_FIELD_TYPES: dict[str, tuple[str, str]] = {
    "int64_t": ("number", "0"),
    "double": ("number", "0"),
    "int": ("number", "0"),
    "uint32_t": ("number", "0"),
}


# -----------------------------------------------------------------------
# Enum context builder (TypeScript-specific)
# -----------------------------------------------------------------------


def build_node_constants_enum_context(idl_enum: EnumType) -> dict:
    """Build template context for one TypeScript string enum."""
    prefix = idl_enum.facade_prefix
    str_values = idl_enum.string_values or {}
    members = []
    for ev in idl_enum.values:
        member_name = ev.name[len(prefix) :]
        str_value = str_values.get(member_name, member_name.lower())
        members.append({"name": member_name, "str_value": str_value})

    return {
        "ts_class": idl_enum.facade_class,
        "members": members,
    }


# -----------------------------------------------------------------------
# Value type context builders
# -----------------------------------------------------------------------


def _pure_method_body(
    name: str,
    ts_class: str,
    field_names: list[str],
    method: VTMethod,
    idl: IDL,
) -> list[str]:
    """Generate TypeScript body lines for a pure (non-C-backed) value type method."""
    if name == "duplicate":
        args = ", ".join(f"this.{fn}" for fn in field_names)
        return [f"return new {ts_class}({args});"]
    if name == "format":
        parts = ", ".join(f"{fn}=${{this.{fn}}}" for fn in field_names)
        return [f"return `{ts_class}({parts})`;"]
    if name == "to_int":
        # DimensionsFloat → DimensionsInt
        ret_type = _resolve_vt_ts_type(method.returns or "void", idl, for_self_class=ts_class)
        return [f"return new {ret_type}(Math.trunc(this.width), Math.trunc(this.height));"]
    if name == "from_dimensions":
        # classmethod: DimensionsFloat.fromDimensions(dims) → self
        param_name = "dims"
        if method.params:
            param_name = snake_to_camel(method.params[0].name)
        return [f"return new {ts_class}({param_name}.width, {param_name}.height);"]
    if name == "scale_by":
        # Mutate in place (void return in IDL)
        param_name = "factor"
        if method.params:
            param_name = snake_to_camel(method.params[0].name)
        lines = []
        for fn in field_names:
            lines.append(f"this.{fn} *= {param_name};")
        return lines
    return [f"throw new Error('Not implemented: {name}');"]


_build_enum_to_c_maps = build_enum_to_c_maps


def _build_addon_args(
    params: list,
    field_names: list[str],
    idl: IDL,
    enum_to_c_maps: dict[str, str],
    needed_enum_maps: set[str],
    needed_types: set[str],
    *,
    self_obj: str | None = None,
) -> list[str]:
    """Build addon call argument list from method params.

    If self_obj is provided, it's prepended (for instance methods on value types).
    """
    addon_args: list[str] = []
    if self_obj is not None:
        addon_args.append(self_obj)

    for p in params:
        camel_name = snake_to_camel(p.name)
        if p.param_type.startswith("fdl_") and p.param_type in _node.TYPES:
            p_fields = _vt_field_names_for_type(p.param_type, idl)
            needed_types.add(_node.TYPES[p.param_type])
            addon_args.append(f"{{ {', '.join(f'{fn}: {camel_name}.{fn}' for fn in p_fields)} }}")
        elif p.param_type in enum_to_c_maps:
            map_name = enum_to_c_maps[p.param_type]
            needed_enum_maps.add(map_name)
            addon_args.append(f"{map_name}.get({camel_name})!")
        elif p.param_type == "double" and p.nullable:
            addon_args.append(f"{camel_name} ?? 0")
            addon_args.append(f"{camel_name} !== null ? 1 : 0")
        else:
            addon_args.append(camel_name)

    return addon_args


def _self_obj_expr(field_names: list[str]) -> str:
    """Build the self-as-plain-object expression for addon calls."""
    return f"{{ {', '.join(f'{fn}: this.{fn}' for fn in field_names)} }}"


def _construct_from_result(ts_class: str, field_names: list[str], var: str = "_r") -> str:
    """Build `new TsClass(_r.field1, _r.field2, ...)` expression."""
    return f"new {ts_class}({', '.join(f'{var}.{fn}' for fn in field_names)})"


def build_node_vt_method_context(method: VTMethod, vt: ValueType, idl: IDL) -> dict:
    """Build template context for one value type method (TypeScript).

    Produces flat context with pre-computed ``body_lines`` and ``params_str``.
    """
    ts_class = vt.facade_class or vt.name
    field_names = [f.name for f in vt.fields]
    ret_type = method.returns or "void"
    ts_return = _resolve_vt_ts_type(ret_type, idl, for_self_class=ts_class)

    # Parameter declarations
    params_parts: list[str] = []
    for p in method.params:
        ts_type = _resolve_vt_ts_type(p.param_type, idl, for_self_class=ts_class)
        if p.nullable:
            ts_type = f"{ts_type} | null"
        params_parts.append(f"{snake_to_camel(p.name)}: {ts_type}")

    params_str = ", ".join(params_parts)

    # Return type for out-params
    if method.out_params:
        out_ts_parts = [
            f"{snake_to_camel(op.name)}: {_resolve_vt_ts_type(op.param_type, idl, for_self_class=ts_class)}" for op in method.out_params
        ]
        ts_return = f"{{ result: {ts_return}; {'; '.join(out_ts_parts)} }}"

    # Track enum types referenced in parameter annotations (for imports)
    needed_enum_imports: set[str] = set()
    for p in method.params:
        if p.param_type in _ENUM_SHORT_TO_TS:
            needed_enum_imports.add(_ENUM_SHORT_TO_TS[p.param_type])

    # Build body lines
    enum_to_c_maps = _build_enum_to_c_maps(idl)
    needed_enum_maps: set[str] = set()
    needed_types: set[str] = set()

    self_obj = _self_obj_expr(field_names) if method.kind != "classmethod" else None
    addon_args = _build_addon_args(
        method.params,
        field_names,
        idl,
        enum_to_c_maps,
        needed_enum_maps,
        needed_types,
        self_obj=self_obj,
    )

    body_lines: list[str] = []

    if method.pure:
        # Pure methods have inline TypeScript logic
        body_lines.extend(_pure_method_body(method.name, ts_class, field_names, method, idl))
    else:
        call_str = f"addon.{method.c_function}({', '.join(addon_args)})"
        body_lines.append("const addon = getAddon();")

        if method.out_params:
            body_lines.append(f"const _out = {call_str};")
            # Extract out params
            for op in method.out_params:
                op_ts_type = _resolve_vt_ts_type(op.param_type, idl, for_self_class=ts_class)
                op_fields = _vt_field_names_for_type(op.param_type, idl)
                construct = f"new {op_ts_type}({', '.join(f'_out.{op.name}.{fn}' for fn in op_fields)})"
                body_lines.append(f"const {snake_to_camel(op.name)} = {construct};")
            # Main return
            if ret_type == "bool":
                out_fields = ", ".join(f"{snake_to_camel(op.name)}" for op in method.out_params)
                body_lines.append(f"return {{ result: Boolean(_out._return), {out_fields} }};")
            else:
                ret_fields = _vt_field_names_for_type(ret_type, idl)
                main_type = _resolve_vt_ts_type(ret_type, idl, for_self_class=ts_class)
                main_construct = f"new {main_type}({', '.join(f'_out._return.{fn}' for fn in ret_fields)})"
                out_fields = ", ".join(f"{snake_to_camel(op.name)}" for op in method.out_params)
                body_lines.append(f"return {{ result: {main_construct}, {out_fields} }};")
        elif ret_type == "bool":
            body_lines.append(f"return Boolean({call_str});")
        elif ret_type in ("self", vt.name):
            body_lines.append(f"const _r = {call_str};")
            body_lines.append(f"return {_construct_from_result(ts_class, field_names)};")
        elif ret_type in ("double", "float", "f64", "int", "int64_t"):
            body_lines.append(f"return {call_str} as number;")
        elif ret_type == "string":
            body_lines.append(f"return {call_str} as string;")
        elif ret_type == "void":
            body_lines.append(f"{call_str};")
        else:
            # Return type is a different value type
            ret_fields = _vt_field_names_for_type(ret_type, idl)
            ret_ts_type = _resolve_vt_ts_type(ret_type, idl, for_self_class=ts_class)
            if ret_fields:
                body_lines.append(f"const _r = {call_str};")
                body_lines.append(f"return {_construct_from_result(ret_ts_type, ret_fields)};")
            else:
                body_lines.append(f"return {call_str};")

    return {
        "name": snake_to_camel(method.name),
        "doc": snake_to_camel(method.name),
        "kind": method.kind,
        "params_str": params_str,
        "ts_return": ts_return,
        "body_lines": body_lines,
        "needed_enum_maps": sorted(needed_enum_maps),
        "needed_enum_imports": sorted(needed_enum_imports),
        "needed_types": sorted(needed_types),
    }


def build_node_vt_operator_context(op: VTOperator, vt: ValueType, idl: IDL) -> dict:
    """Build template context for one value type operator (TypeScript).

    Produces flat context with pre-computed ``body_lines``.
    """
    ts_class = vt.facade_class or vt.name
    field_names = [f.name for f in vt.fields]

    param_ts_type: str | None = None
    if op.param_type:
        if op.param_type == "scalar_or_point":
            param_ts_type = "PointFloat | number"
        else:
            param_ts_type = _resolve_vt_ts_type(op.param_type, idl, for_self_class=ts_class)

    ts_return = _resolve_vt_ts_type(op.returns, idl, for_self_class=ts_class)

    needed_types: set[str] = set()
    if op.param_type and op.param_type in _node.TYPES and op.param_type.startswith("fdl_"):
        needed_types.add(_node.TYPES[op.param_type])

    op_name_map: dict[str, str] = {
        "__gt__": "gt",
        "__lt__": "lt",
        "__eq__": "equals",
        "__bool__": "toBool",
        "__add__": "add",
        "__iadd__": "iadd",
        "__sub__": "sub",
        "__mul__": "mul",
    }
    ts_name = op_name_map.get(op.op, op.op.strip("_"))

    # Build body lines
    self_obj = _self_obj_expr(field_names)
    body_lines: list[str] = []

    if op.pure:
        if op.op == "__bool__":
            body_lines.append(f"return {' || '.join(f'this.{fn} !== 0' for fn in field_names)};")
        elif op.op == "__iadd__":
            for fn in field_names:
                body_lines.append(f"this.{fn} += other.{fn};")
            body_lines.append("return this;")
        else:
            body_lines.append(f"throw new Error('Not implemented: {op.op}');")
    elif op.c_function:
        body_lines.append("const addon = getAddon();")

        if op.param_type == "scalar_or_point":
            # Dispatch based on argument type:
            # scalar → call C function with (self, scalar)
            # point  → element-wise mul in pure TypeScript
            body_lines.append("if (typeof other === 'number') {")
            body_lines.append(f"  const _r = addon.{op.c_function}({self_obj}, other);")
            body_lines.append(f"  return {_construct_from_result(ts_class, field_names)};")
            body_lines.append("}")
            # Element-wise point multiplication (no C function for this)
            p_fields = _vt_field_names_for_type("fdl_point_f64_t", idl) or ["x", "y"]
            ewise_args = ", ".join(f"this.{fn} * (other as PointFloat).{fn}" for fn in p_fields)
            body_lines.append(f"return new {ts_class}({ewise_args});")
        elif param_ts_type:
            # Binary operator with typed param
            other_fields = _vt_field_names_for_type(op.param_type, idl) if op.param_type.startswith("fdl_") else field_names
            other_obj = f"{{ {', '.join(f'{fn}: other.{fn}' for fn in other_fields)} }}"
            if ts_return == "boolean":
                body_lines.append(f"return Boolean(addon.{op.c_function}({self_obj}, {other_obj}));")
            else:
                body_lines.append(f"const _r = addon.{op.c_function}({self_obj}, {other_obj});")
                body_lines.append(f"return {_construct_from_result(ts_class, field_names)};")
        else:
            # Unary operator
            if ts_return == "boolean":
                body_lines.append(f"return Boolean(addon.{op.c_function}({self_obj}));")
            else:
                body_lines.append(f"const _r = addon.{op.c_function}({self_obj});")
                body_lines.append(f"return {_construct_from_result(ts_class, field_names)};")

    return {
        "op": op.op,
        "ts_name": ts_name,
        "param_ts_type": param_ts_type,
        "ts_return": ts_return,
        "body_lines": body_lines,
        "needed_types": sorted(needed_types),
    }


def build_node_value_type_context(vt: ValueType, idl: IDL) -> dict:
    """Build template context for one TypeScript value type class."""
    ts_class = vt.facade_class
    defaults_override = vt.facade_defaults or {}

    enum_facade_map = build_enum_facade_map(idl)

    fields = []
    enum_imports: set[str] = set()
    has_float = False

    for f in vt.fields:
        c_type = f.c_type
        if c_type in _C_FIELD_TYPES:
            ts_type, default = _C_FIELD_TYPES[c_type]
            if c_type == "double":
                has_float = True
        elif c_type in enum_facade_map:
            ts_type = enum_facade_map[c_type]
            enum_imports.add(ts_type)
            if f.name in defaults_override:
                default = f"{ts_type}.{defaults_override[f.name]}"
            else:
                default = "null"
        else:
            ts_type = _node.TYPES.get(c_type, "unknown")
            default = "null"

        fields.append(
            {
                "name": f.name,
                "ts_type": ts_type,
                "default": default,
            }
        )

    field_names = [f["name"] for f in fields]

    # Build equality expression parts
    if has_float:
        eq_parts = [
            f"Math.abs(this.{f['name']} - other.{f['name']}) < _FP_ABS_TOL"
            if f["ts_type"] == "number" and f["name"] not in defaults_override
            else f"this.{f['name']} === other.{f['name']}"
            for f in fields
        ]
    else:
        eq_parts = [f"this.{f['name']} === other.{f['name']}" for f in fields]

    cross_eq_class = resolve_cross_eq_class(vt, idl)

    method_contexts = [build_node_vt_method_context(m, vt, idl) for m in vt.methods]
    operator_contexts = [build_node_vt_operator_context(o, vt, idl) for o in vt.operators]

    clone_args = ", ".join(f"this.{fn}" for fn in field_names)
    repr_expr = "`" + ts_class + "(" + ", ".join(f"{fn}=${{this.{fn}}}" for fn in field_names) + ")" + "`"
    json_entries = ", ".join(f"{fn}: this.{fn}" for fn in field_names)

    return {
        "ts_class": ts_class,
        "c_type": vt.name,
        "doc": f"Lightweight {ts_class} value type.",
        "fields": fields,
        "field_names": field_names,
        "float_compare": has_float,
        "eq_parts": eq_parts,
        "cross_eq_class": cross_eq_class,
        "enum_imports": sorted(enum_imports),
        "methods": method_contexts,
        "operators": operator_contexts,
        "clone_args": clone_args,
        "repr_expr": repr_expr,
        "json_entries": json_entries,
    }


# -----------------------------------------------------------------------
# Converter context builder (TypeScript)
# -----------------------------------------------------------------------


def build_node_converter_context(vt: ValueType, idl: IDL) -> dict:
    """Build template context for TypeScript converter functions."""
    enum_info = build_enum_info(idl)

    defaults_override = vt.facade_defaults or {}
    fields = []
    enum_from_c_imports: list[str] = []
    enum_to_c_imports: list[str] = []
    enum_class_imports: set[str] = set()

    for f in vt.fields:
        c_type = f.c_type
        if c_type in ("int64_t", "int", "uint32_t", "double"):
            from_c_expr = f"raw.{f.name}"
            to_c_expr = f"val.{f.name}"
        elif c_type in enum_info:
            info = enum_info[c_type]
            from_c_name = f"{info['map_name']}_FROM_C"
            to_c_name = f"{info['map_name']}_TO_C"
            default_member = defaults_override.get(f.name, "")
            default_expr = f"{info['facade_class']}.{default_member}" if default_member else "null"
            from_c_expr = f"{from_c_name}.get(raw.{f.name}) ?? {default_expr}"
            to_c_expr = f"{to_c_name}.get(val.{f.name})!"
            enum_from_c_imports.append(from_c_name)
            enum_to_c_imports.append(to_c_name)
            enum_class_imports.add(info["facade_class"])
        else:
            from_c_expr = f"raw.{f.name}"
            to_c_expr = f"val.{f.name}"

        fields.append(
            {
                "name": f.name,
                "from_c_expr": from_c_expr,
                "to_c_expr": to_c_expr,
            }
        )

    converter_name = snake_to_camel(vt.facade_converter) if vt.facade_converter else ""
    cap_name = converter_name[0].upper() + converter_name[1:] if converter_name else ""

    return {
        "converter": converter_name,
        "from_fn": f"from{cap_name}",
        "to_fn": f"to{cap_name}",
        "ts_class": vt.facade_class,
        "c_struct": vt.name,
        "fields": fields,
        "enum_from_c_imports": enum_from_c_imports,
        "enum_to_c_imports": enum_to_c_imports,
        "enum_class_imports": sorted(enum_class_imports),
    }


# -----------------------------------------------------------------------
# Free function context builder (TypeScript)
# -----------------------------------------------------------------------


def build_node_free_function_context(ff: FreeFunctionDef, idl: IDL) -> dict:
    """Build template context for one utility/rounding free function.

    Produces flat context with pre-computed ``body_lines`` and ``params_str``.
    """
    ts_name = snake_to_camel(ff.display_name)
    ts_return = _resolve_vt_ts_type(ff.returns or "void", idl)

    enum_to_c_maps = _build_enum_to_c_maps(idl)
    needed_enum_maps: set[str] = set()
    needed_enum_imports: set[str] = set()
    needed_types: set[str] = set()

    # Build params_str and track enum imports from param types
    params_parts: list[str] = []
    for p in ff.params:
        ts_type = _resolve_vt_ts_type(p.param_type, idl)
        if p.param_type in _ENUM_SHORT_TO_TS:
            needed_enum_imports.add(_ENUM_SHORT_TO_TS[p.param_type])
        camel_name = snake_to_camel(p.name)
        params_parts.append(f"{camel_name}: {ts_type}")
    params_str = ", ".join(params_parts)

    # Build addon args
    addon_args: list[str] = []
    for p in ff.params:
        camel_name = snake_to_camel(p.name)
        if p.param_type.startswith("fdl_") and p.param_type in _node.TYPES:
            p_fields = _vt_field_names_for_type(p.param_type, idl)
            needed_types.add(_node.TYPES[p.param_type])
            addon_args.append(f"{{ {', '.join(f'{fn}: {camel_name}.{fn}' for fn in p_fields)} }}")
        elif p.param_type in enum_to_c_maps:
            map_name = enum_to_c_maps[p.param_type]
            needed_enum_maps.add(map_name)
            addon_args.append(f"{map_name}.get({camel_name})!")
        else:
            addon_args.append(camel_name)

    # Build body lines
    call_str = f"addon.{ff.c_function}({', '.join(addon_args)})"
    body_lines: list[str] = ["const addon = getAddon();"]

    return_is_vt = ff.returns and ff.returns.startswith("fdl_") and ff.returns in _node.TYPES
    if return_is_vt:
        vt_class = _node.TYPES[ff.returns]
        needed_types.add(vt_class)
        vt_fields = _vt_field_names_for_type(ff.returns, idl)
        body_lines.append(f"const _r = {call_str};")
        body_lines.append(f"return {_construct_from_result(vt_class, vt_fields)};")
    elif ff.returns == "bool":
        body_lines.append(f"return Boolean({call_str});")
    elif ff.returns in ("double", "float", "f64", "int", "int64_t"):
        body_lines.append(f"return {call_str} as number;")
    elif ff.returns == "void" or not ff.returns:
        body_lines.append(f"{call_str};")
    else:
        body_lines.append(f"return {call_str};")

    return {
        "name": ts_name,
        "c_function": ff.c_function,
        "doc": ff.doc or ts_name,
        "params_str": params_str,
        "ts_return": ts_return,
        "body_lines": body_lines,
        "needed_enum_maps": sorted(needed_enum_maps),
        "needed_enum_imports": sorted(needed_enum_imports),
        "needed_types": sorted(needed_types),
    }


# -----------------------------------------------------------------------
# Facade class context builders (TypeScript)
# -----------------------------------------------------------------------

# Converter lookup: type_key → { from_fn, to_fn, from_module, to_module }
_CONVERTER_INFO: dict[str, dict[str, str]] = {
    "fdl_dimensions_i64_t": {"from_fn": "fromDimsI64", "to_fn": "toDimsI64"},
    "fdl_dimensions_f64_t": {"from_fn": "fromDimsF64", "to_fn": "toDimsF64"},
    "fdl_point_f64_t": {"from_fn": "fromPointF64", "to_fn": "toPointF64"},
    "fdl_rect_t": {"from_fn": "fromRect", "to_fn": "toRect"},
    "fdl_round_strategy_t": {"from_fn": "fromRoundStrategy", "to_fn": "toRoundStrategy"},
}


def _node_convert_expr(converter: str, prop_name: str) -> str:
    """Build getter conversion expression for a property."""
    if converter == "string":
        return "raw as string"
    if converter == "number":
        return "raw as number"
    if converter == "boolean":
        return "Boolean(raw)"
    if converter == "jsonValue":
        return "JSON.parse(raw as string)"
    if converter.startswith("enum"):
        return "raw"  # Filled in by template using FROM_C map
    # Value type converters
    info = {
        "dimsI64": "fromDimsI64",
        "dimsF64": "fromDimsF64",
        "pointF64": "fromPointF64",
        "rect": "fromRect",
        "roundStrategy": "fromRoundStrategy",
    }
    fn = info.get(converter)
    if fn:
        return f"{fn}(raw)"
    return "raw"


def _node_reverse_convert_expr(converter: str) -> str:
    """Build setter conversion expression for a property."""
    if converter == "string":
        return "value"
    if converter == "number":
        return "value"
    if converter == "boolean":
        return "value ? 1 : 0"
    if converter.startswith("enum"):
        return "value"  # Filled in by template using TO_C map
    info = {
        "dimsI64": "toDimsI64",
        "dimsF64": "toDimsF64",
        "pointF64": "toPointF64",
        "rect": "toRect",
        "roundStrategy": "toRoundStrategy",
    }
    fn = info.get(converter)
    if fn:
        return f"{fn}(value)"
    return "value"


def _build_node_property_context(
    prop: IRProperty,
    idl: IDL,
    enum_contexts: list[dict],
) -> dict:
    """Build template context for one facade class property."""
    type_key_to_from_c, type_key_to_to_c = build_enum_context_lookups(enum_contexts)

    ts_name = snake_to_camel(prop.name)

    # Resolve TypeScript type
    if prop.type_key == "handle_ref" and prop.handle_class:
        ts_type = prop.handle_class
        if prop.nullable:
            ts_type = f"{ts_type} | null"
    else:
        ts_type = _node.resolve_type(prop.type_key, nullable=prop.nullable)

    converter = _node.resolve_converter(prop.type_key)

    # Enum map references
    enum_from_c = type_key_to_from_c.get(prop.type_key, "")
    enum_to_c = type_key_to_to_c.get(prop.type_key, "")

    ctx: dict = {
        "name": ts_name,
        "py_name": prop.name,
        "type_key": prop.type_key,
        "ts_type": ts_type,
        "getter_fn": prop.getter_fn,
        "setter_fn": prop.setter_fn,
        "remover_fn": prop.remover_fn,
        "has_fn": prop.has_fn,
        "nullable": prop.nullable,
        "converter": converter,
        "enum_from_c": enum_from_c,
        "enum_to_c": enum_to_c,
    }
    if prop.handle_class:
        ctx["handle_class"] = prop.handle_class
        ctx["handle_class_module"] = class_to_module(prop.handle_class)
    return ctx


def _build_node_collection_context(coll: IRCollection) -> dict:
    """Build template context for one collection property."""
    return {
        "name": snake_to_camel(coll.name),
        "py_name": coll.name,
        "item_class": coll.item_class,
        "item_module": class_to_module(coll.item_class),
        "count_fn": coll.count_fn,
        "at_fn": coll.at_fn,
        "find_by_id_fn": coll.find_by_id_fn,
        "find_by_label_fn": coll.find_by_label_fn,
        "add_fn": coll.add_fn,
    }


def _build_node_builder_context(
    method: IRMethod,
    idl: IDL,
    enum_contexts: list[dict],
) -> dict:
    """Build template context for a builder method (addContext, addCanvas, etc.)."""
    _, type_key_to_to_c = build_enum_context_lookups(enum_contexts)
    expand_map = build_expand_map(idl)
    converter_lookup = build_converter_lookup(idl)

    params = []
    addon_args: list[str] = []

    for p in method.params:
        ts_type = _node.resolve_type(p.type_key, nullable=p.nullable)
        default = "null" if p.nullable and p.default is None else (_node.render_default(p.default) if p.default else None)
        ts_name = snake_to_camel(p.name)
        params.append({"name": ts_name, "type_key": p.type_key, "ts_type": ts_type, "default": default})

        if p.type_key == "string":
            addon_args.append(ts_name)
        elif p.type_key == "bytes":
            addon_args.append(ts_name)
            addon_args.append(f"{ts_name}.length")
        elif p.type_key in ("double", "int", "int64_t", "uint32_t"):
            addon_args.append(ts_name)
        elif p.expand and p.type_key in expand_map:
            for fi in expand_map[p.type_key]:
                addon_args.append(f"{ts_name}.{fi['name']}")
        elif p.type_key in converter_lookup:
            conv_camel = snake_to_camel(converter_lookup[p.type_key])
            cap = conv_camel[0].upper() + conv_camel[1:]
            addon_args.append(f"to{cap}({ts_name})")
        elif p.type_key in type_key_to_to_c:
            addon_args.append(f"{type_key_to_to_c[p.type_key]}.get({ts_name})!")
        else:
            addon_args.append(ts_name)

    return {
        "name": snake_to_camel(method.name),
        "c_function": method.function,
        "returns": method.returns,
        "returns_module": class_to_module(method.returns) if method.returns else "",
        "doc": method.doc,
        "params": params,
        "addon_args": addon_args,
        "error_pattern": method.error_handling.pattern if method.error_handling else None,
    }


def _build_node_lifecycle_context(
    method: IRMethod,
    ir_cls: IRClass,
    idl: IDL,
    enum_contexts: list[dict],
) -> dict:
    """Build template context for a lifecycle method."""
    if method.kind == "alias":
        return {
            "name": snake_to_camel(method.name),
            "kind": "alias",
            "alias_of": snake_to_camel(method.alias_of) if method.alias_of else "",
            "doc": method.doc,
        }

    if method.kind in ("instance_getter", "instance_getter_optional"):
        return_vt = method.returns
        facade_class = None
        converter_fn = None
        for vt in idl.value_types:
            if vt.name == return_vt:
                facade_class = vt.facade_class
                conv = vt.facade_converter or ""
                conv_camel = snake_to_camel(conv) if conv else ""
                cap = conv_camel[0].upper() + conv_camel[1:] if conv_camel else ""
                converter_fn = f"from{cap}"
                break
        ctx: dict = {
            "name": snake_to_camel(method.name),
            "kind": method.kind,
            "c_function": method.function,
            "returns": facade_class,
            "converter_fn": converter_fn,
            "doc": method.doc,
        }
        return ctx

    if method.kind == "composite_property":
        compose = {}
        if method.compose_from:
            compose = {k: snake_to_camel(v) for k, v in method.compose_from.items()}
        return {
            "name": snake_to_camel(method.name),
            "kind": "composite_property",
            "returns": method.returns,
            "doc": method.doc,
            "compose_from": compose,
        }

    # Generic lifecycle method (compound_setter, static_factory, class_factory, instance, validate_json)
    _, type_key_to_to_c = build_enum_context_lookups(enum_contexts)
    converter_lookup = build_converter_lookup(idl)

    params = []
    addon_args: list[str] = []

    for p in method.params:
        if p.type_key == "handle" and p.source_class:
            ts_type = p.source_class
        elif p.type_key in type_key_to_to_c:
            # Enum type — use the facade class name
            for e in idl.enums:
                if e.name == p.type_key and e.facade_class:
                    ts_type = e.facade_class
                    break
            else:
                ts_type = "string"
        else:
            ts_type = _node.resolve_type(p.type_key, nullable=p.nullable)
        default = "null" if p.nullable and p.default is None else (_node.render_default(p.default) if p.default else None)
        ts_name = snake_to_camel(p.name)
        param_ctx: dict = {"name": ts_name, "type_key": p.type_key, "ts_type": ts_type, "default": default}
        if p.global_fallback:
            param_ctx["global_fallback"] = snake_to_camel(p.global_fallback)
        params.append(param_ctx)

        # Build addon arg
        if p.type_key == "handle":
            addon_args.append(f"{ts_name}._handle")
        elif p.type_key == "bytes":
            addon_args.append(f"_{ts_name}")
            addon_args.append(f"_{ts_name}.length")
        elif p.type_key == "string":
            addon_args.append(ts_name)
        elif p.type_key in ("int", "int64_t", "uint32_t", "double"):
            addon_args.append(ts_name)
        elif p.type_key in type_key_to_to_c:
            addon_args.append(f"{type_key_to_to_c[p.type_key]}.get({ts_name})!")
        elif p.type_key in converter_lookup:
            conv_camel = snake_to_camel(converter_lookup[p.type_key])
            cap = conv_camel[0].upper() + conv_camel[1:]
            addon_args.append(f"to{cap}({ts_name})")
        else:
            addon_args.append(ts_name)

    eh = method.error_handling
    error_ctx = None
    if eh:
        result_fields_ctx = None
        if eh.result_fields:
            result_fields_ctx = []
            for rf in eh.result_fields:
                # Determine TypeScript type for interface generation
                if rf.extract in ("handle", "handle_ref"):
                    rf_ts_type = rf.wrap_class or "object"
                elif rf.extract == "scalar" and rf.scalar_type == "bool":
                    rf_ts_type = "boolean"
                elif rf.extract == "scalar":
                    rf_ts_type = "number"
                elif rf.extract == "string":
                    rf_ts_type = "string"
                else:
                    rf_ts_type = "unknown"
                result_fields_ctx.append(
                    {
                        "name": rf.name,
                        "source": rf.source,
                        "extract": rf.extract,
                        "wrap_class": rf.wrap_class,
                        "wrap_class_module": class_to_module(rf.wrap_class) if rf.wrap_class else "",
                        "converter": rf.converter,
                        "scalar_type": rf.scalar_type,
                        "private": rf.private,
                        "ts_type": rf_ts_type,
                    }
                )
        error_ctx = {
            "pattern": eh.pattern,
            "error_field": eh.error_field,
            "success_field": eh.success_field,
            "error_class": _node.resolve_error_class(eh.error_class) if eh.error_class else None,
            "free_fn": eh.free_fn,
            "count_fn": eh.count_fn,
            "at_fn": eh.at_fn,
            "result_fields": result_fields_ctx,
        }

    ctx = {
        "name": snake_to_camel(method.name),
        "kind": method.kind,
        "c_function": method.function,
        "returns": method.returns,
        "doc": method.doc,
        "params": params,
        "addon_args": addon_args,
        "error": error_ctx,
    }
    if method.factory_kwargs:

        def _camel_factory_value(val: str) -> str:
            if "." in val:
                parts = val.split(".", 1)
                return snake_to_camel(parts[0]) + "." + parts[1]
            return val

        ctx["factory_kwargs"] = [
            {"name": snake_to_camel(kw["name"]), "value": _camel_factory_value(kw["value"])} for kw in method.factory_kwargs
        ]
    return ctx


def build_node_facade_class_context(
    ir_cls: IRClass,
    idl: IDL,
    enum_contexts: list[dict],
    ir_class_by_name: dict[str, IRClass] | None = None,
) -> dict:
    """Build template context for one TypeScript facade class."""
    # Properties
    properties = [_build_node_property_context(p, idl, enum_contexts) for p in ir_cls.properties]

    # Collections
    collections = [_build_node_collection_context(c) for c in ir_cls.collections]

    # to_json function
    to_json_fn = None
    for method in ir_cls.methods:
        if method.name == "to_json":
            to_json_fn = method.function
            break

    # Builders
    builders = [_build_node_builder_context(m, idl, enum_contexts) for m in ir_cls.methods if m.kind == "builder"]

    # Lifecycle methods
    _skip_instance_names = {"to_json"}
    if to_json_fn:
        # The to_json_fn block already generates asJson; skip the lifecycle instance
        # variant that would produce a duplicate method with string_free return.
        _skip_instance_names.add("as_json")

    lifecycle = []
    for method in ir_cls.methods:
        if is_lifecycle_method(method, skip_instance_names=_skip_instance_names):
            lifecycle.append(_build_node_lifecycle_context(method, ir_cls, idl, enum_contexts))

    # Custom attributes
    custom_attrs = ir_cls.custom_attrs
    ca_prefix = ir_cls.handle_type.removesuffix("t") if custom_attrs else None

    # Free function for OwnedHandle classes (e.g., fdl_doc_t → fdl_doc_free)
    free_fn = ir_cls.handle_type.removesuffix("_t") + "_free" if ir_cls.owns_handle else None

    # Build inline interfaces for result_struct_multi return types
    # Look up dataclass definitions for accessor generation
    dc_by_name: dict[str, object] = {}
    for dc in idl.auxiliary_types.dataclasses:
        dc_by_name[dc.class_name] = dc

    inline_interfaces: list[dict] = []
    for method_ctx in lifecycle:
        error = method_ctx.get("error")
        if error and error.get("pattern") == "result_struct_multi" and error.get("result_fields"):
            fields = []
            for rf in error["result_fields"]:
                f_name = f"_{rf['name']}" if rf.get("private") else rf["name"]
                fields.append(
                    {
                        "name": f_name,
                        "type": rf["ts_type"],
                        "private": rf.get("private", False),
                    }
                )
            # Check if there's a matching dataclass with accessor definitions
            returns_name = method_ctx["returns"]
            dc_def = dc_by_name.get(returns_name)
            accessors = None
            if dc_def and dc_def.accessors:
                accessors = []
                for acc in dc_def.accessors:
                    # Convert dotted collection path to camelCase parts
                    coll_parts = acc.collection.split(".")
                    camel_coll = ".".join(snake_to_camel(p) for p in coll_parts)
                    accessors.append(
                        {
                            "name": snake_to_camel(acc.name),
                            "returns": acc.returns,
                            "doc": acc.doc,
                            "lookup": acc.lookup,
                            "collection": camel_coll,
                            "key_field": acc.key_field,  # Keep snake_case — matches _field_name in class
                        }
                    )
            inline_interfaces.append(
                {
                    "name": returns_name,
                    "fields": fields,
                    "accessors": accessors,
                }
            )

    # Constructor (init)
    init_ctx = None
    if ir_cls.init and ir_class_by_name:
        init_ctx = _build_node_init_context(ir_cls, idl, enum_contexts, ir_class_by_name)

    # Build set of result type names that are classes (have accessors)
    class_result_types = {iface["name"] for iface in inline_interfaces if iface.get("accessors")}

    return {
        "name": ir_cls.name,
        "handle_type": ir_cls.handle_type,
        "owns_handle": ir_cls.owns_handle,
        "free_fn": free_fn,
        "identity_attr": snake_to_camel(ir_cls.identity_attr) if ir_cls.identity_attr else None,
        "custom_attrs": custom_attrs,
        "ca_prefix": ca_prefix,
        "pydantic_model": ir_cls.pydantic_model,
        "properties": properties,
        "collections": collections,
        "to_json_fn": to_json_fn,
        "builders": builders,
        "lifecycle": lifecycle,
        "inline_interfaces": inline_interfaces,
        "class_result_types": class_result_types,
        "init": init_ctx,
    }


def _build_node_init_context(
    ir_cls: IRClass,
    idl: IDL,
    enum_contexts: list[dict],
    ir_class_by_name: dict[str, IRClass],
) -> dict | None:
    """Build template context for an options-object constructor."""
    init = ir_cls.init
    if not init:
        return None

    builder_ir_method = find_builder_method(ir_cls, init, ir_class_by_name)
    if not builder_ir_method:
        return None

    # Reuse builder context for addon args
    builder_ctx = _build_node_builder_context(builder_ir_method, idl, enum_contexts)

    # Build init param list
    init_params = []
    for p in init.params:
        if p.type_key == "ignore":
            init_params.append(
                {
                    "name": snake_to_camel(p.name),
                    "type_key": "ignore",
                    "ts_type": "object",
                    "default": "null",
                    "ignore": True,
                    "optional": True,
                }
            )
        else:
            ts_type = _node.resolve_type(p.type_key, nullable=p.nullable)
            default = _node.render_default(p.default) if p.default else None
            optional = default is not None or p.nullable
            if p.nullable and default is None:
                default = "null"
            init_params.append(
                {
                    "name": snake_to_camel(p.name),
                    "type_key": p.type_key,
                    "ts_type": ts_type,
                    "default": default,
                    "ignore": False,
                    "optional": optional,
                }
            )

    # Remap builder addon_args to reference init param variables.
    # Params with defaults use the local `_paramName` variable;
    # params without defaults use `opts.paramName`.
    builder_params = builder_ctx["params"]
    init_param_names_with_defaults = {
        snake_to_camel(p.name) for p in init.params if p.default is not None or (p.nullable and p.type_key != "ignore")
    }
    addon_args: list[str] = []
    for arg in builder_ctx["addon_args"]:
        matched = False
        for bp in builder_params:
            bp_name = bp["name"]
            # Choose prefix: _ for defaulted params, opts. for required params
            pfx = "_" if bp_name in init_param_names_with_defaults else "opts."
            if arg == bp_name:
                addon_args.append(f"{pfx}{bp_name}")
                matched = True
                break
            elif arg.startswith(bp_name + "."):
                suffix = arg[len(bp_name) :]
                addon_args.append(f"{pfx}{bp_name}{suffix}")
                matched = True
                break
            elif arg.endswith(f"({bp_name})"):
                prefix_str = arg[: arg.index("(") + 1]
                addon_args.append(f"{prefix_str}{pfx}{bp_name})")
                matched = True
                break
            elif arg.endswith(f"({bp_name})!"):
                prefix_str = arg[: arg.index("(") + 1]
                addon_args.append(f"{prefix_str}{pfx}{bp_name})!")
                matched = True
                break
        if not matched:
            addon_args.append(arg)

    # Value type zero defaults for compound setter args (TypeScript)
    vt_zeros = {
        "fdl_point_f64_t": "new PointFloat(0, 0)",
        "fdl_dimensions_i64_t": "new DimensionsInt(0, 0)",
        "fdl_dimensions_f64_t": "new DimensionsFloat(0, 0)",
    }
    init_param_by_name = {p.name: p for p in init.params}

    # Build post-setter contexts
    post_setter_ctx = []
    for ps in init.post_setters:
        # For 'always' property setters, find the init param default
        prop_default = None
        if ps.kind == "property" and ps.always and ps.property:
            ip = init_param_by_name.get(ps.property)
            if ip and ip.default:
                prop_default = _node.render_default(ip.default)
        ctx: dict = {
            "kind": ps.kind,
            "property": snake_to_camel(ps.property) if ps.property else None,
            "method": snake_to_camel(ps.method) if ps.method else None,
            "condition": snake_to_camel(ps.condition) if ps.condition else None,
            "always": ps.always,
            "prop_default": prop_default,
        }
        if ps.args:
            args = []
            for arg_name, param_name in ps.args.items():
                ip = init_param_by_name.get(param_name)
                default_expr = None
                if ip and ip.nullable:
                    default_expr = vt_zeros.get(ip.type_key)
                args.append(
                    {
                        "name": snake_to_camel(arg_name),
                        "param": snake_to_camel(param_name),
                        "default": default_expr,
                    }
                )
            ctx["args"] = args
        else:
            ctx["args"] = []
        post_setter_ctx.append(ctx)

    parent_handle_map = {0: None, 1: "docH", 2: "ctxH", 3: "canvasH"}
    parent_handle = parent_handle_map[init.depth]

    return {
        "depth": init.depth,
        "parent_handle": parent_handle,
        "builder_fn": builder_ctx["c_function"],
        "addon_args": addon_args,
        "params": init_params,
        "post_setters": post_setter_ctx,
    }
