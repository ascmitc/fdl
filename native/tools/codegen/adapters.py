# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Per-language adapters for code generation.

Each adapter resolves language-neutral IR concepts (type keys, defaults,
error classes, converters) into target-language strings.  Generators and
context builders receive an adapter instance instead of importing dicts
directly.
"""

from __future__ import annotations

from .ir import DefaultDescriptor


class PythonAdapter:
    """Resolve IR type keys, defaults, and errors for Python codegen."""

    TYPES: dict[str, str] = {
        "string": "str",
        "double": "float",
        "int": "int",
        "int64_t": "int",
        "uint32_t": "int",
        "bool": "bool",
        "bytes": "bytes",
        "handle": "object",
        "json_value": "object",
        "fdl_dimensions_i64_t": "DimensionsInt",
        "fdl_dimensions_f64_t": "DimensionsFloat",
        "fdl_point_f64_t": "PointFloat",
        "fdl_rect_t": "Rect",
        "fdl_round_strategy_t": "RoundStrategy",
        "fdl_geometry_path_t": "GeometryPath",
        "fdl_fit_method_t": "FitMethod",
        "fdl_halign_t": "HAlign",
        "fdl_valign_t": "VAlign",
        "fdl_geometry_t": "Geometry",
        "clip_id": "ClipID",
        "handle_ref": "object",
    }

    CONVERTERS: dict[str, str] = {
        "string": "string",
        "double": "float",
        "int": "int",
        "int64_t": "int",
        "uint32_t": "int",
        "bool": "bool",
        "json_value": "json_value",
        "fdl_dimensions_i64_t": "dims_i64",
        "fdl_dimensions_f64_t": "dims_f64",
        "fdl_point_f64_t": "point_f64",
        "fdl_rect_t": "rect",
        "fdl_round_strategy_t": "round_strategy",
        "fdl_geometry_path_t": "enum_geometry_path",
        "fdl_fit_method_t": "enum_fit_method",
        "fdl_halign_t": "enum_halign",
        "fdl_valign_t": "enum_valign",
        "clip_id": "clip_id",
        "handle_ref": "handle_ref",
    }

    ERROR_CLASSES: dict[str, str] = {
        "validation_error": "ValueError",
    }

    def resolve_type(self, type_key: str, *, nullable: bool = False) -> str:
        base = self.TYPES.get(type_key, type_key)
        if nullable:
            return f"{base} | None"
        return base

    def resolve_converter(self, type_key: str) -> str:
        return self.CONVERTERS.get(type_key, "raw")

    def resolve_error_class(self, semantic_key: str) -> str:
        return self.ERROR_CLASSES.get(semantic_key, semantic_key)

    def render_default(self, desc: DefaultDescriptor) -> str:
        if desc.kind == "none":
            return "None"
        if desc.kind == "literal":
            return desc.value or ""
        if desc.kind == "enum_member":
            return f"{desc.enum_class}.{desc.member}"
        if desc.kind == "constructor":
            if desc.constructor_kwargs:
                args = ", ".join(f"{k}={v}" for k, v in desc.constructor_kwargs.items())
                return f"{desc.constructor_class}({args})"
            return f"{desc.constructor_class}()"
        return ""


class CppAdapter:
    """Resolve IR type keys, defaults, and errors for C++ codegen."""

    TYPES: dict[str, str] = {
        "string": "std::string",
        "double": "double",
        "int": "int",
        "int64_t": "int64_t",
        "uint32_t": "uint32_t",
        "bool": "bool",
        "bytes": "std::string",
        "fdl_dimensions_i64_t": "fdl_dimensions_i64_t",
        "fdl_dimensions_f64_t": "fdl_dimensions_f64_t",
        "fdl_point_f64_t": "fdl_point_f64_t",
        "fdl_rect_t": "fdl_rect_t",
        "fdl_round_strategy_t": "fdl_round_strategy_t",
        "fdl_geometry_path_t": "fdl_geometry_path_t",
        "fdl_fit_method_t": "fdl_fit_method_t",
        "fdl_halign_t": "fdl_halign_t",
        "fdl_valign_t": "fdl_valign_t",
        "fdl_geometry_t": "fdl_geometry_t",
    }

    ERROR_CLASSES: dict[str, str] = {
        "validation_error": "std::invalid_argument",
    }

    # Enum member → C enum constant prefix map
    _ENUM_PREFIX: dict[str, str] = {
        "GeometryPath": "FDL_GEOMETRY_PATH",
        "FitMethod": "FDL_FIT_METHOD",
        "HAlign": "FDL_HALIGN",
        "VAlign": "FDL_VALIGN",
    }

    # Constructor → C++ aggregate literal
    _CONSTRUCTOR_MAP: dict[str, str] = {
        "RoundStrategy": "{FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND}",
    }

    def resolve_type(self, type_key: str, *, nullable: bool = False) -> str:
        base = self.TYPES.get(type_key, type_key)
        if nullable:
            return f"std::optional<{base}>"
        return base

    def resolve_error_class(self, semantic_key: str) -> str:
        return self.ERROR_CLASSES.get(semantic_key, semantic_key)

    def render_default(self, desc: DefaultDescriptor) -> str:
        if desc.kind == "none":
            return '""'
        if desc.kind == "literal":
            v = desc.value or ""
            if v == "False":
                return "false"
            if v == "True":
                return "true"
            return v
        if desc.kind == "enum_member":
            prefix = self._ENUM_PREFIX.get(desc.enum_class or "", "")
            return f"{prefix}_{desc.member}" if prefix else f"{desc.enum_class}_{desc.member}"
        if desc.kind == "constructor":
            return self._CONSTRUCTOR_MAP.get(desc.constructor_class or "", "{}")
        return ""
