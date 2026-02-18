# Code Generation

All language bindings (Python FFI, Python facade, C++ RAII header) are
auto-generated from a single IDL file. This document explains the pipeline
and how to extend it.

## Overview

```
native/api/fdl_api.yaml        <- Single source of truth (IDL)
         |
         v
   fdl_idl.py  (parse +        <- Parsed IDL dataclasses + synthesized
                synthesize)       accessor/collection functions
         |
         v
     ir.py  (transform)        <- Language-neutral IR (IRClass, IRProperty, ...)
         |
         v
   adapters.py (resolve)       <- Language-specific type names, defaults
         |
         v
   Jinja2 templates            <- Per-language templates
         |
         +-- python-ffi  ->  native/bindings/python/fdl_ffi/
         +-- python-facade ->  native/bindings/python/fdl/
         +-- cpp-raii     ->  native/bindings/cpp/fdl/fdl.hpp
```

**Running codegen:**

```shell
python scripts/run_codegen.py           # regenerate all 3 targets + format
python scripts/run_codegen.py --check   # regenerate, then fail if output drifted
```

The script runs all three targets, formats Python output with `ruff format`,
formats C++ output with `clang-format`, and optionally checks for drift
against committed files.

## The IDL (`fdl_api.yaml`)

The IDL is a YAML file at `native/api/fdl_api.yaml`. It has four top-level
sections:

### `value_types`

Maps logical type names to their C struct equivalents:

```yaml
value_types:
  DimensionsInt:
    c_type: fdl_dimensions_i64_t
    fields: {width: int64_t, height: int64_t}
  DimensionsFloat:
    c_type: fdl_dimensions_f64_t
    fields: {width: double, height: double}
  PointFloat:
    c_type: fdl_point_f64_t
    fields: {x: double, y: double}
  # ...
```

### `enums`

Defines enum types with their members and C constant prefix:

```yaml
enums:
  RoundingMode:
    c_prefix: FDL_ROUNDING_MODE_
    members: [UP, DOWN, ROUND]
  FitMethod:
    c_prefix: FDL_FIT_METHOD_
    members: [WIDTH, HEIGHT, FIT_ALL, FILL]
  # ...
```

### `functions`

Declares C ABI functions that **cannot be derived** from `object_model` --
typically parsing, serialization, validation, template application, and other
non-accessor operations:

```yaml
functions:
  fdl_doc_parse_json:
    params:
      - {name: json_str, type: "const char*"}
      - {name: json_len, type: size_t}
    return: fdl_parse_result_t
  fdl_doc_to_json:
    params:
      - {name: doc, type: "const fdl_doc_t*"}
      - {name: indent, type: int}
    return: "char*"
    ownership: caller_frees
  # ...
```

Accessor functions (property getters/setters/has/removers) and collection
functions (count/at/find) are **synthesized automatically** from the
`object_model` section by `fdl_idl.py` -- they do not need to be listed here.
Explicit entries in `functions` take precedence over synthesized ones.

### `object_model`

Defines the class hierarchy, properties, collections, and methods that
the facade generators use:

```yaml
object_model:
  FDL:
    handle_type: fdl_doc_t
    owned: true
    properties:
      uuid: {type: string, getter: fdl_doc_get_uuid, setter: fdl_doc_set_uuid}
      # ...
    collections:
      framing_intents: {item: FramingIntent, count: ..., at: ..., find: ...}
      contexts: {item: Context, count: ..., at: ..., find: ...}
    methods:
      parse: {type: classmethod, ...}
      to_json: {...}
  Canvas:
    handle_type: fdl_canvas_t
    properties:
      dimensions: {type: DimensionsInt, getter: fdl_canvas_get_dimensions}
      # ...
```

## Pipeline Stages

### 1. Parse & Synthesize -- `fdl_idl.py`

`parse_idl(path)` reads the YAML and returns a structured `IDL` object
containing parsed value types, enums, functions, and the object model.

As a final step, `_synthesize_functions()` derives C ABI function signatures
for property accessors (getter, setter, has, remover) and collection
traversal (count, at, find_by_id, find_by_label) from the `object_model`
section. These synthesized functions are merged with the explicit `functions`
list -- explicit entries take precedence. This means adding a property to
`object_model` automatically generates the corresponding C ABI declarations
without duplicating them in the `functions` section.

### 2. Transform -- `ir.py`

The IDL object model is transformed into language-neutral IR dataclasses:

- **`IRClass`** -- one per object model class (FDL, Canvas, Context, ...)
- **`IRProperty`** -- a readable/writable property with getter/setter C function names
- **`IRCollection`** -- a typed collection (count/at/find patterns)
- **`IRMethod`** -- a class or instance method with parameters
- **`DefaultDescriptor`** -- structured default values (enum members, constructors, literals)

