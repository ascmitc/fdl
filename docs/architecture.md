# Architecture

ASC FDL is a multi-language toolkit built around a single shared C library.
This document explains how the layers fit together and why the project
is structured this way.

## Layer Diagram

```
+-----------------------------------------------------+
|                  Application Code                    |
|         (Python scripts, C++ programs, etc.)         |
+----------------------+------------------------------+
|   Python Facade      |   C++ RAII Header            |
|   fdl/               |   fdl/fdl.hpp               |
|   (idiomatic classes)|   (RAII wrapper classes)      |
+----------------------+                              |
|   Python FFI         |                              |
|   fdl_ffi/           |                              |
|   (ctypes bindings)  |                              |
+----------------------+------------------------------+
|                    C ABI                             |
|             fdl_core.h (fdl_doc_*, fdl_canvas_*, ...) |
+-----------------------------------------------------+
|              libfdl_core (C++ shared library)        |
|        native/core/src/ -- JSON parsing, validation,  |
|        geometry, templates, builder, custom attrs     |
+-----------------------------------------------------+
```

## Design Decisions

**Why a C ABI?** A stable C ABI is the most portable FFI boundary. Any
language with a foreign-function interface (Python ctypes, Node.js ffi-napi,
Rust `extern "C"`, Swift, etc.) can call C functions directly. The C++ core
compiles to a shared library (`libfdl_core.dylib`/`.so`/`.dll`) exporting
only C-linkage symbols, so binding authors never depend on C++ name mangling,
exceptions, or STL types.

**Why opaque handles?** All domain objects (documents, contexts, canvases,
framing decisions, etc.) are represented as opaque pointers (`fdl_doc_t*`,
`fdl_canvas_t*`, ...). This allows the internal C++ implementation to change
freely without breaking the ABI. Callers interact through accessor functions
rather than struct field offsets.

**Why two Python layers?** The Python binding is split into a low-level FFI
layer (`fdl_ffi/`) and a high-level facade layer (`fdl/`). Both are
auto-generated from `fdl_api.yaml` via code generation. The FFI layer is a
mechanical mapping of C function signatures to ctypes declarations -- it
contains no logic. The facade layer provides idiomatic Python classes with
properties, context managers, and Pythonic iteration. Separating the layers
means the FFI can be regenerated without touching hand-written base classes,
and the facade classes can evolve their API surface independently.

## Data Flow

```
FDL JSON file
    |
    v
fdl_doc_parse_json()          <- C ABI entry point
    |
    v
Opaque fdl_doc_t*             <- Internal: C++ FdlDocument with JSON tree
    |
    +--> fdl_doc_contexts_count / fdl_doc_context_at    <- collection traversal
    |       |
    |       v
    |   fdl_context_t*  ->  fdl_canvas_t*  ->  fdl_framing_decision_t*
    |
    v
Python: FDL (OwnedHandle)  ->  Context  ->  Canvas  ->  FramingDecision
C++:    fdl::FDL            ->  fdl::Context  -> ...
```

Parsing produces an opaque document handle. Sub-objects (contexts, canvases,
framing decisions, framing intents, canvas templates) are accessed via
index-based collection traversal: `count()` + `at(index)` + `find_by_id()`.
The Python facade wraps these in `CollectionWrapper` for Pythonic `len()`,
`[]`, and `for` iteration.

## Ownership Model

The C core uses a **document-owns-everything** model:

- `fdl_doc_t*` is the only heap-allocated handle. The caller owns it and must
  call `fdl_doc_free()` when done.
- All other handles (`fdl_context_t*`, `fdl_canvas_t*`, etc.) are
  **borrowed pointers** into the document's internal data. They are valid
  until the document is freed.
- Strings returned as `const char*` are borrowed (thread-local, valid until
  the next call for the same field on the same thread). Strings returned as
  `char*` are caller-owned and must be freed with `fdl_free()`.

The Python facade mirrors this with two base classes (defined in
`native/bindings/python/fdl/base.py`):

- **`OwnedHandle`** -- wraps `fdl_doc_t*`. Calls `fdl_doc_free()` on
  close/exit. Supports `with` statements and warns if not closed explicitly.
  Stores a `threading.Lock` for safe close operations.
