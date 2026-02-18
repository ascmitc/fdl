"""
Python code generator: produces ctypes FFI bindings and idiomatic facade classes.

This module contains all Python-specific type maps, context builders, and
rendering logic. Language-neutral context builders live in shared_context.py;
Python-specific ones live in python_context.py.
"""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .python_context import (
    build_constants_enum_context,
    build_converter_context,
    build_facade_class_context,
    build_free_function_context,
    build_value_type_context,
)
from .shared_context import (
    build_enum_context,
)
from .fdl_idl import IDL, Function, ValueType, build_ir

# -----------------------------------------------------------------------
# C type → ctypes type mapping
# -----------------------------------------------------------------------

_C_TO_CTYPES: dict[str, str] = {
    "void": "None",
    "int": "ctypes.c_int",
    "int64_t": "ctypes.c_int64",
    "uint32_t": "ctypes.c_uint32",
    "double": "ctypes.c_double",
    "size_t": "ctypes.c_size_t",
    "char*": "ctypes.c_char_p",
    "const char*": "ctypes.c_char_p",
    "void*": "ctypes.c_void_p",
}


def _resolve_ctypes_type(c_type: str, idl: IDL, *, caller_frees: bool = False) -> str:
    """Map a C type string to its ctypes equivalent.

    If caller_frees is True and the type is char*, use c_void_p instead of
    c_char_p so the raw pointer is preserved for freeing with fdl_free().
    """
    # For caller-owned strings, we must return c_void_p to keep the pointer
    if caller_frees and c_type in ("char*", "const char*"):
        return "ctypes.c_void_p"

    # Direct scalar mapping
    if c_type in _C_TO_CTYPES:
        return _C_TO_CTYPES[c_type]

    # Pointer to opaque type → c_void_p
    stripped = c_type.replace("const ", "").replace("*", "").strip()
    if stripped in idl.opaque_types:
        return "ctypes.c_void_p"

    # Pointer to value type → ctypes.POINTER(Struct)
    for vt in idl.value_types:
        if stripped == vt.name:
            if "*" in c_type:
                return f"ctypes.POINTER({vt.name})"
            return vt.name

    # Enum types → uint32_t
    for e in idl.enums:
        if c_type == e.name:
            return _C_TO_CTYPES[e.underlying]

    # Fallback
    return f"ctypes.c_void_p  # UNKNOWN: {c_type}"


def _resolve_field_ctypes_type(c_type: str, idl: IDL, *, caller_frees: bool = False) -> str:
    """Map a C struct field type to its ctypes equivalent for _fields_."""
    # For caller-owned strings, use c_void_p to preserve the raw pointer for freeing
    if caller_frees and c_type in ("char*", "const char*"):
        return "ctypes.c_void_p"

    # Direct scalar mapping
    if c_type in _C_TO_CTYPES:
        return _C_TO_CTYPES[c_type]

    # Check if it's a value type (embedded struct)
    for vt in idl.value_types:
        if c_type == vt.name:
            return vt.name

    # Pointer types
    stripped = c_type.replace("const ", "").replace("*", "").strip()
    if stripped in idl.opaque_types:
        return "ctypes.c_void_p"

    for vt in idl.value_types:
        if stripped == vt.name and "*" in c_type:
            return f"ctypes.POINTER({vt.name})"

    # Enum types
    for e in idl.enums:
        if c_type == e.name:
            return _C_TO_CTYPES[e.underlying]

    return f"ctypes.c_void_p  # UNKNOWN: {c_type}"


# -----------------------------------------------------------------------
# Template context builders (FFI-specific)
# -----------------------------------------------------------------------


def _build_struct_context(vt: ValueType, idl: IDL) -> dict:
    fields = []
    for f in vt.fields:
        is_caller_frees = f.ownership is not None and "caller_frees" in f.ownership
        fields.append(
            {
                "name": f.name,
                "ctypes_type": _resolve_field_ctypes_type(f.c_type, idl, caller_frees=is_caller_frees),
            }
        )
    return {"name": vt.name, "fields": fields}


def _build_function_context(fn: Function, idl: IDL) -> dict:
    argtypes = []
    for p in fn.params:
        argtypes.append(_resolve_ctypes_type(p.c_type, idl))

    is_caller_frees = fn.ownership is not None and "caller_frees" in fn.ownership
    restype = _resolve_ctypes_type(fn.returns, idl, caller_frees=is_caller_frees)

    return {
        "name": fn.name,
        "doc": fn.doc,
        "argtypes_str": ", ".join(argtypes),
        "restype_str": restype,
    }


