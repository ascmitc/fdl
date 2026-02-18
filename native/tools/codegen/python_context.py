# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Python-specific context builders for code generation.

These functions produce template-ready dictionaries for the Python facade
and FFI bindings.  Type resolution is delegated to PythonAdapter.
"""

from __future__ import annotations

import re

from .adapters import PythonAdapter
from .fdl_idl import IDL, EnumType, FreeFunctionDef, ValueType, VTMethod, VTOperator
from .shared_context import camel_to_upper_snake


def _class_to_module(class_name: str) -> str:
    """Map a facade class name to its per-class module (e.g. ClipID → clip_id)."""
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", class_name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


_py = PythonAdapter()


# -----------------------------------------------------------------------
# Enum context builders (Python-specific)
# -----------------------------------------------------------------------


def build_constants_enum_context(idl_enum: EnumType) -> dict:
    """Build template context for one StrEnum class in _constants.py."""
    prefix = idl_enum.facade_prefix
    str_values = idl_enum.string_values or {}
    members = []
    for ev in idl_enum.values:
        member_name = ev.name[len(prefix) :]
        str_value = str_values.get(member_name, member_name.lower())
        members.append({"name": member_name, "str_value": str_value})

    return {
        "python_class": idl_enum.facade_class,
        "members": members,
    }


# -----------------------------------------------------------------------
# Value type helpers
# -----------------------------------------------------------------------

# C type → Python type and default for value type generation
_C_FIELD_TYPES: dict[str, tuple[str, str, str]] = {
    # c_type: (python_type, default_value, coerce_function)
    "int64_t": ("int", "0", "int"),
    "double": ("float", "0.0", "float"),
    "int": ("int", "0", "int"),
    "uint32_t": ("int", "0", "int"),
}

# Enum IDL short names — all enums are passed as str in Python VT methods
_ENUM_SHORT_NAMES = {"rounding_even", "rounding_mode", "fit_method", "geometry_path", "halign", "valign"}


def _resolve_vt_python_type(idl_type: str, idl: IDL, *, for_self_class: str = "") -> str:
    """Resolve an IDL type used in value type methods to a Python type string."""
    if idl_type == "self":
        return for_self_class
    if idl_type == "bool":
        return "bool"
    if idl_type == "string":
        return "str"
    if idl_type in ("double", "float", "f64"):
        return "float"
    if idl_type in ("int", "int64_t"):
        return "int"
    # Check if it's a known value type
    py = _py.TYPES.get(idl_type)
    if py:
        return py
    if idl_type in _ENUM_SHORT_NAMES:
        return "str"
    return idl_type


def _vt_field_names_for_type(idl_type: str, idl: IDL) -> list[str]:
    """Get field names for a value type by IDL type name."""
    for vt in idl.value_types:
        if vt.name == idl_type:
            return [f.name for f in vt.fields]
    return []


# -----------------------------------------------------------------------
# Value type context builders
# -----------------------------------------------------------------------


def build_vt_method_context(method: VTMethod, vt: ValueType, idl: IDL) -> dict:
    """Build template context for one value type method."""
    python_class = vt.facade_class or vt.name
    field_names = [f.name for f in vt.fields]

    # Resolve return type
    ret_type = method.returns or "None"
    python_return = _resolve_vt_python_type(ret_type, idl, for_self_class=python_class)
    if method.out_params:
        out_types = [_resolve_vt_python_type(op.param_type, idl, for_self_class=python_class) for op in method.out_params]
        python_return = f"tuple[{python_return}, {', '.join(out_types)}]"

    # Build parameter list
    params = []
    for p in method.params:
        py_type = _resolve_vt_python_type(p.param_type, idl, for_self_class=python_class)
        if p.nullable:
            py_type = f"{py_type} | None"
        params.append(
            {
                "name": p.name,
                "python_type": py_type,
                "nullable": p.nullable,
                "idl_type": p.param_type,
            }
        )

    c_struct = vt.name

    # Build enum TO_C map names
    enum_to_c_maps: dict[str, str] = {}
    for e in idl.enums:
        if e.facade_class:
            map_name = camel_to_upper_snake(e.facade_class)
            enum_to_c_maps[e.name] = f"{map_name}_TO_C"
    enum_to_c_maps["rounding_even"] = "ROUNDING_EVEN_TO_C"
    enum_to_c_maps["rounding_mode"] = "ROUNDING_MODE_TO_C"

    # Compute imports and pre-build C call args
    needed_c_structs: set[str] = {c_struct}
    needed_enum_maps: set[str] = set()
    setup_lines: list[str] = []
    c_call_args: list[str] = ["_c"]

    for p in method.params:
        if p.param_type.startswith("fdl_") and p.param_type in _py.TYPES:
            needed_c_structs.add(p.param_type)
            p_fields = _vt_field_names_for_type(p.param_type, idl)
            field_assigns = ", ".join(f"{fn}={p.name}.{fn}" for fn in p_fields)
            setup_lines.append(f"_c_{p.name} = {p.param_type}({field_assigns})")
            c_call_args.append(f"_c_{p.name}")
        elif p.param_type in enum_to_c_maps:
            map_name = enum_to_c_maps[p.param_type]
            needed_enum_maps.add(map_name)
            c_call_args.append(f"{map_name}[{p.name}]")
        elif p.param_type == "double" and p.nullable:
            # Nullable float: extract value and has_X flag into locals
            setup_lines.append(f"_{p.name}_val = float({p.name}) if {p.name} is not None else 0.0")
            setup_lines.append(f"_{p.name}_has = 1 if {p.name} is not None else 0")
            c_call_args.append(f"_{p.name}_val")
            c_call_args.append(f"_{p.name}_has")
        elif p.param_type == "double":
            c_call_args.append(f"float({p.name})")
        elif p.param_type in ("int", "int64_t"):
            c_call_args.append(f"int({p.name})")
        else:
            c_call_args.append(p.name)

    for op in method.out_params:
        if op.param_type.startswith("fdl_"):
            needed_c_structs.add(op.param_type)
        setup_lines.append(f"_out_{op.name} = {op.param_type}()")
        c_call_args.append(f"ctypes.byref(_out_{op.name})")

    # Build return expression
    return_expr = ""
    if ret_type == "bool":
        return_expr = f"return bool(get_lib().{method.c_function}({', '.join(c_call_args)}))"
    elif method.out_params:
        call = f"_r = get_lib().{method.c_function}({', '.join(c_call_args)})"
        # Build main return value
        main_ret_class = _resolve_vt_python_type(method.returns or "None", idl, for_self_class=python_class)
        ret_fields = _vt_field_names_for_type(method.returns or "", idl)
        main_ret = f"{main_ret_class}({', '.join(f'{fn}=_r.{fn}' for fn in ret_fields)})"
        # Build out param values
        out_rets = []
        for op in method.out_params:
            op_class = _resolve_vt_python_type(op.param_type, idl, for_self_class=python_class)
            op_fields = _vt_field_names_for_type(op.param_type, idl)
            out_rets.append(f"{op_class}({', '.join(f'{fn}=_out_{op.name}.{fn}' for fn in op_fields)})")
        return_expr = f"{call}\n        return {main_ret}, {', '.join(out_rets)}"
    else:
        call = f"_r = get_lib().{method.c_function}({', '.join(c_call_args)})"
        ret_class = python_return
        ret_fields = _vt_field_names_for_type(method.returns or "", idl)
        ret_construct = f"{ret_class}({', '.join(f'{fn}=_r.{fn}' for fn in ret_fields)})"
        return_expr = f"{call}\n        return {ret_construct}"

    return {
        "name": method.name,
        "c_function": method.c_function,
        "pure": method.pure,
        "kind": method.kind,
        "params": params,
        "python_return": python_return,
        "ret_type": ret_type,
        "c_struct": c_struct,
        "field_names": field_names,
        "needed_c_structs": sorted(needed_c_structs),
        "needed_enum_maps": sorted(needed_enum_maps),
        "has_out_params": bool(method.out_params),
        "python_class": python_class,
        "setup_lines": setup_lines,
        "return_expr": return_expr,
    }


def build_vt_operator_context(op: VTOperator, vt: ValueType, idl: IDL) -> dict:
    """Build template context for one value type operator."""
    python_class = vt.facade_class or vt.name
    field_names = [f.name for f in vt.fields]

    param_python_type = None
    if op.param_type:
        if op.param_type == "scalar_or_point":
            param_python_type = "PointFloat | float"
        else:
            param_python_type = _resolve_vt_python_type(op.param_type, idl, for_self_class=python_class)

    python_return = _resolve_vt_python_type(op.returns, idl, for_self_class=python_class)

    c_struct = vt.name
    needed_c_structs: set[str] = set()
    if op.c_function:
        needed_c_structs.add(c_struct)
        if op.param_type and op.param_type in _py.TYPES and op.param_type.startswith("fdl_"):
            needed_c_structs.add(op.param_type)

    return {
        "op": op.op,
        "c_function": op.c_function,
        "pure": op.pure,
        "param_type": op.param_type,
        "param_python_type": param_python_type,
        "python_return": python_return,
        "c_struct": c_struct,
        "field_names": field_names,
        "needed_c_structs": sorted(needed_c_structs),
        "python_class": python_class,
    }


def build_value_type_context(vt: ValueType, idl: IDL) -> dict:
    """Build template context for one value type class in _types.py."""
    python_class = vt.facade_class
    defaults_override = vt.facade_defaults or {}

    # Build lookup for enum facade classes from IDL
    enum_facade_map = {e.name: e.facade_class for e in idl.enums if e.facade_class}

    fields = []
    enum_imports: set[str] = set()
    has_float = False

    for f in vt.fields:
        c_type = f.c_type
        if c_type in _C_FIELD_TYPES:
            py_type, default, coerce = _C_FIELD_TYPES[c_type]
            if c_type == "double":
                has_float = True
        elif c_type in enum_facade_map:
            # Enum field — resolve facade class from IDL
            py_type = enum_facade_map[c_type]
            enum_imports.add(py_type)
            # Resolve default: IDL gives member name (e.g., "EVEN"), construct "RoundingEven.EVEN"
            if f.name in defaults_override:
                default = f"{py_type}.{defaults_override[f.name]}"
            else:
                default = "None"
            coerce = ""
        else:
            py_type = _py.TYPES.get(c_type, "object")
            default = "None"
            coerce = ""

        fields.append(
            {
                "name": f.name,
                "python_type": py_type,
                "default": default,
                "coerce": coerce,
            }
        )

    field_names = [f["name"] for f in fields]

    # Build init params string
    init_parts = []
    for f in fields:
        init_parts.append(f"{f['name']}: {f['python_type']} = {f['default']}")

    # Build equality expression parts (rendered by template)
    if has_float:
        eq_parts = []
        for f in fields:
            if f["python_type"] == "float":
                eq_parts.append(f"math.isclose(self.{f['name']}, other.{f['name']}, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL)")
            else:
                eq_parts.append(f"self.{f['name']} == other.{f['name']}")
    else:
        eq_parts = [f"self.{f['name']} == other.{f['name']}" for f in fields]

    # Build method and operator contexts
    method_contexts = [build_vt_method_context(m, vt, idl) for m in vt.methods]
    operator_contexts = [build_vt_operator_context(o, vt, idl) for o in vt.operators]

    # Resolve cross-type equality sibling (e.g. DimensionsInt ↔ DimensionsFloat)
    cross_eq_class = None
    if vt.cross_eq:
        for other_vt in idl.value_types:
            if other_vt.name == vt.cross_eq:
                cross_eq_class = other_vt.facade_class
                break

    return {
        "python_class": python_class,
        "c_type": vt.name,
        "doc": f"Lightweight {python_class} value type.",
        "fields": fields,
        "slot_names": ", ".join(f'"{fn}"' for fn in sorted(field_names)),
        "init_params": ", ".join(init_parts),
        "float_compare": has_float,
        "eq_parts": eq_parts,
        "cross_eq_class": cross_eq_class,
        "hash_fields": ", ".join(f"self.{fn}" for fn in field_names),
        "iter_fields": ", ".join(f"self.{fn}" for fn in field_names),
        "repr_format": python_class + "(" + ", ".join(f"{fn}={{self.{fn}!r}}" for fn in field_names) + ")",
        "enum_imports": sorted(enum_imports),
        "methods": method_contexts,
        "operators": operator_contexts,
    }


# -----------------------------------------------------------------------
# Converter context builder
# -----------------------------------------------------------------------


def build_converter_context(vt: ValueType, idl: IDL) -> dict:
    """Build template context for one value type's converter functions."""
    # Build enum metadata lookup
    enum_info: dict[str, dict] = {}
    for e in idl.enums:
        if e.facade_class:
            enum_info[e.name] = {
                "facade_class": e.facade_class,
                "map_name": camel_to_upper_snake(e.facade_class),
            }

    defaults_override = vt.facade_defaults or {}
    fields = []
    enum_from_c_imports: list[str] = []
    enum_to_c_imports: list[str] = []
    enum_class_imports: set[str] = set()

    for f in vt.fields:
        c_type = f.c_type
        if c_type in ("int64_t", "int", "uint32_t"):
            from_c_expr = f"int(c_struct.{f.name})"
            to_c_expr = f"int(val.{f.name})"
        elif c_type == "double":
            from_c_expr = f"c_struct.{f.name}"
            to_c_expr = f"float(val.{f.name})"
        elif c_type in enum_info:
            info = enum_info[c_type]
            from_c_name = f"{info['map_name']}_FROM_C"
            to_c_name = f"{info['map_name']}_TO_C"
            default_member = defaults_override.get(f.name, "")
            default_expr = f"{info['facade_class']}.{default_member}" if default_member else "None"
            from_c_expr = f"{from_c_name}.get(c_struct.{f.name}, {default_expr})"
            to_c_expr = f"{to_c_name}[val.{f.name}]"
            enum_from_c_imports.append(from_c_name)
            enum_to_c_imports.append(to_c_name)
            enum_class_imports.add(info["facade_class"])
        else:
            from_c_expr = f"c_struct.{f.name}"
            to_c_expr = f"val.{f.name}"

        fields.append(
            {
                "name": f.name,
                "from_c_expr": from_c_expr,
                "to_c_expr": to_c_expr,
            }
        )

    return {
        "converter": vt.facade_converter,
        "python_class": vt.facade_class,
        "c_struct": vt.name,
        "fields": fields,
        "enum_from_c_imports": sorted(enum_from_c_imports),
        "enum_to_c_imports": sorted(enum_to_c_imports),
        "enum_class_imports": sorted(enum_class_imports),
    }


