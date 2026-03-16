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
import { FDLValidationError } from "./errors.js";
import { FileSequence } from "./file-sequence.js";

export class ClipID extends HandleWrapper {
  /** @internal */
  static override _fromHandle(
    handle: object,
    docRef: OwnedHandle | null,
  ): ClipID {
    return new ClipID(handle, docRef);
  }

  /** clipName */
  get clipName(): string {
    this._checkHandle();
    const raw = this._addon.fdl_clip_id_get_clip_name(this._handle);
    return raw as string;
  }

  /** file */
  get file(): string | null {
    this._checkHandle();
    if (!this._addon.fdl_clip_id_has_file(this._handle)) return null;
    const raw = this._addon.fdl_clip_id_get_file(this._handle);
    return raw as string | null;
  }

  /** sequence */
  get sequence(): FileSequence | null {
    this._checkHandle();
    if (!this._addon.fdl_clip_id_has_sequence(this._handle)) return null;
    const handle = this._addon.fdl_clip_id_sequence(this._handle);
    if (!handle) return null;
    return FileSequence._fromHandle(handle, this._docRef!);
  }

  asDict(): Record<string, unknown> {
    this._checkHandle();
    const json = this._addon.fdl_clip_id_to_json(this._handle, 0);
    if (!json) throw new Error("fdl_clip_id_to_json returned NULL");
    return JSON.parse(json as string);
  }

  asJson(indent = 0): string {
    this._checkHandle();
    const json = this._addon.fdl_clip_id_to_json(this._handle, indent);
    if (!json) throw new Error("fdl_clip_id_to_json returned NULL");
    return json as string;
  }

  toJSON(): Record<string, unknown> {
    return this.asDict();
  }

  validate(): void {
    this._checkHandle();
    const json = this._addon.fdl_clip_id_to_json(this._handle, 0);
    if (!json) throw new Error("fdl_clip_id_to_json returned NULL");
    const err = this._addon.fdl_clip_id_validate_json(
      json as string,
      (json as string).length,
    );
    if (err) {
      throw new FDLValidationError(err as string);
    }
  }

  private static readonly _CA_PREFIX = "fdl_clip_id_";

  setCustomAttr(name: string, value: CustomAttrValue): void {
    this._checkHandle();
    caSet(this._addon, this._handle, ClipID._CA_PREFIX, name, value);
  }

  getCustomAttr(name: string): CustomAttrValue | null {
    this._checkHandle();
    return caGet(this._addon, this._handle, ClipID._CA_PREFIX, name);
  }

  hasCustomAttr(name: string): boolean {
    this._checkHandle();
    return caHas(this._addon, this._handle, ClipID._CA_PREFIX, name);
  }

  removeCustomAttr(name: string): boolean {
    this._checkHandle();
    return caRemove(this._addon, this._handle, ClipID._CA_PREFIX, name);
  }

  get customAttrsCount(): number {
    this._checkHandle();
    return caCount(this._addon, this._handle, ClipID._CA_PREFIX);
  }

  get customAttrs(): Record<string, CustomAttrValue> {
    this._checkHandle();
    return caGetAll(this._addon, this._handle, ClipID._CA_PREFIX);
  }
}