# -----------------------------------------------------------------------
# Per-class facade helpers
# -----------------------------------------------------------------------


def _class_to_module(class_name: str) -> str:
    """Map a facade class name to its per-class module (e.g. FDL → fdl, CanvasTemplate → canvas_template)."""
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", class_name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _add_lazy_imports(cls_ctx: dict, all_class_names: set[str]) -> None:
    """Add lazy import annotations to class context for cross-class references.

    Lazy imports are needed to break circular dependencies between per-class modules.
    They are only needed where a peer class is referenced *at runtime* (not just in
    type annotations, which are deferred by ``from __future__ import annotations``).
    """
    current_class = cls_ctx["name"]

    # Collections — item_cls is a runtime class reference
    for coll in cls_ctx["collections"]:
        item_class = coll["item_class"]
        if item_class in all_class_names and item_class != current_class:
            coll["lazy_import"] = {"module": _class_to_module(item_class), "cls": item_class}
        else:
            coll["lazy_import"] = None

    # Builders — return type's ._from_handle is called at runtime
    for builder in cls_ctx["builders"]:
        returns = builder["returns"]
        if returns in all_class_names and returns != current_class:
            builder["lazy_import"] = {"module": _class_to_module(returns), "cls": returns}
        else:
            builder["lazy_import"] = None

    # Init — depth > 0 classes need FDL for backing document
    init = cls_ctx.get("init")
    if init and init.get("depth", 0) > 0 and current_class != "FDL":
        init["lazy_imports"] = [{"module": _class_to_module("FDL"), "cls": "FDL"}]
    elif init:
        init["lazy_imports"] = []

    # Handle_ref properties — the getter calls HandleClass._from_handle() at runtime
    # (the lazy import is emitted inline in the template, not as a module-level import,
    #  so we don't need to add anything here — but we do need TYPE_CHECKING imports
    #  for the type annotations on setters, which _compute_per_class_imports handles)

    # Lifecycle methods — result_struct_multi wrap_class references
    for method in cls_ctx.get("lifecycle", []):
        lazy: list[dict] = []
        error = method.get("error")
        if error and error.get("result_fields"):
            for rf in error["result_fields"]:
                wc = rf.get("wrap_class")
                if wc and wc in all_class_names and wc != current_class:
                    entry = {"module": _class_to_module(wc), "cls": wc}
                    if entry not in lazy:
                        lazy.append(entry)
        method["lazy_imports"] = lazy


