# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Parse C function signatures and Doxygen docs from fdl_core.h.

Extracts function declarations with their return types, parameters, and
leading Doxygen doc comments. Used by the codegen pipeline to derive
Function objects from the C header instead of duplicating signatures in YAML.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedParam:
    """A single C function parameter."""

    name: str
    c_type: str  # e.g. "const fdl_doc_t*", "double", "fdl_point_f64_t*"


@dataclass
class ParsedFunction:
    """A C function extracted from the header."""

    name: str
    return_type: str  # e.g. "void", "fdl_doc_t*", "fdl_dimensions_f64_t"
    params: list[ParsedParam] = field(default_factory=list)
    doc: str = ""  # First paragraph of Doxygen block comment


# Regex to match FDL_API function declarations (possibly multi-line).
# Captures: return_type, function_name, param_list
_FDL_API_RE = re.compile(
    r"FDL_API\s+"  # FDL_API prefix
    r"([\w\s*]+?)\s+"  # return type (greedy but lazy on trailing space)
    r"(\w+)"  # function name
    r"\s*\("  # open paren
    r"([^)]*)"  # param list (everything until close paren)
    r"\)\s*;",  # close paren + semicolon
    re.DOTALL,
)

# Regex to match Doxygen block comments: /** ... */
_DOXYGEN_BLOCK_RE = re.compile(r"/\*\*\s*(.*?)\s*\*/", re.DOTALL)


def _clean_return_type(raw: str) -> str:
    """Normalize a return type string."""
    # Collapse whitespace, handle pointer spacing
    parts = raw.split()
    result = []
    for p in parts:
        result.append(p)
    s = " ".join(result)
    # Normalize pointer: "char *" -> "char*", "fdl_doc_t *" -> "fdl_doc_t*"
    s = re.sub(r"\s+\*", "*", s)
    return s


def _parse_param(raw: str) -> ParsedParam | None:
    """Parse a single parameter string like 'const fdl_doc_t* doc'."""
    raw = raw.strip()
    if not raw or raw == "void":
        return None

    # Handle function pointers (unlikely in this header, but defensive)
    if "(" in raw:
        return None

    # Split into tokens
    tokens = raw.split()
    if len(tokens) < 2:
        return None

    # The last token is the name (possibly with leading *)
    name = tokens[-1].lstrip("*")

    # Everything before the name is the type
    type_part = raw[: raw.rfind(name)].strip()

    # If name was prefixed with *, the * belongs to the type
    stars_on_name = len(tokens[-1]) - len(name)
    if stars_on_name > 0:
        type_part += "*" * stars_on_name

    # Normalize pointer spacing
    type_part = re.sub(r"\s+\*", "*", type_part)
    type_part = type_part.strip()

    return ParsedParam(name=name, c_type=type_part)


def _extract_doc(doxygen_text: str) -> str:
    """Extract the first paragraph from a Doxygen block comment body.

    Stops at the first @param, @return, @anchor, @par, @note, @ref tag
    or at a blank comment line.
    """
    lines = []
    for line in doxygen_text.splitlines():
        # Strip leading ' * ' pattern
        cleaned = re.sub(r"^\s*\*\s?", "", line).strip()
        # Stop at Doxygen tags
        if re.match(r"@(param|return|anchor|par\b|note|ref|see|brief)\b", cleaned):
            break
        # Stop at blank line (paragraph separator) if we already have content
        if not cleaned and lines:
            break
        if cleaned:
            # Strip @brief prefix if present
            cleaned = re.sub(r"^@brief\s+", "", cleaned)
            lines.append(cleaned)
    return " ".join(lines)


def parse_c_header(header_path: Path) -> dict[str, ParsedFunction]:
    """Parse fdl_core.h and return a dict mapping function name -> ParsedFunction.

    Skips:
    - FDL_CUSTOM_ATTR_DECL macro definition and invocations
    - Non-FDL_API declarations (typedefs, structs, #defines)

    Handles:
    - Multi-line declarations
    - void parameter lists
    - Pointer types and const qualifiers
    - Doxygen block comments preceding declarations
    """
    text = header_path.read_text(encoding="utf-8")

    # Remove the FDL_CUSTOM_ATTR_DECL macro definition (multi-line #define)
    text = re.sub(
        r"#define\s+FDL_CUSTOM_ATTR_DECL\b.*?(?<!\\)\n",
        "",
        text,
        flags=re.DOTALL,
    )

    # Remove FDL_CUSTOM_ATTR_DECL invocations
    text = re.sub(r"FDL_CUSTOM_ATTR_DECL\([^)]*\)", "", text)

    # Remove #undef FDL_CUSTOM_ATTR_DECL
    text = re.sub(r"#undef\s+FDL_CUSTOM_ATTR_DECL\b[^\n]*", "", text)

    # Build a map of position -> preceding Doxygen comment
    # We associate each Doxygen block with the FDL_API declaration that follows it.
    doxygen_blocks: list[tuple[int, int, str]] = []  # (start, end, doc_text)
    for m in _DOXYGEN_BLOCK_RE.finditer(text):
        doxygen_blocks.append((m.start(), m.end(), m.group(1)))

    result: dict[str, ParsedFunction] = {}

    for m in _FDL_API_RE.finditer(text):
        ret_raw = m.group(1).strip()
        func_name = m.group(2).strip()
        params_raw = m.group(3).strip()

        return_type = _clean_return_type(ret_raw)

        # Parse parameters
        params: list[ParsedParam] = []
        if params_raw and params_raw != "void":
            for p_str in params_raw.split(","):
                pp = _parse_param(p_str)
                if pp is not None:
                    params.append(pp)

        # Find the closest preceding Doxygen block
        doc = ""
        decl_start = m.start()
        for bstart, bend, btext in reversed(doxygen_blocks):
            if bend <= decl_start:
                # Check that there's only whitespace between the block end
                # and the declaration start
                between = text[bend:decl_start].strip()
                if not between:
                    doc = _extract_doc(btext)
                break

        result[func_name] = ParsedFunction(
            name=func_name,
            return_type=return_type,
            params=params,
            doc=doc,
        )

    return result
