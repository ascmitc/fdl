# FDL IDL Format Reference

This document describes the structure and semantics of `fdl_api.yaml`, the
Interface Description Language (IDL) for the FDL codegen pipeline.

## Overview

`fdl_api.yaml` is the single source of truth for generating language bindings
(Python, TypeScript, C++ RAII) from the C ABI defined in `fdl_core.h`. The
codegen pipeline works as follows:

```
fdl_api.yaml  ──┐
                 ├─→  parse_idl()  →  IR  →  language context  →  Jinja2 templates  →  bindings
fdl_core.h   ──┘
```

The C header provides function signatures and Doxygen doc comments. The YAML
provides higher-level semantics: ownership, nullability, class hierarchies,
property/collection mappings, and facade metadata. Together they produce
complete bindings without duplicating information.

## Top-Level Sections

| Section | Purpose |
|---------|---------|
| `value_types` | Stack-allocated structs passed by value |
| `enums` | Integer enum types with string mappings |
| `opaque_types` | Pointer-only handle types (no field access) |
| `object_model` | Class hierarchy mapping C handles to facade classes |
| `function_metadata` | Annotations for C functions parsed from the header |
| `auxiliary_types` | Error classes, version, dataclasses, JSON wrappers |
| `free_functions` | Top-level functions exposed in target language |
| `utilities` | Generated per-language helper functions |

---

## `value_types`

Defines lightweight value types (stack-allocated C structs) that are passed by
value across the FFI boundary. Each value type becomes a class in every target
language.

### Schema

```yaml
value_types:
  <c_struct_name>:
    fields:
      - { name: <field_name>, type: <c_type> }
    cross_eq: <other_vt_name>         # optional: cross-type equality
    facade:
      class_name: <FacadeClass>       # required
      converter: <converter_name>     # required: camelCase converter name
      defaults:                       # optional: default values for enum fields
        <field_name>: <MEMBER_NAME>
    methods:                          # optional
      - name: <method_name>
        c_function: <c_func>          # omit for pure methods
        pure: true                    # true = implemented in target language
        kind: instance | classmethod  # default: instance
        params: [{ name: <n>, type: <t>, nullable: <bool> }]
        returns: <type>               # "self", "bool", "string", C type, or omit for void
        out_params: [{ name: <n>, type: <t> }]
    operators:                        # optional
      - op: __gt__ | __lt__ | __eq__ | __bool__ | __add__ | __sub__ | __mul__ | __iadd__
        c_function: <c_func>         # omit for pure operators
        pure: true
        param_type: <type>           # binary operator right-hand type
        returns: <type>
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `fields` | yes | List of struct fields with `name` and C `type` |
| `cross_eq` | no | Another value type to support cross-type `==` comparison |
| `facade.class_name` | yes | Target language class name (e.g., `DimensionsInt`) |
| `facade.converter` | yes | Snake-case converter name for FFI bridge (e.g., `dims_i64`) |
| `facade.defaults` | no | Map of field name → enum member for default values |
| `methods` | no | Instance or class methods on the value type |
| `operators` | no | Operator overloads (`__eq__`, `__add__`, etc.) |

### Valid C types for fields

`int64_t`, `uint32_t`, `double`, `int`, and any enum C type name.

### Example

```yaml
fdl_dimensions_i64_t:
  fields:
    - { name: width, type: int64_t }
    - { name: height, type: int64_t }
  cross_eq: fdl_dimensions_f64_t
  facade:
    class_name: DimensionsInt
    converter: dims_i64
  methods:
    - name: is_zero
      c_function: fdl_dimensions_i64_is_zero
      returns: bool
    - name: duplicate
      pure: true
      returns: self
```

---

## `enums`

Defines C enum types with integer values, facade names, and optional string
value mappings (for JSON serialization).

### Schema

```yaml
enums:
  <c_enum_name>:
    underlying: uint32_t
    values:
      <C_CONSTANT_NAME>: <int_value>
    facade:
      class_name: <FacadeEnum>
      prefix: <C_PREFIX_>
    string_values:            # optional
      <MEMBER_NAME>: <json_string>
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `underlying` | yes | C underlying type (always `uint32_t` currently) |
| `values` | yes | Map of C constant name → integer value |
| `facade.class_name` | yes | Target language enum/class name |
| `facade.prefix` | yes | C constant prefix to strip for member names |
| `string_values` | no | Map of member name → JSON string representation |

### Example

```yaml
fdl_rounding_mode_t:
  underlying: uint32_t
  values:
    FDL_ROUNDING_MODE_UP: 0
    FDL_ROUNDING_MODE_DOWN: 1
    FDL_ROUNDING_MODE_ROUND: 2
  facade:
    class_name: RoundingMode
    prefix: FDL_ROUNDING_MODE_
  string_values:
    UP: up
    DOWN: down
    ROUND: round
```