def _compute_per_class_imports(
    cls_ctx: dict,
    enum_contexts: list[dict],
    generated_converter_names: set[str],
    all_class_names: set[str],
    dataclass_name_set: set[str],
) -> dict:
    """Compute the import requirements for a single facade class file."""
    all_enum_classes = {ec["facade_class"] for ec in enum_contexts}

    # Sets for tracking
    types_set = {"DimensionsInt", "DimensionsFloat", "PointFloat", "Rect"}
    rounding_set = {"RoundStrategy"}

    current_class = cls_ctx["name"]

    base_imports: set[str] = set()
    base_imports.add("OwnedHandle" if cls_ctx["owns_handle"] else "HandleWrapper")
    base_imports.add("_decode_str")
    if cls_ctx["collections"]:
        base_imports.add("CollectionWrapper")

    getter_converters: set[str] = set()
    setter_converters: set[str] = set()
    used_enum_from_c: set[str] = set()
    used_enum_to_c: set[str] = set()
    type_check_enum_classes: set[str] = set()
    runtime_enum_classes: set[str] = set()
    type_check_class_names: set[str] = set()
    type_names: set[str] = set()
    rounding_names: set[str] = set()

    def _scan_type(py_type_str: str) -> None:
        """Classify a Python type annotation string for import tracking."""
        clean = py_type_str.replace(" | None", "")
        if clean in types_set:
            type_names.add(clean)
        elif clean in rounding_set:
            rounding_names.add(clean)
        elif clean in all_enum_classes:
            type_check_enum_classes.add(clean)
        elif clean in all_class_names and clean != current_class:
            type_check_class_names.add(clean)

    def _scan_c_args(c_args: list[str]) -> None:
        """Scan C args for enum TO_C map usage and reverse converter usage."""
        for c_arg in c_args:
            for ec in enum_contexts:
                to_c_name = f"{ec['map_name']}_TO_C"
                if to_c_name in c_arg:
                    used_enum_to_c.add(ec["map_name"])
            for conv_name in generated_converter_names:
                if f"_to_c_{conv_name}(" in c_arg:
                    setter_converters.add(conv_name)

    def _scan_params(params: list[dict]) -> None:
        """Scan method params for type imports and enum defaults."""
        for p in params:
            _scan_type(p["python_type"])
            default = p.get("default")
            if default:
                for enum_cls in all_enum_classes:
                    if enum_cls in str(default):
                        runtime_enum_classes.add(enum_cls)

    # Scan collection item classes and builder returns for TYPE_CHECKING
    for coll in cls_ctx["collections"]:
        item_class = coll["item_class"]
        if item_class in all_class_names and item_class != current_class:
            type_check_class_names.add(item_class)
    for builder in cls_ctx["builders"]:
        returns = builder["returns"]
        if returns in all_class_names and returns != current_class:
            type_check_class_names.add(returns)

    # Scan properties
    for prop in cls_ctx["properties"]:
        getter_converters.add(prop["converter"])
        if prop["enum_from_c"]:
            used_enum_from_c.add(prop["enum_from_c"].removesuffix("_FROM_C"))
        if prop["setter_fn"]:
            setter_converters.add(prop["converter"])
            if prop["enum_to_c"]:
                used_enum_to_c.add(prop["enum_to_c"].removesuffix("_TO_C"))
        _scan_type(prop["python_type"])

    # Scan builders and lifecycle
    for method_list_key in ("builders", "lifecycle"):
        for method_ctx in cls_ctx.get(method_list_key, []):
            _scan_c_args(method_ctx.get("c_args", []))
            _scan_params(method_ctx.get("params", []))
            # Scan result_fields for converters
            error = method_ctx.get("error")
            if error and error.get("result_fields"):
                for rf in error["result_fields"]:
                    if rf.get("converter"):
                        getter_converters.add(rf["converter"])
            # Scan instance_getter return type converters
            if method_ctx.get("converter_fn"):
                conv_name = method_ctx["converter_fn"].lstrip("_")
                getter_converters.add(conv_name)
            if method_ctx.get("returns"):
                _scan_type(method_ctx["returns"])

    # Scan init
    init_ctx = cls_ctx.get("init")
    if init_ctx:
        _scan_c_args(init_ctx.get("builder_c_args", []))
        _scan_params(init_ctx.get("params", []))

    # Determine base helpers needed
    if "string" in setter_converters:
        base_imports.add("_encode_str")
    if "json_value" in getter_converters:
        base_imports.add("_decode_str_free")

    # Build converter imports
    forward = sorted(getter_converters & generated_converter_names)
    reverse = sorted(setter_converters & generated_converter_names)
    converter_imports = [f"_{n}" for n in forward] + [f"_to_c_{n}" for n in reverse]

    # Build enum map imports
    enum_map_imports: list[str] = []
    for ec in enum_contexts:
        if ec["map_name"] in used_enum_from_c:
            enum_map_imports.append(f"{ec['map_name']}_FROM_C")
    for ec in enum_contexts:
        if ec["map_name"] in used_enum_to_c:
            enum_map_imports.append(f"{ec['map_name']}_TO_C")

    # Version / JSON checks
    needs_version = any(lc.get("kind") == "composite_property" and lc.get("returns") == "Version" for lc in cls_ctx.get("lifecycle", []))
    has_handle_ref_setter = any(p["converter"] == "handle_ref" and p.get("setter_fn") for p in cls_ctx["properties"])
    needs_json = bool(cls_ctx.get("to_json_fn")) or "json_value" in getter_converters or has_handle_ref_setter

    # ctypes is used by: to_json (string_at), lifecycle errors (string_at),
    # composite_property (string_at), struct-returning getters (byref)
    has_struct_getters = "struct" in getter_converters
    has_lifecycle_errors = any(lc.get("error") for lc in cls_ctx.get("lifecycle", []))
    has_composite = any(lc.get("kind") == "composite_property" for lc in cls_ctx.get("lifecycle", []))
    needs_ctypes = bool(cls_ctx.get("to_json_fn")) or has_struct_getters or has_lifecycle_errors or has_composite

    # Dataclass imports
    dataclass_imports = sorted({lc["returns"] for lc in cls_ctx.get("lifecycle", []) if lc.get("returns") in dataclass_name_set})

    type_check_enums = sorted(type_check_enum_classes - runtime_enum_classes)
    runtime_enums = sorted(runtime_enum_classes)

    type_check_classes = [{"module": _class_to_module(name), "cls": name} for name in sorted(type_check_class_names)]

    return {
        "base_imports": sorted(base_imports),
        "type_imports": sorted(type_names),
        "rounding_imports": sorted(rounding_names),
        "converter_imports": sorted(converter_imports),
        "enum_map_imports": sorted(enum_map_imports),
        "needs_json": needs_json,
        "needs_ctypes": needs_ctypes,
        "needs_version": needs_version,
        "dataclass_imports": dataclass_imports,
        "runtime_enums": runtime_enums,
        "type_check_enums": type_check_enums,
        "type_check_classes": type_check_classes,
    }


