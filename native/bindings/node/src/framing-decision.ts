// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT

import type { HAlign, VAlign } from "./constants.js";
import type { RoundStrategy } from "./rounding.js";
import type { Rect } from "./types.js";
import { DimensionsFloat, PointFloat } from "./types.js";
import type { NativeAddon } from "./ffi/index.js";
import { getAddon } from "./ffi/index.js";
import { HandleWrapper, OwnedHandle } from "./base.js";
import {
  fromDimsF64,
  fromPointF64,
  fromRect,
  toDimsF64,
  toPointF64,
  toRoundStrategy,
} from "./converters.js";
import { H_ALIGN_TO_C, V_ALIGN_TO_C } from "./enum-maps.js";
import {
  type CustomAttrValue,
  caGetAll,
  caCount,
  caGet,
  caHas,
  caRemove,
  caSet,
} from "./custom-attrs.js";
import { getRounding } from "./rounding.js";
import { Canvas } from "./canvas.js";
import { FramingIntent } from "./framing-intent.js";
import { FDL } from "./fdl.js";

export class FramingDecision extends HandleWrapper {
  /** @internal */
  static override _fromHandle(
    handle: object,
    docRef: OwnedHandle | null,
  ): FramingDecision {
    return new FramingDecision(handle, docRef);
  }

  constructor(opts: {
    id: string;
    label?: string;
    framingIntentId: string;
    dimensions?: DimensionsFloat;
    anchorPoint?: PointFloat;
    protectionDimensions?: DimensionsFloat | null;
    protectionAnchorPoint?: PointFloat | null;
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
      framingIntentId: string;
      dimensions?: DimensionsFloat;
      anchorPoint?: PointFloat;
      protectionDimensions?: DimensionsFloat | null;
      protectionAnchorPoint?: PointFloat | null;
    };
    const addon = getAddon();
    const _label = opts.label ?? "";
    const _dimensions = opts.dimensions ?? new DimensionsFloat(0.0, 0.0);
    const _anchorPoint = opts.anchorPoint ?? new PointFloat(0.0, 0.0);
    const _protectionDimensions = opts.protectionDimensions ?? null;
    const _protectionAnchorPoint = opts.protectionAnchorPoint ?? null;
    const docH = addon.fdl_doc_create_with_header(
      "00000000-0000-0000-0000-000000000000",
      2,
      0,
      "_",
      null,
    );
    const backing = FDL._fromHandle(docH, null);
    const ctxH = addon.fdl_doc_add_context(docH, "_", null);
    const canvasH = addon.fdl_context_add_canvas(
      ctxH,
      "_",
      "_",
      "_",
      1,
      1,
      1.0,
    );
    const handle = addon.fdl_canvas_add_framing_decision(
      canvasH,
      opts.id,
      _label,
      opts.framingIntentId,
      _dimensions.width,
      _dimensions.height,
      _anchorPoint.x,
      _anchorPoint.y,
    );
    if (!handle)
      throw new Error("fdl_canvas_add_framing_decision returned NULL");
    super(handle, backing);
    if (
      opts.protectionDimensions !== undefined &&
      opts.protectionDimensions !== null
    ) {
      this.setProtection(
        opts.protectionDimensions ?? new DimensionsFloat(0, 0),
        opts.protectionAnchorPoint ?? new PointFloat(0, 0),
      );
    }
  }

  /** id */
  get id(): string {
    this._checkHandle();
    const raw = this._addon.fdl_framing_decision_get_id(this._handle);
    return raw as string;
  }

  /** label */
  get label(): string {
    this._checkHandle();
    const raw = this._addon.fdl_framing_decision_get_label(this._handle);
    return raw as string;
  }

  /** framingIntentId */
  get framingIntentId(): string {
    this._checkHandle();
    const raw = this._addon.fdl_framing_decision_get_framing_intent_id(
      this._handle,
    );
    return raw as string;
  }

  /** dimensions */
  get dimensions(): DimensionsFloat {
    this._checkHandle();
    const raw = this._addon.fdl_framing_decision_get_dimensions(this._handle);
    return fromDimsF64(raw);
  }

  set dimensions(value: DimensionsFloat) {
    this._checkHandle();
    this._addon.fdl_framing_decision_set_dimensions(
      this._handle,
      toDimsF64(value),
    );
  }

  /** anchorPoint */
  get anchorPoint(): PointFloat {
    this._checkHandle();
    const raw = this._addon.fdl_framing_decision_get_anchor_point(this._handle);
    return fromPointF64(raw);
  }

  set anchorPoint(value: PointFloat) {
    this._checkHandle();
    this._addon.fdl_framing_decision_set_anchor_point(
      this._handle,
      toPointF64(value),
    );
  }

  /** protectionDimensions */
  get protectionDimensions(): DimensionsFloat | null {
    this._checkHandle();
    if (!this._addon.fdl_framing_decision_has_protection(this._handle))
      return null;
    const raw = this._addon.fdl_framing_decision_get_protection_dimensions(
      this._handle,
    );
    return fromDimsF64(raw);
  }

  set protectionDimensions(value: DimensionsFloat | null) {
    this._checkHandle();
    if (value === null) {
      this._addon.fdl_framing_decision_remove_protection(this._handle);
      return;
    }
    this._addon.fdl_framing_decision_set_protection_dimensions(
      this._handle,
      toDimsF64(value),
    );
  }