### 3. Resolve -- `adapters.py`

Language adapters translate IR type keys into concrete language types:

- **`PythonAdapter`** -- maps `DimensionsInt` -> `DimensionsInt`, `string` -> `str`, etc.
- **`CppAdapter`** -- maps `DimensionsInt` -> `fdl_dimensions_i64_t`, `string` -> `std::string`, etc.

Adapters also handle default value rendering (e.g., `FitMethod.WIDTH` becomes
`fdl::FitMethod::Width` in C++).

### 4. Render -- Jinja2 Templates

Templates live in `native/tools/codegen/templates/`:

**Python templates** (`templates/python/`):

| Template | Output | Purpose |
|----------|--------|---------|
| `ffi.py.j2` | `fdl_ffi/_functions.py` | ctypes function declarations |
| `structs.py.j2` | `fdl_ffi/_structs.py` | ctypes struct mappings |
| `types.py.j2` | `fdl_ffi/_types.py` | Type aliases |
| `class.py.j2` | `fdl/*.py` (one per class) | Facade class files |
| `enums.py.j2` | `fdl/fdl_types.py` | Enum classes |
| `converters.py.j2` | `fdl/converters.py` | Value-type converters |
| `constants.py.j2` | `fdl/constants.py` | Constant definitions |
| `custom_attrs.py.j2` | `fdl/_custom_attrs.py` | Custom attribute mixins |
| `errors.py.j2` | `fdl/errors.py` | Exception classes |
| `utils.py.j2` | `fdl/utils.py` | Utility functions |
| `rounding.py.j2` | `fdl/rounding.py` | Rounding strategy helpers |
| `enum_maps.py.j2` | `fdl/enum_maps.py` | Enum <-> string maps |
| `header.py.j2` | `fdl/header.py` | Version/header class |
| `clipid.py.j2` | `fdl/clip_id.py` | ClipID class |

**C++ templates** (`templates/cpp/`):

| Template | Output | Purpose |
|----------|--------|---------|
| `raii_header.hpp.j2` | `fdl/fdl.hpp` | Header-only RAII wrapper |

## Generated vs Hand-Written Files

In the Python facade (`native/bindings/python/fdl/`), almost every file is
auto-generated and marked with:

```python
# AUTO-GENERATED from fdl_api.yaml -- DO NOT EDIT
```

**Hand-written files** (safe to edit, not overwritten by codegen):

| File | Purpose |
|------|---------|
| `base.py` | `HandleWrapper`, `OwnedHandle`, `CollectionWrapper`, string helpers |
| `cli.py` | `fdl-validate` command-line tool |

Everything else in `fdl/` and all of `fdl_ffi/` is generated. Never edit
these files by hand -- your changes will be overwritten on the next codegen
run.

## How To: Add a Field to an Existing Class

1. **Edit `fdl_api.yaml`** -- add the property under the appropriate class in
   `object_model` with getter/setter function names. You do **not** need to
   add these functions to the `functions` section -- they are synthesized
   automatically.

2. **Add C ABI functions** -- implement the getter/setter in the appropriate
   `_api.cpp` file in `native/core/src/` and declare them in `fdl_core.h`.

3. **Run codegen:**
   ```shell
   python scripts/run_codegen.py
   ```

4. **Verify:** run the drift check and tests:
   ```shell
   python scripts/run_codegen.py --check
   python scripts/build_native.py --run-tests
   uv run pytest native/bindings/python/tests/ -v -n auto -p no:pytest-qt
   ```

5. **Commit** both the IDL change and the regenerated binding files.

## How To: Add a New Class

1. **Add the C implementation** -- create `fdl_foo.cpp`, `fdl_foo.h`,
   `fdl_foo_api.cpp` in `native/core/src/`. Declare the opaque handle
   and accessor functions in `fdl_core.h`.

2. **Register in `fdl_api.yaml`**:
   - Add the class to `object_model` with properties, collections, and methods
     (accessor/collection functions are synthesized automatically)
   - Add any non-accessor functions (factories, serialization, etc.) to `functions`

3. **Run codegen** -- a new facade class file will be generated automatically.

4. **Update `native/core/CMakeLists.txt`** -- add the new `.cpp` files.

5. **Write tests** -- C++ tests in `native/core/tests/`, Python tests in
   `native/bindings/python/tests/`.

## Drift Detection

CI runs `python scripts/run_codegen.py --check` to ensure committed bindings
match the IDL. If you edit `fdl_api.yaml` or any Jinja2 template, you must
regenerate and commit the output. The check will fail if:

- Generated files differ from committed versions (`git diff`)
- Untracked generated files exist