# -----------------------------------------------------------------------
# Generation
# -----------------------------------------------------------------------

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _make_env() -> Environment:
    """Create a Jinja2 environment pointing at the templates directory."""
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _generate_custom_attr_ffi(idl: IDL) -> list[dict]:
    """Generate FFI function contexts for custom attribute functions.

    For each handle type with custom_attrs=True, generates 13 function
    declarations matching the C ABI macro expansion.
    """
    # Template: (suffix, argtypes, restype)
    _CA_FUNCTIONS = [
        ("set_custom_attr_string", "ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p", "ctypes.c_int"),
        ("set_custom_attr_int", "ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64", "ctypes.c_int"),
        ("set_custom_attr_float", "ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double", "ctypes.c_int"),
        ("set_custom_attr_bool", "ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int", "ctypes.c_int"),
        ("get_custom_attr_string", "ctypes.c_void_p, ctypes.c_char_p", "ctypes.c_char_p"),
        ("get_custom_attr_int", "ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)", "ctypes.c_int"),
        ("get_custom_attr_float", "ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)", "ctypes.c_int"),
        ("get_custom_attr_bool", "ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)", "ctypes.c_int"),
        ("has_custom_attr", "ctypes.c_void_p, ctypes.c_char_p", "ctypes.c_int"),
        ("get_custom_attr_type", "ctypes.c_void_p, ctypes.c_char_p", "ctypes.c_uint32"),
        ("remove_custom_attr", "ctypes.c_void_p, ctypes.c_char_p", "ctypes.c_int"),
        ("custom_attrs_count", "ctypes.c_void_p", "ctypes.c_uint32"),
        ("custom_attr_name_at", "ctypes.c_void_p, ctypes.c_uint32", "ctypes.c_char_p"),
        ("set_custom_attr_point_f64", "ctypes.c_void_p, ctypes.c_char_p, fdl_point_f64_t", "ctypes.c_int"),
        ("get_custom_attr_point_f64", "ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_point_f64_t)", "ctypes.c_int"),
        ("set_custom_attr_dims_f64", "ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_f64_t", "ctypes.c_int"),
        ("get_custom_attr_dims_f64", "ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_f64_t)", "ctypes.c_int"),
        ("set_custom_attr_dims_i64", "ctypes.c_void_p, ctypes.c_char_p, fdl_dimensions_i64_t", "ctypes.c_int"),
        ("get_custom_attr_dims_i64", "ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(fdl_dimensions_i64_t)", "ctypes.c_int"),
    ]

    contexts = []
    for cls in idl.object_model.classes:
        if not cls.custom_attrs:
            continue
        prefix = cls.c_handle.removesuffix("t")  # fdl_doc_t → fdl_doc_
        for suffix, argtypes, restype in _CA_FUNCTIONS:
            fn_name = f"{prefix}{suffix}"
            contexts.append(
                {
                    "name": fn_name,
                    "doc": f"Custom attr: {suffix} on {cls.name}",
                    "argtypes_str": argtypes,
                    "restype_str": restype,
                }
            )
    return contexts


