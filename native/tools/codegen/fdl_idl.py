# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Parse fdl_api.yaml into typed dataclass models for code generation.

Supports both the flat function list (for low-level FFI generation) and
the ``object_model`` section (for facade generation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .ir import (
    IR,
    IRClass,
    IRCollection,
    IRErrorHandling,
    IRInit,
    IRInitParam,
    IRInitPostSetter,
    IRMethod,
    IRMethodParam,
    IRProperty,
    IRResultField,
    parse_default,
)

# -----------------------------------------------------------------------
# Low-level IDL dataclasses (unchanged from Phase 3)
# -----------------------------------------------------------------------


@dataclass
class StructField:
    name: str
    c_type: str
    ownership: str | None = None
    direction: str | None = None
    nullable: bool = False


@dataclass
class VTMethodParam:
    name: str
    param_type: str
    nullable: bool = False


@dataclass
class VTOutParam:
    name: str
    param_type: str


@dataclass
class VTMethod:
    name: str
    c_function: str | None = None
    pure: bool = False
    kind: str = "instance"  # "instance" or "classmethod"
    params: list[VTMethodParam] = field(default_factory=list)
    returns: str | None = None
    out_params: list[VTOutParam] = field(default_factory=list)


@dataclass
class VTOperator:
    op: str
    c_function: str | None = None
    pure: bool = False
    param_type: str | None = None
    returns: str = "bool"


@dataclass
class ValueType:
    name: str
    fields: list[StructField]
    facade_class: str | None = None
    facade_converter: str | None = None
    facade_defaults: dict[str, str] | None = None
    cross_eq: str | None = None
    methods: list[VTMethod] = field(default_factory=list)
    operators: list[VTOperator] = field(default_factory=list)


@dataclass
class EnumValue:
    name: str
    value: int


@dataclass
class EnumType:
    name: str
    underlying: str
    values: list[EnumValue]
    facade_class: str | None = None
    facade_prefix: str | None = None
    string_values: dict[str, str] | None = None


@dataclass
class FunctionParam:
    name: str
    c_type: str
    direction: str | None = None
    nullable: bool = False


@dataclass
class Function:
    name: str
    returns: str
    params: list[FunctionParam]
    doc: str = ""
    ownership: str | None = None
    nullable: bool = False
    category: str | None = None


# -----------------------------------------------------------------------
# Object model dataclasses (new for Phase 4 groundwork)
# -----------------------------------------------------------------------


@dataclass
class PropertyMapping:
    name: str
    getter: str
    setter: str | None = None
    remover: str | None = None
    has_fn: str | None = None
    value_type: str = "string"
    nullable: bool = False
    handle_class: str | None = None  # For handle_ref: target facade class name


@dataclass
class CollectionPattern:
    name: str
    item_class: str
    count_fn: str
    at_fn: str
    find_by_id_fn: str | None = None
    find_by_label_fn: str | None = None
    add_fn: str | None = None


@dataclass
class MethodParamMapping:
    name: str
    param_type: str
    nullable: bool = False
    default: str | None = None
    expand: bool = False
    source_class: str | None = None
    global_fallback: str | None = None


@dataclass
class ResultFieldMapping:
    name: str
    source: str
    extract: str  # "handle", "scalar", "value_type", "string"
    wrap_class: str | None = None
    converter: str | None = None
    scalar_type: str | None = None
    private: bool = False


@dataclass
class ErrorHandlingMapping:
    pattern: str  # "null_check", "result_struct", "result_struct_multi", "validation"
    error_field: str | None = None
    success_field: str | None = None
    error_class: str | None = None
    free_fn: str | None = None
    count_fn: str | None = None
    at_fn: str | None = None
    result_fields: list[ResultFieldMapping] | None = None


@dataclass
class MethodMapping:
    name: str
    function: str
    kind: str = "instance"  # "static_factory", "instance", "builder", "compound_setter", "alias", "class_factory"
    params: list[MethodParamMapping] | None = None
    returns: str | None = None
    error_handling: ErrorHandlingMapping | None = None
    doc: str = ""
    alias_of: str | None = None
    compose_from: dict[str, str] | None = None
    factory_kwargs: list[dict] | None = None


@dataclass
class InitParam:
    name: str
    param_type: str
    nullable: bool = False
    default: str | None = None


@dataclass
class InitPostSetter:
    kind: str  # "property" or "compound"
    property: str | None = None
    method: str | None = None
    condition: str | None = None
    args: dict[str, str] | None = None
    always: bool = False


@dataclass
class InitDef:
    depth: int
    builder_method: str
    params: list[InitParam]
    post_setters: list[InitPostSetter] = field(default_factory=list)


@dataclass
class ObjectClass:
    name: str
    c_handle: str
    owns_handle: bool = False
    parent: str | None = None
    factory: str | None = None
    destructor: str | None = None
    custom_attrs: bool = False
    pydantic_model: str | None = None
    properties: list[PropertyMapping] = field(default_factory=list)
    collections: list[CollectionPattern] = field(default_factory=list)
    methods: list[MethodMapping] = field(default_factory=list)
    init: InitDef | None = None


@dataclass
class ObjectModel:
    classes: list[ObjectClass] = field(default_factory=list)


# -----------------------------------------------------------------------
# Auxiliary types (errors, version, etc.)
# -----------------------------------------------------------------------


@dataclass
class ErrorDef:
    name: str
    parent: str
    doc: str = ""


@dataclass
class VersionSlot:
    name: str
    slot_type: str
    default: str


@dataclass
class VersionDef:
    class_name: str
    doc: str
    slots: list[VersionSlot]


@dataclass
class DataclassField:
    name: str
    field_type: str
    private: bool = False


@dataclass
class DataclassAccessor:
    name: str
    returns: str
    doc: str
    lookup: str  # "by_label" or "by_id"
    collection: str  # e.g. "fdl.contexts", "context.canvases"
    key_field: str  # e.g. "context_label"


@dataclass
class DataclassDef:
    class_name: str
    doc: str
    fields: list[DataclassField]
    accessors: list[DataclassAccessor] | None = None


@dataclass
class JsonWrapperField:
    name: str
    field_type: str
    nullable: bool = False
    max_length: int | None = None
    min_value: int | None = None
    c_has_flag: str | None = None


@dataclass
class JsonWrapperDef:
    class_name: str
    doc: str
    fields: list[JsonWrapperField]
    c_struct: str | None = None
    free_fn: str | None = None
    mutual_exclusion: list[str] | None = None


@dataclass
class AuxiliaryTypes:
    errors: list[ErrorDef] = field(default_factory=list)
    version: VersionDef | None = None
    dataclasses: list[DataclassDef] = field(default_factory=list)
    json_wrappers: list[JsonWrapperDef] = field(default_factory=list)


# -----------------------------------------------------------------------
# Free functions (top-level functions wrapping C ABI)
# -----------------------------------------------------------------------


@dataclass
class FreeFunctionParam:
    name: str
    param_type: str


@dataclass
class FreeFunctionDef:
    name: str
    display_name: str
    c_function: str
    doc: str
    params: list[FreeFunctionParam]
    returns: str
    module: str = "rounding"  # target module grouping: "rounding" or "utils"


# -----------------------------------------------------------------------
# Utility functions (generated per-language from template)
# -----------------------------------------------------------------------


@dataclass
class UtilityDef:
    name: str
    kind: str  # "c_abi", "collection_find", "io", "rounding_state", "constant"
    doc: str
    c_function: str | None = None
    extract: str | None = None  # "dims" or "anchor" (for c_abi kind)


# -----------------------------------------------------------------------
# Complete IDL
# -----------------------------------------------------------------------


@dataclass
class IDL:
    value_types: list[ValueType]
    enums: list[EnumType]
    opaque_types: list[str]
    functions: list[Function]
    object_model: ObjectModel = field(default_factory=ObjectModel)
    auxiliary_types: AuxiliaryTypes = field(default_factory=AuxiliaryTypes)
    free_functions: list[FreeFunctionDef] = field(default_factory=list)
    utilities: list[UtilityDef] = field(default_factory=list)


# -----------------------------------------------------------------------
# Parsers
# -----------------------------------------------------------------------


def _parse_field(raw: dict) -> StructField:
    return StructField(
        name=raw["name"],
        c_type=raw["type"],
        ownership=raw.get("ownership"),
        direction=raw.get("direction"),
        nullable=raw.get("nullable", False),
    )


def _parse_value_type(name: str, raw: dict) -> ValueType:
    facade = raw.get("facade", {})

    methods = []
    for m in raw.get("methods", []):
        params = [VTMethodParam(name=p["name"], param_type=p["type"], nullable=p.get("nullable", False)) for p in m.get("params", [])]
        out_params = [VTOutParam(name=p["name"], param_type=p["type"]) for p in m.get("out_params", [])]
        methods.append(
            VTMethod(
                name=m["name"],
                c_function=m.get("c_function"),
                pure=m.get("pure", False),
                kind=m.get("kind", "instance"),
                params=params,
                returns=m.get("returns"),
                out_params=out_params,
            )
        )

    operators = [
        VTOperator(
            op=o["op"],
            c_function=o.get("c_function"),
            pure=o.get("pure", False),
            param_type=o.get("param_type"),
            returns=o.get("returns", "bool"),
        )
        for o in raw.get("operators", [])
    ]

    return ValueType(
        name=name,
        fields=[_parse_field(f) for f in raw["fields"]],
        facade_class=facade.get("class_name"),
        facade_converter=facade.get("converter"),
        facade_defaults=facade.get("defaults"),
        cross_eq=raw.get("cross_eq"),
        methods=methods,
        operators=operators,
    )


def _parse_enum(name: str, raw: dict) -> EnumType:
    values = [EnumValue(name=k, value=v) for k, v in raw["values"].items()]
    facade = raw.get("facade", {})
    return EnumType(
        name=name,
        underlying=raw["underlying"],
        values=values,
        facade_class=facade.get("class_name"),
        facade_prefix=facade.get("prefix"),
        string_values=raw.get("string_values"),
    )


def _parse_function(raw: dict) -> Function:
    params = []
    for p in raw.get("params", []):
        params.append(
            FunctionParam(
                name=p["name"],
                c_type=p["type"],
                direction=p.get("direction"),
                nullable=p.get("nullable", False),
            )
        )
    return Function(
        name=raw["name"],
        returns=raw["returns"],
        params=params,
        doc=raw.get("doc", ""),
        ownership=raw.get("ownership"),
        nullable=raw.get("nullable", False),
        category=raw.get("category"),
    )


def _parse_property(name: str, raw: dict) -> PropertyMapping:
    return PropertyMapping(
        name=name,
        getter=raw["getter"],
        setter=raw.get("setter"),
        remover=raw.get("remover"),
        has_fn=raw.get("has"),
        value_type=raw.get("type", "string"),
        nullable=raw.get("nullable", False),
        handle_class=raw.get("handle_class"),
    )


def _parse_collection(name: str, raw: dict) -> CollectionPattern:
    return CollectionPattern(
        name=name,
        item_class=raw["item_class"],
        count_fn=raw["count"],
        at_fn=raw["at"],
        find_by_id_fn=raw.get("find_by_id"),
        find_by_label_fn=raw.get("find_by_label"),
        add_fn=raw.get("add"),
    )


def _parse_method(name: str, raw: dict) -> MethodMapping:
    params = None
    if "params" in raw:
        params = [
            MethodParamMapping(
                name=p["name"],
                param_type=p["type"],
                nullable=p.get("nullable", False),
                default=p.get("default"),
                expand=p.get("expand", False),
                source_class=p.get("source_class"),
                global_fallback=p.get("global_fallback"),
            )
            for p in raw["params"]
        ]
    error_handling = None
    if "error_handling" in raw:
        eh = raw["error_handling"]
        result_fields = None
        if "fields" in eh:
            result_fields = [
                ResultFieldMapping(
                    name=f["name"],
                    source=f["source"],
                    extract=f["extract"],
                    wrap_class=f.get("wrap_class"),
                    converter=f.get("converter"),
                    scalar_type=f.get("scalar_type"),
                    private=f.get("private", False),
                )
                for f in eh["fields"]
            ]
        error_handling = ErrorHandlingMapping(
            pattern=eh["pattern"],
            error_field=eh.get("error_field"),
            success_field=eh.get("success_field"),
            error_class=eh.get("error_class"),
            free_fn=eh.get("free_fn"),
            count_fn=eh.get("count_fn"),
            at_fn=eh.get("at_fn"),
            result_fields=result_fields,
        )
    return MethodMapping(
        name=name,
        function=raw.get("function", ""),
        kind=raw.get("kind", "instance"),
        params=params,
        returns=raw.get("returns"),
        error_handling=error_handling,
        doc=raw.get("doc", ""),
        alias_of=raw.get("alias_of"),
        compose_from=raw.get("compose_from"),
        factory_kwargs=raw.get("factory_kwargs"),
    )


def _parse_init(raw: dict) -> InitDef:
    params = [
        InitParam(
            name=p["name"],
            param_type=p["type"],
            nullable=p.get("nullable", False),
            default=p.get("default"),
        )
        for p in raw.get("params", [])
    ]
    post_setters = [
        InitPostSetter(
            kind=ps["kind"],
            property=ps.get("property"),
            method=ps.get("method"),
            condition=ps.get("condition"),
            args=ps.get("args"),
            always=ps.get("always", False),
        )
        for ps in raw.get("post_setters", [])
    ]
    return InitDef(
        depth=raw["depth"],
        builder_method=raw["builder_method"],
        params=params,
        post_setters=post_setters,
    )


def _parse_object_class(name: str, raw: dict) -> ObjectClass:
    properties = [_parse_property(k, v) for k, v in raw.get("properties", {}).items()]
    collections = [_parse_collection(k, v) for k, v in raw.get("collections", {}).items()]
    methods = [_parse_method(k, v) for k, v in raw.get("methods", {}).items()]
    init = _parse_init(raw["init"]) if "init" in raw else None

    return ObjectClass(
        name=name,
        c_handle=raw["c_handle"],
        owns_handle=raw.get("owns_handle", False),
        parent=raw.get("parent"),
        pydantic_model=raw.get("pydantic_model"),
        factory=raw.get("factory"),
        destructor=raw.get("destructor"),
        custom_attrs=raw.get("custom_attrs", False),
        properties=properties,
        collections=collections,
        methods=methods,
        init=init,
    )


def _parse_object_model(raw: dict | None) -> ObjectModel:
    if not raw:
        return ObjectModel()
    classes = [_parse_object_class(name, cls) for name, cls in raw.get("classes", {}).items()]
    return ObjectModel(classes=classes)


def _parse_auxiliary_types(raw: dict | None) -> AuxiliaryTypes:
    if not raw:
        return AuxiliaryTypes()
    errors = [ErrorDef(name=e["name"], parent=e["parent"], doc=e.get("doc", "")) for e in raw.get("errors", [])]
    version = None
    if "version" in raw:
        v = raw["version"]
        slots = [VersionSlot(name=s["name"], slot_type=s["type"], default=str(s["default"])) for s in v.get("slots", [])]
        version = VersionDef(class_name=v["class_name"], doc=v.get("doc", ""), slots=slots)
    dataclasses_list = []
    for dc_name, dc_raw in raw.get("dataclasses", {}).items():
        fields = [DataclassField(name=f["name"], field_type=f["type"], private=f.get("private", False)) for f in dc_raw.get("fields", [])]
        accessors = None
        if "accessors" in dc_raw:
            accessors = [
                DataclassAccessor(
                    name=a["name"],
                    returns=a["returns"],
                    doc=a.get("doc", ""),
                    lookup=a["lookup"],
                    collection=a["collection"],
                    key_field=a["key_field"],
                )
                for a in dc_raw["accessors"]
            ]
        dataclasses_list.append(
            DataclassDef(
                class_name=dc_name,
                doc=dc_raw.get("doc", ""),
                fields=fields,
                accessors=accessors,
            )
        )
    json_wrappers_list = []
    for jw_name, jw_raw in raw.get("json_wrappers", {}).items():
        jw_fields = [
            JsonWrapperField(
                name=f["name"],
                field_type=f["type"],
                nullable=f.get("nullable", False),
                max_length=f.get("max_length"),
                min_value=f.get("min_value"),
                c_has_flag=f.get("c_has_flag"),
            )
            for f in jw_raw.get("fields", [])
        ]
        json_wrappers_list.append(
            JsonWrapperDef(
                class_name=jw_name,
                doc=jw_raw.get("doc", ""),
                fields=jw_fields,
                c_struct=jw_raw.get("c_struct"),
                free_fn=jw_raw.get("free_fn"),
                mutual_exclusion=jw_raw.get("mutual_exclusion"),
            )
        )
    return AuxiliaryTypes(errors=errors, version=version, dataclasses=dataclasses_list, json_wrappers=json_wrappers_list)


# -----------------------------------------------------------------------
# Function synthesis — derive C ABI functions from object_model
# -----------------------------------------------------------------------

# Map object_model property type keys to C ABI getter return / setter param types.
_PROP_TYPE_TO_C: dict[str, dict[str, str]] = {
    "string": {"getter_ret": "const char*", "setter_param": "const char*"},
    "int": {"getter_ret": "int", "setter_param": "int"},
    "int64_t": {"getter_ret": "int64_t", "setter_param": "int64_t"},
    "double": {"getter_ret": "double", "setter_param": "double"},
}

# Map opaque handle name → conventional short param name used in C ABI.
_HANDLE_PARAM_NAMES: dict[str, str] = {
    "fdl_doc_t": "doc",
    "fdl_context_t": "ctx",
    "fdl_canvas_t": "canvas",
    "fdl_framing_decision_t": "fd",
    "fdl_framing_intent_t": "fi",
    "fdl_canvas_template_t": "ct",
    "fdl_clip_id_t": "cid",
    "fdl_file_sequence_t": "seq",
}


def _synthesize_property_fns(
    prop: PropertyMapping,
    handle: str,
    param_name: str,
    const_ptr: str,
    mut_ptr: str,
    object_model: ObjectModel,
    vt_names: set[str],
    enum_names: set[str],
) -> list[Function]:
    """Synthesize C ABI getter/setter/has/remover functions for a single property."""
    vtype = prop.value_type

    # Determine C return type for getter
    if vtype in _PROP_TYPE_TO_C:
        c_ret = _PROP_TYPE_TO_C[vtype]["getter_ret"]
        c_set_param = _PROP_TYPE_TO_C[vtype]["setter_param"]
        # String getters on document-owned handles return borrowed ptrs.
        # Sub-object handles (ClipID, FileSequence) don't carry this.
        ownership = "valid_until_doc_freed" if vtype == "string" and handle not in ("fdl_clip_id_t", "fdl_file_sequence_t") else None
    elif vtype == "handle_ref":
        # Handle reference getter returns mutable pointer to child handle
        child_handle = prop.handle_class  # e.g. "ClipID"
        child_cls = next((c for c in object_model.classes if c.name == child_handle), None)
        if child_cls:
            c_ret = f"{child_cls.c_handle}*"
        else:
            return []
        c_set_param = "const char*"  # handle_ref setters take JSON
        ownership = None
    elif vtype in vt_names:
        c_ret = vtype
        c_set_param = vtype
        ownership = None
    elif vtype in enum_names:
        c_ret = vtype
        c_set_param = vtype
        ownership = None
    else:
        return []  # unknown type, skip

    result: list[Function] = []

    # Getter
    if prop.getter:
        getter_handle_param = mut_ptr if vtype == "handle_ref" else const_ptr
        result.append(
            Function(
                name=prop.getter,
                returns=c_ret,
                params=[FunctionParam(name=param_name, c_type=getter_handle_param)],
                category="accessor",
                ownership=ownership,
            )
        )

    # Has-check
    if prop.has_fn:
        result.append(
            Function(
                name=prop.has_fn,
                returns="int",
                params=[FunctionParam(name=param_name, c_type=const_ptr)],
                category="accessor",
            )
        )

    # Setter (simple property setters only — compound setters are explicit)
    if prop.setter and vtype != "handle_ref":
        result.append(
            Function(
                name=prop.setter,
                returns="void",
                params=[
                    FunctionParam(name=param_name, c_type=mut_ptr),
                    FunctionParam(name=prop.name, c_type=c_set_param),
                ],
                category="setter",
            )
        )
    elif prop.setter and vtype == "handle_ref":
        # handle_ref setters take JSON string + length, return error string
        result.append(
            Function(
                name=prop.setter,
                returns="const char*",
                params=[
                    FunctionParam(name=param_name, c_type=mut_ptr),
                    FunctionParam(name="json_str", c_type="const char*"),
                    FunctionParam(name="json_len", c_type="size_t"),
                ],
                category="setter",
                ownership="caller_frees",
                nullable=True,
            )
        )

    # Remover
    if prop.remover:
        result.append(
            Function(
                name=prop.remover,
                returns="void",
                params=[FunctionParam(name=param_name, c_type=mut_ptr)],
                category="setter",
            )
        )

    return result


def _synthesize_collection_fns(
    coll: CollectionPattern,
    owns_handle: bool,
    param_name: str,
    const_ptr: str,
    mut_ptr: str,
    object_model: ObjectModel,
) -> list[Function]:
    """Synthesize C ABI count/at/find functions for a single collection."""
    item_cls = next((c for c in object_model.classes if c.name == coll.item_class), None)
    if not item_cls:
        return []
    item_ptr = f"{item_cls.c_handle}*"

    result: list[Function] = []

    # Count
    if coll.count_fn:
        result.append(
            Function(
                name=coll.count_fn,
                returns="uint32_t",
                params=[FunctionParam(name=param_name, c_type=const_ptr if not owns_handle else mut_ptr)],
                category="collection",
            )
        )

    # At (indexed access)
    if coll.at_fn:
        result.append(
            Function(
                name=coll.at_fn,
                returns=item_ptr,
                params=[
                    FunctionParam(name=param_name, c_type=mut_ptr),
                    FunctionParam(name="index", c_type="uint32_t"),
                ],
                category="collection",
                ownership="valid_until_doc_freed",
            )
        )

    # Find by ID
    if coll.find_by_id_fn:
        result.append(
            Function(
                name=coll.find_by_id_fn,
                returns=item_ptr,
                params=[
                    FunctionParam(name=param_name, c_type=mut_ptr),
                    FunctionParam(name="id", c_type="const char*"),
                ],
                category="collection",
                ownership="valid_until_doc_freed",
                nullable=True,
            )
        )

    # Find by label
    if coll.find_by_label_fn:
        result.append(
            Function(
                name=coll.find_by_label_fn,
                returns=item_ptr,
                params=[
                    FunctionParam(name=param_name, c_type=mut_ptr),
                    FunctionParam(name="label", c_type="const char*"),
                ],
                category="collection",
                ownership="valid_until_doc_freed",
                nullable=True,
            )
        )

    return result


def _synthesize_functions(
    object_model: ObjectModel,
    value_types: list[ValueType],
    enums: list[EnumType],
) -> list[Function]:
    """Derive C ABI Function objects from object_model property/collection refs.

    For each function name referenced in object_model (getter, setter, has,
    remover, count, at, find_by_id, find_by_label), synthesize the C ABI
    signature. This eliminates the need to maintain these entries manually in
    the functions section of the YAML.
    """
    vt_names = {vt.name for vt in value_types}
    enum_names = {e.name for e in enums}

    synth: list[Function] = []
    seen: set[str] = set()  # Deduplicate (shared has_fn across properties)

    def _add(func: Function) -> None:
        if func.name not in seen:
            seen.add(func.name)
            synth.append(func)

    for cls in object_model.classes:
        handle = cls.c_handle
        param_name = _HANDLE_PARAM_NAMES.get(handle, "h")
        const_ptr = f"const {handle}*"
        mut_ptr = f"{handle}*"

        for prop in cls.properties:
            for f in _synthesize_property_fns(prop, handle, param_name, const_ptr, mut_ptr, object_model, vt_names, enum_names):
                _add(f)

        for coll in cls.collections:
            for f in _synthesize_collection_fns(coll, cls.owns_handle, param_name, const_ptr, mut_ptr, object_model):
                _add(f)

    return synth


def _merge_header_overlay(
    header_path: Path,
    metadata: dict,
) -> list[Function]:
    """Build Function list from C header signatures + YAML metadata overlay."""
    from .c_header_parser import parse_c_header

    parsed = parse_c_header(header_path)
    functions: list[Function] = []

    for pf in parsed.values():
        # Skip custom attribute functions (handled by _generate_custom_attr_functions)
        if "custom_attr" in pf.name:
            continue

        overlay = metadata.get(pf.name, {})
        overlay_params = overlay.get("params", {})

        params = []
        for pp in pf.params:
            pm = overlay_params.get(pp.name, {})
            params.append(
                FunctionParam(
                    name=pp.name,
                    c_type=pp.c_type,
                    direction=pm.get("direction"),
                    nullable=pm.get("nullable", False),
                )
            )

        functions.append(
            Function(
                name=pf.name,
                returns=pf.return_type,
                params=params,
                doc=overlay.get("doc", pf.doc),
                ownership=overlay.get("ownership"),
                nullable=overlay.get("nullable", False),
                category=overlay.get("category"),
            )
        )

    return functions


def parse_idl(path: Path, header_path: Path | None = None) -> IDL:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    value_types = [_parse_value_type(name, vt) for name, vt in data.get("value_types", {}).items()]
    enums = [_parse_enum(name, e) for name, e in data.get("enums", {}).items()]
    opaque_types = data.get("opaque_types", [])

    # Two modes: new function_metadata overlay (with C header parsing) or legacy functions list
    if "function_metadata" in data and header_path is not None and header_path.exists():
        functions = _merge_header_overlay(header_path, data["function_metadata"])
    else:
        functions = [_parse_function(f) for f in data.get("functions", [])]

    object_model = _parse_object_model(data.get("object_model"))
    auxiliary_types = _parse_auxiliary_types(data.get("auxiliary_types"))

    # Parse free functions
    free_functions = []
    for ff_raw in data.get("free_functions", []):
        params = [FreeFunctionParam(name=p["name"], param_type=p["type"]) for p in ff_raw.get("params", [])]
        free_functions.append(
            FreeFunctionDef(
                name=ff_raw["name"],
                display_name=ff_raw["display_name"],
                c_function=ff_raw["c_function"],
                doc=ff_raw.get("doc", ""),
                params=params,
                returns=ff_raw.get("returns", "None"),
                module=ff_raw.get("module", "rounding"),
            )
        )

    # Parse utilities
    utilities = []
    for u_raw in data.get("utilities", []):
        utilities.append(
            UtilityDef(
                name=u_raw["name"],
                kind=u_raw.get("kind", "c_abi"),
                doc=u_raw.get("doc", ""),
                c_function=u_raw.get("c_function"),
                extract=u_raw.get("extract"),
            )
        )

    # Synthesize accessor/collection functions from object_model.
    # When using header-parsed functions, synthesized metadata (ownership,
    # nullable) takes precedence over the bare header signatures.
    fn_by_name = {f.name: f for f in functions}
    synthesized = _synthesize_functions(object_model, value_types, enums)
    for sf in synthesized:
        existing = fn_by_name.get(sf.name)
        if existing is None:
            functions.append(sf)
        else:
            # Merge synthesized metadata into header-parsed function
            if sf.ownership and not existing.ownership:
                existing.ownership = sf.ownership
            if sf.nullable and not existing.nullable:
                existing.nullable = sf.nullable
            for sp in sf.params:
                for ep in existing.params:
                    if ep.name == sp.name:
                        if sp.direction and not ep.direction:
                            ep.direction = sp.direction
                        if sp.nullable and not ep.nullable:
                            ep.nullable = sp.nullable
                        break

    # Sort for stable output regardless of YAML entry order or synthesis order.
    functions.sort(key=lambda f: f.name)

    return IDL(
        value_types=value_types,
        enums=enums,
        opaque_types=opaque_types,
        functions=functions,
        object_model=object_model,
        auxiliary_types=auxiliary_types,
        free_functions=free_functions,
        utilities=utilities,
    )


# -----------------------------------------------------------------------
# IDL → IR transformation
# -----------------------------------------------------------------------


_IDENTITY_ATTRS: dict[str, str] = {
    "Context": "label",
    "Canvas": "id",
    "FramingDecision": "id",
    "FramingIntent": "id",
    "CanvasTemplate": "id",
}


def build_ir(idl: IDL) -> IR:
    """Transform the IDL object model into the language-neutral IR."""
    ir = IR()
    for cls in idl.object_model.classes:
        ir_class = IRClass(
            name=cls.name,
            handle_type=cls.c_handle,
            owns_handle=cls.owns_handle,
            parent=cls.parent,
            factory=cls.factory,
            destructor=cls.destructor,
            identity_attr=_IDENTITY_ATTRS.get(cls.name),
            custom_attrs=cls.custom_attrs,
            pydantic_model=cls.pydantic_model,
        )

        for prop in cls.properties:
            ir_class.properties.append(
                IRProperty(
                    name=prop.name,
                    type_key=prop.value_type,
                    getter_fn=prop.getter,
                    setter_fn=prop.setter,
                    remover_fn=prop.remover,
                    has_fn=prop.has_fn,
                    nullable=prop.nullable,
                    handle_class=prop.handle_class,
                )
            )

        for coll in cls.collections:
            ir_class.collections.append(
                IRCollection(
                    name=coll.name,
                    item_class=coll.item_class,
                    count_fn=coll.count_fn,
                    at_fn=coll.at_fn,
                    find_by_id_fn=coll.find_by_id_fn,
                    find_by_label_fn=coll.find_by_label_fn,
                    add_fn=coll.add_fn,
                )
            )

        for method in cls.methods:
            ir_params = []
            if method.params:
                for p in method.params:
                    ir_params.append(
                        IRMethodParam(
                            name=p.name,
                            type_key=p.param_type,
                            nullable=p.nullable,
                            default=parse_default(p.default) if p.default is not None else None,
                            expand=p.expand,
                            source_class=p.source_class,
                            global_fallback=p.global_fallback,
                        )
                    )
            ir_error = None
            if method.error_handling:
                eh = method.error_handling
                ir_result_fields = None
                if eh.result_fields:
                    ir_result_fields = [
                        IRResultField(
                            name=rf.name,
                            source=rf.source,
                            extract=rf.extract,
                            wrap_class=rf.wrap_class,
                            converter=rf.converter,
                            scalar_type=rf.scalar_type,
                            private=rf.private,
                        )
                        for rf in eh.result_fields
                    ]
                ir_error = IRErrorHandling(
                    pattern=eh.pattern,
                    error_field=eh.error_field,
                    success_field=eh.success_field,
                    error_class=eh.error_class,
                    free_fn=eh.free_fn,
                    count_fn=eh.count_fn,
                    at_fn=eh.at_fn,
                    result_fields=ir_result_fields,
                )
            ir_class.methods.append(
                IRMethod(
                    name=method.name,
                    function=method.function,
                    kind=method.kind,
                    params=ir_params,
                    returns=method.returns,
                    error_handling=ir_error,
                    doc=method.doc,
                    alias_of=method.alias_of,
                    compose_from=method.compose_from,
                    factory_kwargs=method.factory_kwargs,
                )
            )

        if cls.init:
            ir_class.init = IRInit(
                depth=cls.init.depth,
                builder_method=cls.init.builder_method,
                params=[
                    IRInitParam(
                        name=p.name,
                        type_key=p.param_type,
                        nullable=p.nullable,
                        default=parse_default(p.default) if p.default is not None else None,
                    )
                    for p in cls.init.params
                ],
                post_setters=[
                    IRInitPostSetter(
                        kind=ps.kind,
                        property=ps.property,
                        method=ps.method,
                        condition=ps.condition,
                        args=ps.args,
                        always=ps.always,
                    )
                    for ps in cls.init.post_setters
                ],
            )

        ir.classes.append(ir_class)

    return ir
