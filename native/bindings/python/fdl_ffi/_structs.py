# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
"""FDL Core ctypes.Structure definitions."""

from __future__ import annotations

import ctypes
from typing import ClassVar


class fdl_abi_version_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("major", ctypes.c_uint32),
        ("minor", ctypes.c_uint32),
        ("patch", ctypes.c_uint32),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_abi_version_t({fields})"


class fdl_dimensions_i64_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("width", ctypes.c_int64),
        ("height", ctypes.c_int64),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_dimensions_i64_t({fields})"


class fdl_dimensions_f64_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("width", ctypes.c_double),
        ("height", ctypes.c_double),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_dimensions_f64_t({fields})"


class fdl_point_f64_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_point_f64_t({fields})"


class fdl_rect_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("width", ctypes.c_double),
        ("height", ctypes.c_double),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_rect_t({fields})"


class fdl_round_strategy_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("even", ctypes.c_uint32),
        ("mode", ctypes.c_uint32),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_round_strategy_t({fields})"


class fdl_geometry_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("canvas_dims", fdl_dimensions_f64_t),
        ("effective_dims", fdl_dimensions_f64_t),
        ("protection_dims", fdl_dimensions_f64_t),
        ("framing_dims", fdl_dimensions_f64_t),
        ("effective_anchor", fdl_point_f64_t),
        ("protection_anchor", fdl_point_f64_t),
        ("framing_anchor", fdl_point_f64_t),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_geometry_t({fields})"


class fdl_from_intent_result_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("dimensions", fdl_dimensions_f64_t),
        ("anchor_point", fdl_point_f64_t),
        ("has_protection", ctypes.c_int),
        ("protection_dimensions", fdl_dimensions_f64_t),
        ("protection_anchor_point", fdl_point_f64_t),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_from_intent_result_t({fields})"


class fdl_parse_result_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("doc", ctypes.c_void_p),
        ("error", ctypes.c_void_p),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_parse_result_t({fields})"


class fdl_template_result_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("output_fdl", ctypes.c_void_p),
        ("context_label", ctypes.c_void_p),
        ("canvas_id", ctypes.c_void_p),
        ("framing_decision_id", ctypes.c_void_p),
        ("error", ctypes.c_void_p),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_template_result_t({fields})"


class fdl_resolve_canvas_result_t(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, type]]] = [
        ("canvas", ctypes.c_void_p),
        ("framing_decision", ctypes.c_void_p),
        ("was_resolved", ctypes.c_int),
        ("error", ctypes.c_void_p),
    ]

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={getattr(self, name)}" for name, _ in self._fields_)
        return f"fdl_resolve_canvas_result_t({fields})"
