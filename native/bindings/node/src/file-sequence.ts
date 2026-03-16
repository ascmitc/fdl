// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT

import type { NativeAddon } from "./ffi/index.js";
import { getAddon } from "./ffi/index.js";
import { HandleWrapper, OwnedHandle } from "./base.js";
import {
  type CustomAttrValue,
  caGetAll,
  caCount,
  caGet,
  caHas,
  caRemove,
  caSet,
} from "./custom-attrs.js";

export class FileSequence extends HandleWrapper {
  /** @internal */
  static override _fromHandle(
    handle: object,
    docRef: OwnedHandle | null,
  ): FileSequence {
    return new FileSequence(handle, docRef);
  }

  /** value */
  get value(): string {
    this._checkHandle();
    const raw = this._addon.fdl_file_sequence_get_value(this._handle);
    return raw as string;
  }

  /** idx */
  get idx(): string {
    this._checkHandle();
    const raw = this._addon.fdl_file_sequence_get_idx(this._handle);
    return raw as string;
  }

  /** min */
  get min(): number {
    this._checkHandle();
    const raw = this._addon.fdl_file_sequence_get_min(this._handle);
    return raw as number;
  }

  /** max */
  get max(): number {
    this._checkHandle();
    const raw = this._addon.fdl_file_sequence_get_max(this._handle);
    return raw as number;
  }

  asDict(): Record<string, unknown> {
    this._checkHandle();
    const d: Record<string, unknown> = {};
    d["value"] = this.value;
    d["idx"] = this.idx;
    d["min"] = this.min;
    d["max"] = this.max;
    return d;
  }

  asJson(indent = 0): string {
    return JSON.stringify(this.asDict(), null, indent || undefined);
  }

  toJSON(): Record<string, unknown> {
    return this.asDict();
  }

  private static readonly _CA_PREFIX = "fdl_file_sequence_";

  setCustomAttr(name: string, value: CustomAttrValue): void {
    this._checkHandle();
    caSet(this._addon, this._handle, FileSequence._CA_PREFIX, name, value);
  }

  getCustomAttr(name: string): CustomAttrValue | null {
    this._checkHandle();
    return caGet(this._addon, this._handle, FileSequence._CA_PREFIX, name);
  }

  hasCustomAttr(name: string): boolean {
    this._checkHandle();
    return caHas(this._addon, this._handle, FileSequence._CA_PREFIX, name);
  }

  removeCustomAttr(name: string): boolean {
    this._checkHandle();
    return caRemove(this._addon, this._handle, FileSequence._CA_PREFIX, name);
  }

  get customAttrsCount(): number {
    this._checkHandle();
    return caCount(this._addon, this._handle, FileSequence._CA_PREFIX);
  }

  get customAttrs(): Record<string, CustomAttrValue> {
    this._checkHandle();
    return caGetAll(this._addon, this._handle, FileSequence._CA_PREFIX);
  }
}
