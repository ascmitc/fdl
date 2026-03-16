# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
fdl_ffi — CFFI bindings for libfdl_core.

Usage:
    from fdl_ffi import get_lib, ffi

    lib = get_lib()
    ver = lib.fdl_abi_version()
    print(f"ABI {ver.major}.{ver.minor}.{ver.patch}")
"""

from __future__ import annotations

import threading
from pathlib import Path

from cffi import FFI

from ._loader import find_library

# -- CFFI setup ---------------------------------------------------------------

ffi = FFI()

_DECL_PATH = Path(__file__).parent / "fdl_core_decl.h"
ffi.cdef(_DECL_PATH.read_text(encoding="utf-8"))

# -- Enum constants (stable ABI values) ---------------------------------------
# These are #define constants in fdl_core.h. CFFI parses them in cdef but
# doesn't expose them as Python attributes in ABI mode, so we define them here.

# fdl_rounding_mode_t
FDL_ROUNDING_MODE_UP = 0
FDL_ROUNDING_MODE_DOWN = 1
FDL_ROUNDING_MODE_ROUND = 2

# fdl_rounding_even_t
FDL_ROUNDING_EVEN_WHOLE = 0
FDL_ROUNDING_EVEN_EVEN = 1

# fdl_geometry_path_t
FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS = 0
FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS = 1
FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS = 2
FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS = 3

# fdl_fit_method_t
FDL_FIT_METHOD_WIDTH = 0
FDL_FIT_METHOD_HEIGHT = 1
FDL_FIT_METHOD_FIT_ALL = 2
FDL_FIT_METHOD_FILL = 3

# fdl_halign_t
FDL_HALIGN_LEFT = 0
FDL_HALIGN_CENTER = 1
FDL_HALIGN_RIGHT = 2

# fdl_valign_t
FDL_VALIGN_TOP = 0
FDL_VALIGN_CENTER = 1
FDL_VALIGN_BOTTOM = 2

# fdl_custom_attr_type_t
FDL_CUSTOM_ATTR_TYPE_NONE = 0
FDL_CUSTOM_ATTR_TYPE_STRING = 1
FDL_CUSTOM_ATTR_TYPE_INT = 2
FDL_CUSTOM_ATTR_TYPE_FLOAT = 3
FDL_CUSTOM_ATTR_TYPE_BOOL = 4
FDL_CUSTOM_ATTR_TYPE_POINT_F64 = 5
FDL_CUSTOM_ATTR_TYPE_DIMS_F64 = 6
FDL_CUSTOM_ATTR_TYPE_DIMS_I64 = 7
FDL_CUSTOM_ATTR_TYPE_OTHER = 8

# -- Library loading ----------------------------------------------------------

# Expected ABI compatibility range
_ABI_MAJOR = 0
_ABI_MINOR_MIN = 3

_lib = None
_lib_lock = threading.Lock()


def get_lib():
    """Get the loaded library singleton (thread-safe)."""
    global _lib
    if _lib is None:
        with _lib_lock:
            if _lib is None:
                _lib = _load_and_verify()
    return _lib


def _load_and_verify():
    lib_path = find_library()
    lib = ffi.dlopen(str(lib_path))

    # ABI version check
    ver = lib.fdl_abi_version()
    if ver.major != _ABI_MAJOR or ver.minor < _ABI_MINOR_MIN:
        msg = f"fdl_core ABI {ver.major}.{ver.minor}.{ver.patch} is incompatible. Expected {_ABI_MAJOR}.>={_ABI_MINOR_MIN}.x"
        raise RuntimeError(msg)

    return lib


def is_available() -> bool:
    """Check if libfdl_core can be loaded without raising."""
    try:
        get_lib()
        return True
    except (OSError, RuntimeError):
        return False
