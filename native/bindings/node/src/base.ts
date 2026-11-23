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
// Finalization warning
// -----------------------------------------------------------------------

const _registry = new FinalizationRegistry<string>((msg: string) => {
  // eslint-disable-next-line no-console
  console.warn(msg);
});

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
 *
 * Objects built standalone (`new CanvasTemplate({...})`, `new Canvas({...})`, ...)
 * live inside a hidden backing document that they own: `close()` releases it.
 * `close()` on an object borrowed from a parsed document only invalidates that
 * object and never closes the document.
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

  /** Whether this wrapper has been closed. */
  protected _closed = false;

  /** True when `_docRef` is a hidden backing document created for this object. */
  protected _ownsDocRef = false;

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

  /**
   * @internal Take ownership of the hidden backing document of a standalone object.
   *
   * The backing document is created by the generated constructor and is not
   * visible to the caller, so the finalization warning is moved onto this
   * object, where it names the class the caller actually created.
   */
  protected _adoptBackingDoc(backing: OwnedHandle): void {
    this._ownsDocRef = true;
    _registry.unregister(backing);
    _registry.register(
      this,
      `${this.constructor.name} was garbage collected without being closed. ` +
        `Call .close() or use 'using' syntax.`,
      this,
    );
  }

  /**
   * Release this object. A standalone object also closes its hidden backing
   * document; an object borrowed from a parsed document is only invalidated.
   * Safe to call multiple times.
   */
  close(): void {
    if (this._closed) return;
    this._closed = true;
    if (this._ownsDocRef && this._docRef) {
      this._docRef.close();
    }
    this._handle = null!;
    _registry.unregister(this);
  }

  /** Support `using x = new CanvasTemplate(...)` syntax (Symbol.dispose). */
  [Symbol.dispose](): void {
    this.close();
  }

  /** Whether this object has been closed. */
  get isClosed(): boolean {
    return this._closed;
  }

  /** Check that the handle is still valid. Throws if it or its document is closed. */
  protected _checkHandle(): void {
    if (this._handle === null || this._closed) {
      throw new Error("Handle has been closed or freed");
    }
    if (
      this._docRef &&
      (this._docRef as HandleWrapper) !== this &&
      this._docRef.isClosed
    ) {
      throw new Error(
        "Handle has been closed or freed (its document is closed)",
      );
    }
  }
}

// -----------------------------------------------------------------------
// OwnedHandle — RAII document owner
// -----------------------------------------------------------------------

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
  override close(): void {
    if (!this._closed && this._handle !== null) {
      this._addon[this._freeFn](this._handle);
      this._handle = null!;
      this._closed = true;
      _registry.unregister(this);
    }
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

  /** Throws if the owning document has been closed (its handles are freed). */
  private _checkDoc(): void {
    if (this._docRef.isClosed) {
      throw new Error(
        "Handle has been closed or freed (its document is closed)",
      );
    }
  }

  /** Number of items in the collection. */
  get length(): number {
    this._checkDoc();
    return this._addon[this._countFn](this._parentHandle) as number;
  }

  /**
   * Get the item at `index` (0-based). A negative index counts from the end, as with
   * `Array.prototype.at`. Returns null when out of range (Python raises IndexError).
   */
  at(index: number): T | null {
    const n = this.length;
    const i = index < 0 ? index + n : index;
    if (i < 0 || i >= n) return null;
    const h = this._addon[this._atFn](this._parentHandle, i);
    if (!h) return null;
    return this._wrapFn(h, this._docRef);
  }

  /** Find item by ID. Returns null if not found. */
  findById(id: string): T | null {
    this._checkDoc();
    if (!this._findByIdFn) {
      throw new Error(
        "findById is not supported on this collection" +
          (this._findByLabelFn
            ? " (its items have no id; use findByLabel())"
            : ""),
      );
    }
    const h = this._addon[this._findByIdFn](this._parentHandle, id);
    if (!h) return null;
    return this._wrapFn(h, this._docRef);
  }

  /** Find item by label. Returns null if not found. */
  findByLabel(label: string): T | null {
    this._checkDoc();
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
