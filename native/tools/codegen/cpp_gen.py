# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
C++ code generator: produces a single-file RAII header (fdl.hpp) from the IDL.

Consumes the language-neutral IR and CppAdapter to produce C++ idioms:
RAII ownership, move semantics, std::optional, forward declarations,
and inline implementations at file bottom for cross-class references.
"""

from __future__ import annotations

from pathlib import Path

from .adapters import CppAdapter
from .fdl_idl import IDL, ValueType, VTMethod, VTOperator, build_ir
from .shared_context import is_lifecycle_method, make_jinja_env

_cpp = CppAdapter()

# -----------------------------------------------------------------------
# C++ naming helpers
# -----------------------------------------------------------------------


def _cpp_class_name(ir_name: str) -> str:
    """FDL stays FDL, others get Ref suffix."""
    return "FDL" if ir_name == "FDL" else f"{ir_name}Ref"


_HANDLE_FIELD_MAP = {
    "fdl_doc_t": "doc_",
    "fdl_context_t": "ctx_",
    "fdl_canvas_t": "canvas_",
    "fdl_framing_decision_t": "fd_",
    "fdl_framing_intent_t": "fi_",
    "fdl_canvas_template_t": "ct_",
    "fdl_clip_id_t": "cid_",
    "fdl_file_sequence_t": "seq_",
}


def _handle_field(handle_type: str) -> str:
    return _HANDLE_FIELD_MAP.get(handle_type, "handle_")


# Special cases for naive singularization
_SINGULAR_MAP = {"canvases": "canvas"}


def _singular(name: str) -> str:
    """Singularize a collection name (contexts→context, canvases→canvas)."""
    if name in _SINGULAR_MAP:
        return _SINGULAR_MAP[name]
    return name[:-1] if name.endswith("s") else name


# -----------------------------------------------------------------------
# Type resolution: IR type_key → C++ declaration
# -----------------------------------------------------------------------

# Types that should be passed by const ref
_CONST_REF_TYPES = {"std::string", "fdl_dimensions_i64_t", "fdl_dimensions_f64_t", "fdl_point_f64_t", "fdl_round_strategy_t"}

# All facade class names
_ALL_CLASSES = {"FDL", "Context", "Canvas", "FramingDecision", "FramingIntent", "CanvasTemplate", "ClipID", "FileSequence"}

# Auxiliary dataclass field type → C++ type (for YAML-defined dataclass fields)
_DC_FIELD_CPP: dict[str, str] = {
    "str": "std::string",
    "float": "double",
}


def _cpp_param(name: str, type_key: str, default=None, *, nullable: bool = False, source_class: str | None = None) -> dict:
    """Build a C++ parameter dict from IR type information.

    Parameters
    ----------
    name : str
        Parameter name.
    type_key : str
        IR type key (e.g. "string", "fdl_halign_t").
    default : DefaultDescriptor | None
        Structured default from IR.
    nullable : bool
        Whether the parameter is nullable.
    source_class : str | None
        For handle params: the facade class name (e.g. "FramingIntent").
    """
    if source_class:
        cpp_type = _cpp_class_name(source_class)
    else:
        cpp_type = _cpp.resolve_type(type_key)
    is_ref = cpp_type in _CONST_REF_TYPES or cpp_type.endswith("Ref")
    pass_decl = f"const {cpp_type}&" if is_ref else cpp_type
    cpp_default = None
    if default is not None:
        cpp_default = _cpp.render_default(default)
        # Don't apply string-typed defaults (like '""') to non-string C++ types
        if cpp_default == '""' and cpp_type != "std::string":
            cpp_default = None
    elif nullable and cpp_type == "std::string":
        cpp_default = '""'
    bare = f"{pass_decl} {name}"
    return {
        "name": name,
        "decl": bare + (f" = {cpp_default}" if cpp_default else ""),
        "impl_decl": bare,  # without default — for out-of-line definitions
    }


def _cpp_call_arg(
    name: str, type_key: str, *, expand_vt: bool = True, nullable: bool = False, source_class: str | None = None
) -> list[str]:
    """Build C ABI call argument(s) for a parameter from IR type information.

    Value types with expand_vt=True get their fields expanded (e.g. dims.width, dims.height).
    Returns a list because some types expand to multiple args.
    """
    if source_class:
        return [f"{name}.get()"]
    if type_key == "string":
        if nullable:
            return [f"{name}.empty() ? nullptr : {name}.c_str()"]
        return [f"{name}.c_str()"]
    if expand_vt:
        if type_key in ("fdl_dimensions_i64_t", "fdl_dimensions_f64_t"):
            return [f"{name}.width", f"{name}.height"]
        if type_key == "fdl_point_f64_t":
            return [f"{name}.x", f"{name}.y"]
    return [name]


# -----------------------------------------------------------------------
# Value type wrapper classes (DimensionsInt, DimensionsFloat, PointFloat)
# -----------------------------------------------------------------------

# C struct name → C++ wrapper class name
_VT_CLASS_MAP: dict[str, str] = {
    "fdl_dimensions_i64_t": "DimensionsInt",
    "fdl_dimensions_f64_t": "DimensionsFloat",
    "fdl_point_f64_t": "PointFloat",
    "fdl_rect_t": "Rect",
}

# IDL param/return type → C++ type for VT methods
_VT_TYPE_MAP: dict[str, str] = {
    "double": "double",
    "f64": "double",
    "int": "int",
    "int64_t": "int64_t",
    "bool": "bool",
    "string": "std::string",
    "rounding_even": "fdl_rounding_even_t",
    "rounding_mode": "fdl_rounding_mode_t",
    "fit_method": "fdl_fit_method_t",
}

# C field type → C++ accessor return type
_C_FIELD_CPP: dict[str, str] = {
    "int64_t": "int64_t",
    "double": "double",
    "uint32_t": "uint32_t",
}

# IDL operator name → C++ operator symbol
_OP_MAP: dict[str, str] = {
    "__add__": "+",
    "__iadd__": "+=",
    "__sub__": "-",
    "__mul__": "*",
    "__lt__": "<",
    "__gt__": ">",
}

# Pure methods to skip in C++ (C++ has better native alternatives)
_SKIP_PURE_METHODS = {"duplicate", "from_dimensions"}


def _resolve_vt_type(idl_type: str, self_class: str) -> str:
    """Resolve an IDL type to a C++ type for value type methods."""
    if idl_type == "self":
        return self_class
    if idl_type in _VT_CLASS_MAP:
        return _VT_CLASS_MAP[idl_type]
    return _VT_TYPE_MAP.get(idl_type, idl_type)


def _vt_type_is_wrapper(cpp_type: str) -> bool:
    """Check if a C++ type is a VT wrapper class."""
    return cpp_type in _VT_CLASS_MAP.values()


def _build_vt_method(method: VTMethod, vt: ValueType, self_class: str, vt_defined: set[str]) -> dict | None:
    """Build C++ method context for a value type method.

    Returns None if the method should be skipped.
    vt_defined: set of VT wrapper class names already fully defined.
    """
    if method.pure and method.name in _SKIP_PURE_METHODS:
        return None

    ret_cpp = _resolve_vt_type(method.returns or "void", self_class)

    # Check if any referenced type needs deferred implementation
    needs_defer = False
    if _vt_type_is_wrapper(ret_cpp) and ret_cpp not in vt_defined and ret_cpp != self_class:
        needs_defer = True
    for op in method.out_params:
        op_cpp = _resolve_vt_type(op.param_type, self_class)
        if _vt_type_is_wrapper(op_cpp) and op_cpp not in vt_defined and op_cpp != self_class:
            needs_defer = True

    # Build return type (handle out_params → std::pair)
    if method.out_params:
        out_types = [_resolve_vt_type(op.param_type, self_class) for op in method.out_params]
        return_type = f"std::pair<{ret_cpp}, {', '.join(out_types)}>"
    else:
        return_type = ret_cpp

    # Build parameters
    # Nullable params expand to (value, has_flag) in C ABI — values come first,
    # then flags, matching the C function signature order.
    params = []
    c_args = ["data_"]
    c_flag_args: list[str] = []
    for p in method.params:
        p_cpp = _resolve_vt_type(p.param_type, self_class)
        if p.nullable and p.param_type == "double":
            params.append(f"std::optional<double> {p.name} = std::nullopt")
            c_args.append(f"{p.name}.value_or(0.0)")
            c_flag_args.append(f"{p.name}.has_value() ? 1 : 0")
        elif _vt_type_is_wrapper(p_cpp):
            params.append(f"const {p_cpp}& {p.name}")
            c_args.append(f"static_cast<{vt.name}>({p.name})" if p_cpp != self_class else p.name)
        elif p_cpp in _CONST_REF_TYPES:
            params.append(f"const {p_cpp}& {p.name}")
            c_args.append(p.name)
        else:
            params.append(f"{p_cpp} {p.name}")
            c_args.append(p.name)
    c_args.extend(c_flag_args)

    param_list = ", ".join(params)
    is_const = method.name != "scale_by"  # scale_by mutates

    # Build body
    if method.pure:
        body = _build_pure_method_body(method, vt, self_class)
    elif method.out_params:
        body = _build_out_param_body(method, ret_cpp, self_class, c_args)
    elif ret_cpp == "bool":
        body = f"return ::{method.c_function}({', '.join(c_args)}) != 0;"
    elif ret_cpp == "void":
        body = f"::{method.c_function}({', '.join(c_args)});"
    elif _vt_type_is_wrapper(ret_cpp):
        body = f"return {ret_cpp}(::{method.c_function}({', '.join(c_args)}));"
    else:
        body = f"return ::{method.c_function}({', '.join(c_args)});"

    return {
        "name": method.name,
        "return_type": return_type,
        "param_list": param_list,
        "body": body,
        "is_const": is_const,
        "deferred": needs_defer,
    }


def _build_pure_method_body(method: VTMethod, vt: ValueType, self_class: str) -> str:
    """Build inline C++ body for a pure method."""
    field_names = [f.name for f in vt.fields]

    if method.name == "format":
        parts = ' << "x" << '.join(f"data_.{fn}" for fn in field_names)
        return f"std::ostringstream ss; ss << {parts}; return ss.str();"

    if method.name == "to_int":
        assigns = ", ".join(f"static_cast<int64_t>(data_.{fn})" for fn in field_names)
        return f"return DimensionsInt({assigns});"

    if method.name == "scale_by":
        lines = " ".join(f"data_.{fn} *= factor;" for fn in field_names)
        return lines

    return ""


def _build_out_param_body(method: VTMethod, ret_cpp: str, self_class: str, c_args: list[str]) -> str:
    """Build body for a method with out params (e.g. clamp_to_dims)."""
    lines = []
    for op in method.out_params:
        c_struct = op.param_type
        lines.append(f"{c_struct} _out_{op.name};")
    out_refs = ", ".join(f"&_out_{op.name}" for op in method.out_params)
    c_args_with_out = ", ".join([*c_args, out_refs])
    lines.append(f"auto _r = ::{method.c_function}({c_args_with_out});")
    ret_parts = [f"{ret_cpp}(_r)"]
    for op in method.out_params:
        op_cpp = _resolve_vt_type(op.param_type, self_class)
        ret_parts.append(f"{op_cpp}(_out_{op.name})")
    lines.append(f"return {{{', '.join(ret_parts)}}};")
    return " ".join(lines)


def _build_vt_operator(op: VTOperator, vt: ValueType, self_class: str) -> list[dict]:
    """Build C++ operator context(s) for a value type operator. Returns list (may be >1 for scalar_or_point)."""
    if op.op == "__bool__":
        # Delegate to is_zero() which calls the C ABI — keeps logic in one place
        return [
            {
                "kind": "explicit_bool",
                "body": "return !is_zero();",
            }
        ]

    if op.op == "__iadd__":
        field_names = [f.name for f in vt.fields]
        assigns = " ".join(f"data_.{fn} += other.data_.{fn};" for fn in field_names)
        return [
            {
                "kind": "iadd",
                "param_decl": f"const {self_class}& other",
                "body": f"{assigns} return *this;",
            }
        ]

    cpp_op = _OP_MAP.get(op.op)
    if not cpp_op:
        return []

    ret_cpp = _resolve_vt_type(op.returns, self_class)

    if op.param_type == "scalar_or_point":
        # Two overloads: scalar and element-wise
        field_names = [f.name for f in vt.fields]
        ewise = ", ".join(f"data_.{fn} * other.data_.{fn}" for fn in field_names)
        return [
            {
                "kind": "binary",
                "op_symbol": cpp_op,
                "return_type": ret_cpp,
                "param_decl": "double scalar",
                "body": f"return {ret_cpp}(::{op.c_function}(data_, scalar));",
            },
            {
                "kind": "binary",
                "op_symbol": cpp_op,
                "return_type": ret_cpp,
                "param_decl": f"const {self_class}& other",
                "body": f"return {ret_cpp}({ewise});",
            },
        ]

    if ret_cpp == "bool":
        return [
            {
                "kind": "binary",
                "op_symbol": cpp_op,
                "return_type": "bool",
                "param_decl": f"const {self_class}& other",
                "body": f"return ::{op.c_function}(data_, other.data_) != 0;",
            }
        ]

    return [
        {
            "kind": "binary",
            "op_symbol": cpp_op,
            "return_type": ret_cpp,
            "param_decl": f"const {self_class}& other",
            "body": f"return {ret_cpp}(::{op.c_function}(data_, other.data_));",
        }
    ]


def _build_vt_class(vt: ValueType, vt_defined: set[str]) -> dict | None:
    """Build C++ value type wrapper class context."""
    if not vt.facade_class or vt.name not in _VT_CLASS_MAP:
        return None

    self_class = _VT_CLASS_MAP[vt.name]
    c_struct = vt.name

    # Fields with C++ types
    fields = []
    constructor_params = []
    constructor_init = []
    for f in vt.fields:
        cpp_type = _C_FIELD_CPP.get(f.c_type, f.c_type)
        fields.append({"name": f.name, "cpp_type": cpp_type})
        constructor_params.append(f"{cpp_type} {f.name}")
        constructor_init.append(f.name)

    # Methods
    inline_methods = []
    deferred_methods = []
    for m in vt.methods:
        ctx = _build_vt_method(m, vt, self_class, vt_defined)
        if ctx is None:
            continue
        if ctx["deferred"]:
            deferred_methods.append(ctx)
        else:
            inline_methods.append(ctx)

    # Operators
    operators = []
    for op in vt.operators:
        operators.extend(_build_vt_operator(op, vt, self_class))

    # Equality — delegate to C ABI for FP-tolerant types, inline for exact integer
    _EQUALITY_FN = {
        "fdl_dimensions_f64_t": "::fdl_dimensions_equal(data_, other.data_) != 0",
        "fdl_point_f64_t": "::fdl_point_equal(data_, other.data_) != 0",
    }
    equality_body = _EQUALITY_FN.get(c_struct)
    if equality_body is None and fields:
        # Integer types: inline exact comparison
        equality_body = " && ".join(f"data_.{f['name']} == other.data_.{f['name']}" for f in fields)

    # Cross-type equality (e.g. DimensionsInt == DimensionsFloat)
    # Uses raw() public accessor to avoid private member access across types
    _CROSS_EQ_FN = {
        "fdl_dimensions_i64_t": "::fdl_dimensions_equal(fdl_dimensions_f64_t{(double)data_.width, (double)data_.height}, other.raw()) != 0",
        "fdl_dimensions_f64_t": (
            "::fdl_dimensions_equal(data_, fdl_dimensions_f64_t{(double)other.raw().width, (double)other.raw().height}) != 0"
        ),
    }
    cross_eq_class = None
    cross_eq_body = None
    if vt.cross_eq and vt.cross_eq in _VT_CLASS_MAP:
        cross_eq_class = _VT_CLASS_MAP[vt.cross_eq]
        cross_eq_body = _CROSS_EQ_FN.get(c_struct)

    result = {
        "cpp_class": self_class,
        "c_struct": c_struct,
        "fields": fields,
        "constructor_params": ", ".join(constructor_params),
        "constructor_init": ", ".join(constructor_init),
        "inline_methods": inline_methods,
        "deferred_methods": deferred_methods,
        "operators": operators,
        "equality_body": equality_body,
        "cross_eq_class": cross_eq_class,
        "cross_eq_body": cross_eq_body,
    }

    # Mark this class as defined for subsequent classes
    vt_defined.add(self_class)
    return result


# -----------------------------------------------------------------------
# Free functions (fdl::round, fdl::calculate_scale_factor)
# -----------------------------------------------------------------------


def _build_free_function(ff, idl: IDL) -> dict:
    """Build C++ free function context from IDL FreeFunctionDef."""
    params = []
    c_args = []

    for p in ff.params:
        cpp_type = _VT_TYPE_MAP.get(p.param_type)
        if cpp_type is None and p.param_type in _VT_CLASS_MAP:
            cpp_type = _VT_CLASS_MAP[p.param_type]
        if cpp_type is None:
            cpp_type = p.param_type

        if _vt_type_is_wrapper(cpp_type):
            params.append(f"const {cpp_type}& {p.name}")
            c_args.append(p.name)  # implicit conversion to C struct
        elif cpp_type in _CONST_REF_TYPES:
            params.append(f"const {cpp_type}& {p.name}")
            c_args.append(p.name)
        else:
            params.append(f"{cpp_type} {p.name}")
            c_args.append(p.name)

    ret_type = _VT_TYPE_MAP.get(ff.returns, ff.returns)
    if ff.returns in ("int",):
        ret_type = "int64_t"
    elif ff.returns in ("float",):
        ret_type = "double"

    # Strip "fdl_" prefix for nicer C++ name: fdl_round → round
    cpp_name = ff.display_name
    if cpp_name.startswith("fdl_"):
        cpp_name = cpp_name[4:]

    return {
        "cpp_name": cpp_name,
        "c_function": ff.c_function,
        "return_type": ret_type,
        "param_list": ", ".join(params),
        "c_args": ", ".join(c_args),
        "doc": ff.doc,
    }


# -----------------------------------------------------------------------
# Supporting structs (ClipID, FileSequence, Version)
# -----------------------------------------------------------------------

# JSON wrapper field type → C++ type
_JW_FIELD_CPP: dict[str, str] = {
    "str": "std::string",
    "int": "int64_t",
}


def _build_auxiliary_structs(idl: IDL) -> dict:
    """Build C++ contexts for auxiliary types: json_wrappers and version."""
    json_wrappers = []
    for jw in idl.auxiliary_types.json_wrappers:
        fields = []
        for f in jw.fields:
            cpp_type = _JW_FIELD_CPP.get(f.field_type, f.field_type)
            # Check if it's another wrapper type (e.g. FileSequence)
            is_nested = f.field_type not in _JW_FIELD_CPP
            if f.nullable:
                fields.append(
                    {
                        "name": f.name,
                        "cpp_type": f"std::optional<{cpp_type}>" if not is_nested else f"std::optional<{f.field_type}>",
                        "nullable": True,
                        "c_has_flag": f.c_has_flag,
                        "is_nested": is_nested,
                        "base_type": cpp_type if not is_nested else f.field_type,
                    }
                )
            else:
                fields.append(
                    {
                        "name": f.name,
                        "cpp_type": cpp_type,
                        "nullable": False,
                        "c_has_flag": None,
                        "is_nested": False,
                        "base_type": cpp_type,
                    }
                )
        json_wrappers.append(
            {
                "class_name": jw.class_name,
                "c_struct": jw.c_struct,
                "free_fn": jw.free_fn,
                "fields": fields,
            }
        )

    version = None
    if idl.auxiliary_types.version:
        v = idl.auxiliary_types.version
        version = {
            "class_name": v.class_name,
            "fields": [{"name": s.name, "cpp_type": "int"} for s in v.slots],
        }

    return {
        "json_wrappers": json_wrappers,
        "version": version,
    }


# -----------------------------------------------------------------------
# Property context builder
# -----------------------------------------------------------------------


def _build_prop(prop, handle_field: str) -> dict | None:
    """Build C++ property context from an IRProperty. Returns None to skip."""
    # Skip json_value properties (no equivalent in C++)
    if prop.type_key == "json_value":
        return None

    # Handle-ref properties: wrap child handle as a Ref class
    if prop.type_key == "handle_ref" and prop.handle_class:
        ref_class = _cpp_class_name(prop.handle_class)
        ctx: dict = {
            "name": prop.name,
            "kind": "handle_ref",
            "ref_class": ref_class,
            "getter_fn": prop.getter_fn,
            "setter_fn": prop.setter_fn,
            "remover_fn": prop.remover_fn,
            "has_fn": prop.has_fn,
            "handle_field": handle_field,
            "nullable": prop.nullable,
        }
        return ctx

    type_key = prop.type_key
    nullable = prop.nullable

    # Determine C++ getter return type and body
    # Nullable properties with has_fn must be checked first (including nullable strings)
    if nullable and prop.has_fn and type_key == "string":
        cpp_return_type = "std::optional<std::string>"
        getter_body = (
            f"if (!{prop.has_fn}({handle_field})) return std::nullopt;\n"
            f"        const char* p = {prop.getter_fn}({handle_field});\n"
            f"        return p ? std::optional<std::string>(p) : std::nullopt;"
        )
    elif nullable and prop.has_fn:
        base_type = _cpp.resolve_type(type_key)
        cpp_return_type = f"std::optional<{base_type}>"
        getter_body = f"if (!{prop.has_fn}({handle_field})) return std::nullopt;\n        return {prop.getter_fn}({handle_field});"
    elif type_key == "string":
        cpp_return_type = "std::string"
        getter_body = f"const char* p = {prop.getter_fn}({handle_field});\n        return p ? std::string(p) : std::string();"
    elif type_key == "bool":
        cpp_return_type = "bool"
        getter_body = f"return {prop.getter_fn}({handle_field}) != 0;"
    else:
        cpp_return_type = _cpp.resolve_type(type_key)
        getter_body = f"return {prop.getter_fn}({handle_field});"

    # Setter
    setter = None
    if prop.setter_fn:
        if type_key == "string":
            setter_type = "const std::string&"
            setter_body = f"{prop.setter_fn}({handle_field}, value.c_str());"
        elif type_key == "bool":
            setter_type = "bool"
            setter_body = f"{prop.setter_fn}({handle_field}, value ? 1 : 0);"
        elif type_key == "double":
            setter_type = "double"
            setter_body = f"{prop.setter_fn}({handle_field}, value);"
        else:
            base = _cpp.resolve_type(type_key)
            setter_type = base
            setter_body = f"{prop.setter_fn}({handle_field}, value);"

        setter = {
            "type": setter_type,
            "body": setter_body,
        }

    has_fn_ctx = None
    if nullable and prop.has_fn:
        has_fn_ctx = {"name": f"has_{prop.name}", "body": f"return {prop.has_fn}({handle_field}) != 0;"}

    # Remover for nullable properties (e.g. remove_effective, remove_protection)
    remover_ctx = None
    if nullable and prop.remover_fn:
        remover_name = f"remove_{prop.name}"
        remover_ctx = {"name": remover_name, "body": f"{prop.remover_fn}({handle_field});"}

    return {
        "name": prop.name,
        "return_type": cpp_return_type,
        "getter_body": getter_body,
        "setter": setter,
        "has_fn": has_fn_ctx,
        "remover": remover_ctx,
    }


# -----------------------------------------------------------------------
# Builder context for C++
# -----------------------------------------------------------------------


def _build_builder(method, handle_field: str) -> dict:
    """Build C++ builder method context from an IRMethod."""
    params = []
    c_args = [handle_field]

    for p in method.params:
        params.append(_cpp_param(p.name, p.type_key, p.default, nullable=p.nullable, source_class=p.source_class))
        c_args.extend(_cpp_call_arg(p.name, p.type_key, expand_vt=p.expand, nullable=p.nullable, source_class=p.source_class))

    returns = _cpp_class_name(method.returns)
    return {
        "name": method.name,
        "c_function": method.function,
        "returns": returns,
        "doc": method.doc,
        "params": params,
        "c_args": c_args,
    }


# -----------------------------------------------------------------------
# Lifecycle method context for C++
# -----------------------------------------------------------------------


def _build_error_ctx(eh) -> dict:
    """Build error context dict from an IRErrorHandling for the C++ template."""
    result_fields = None
    if eh.result_fields:
        result_fields = [
            {
                "name": rf.name,
                "source": rf.source,
                "extract": rf.extract,
                "wrap_class": _cpp_class_name(rf.wrap_class) if rf.wrap_class else None,
                "converter": rf.converter,
                "scalar_type": rf.scalar_type,
                "private": rf.private,
            }
            for rf in eh.result_fields
        ]
    return {
        "pattern": eh.pattern,
        "error_field": eh.error_field,
        "success_field": eh.success_field,
        "error_class": _cpp.resolve_error_class(eh.error_class) if eh.error_class else None,
        "free_fn": eh.free_fn,
        "count_fn": eh.count_fn,
        "at_fn": eh.at_fn,
        "result_fields": result_fields,
    }


def _lifecycle_composite_property(method, handle_field: str) -> dict:
    """Build context for a composite property (e.g. effective_dimensions)."""
    return {
        "kind": "composite_property",
        "name": method.name,
        "returns": method.returns,
        "doc": method.doc,
        "compose_from": method.compose_from or {},
    }


def _lifecycle_class_factory(method, handle_field: str) -> dict:
    """Build context for a class factory (e.g. populate_from_intent)."""
    params = []
    c_args = [handle_field]
    for p in method.params:
        params.append(_cpp_param(p.name, p.type_key, p.default, nullable=p.nullable, source_class=p.source_class))
        c_args.extend(_cpp_call_arg(p.name, p.type_key, expand_vt=False, nullable=p.nullable, source_class=p.source_class))
    return {
        "kind": "populate",
        "name": method.name,
        "c_function": method.function,
        "doc": method.doc,
        "params": params,
        "c_args": c_args,
    }


def _lifecycle_static_factory(method, handle_field: str) -> dict | None:
    """Build context for a static factory (parse or create)."""
    eh = method.error_handling
    if not eh:
        return None
    if eh.pattern == "result_struct":
        return {
            "kind": "parse",
            "name": method.name,
            "c_function": method.function,
            "doc": method.doc,
            "error": _build_error_ctx(eh),
        }
    if eh.pattern == "null_check":
        params = []
        c_args = []
        for p in method.params:
            params.append(_cpp_param(p.name, p.type_key, p.default, nullable=p.nullable, source_class=p.source_class))
            c_args.extend(_cpp_call_arg(p.name, p.type_key, expand_vt=False, nullable=p.nullable, source_class=p.source_class))
        return {
            "kind": "create",
            "name": method.name,
            "c_function": method.function,
            "doc": method.doc,
            "params": params,
            "c_args": c_args,
        }
    return None


def _lifecycle_instance(method, handle_field: str) -> dict | None:
    """Build context for an instance method (validate, as_json, or apply)."""
    eh = method.error_handling
    if eh and eh.pattern == "validation":
        return {
            "kind": "validate",
            "name": method.name,
            "c_function": method.function,
            "doc": method.doc,
            "error": _build_error_ctx(eh),
            "handle_field": handle_field,
        }
    if method.returns == "string_free":
        return {
            "kind": "as_json",
            "name": method.name,
            "c_function": method.function,
            "doc": method.doc,
            "handle_field": handle_field,
        }
    if eh and eh.pattern == "result_struct_multi":
        params = []
        c_args = [handle_field]
        for p in method.params:
            params.append(_cpp_param(p.name, p.type_key, p.default, nullable=p.nullable, source_class=p.source_class))
            c_args.extend(_cpp_call_arg(p.name, p.type_key, expand_vt=False, nullable=p.nullable, source_class=p.source_class))
        return {
            "kind": "apply",
            "name": method.name,
            "c_function": method.function,
            "returns": method.returns,
            "doc": method.doc,
            "params": params,
            "c_args": c_args,
            "error": _build_error_ctx(eh),
            "handle_field": handle_field,
        }
    return None


def _lifecycle_compound_setter(method, handle_field: str) -> dict:
    """Build context for a compound setter (e.g. set_dimensions)."""
    params = []
    c_args = [handle_field]
    for p in method.params:
        params.append(_cpp_param(p.name, p.type_key, nullable=p.nullable, source_class=p.source_class))
        c_args.extend(_cpp_call_arg(p.name, p.type_key, expand_vt=False, nullable=p.nullable, source_class=p.source_class))
    return {
        "kind": "compound_setter",
        "name": method.name,
        "c_function": method.function,
        "doc": method.doc,
        "params": params,
        "c_args": c_args,
    }


def _lifecycle_instance_getter(method, handle_field: str) -> dict:
    """Build context for an instance getter returning a value type."""
    cpp_returns = _VT_CLASS_MAP.get(method.returns or "", method.returns)
    return {
        "kind": "instance_getter",
        "name": method.name,
        "c_function": method.function,
        "returns": cpp_returns,
        "doc": method.doc,
    }


def _lifecycle_instance_getter_optional(method, handle_field: str) -> dict:
    """Build context for an optional instance getter."""
    cpp_returns = _VT_CLASS_MAP.get(method.returns or "", method.returns)
    return {
        "kind": "instance_getter_optional",
        "name": method.name,
        "c_function": method.function,
        "returns": cpp_returns,
        "c_struct": method.returns or "",
        "doc": method.doc,
    }


def _lifecycle_validate_json(method, handle_field: str) -> dict:
    """Build context for a JSON validation method."""
    return {
        "kind": "validate_json",
        "name": method.name,
        "c_function": method.function,
        "doc": method.doc or "Validate this object.",
    }


_LIFECYCLE_HANDLERS = {
    "composite_property": _lifecycle_composite_property,
    "class_factory": _lifecycle_class_factory,
    "static_factory": _lifecycle_static_factory,
    "instance": _lifecycle_instance,
    "compound_setter": _lifecycle_compound_setter,
    "instance_getter": _lifecycle_instance_getter,
    "instance_getter_optional": _lifecycle_instance_getter_optional,
    "validate_json": _lifecycle_validate_json,
}


def _build_lifecycle(method, handle_field: str) -> dict | None:
    """Build C++ lifecycle method context from an IRMethod. Returns None to skip."""
    handler = _LIFECYCLE_HANDLERS.get(method.kind)
    if handler is None:
        return None
    return handler(method, handle_field)


# -----------------------------------------------------------------------
# Class context assembly
# -----------------------------------------------------------------------


def _build_class(ir_cls, idl: IDL) -> dict:
    """Build complete C++ class context from an IRClass."""
    hf = _handle_field(ir_cls.handle_type)

    properties = []
    for prop in ir_cls.properties:
        p = _build_prop(prop, hf)
        if p:
            properties.append(p)

    collections = []
    for coll in ir_cls.collections:
        collections.append(
            {
                "name": coll.name,
                "singular": _singular(coll.name),
                "item_class": _cpp_class_name(coll.item_class),
                "count_fn": coll.count_fn,
                "at_fn": coll.at_fn,
                "find_by_id_fn": coll.find_by_id_fn,
                "find_by_label_fn": coll.find_by_label_fn,
            }
        )

    builders = [_build_builder(m, hf) for m in ir_cls.methods if m.kind == "builder"]

    # Find to_json function
    to_json_fn = None
    for method in ir_cls.methods:
        if method.name == "to_json":
            to_json_fn = method.function
            break

    # Build lifecycle method contexts
    lifecycle = []
    for method in ir_cls.methods:
        if is_lifecycle_method(method):
            ctx = _build_lifecycle(method, hf)
            if ctx:
                lifecycle.append(ctx)

    # Custom attributes context
    ca_prefix = ir_cls.handle_type.removesuffix("t") if ir_cls.custom_attrs else None

    return {
        "ir_name": ir_cls.name,
        "cpp_name": _cpp_class_name(ir_cls.name),
        "handle_type": ir_cls.handle_type,
        "handle_field": hf,
        "owns_handle": ir_cls.owns_handle,
        "custom_attrs": ir_cls.custom_attrs,
        "ca_prefix": ca_prefix,
        "properties": properties,
        "collections": collections,
        "builders": builders,
        "lifecycle": lifecycle,
        "to_json_fn": to_json_fn,
    }


# -----------------------------------------------------------------------
# Generation
# -----------------------------------------------------------------------

_make_env = make_jinja_env


def generate_raii(idl: IDL, output_dir: Path) -> None:
    """Generate C++ RAII header from the IDL."""
    ir = build_ir(idl)
    output_dir.mkdir(parents=True, exist_ok=True)
    env = _make_env()

    cpp_classes = [_build_class(cls, idl) for cls in ir.classes]

    fdl_class = next(c for c in cpp_classes if c["owns_handle"])
    ref_classes = [c for c in cpp_classes if not c["owns_handle"]]

    # Value type wrapper classes
    vt_defined: set[str] = set()
    value_types = []
    for vt in idl.value_types:
        ctx = _build_vt_class(vt, vt_defined)
        if ctx:
            value_types.append(ctx)

    # Free functions
    free_functions = [_build_free_function(ff, idl) for ff in idl.free_functions]

    # Utility functions (C ABI-backed, e.g. resolve_geometry_layer)
    # Deduplicate by c_function since Python splits dims/anchor but C++ returns both
    c_abi_utils = []
    seen_c_functions: set[str] = set()
    for u in idl.utilities:
        if u.kind == "c_abi" and u.c_function and u.c_function not in seen_c_functions:
            seen_c_functions.add(u.c_function)
            # Strip "fdl_" prefix for C++ name: fdl_resolve_geometry_layer → resolve_geometry_layer
            cpp_name = u.c_function
            if cpp_name.startswith("fdl_"):
                cpp_name = cpp_name[4:]
            c_abi_utils.append(
                {
                    "cpp_name": cpp_name,
                    "c_function": u.c_function,
                    "doc": u.doc,
                }
            )

    # IO convenience functions (read/write from file/string)
    has_io_utils = any(u.kind == "io" for u in idl.utilities)

    # Auxiliary structs (ClipID, FileSequence, Version)
    aux = _build_auxiliary_structs(idl)

    # TemplateResult struct
    # VT wrapper names that should be used instead of raw C structs
    _vt_wrapper_names = set(_VT_CLASS_MAP.values())
    template_result = None
    if idl.auxiliary_types.dataclasses:
        for dc in idl.auxiliary_types.dataclasses:
            if dc.class_name == "TemplateResult":
                fields = []
                for f in dc.fields:
                    if f.field_type == "object":
                        cpp_type = "FDL"
                    elif f.field_type in _ALL_CLASSES:
                        cpp_type = _cpp_class_name(f.field_type)
                    elif f.field_type in _vt_wrapper_names:
                        cpp_type = f.field_type
                    else:
                        cpp_type = _DC_FIELD_CPP.get(f.field_type, f.field_type)
                    fields.append(
                        {
                            "name": f.name,
                            "cpp_type": cpp_type,
                            "is_move": cpp_type in ("FDL", "std::string"),
                            "private": f.private,
                        }
                    )
                accessors = None
                if dc.accessors:
                    accessors = []
                    for acc in dc.accessors:
                        # Build C++ accessor: use direct find methods on RAII classes
                        parts = acc.collection.split(".")
                        singular = _singular(parts[1])
                        find_suffix = f"find_{acc.lookup}"
                        if parts[0] == "fdl":
                            call_expr = f"fdl.{singular}_{find_suffix}(_{acc.key_field})"
                        else:
                            call_expr = f"{parts[0]}().{singular}_{find_suffix}(_{acc.key_field})"
                        cpp_returns = _cpp_class_name(acc.returns) if acc.returns in _ALL_CLASSES else acc.returns
                        accessors.append(
                            {
                                "name": acc.name,
                                "returns": cpp_returns,
                                "doc": acc.doc,
                                "call_expr": call_expr,
                            }
                        )
                template_result = {"class_name": dc.class_name, "fields": fields, "accessors": accessors}

    # Extra dataclasses (everything except TemplateResult — defined after ref_classes)
    extra_dataclasses = []
    if idl.auxiliary_types.dataclasses:
        for dc in idl.auxiliary_types.dataclasses:
            if dc.class_name == "TemplateResult":
                continue
            fields = []
            for f in dc.fields:
                if f.field_type == "object":
                    cpp_type = "FDL"
                elif f.field_type in _ALL_CLASSES:
                    cpp_type = _cpp_class_name(f.field_type)
                elif f.field_type in _vt_wrapper_names:
                    cpp_type = f.field_type
                else:
                    cpp_type = _DC_FIELD_CPP.get(f.field_type, f.field_type)
                fields.append({"name": f.name, "cpp_type": cpp_type})
            extra_dataclasses.append({"class_name": dc.class_name, "fields": fields})

    tmpl = env.get_template("cpp/raii_header.hpp.j2")
    header_src = tmpl.render(
        fdl_class=fdl_class,
        ref_classes=ref_classes,
        template_result=template_result,
        extra_dataclasses=extra_dataclasses,
        value_types=value_types,
        free_functions=free_functions,
        c_abi_utils=c_abi_utils,
        has_io_utils=has_io_utils,
        aux_json_wrappers=aux["json_wrappers"],
        aux_version=aux["version"],
    )
    (output_dir / "fdl.hpp").write_text(header_src, encoding="utf-8")

    vt_names = [vt["cpp_class"] for vt in value_types]
    ff_names = [ff["cpp_name"] for ff in free_functions]
    util_names = [u["cpp_name"] for u in c_abi_utils]
    print(
        f"Generated C++ RAII header with {1 + len(ref_classes)} classes, "
        f"{len(value_types)} value types ({', '.join(vt_names)}), "
        f"{len(free_functions)} free functions ({', '.join(ff_names)}), "
        f"{len(c_abi_utils)} utility functions ({', '.join(util_names)})" + (", 4 I/O functions" if has_io_utils else "")
    )
    print(f"Output: {output_dir / 'fdl.hpp'}")
