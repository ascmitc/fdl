# FDL Core Library {#mainpage}

C reference implementation of the **ASC Framing Decision List (FDL)** specification.

## Overview

The FDL Core Library provides a pure-C ABI for parsing, creating, validating,
and serializing Framing Decision Lists. It includes geometry math utilities
and a template application engine for computing output framing from intents.

## Key API Areas

- **Document lifecycle** — `fdl_doc_create()`, `fdl_doc_parse_json()`, `fdl_doc_to_json()`, `fdl_doc_free()`
- **Tree traversal** — navigate contexts, canvases, framing decisions, and framing intents
- **Geometry math** — dimension normalization, scaling, rounding, and alignment
- **Template application** — `fdl_apply_canvas_template()` computes output framing from a canvas template and source canvas
- **Canvas resolution** — `fdl_context_resolve_canvas_for_dimensions()` finds or creates a matching canvas
- **Validation** — `fdl_doc_validate()` checks structural and semantic correctness
- **Builder API** — programmatic construction of FDL documents

All public symbols are declared in `fdl_core.h` and prefixed with `fdl_`.
