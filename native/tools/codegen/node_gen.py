# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Node.js code generator: produces C++ N-API addon bindings from the IDL.

This module contains all Node.js/N-API-specific type maps, context builders,
and rendering logic.  Language-neutral context builders live in shared_context.py;
Node.js-specific ones live here.  The NodeAdapter in adapters.py resolves IR
type keys to TypeScript types for the facade layer (Phase 2-4).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from .fdl_idl import IDL, Function, FunctionParam, ValueType, build_ir
from .shared_context import make_jinja_env

# -----------------------------------------------------------------------
# Struct types requiring Object<->struct conversion helpers
# -----------------------------------------------------------------------

_STRUCT_TYPES: set[str] = {
    "fdl_dimensions_i64_t",
    "fdl_dimensions_f64_t",
    "fdl_point_f64_t",
    "fdl_rect_t",
    "fdl_abi_version_t",
    "fdl_round_strategy_t",
    "fdl_geometry_t",
    "fdl_from_intent_result_t",
    "fdl_parse_result_t",
    "fdl_template_result_t",
    "fdl_resolve_canvas_result_t",
}

# N-API number extraction method per C type
_NAPI_NUMBER_GETTER: dict[str, str] = {
    "int": "Int32Value",
    "int64_t": "Int64Value",
    "uint32_t": "Uint32Value",
    "double": "DoubleValue",
    "size_t": "Int64Value",
}

# C types needing a static_cast on extraction
_NEEDS_EXTRACT_CAST: dict[str, str] = {
    "int64_t": "int64_t",
    "size_t": "size_t",
}

# Value type converter names used in property scanning
_NODE_VT_CONVERTERS = frozenset({"dimsI64", "dimsF64", "pointF64", "rect", "roundStrategy"})

# IDL type_key → facade type for import resolution
_NODE_VT_TYPE_MAP: dict[str, str] = {
    "fdl_dimensions_i64_t": "DimensionsInt",
    "fdl_dimensions_f64_t": "DimensionsFloat",
    "fdl_point_f64_t": "PointFloat",
    "fdl_rect_t": "Rect",
    "fdl_round_strategy_t": "RoundStrategy",
}


# -----------------------------------------------------------------------
# Naming helpers
# -----------------------------------------------------------------------


def _struct_pascal_name(c_name: str) -> str:
    """Convert a C struct name to PascalCase for helper function names.

    fdl_dimensions_i64_t -> DimensionsI64
    fdl_point_f64_t      -> PointF64
    fdl_abi_version_t    -> AbiVersion
    """
    inner = c_name
    if inner.startswith("fdl_"):
        inner = inner[4:]
    if inner.endswith("_t"):
        inner = inner[:-2]
    return "".join(word.capitalize() for word in inner.split("_"))


# -----------------------------------------------------------------------
# Parameter context builder
# -----------------------------------------------------------------------


def _build_param_context(p: FunctionParam, js_index: int, idl: IDL) -> dict:
    """Build template-ready context for a single JS-visible parameter.

    Every returned dict has: name, index, kind, c_type, call_arg.
    """
    c_type = p.c_type
    stripped = c_type.replace("const ", "").replace("*", "").strip()

    # 1. Opaque handle pointers (fdl_doc_t*, etc.) or void*
    if c_type == "void*" or stripped in idl.opaque_types:
        ptr_type = c_type if c_type == "void*" else c_type.replace("const ", "").strip()
        return {
            "name": p.name,
            "index": js_index,
            "kind": "handle",
            "c_type": ptr_type,
            "call_arg": p.name,
        }

    # 2. String parameters
    if c_type in ("const char*", "char*"):
        nullable = getattr(p, "nullable", False)
        return {
            "name": p.name,
            "index": js_index,
            "kind": "string",
            "c_type": c_type,
            "nullable": nullable,
            "call_arg": f"{p.name}_str.c_str()" if not nullable else f"({p.name}_is_null ? nullptr : {p.name}_str.c_str())",
        }

    # 3. Scalar numbers
    if c_type in _NAPI_NUMBER_GETTER:
        getter = _NAPI_NUMBER_GETTER[c_type]
        extract = f"info[{js_index}].As<Napi::Number>().{getter}()"
        if c_type in _NEEDS_EXTRACT_CAST:
            extract = f"static_cast<{_NEEDS_EXTRACT_CAST[c_type]}>({extract})"
        return {
            "name": p.name,
            "index": js_index,
            "kind": "number",
            "c_type": c_type,
            "extract": extract,
            "call_arg": p.name,
        }

    # 4. Value type (struct) — pass-by-value or pass-by-pointer
    for vt in idl.value_types:
        if stripped == vt.name:
            pascal = _struct_pascal_name(vt.name)
            is_ptr = "*" in c_type
            return {
                "name": p.name,
                "index": js_index,
                "kind": "struct_ptr" if is_ptr else "struct",
                "c_type": vt.name,
                "pascal_name": pascal,
                "call_arg": f"&{p.name}" if is_ptr else p.name,
            }

    # 5. Enum parameters
    for e in idl.enums:
        if c_type == e.name:
            return {
                "name": p.name,
                "index": js_index,
                "kind": "enum",
                "c_type": c_type,
                "extract": f"static_cast<{e.name}>(info[{js_index}].As<Napi::Number>().Uint32Value())",
                "call_arg": p.name,
            }

    # Fallback
    return {
        "name": p.name,
        "index": js_index,
        "kind": "unknown",
        "c_type": c_type,
        "extract": f"info[{js_index}] /* UNKNOWN: {c_type} */",
        "call_arg": p.name,
    }


# -----------------------------------------------------------------------
# Return type classification
# -----------------------------------------------------------------------