---

## `opaque_types`

Lists C handle types that are pointer-only (no direct field access). These
types are used as parameters and return values in functions but are never
dereferenced — all access goes through C API functions.

### Schema

```yaml
opaque_types:
  - <c_handle_type>
```

### Example

```yaml
opaque_types:
  - fdl_doc_t
  - fdl_context_t
  - fdl_canvas_t
```

---

## `object_model`

The heart of facade generation. Maps C handle types to object-oriented class
hierarchies with properties, collections, methods, and constructors.

### Schema

```yaml
object_model:
  classes:
    <ClassName>:
      c_handle: <handle_type>
      owns_handle: <bool>           # true = class frees handle on destruction
      parent: <ParentClass>         # optional: parent in ownership hierarchy
      factory: <c_create_fn>        # optional: C function to create handle
      destructor: <c_free_fn>       # optional: C function to free handle
      custom_attrs: <bool>          # optional: supports custom attributes
      pydantic_model: <ModelName>   # optional: Pydantic/TS model class name
      properties: { ... }
      collections: { ... }
      methods: { ... }
      init: { ... }
```

### Class-Level Fields

| Field | Required | Description |
|-------|----------|-------------|
| `c_handle` | yes | C opaque handle type (e.g., `fdl_doc_t`) |
| `owns_handle` | no | `true` if class owns and frees the handle (default: `false`) |
| `parent` | no | Parent class in ownership hierarchy |
| `factory` | no | C function to create a new handle |
| `destructor` | no | C function to free the handle |
| `custom_attrs` | no | `true` to generate custom attribute methods |
| `pydantic_model` | no | Name of Pydantic/TypeScript data model for `to_model()`/`from_model()` bridge |

### Properties

Map C getter/setter functions to named properties.

```yaml
properties:
  <prop_name>:
    getter: <c_getter_fn>
    setter: <c_setter_fn>         # optional
    remover: <c_remover_fn>       # optional: removes optional property
    has: <c_has_fn>               # optional: checks if optional property is set
    type: <type_key>              # see type keys below
    handle_class: <ClassName>     # for handle_ref type only
    nullable: <bool>
```

#### Property Type Keys

| Type Key | Description |
|----------|-------------|
| `string` | UTF-8 string |
| `int` | Integer |
| `int64_t` | 64-bit integer |
| `uint32_t` | Unsigned 32-bit integer |
| `double` | 64-bit float |
| `bool` | Boolean |
| `handle_ref` | Reference to another handle-based object (with `handle_class`) |
| `fdl_dimensions_i64_t` | DimensionsInt value type |
| `fdl_dimensions_f64_t` | DimensionsFloat value type |
| `fdl_point_f64_t` | PointFloat value type |
| `fdl_rect_t` | Rect value type |
| `fdl_round_strategy_t` | RoundStrategy value type |
| `<enum_c_name>` | Any enum type name |

### Collections

Map C count/at/find/add functions to iterable collections.

```yaml
collections:
  <collection_name>:
    item_class: <ClassName>
    count: <c_count_fn>
    at: <c_at_fn>
    find_by_id: <c_find_by_id_fn>     # optional
    find_by_label: <c_find_by_label_fn>  # optional
    add: <c_add_fn>                   # optional
```

### Methods

Map C functions to class methods with various kinds.

```yaml
methods:
  <method_name>:
    function: <c_function>
    kind: <method_kind>
    returns: <type>
    doc: <docstring>
    params:
      - name: <param_name>
        type: <type_key>
        nullable: <bool>
        default: <literal>            # Python literal: "2", '""', "None"
        expand: <bool>               # expand value type fields as individual args
        source_class: <ClassName>    # for handle-typed params
        global_fallback: <fn_name>   # fallback function for default value
    error_handling:
      pattern: <error_pattern>
      error_field: <field_name>
      success_field: <field_name>
      error_class: <error_key>
      free_fn: <c_free_fn>
      count_fn: <c_count_fn>
      at_fn: <c_at_fn>
      fields:                        # for result_struct_multi
        - name: <field_name>
          source: <c_field>
          extract: handle | scalar | string | value_type
          wrap_class: <ClassName>
          converter: <converter>
          scalar_type: <type>
          private: <bool>
    alias_of: <other_method>          # for alias kind
    compose_from:                     # for composite_property kind
      <field>: <source_property>
    factory_kwargs:                   # for class_factory kind
      - { name: <kwarg>, value: <expr> }
```

#### Method Kinds