def generate_ffi(idl: IDL, output_dir: Path) -> None:
    """Generate low-level Python ctypes binding files (_enums, _structs, _functions)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    env = _make_env()

    # --- _enums.py ---
    tmpl = env.get_template("python/enums.py.j2")
    enums_src = tmpl.render(enums=idl.enums)
    (output_dir / "_enums.py").write_text(encoding="utf-8", data=enums_src)

    # --- _structs.py ---
    tmpl = env.get_template("python/structs.py.j2")
    struct_contexts = [_build_struct_context(vt, idl) for vt in idl.value_types]
    structs_src = tmpl.render(value_types=struct_contexts)
    (output_dir / "_structs.py").write_text(encoding="utf-8", data=structs_src)

    # --- _functions.py ---
    tmpl = env.get_template("python/ffi.py.j2")
    fn_contexts = [_build_function_context(fn, idl) for fn in idl.functions]
    # Add programmatically-generated custom attr FFI declarations
    fn_contexts.extend(_generate_custom_attr_ffi(idl))
    # Only import struct types that are actually referenced in function signatures
    all_vt_names = {vt.name for vt in idl.value_types}
    used_vt_names: set[str] = set()
    for ctx in fn_contexts:
        for token in (ctx["argtypes_str"] + " " + ctx["restype_str"]).split():
            clean = token.strip("(),")
            if clean in all_vt_names:
                used_vt_names.add(clean)
    vt_contexts = sorted([{"name": n} for n in used_vt_names], key=lambda x: x["name"])
    functions_src = tmpl.render(functions=fn_contexts, value_types=vt_contexts)
    (output_dir / "_functions.py").write_text(encoding="utf-8", data=functions_src)

    print(f"Generated {len(idl.enums)} enums, {len(idl.value_types)} structs, {len(idl.functions)} functions")
    print(f"Output: {output_dir}")


def generate_facade(idl: IDL, output_dir: Path) -> None:
    """Generate idiomatic Python facade classes from the IDL object model."""
    ir = build_ir(idl)
    output_dir.mkdir(parents=True, exist_ok=True)
    env = _make_env()

    # --- Build enum contexts (only enums with facade metadata) ---
    enum_contexts = []
    for enum in idl.enums:
        if enum.facade_class:
            enum_contexts.append(build_enum_context(enum))

    # --- _constants.py (standalone StrEnums) ---
    constants_contexts = []
    for enum in idl.enums:
        if enum.facade_class:
            constants_contexts.append(build_constants_enum_context(enum))
    tmpl = env.get_template("python/constants.py.j2")
    constants_src = tmpl.render(enums=constants_contexts)
    (output_dir / "constants.py").write_text(encoding="utf-8", data=constants_src)

    # --- Build all value type contexts, then split types vs rounding ---
    all_vt_contexts = []
    for vt in idl.value_types:
        if vt.facade_class:
            all_vt_contexts.append(build_value_type_context(vt, idl))

    types_vt_contexts = [ctx for ctx in all_vt_contexts if ctx["python_class"] != "RoundStrategy"]
    rounding_vt_contexts = [ctx for ctx in all_vt_contexts if ctx["python_class"] == "RoundStrategy"]

    # --- fdl_types.py (DimensionsInt, DimensionsFloat, PointFloat — no RoundStrategy) ---
    all_types_enum_imports: set[str] = set()
    for ctx in types_vt_contexts:
        all_types_enum_imports.update(ctx["enum_imports"])
    tmpl = env.get_template("python/types.py.j2")
    types_src = tmpl.render(value_types=types_vt_contexts, enum_imports=sorted(all_types_enum_imports))
    (output_dir / "fdl_types.py").write_text(encoding="utf-8", data=types_src)

    # --- _converters.py (C struct ↔ Python value type converters) ---
    converter_contexts = []
    all_converter_enum_imports: set[str] = set()
    generated_converter_names: set[str] = set()
    for vt in idl.value_types:
        if vt.facade_converter:
            ctx = build_converter_context(vt, idl)
            converter_contexts.append(ctx)
            all_converter_enum_imports.update(ctx["enum_class_imports"])
            generated_converter_names.add(vt.facade_converter)

    # Split converter type imports: _types vs _rounding
    types_converter_imports = sorted(ctx["python_class"] for ctx in converter_contexts if ctx["python_class"] != "RoundStrategy")
    rounding_converter_imports = sorted(ctx["python_class"] for ctx in converter_contexts if ctx["python_class"] == "RoundStrategy")
    tmpl = env.get_template("python/converters.py.j2")
    converters_src = tmpl.render(
        value_types=converter_contexts,
        types_imports=types_converter_imports,
        rounding_imports=rounding_converter_imports,
        enum_class_imports=sorted(all_converter_enum_imports),
    )
    (output_dir / "converters.py").write_text(encoding="utf-8", data=converters_src)

    # --- _enum_maps.py ---
    tmpl = env.get_template("python/enum_maps.py.j2")
    enum_maps_src = tmpl.render(enums=enum_contexts)
    (output_dir / "enum_maps.py").write_text(encoding="utf-8", data=enum_maps_src)

    # --- Build class contexts ---
    ir_class_by_name = {cls.name: cls for cls in ir.classes}
    class_contexts = [build_facade_class_context(cls, idl, enum_contexts, ir_class_by_name) for cls in ir.classes]
    all_class_names = {cls_ctx["name"] for cls_ctx in class_contexts}

    # Add lazy import annotations for cross-class references
    for cls_ctx in class_contexts:
        _add_lazy_imports(cls_ctx, all_class_names)

    # --- _errors.py (from auxiliary_types) ---
    aux = idl.auxiliary_types
    error_class_names: list[str] = []
    if aux.errors:
        error_contexts = [{"name": e.name, "parent": e.parent, "doc": e.doc} for e in aux.errors]
        tmpl = env.get_template("python/errors.py.j2")
        errors_src = tmpl.render(errors=error_contexts)
        (output_dir / "errors.py").write_text(encoding="utf-8", data=errors_src)
        error_class_names = [e.name for e in aux.errors]

    # --- _header.py (from auxiliary_types) ---
    version_class_name: str | None = None
    if aux.version:
        v = aux.version
        slot_names = ", ".join(f'"{s.name}"' for s in v.slots)
        init_params = ", ".join(f"{s.name}: {s.slot_type} = {s.default}" for s in v.slots)
        eq_parts = [f"self.{s.name} == other.{s.name}" for s in v.slots]
        eq_expr = " and ".join(eq_parts)
        repr_format = v.class_name + "(" + ", ".join(f"{s.name}={{self.{s.name}!r}}" for s in v.slots) + ")"
        tmpl = env.get_template("python/header.py.j2")
        version_src = tmpl.render(
            class_name=v.class_name,
            doc=v.doc,
            slots=v.slots,
            slot_names=slot_names,
            init_params=init_params,
            eq_expr=eq_expr,
            repr_format=repr_format,
        )
        (output_dir / "header.py").write_text(encoding="utf-8", data=version_src)
        version_class_name = v.class_name

    # --- Build dataclass contexts for inlining into class modules ---
    dataclass_names: list[str] = []
    dc_by_name: dict[str, dict] = {}
    if aux.dataclasses:
        builtins = {"object", "float", "int", "str", "bool", "bytes"}
        for dc in aux.dataclasses:
            fields = [{"name": f.name, "type": f.field_type, "private": f.private} for f in dc.fields]
            accessors = None
            if dc.accessors:
                accessors = []
                for acc in dc.accessors:
                    # Build the Python expression for the collection and lookup function
                    parts = acc.collection.split(".")
                    if parts[0] == "fdl":
                        on_expr = f"self.fdl.{parts[1]}"
                    else:
                        on_expr = f"self.{parts[0]}.{parts[1]}"
                    lookup_fn = f"find_{acc.lookup}"
                    accessors.append(
                        {
                            "name": acc.name,
                            "returns": acc.returns,
                            "doc": acc.doc,
                            "lookup_fn": lookup_fn,
                            "on_expr": on_expr,
                            "key_field": acc.key_field,
                        }
                    )
            dc_by_name[dc.class_name] = {
                "class_name": dc.class_name,
                "doc": dc.doc,
                "fields": fields,
                "accessors": accessors,
            }
            dataclass_names.append(dc.class_name)

    # --- Free functions (split by module: rounding vs utils) ---
    # Skip free functions whose return types lack Python facade mappings
    # (these are hand-coded in the template instead)
    _PYTHON_SKIP_FF = {"abi_version", "compute_framing_from_intent"}
    ff_contexts = [build_free_function_context(ff, idl) for ff in idl.free_functions if ff.display_name not in _PYTHON_SKIP_FF]
    ff_defs = [ff for ff in idl.free_functions if ff.display_name not in _PYTHON_SKIP_FF]
    # Tag each context with its module
    for ff, ctx in zip(ff_defs, ff_contexts):
        ctx["module"] = ff.module
    # Build converter lookup for value type returns
    vt_converter_map: dict[str, str] = {}
    for vt in idl.value_types:
        if vt.facade_converter:
            vt_converter_map[vt.facade_class] = f"_{vt.facade_converter}"
    # Compute param signatures and return lines
    for ctx in ff_contexts:
        ctx["param_sig"] = ", ".join(f"{p['name']}: {p['python_type']}" for p in ctx["params"])
        c_args_str = ", ".join(ctx["c_call_args"])
        call_expr = f"get_lib().{ctx['c_function']}({c_args_str})"
        converter_fn = vt_converter_map.get(ctx["python_return"])
        if converter_fn:
            ctx["needed_converters"] = [converter_fn]
            ret_line = f"return {converter_fn}({call_expr})"
        else:
            ctx["needed_converters"] = []
            ret_line = f"return {ctx['python_return']}({call_expr})"
        if len(f"    {ret_line}") > 140:
            wrap = converter_fn or ctx["python_return"]
            ret_line = f"_r = {call_expr}\n    return {wrap}(_r)"
        ctx["return_line"] = ret_line

    # Split by module
    rounding_ff_contexts = [ctx for ctx in ff_contexts if ctx["module"] == "rounding"]
    utils_ff_contexts = [ctx for ctx in ff_contexts if ctx["module"] == "utils"]

    # --- rounding.py (RoundStrategy class + rounding free functions) ---
    # Collect type imports needed by rounding free functions
    ff_type_imports: set[str] = set()
    builtins = {"int", "float", "str", "bool", "None"}
    for ctx in rounding_ff_contexts:
        for p in ctx["params"]:
            if p["python_type"] not in builtins:
                ff_type_imports.add(p["python_type"])
        if ctx["python_return"] not in builtins:
            ff_type_imports.add(ctx["python_return"])

    # Collect enum imports needed by RoundStrategy
    rs_enum_imports: set[str] = set()
    for ctx in rounding_vt_contexts:
        rs_enum_imports.update(ctx["enum_imports"])

    rs_ctx = rounding_vt_contexts[0] if rounding_vt_contexts else None
    tmpl = env.get_template("python/rounding.py.j2")
    rounding_src = tmpl.render(
        round_strategy=rs_ctx,
        free_functions=rounding_ff_contexts,
        type_imports=sorted(ff_type_imports),
        enum_imports=sorted(rs_enum_imports),
    )
    (output_dir / "rounding.py").write_text(encoding="utf-8", data=rounding_src)
    rounding_ff_names = sorted(ctx["display_name"] for ctx in rounding_ff_contexts)
    rounding_vt_names = sorted(ctx["python_class"] for ctx in rounding_vt_contexts)

    # --- utils.py (generated from template) ---
    utility_names = sorted(u.name for u in idl.utilities)
    utils_ff_names = sorted(ctx["display_name"] for ctx in utils_ff_contexts)
    # Include hand-coded utils functions (skipped from codegen but defined in template)
    _HANDCODED_UTILS = {"abi_version", "compute_framing_from_intent", "FramingFromIntentResult"}
    utility_names = sorted(set(utility_names) | set(utils_ff_names) | _HANDCODED_UTILS)
    c_abi_utils = [u for u in idl.utilities if u.kind == "c_abi"]
    # Collect extra type imports needed by utils free functions (beyond DimensionsFloat/PointFloat)
    utils_extra_types: set[str] = set()
    base_utils_types = {"DimensionsFloat", "PointFloat"}
    for ctx in utils_ff_contexts:
        for p in ctx["params"]:
            if p["python_type"] not in builtins and p["python_type"] not in base_utils_types:
                utils_extra_types.add(p["python_type"])
        if ctx["python_return"] not in builtins and ctx["python_return"] not in base_utils_types:
            utils_extra_types.add(ctx["python_return"])
    utils_tmpl = env.get_template("python/utils.py.j2")
    utils_src = utils_tmpl.render(
        utility_names=utility_names,
        c_abi_utils=c_abi_utils,
        free_functions=utils_ff_contexts,
        utils_type_imports=sorted(utils_extra_types),
    )
    (output_dir / "utils.py").write_text(encoding="utf-8", data=utils_src)

    # --- _custom_attrs.py (shared custom attribute helpers) ---
    has_custom_attrs = any(cls_ctx.get("custom_attrs") for cls_ctx in class_contexts)
    if has_custom_attrs:
        ca_tmpl = env.get_template("python/custom_attrs.py.j2")
        ca_src = ca_tmpl.render()
        (output_dir / "_custom_attrs.py").write_text(encoding="utf-8", data=ca_src)

    # --- Per-class facade files ---
    dataclass_name_set = set(dataclass_names)
    dc_name_to_module: dict[str, str] = {}
    tmpl = env.get_template("python/class.py.j2")
    for cls_ctx in class_contexts:
        imports = _compute_per_class_imports(
            cls_ctx,
            enum_contexts,
            generated_converter_names,
            all_class_names,
            dataclass_name_set,
        )
        module_name = _class_to_module(cls_ctx["name"])
        # Attach inline dataclass contexts for classes that need them
        inline_dcs = [dc_by_name[name] for name in imports["dataclass_imports"] if name in dc_by_name]
        cls_ctx["inline_dataclasses"] = inline_dcs
        for dc in inline_dcs:
            dc_name_to_module[dc["class_name"]] = module_name
            # Ensure dataclass field types are included in type_imports
            types_set = {"DimensionsInt", "DimensionsFloat", "PointFloat", "Rect"}
            for field in dc["fields"]:
                if field["type"] in types_set and field["type"] not in imports["type_imports"]:
                    imports["type_imports"] = sorted(set(imports["type_imports"]) | {field["type"]})
        # Ensure composite types are imported for custom attribute annotations
        if cls_ctx.get("custom_attrs"):
            ca_types = {"DimensionsFloat", "DimensionsInt", "PointFloat"}
            missing = ca_types - set(imports["type_imports"])
            if missing:
                imports["type_imports"] = sorted(set(imports["type_imports"]) | missing)
        cls_src = tmpl.render(cls=cls_ctx, imports=imports)
        (output_dir / f"{module_name}.py").write_text(encoding="utf-8", data=cls_src)

    # --- __init__.py ---
    class_names = sorted(
        [cls.name for cls in ir.classes],
        key=lambda n: (not n.isupper(), n.casefold()),
    )
    enum_class_names = sorted(ec["python_class"] for ec in constants_contexts)
    vt_class_names = sorted(vc["python_class"] for vc in types_vt_contexts)

    init_lines = [
        "# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers",
        "# SPDX-License-Identifier: Apache-2.0",
        "# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT",
        '"""fdl — handle-backed Python facade for libfdl_core."""',
        "# ruff: noqa: I001",
        "",
    ]
    # Import facade classes from per-class modules
    for name in class_names:
        module = _class_to_module(name)
        init_lines.append(f"from .{module} import {name}  # noqa: F401")

    # Export enums from constants
    init_lines.append("from .constants import (  # noqa: F401")
    for name in enum_class_names:
        init_lines.append(f"    {name},")
    # First-class custom attribute name constants
    for name in ["ATTR_CONTENT_TRANSLATION", "ATTR_SCALE_FACTOR", "ATTR_SCALED_BOUNDING_BOX"]:
        init_lines.append(f"    {name},")
    init_lines.append(")")

    # Export dataclasses (from their containing class modules)
    for name in sorted(dataclass_names):
        module = dc_name_to_module.get(name)
        if module:
            init_lines.append(f"from .{module} import {name}  # noqa: F401")

    # Export errors
    if error_class_names:
        init_lines.append("from .errors import (  # noqa: F401")
        for name in error_class_names:
            init_lines.append(f"    {name},")
        init_lines.append(")")

    # Export rounding (RoundStrategy + rounding free functions)
    rounding_exports = sorted(rounding_vt_names + rounding_ff_names)
    if rounding_exports:
        init_lines.append("from .rounding import (  # noqa: F401")
        for name in rounding_exports:
            init_lines.append(f"    {name},")
        init_lines.append(")")

    # Export value types from fdl_types
    init_lines.append("from .fdl_types import (  # noqa: F401")
    for name in vt_class_names:
        init_lines.append(f"    {name},")
    init_lines.append(")")

    # Export utilities (driven by IDL utilities section)
    if utility_names:
        init_lines.append("from .utils import (  # noqa: F401")
        for name in utility_names:
            init_lines.append(f"    {name},")
        init_lines.append(")")

    # Export Version from _header
    if version_class_name:
        init_lines.append(f"from .header import {version_class_name}  # noqa: F401")

    init_lines.append("")
    (output_dir / "__init__.py").write_text(encoding="utf-8", data="\n".join(init_lines))

    print(
        f"Generated {len(class_contexts)} facade classes, {len(enum_contexts)} enum maps, "
        f"{len(constants_contexts)} constants, {len(types_vt_contexts) + len(rounding_vt_contexts)} value types"
    )
    print(f"Output: {output_dir}")