def _classify_return(fn: Function, idl: IDL) -> dict:
    """Classify a function's return type for N-API wrapping.

    Returns a dict whose keys are used directly in the function context.
    """
    c_type = fn.returns
    is_caller_frees = fn.ownership is not None and "caller_frees" in fn.ownership

    if c_type == "void":
        return {"return_kind": "void", "return_type": "void"}

    # Caller-frees strings
    if is_caller_frees and c_type in ("char*", "const char*"):
        return {
            "return_kind": "string_free",
            "return_type": c_type,
            "return_nullable": fn.nullable,
        }

    # Borrowed strings
    if c_type in ("const char*", "char*"):
        return {
            "return_kind": "string",
            "return_type": c_type,
            "return_nullable": fn.nullable,
        }

    # Scalar numbers
    if c_type in _NAPI_NUMBER_GETTER:
        return {"return_kind": "number", "return_type": c_type}

    # Opaque handle pointer
    stripped = c_type.replace("const ", "").replace("*", "").strip()
    if stripped in idl.opaque_types:
        return {
            "return_kind": "handle",
            "return_type": c_type,
            "return_nullable": fn.nullable,
        }

    # Value type (struct)
    for vt in idl.value_types:
        if c_type == vt.name:
            return {
                "return_kind": "struct",
                "return_type": c_type,
                "return_pascal_name": _struct_pascal_name(vt.name),
            }

    # Enum
    for e in idl.enums:
        if c_type == e.name:
            return {"return_kind": "enum", "return_type": c_type}

    return {"return_kind": "unknown", "return_type": c_type}


# -----------------------------------------------------------------------
# Function context builder
# -----------------------------------------------------------------------


def _build_napi_function_context(fn: Function, idl: IDL) -> dict:
    """Build a *flat*, template-ready context dict for one C function.

    Keys consumed directly by ``binding.cc.j2``:
      name, wrapper_name, doc,
      return_kind, return_type, return_nullable, return_pascal_name,
      params, out_params, has_out_params,
      call_args_str, is_free_fn
    """
    js_params: list[dict] = []
    out_params: list[dict] = []
    call_args: list[str] = []
    js_index = 0

    for p in fn.params:
        if p.direction == "out":
            base_type = p.c_type.replace("const ", "").replace("*", "").strip()
            pascal = _struct_pascal_name(base_type) if base_type in _STRUCT_TYPES else base_type
            js_name = p.name.removeprefix("out_") if p.name.startswith("out_") else p.name
            out_params.append(
                {
                    "name": p.name,
                    "js_name": js_name,
                    "base_type": base_type,
                    "pascal_name": pascal,
                    "is_struct": base_type in _STRUCT_TYPES,
                }
            )
            call_args.append(f"&{p.name}")
        else:
            ctx = _build_param_context(p, js_index, idl)
            js_params.append(ctx)
            call_args.append(ctx["call_arg"])
            js_index += 1

    ret = _classify_return(fn, idl)

    is_free_fn = ret["return_kind"] == "void" and len(js_params) == 1 and js_params[0]["kind"] == "handle" and "free" in fn.name

    return {
        "name": fn.name,
        "wrapper_name": f"Wrap_{fn.name}",
        "doc": fn.doc or "",
        # Return (flattened from _classify_return)
        "return_kind": ret["return_kind"],
        "return_type": ret.get("return_type", "void"),
        "return_nullable": ret.get("return_nullable", False),
        "return_pascal_name": ret.get("return_pascal_name", ""),
        # Parameters
        "params": js_params,
        "out_params": out_params,
        "has_out_params": bool(out_params),
        "call_args_str": ", ".join(call_args),
        "is_free_fn": is_free_fn,
    }


# -----------------------------------------------------------------------
# Struct helper context builder (structs.h)
# -----------------------------------------------------------------------


def _build_struct_helpers_context(vt: ValueType) -> dict:
    """Build context for ObjectTo* / *ToObject helpers in structs.h."""
    pascal = _struct_pascal_name(vt.name)
    fields = []

    for f in vt.fields:
        fields.append(_classify_struct_field(f.c_type, f.name))

    return {"c_name": vt.name, "pascal_name": pascal, "fields": fields}