  /** protectionAnchorPoint */
  get protectionAnchorPoint(): PointFloat | null {
    this._checkHandle();
    if (!this._addon.fdl_framing_decision_has_protection(this._handle))
      return null;
    const raw = this._addon.fdl_framing_decision_get_protection_anchor_point(
      this._handle,
    );
    return fromPointF64(raw);
  }

  set protectionAnchorPoint(value: PointFloat) {
    this._checkHandle();
    this._addon.fdl_framing_decision_set_protection_anchor_point(
      this._handle,
      toPointF64(value),
    );
  }

  equals(other: FramingDecision | string): boolean {
    if (typeof other === "string") return this.id === other;
    return this.id === other.id;
  }

  asDict(): Record<string, unknown> {
    this._checkHandle();
    const json = this._addon.fdl_framing_decision_to_json(this._handle, 0);
    if (!json) throw new Error("fdl_framing_decision_to_json returned NULL");
    return JSON.parse(json as string);
  }

  asJson(indent = 0): string {
    this._checkHandle();
    const json = this._addon.fdl_framing_decision_to_json(this._handle, indent);
    if (!json) throw new Error("fdl_framing_decision_to_json returned NULL");
    return json as string;
  }

  toJSON(): Record<string, unknown> {
    return this.asDict();
  }

  /** Get framing rect as (anchor_x, anchor_y, width, height). */
  getRect(): Rect {
    this._checkHandle();
    const raw = this._addon.fdl_framing_decision_get_rect(this._handle);
    return fromRect(raw);
  }

  /** Get protection rect or None if not defined. */
  getProtectionRect(): Rect | null {
    this._checkHandle();
    const raw = this._addon.fdl_framing_decision_get_protection_rect(
      this._handle,
    );
    if (!raw || raw._return === 0) return null;
    return fromRect(raw);
  }

  /** Set protection dimensions and anchor point on this framing decision. */
  setProtection(dims: DimensionsFloat, anchor: PointFloat): void {
    this._checkHandle();
    this._addon.fdl_framing_decision_set_protection(
      this._handle,
      toDimsF64(dims),
      toPointF64(anchor),
    );
  }

  /** Adjust anchor point based on alignment within canvas. */
  adjustAnchorPoint(canvas: Canvas, hMethod: HAlign, vMethod: VAlign): void {
    this._checkHandle();
    this._addon.fdl_framing_decision_adjust_anchor(
      this._handle,
      canvas._handle,
      H_ALIGN_TO_C.get(hMethod)!,
      V_ALIGN_TO_C.get(vMethod)!,
    );
  }

  /** Adjust protection anchor point based on alignment within canvas. */
  adjustProtectionAnchorPoint(
    canvas: Canvas,
    hMethod: HAlign,
    vMethod: VAlign,
  ): void {
    this._checkHandle();
    this._addon.fdl_framing_decision_adjust_protection_anchor(
      this._handle,
      canvas._handle,
      H_ALIGN_TO_C.get(hMethod)!,
      V_ALIGN_TO_C.get(vMethod)!,
    );
  }

  /** Create a FramingDecision from a canvas and framing intent. */
  static fromFramingIntent(
    canvas: Canvas,
    framingIntent: FramingIntent,
    rounding: RoundStrategy | null = null,
  ): FramingDecision {
    if (rounding === null) {
      rounding = getRounding();
    }
    const instance = new FramingDecision({
      id: "",
      framingIntentId: framingIntent.id,
    });
    instance._addon.fdl_framing_decision_populate_from_intent(
      instance._handle,
      canvas._handle,
      framingIntent._handle,
      toRoundStrategy(rounding),
    );
    return instance;
  }

  /** Populate this framing decision from a canvas and framing intent (in-place). */
  populateFromIntent(
    canvas: Canvas,
    framingIntent: FramingIntent,
    rounding: RoundStrategy | null = null,
  ): void {
    this._checkHandle();
    if (rounding === null) {
      rounding = getRounding();
    }
    this._addon.fdl_framing_decision_populate_from_intent(
      this._handle,
      canvas._handle,
      framingIntent._handle,
      toRoundStrategy(rounding),
    );
  }

  private static readonly _CA_PREFIX = "fdl_framing_decision_";

  setCustomAttr(name: string, value: CustomAttrValue): void {
    this._checkHandle();
    caSet(this._addon, this._handle, FramingDecision._CA_PREFIX, name, value);
  }

  getCustomAttr(name: string): CustomAttrValue | null {
    this._checkHandle();
    return caGet(this._addon, this._handle, FramingDecision._CA_PREFIX, name);
  }

  hasCustomAttr(name: string): boolean {
    this._checkHandle();
    return caHas(this._addon, this._handle, FramingDecision._CA_PREFIX, name);
  }

  removeCustomAttr(name: string): boolean {
    this._checkHandle();
    return caRemove(
      this._addon,
      this._handle,
      FramingDecision._CA_PREFIX,
      name,
    );
  }

  get customAttrsCount(): number {
    this._checkHandle();
    return caCount(this._addon, this._handle, FramingDecision._CA_PREFIX);
  }

  get customAttrs(): Record<string, CustomAttrValue> {
    this._checkHandle();
    return caGetAll(this._addon, this._handle, FramingDecision._CA_PREFIX);
  }
}
