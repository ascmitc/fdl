# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
WebAssembly code generator: produces Embind C++ bindings (bindings.cpp) from the IDL.

The Embind output exposes every C ABI function from fdl_core.h to JavaScript
with names matching the C function names exactly.  This lets the generated
TypeScript facade call the WASM module the same way it calls the N-API addon
(via the shared ``NativeAddon`` interface in ``ffi/index.ts``).

Handle representation:
    Opaque handles are passed across the JS/WASM boundary as plain JavaScript
    objects with a single ``__ptr`` field (a numeric WASM linear-memory address).
    This avoids Embind class lifetime management (no ``.delete()`` required)
    and matches the existing TypeScript ``_handle: object`` type in base.ts.

Struct representation:
    Value types (Dimensions, Point, Rect, etc.) cross the boundary as plain JS
    objects with the same property names as the N-API path produces (matching
    ``structs.h``).  Helper functions ``from_val_*`` / ``to_val_*`` convert
    between ``emscripten::val`` and the C structs.
"""

from __future__ import annotations

from pathlib import Path

from .fdl_idl import IDL, Function, FunctionParam, ValueType
from .node_gen import (
    _STRUCT_TYPES,
    _generate_custom_attr_functions,
    _struct_pascal_name,
)
from .shared_context import make_jinja_env


# Functions never invoked from the JavaScript facade. They take a result-type
# struct (by pointer) as input, which would trigger generation of an unsafe
# JS→C `from_val_*` helper (lifetime UB on the embedded `const char*` fields).
# The facade frees these results piece-by-piece instead (`fdl_doc_free` on
# `output_fdl`, `fdl_free` on the string fields), so dropping the binding has
# zero runtime impact.
_SKIP_FUNCTIONS: frozenset[str] = frozenset(
    {
        "fdl_template_result_free",
    }
)

# Structs that only ever appear as C→JS outputs (function returns or out-params)
# at the binding boundary. We skip emitting their `from_val_*` helpers entirely;
# the corresponding `to_val_*` is always emitted.
_OUTPUT_ONLY_STRUCTS: frozenset[str] = frozenset(
    {
        "fdl_parse_result_t",
        "fdl_template_result_t",
        "fdl_resolve_canvas_result_t",
    }
)


# -----------------------------------------------------------------------
# Parameter context builder (Embind variant)
# -----------------------------------------------------------------------


def _build_param_context(p: FunctionParam, idl: IDL) -> dict:
    """Build template-ready context for one JS-visible parameter.

    Every returned dict has: name, kind, c_type, decl, extract, call_arg.
      - decl: the C++ parameter declaration in the lambda signature
      - extract: optional statement(s) to run before the call
      - call_arg: the expression passed to the underlying C function
    """
    c_type = p.c_type
    stripped = c_type.replace("const ", "").replace("*", "").strip()

    # 1. Opaque handle pointers
    if c_type == "void*" or stripped in idl.opaque_types:
        ptr_type = c_type if c_type == "void*" else c_type.replace("const ", "").strip()
        return {
            "name": p.name,
            "kind": "handle",
            "c_type": ptr_type,
            "decl": f"emscripten::val {p.name}_v",
            "extract": f"auto* {p.name} = unwrap_handle<{ptr_type.rstrip('*').strip()}>({p.name}_v);",
            "call_arg": p.name,
        }

    # 2. Strings
    if c_type in ("const char*", "char*"):
        nullable = getattr(p, "nullable", False)
        if nullable:
            return {
                "name": p.name,
                "kind": "string_nullable",
                "c_type": c_type,
                "decl": f"emscripten::val {p.name}_v",
                "extract": (f"std::string {p.name}_buf;\n    const char* {p.name} = val_to_cstr_or_null({p.name}_v, {p.name}_buf);"),
                "call_arg": p.name,
            }
        return {
            "name": p.name,
            "kind": "string",
            "c_type": c_type,
            "decl": f"std::string {p.name}_str",
            "extract": None,
            "call_arg": f"{p.name}_str.c_str()",
        }

    # 3. Scalar numbers
    if c_type in ("int", "int64_t", "uint32_t", "double", "size_t"):
        # int64_t and size_t pass through double to avoid BigInt dependency.
        if c_type in ("int64_t", "size_t"):
            return {
                "name": p.name,
                "kind": "number",
                "c_type": c_type,
                "decl": f"double {p.name}_d",
                "extract": f"{c_type} {p.name} = static_cast<{c_type}>({p.name}_d);",
                "call_arg": p.name,
            }
        return {
            "name": p.name,
            "kind": "number",
            "c_type": c_type,
            "decl": f"{c_type} {p.name}",
            "extract": None,
            "call_arg": p.name,
        }

    # 4. Value-type structs (pass-by-value or pass-by-pointer)
    for vt in idl.value_types:
        if stripped == vt.name:
            pascal = _struct_pascal_name(vt.name)
            is_ptr = "*" in c_type
            return {
                "name": p.name,
                "kind": "struct_ptr" if is_ptr else "struct",
                "c_type": vt.name,
                "pascal_name": pascal,
                "decl": f"emscripten::val {p.name}_v",
                "extract": f"{vt.name} {p.name} = from_val_{pascal}({p.name}_v);",
                "call_arg": f"&{p.name}" if is_ptr else p.name,
            }

    # 5. Enums
    for e in idl.enums:
        if c_type == e.name:
            return {
                "name": p.name,
                "kind": "enum",
                "c_type": c_type,
                "decl": f"unsigned {p.name}_i",
                "extract": f"{c_type} {p.name} = static_cast<{c_type}>({p.name}_i);",
                "call_arg": p.name,
            }

    # Fallback
    return {
        "name": p.name,
        "kind": "unknown",
        "c_type": c_type,
        "decl": f"emscripten::val {p.name}_v /* UNKNOWN: {c_type} */",
        "extract": None,
        "call_arg": p.name,
    }


# -----------------------------------------------------------------------
# Return-type classifier
# -----------------------------------------------------------------------


def _classify_return(fn: Function, idl: IDL) -> dict:
    """Classify a function's return for Embind wrapping."""
    c_type = fn.returns
    is_caller_frees = fn.ownership is not None and "caller_frees" in fn.ownership

    if c_type == "void":
        return {"kind": "void", "c_type": "void"}

    if is_caller_frees and c_type in ("char*", "const char*"):
        return {"kind": "string_free", "c_type": c_type, "nullable": fn.nullable}

    if c_type in ("const char*", "char*"):
        return {"kind": "string", "c_type": c_type, "nullable": fn.nullable}

    if c_type in ("int", "int64_t", "uint32_t", "double", "size_t"):
        return {"kind": "number", "c_type": c_type}

    stripped = c_type.replace("const ", "").replace("*", "").strip()
    if stripped in idl.opaque_types:
        return {"kind": "handle", "c_type": c_type, "nullable": fn.nullable}

    for vt in idl.value_types:
        if c_type == vt.name:
            # Owned-string fields (ownership=caller_frees on a string field) need
            # explicit fdl_free() cleanup after the JS object is built, otherwise
            # the C-side malloc'd buffers leak. See the cleanup loop in
            # binding.cc.j2 / bindings.cpp.j2.
            owned_strings = [f.name for f in vt.fields if f.ownership == "caller_frees" and f.c_type in ("const char*", "char*")]
            return {
                "kind": "struct",
                "c_type": c_type,
                "pascal_name": _struct_pascal_name(vt.name),
                "owned_string_fields": owned_strings,
            }

    for e in idl.enums:
        if c_type == e.name:
            return {"kind": "enum", "c_type": c_type}

    return {"kind": "unknown", "c_type": c_type}


