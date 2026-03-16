// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file base.ts
 * @brief Foundation classes for the FDL facade: HandleWrapper, OwnedHandle,
 *        and CollectionWrapper.
 *
 * These classes mirror the Python base.py hierarchy and provide:
 *   - HandleWrapper: non-owning facade for child handles
 *   - OwnedHandle: RAII owner (FDL class) with Symbol.dispose support
 *   - CollectionWrapper<T>: typed collection wrapping C count/at/find
 */

import type { NativeAddon } from "./ffi/index.js";
import { getAddon } from "./ffi/index.js";

// -----------------------------------------------------------------------
// HandleWrapper — non-owning facade base
// -----------------------------------------------------------------------

/**
 * Base class for all facade objects that wrap a C opaque handle.
 *
 * The handle is borrowed (not owned); the owning FDL document keeps it alive.
 * Each HandleWrapper stores a reference to its owning OwnedHandle (`_docRef`)
 * to prevent the document from being garbage collected while child handles
 * are still in use.
 */
export class HandleWrapper {
  /** @internal The opaque C handle (Napi::External). */
  _handle: object;

  /** Cached addon reference. */
  protected _addon: NativeAddon;

  /**
   * Strong reference to the owning document.
   * Prevents GC of the document while this child handle lives.
   * For OwnedHandle, this is `this` (self-referencing).
   */
  protected _docRef: OwnedHandle | null;

  /** @internal */
  constructor(handle: object, docRef: OwnedHandle | null = null) {
    this._handle = handle;
    this._addon = getAddon();
    this._docRef = docRef;
  }

  /** @internal Construct from an existing C handle. */
  static _fromHandle(
    handle: object,
    docRef: OwnedHandle | null,
  ): HandleWrapper {
    return new this(handle, docRef);
  }

  /** Check that the handle is still valid. Throws if closed. */
  protected _checkHandle(): void {
    if (this._handle === null) {
      throw new Error("Handle has been closed or freed");
    }
  }
}

// -----------------------------------------------------------------------
// OwnedHandle — RAII document owner
// -----------------------------------------------------------------------

const _registry = new FinalizationRegistry<string>((msg: string) => {
  // eslint-disable-next-line no-console
  console.warn(msg);
});

/**
 * Owning handle for FDL documents.
 *
 * Supports:
 *   - Explicit `close()` method
 *   - `using` syntax via `Symbol.dispose` (TC39 Explicit Resource Management)
 *   - FinalizationRegistry warning if not closed
 */
export class OwnedHandle extends HandleWrapper {
  private _freeFn: string;
  private _closed = false;

  /** @internal */
  constructor(handle: object, freeFn: string) {
    super(handle, null);
    this._docRef = this; // self-reference
    this._freeFn = freeFn;

    // Register GC warning
    _registry.register(
      this,
      `FDL document was garbage collected without being closed. ` +
        `Call .close() or use 'using' syntax.`,
      this,
    );
  }

  /** Release the underlying C handle. Safe to call multiple times. */
  close(): void {
    if (!this._closed && this._handle !== null) {
      this._addon[this._freeFn](this._handle);
      this._handle = null!;
      this._closed = true;
      _registry.unregister(this);
    }
  }

  /** Support `using doc = FDL.parse(...)` syntax (Symbol.dispose). */
  [Symbol.dispose](): void {
    this.close();
  }

  /** Whether this handle has been closed. */
  get isClosed(): boolean {
    return this._closed;
  }
}

// -----------------------------------------------------------------------
// CollectionWrapper<T> — typed lazy collection
// -----------------------------------------------------------------------

/**
 * Typed collection wrapping C count/at/find functions.
 *
 * Stateless: all data is fetched lazily from C at access time.
 * Stores a strong reference to the owning document to prevent GC.
 */
export class CollectionWrapper<T extends HandleWrapper> {
  private _parentHandle: object;
  private _docRef: OwnedHandle;
  private _addon: NativeAddon;

  /** C function name: returns count (uint32_t). */
  private _countFn: string;

  /** C function name: returns handle at index. */
  private _atFn: string;

  /** Optional C function: find by ID string, returns handle or null. */
  private _findByIdFn: string | null;

  /** Optional C function: find by label string, returns handle or null. */
  private _findByLabelFn: string | null;

  /** Factory to wrap raw handles into typed instances. */
  private _wrapFn: (handle: object, docRef: OwnedHandle) => T;

  constructor(
    parentHandle: object,
    docRef: OwnedHandle,
    countFn: string,
    atFn: string,
    wrapFn: (handle: object, docRef: OwnedHandle) => T,
    findByIdFn?: string,
    findByLabelFn?: string,
  ) {
    this._parentHandle = parentHandle;
    this._docRef = docRef;
    this._addon = getAddon();
    this._countFn = countFn;
    this._atFn = atFn;
    this._wrapFn = wrapFn;
    this._findByIdFn = findByIdFn ?? null;
    this._findByLabelFn = findByLabelFn ?? null;
  }

  /** Number of items in the collection. */
  get length(): number {
    return this._addon[this._countFn](this._parentHandle) as number;
  }

  /** Get item at index (0-based). Returns null if out of range. */
  at(index: number): T | null {
    const n = this.length;
    if (index < 0 || index >= n) return null;
    const h = this._addon[this._atFn](this._parentHandle, index);
    if (!h) return null;
    return this._wrapFn(h, this._docRef);
  }

  /** Find item by ID. Returns null if not found. */
  findById(id: string): T | null {
    if (!this._findByIdFn) {
      throw new Error("findById not supported on this collection");
    }
    const h = this._addon[this._findByIdFn](this._parentHandle, id);
    if (!h) return null;
    return this._wrapFn(h, this._docRef);
  }

  /** Find item by label. Returns null if not found. */
  findByLabel(label: string): T | null {
    if (!this._findByLabelFn) {
      throw new Error("findByLabel not supported on this collection");
    }
    const h = this._addon[this._findByLabelFn](this._parentHandle, label);
    if (!h) return null;
    return this._wrapFn(h, this._docRef);
  }

  /** Iterate over all items. */
  *[Symbol.iterator](): IterableIterator<T> {
    const n = this.length;
    for (let i = 0; i < n; i++) {
      const item = this.at(i);
      if (item !== null) yield item;
    }
  }

  /** Convert to array. */
  toArray(): T[] {
    return [...this];
  }
}
