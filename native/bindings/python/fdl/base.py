# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Handwritten base classes for the fdl package.

Provides HandleWrapper (non-owning), OwnedHandle (RAII for FDL),
CollectionWrapper (typed collection protocol), and string/JSON helpers.
Value-type converters are now auto-generated in _converters.py.
"""

from __future__ import annotations

import threading
import warnings
from typing import Generic, TypeVar

from fdl_ffi import ffi

T = TypeVar("T")


# -----------------------------------------------------------------------
# Handle wrappers
# -----------------------------------------------------------------------


class HandleWrapper:
    """Base for non-owning facade objects (Context, Canvas, FD, FI, CT).

    Stores a borrowed C handle and a reference to the owning FDL document
    (to prevent GC from freeing the document while child handles are live).
    """

    __slots__ = ("_doc_ref", "_handle", "_lib")

    def __init__(self, handle, lib, doc_ref=None):
        self._handle = handle
        self._lib = lib
        self._doc_ref = doc_ref  # prevent GC of owning document

    @classmethod
    def _from_handle(cls, handle, lib, doc_ref=None):
        """Internal: wrap an existing C handle (bypasses subclass __init__)."""
        obj = object.__new__(cls)
        obj._handle = handle
        obj._lib = lib
        obj._doc_ref = doc_ref
        return obj

    def _check_handle(self):
        if self._handle is None:
            raise RuntimeError(f"{type(self).__name__} handle has been freed")


class OwnedHandle(HandleWrapper):
    """RAII wrapper for FDL document (owns its C handle).

    Calls ``fdl_doc_free()`` on close. Supports context manager protocol.

    Thread Safety:
        The underlying C library provides per-document mutex locking.
        Concurrent reads and writes to the same FDL document from multiple
        threads are safe. However, do not call close()/free on a document
        while other threads are still using it.
    """

    __slots__ = ("_close_lock", "_closed")

    def __init__(self, handle, lib):
        super().__init__(handle, lib, doc_ref=None)
        self._doc_ref = self  # document references itself
        self._closed = False
        self._close_lock = threading.Lock()

    @classmethod
    def _from_handle(cls, handle, lib, doc_ref=None):
        """Internal: wrap an existing C handle (bypasses subclass __init__)."""
        obj = object.__new__(cls)
        obj._handle = handle
        obj._lib = lib
        obj._doc_ref = obj  # self-referencing for documents
        obj._closed = False
        obj._close_lock = threading.Lock()
        return obj

    def close(self):
        with self._close_lock:
            if not self._closed and self._handle is not None:
                self._lib.fdl_doc_free(self._handle)
                self._handle = None
                self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        if not self._closed and self._handle is not None:
            warnings.warn(
                f"{type(self).__name__} was not closed explicitly. Use 'with' or call .close().",
                ResourceWarning,
                stacklevel=2,
            )
            self.close()


# -----------------------------------------------------------------------
# Collection wrapper
# -----------------------------------------------------------------------


class CollectionWrapper(Generic[T]):
    """Typed collection wrapping C count/at/find patterns.

    Implements the same protocol as ``TypedCollection`` (len, iter, getitem,
    contains, bool, get_by_id).
    """

    __slots__ = (
        "_at_fn",
        "_count_fn",
        "_doc_ref",
        "_find_by_id_fn",
        "_find_by_label_fn",
        "_item_cls",
        "_lib",
        "_parent_handle",
    )

    def __init__(
        self,
        lib,
        parent_handle,
        item_cls: type[T],
        count_fn,
        at_fn,
        find_by_id_fn=None,
        find_by_label_fn=None,
        doc_ref=None,
    ):
        self._lib = lib
        self._parent_handle = parent_handle
        self._item_cls = item_cls
        self._count_fn = count_fn
        self._at_fn = at_fn
        self._find_by_id_fn = find_by_id_fn
        self._find_by_label_fn = find_by_label_fn
        self._doc_ref = doc_ref

    def __len__(self) -> int:
        return self._count_fn(self._parent_handle)

    def __getitem__(self, index: int) -> T:
        length = len(self)
        if index < 0:
            index += length
        if index < 0 or index >= length:
            raise IndexError(f"index {index} out of range for collection of length {length}")
        raw = self._at_fn(self._parent_handle, index)
        return self._item_cls._from_handle(raw, self._lib, self._doc_ref)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __contains__(self, item) -> bool:
        for existing in self:
            if existing == item:
                return True
        return False

    def __bool__(self) -> bool:
        return len(self) > 0

    def get_by_id(self, id_str: str):
        """Find item by ID (or label for Context). Returns None if not found."""
        if self._find_by_id_fn is not None:
            raw = self._find_by_id_fn(self._parent_handle, id_str.encode("utf-8"))
            if raw != ffi.NULL:
                return self._item_cls._from_handle(raw, self._lib, self._doc_ref)
            return None
        if self._find_by_label_fn is not None:
            raw = self._find_by_label_fn(self._parent_handle, id_str.encode("utf-8"))
            if raw != ffi.NULL:
                return self._item_cls._from_handle(raw, self._lib, self._doc_ref)
            return None
        # Fallback: linear scan
        for item in self:
            if hasattr(item, "id") and item.id == id_str:
                return item
            if hasattr(item, "label") and item.label == id_str:
                return item
        return None

    def append(self, item):
        raise NotImplementedError("append() not supported on facade collections (read-only)")

    def remove(self, item):
        raise NotImplementedError("remove() not supported on facade collections (read-only)")


# -----------------------------------------------------------------------
# Conversion helpers
# -----------------------------------------------------------------------


def _decode_str(raw) -> str | None:
    """Decode a C const char* to Python str. Returns None if NULL."""
    if raw is None:
        return None
    if raw == ffi.NULL:
        return None
    return ffi.string(raw).decode("utf-8")


def _decode_str_free(raw, lib) -> str | None:
    """Decode a caller-owned C char* and free it. Returns None if NULL."""
    if raw is None or raw == ffi.NULL:
        return None
    result = ffi.string(raw).decode("utf-8")
    lib.fdl_free(raw)
    return result


# -----------------------------------------------------------------------
# Reverse conversion helpers (Python → C) — string only; value-type
# converters are now auto-generated in _converters.py
# -----------------------------------------------------------------------


def _encode_str(val: str) -> bytes:
    """Encode a Python str to UTF-8 bytes for C const char*."""
    return val.encode("utf-8")
