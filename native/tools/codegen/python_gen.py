"""
Python code generator: produces idiomatic facade classes and Pydantic models.

This module contains all Python-specific type maps, context builders, and
rendering logic. Language-neutral context builders live in shared_context.py;
Python-specific ones live in python_context.py.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

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
from .fdl_idl import IDL, build_ir

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


# -----------------------------------------------------------------------
# Import computation helpers
# -----------------------------------------------------------------------

_PY_TYPES_SET = frozenset({"DimensionsInt", "DimensionsFloat", "PointFloat", "Rect"})
_PY_ROUNDING_SET = frozenset({"RoundStrategy"})


def _py_scan_type(py_type_str, acc, all_enum_classes, all_class_names, current_class):
    """Classify a Python type annotation string for import tracking."""
    clean = py_type_str.replace(" | None", "")
    if clean in _PY_TYPES_SET:
        acc.type_names.add(clean)
    elif clean in _PY_ROUNDING_SET:
        acc.rounding_names.add(clean)
    elif clean in all_enum_classes:
        acc.type_check_enum_classes.add(clean)
    elif clean in all_class_names and clean != current_class:
        acc.type_check_class_names.add(clean)


def _py_scan_c_args(c_args, acc, enum_contexts, generated_converter_names):
    """Scan C args for enum TO_C map usage and reverse converter usage."""
    for c_arg in c_args:
        for ec in enum_contexts:
            to_c_name = f"{ec['map_name']}_TO_C"
            if to_c_name in c_arg:
                acc.used_enum_to_c.add(ec["map_name"])
        for conv_name in generated_converter_names:
            if f"_to_c_{conv_name}(" in c_arg:
                acc.setter_converters.add(conv_name)


def _py_scan_params(params, acc, all_enum_classes, all_class_names, current_class):
    """Scan method params for type imports and enum defaults."""
    for p in params:
        _py_scan_type(p["python_type"], acc, all_enum_classes, all_class_names, current_class)
        default = p.get("default")
        if default:
            for enum_cls in all_enum_classes:
                if enum_cls in str(default):
                    acc.runtime_enum_classes.add(enum_cls)


def _scan_py_collections(cls_ctx, acc, all_class_names, current_class):
    """Scan collection item classes and builder return types for TYPE_CHECKING imports."""
    for coll in cls_ctx["collections"]:
        item_class = coll["item_class"]
        if item_class in all_class_names and item_class != current_class:
            acc.type_check_class_names.add(item_class)
    for builder in cls_ctx["builders"]:
        returns = builder["returns"]
        if returns in all_class_names and returns != current_class:
            acc.type_check_class_names.add(returns)


def _scan_py_properties(cls_ctx, acc, all_enum_classes, all_class_names, current_class):
    """Scan properties for converter, enum, and type imports."""
    for prop in cls_ctx["properties"]:
        acc.getter_converters.add(prop["converter"])
        if prop["enum_from_c"]:
            acc.used_enum_from_c.add(prop["enum_from_c"].removesuffix("_FROM_C"))
        if prop["setter_fn"]:
            acc.setter_converters.add(prop["converter"])
            if prop["enum_to_c"]:
                acc.used_enum_to_c.add(prop["enum_to_c"].removesuffix("_TO_C"))
        _py_scan_type(prop["python_type"], acc, all_enum_classes, all_class_names, current_class)


def _scan_py_methods(cls_ctx, acc, all_enum_classes, all_class_names, current_class, enum_contexts, generated_converter_names):
    """Scan builders and lifecycle methods for imports."""
    for method_list_key in ("builders", "lifecycle"):
        for method_ctx in cls_ctx.get(method_list_key, []):
            _py_scan_c_args(method_ctx.get("c_args", []), acc, enum_contexts, generated_converter_names)
            _py_scan_params(method_ctx.get("params", []), acc, all_enum_classes, all_class_names, current_class)
            error = method_ctx.get("error")
            if error and error.get("result_fields"):
                for rf in error["result_fields"]:
                    if rf.get("converter"):
                        acc.getter_converters.add(rf["converter"])
            if method_ctx.get("converter_fn"):
                conv_name = method_ctx["converter_fn"].lstrip("_")
                acc.getter_converters.add(conv_name)
            if method_ctx.get("returns"):
                _py_scan_type(method_ctx["returns"], acc, all_enum_classes, all_class_names, current_class)


def _scan_py_init(cls_ctx, acc, all_enum_classes, all_class_names, current_class, enum_contexts, generated_converter_names):
    """Scan init context for imports."""
    init_ctx = cls_ctx.get("init")
    if init_ctx:
        _py_scan_c_args(init_ctx.get("builder_c_args", []), acc, enum_contexts, generated_converter_names)
        _py_scan_params(init_ctx.get("params", []), acc, all_enum_classes, all_class_names, current_class)


def _assemble_py_import_result(acc, cls_ctx, enum_contexts, generated_converter_names, dataclass_name_set):
    """Assemble the final import dict from accumulated state."""
    # Determine base helpers needed
    if "string" in acc.setter_converters:
        acc.base_imports.add("_encode_str")
    if "json_value" in acc.getter_converters:
        acc.base_imports.add("_decode_str_free")

    # Build converter imports
    forward = sorted(acc.getter_converters & generated_converter_names)
    reverse = sorted(acc.setter_converters & generated_converter_names)
    converter_imports = [f"_{n}" for n in forward] + [f"_to_c_{n}" for n in reverse]

    # Build enum map imports
    enum_map_imports: list[str] = []
    for ec in enum_contexts:
        if ec["map_name"] in acc.used_enum_from_c:
            enum_map_imports.append(f"{ec['map_name']}_FROM_C")
    for ec in enum_contexts:
        if ec["map_name"] in acc.used_enum_to_c:
            enum_map_imports.append(f"{ec['map_name']}_TO_C")

    # Version / JSON checks
    needs_version = any(lc.get("kind") == "composite_property" and lc.get("returns") == "Version" for lc in cls_ctx.get("lifecycle", []))
    has_handle_ref_setter = any(p["converter"] == "handle_ref" and p.get("setter_fn") for p in cls_ctx["properties"])
    needs_json = bool(cls_ctx.get("to_json_fn")) or "json_value" in acc.getter_converters or has_handle_ref_setter

    # ffi is needed when the class uses ffi.string (to_json), ffi.NULL (nullable string args),
    # ffi.new (out-param methods), or ffi.addressof (clip_id)
    needs_ffi = bool(
        needs_json
        or any(any(a for a in lc.get("c_args", []) if "ffi." in str(a)) for lc in cls_ctx.get("lifecycle", []))
        or any(m.get("c_struct") for m in cls_ctx.get("methods", []))
    )

    # Dataclass imports
    dataclass_imports = sorted({lc["returns"] for lc in cls_ctx.get("lifecycle", []) if lc.get("returns") in dataclass_name_set})

    type_check_enums = sorted(acc.type_check_enum_classes - acc.runtime_enum_classes)
    runtime_enums = sorted(acc.runtime_enum_classes)

    type_check_classes = [{"module": _class_to_module(name), "cls": name} for name in sorted(acc.type_check_class_names)]

    return {
        "base_imports": sorted(acc.base_imports),
        "type_imports": sorted(acc.type_names),
        "rounding_imports": sorted(acc.rounding_names),
        "converter_imports": sorted(converter_imports),
        "enum_map_imports": sorted(enum_map_imports),
        "needs_ffi": needs_ffi,
        "needs_json": needs_json,
        "needs_version": needs_version,
        "dataclass_imports": dataclass_imports,
        "runtime_enums": runtime_enums,
        "type_check_enums": type_check_enums,
        "type_check_classes": type_check_classes,
    }


def _compute_per_class_imports(
    cls_ctx: dict,
    enum_contexts: list[dict],
    generated_converter_names: set[str],
    all_class_names: set[str],
    dataclass_name_set: set[str],
) -> dict:
    """Compute the import requirements for a single facade class file."""
    all_enum_classes = {ec["facade_class"] for ec in enum_contexts}
    current_class = cls_ctx["name"]

    acc = SimpleNamespace(
        base_imports={"OwnedHandle" if cls_ctx["owns_handle"] else "HandleWrapper", "_decode_str"},
        getter_converters=set(),
        setter_converters=set(),
        used_enum_from_c=set(),
        used_enum_to_c=set(),
        type_check_enum_classes=set(),
        runtime_enum_classes=set(),
        type_check_class_names=set(),
        type_names=set(),
        rounding_names=set(),
    )
    if cls_ctx["collections"]:
        acc.base_imports.add("CollectionWrapper")

    _scan_py_collections(cls_ctx, acc, all_class_names, current_class)
    _scan_py_properties(cls_ctx, acc, all_enum_classes, all_class_names, current_class)
    _scan_py_methods(cls_ctx, acc, all_enum_classes, all_class_names, current_class, enum_contexts, generated_converter_names)
    _scan_py_init(cls_ctx, acc, all_enum_classes, all_class_names, current_class, enum_contexts, generated_converter_names)

    return _assemble_py_import_result(acc, cls_ctx, enum_contexts, generated_converter_names, dataclass_name_set)


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


# -----------------------------------------------------------------------
# Pydantic model generation
# -----------------------------------------------------------------------

# Rename map: datamodel-code-generator auto-derived name → our convention.
_MODEL_RENAMES: dict[str, str] = {
    "AscFramingDecisionList": "FramingDecisionList",
    "Version": "VersionModel",
    "Sequence": "FileSequenceModel",
    "ClipId": "ClipIDModel",
    "Round": "RoundModel",
    "DimensionsInt": "DimensionsIntModel",
    "DimensionsFloat": "DimensionsFloatModel",
    "PointFloat": "PointFloatModel",
    "FramingIntent": "FramingIntentModel",
    "FramingDecision": "FramingDecisionModel",
    "Canvas": "CanvasModel",
    "Context": "ContextModel",
    "CanvasTemplate": "CanvasTemplateModel",
    # RootModel types — keep as-is
    "FdlId": "FdlId",
    "FdlIdFramingDecision": "FdlIdFramingDecision",
}

# Exported model classes (BaseModel subclasses only, not Enums or RootModels).
_MODEL_EXPORTS: list[str] = [
    "CanvasModel",
    "CanvasTemplateModel",
    "ClipIDModel",
    "ContextModel",
    "DimensionsFloatModel",
    "DimensionsIntModel",
    "FileSequenceModel",
    "FramingDecisionList",
    "FramingDecisionModel",
    "FramingIntentModel",
    "PointFloatModel",
    "RoundModel",
    "VersionModel",
]


def _postprocess_models(filepath: Path) -> None:
    """Post-process the datamodel-code-generator output.

    1. Rename classes to our conventions.
    2. Change extra='forbid' → extra='allow' (for patternProperties custom attrs).
    3. Inject C-core semantic validator on the root model.
    """
    text = filepath.read_text(encoding="utf-8")

    # --- Remove timestamp comment (causes codegen drift check failures) ---
    text = re.sub(r"#   timestamp:.*\n", "", text)

    # --- Rename classes ---
    for old_name, new_name in _MODEL_RENAMES.items():
        if old_name == new_name:
            continue
        # Class definition: "class OldName(" → "class NewName("
        text = re.sub(rf"\bclass {old_name}\b", f"class {new_name}", text)
        # Type annotations, field types, list items: OldName
        text = re.sub(rf"\b{old_name}\b", new_name, text)

    # --- Allow extra fields for custom attributes ---
    text = text.replace("extra='forbid'", "extra='allow'")

    # --- Inject semantic validator on root model ---
    # Find the FramingDecisionList class and append the validator before the next class or EOF
    validator_code = '''
    @model_validator(mode="after")
    def _validate_fdl_semantics(self) -> FramingDecisionList:
        """Run C-core schema + semantic validation on top of Pydantic validation."""
        from fdl import FDL

        json_bytes = self.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
        doc = FDL.parse(json_bytes)
        doc.validate()
        return self
'''
    # Insert validator at the end of the FramingDecisionList class body.
    # The class is last in the file, so append before the trailing newline.
    if "class FramingDecisionList" in text:
        # Add model_validator import
        text = text.replace(
            "from pydantic import BaseModel, ConfigDict, Field, RootModel",
            "from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator",
        )
        # Append validator to end of file (FramingDecisionList is the last class)
        text = text.rstrip("\n") + "\n" + validator_code + "\n"

    filepath.write_text(text, encoding="utf-8")


def _write_models_init(output_dir: Path) -> None:
    """Write fdl/models/__init__.py with re-exports and documentation."""
    lines = [
        "# AUTO-GENERATED — DO NOT EDIT",
        '"""Pydantic v2 data models for the ASC Framing Decision List.',
        "",
        "These models provide a pure-data DTO (Data Transfer Object) layer for",
        "interoperability with web services and frameworks like FastAPI, Django REST",
        "Framework, and other Pydantic-native tools.",
        "",
        "**Data vs Logic**: The Pydantic models in this subpackage are data-only classes",
        "for serialization, validation, and transport. Business logic (compute framing,",
        "resolve canvas, round dimensions, etc.) lives on the bound facade classes in the",
        "parent ``fdl`` package (``FDL``, ``Canvas``, ``Context``, etc.).",
        "",
        "**Validation**: These models provide full semantic validation. Pydantic validates",
        "types and JSON Schema constraints first, then the C core validates semantic rules",
        "(ID reference integrity, dependent required fields, version constraints, etc.).",
        "",
        "**Converting between models and facades**::",
        "",
        "    from fdl import FDL",
        "    from fdl.models import FramingDecisionList",
        "",
        "    # Facade -> Model (for API responses, serialization)",
        "    doc = FDL.parse(json_bytes)",
        "    model = doc.to_model()",
        "",
        "    # Model -> Facade (for computation after receiving API input)",
        "    doc = FDL.from_model(model)",
        '"""',
        "",
        "from ._generated import (  # noqa: F401",
    ]
    for name in _MODEL_EXPORTS:
        lines.append(f"    {name},")
    lines.append(")")
    lines.append("")

    (output_dir / "__init__.py").write_text(encoding="utf-8", data="\n".join(lines))


def generate_models(schema_path: Path, output_dir: Path) -> None:
    """Generate Pydantic v2 models from the FDL JSON Schema.

    Runs datamodel-code-generator, then post-processes the output
    for class naming, custom attribute support, and semantic validation.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_file = output_dir / "_generated.py"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "datamodel_code_generator",
            "--input",
            str(schema_path),
            "--input-file-type",
            "jsonschema",
            "--output",
            str(generated_file),
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--target-python-version",
            "3.10",
            "--use-standard-collections",
            "--use-union-operator",
            "--field-constraints",
            "--use-annotated",
        ],
        check=True,
    )

    _postprocess_models(generated_file)
    _write_models_init(output_dir)

    print(f"Generated Pydantic models from {schema_path}")
    print(f"Output: {output_dir}")
