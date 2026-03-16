// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT

import type { DimensionsInt } from "./types.js";
import type { NativeAddon } from "./ffi/index.js";
import { getAddon } from "./ffi/index.js";
import { HandleWrapper, OwnedHandle } from "./base.js";
import { fromDimsI64, toDimsI64 } from "./converters.js";
import {
  type CustomAttrValue,
  caGetAll,
  caCount,
  caGet,
  caHas,
  caRemove,
  caSet,
} from "./custom-attrs.js";
import { FDL } from "./fdl.js";

export class FramingIntent extends HandleWrapper {
  /** @internal */
  static override _fromHandle(
    handle: object,
    docRef: OwnedHandle | null,
  ): FramingIntent {
    return new FramingIntent(handle, docRef);
  }

  constructor(opts: {
    id: string;
    label?: string;
    aspectRatio: DimensionsInt;
    protection?: number;
  });
  /** @internal */
  constructor(handle: object, docRef: OwnedHandle | null);
  constructor(first: unknown, docRef?: OwnedHandle | null) {
    if (docRef !== undefined) {
      super(first as object, docRef);
      return;
    }
    const opts = first as {
      id: string;
      label?: string;
      aspectRatio: DimensionsInt;
      protection?: number;
    };
    const addon = getAddon();
    const _label = opts.label ?? "";
    const _protection = opts.protection ?? 0.0;
    const docH = addon.fdl_doc_create_with_header(
      "00000000-0000-0000-0000-000000000000",
      2,
      0,
      "_",
      null,
    );
    const backing = FDL._fromHandle(docH, null);
    const handle = addon.fdl_doc_add_framing_intent(
      docH,
      opts.id,
      _label,
      opts.aspectRatio.width,
      opts.aspectRatio.height,
      _protection,
    );
    if (!handle) throw new Error("fdl_doc_add_framing_intent returned NULL");
    super(handle, backing);
  }

  /** id */
  get id(): string {
    this._checkHandle();
    const raw = this._addon.fdl_framing_intent_get_id(this._handle);
    return raw as string;
  }

  /** label */
  get label(): string {
    this._checkHandle();
    const raw = this._addon.fdl_framing_intent_get_label(this._handle);
    return raw as string;
  }

  /** aspectRatio */
  get aspectRatio(): DimensionsInt {
    this._checkHandle();
    const raw = this._addon.fdl_framing_intent_get_aspect_ratio(this._handle);
    return fromDimsI64(raw);
  }

  set aspectRatio(value: DimensionsInt) {
    this._checkHandle();
    this._addon.fdl_framing_intent_set_aspect_ratio(
      this._handle,
      toDimsI64(value),
    );
  }

  /** protection */
  get protection(): number {
    this._checkHandle();
    const raw = this._addon.fdl_framing_intent_get_protection(this._handle);
    return raw as number;
  }

  set protection(value: number) {
    this._checkHandle();
    this._addon.fdl_framing_intent_set_protection(this._handle, value);
  }

  equals(other: FramingIntent | string): boolean {
    if (typeof other === "string") return this.id === other;
    return this.id === other.id;
  }

  asDict(): Record<string, unknown> {
    this._checkHandle();
    const json = this._addon.fdl_framing_intent_to_json(this._handle, 0);
    if (!json) throw new Error("fdl_framing_intent_to_json returned NULL");
    return JSON.parse(json as string);
  }

  asJson(indent = 0): string {
    this._checkHandle();
    const json = this._addon.fdl_framing_intent_to_json(this._handle, indent);
    if (!json) throw new Error("fdl_framing_intent_to_json returned NULL");
    return json as string;
  }

  toJSON(): Record<string, unknown> {
    return this.asDict();
  }

  private static readonly _CA_PREFIX = "fdl_framing_intent_";

  setCustomAttr(name: string, value: CustomAttrValue): void {
    this._checkHandle();
    caSet(this._addon, this._handle, FramingIntent._CA_PREFIX, name, value);
  }

  getCustomAttr(name: string): CustomAttrValue | null {
    this._checkHandle();
    return caGet(this._addon, this._handle, FramingIntent._CA_PREFIX, name);
  }

  hasCustomAttr(name: string): boolean {
    this._checkHandle();
    return caHas(this._addon, this._handle, FramingIntent._CA_PREFIX, name);
  }

  removeCustomAttr(name: string): boolean {
    this._checkHandle();
    return caRemove(this._addon, this._handle, FramingIntent._CA_PREFIX, name);
  }

  get customAttrsCount(): number {
    this._checkHandle();
    return caCount(this._addon, this._handle, FramingIntent._CA_PREFIX);
  }

  get customAttrs(): Record<string, CustomAttrValue> {
    this._checkHandle();
    return caGetAll(this._addon, this._handle, FramingIntent._CA_PREFIX);
  }
}