| Kind | Description |
|------|-------------|
| `static_factory` | Static method returning a new instance (e.g., `parse`, `create`) |
| `class_factory` | Factory creating child with fixed parent args |
| `instance` | Regular instance method |
| `builder` | Method that creates and returns a child handle |
| `compound_setter` | Sets multiple properties via a single C function |
| `alias` | Alias for another method |
| `composite_property` | Read-only property composed from other properties |
| `instance_getter` | Instance method returning a value type |
| `instance_getter_optional` | Like `instance_getter` but nullable |
| `validate_json` | JSON validation method returning nullable error string |

#### Error Handling Patterns

| Pattern | Description |
|---------|-------------|
| `null_check` | C function returns NULL on error |
| `result_struct` | C function returns a struct with error + success fields |
| `result_struct_multi` | Like `result_struct` but with multiple result fields |
| `validation` | Returns validation result handle with error list |

### Init (Constructor)

Defines an options-object constructor that delegates to a builder method.

```yaml
init:
  depth: <int>                      # nesting depth: 0=doc, 1=doc child, 2=context child, 3=canvas child
  builder_method: <method_name>     # name of the builder method to delegate to
  params:
    - name: <param_name>
      type: <type_key>
      nullable: <bool>
      default: <literal>
  post_setters:                     # optional: properties to set after construction
    - kind: property | compound
      property: <prop_name>
      method: <method_name>         # for compound kind
      condition: <param_name>       # set only if param is not None
      always: <bool>                # set even if value equals default
      args:                         # for compound kind
        <arg_name>: <param_name>
```

### Example

```yaml
Canvas:
  c_handle: fdl_canvas_t
  owns_handle: false
  parent: Context
  custom_attrs: true
  pydantic_model: CanvasModel
  properties:
    id:
      getter: fdl_canvas_get_id
      type: string
    dimensions:
      getter: fdl_canvas_get_dimensions
      setter: fdl_canvas_set_dimensions
      type: fdl_dimensions_i64_t
  collections:
    framing_decisions:
      item_class: FramingDecision
      count: fdl_canvas_framing_decisions_count
      at: fdl_canvas_framing_decision_at
      add: fdl_canvas_add_framing_decision
  methods:
    to_json:
      function: fdl_canvas_to_json
      kind: instance
```

---

## `function_metadata`

Annotations for C functions that cannot be inferred from the C header alone.
Function signatures and doc strings are parsed from `fdl_core.h` by
`c_header_parser.py` at codegen time. This section adds ownership semantics,
nullability, and parameter direction.

### Schema

```yaml
function_metadata:
  <c_function_name>:
    ownership: <ownership_kind>
    nullable: <bool>                # return value is nullable
    params:
      <param_name>:
        nullable: <bool>
        direction: out              # param is output-only
```

### Ownership Kinds

| Ownership | Description |
|-----------|-------------|
| `caller_frees` | Caller must free the returned pointer with `fdl_free()` |
| `caller_frees_with_<fn>` | Caller must free with a specific function (e.g., `fdl_doc_free`) |
| `valid_until_doc_freed` | Returned handle is valid until the owning document is freed |
| `valid_until_result_freed` | Returned handle is valid until the result struct is freed |

### How It Works

The `_merge_header_overlay()` function in `fdl_idl.py`:
1. Parses all `FDL_API` function declarations from `fdl_core.h`
2. Merges metadata from this section (ownership, nullable, direction)
3. Produces `Function` objects with complete signatures + semantics

Only functions needing annotations beyond what the header provides need entries
here. Functions with no special ownership, nullability, or direction are fully
described by their C declaration.

### Example

```yaml
function_metadata:
  fdl_doc_create:
    ownership: caller_frees_with_fdl_doc_free
  fdl_doc_to_json:
    ownership: caller_frees
  fdl_context_get_clip_id:
    ownership: caller_frees
    nullable: true
  fdl_geometry_apply_offset:
    params:
      theo_eff: { direction: out }
      theo_prot: { direction: out }
```

---

## `auxiliary_types`

Defines error classes, version objects, result dataclasses, and JSON wrapper
classes that are generated in target language code but don't map to C handles.

### Schema

```yaml
auxiliary_types:
  errors:
    - name: <ErrorClass>
      parent: <ParentError>
      doc: <docstring>

  version:
    class_name: <ClassName>
    doc: <docstring>
    slots:
      - { name: <field>, type: <type>, default: <value> }

  dataclasses:
    <ClassName>:
      doc: <docstring>
      fields:
        - { name: <field>, type: <type>, private: <bool> }
      accessors:                     # optional: computed properties
        - name: <accessor_name>
          returns: <ClassName>
          doc: <docstring>
          lookup: by_id | by_label
          collection: <dotted.path>  # e.g., "fdl.contexts"
          key_field: <field_name>
```

### Example