def _classify_struct_field(c_type: str, name: str) -> dict:
    """Classify one struct field for Object<->struct conversion.

    Every returned dict has: name, c_type, kind, to_c, to_js, is_nested.
    Nested structs also have: pascal_name.
    """
    # Integer types
    if c_type in ("int", "int64_t", "uint32_t"):
        napi_getter = {"int": "Int32Value", "int64_t": "Int64Value", "uint32_t": "Uint32Value"}[c_type]
        to_c = f'obj.Get("{name}").As<Napi::Number>().{napi_getter}()'
        if c_type == "int64_t":
            to_c = f'static_cast<int64_t>(obj.Get("{name}").As<Napi::Number>().Int64Value())'
        to_js = f"Napi::Number::New(env, static_cast<double>(d.{name}))" if c_type == "int64_t" else f"Napi::Number::New(env, d.{name})"
        return {"name": name, "c_type": c_type, "kind": "number", "to_c": to_c, "to_js": to_js, "is_nested": False}

    if c_type == "double":
        return {
            "name": name,
            "c_type": c_type,
            "kind": "number",
            "to_c": f'obj.Get("{name}").As<Napi::Number>().DoubleValue()',
            "to_js": f"Napi::Number::New(env, d.{name})",
            "is_nested": False,
        }

    # String fields
    if c_type in ("char*", "const char*"):
        return {
            "name": name,
            "c_type": c_type,
            "kind": "string",
            "to_c": f'obj.Get("{name}").As<Napi::String>().Utf8Value()',
            "to_js": f"d.{name} ? Napi::String::New(env, d.{name}) : env.Null()",
            "is_nested": False,
        }

    # Nested struct
    if c_type in _STRUCT_TYPES:
        pascal = _struct_pascal_name(c_type)
        return {
            "name": name,
            "c_type": c_type,
            "kind": "nested_struct",
            "pascal_name": pascal,
            "to_c": f'ObjectTo{pascal}(obj.Get("{name}").As<Napi::Object>())',
            "to_js": f"{pascal}ToObject(env, d.{name})",
            "is_nested": True,
        }

    # Opaque pointer inside a struct
    if c_type.endswith("*"):
        return {
            "name": name,
            "c_type": c_type,
            "kind": "handle",
            "to_c": f'static_cast<{c_type}>(obj.Get("{name}").As<Napi::External<void>>().Data())',
            "to_js": (f"d.{name} ? Napi::External<void>::New(env, const_cast<void*>(static_cast<const void*>(d.{name}))) : env.Null()"),
            "is_nested": False,
        }

    # Enum or other integral
    return {
        "name": name,
        "c_type": c_type,
        "kind": "enum",
        "to_c": f'static_cast<{c_type}>(obj.Get("{name}").As<Napi::Number>().Uint32Value())',
        "to_js": f"Napi::Number::New(env, static_cast<uint32_t>(d.{name}))",
        "is_nested": False,
    }


# -----------------------------------------------------------------------
# Custom attribute function synthesis
# -----------------------------------------------------------------------

# (suffix, extra_param_types_after_handle, c_return_type)
_CA_FUNCTIONS: list[tuple[str, list[str], str]] = [
    ("set_custom_attr_string", ["const char*", "const char*"], "int"),
    ("set_custom_attr_int", ["const char*", "int64_t"], "int"),
    ("set_custom_attr_float", ["const char*", "double"], "int"),
    ("set_custom_attr_bool", ["const char*", "int"], "int"),
    ("get_custom_attr_string", ["const char*"], "const char*"),
    ("get_custom_attr_int", ["const char*", "int64_t*"], "int"),
    ("get_custom_attr_float", ["const char*", "double*"], "int"),
    ("get_custom_attr_bool", ["const char*", "int*"], "int"),
    ("has_custom_attr", ["const char*"], "int"),
    ("get_custom_attr_type", ["const char*"], "uint32_t"),
    ("remove_custom_attr", ["const char*"], "int"),
    ("custom_attrs_count", [], "uint32_t"),
    ("custom_attr_name_at", ["uint32_t"], "const char*"),
    ("set_custom_attr_point_f64", ["const char*", "fdl_point_f64_t"], "int"),
    ("get_custom_attr_point_f64", ["const char*", "fdl_point_f64_t*"], "int"),
    ("set_custom_attr_dims_f64", ["const char*", "fdl_dimensions_f64_t"], "int"),
    ("get_custom_attr_dims_f64", ["const char*", "fdl_dimensions_f64_t*"], "int"),
    ("set_custom_attr_dims_i64", ["const char*", "fdl_dimensions_i64_t"], "int"),
    ("get_custom_attr_dims_i64", ["const char*", "fdl_dimensions_i64_t*"], "int"),
]


def _generate_custom_attr_functions(idl: IDL) -> list[Function]:
    """Synthesize Function objects for the macro-expanded custom attr C functions."""
    functions: list[Function] = []
    for cls in idl.object_model.classes:
        if not cls.custom_attrs:
            continue
        prefix = cls.c_handle.removesuffix("t")  # fdl_doc_t -> fdl_doc_
        handle_type = cls.c_handle + "*"

        for suffix, extra_types, ret_type in _CA_FUNCTIONS:
            fn_name = f"{prefix}{suffix}"
            params = [FunctionParam(name="handle", c_type=handle_type)]

            for i, pt in enumerate(extra_types):
                is_ptr = pt.endswith("*") and pt not in ("const char*", "char*")
                if is_ptr:
                    params.append(FunctionParam(name="out_value", c_type=pt, direction="out"))
                else:
                    pname = "key" if pt == "const char*" and i == 0 else f"arg{i}"
                    params.append(FunctionParam(name=pname, c_type=pt))

            functions.append(
                Function(
                    name=fn_name,
                    returns=ret_type,
                    params=params,
                    doc=f"Custom attr: {suffix} on {cls.name}",
                    nullable="get_custom_attr_string" in suffix,
                )
            )

    return functions


# -----------------------------------------------------------------------
# Generation entry points
# -----------------------------------------------------------------------

_make_env = make_jinja_env