# -----------------------------------------------------------------------
# Function context builder
# -----------------------------------------------------------------------


def _build_function_context(fn: Function, idl: IDL) -> dict:
    """Build a flat template context for one C function's Embind binding."""
    params: list[dict] = []
    out_params: list[dict] = []
    call_args: list[str] = []

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
                    "is_number": base_type in ("int", "int64_t", "uint32_t", "double", "size_t"),
                }
            )
            call_args.append(f"&{p.name}")
        else:
            ctx = _build_param_context(p, idl)
            params.append(ctx)
            call_args.append(ctx["call_arg"])

    ret = _classify_return(fn, idl)
    is_free_fn = ret["kind"] == "void" and len(params) == 1 and params[0]["kind"] == "handle" and "free" in fn.name

    return {
        "name": fn.name,
        "doc": fn.doc or "",
        "params": params,
        "out_params": out_params,
        "has_out_params": bool(out_params),
        "call_args_str": ", ".join(call_args),
        "return": ret,
        "is_free_fn": is_free_fn,
    }


# -----------------------------------------------------------------------
# Struct helper context builder
# -----------------------------------------------------------------------


def _classify_struct_field_embind(c_type: str, name: str) -> dict:
    """Classify a struct field for from_val_* / to_val_* helpers.

    Mirrors _classify_struct_field from node_gen but emits emscripten::val
    code instead of Napi:: code.  All fields have: name, c_type, kind, to_c,
    to_js, is_nested (+ pascal_name when nested).
    """
    # Integer types (cast through double to avoid BigInt)
    if c_type in ("int", "int64_t", "uint32_t"):
        to_c = f'static_cast<{c_type}>(v["{name}"].as<double>())'
        to_js = f"emscripten::val(static_cast<double>(d.{name}))"
        return {"name": name, "c_type": c_type, "kind": "number", "to_c": to_c, "to_js": to_js, "is_nested": False}

    if c_type == "double":
        return {
            "name": name,
            "c_type": c_type,
            "kind": "number",
            "to_c": f'v["{name}"].as<double>()',
            "to_js": f"emscripten::val(d.{name})",
            "is_nested": False,
        }

    if c_type in ("char*", "const char*"):
        # NOTE: from_val_* is only generated for completeness; result-type structs
        # are output-only and never reconverted JS→C at runtime, so the lifetime
        # of the std::string temporary doesn't matter in practice. We mirror the
        # pattern used by the N-API path's structs.h so the code compiles.
        to_c_stmt = f'{{ std::string _s = v["{name}"].as<std::string>(); d.{name} = _s.c_str(); }}'
        return {
            "name": name,
            "c_type": c_type,
            "kind": "string",
            "to_c_stmt": to_c_stmt,
            "to_c": None,
            "to_js": f"(d.{name} ? emscripten::val(std::string(d.{name})) : emscripten::val::null())",
            "is_nested": False,
        }

    if c_type in _STRUCT_TYPES:
        pascal = _struct_pascal_name(c_type)
        return {
            "name": name,
            "c_type": c_type,
            "kind": "nested_struct",
            "pascal_name": pascal,
            "to_c": f'from_val_{pascal}(v["{name}"])',
            "to_js": f"to_val_{pascal}(d.{name})",
            "is_nested": True,
        }

    if c_type.endswith("*"):
        ptr_inner = c_type.rstrip("*").replace("const", "").strip()
        return {
            "name": name,
            "c_type": c_type,
            "kind": "handle",
            "to_c": f'unwrap_handle<{ptr_inner}>(v["{name}"])',
            "to_js": f"wrap_handle(d.{name})",
            "is_nested": False,
        }

    # Enum-like / other integral
    return {
        "name": name,
        "c_type": c_type,
        "kind": "enum",
        "to_c": f'static_cast<{c_type}>(v["{name}"].as<unsigned>())',
        "to_js": f"emscripten::val(static_cast<unsigned>(d.{name}))",
        "is_nested": False,
    }