```yaml
auxiliary_types:
  errors:
    - name: FDLError
      parent: Exception
      doc: Base error for FDL operations.
    - name: FDLValidationError
      parent: FDLError
      doc: Raised when FDL validation fails.

  dataclasses:
    TemplateResult:
      doc: Result of applying a canvas template.
      fields:
        - { name: fdl, type: object }
        - { name: context_label, type: str, private: true }
      accessors:
        - name: context
          returns: Context
          doc: The new context created by the template apply.
          lookup: by_label
          collection: fdl.contexts
          key_field: context_label
```

---

## `free_functions`

Top-level functions that don't belong to any class. These are exposed as
module-level functions in each target language.

### Schema

```yaml
free_functions:
  - name: <internal_name>
    display_name: <exported_name>
    c_function: <c_function>
    doc: <docstring>
    module: rounding | utils        # default: rounding
    params:
      - { name: <param>, type: <idl_type> }
    returns: <idl_type>
```

### Parameter and Return Types

Free function types use IDL type names (not C type names):

| IDL Type | C Type |
|----------|--------|
| `f64` | `double` |
| `double` | `double` |
| `int` | `int` |
| `float` | `double` (returned) |
| `bool` | `int` (C boolean) |
| `rounding_even` | `fdl_rounding_even_t` |
| `rounding_mode` | `fdl_rounding_mode_t` |
| `fit_method` | `fdl_fit_method_t` |
| `fdl_dimensions_i64_t` | (value type) |
| `fdl_dimensions_f64_t` | (value type) |
| `fdl_round_strategy_t` | (value type) |

### Example

```yaml
free_functions:
  - name: calculate_scale_factor
    display_name: calculate_scale_factor
    c_function: fdl_calculate_scale_factor
    doc: Calculate scale factor based on fit method.
    params:
      - { name: fit_norm, type: fdl_dimensions_f64_t }
      - { name: target_norm, type: fdl_dimensions_f64_t }
      - { name: fit_method, type: fit_method }
    returns: float
```

---

## `utilities`

Template-driven utility functions generated per target language. Unlike
`free_functions` which wrap a single C function, utilities may combine
multiple operations or provide language-specific convenience.

### Schema

```yaml
utilities:
  - name: <function_name>
    kind: <utility_kind>
    doc: <docstring>
    c_function: <c_func>           # for c_abi kind
    extract: dims | anchor         # for c_abi kind
```

### Utility Kinds

| Kind | Description |
|------|-------------|
| `c_abi` | Wraps a C function with specific result extraction (dims or anchor) |
| `collection_find` | Generic find-by-id/label on any collection |
| `io` | I/O helpers (read/write from file/string) |
| `rounding_state` | Global rounding strategy get/set |
| `constant` | Module-level constant value |

### Example

```yaml
utilities:
  - name: get_dimensions_from_path
    kind: c_abi
    c_function: fdl_resolve_geometry_layer
    extract: dims
    doc: Get dimensions from a canvas or framing decision using a GeometryPath string.
  - name: read_from_file
    kind: io
    doc: Read an FDL document from a file on disk.
```

---

## Codegen Pipeline Architecture

### Input Sources

1. **`fdl_api.yaml`** — IDL metadata (this file)
2. **`fdl_core.h`** — C function declarations + Doxygen docs
3. **`ascfdl.schema.json`** — JSON Schema (for Pydantic/TypeScript data models)

### Processing Steps

```
fdl_api.yaml  ─→  YAML parser  ─→  IDL dataclasses  ─┐
                                                       ├─→  parse_idl()  ─→  IDL + IR
fdl_core.h    ─→  c_header_parser  ─→  ParsedFunction ─┘
                                                       ↓
                                            ┌─── python_context.py ─→ *.py.j2  ─→  Python
                                      IR ───┤─── node_context.py   ─→ *.ts.j2  ─→  TypeScript
                                            └─── cpp_gen.py        ─→ *.hpp.j2 ─→  C++
```

### C Header Parser

`c_header_parser.py` extracts:
- Function signatures (`FDL_API` declarations)
- Return types and parameters
- Doxygen block comment doc strings

It matches `FDL_API` function declarations using regex, handles multi-line
declarations, pointer types, const qualifiers, and void parameter lists.

### Function Synthesis

`_synthesize_functions()` in `fdl_idl.py` auto-derives C function names from
the `object_model` section:
- Property getters/setters → `fdl_<handle>_get_<prop>`, `fdl_<handle>_set_<prop>`
- Collection operations → `fdl_<handle>_<coll>_count`, `fdl_<handle>_<coll>_at`
- Builder methods → referenced C function
- Custom attribute operations → `fdl_custom_attr_*` family

These derived function names are cross-referenced with the header-parsed
functions to produce the complete function list for FFI codegen.

### Data Model Generation

Pydantic (Python) and TypeScript data model interfaces are generated from the
JSON Schema rather than from the IDL. The `pydantic_model` field in
`object_model` classes links facade classes to their corresponding model types,
enabling `to_model()`/`from_model()` bridge methods.