# -----------------------------------------------------------------------
# Facade class context builders
# -----------------------------------------------------------------------


def build_builder_method_context(method, idl: IDL, enum_contexts: list[dict]) -> dict:
    """Build template context for a builder method."""
    # Enum TO_C map lookup
    type_key_to_to_c: dict[str, str] = {}
    for ectx in enum_contexts:
        type_key_to_to_c[ectx["idl_name"]] = f"{ectx['map_name']}_TO_C"

    # Build expand map from IDL value types (field names and coercion)
    expand_map: dict[str, list[dict]] = {}
    for vt in idl.value_types:
        if vt.facade_class:
            fields = []
            for f in vt.fields:
                coerce = "int" if f.c_type in ("int64_t", "int", "uint32_t") else "float" if f.c_type == "double" else None
                fields.append({"name": f.name, "coerce": coerce})
            expand_map[vt.name] = fields

    # Converter name lookup for non-expanded value types
    converter_lookup: dict[str, str] = {}
    for vt in idl.value_types:
        if vt.facade_converter:
            converter_lookup[vt.name] = vt.facade_converter

    params = []
    c_args: list[str] = []

    for p in method.params:
        python_type = _py.resolve_type(p.type_key, nullable=p.nullable)
        default = "None" if p.nullable and p.default is None else (_py.render_default(p.default) if p.default else None)
        params.append(
            {
                "name": p.name,
                "python_type": python_type,
                "default": default,
            }
        )

        if p.type_key == "string":
            if p.nullable:
                c_args.append(f'{p.name}.encode("utf-8") if {p.name} else None')
            else:
                c_args.append(f'{p.name}.encode("utf-8")')
        elif p.type_key == "double":
            c_args.append(f"float({p.name})")
        elif p.type_key in ("int", "int64_t", "uint32_t"):
            c_args.append(f"int({p.name})")
        elif p.expand and p.type_key in expand_map:
            for field_info in expand_map[p.type_key]:
                coerce = field_info["coerce"]
                if coerce:
                    c_args.append(f"{coerce}({p.name}.{field_info['name']})")
                else:
                    c_args.append(f"{p.name}.{field_info['name']}")
        elif p.type_key in converter_lookup:
            c_args.append(f"_to_c_{converter_lookup[p.type_key]}({p.name})")
        elif p.type_key in type_key_to_to_c:
            c_args.append(f"{type_key_to_to_c[p.type_key]}[{p.name}]")
        else:
            c_args.append(p.name)

    return {
        "name": method.name,
        "c_function": method.function,
        "returns": method.returns,
        "doc": method.doc,
        "params": params,
        "c_args": c_args,
        "error_pattern": method.error_handling.pattern if method.error_handling else None,
    }