def generate_addon(idl: IDL, output_dir: Path) -> None:
    """Generate C++ N-API addon files (binding.cc, structs.h).

    Produces:
      - binding.cc: N-API wrapper functions for all C ABI functions
        (including custom attribute functions), plus module init.
      - structs.h: ObjectTo*/\u200b*ToObject helpers for each value type.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    env = _make_env()

    # --- Struct helpers ---
    struct_contexts = [_build_struct_helpers_context(vt) for vt in idl.value_types]

    # --- Function wrappers (IDL functions + synthesized custom-attr functions) ---
    all_fns = list(idl.functions) + _generate_custom_attr_functions(idl)
    fn_contexts = [_build_napi_function_context(fn, idl) for fn in all_fns]

    # --- Module init registrations (export using C function names) ---
    registrations = [{"c_name": ctx["name"], "wrapper_name": ctx["wrapper_name"]} for ctx in fn_contexts]

    # --- Filter structs to those actually referenced ---
    used_struct_names: set[str] = set()
    for ctx in fn_contexts:
        for p in ctx["params"]:
            if p["kind"] in ("struct", "struct_ptr"):
                used_struct_names.add(p["c_type"])
        if ctx["return_kind"] == "struct":
            used_struct_names.add(ctx["return_type"])
        for op in ctx["out_params"]:
            if op["is_struct"]:
                used_struct_names.add(op["base_type"])
    # Transitive nested deps
    for sc in struct_contexts:
        if sc["c_name"] in used_struct_names:
            for f in sc["fields"]:
                if f["is_nested"]:
                    used_struct_names.add(f["c_type"])

    used_structs = [sc for sc in struct_contexts if sc["c_name"] in used_struct_names]

    # Topological sort: leaf structs (no nested deps) first
    sorted_structs: list[dict] = []
    remaining = list(used_structs)
    remaining_names = {sc["c_name"] for sc in remaining}
    while remaining:
        batch = [
            sc for sc in remaining if not any(f["is_nested"] and f["c_type"] in remaining_names - {sc["c_name"]} for f in sc["fields"])
        ]
        if not batch:
            sorted_structs.extend(remaining)
            break
        for sc in batch:
            sorted_structs.append(sc)
            remaining_names.discard(sc["c_name"])
            remaining.remove(sc)

    # --- Render ---
    structs_tmpl = env.get_template("node/structs.h.j2")
    (output_dir / "structs.h").write_text(
        encoding="utf-8",
        data=structs_tmpl.render(structs=sorted_structs),
    )

    binding_tmpl = env.get_template("node/binding.cc.j2")
    (output_dir / "binding.cc").write_text(
        encoding="utf-8",
        data=binding_tmpl.render(functions=fn_contexts, registrations=registrations),
    )

    print(f"Generated N-API addon: {len(fn_contexts)} function wrappers, {len(sorted_structs)} struct helpers")
    print(f"Output: {output_dir}")


def _gen_node_constants(env, idl, output_dir: Path) -> list[dict]:
    """Generate constants.ts and return constants_contexts."""
    from .node_context import build_node_constants_enum_context

    constants_contexts = [build_node_constants_enum_context(e) for e in idl.enums if e.facade_class]
    tmpl = env.get_template("node/constants.ts.j2")
    (output_dir / "constants.ts").write_text(
        encoding="utf-8",
        data=tmpl.render(enums=constants_contexts),
    )
    return constants_contexts


def _gen_node_enum_maps(env, idl, enum_contexts: list[dict], output_dir: Path) -> None:
    """Generate enum-maps.ts."""
    tmpl = env.get_template("node/enum-maps.ts.j2")
    (output_dir / "enum-maps.ts").write_text(
        encoding="utf-8",
        data=tmpl.render(enums=enum_contexts),
    )


def _gen_node_types(env, idl, output_dir: Path) -> tuple[list[dict], list[dict]]:
    """Generate types.ts and return (types_vt_contexts, rounding_vt_contexts)."""
    from .node_context import build_node_value_type_context

    # --- Value type contexts (split types vs rounding) ---
    all_vt_contexts = [build_node_value_type_context(vt, idl) for vt in idl.value_types if vt.facade_class]
    types_vt_contexts = [ctx for ctx in all_vt_contexts if ctx["ts_class"] != "RoundStrategy"]
    rounding_vt_contexts = [ctx for ctx in all_vt_contexts if ctx["ts_class"] == "RoundStrategy"]

    # Collect imports for types.ts
    all_types_enum_imports: set[str] = set()
    all_types_enum_map_imports: set[str] = set()
    for ctx in types_vt_contexts:
        all_types_enum_imports.update(ctx["enum_imports"])
        for m in ctx["methods"]:
            all_types_enum_imports.update(m.get("needed_enum_imports", []))
            all_types_enum_map_imports.update(m["needed_enum_maps"])
        for op in ctx["operators"]:
            all_types_enum_map_imports.update(op.get("needed_enum_maps", []))

    # --- types.ts ---
    tmpl = env.get_template("node/types.ts.j2")
    (output_dir / "types.ts").write_text(
        encoding="utf-8",
        data=tmpl.render(
            value_types=types_vt_contexts,
            all_enum_imports=sorted(all_types_enum_imports),
            all_enum_map_imports=sorted(all_types_enum_map_imports),
            has_float_compare=any(ctx["float_compare"] for ctx in types_vt_contexts),
        ),
    )
    return types_vt_contexts, rounding_vt_contexts


def _gen_node_converters(env, idl, output_dir: Path) -> None:
    """Generate converters.ts."""
    from .node_context import build_node_converter_context

    converter_contexts = [build_node_converter_context(vt, idl) for vt in idl.value_types if vt.facade_converter]
    all_type_imports: set[str] = set()
    all_enum_map_imports: set[str] = set()
    all_enum_class_imports: set[str] = set()
    for ctx in converter_contexts:
        all_type_imports.add(ctx["ts_class"])
        all_enum_map_imports.update(ctx["enum_from_c_imports"])
        all_enum_map_imports.update(ctx["enum_to_c_imports"])
        all_enum_class_imports.update(ctx["enum_class_imports"])

    # Split type imports: RoundStrategy lives in rounding.ts, others in types.ts
    rounding_type_imports = {t for t in all_type_imports if t == "RoundStrategy"}
    types_only_imports = all_type_imports - rounding_type_imports

    tmpl = env.get_template("node/converters.ts.j2")
    (output_dir / "converters.ts").write_text(
        encoding="utf-8",
        data=tmpl.render(
            value_types=converter_contexts,
            types_type_imports=sorted(types_only_imports),
            rounding_type_imports=sorted(rounding_type_imports),
            all_enum_map_imports=sorted(all_enum_map_imports),
            all_enum_class_imports=sorted(all_enum_class_imports),
        ),
    )


def _gen_node_errors(env, idl, output_dir: Path) -> None:
    """Generate errors.ts."""
    aux = idl.auxiliary_types
    if aux.errors:
        parent_map = {"Exception": "Error"}
        error_contexts = [{"name": e.name, "parent": parent_map.get(e.parent, e.parent), "doc": e.doc} for e in aux.errors]
        tmpl = env.get_template("node/errors.ts.j2")
        (output_dir / "errors.ts").write_text(
            encoding="utf-8",
            data=tmpl.render(errors=error_contexts),
        )


def _gen_node_version(env, idl, output_dir: Path) -> None:
    """Generate version.ts."""
    aux = idl.auxiliary_types
    if aux.version:
        v = aux.version
        eq_parts = [f"this.{s.name} === other.{s.name}" for s in v.slots]
        repr_format = v.class_name + "(" + ", ".join(f"{s.name}=${{this.{s.name}}}" for s in v.slots) + ")"
        tmpl = env.get_template("node/version.ts.j2")
        (output_dir / "version.ts").write_text(
            encoding="utf-8",
            data=tmpl.render(
                version={
                    "class_name": v.class_name,
                    "doc": v.doc,
                    "slots": v.slots,
                    "eq_parts": eq_parts,
                    "repr_format": repr_format,
                },
            ),
        )


def _gen_node_free_functions(idl) -> tuple[list[dict], list[dict], list, list[dict]]:
    """Split free functions into rounding vs utils groups.

    Returns (rounding_ff_contexts, utils_ff_contexts, eligible_ffs, ff_contexts).
    """
    from .node_context import build_node_free_function_context

    # --- Free functions (split: rounding vs utils) ---
    # Skip functions whose return types have no TS facade mapping (hand-coded in templates)
    _NODE_SKIP_FF = {"abi_version", "compute_framing_from_intent"}
    eligible_ffs = [ff for ff in idl.free_functions if ff.display_name not in _NODE_SKIP_FF]
    ff_contexts = [build_node_free_function_context(ff, idl) for ff in eligible_ffs]
    ff_by_module: dict[str, list[dict]] = {}
    for ff, ctx in zip(eligible_ffs, ff_contexts):
        mod = ff.module or "utils"
        ff_by_module.setdefault(mod, []).append(ctx)

    rounding_ff_contexts = ff_by_module.get("rounding", [])
    utils_ff_contexts = ff_by_module.get("utils", [])
    return rounding_ff_contexts, utils_ff_contexts, eligible_ffs, ff_contexts


def _gen_node_rounding(env, rounding_vt_contexts: list[dict], rounding_ff_contexts: list[dict], output_dir: Path) -> None:
    """Generate rounding.ts."""
    # Collect rounding imports
    rs_enum_imports: set[str] = set()
    rs_enum_map_imports: set[str] = set()
    rs_type_imports: set[str] = set()
    for ctx in rounding_vt_contexts:
        rs_enum_imports.update(ctx["enum_imports"])
    for ctx in rounding_ff_contexts:
        rs_enum_imports.update(ctx.get("needed_enum_imports", []))
        rs_enum_map_imports.update(ctx["needed_enum_maps"])
        rs_type_imports.update(ctx["needed_types"])

    rs_ctx = rounding_vt_contexts[0] if rounding_vt_contexts else None

    # --- rounding.ts ---
    tmpl = env.get_template("node/rounding.ts.j2")
    (output_dir / "rounding.ts").write_text(
        encoding="utf-8",
        data=tmpl.render(
            round_strategy=rs_ctx,
            free_functions=rounding_ff_contexts,
            enum_imports=sorted(rs_enum_imports),
            enum_map_imports=sorted(rs_enum_map_imports),
            type_imports=sorted(rs_type_imports),
        ),
    )


def _gen_node_utils(env, idl, utils_ff_contexts: list[dict], output_dir: Path) -> None:
    """Generate utils.ts."""
    aux = idl.auxiliary_types

    # Collect utils imports
    utils_type_imports: set[str] = set()
    utils_enum_imports: set[str] = set()
    utils_enum_map_imports: set[str] = set()
    for ctx in utils_ff_contexts:
        utils_type_imports.update(ctx["needed_types"])
        utils_enum_imports.update(ctx.get("needed_enum_imports", []))
        utils_enum_map_imports.update(ctx["needed_enum_maps"])

    # --- utils.ts ---
    tmpl = env.get_template("node/utils.ts.j2")
    (output_dir / "utils.ts").write_text(
        encoding="utf-8",
        data=tmpl.render(
            free_functions=utils_ff_contexts,
            type_imports=sorted(utils_type_imports),
            enum_imports=sorted(utils_enum_imports),
            enum_map_imports=sorted(utils_enum_map_imports),
            has_version=bool(aux.version),
        ),
    )


def _gen_node_classes(env, idl, enum_contexts: list[dict], output_dir: Path) -> list[dict]:
    """Generate per-class .ts files and custom-attrs.ts. Return class_contexts."""
    from .node_context import build_node_facade_class_context, class_to_module

    # ===================================================================
    # Phase 3: Facade classes, custom-attrs, index
    # ===================================================================

    ir = build_ir(idl)
    ir_class_by_name = {cls.name: cls for cls in ir.classes}
    class_contexts = [build_node_facade_class_context(cls, idl, enum_contexts, ir_class_by_name) for cls in ir.classes]
    all_class_names = {ctx["name"] for ctx in class_contexts}

    # NodeAdapter for type resolution
    from .adapters import NodeAdapter

    node_adapter = NodeAdapter()

    # Converter function lookup (property converter key -> from/to function)
    converter_fn_map = {
        "dimsI64": "fromDimsI64",
        "dimsF64": "fromDimsF64",
        "pointF64": "fromPointF64",
        "rect": "fromRect",
        "roundStrategy": "fromRoundStrategy",
    }
    converter_to_fn_map = {
        "dimsI64": "toDimsI64",
        "dimsF64": "toDimsF64",
        "pointF64": "toPointF64",
        "rect": "toRect",
        "roundStrategy": "toRoundStrategy",
    }

    # --- custom-attrs.ts (rendered from template, no dynamic context) ---
    has_custom_attrs = any(ctx.get("custom_attrs") for ctx in class_contexts)
    if has_custom_attrs:
        ca_tmpl = env.get_template("node/custom-attrs.ts.j2")
        (output_dir / "custom-attrs.ts").write_text(encoding="utf-8", data=ca_tmpl.render())

    # --- Per-class facade files ---
    class_tmpl = env.get_template("node/class.ts.j2")
    for cls_ctx in class_contexts:
        imports = _compute_node_class_imports(
            cls_ctx,
            enum_contexts,
            all_class_names,
            node_adapter,
            converter_fn_map,
            converter_to_fn_map,
        )
        module_name = class_to_module(cls_ctx["name"])
        # inline_interfaces are built by build_node_facade_class_context
        (output_dir / f"{module_name}.ts").write_text(
            encoding="utf-8",
            data=class_tmpl.render(cls=cls_ctx, imports=imports),
        )

    return class_contexts


def _gen_node_index(
    env,
    class_contexts: list[dict],
    constants_contexts: list[dict],
    utils_ff_contexts: list[dict],
    idl,
    output_dir: Path,
) -> None:
    """Generate index.ts."""
    from .node_context import class_to_module

    aux = idl.auxiliary_types

    # --- index.ts ---
    class_entries = []
    for cls_ctx in class_contexts:
        class_entries.append(
            {
                "name": cls_ctx["name"],
                "module": class_to_module(cls_ctx["name"]),
            }
        )
    # Sort: FDL first, then alphabetically
    class_entries.sort(key=lambda e: (not e["name"].isupper(), e["name"].casefold()))

    enum_names = sorted(ec["ts_class"] for ec in constants_contexts)
    error_names = [e.name for e in aux.errors] if aux.errors else []
    # Hand-coded utils that are added in the template alongside codegen-generated ones
    _HANDCODED_UTILS = {
        "readFromString",
        "readFromFile",
        "writeToString",
        "writeToFile",
        "abiVersion",
        "getDimensionsFromPath",
        "getAnchorFromPath",
        "computeFramingFromIntent",
    }
    utils_names = sorted(set(ctx["name"] for ctx in utils_ff_contexts) | _HANDCODED_UTILS)

    index_tmpl = env.get_template("node/index.ts.j2")
    (output_dir / "index.ts").write_text(
        encoding="utf-8",
        data=index_tmpl.render(
            classes=class_entries,
            enums=enum_names,
            errors=error_names,
            utils=utils_names,
        ),
    )


def generate_facade(idl: IDL, output_dir: Path) -> None:
    """Generate idiomatic TypeScript facade files from the IDL.

    Phases 2-3: constants, enums, value types, converters, errors, version,
    rounding, utility modules, facade classes, custom-attrs, and index.
    """
    from .node_context import class_to_module
    from .shared_context import build_enum_context

    output_dir.mkdir(parents=True, exist_ok=True)
    env = _make_env()

    # --- Enum contexts (for enum-maps.ts) ---
    enum_contexts = [build_enum_context(e) for e in idl.enums if e.facade_class]

    constants_contexts = _gen_node_constants(env, idl, output_dir)
    _gen_node_enum_maps(env, idl, enum_contexts, output_dir)
    types_vt_contexts, rounding_vt_contexts = _gen_node_types(env, idl, output_dir)
    _gen_node_converters(env, idl, output_dir)
    _gen_node_errors(env, idl, output_dir)
    _gen_node_version(env, idl, output_dir)
    rounding_ff_contexts, utils_ff_contexts, eligible_ffs, ff_contexts = _gen_node_free_functions(idl)
    _gen_node_rounding(env, rounding_vt_contexts, rounding_ff_contexts, output_dir)
    _gen_node_utils(env, idl, utils_ff_contexts, output_dir)
    class_contexts = _gen_node_classes(env, idl, enum_contexts, output_dir)
    _gen_node_index(env, class_contexts, constants_contexts, utils_ff_contexts, idl, output_dir)

    generated_files = [
        "constants.ts",
        "enum-maps.ts",
        "types.ts",
        "converters.ts",
        "errors.ts",
        "version.ts",
        "rounding.ts",
        "utils.ts",
        "custom-attrs.ts",
        "index.ts",
    ] + [f"{class_to_module(ctx['name'])}.ts" for ctx in class_contexts]
    print(f"Generated Node.js facade: {len(generated_files)} files")
    print(f"  Value types: {len(types_vt_contexts)}, Enums: {len(constants_contexts)}")
    print(f"  Classes: {len(class_contexts)}")
    print(f"  Free functions: {len(rounding_ff_contexts)} rounding, {len(utils_ff_contexts)} utils")
    print(f"Output: {output_dir}")


# -----------------------------------------------------------------------
# Import computation helpers
# -----------------------------------------------------------------------


def _node_add_vt_type_import(type_imports_map, ts_type):
    """Add a value type import to the correct module."""
    if ts_type == "RoundStrategy":
        type_imports_map.setdefault("./rounding.js", set()).add(ts_type)
    else:
        type_imports_map.setdefault("./types.js", set()).add(ts_type)


def _node_import_param_type(tk, acc, enum_tk_to_facade, enum_tk_to_map):
    """Add imports for a parameter type_key used in builders/lifecycle."""
    if tk in _NODE_VT_TYPE_MAP:
        _node_add_vt_type_import(acc.type_imports_map, _NODE_VT_TYPE_MAP[tk])
    if tk in enum_tk_to_facade:
        acc.type_imports_map.setdefault("./constants.js", set()).add(enum_tk_to_facade[tk])
        acc.enum_map_imports.add(enum_tk_to_map[tk])


def _scan_node_properties(cls_ctx, acc, enum_contexts, all_class_names, node_adapter, converter_fn_map, converter_to_fn_map):
    """Scan properties for import requirements."""
    from .node_context import class_to_module

    for prop in cls_ctx["properties"]:
        conv = prop["converter"]
        if conv in _NODE_VT_CONVERTERS:
            acc.converter_imports.add(converter_fn_map[conv])
            if prop.get("setter_fn"):
                acc.converter_imports.add(converter_to_fn_map[conv])
            ts_type = node_adapter.TYPES.get(prop["type_key"], "")
            if ts_type and ts_type != "object":
                _node_add_vt_type_import(acc.type_imports_map, ts_type)
        if conv.startswith("enum"):
            if prop.get("enum_from_c"):
                acc.enum_map_imports.add(prop["enum_from_c"])
            if prop.get("enum_to_c") and prop.get("setter_fn"):
                acc.enum_map_imports.add(prop["enum_to_c"])
            ts_type = node_adapter.TYPES.get(prop["type_key"], "")
            if ts_type:
                acc.type_imports_map.setdefault("./constants.js", set()).add(ts_type)
        if conv == "handleRef" and prop.get("handle_class"):
            hc = prop["handle_class"]
            if hc in all_class_names and hc != cls_ctx["name"]:
                acc.lazy_class_imports.append({"cls": hc, "module": class_to_module(hc)})


def _scan_node_collections(cls_ctx, acc, all_class_names):
    """Scan collections for lazy class imports."""
    for coll in cls_ctx["collections"]:
        ic = coll["item_class"]
        if ic in all_class_names and ic != cls_ctx["name"]:
            acc.lazy_class_imports.append({"cls": ic, "module": coll["item_module"]})


def _scan_node_builders(cls_ctx, acc, all_class_names, enum_tk_to_facade, enum_tk_to_map, converter_to_fn_map):
    """Scan builders for import requirements."""
    from .node_context import class_to_module

    for builder in cls_ctx["builders"]:
        ret = builder["returns"]
        if ret in all_class_names and ret != cls_ctx["name"]:
            acc.lazy_class_imports.append({"cls": ret, "module": class_to_module(ret)})
        for p in builder.get("params", []):
            tk = p.get("type_key", "")
            _node_import_param_type(tk, acc, enum_tk_to_facade, enum_tk_to_map)
        for arg in builder.get("addon_args", []):
            for to_fn in converter_to_fn_map.values():
                if to_fn in arg:
                    acc.converter_imports.add(to_fn)


def _scan_node_lifecycle(cls_ctx, acc, all_class_names, enum_tk_to_facade, enum_tk_to_map, converter_to_fn_map):
    """Scan lifecycle methods for import requirements."""
    from .node_context import class_to_module

    for method in cls_ctx["lifecycle"]:
        kind = method["kind"]
        error = method.get("error")
        if error and error.get("error_class"):
            acc.error_imports.add(error["error_class"])
        if kind == "instance" and error and error.get("pattern") == "validation":
            acc.error_imports.add("FDLValidationError")
        if kind == "validate_json":
            acc.error_imports.add("FDLValidationError")
        if kind == "composite_property" and method.get("returns") == "Version":
            acc.needs_version = True
            acc.value_imports_map.setdefault("./version.js", set()).add("Version")
        if kind in ("instance_getter", "instance_getter_optional"):
            conv_fn = method.get("converter_fn")
            if conv_fn:
                acc.converter_imports.add(conv_fn)
            ret = method.get("returns")
            if ret and ret not in ("string", "number", "boolean"):
                _node_add_vt_type_import(acc.type_imports_map, ret)
        if error and error.get("result_fields"):
            for rf in error["result_fields"]:
                if rf.get("wrap_class") and rf["wrap_class"] in all_class_names:
                    wc = rf["wrap_class"]
                    if wc != cls_ctx["name"]:
                        acc.lazy_class_imports.append({"cls": wc, "module": class_to_module(wc)})
                if rf.get("converter"):
                    acc.converter_imports.add(rf["converter"])
        for p in method.get("params", []):
            tk = p.get("type_key", "")
            if tk == "handle":
                ts_type = p.get("ts_type", "")
                if ts_type in all_class_names and ts_type != cls_ctx["name"]:
                    acc.lazy_class_imports.append({"cls": ts_type, "module": class_to_module(ts_type)})
            else:
                _node_import_param_type(tk, acc, enum_tk_to_facade, enum_tk_to_map)
        for arg in method.get("addon_args", []):
            for to_fn in converter_to_fn_map.values():
                if to_fn in arg:
                    acc.converter_imports.add(to_fn)
        for p in method.get("params", []):
            if p.get("global_fallback"):
                acc.rounding_imports.add(p["global_fallback"])


def _scan_node_init(cls_ctx, acc, all_class_names, enum_tk_to_facade, enum_tk_to_map, converter_to_fn_map):
    """Scan init context for import requirements."""

    init_ctx = cls_ctx.get("init")
    if not init_ctx:
        return

    for p in init_ctx.get("params", []):
        if not p.get("ignore"):
            tk = p.get("type_key", "")
            if tk:
                _node_import_param_type(tk, acc, enum_tk_to_facade, enum_tk_to_map)
            default = p.get("default", "")
            if default and isinstance(default, str) and "." in default:
                enum_cls = default.split(".")[0]
                if enum_cls and enum_cls in enum_tk_to_facade.values():
                    acc.value_imports_map.setdefault("./constants.js", set()).add(enum_cls)
            if default and isinstance(default, str) and "new " in default:
                for vt_cls in ("PointFloat", "DimensionsFloat", "DimensionsInt"):
                    if vt_cls in default:
                        acc.value_imports_map.setdefault("./types.js", set()).add(vt_cls)
                if "RoundStrategy" in default:
                    acc.value_imports_map.setdefault("./rounding.js", set()).add("RoundStrategy")

    for arg in init_ctx.get("addon_args", []):
        for to_fn in converter_to_fn_map.values():
            if to_fn in arg:
                acc.converter_imports.add(to_fn)
        for map_name in enum_tk_to_map.values():
            if map_name in arg:
                acc.enum_map_imports.add(map_name)

    for ps in init_ctx.get("post_setters", []):
        for arg in ps.get("args", []):
            default = arg.get("default", "")
            if default and isinstance(default, str):
                for vt_cls in ("PointFloat", "DimensionsFloat", "DimensionsInt"):
                    if vt_cls in default:
                        acc.value_imports_map.setdefault("./types.js", set()).add(vt_cls)

    if init_ctx["depth"] >= 1:
        acc.lazy_class_imports.append({"cls": "FDL", "module": "fdl"})


def _scan_node_interfaces(cls_ctx, acc, all_class_names):
    """Scan inline interface accessors for lazy class imports."""
    from .node_context import class_to_module

    for iface in cls_ctx.get("inline_interfaces", []):
        for accessor in iface.get("accessors") or []:
            ret = accessor.get("returns", "")
            if ret and ret in all_class_names and ret != cls_ctx["name"]:
                acc.lazy_class_imports.append({"cls": ret, "module": class_to_module(ret)})


def _finalize_node_imports(acc, converter_fn_map, converter_to_fn_map):
    """Deduplicate and assemble the final import dict."""
    # Deduplicate lazy class imports
    seen_lazy: set[str] = set()
    unique_lazy: list[dict] = []
    for lc in acc.lazy_class_imports:
        if lc["cls"] not in seen_lazy:
            seen_lazy.add(lc["cls"])
            unique_lazy.append(lc)

    # Deduplicate: remove type imports that are also value imports
    for mod, val_names in acc.value_imports_map.items():
        if mod in acc.type_imports_map:
            acc.type_imports_map[mod] -= val_names

    # Build structured type_imports and value_imports lists
    type_imports = [{"module": mod, "names": sorted(names)} for mod, names in sorted(acc.type_imports_map.items()) if names]
    value_imports = [{"module": mod, "names": sorted(names)} for mod, names in sorted(acc.value_imports_map.items()) if names]

    return {
        "type_imports": type_imports,
        "value_imports": value_imports,
        "converter_imports": sorted(acc.converter_imports),
        "enum_map_imports": sorted(acc.enum_map_imports),
        "runtime_enum_imports": sorted(acc.runtime_enum_imports),
        "error_imports": sorted(acc.error_imports),
        "rounding_imports": sorted(acc.rounding_imports),
        "needs_version": acc.needs_version,
        "lazy_class_imports": unique_lazy,
        "converter_fn_map": converter_fn_map,
        "converter_to_fn_map": converter_to_fn_map,
    }


# -----------------------------------------------------------------------
# Per-class import computation
# -----------------------------------------------------------------------


def _compute_node_class_imports(
    cls_ctx: dict,
    enum_contexts: list[dict],
    all_class_names: set[str],
    node_adapter,
    converter_fn_map: dict[str, str],
    converter_to_fn_map: dict[str, str],
) -> dict:
    """Compute import sets for one facade class .ts file."""
    acc = SimpleNamespace(
        type_imports_map={},
        value_imports_map={},
        converter_imports=set(),
        enum_map_imports=set(),
        runtime_enum_imports=set(),
        error_imports=set(),
        rounding_imports=set(),
        lazy_class_imports=[],
        needs_version=False,
    )

    # Build enum/VT lookup maps
    enum_tk_to_facade: dict[str, str] = {}
    enum_tk_to_map: dict[str, str] = {}
    for ectx in enum_contexts:
        enum_tk_to_facade[ectx["idl_name"]] = ectx.get("facade_class", "")
        enum_tk_to_map[ectx["idl_name"]] = f"{ectx['map_name']}_TO_C"

    _scan_node_properties(cls_ctx, acc, enum_contexts, all_class_names, node_adapter, converter_fn_map, converter_to_fn_map)
    _scan_node_collections(cls_ctx, acc, all_class_names)
    _scan_node_builders(cls_ctx, acc, all_class_names, enum_tk_to_facade, enum_tk_to_map, converter_to_fn_map)
    _scan_node_lifecycle(cls_ctx, acc, all_class_names, enum_tk_to_facade, enum_tk_to_map, converter_to_fn_map)
    _scan_node_init(cls_ctx, acc, all_class_names, enum_tk_to_facade, enum_tk_to_map, converter_to_fn_map)
    _scan_node_interfaces(cls_ctx, acc, all_class_names)

    return _finalize_node_imports(acc, converter_fn_map, converter_to_fn_map)