- **`HandleWrapper`** -- wraps borrowed sub-object handles. Stores a
  `_doc_ref` back-reference to the owning `OwnedHandle`, preventing the
  Python garbage collector from freeing the document while child handles
  are still alive.

## Thread Safety

The C core provides **per-document mutex locking**:

- Different documents on different threads: **safe**
- Same document, concurrent reads: **safe** (serialized by mutex)
- Same document, concurrent reads + writes: **safe** (serialized)
- `fdl_doc_free()` during operations: **NOT safe** (caller must synchronize)

String accessors return thread-local pointers keyed by field name, valid until
the next call for the same field on the same thread.

The Python `OwnedHandle.close()` is protected by a `threading.Lock`.

## Core Module Map

The C++ implementation in `native/core/src/` is organized by domain:

| Module | Files | Responsibility |
|--------|-------|----------------|
| **Document** | `fdl_doc.cpp`, `fdl_doc_api.cpp` | JSON parsing, serialization, document lifecycle |
| **Validation** | `fdl_validate.cpp`, `fdl_validate_api.cpp` | JSON Schema (Draft 2020-12) + semantic validation |
| **Geometry** | `fdl_geometry.cpp`, `fdl_geometry_api.cpp` | Dimension normalization, scaling, hierarchy gap-filling, cropping |
| **Pipeline** | `fdl_pipeline.cpp`, `fdl_pipeline_api.cpp` | Scale factor calculation, output sizing, alignment shifts |
| **Template** | `fdl_template.cpp`, `fdl_template_api.cpp` | Full canvas template application pipeline |
| **Builder** | `fdl_builder.cpp`, `fdl_builder_api.cpp` | Programmatic document construction (create, add, set) |
| **Framing** | `fdl_framing.cpp`, `fdl_framing_api.cpp` | Framing-from-intent computation, anchor adjustment |
| **Custom Attrs** | `fdl_custom_attr.cpp`, `fdl_custom_attr_api.cpp` | Per-object key/value metadata (8 types, 19 functions each) |
| **Rounding** | `fdl_rounding.cpp` | Configurable rounding (even/whole, up/down/round) |
| **Handles** | `fdl_handles.cpp` | Index-based handle resolution and deduplication |
| **Canonical** | `fdl_canonical.cpp` | Key ordering per FDL specification |
| **Value Types** | `fdl_value_types.cpp` | Dimension/point arithmetic and comparison |
| **ABI** | `fdl_abi.cpp` | ABI version reporting |

Each module follows a pattern: internal implementation (`fdl_foo.cpp` with
`fdl_foo.h`) and a thin `_api.cpp` file that exposes functions through the
public C ABI header (`fdl_core.h`).

## Directory Structure

```
native/
+-- api/fdl_api.yaml           # IDL -- single source of truth
+-- core/                      # C++ shared library (CMake)
|   +-- include/fdl/fdl_core.h #   public C ABI header
|   +-- src/                   #   implementation modules
|   +-- tests/                 #   Catch2 C++ unit tests
|   +-- Doxyfile               #   Doxygen configuration
|   +-- CMakeLists.txt         #   build configuration
+-- bindings/
|   +-- python/
|   |   +-- fdl_ffi/           #   auto-generated ctypes (low-level)
|   |   +-- fdl/               #   auto-generated facade + hand-written base
|   |   +-- tests/             #   pytest suite
|   +-- cpp/
|       +-- fdl/fdl.hpp        #   auto-generated RAII header
+-- tools/
    +-- codegen/               # code generation pipeline
        +-- fdl_idl.py         #   IDL parser
        +-- ir.py              #   intermediate representation
        +-- adapters.py        #   language-specific type adapters
        +-- generate.py        #   entry point
        +-- templates/         #   Jinja2 templates (python/, cpp/)

packages/
+-- fdl_imaging/               # OpenImageIO-based image processing
+-- fdl_frameline_generator/   # frameline overlay generation
+-- fdl_viewer/                # PySide6 desktop application

schema/                        # JSON Schema definitions (v0.1-v2.0.1)
scripts/                       # build, codegen, lint, and CI utilities
```