def build_lifecycle_method_context(method, idl: IDL, enum_contexts: list[dict]) -> dict:
    """Build template context for a lifecycle method (static/class factory, instance, compound_setter, etc.)."""
    if method.kind == "alias":
        return {
            "name": method.name,
            "kind": "alias",
            "alias_of": method.alias_of,
            "doc": method.doc,
        }

    if method.kind in ("instance_getter", "instance_getter_optional"):
        # Look up facade class and converter for the return value type
        return_vt = method.returns
        facade_class = None
        converter_fn = None
        for vt in idl.value_types:
            if vt.name == return_vt:
                facade_class = vt.facade_class
                converter_fn = f"_{vt.facade_converter}"
                break
        ctx: dict = {
            "name": method.name,
            "kind": method.kind,
            "c_function": method.function,
            "returns": facade_class,
            "converter_fn": converter_fn,
            "doc": method.doc,
        }
        if method.kind == "instance_getter_optional":
            ctx["c_struct"] = return_vt
        return ctx

    if method.kind == "composite_property":
        return {
            "name": method.name,
            "kind": "composite_property",
            "returns": method.returns,
            "doc": method.doc,
            "compose_from": method.compose_from or {},
        }

    # Build converter lookup for value types
    converter_lookup: dict[str, str] = {}
    for vt in idl.value_types:
        if vt.facade_converter:
            converter_lookup[vt.name] = vt.facade_converter

    # Build enum TO_C map lookup
    enum_to_c_maps: dict[str, str] = {}
    for ec in enum_contexts:
        enum_to_c_maps[ec["idl_name"]] = f"{ec['map_name']}_TO_C"

    # Build params and c_args using same logic as builders
    params = []
    c_args: list[str] = []

    for p in method.params:
        if p.type_key == "handle" and p.source_class:
            python_type = p.source_class
        elif p.type_key in enum_to_c_maps:
            python_type = "str"
        else:
            python_type = _py.resolve_type(p.type_key, nullable=p.nullable)
        default = "None" if p.nullable and p.default is None else (_py.render_default(p.default) if p.default else None)
        param_ctx = {
            "name": p.name,
            "type_key": p.type_key,
            "python_type": python_type,
            "default": default,
        }
        if p.global_fallback:
            param_ctx["global_fallback"] = p.global_fallback
        params.append(param_ctx)

        if p.type_key == "handle":
            c_args.append(f"{p.name}._handle")
        elif p.type_key == "bytes":
            c_args.append(p.name)
            c_args.append(f"len({p.name})")
        elif p.type_key == "string":
            if p.nullable:
                c_args.append(f'{p.name}.encode("utf-8") if {p.name} else None')
            else:
                c_args.append(f'{p.name}.encode("utf-8")')
        elif p.type_key in ("int", "int64_t", "uint32_t"):
            if p.nullable:
                c_args.append(f"{p.name} or 0")
            else:
                c_args.append(p.name)
        elif p.type_key == "double":
            c_args.append(f"float({p.name})")
        elif p.type_key in enum_to_c_maps:
            c_args.append(f"{enum_to_c_maps[p.type_key]}[{p.name}]")
        elif p.type_key in converter_lookup:
            c_args.append(f"_to_c_{converter_lookup[p.type_key]}({p.name})")
        else:
            c_args.append(p.name)

    eh = method.error_handling
    error_ctx = None
    if eh:
        result_fields_ctx = None
        if eh.result_fields:
            result_fields_ctx = [
                {
                    "name": rf.name,
                    "source": rf.source,
                    "extract": rf.extract,
                    "wrap_class": rf.wrap_class,
                    "converter": rf.converter,
                    "scalar_type": rf.scalar_type,
                    "private": rf.private,
                }
                for rf in eh.result_fields
            ]
        error_ctx = {
            "pattern": eh.pattern,
            "error_field": eh.error_field,
            "success_field": eh.success_field,
            "error_class": _py.resolve_error_class(eh.error_class),
            "free_fn": eh.free_fn,
            "count_fn": eh.count_fn,
            "at_fn": eh.at_fn,
            "result_fields": result_fields_ctx,
        }

    ctx = {
        "name": method.name,
        "kind": method.kind,
        "c_function": method.function,
        "returns": method.returns,
        "doc": method.doc,
        "params": params,
        "c_args": c_args,
        "error": error_ctx,
    }
    if method.factory_kwargs:
        ctx["factory_kwargs"] = method.factory_kwargs
    return ctx


