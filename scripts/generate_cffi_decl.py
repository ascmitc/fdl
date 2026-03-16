# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Generate a CFFI-compatible declaration header from fdl_core.h.

Strips preprocessor directives that CFFI cannot parse (#include, header guards,
extern "C"), removes the FDL_API export macro, expands the FDL_CUSTOM_ATTR_DECL
macro, and strips Doxygen comments. Preserves #define NAME VALUE for simple
integer constants (which CFFI supports).

Usage:
    python scripts/generate_cffi_decl.py
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_HEADER = _ROOT / "native" / "core" / "include" / "fdl" / "fdl_core.h"
_OUTPUT = _ROOT / "native" / "bindings" / "python" / "fdl_ffi" / "fdl_core_decl.h"

# Handle types and their prefixes for custom attribute macro expansion
_CUSTOM_ATTR_HANDLES = [
    ("fdl_doc_", "fdl_doc_t"),
    ("fdl_context_", "fdl_context_t"),
    ("fdl_canvas_", "fdl_canvas_t"),
    ("fdl_framing_decision_", "fdl_framing_decision_t"),
    ("fdl_framing_intent_", "fdl_framing_intent_t"),
    ("fdl_canvas_template_", "fdl_canvas_template_t"),
    ("fdl_clip_id_", "fdl_clip_id_t"),
    ("fdl_file_sequence_", "fdl_file_sequence_t"),
]

_CUSTOM_ATTR_TEMPLATE = """\
int {prefix}set_custom_attr_string({ht}* h, const char* name, const char* value);
int {prefix}set_custom_attr_int({ht}* h, const char* name, int64_t value);
int {prefix}set_custom_attr_float({ht}* h, const char* name, double value);
int {prefix}set_custom_attr_bool({ht}* h, const char* name, int value);
const char* {prefix}get_custom_attr_string(const {ht}* h, const char* name);
int {prefix}get_custom_attr_int(const {ht}* h, const char* name, int64_t* out);
int {prefix}get_custom_attr_float(const {ht}* h, const char* name, double* out);
int {prefix}get_custom_attr_bool(const {ht}* h, const char* name, int* out);
int {prefix}has_custom_attr(const {ht}* h, const char* name);
uint32_t {prefix}get_custom_attr_type(const {ht}* h, const char* name);
int {prefix}remove_custom_attr({ht}* h, const char* name);
uint32_t {prefix}custom_attrs_count(const {ht}* h);
const char* {prefix}custom_attr_name_at(const {ht}* h, uint32_t index);
int {prefix}set_custom_attr_point_f64({ht}* h, const char* name, fdl_point_f64_t value);
int {prefix}get_custom_attr_point_f64(const {ht}* h, const char* name, fdl_point_f64_t* out);
int {prefix}set_custom_attr_dims_f64({ht}* h, const char* name, fdl_dimensions_f64_t value);
int {prefix}get_custom_attr_dims_f64(const {ht}* h, const char* name, fdl_dimensions_f64_t* out);
int {prefix}set_custom_attr_dims_i64({ht}* h, const char* name, fdl_dimensions_i64_t value);
int {prefix}get_custom_attr_dims_i64(const {ht}* h, const char* name, fdl_dimensions_i64_t* out);
"""

# Lines to skip entirely
_SKIP_PATTERNS = [
    re.compile(r"^\s*#\s*ifndef\b"),
    re.compile(r"^\s*#\s*define\s+FDL_CORE_H\b"),
    re.compile(r"^\s*#\s*endif"),
    re.compile(r"^\s*#\s*include\b"),
    re.compile(r"^\s*#\s*ifdef\s+__cplusplus"),
    re.compile(r"^\s*extern\s+\"C\"\s*\{"),
    re.compile(r"^\s*\}\s*$"),
    re.compile(r"^\s*#\s*undef\b"),
    # The macro definition itself (multi-line, handled separately)
    re.compile(r"^\s*#\s*define\s+FDL_CUSTOM_ATTR_DECL\b"),
    # Macro invocations (we expand them separately)
    re.compile(r"^\s*FDL_CUSTOM_ATTR_DECL\("),
]

# String #defines that CFFI doesn't support — skip them
_STRING_DEFINE = re.compile(r'^\s*#\s*define\s+\w+\s+"')


def _strip_doxygen(text: str) -> str:
    """Remove Doxygen-style block and line comments."""
    # Block comments: /** ... */
    text = re.sub(r"/\*\*.*?\*/", "", text, flags=re.DOTALL)
    # Single-line C comments that are Doxygen: /** ... */ or /* ... */
    text = re.sub(r"/\*[^*].*?\*/", "", text, flags=re.DOTALL)
    return text


def _should_skip(line: str) -> bool:
    """Check if a line should be removed entirely."""
    return any(p.search(line) for p in _SKIP_PATTERNS)


def generate() -> str:
    """Generate CFFI-compatible declaration string from fdl_core.h."""
    header_text = _HEADER.read_text(encoding="utf-8")

    # Strip Doxygen comments first
    header_text = _strip_doxygen(header_text)

    # Remove FDL_API export macro
    header_text = header_text.replace("FDL_API ", "")

    lines = header_text.splitlines()
    out_lines: list[str] = []

    # Track multi-line macro definition to skip it entirely
    in_macro_def = False

    for line in lines:
        # Skip the multi-line macro definition
        if re.match(r"^\s*#\s*define\s+FDL_CUSTOM_ATTR_DECL\b", line):
            in_macro_def = True
            continue
        if in_macro_def:
            # Macro continues until a line doesn't end with backslash
            if line.rstrip().endswith("\\"):
                continue
            in_macro_def = False
            continue

        if _should_skip(line):
            continue

        # Skip string #defines (CFFI only supports integer #defines)
        if _STRING_DEFINE.match(line):
            continue

        out_lines.append(line)

    # Add expanded custom attribute declarations
    out_lines.append("")
    out_lines.append("/* Custom attribute functions (expanded from FDL_CUSTOM_ATTR_DECL macro) */")
    for prefix, handle_type in _CUSTOM_ATTR_HANDLES:
        out_lines.append(_CUSTOM_ATTR_TEMPLATE.format(prefix=prefix, ht=handle_type))

    # Clean up: strip trailing whitespace and collapse multiple blank lines
    result = "\n".join(line.rstrip() for line in out_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    result = result.strip() + "\n"

    return result


def main() -> None:
    decl = generate()
    _OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT.write_text(decl, encoding="utf-8")
    print(f"Generated {_OUTPUT} ({len(decl)} bytes)")


if __name__ == "__main__":
    main()