def _build_struct_helpers_context(vt: ValueType) -> dict:
    pascal = _struct_pascal_name(vt.name)
    fields = [_classify_struct_field_embind(f.c_type, f.name) for f in vt.fields]
    return {"c_name": vt.name, "pascal_name": pascal, "fields": fields}


# -----------------------------------------------------------------------
# Generation entry point
# -----------------------------------------------------------------------


def generate_bindings(idl: IDL, output_dir: Path) -> None:
    """Generate Embind bindings.cpp for the WASM backend.

    Produces a single C++ file at ``output_dir / bindings.cpp`` that contains:
      - Handle wrap/unwrap helpers
      - from_val_* / to_val_* helpers for each value type used at the boundary
      - One ``emscripten::function`` registration per C ABI function
      - One ``emscripten::enum_`` registration per enum (purely informational)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    env = make_jinja_env()

    # All functions (IDL + synthesised custom-attr functions), minus the
    # blocklist of dead bindings (see _SKIP_FUNCTIONS above).
    all_fns = [fn for fn in list(idl.functions) + _generate_custom_attr_functions(idl) if fn.name not in _SKIP_FUNCTIONS]
    fn_contexts = [_build_function_context(fn, idl) for fn in all_fns]

    # Build struct helper contexts, filtered to those referenced.
    # We track input-uses (JS→C, needs `from_val_*`) separately from output-uses
    # (C→JS, needs `to_val_*`). The split lets us avoid emitting unsafe
    # `from_val_*` helpers for result structs that are never built from JS.
    all_struct_contexts = [_build_struct_helpers_context(vt) for vt in idl.value_types]

    used_as_input: set[str] = set()
    used_as_output: set[str] = set()
    for ctx in fn_contexts:
        for p in ctx["params"]:
            if p["kind"] in ("struct", "struct_ptr"):
                used_as_input.add(p["c_type"])
        if ctx["return"]["kind"] == "struct":
            used_as_output.add(ctx["return"]["c_type"])
        for op in ctx["out_params"]:
            if op["is_struct"]:
                used_as_output.add(op["base_type"])

    # Transitive nested deps: a struct used as output that nests another struct
    # propagates output-use to the nested type; ditto for input.
    def _propagate(seed: set[str]) -> set[str]:
        out = set(seed)
        changed = True
        while changed:
            changed = False
            for sc in all_struct_contexts:
                if sc["c_name"] in out:
                    for f in sc["fields"]:
                        if f["is_nested"] and f["c_type"] not in out:
                            out.add(f["c_type"])
                            changed = True
        return out

    used_as_output = _propagate(used_as_output)
    used_as_input = _propagate(used_as_input)
    # Force-skip from_val_* for output-only result structs even if some
    # function happens to reference them (defense in depth).
    used_as_input -= _OUTPUT_ONLY_STRUCTS

    used = used_as_input | used_as_output

    # Annotate each struct context with whether the JS→C helper should be emitted.
    for sc in all_struct_contexts:
        sc["emit_from_val"] = sc["c_name"] in used_as_input

    used_structs = [sc for sc in all_struct_contexts if sc["c_name"] in used]

    # Topological sort: leaves first
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

    tmpl = env.get_template("wasm/bindings.cpp.j2")
    (output_dir / "bindings.cpp").write_text(
        encoding="utf-8",
        data=tmpl.render(
            functions=fn_contexts,
            structs=sorted_structs,
        ),
    )

    print(f"Generated WASM Embind bindings: {len(fn_contexts)} function wrappers, {len(sorted_structs)} struct helpers")
    print(f"Output: {output_dir}")