def build_init_context(ir_cls, idl: IDL, enum_contexts: list[dict], ir_class_by_name: dict) -> dict | None:
    """Build template context for kwargs __init__ on a facade class."""
    init = ir_cls.init
    if not init:
        return None

    # For depth 0 (root/OwnedHandle), the builder method is on the class itself
    if init.depth == 0:
        builder_ir_method = None
        for m in ir_cls.methods:
            if m.name == init.builder_method:
                builder_ir_method = m
                break
    else:
        # Find the builder method in the parent IR class
        parent_ir = ir_class_by_name.get(ir_cls.parent)
        if not parent_ir:
            return None
        builder_ir_method = None
        for m in parent_ir.methods:
            if m.name == init.builder_method:
                builder_ir_method = m
                break
    if not builder_ir_method:
        return None

    # Reuse existing builder context for C args
    builder_ctx = build_builder_method_context(builder_ir_method, idl, enum_contexts)

    # Build init param list for template
    init_params = []
    for p in init.params:
        if p.type_key == "ignore":
            init_params.append(
                {
                    "name": p.name,
                    "python_type": "object",
                    "default": "None",
                    "ignore": True,
                }
            )
        else:
            python_type = _py.resolve_type(p.type_key, nullable=p.nullable)
            default = _py.render_default(p.default) if p.default else None
            if p.nullable and default is None:
                default = "None"
            init_params.append(
                {
                    "name": p.name,
                    "python_type": python_type,
                    "default": default,
                    "ignore": False,
                }
            )

    # Value type zero defaults for compound setter args
    vt_zeros = {
        "fdl_point_f64_t": "PointFloat(x=0.0, y=0.0)",
        "fdl_dimensions_i64_t": "DimensionsInt(width=0, height=0)",
        "fdl_dimensions_f64_t": "DimensionsFloat(width=0.0, height=0.0)",
    }
    init_param_by_name = {p.name: p for p in init.params}

    # Build post-setter contexts
    post_setter_ctx = []
    for ps in init.post_setters:
        ctx = {
            "kind": ps.kind,
            "property": ps.property,
            "method": ps.method,
            "condition": ps.condition,
            "always": ps.always,
        }
        if ps.args:
            args = []
            for arg_name, param_name in ps.args.items():
                ip = init_param_by_name.get(param_name)
                default_expr = None
                if ip and ip.nullable:
                    default_expr = vt_zeros.get(ip.type_key)
                args.append({"name": arg_name, "param": param_name, "default": default_expr})
            ctx["args"] = args
        else:
            ctx["args"] = []
        post_setter_ctx.append(ctx)

    # Determine parent handle variable name
    parent_handle_map = {0: None, 1: "_doc_h", 2: "_ctx_h", 3: "_canvas_h"}
    parent_handle = parent_handle_map[init.depth]

    return {
        "depth": init.depth,
        "parent_handle": parent_handle,
        "builder_fn": builder_ctx["c_function"],
        "builder_c_args": builder_ctx["c_args"],
        "params": init_params,
        "post_setters": post_setter_ctx,
    }


