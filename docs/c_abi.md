# C ABI Design

`libfdl_core` exposes a pure C ABI through `native/core/include/fdl/fdl_core.h`.
This document describes the interface contract for anyone calling the library
directly or writing a new language binding.

For function-level documentation, see the
[Doxygen C/C++ API Reference](api/index.html).

## Opaque Handles

All domain objects are represented as **opaque pointers** to forward-declared
structs:

```c
typedef struct fdl_doc fdl_doc_t;
typedef struct fdl_context fdl_context_t;
typedef struct fdl_canvas fdl_canvas_t;
typedef struct fdl_framing_decision fdl_framing_decision_t;
typedef struct fdl_framing_intent fdl_framing_intent_t;
typedef struct fdl_canvas_template fdl_canvas_template_t;
typedef struct fdl_clip_id fdl_clip_id_t;
typedef struct fdl_file_sequence fdl_file_sequence_t;
```

**Only `fdl_doc_t*` is caller-owned.** Create it with `fdl_doc_create()` or
`fdl_doc_parse_json()`, free it with `fdl_doc_free()`.

All other handles are **borrowed pointers** into the document's internal data
structure. They are obtained via collection traversal (`fdl_doc_context_at`,
`fdl_context_canvas_at`, etc.) and remain valid until the owning document is
freed. Handles use index-based resolution and are stable across collection
mutations (e.g., `push_back`).

## Value Types

Small data structures are passed **by value** (not as opaque handles):

| Type | Fields | Usage |
|------|--------|-------|
| `fdl_dimensions_i64_t` | `width`, `height` (int64) | Canvas pixel dimensions |
| `fdl_dimensions_f64_t` | `width`, `height` (double) | Computed/intermediate dimensions |
| `fdl_point_f64_t` | `x`, `y` (double) | Anchor points, offsets |
| `fdl_rect_t` | `x`, `y`, `width`, `height` (double) | Bounding rectangles |
| `fdl_round_strategy_t` | `even`, `mode` (uint32) | Rounding configuration |
| `fdl_geometry_t` | 4 dims + 3 anchors | Template pipeline geometry container |

These are stack-allocated -- no heap management required.

## String Ownership

The ABI uses two string return conventions:

### Borrowed strings (`const char*`)

Returned by field accessors like `fdl_canvas_get_label()`. The pointer is
**thread-local** and valid until the next call for the **same field** on the
**same thread**. Do not free these.

### Caller-owned strings (`char*`)

Returned by serialization functions (`fdl_doc_to_json`, `fdl_context_to_json`,
etc.) and error messages. The caller **must free** these with `fdl_free()`.

The IDL annotates this with `ownership: caller_frees` on the relevant
functions in `fdl_api.yaml`.

## Error Handling

The ABI uses three error-reporting patterns:

**Null return** -- factory functions return `NULL` on failure:
```c
fdl_doc_t* doc = fdl_doc_create();  // NULL on allocation failure
```

**Result structs** -- operations that can fail return a struct with both a
success value and an error string:
```c
fdl_parse_result_t r = fdl_doc_parse_json(json, len);
if (r.doc)   { /* success -- caller owns r.doc */ }
if (r.error) { /* failure -- caller must fdl_free(r.error) */ }
```

**Validation result** -- `fdl_doc_validate()` returns an opaque result handle
with `error_count` + `error_at(index)`:
```c
fdl_validation_result_t* v = fdl_doc_validate(doc);
for (uint32_t i = 0; i < fdl_validation_result_error_count(v); i++)
    printf("%s\n", fdl_validation_result_error_at(v, i));
fdl_validation_result_free(v);
```

## Enums

Enums are `uint32_t` typedefs with `#define` constants using the `FDL_` prefix:

```c
typedef uint32_t fdl_rounding_mode_t;
#define FDL_ROUNDING_MODE_UP    0
#define FDL_ROUNDING_MODE_DOWN  1
#define FDL_ROUNDING_MODE_ROUND 2
```

Enum types: `fdl_rounding_mode_t`, `fdl_rounding_even_t`,
`fdl_geometry_path_t`, `fdl_fit_method_t`, `fdl_halign_t`, `fdl_valign_t`,
`fdl_custom_attr_type_t`.

## Collection Traversal

Collections follow a consistent `count` / `at` / `find_by_id` pattern:

```c
uint32_t n = fdl_doc_contexts_count(doc);
for (uint32_t i = 0; i < n; i++) {
    fdl_context_t* ctx = fdl_doc_context_at(doc, i);
    // use ctx...
}
// Or look up by identifier:
fdl_context_t* ctx = fdl_doc_context_find_by_label(doc, "Camera A");
```

## Custom Attributes

Custom attributes use a macro-generated API providing 19 functions per handle
type across all 8 handle types (152 functions total). Attribute names are passed
**without** the underscore prefix -- the library prepends `_` internally.

Type-safe: setting an attribute with a different type than its current value
returns `-1`. Remove first, then set with the new type.

## ABI Versioning

The library reports its ABI version at runtime:

```c
fdl_abi_version_t v = fdl_abi_version();
// v.major -- breaking changes
// v.minor -- backwards-compatible additions
// v.patch -- bug fixes
```

CI enforces ABI parity between `fdl_api.yaml` and the compiled library via
`python scripts/check_abi_symbols.py`.

## Thread Safety

Per-document mutex locking. See the [Architecture](architecture.md#thread-safety)
doc for details.

## Memory Management

All heap-allocated values returned by the library must be freed by the caller:

| Allocated by | Free with |
|-------------|-----------|
| `fdl_doc_create`, `fdl_doc_parse_json` | `fdl_doc_free()` |
| `fdl_apply_canvas_template` | `fdl_template_result_free()` |
| `fdl_doc_validate` | `fdl_validation_result_free()` |
| `fdl_doc_to_json`, error strings, etc. | `fdl_free()` |

`fdl_free()` is safe to call with `NULL`.