def build_facade_class_context(ir_cls, idl: IDL, enum_contexts: list[dict], ir_class_by_name: dict | None = None) -> dict:
    """Build template context for one facade class."""
    # Map IDL enum type_key → FROM_C / TO_C lookup table names
    type_key_to_from_c: dict[str, str] = {}
    type_key_to_to_c: dict[str, str] = {}
    for ectx in enum_contexts:
        type_key_to_from_c[ectx["idl_name"]] = f"{ectx['map_name']}_FROM_C"
        type_key_to_to_c[ectx["idl_name"]] = f"{ectx['map_name']}_TO_C"

    properties = []
    for prop in ir_cls.properties:
        # For handle_ref properties, resolve the target class name as the Python type
        if prop.type_key == "handle_ref" and prop.handle_class:
            python_type = prop.handle_class
            if prop.nullable:
                python_type = f"{python_type} | None"
        else:
            python_type = _py.resolve_type(prop.type_key, nullable=prop.nullable)
        converter = _py.resolve_converter(prop.type_key)

        # For enum converters, resolve the FROM_C / TO_C map names
        enum_from_c = type_key_to_from_c.get(prop.type_key, "")
        enum_to_c = type_key_to_to_c.get(prop.type_key, "")

        prop_ctx: dict = {
            "name": prop.name,
            "type_key": prop.type_key,
            "python_type": python_type,
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
            prop_ctx["handle_class"] = prop.handle_class
            prop_ctx["handle_class_module"] = _class_to_module(prop.handle_class)
        properties.append(prop_ctx)

    collections = []
    for coll in ir_cls.collections:
        collections.append(
            {
                "name": coll.name,
                "item_class": coll.item_class,
                "count_fn": coll.count_fn,
                "at_fn": coll.at_fn,
                "find_by_id_fn": coll.find_by_id_fn,
                "find_by_label_fn": coll.find_by_label_fn,
                "add_fn": coll.add_fn,
            }
        )

    # Find the to_json method if it exists
    to_json_fn = None
    for method in ir_cls.methods:
        if method.name == "to_json":
            to_json_fn = method.function
            break

    # Build builder method contexts
    builders = []
    for method in ir_cls.methods:
        if method.kind == "builder":
            builders.append(build_builder_method_context(method, idl, enum_contexts))

    # Build lifecycle method contexts
    lifecycle = []
    for method in ir_cls.methods:
        if method.kind in (
            "static_factory",
            "class_factory",
            "alias",
            "compound_setter",
            "composite_property",
            "instance_getter",
            "instance_getter_optional",
            "validate_json",
        ) or (method.kind == "instance" and method.name != "to_json" and (method.params or method.error_handling)):
            ctx = build_lifecycle_method_context(method, idl, enum_contexts)
            lifecycle.append(ctx)

    # Build init context if class has kwargs init
    init_ctx = None
    if ir_cls.init and ir_class_by_name:
        init_ctx = build_init_context(ir_cls, idl, enum_contexts, ir_class_by_name)

    # Custom attributes context
    custom_attrs = ir_cls.custom_attrs
    ca_prefix = ir_cls.handle_type.removesuffix("t") if custom_attrs else None

    return {
        "name": ir_cls.name,
        "handle_type": ir_cls.handle_type,
        "owns_handle": ir_cls.owns_handle,
        "identity_attr": ir_cls.identity_attr,
        "custom_attrs": custom_attrs,
        "ca_prefix": ca_prefix,
        "properties": properties,
        "collections": collections,
        "to_json_fn": to_json_fn,
        "builders": builders,
        "lifecycle": lifecycle,
        "init": init_ctx,
    }


# -----------------------------------------------------------------------
# Free function context builder
# -----------------------------------------------------------------------


def build_free_function_context(ff: FreeFunctionDef, idl: IDL) -> dict:
    """Build template context for a free function exported from fdl_core."""
    # Build enum TO_C map names
    enum_to_c_maps: dict[str, str] = {}
    for e in idl.enums:
        if e.facade_class:
            map_name = camel_to_upper_snake(e.facade_class)
            enum_to_c_maps[e.name] = f"{map_name}_TO_C"
    enum_to_c_maps["rounding_even"] = "ROUNDING_EVEN_TO_C"
    enum_to_c_maps["rounding_mode"] = "ROUNDING_MODE_TO_C"
    enum_to_c_maps["fit_method"] = "FIT_METHOD_TO_C"

    params = []
    c_call_args: list[str] = []
    setup_lines: list[str] = []
    needed_c_structs: set[str] = set()
    needed_enum_maps: set[str] = set()

    for p in ff.params:
        py_type = _resolve_vt_python_type(p.param_type, idl)
        params.append({"name": p.name, "python_type": py_type})

        if p.param_type.startswith("fdl_") and p.param_type in _py.TYPES:
            needed_c_structs.add(p.param_type)
            p_fields = _vt_field_names_for_type(p.param_type, idl)
            field_assigns = ", ".join(f"{fn}={p.name}.{fn}" for fn in p_fields)
            setup_lines.append(f"_c_{p.name} = {p.param_type}({field_assigns})")
            c_call_args.append(f"_c_{p.name}")
        elif p.param_type in enum_to_c_maps:
            map_name = enum_to_c_maps[p.param_type]
            needed_enum_maps.add(map_name)
            c_call_args.append(f"{map_name}[{p.name}]")
        elif p.param_type in ("f64", "double", "float"):
            c_call_args.append(f"float({p.name})")
        elif p.param_type in ("int", "int64_t"):
            c_call_args.append(f"int({p.name})")
        else:
            c_call_args.append(p.name)

    python_return = _resolve_vt_python_type(ff.returns, idl)

    return {
        "display_name": ff.display_name,
        "c_function": ff.c_function,
        "doc": ff.doc,
        "params": params,
        "python_return": python_return,
        "c_call_args": c_call_args,
        "setup_lines": setup_lines,
        "needed_c_structs": sorted(needed_c_structs),
        "needed_enum_maps": sorted(needed_enum_maps),
    }
