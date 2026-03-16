// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT

import type { DimensionsFloat, Rect } from "./types.js";
import { DimensionsInt, PointFloat } from "./types.js";
import type { NativeAddon } from "./ffi/index.js";
import { getAddon } from "./ffi/index.js";
import { HandleWrapper, OwnedHandle, CollectionWrapper } from "./base.js";
import {
  fromDimsF64,
  fromDimsI64,
  fromPointF64,
  fromRect,
  toDimsF64,
  toDimsI64,
  toPointF64,
} from "./converters.js";
import {
  type CustomAttrValue,
  caGetAll,
  caCount,
  caGet,
  caHas,
  caRemove,
  caSet,
} from "./custom-attrs.js";
import { FramingDecision } from "./framing-decision.js";
import { FDL } from "./fdl.js";

export class Canvas extends HandleWrapper {
  /** @internal */
  static override _fromHandle(
    handle: object,
    docRef: OwnedHandle | null,
  ): Canvas {
    return new Canvas(handle, docRef);
  }

  constructor(opts: {
    id: string;
    label?: string;
    sourceCanvasId: string;
    dimensions: DimensionsInt;
    anamorphicSqueeze?: number;
    effectiveDimensions?: DimensionsInt | null;
    effectiveAnchorPoint?: PointFloat | null;
    photositeDimensions?: DimensionsInt | null;
    physicalDimensions?: DimensionsFloat | null;
    framingDecisions?: object;
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
      sourceCanvasId: string;
      dimensions: DimensionsInt;
      anamorphicSqueeze?: number;
      effectiveDimensions?: DimensionsInt | null;
      effectiveAnchorPoint?: PointFloat | null;
      photositeDimensions?: DimensionsInt | null;
      physicalDimensions?: DimensionsFloat | null;
      framingDecisions?: object;
    };
    const addon = getAddon();
    const _label = opts.label ?? "";
    const _anamorphicSqueeze = opts.anamorphicSqueeze ?? 1.0;
    const _effectiveDimensions = opts.effectiveDimensions ?? null;
    const _effectiveAnchorPoint = opts.effectiveAnchorPoint ?? null;
    const _photositeDimensions = opts.photositeDimensions ?? null;
    const _physicalDimensions = opts.physicalDimensions ?? null;
    const docH = addon.fdl_doc_create_with_header(
      "00000000-0000-0000-0000-000000000000",
      2,
      0,
      "_",
      null,
    );
    const backing = FDL._fromHandle(docH, null);
    const ctxH = addon.fdl_doc_add_context(docH, "_", null);
    const handle = addon.fdl_context_add_canvas(
      ctxH,
      opts.id,
      _label,
      opts.sourceCanvasId,
      opts.dimensions.width,
      opts.dimensions.height,
      _anamorphicSqueeze,
    );
    if (!handle) throw new Error("fdl_context_add_canvas returned NULL");
    super(handle, backing);
    if (
      opts.effectiveDimensions !== undefined &&
      opts.effectiveDimensions !== null
    ) {
      this.setEffective(
        opts.effectiveDimensions ?? new DimensionsInt(0, 0),
        opts.effectiveAnchorPoint ?? new PointFloat(0, 0),
      );
    }
    if (
      opts.photositeDimensions !== undefined &&
      opts.photositeDimensions !== null
    ) {
      this.photositeDimensions = opts.photositeDimensions;
    }
    if (
      opts.physicalDimensions !== undefined &&
      opts.physicalDimensions !== null
    ) {
      this.physicalDimensions = opts.physicalDimensions;
    }
  }

  /** id */
  get id(): string {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_get_id(this._handle);
    return raw as string;
  }

  /** label */
  get label(): string {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_get_label(this._handle);
    return raw as string;
  }

  /** sourceCanvasId */
  get sourceCanvasId(): string {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_get_source_canvas_id(this._handle);
    return raw as string;
  }

  /** dimensions */
  get dimensions(): DimensionsInt {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_get_dimensions(this._handle);
    return fromDimsI64(raw);
  }

  set dimensions(value: DimensionsInt) {
    this._checkHandle();
    this._addon.fdl_canvas_set_dimensions(this._handle, toDimsI64(value));
  }

  /** anamorphicSqueeze */
  get anamorphicSqueeze(): number {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_get_anamorphic_squeeze(this._handle);
    return raw as number;
  }

  set anamorphicSqueeze(value: number) {
    this._checkHandle();
    this._addon.fdl_canvas_set_anamorphic_squeeze(this._handle, value);
  }

  /** effectiveDimensions */
  get effectiveDimensions(): DimensionsInt | null {
    this._checkHandle();
    if (!this._addon.fdl_canvas_has_effective_dimensions(this._handle))
      return null;
    const raw = this._addon.fdl_canvas_get_effective_dimensions(this._handle);
    return fromDimsI64(raw);
  }

  set effectiveDimensions(value: DimensionsInt | null) {
    this._checkHandle();
    if (value === null) {
      this._addon.fdl_canvas_remove_effective(this._handle);
      return;
    }
    this._addon.fdl_canvas_set_effective_dims_only(
      this._handle,
      toDimsI64(value),
    );
  }

  /** effectiveAnchorPoint */
  get effectiveAnchorPoint(): PointFloat | null {
    this._checkHandle();
    if (!this._addon.fdl_canvas_has_effective_dimensions(this._handle))
      return null;
    const raw = this._addon.fdl_canvas_get_effective_anchor_point(this._handle);
    return fromPointF64(raw);
  }

  /** photositeDimensions */
  get photositeDimensions(): DimensionsInt | null {
    this._checkHandle();
    if (!this._addon.fdl_canvas_has_photosite_dimensions(this._handle))
      return null;
    const raw = this._addon.fdl_canvas_get_photosite_dimensions(this._handle);
    return fromDimsI64(raw);
  }

  set photositeDimensions(value: DimensionsInt) {
    this._checkHandle();
    this._addon.fdl_canvas_set_photosite_dimensions(
      this._handle,
      toDimsI64(value),
    );
  }

  /** physicalDimensions */
  get physicalDimensions(): DimensionsFloat | null {
    this._checkHandle();
    if (!this._addon.fdl_canvas_has_physical_dimensions(this._handle))
      return null;
    const raw = this._addon.fdl_canvas_get_physical_dimensions(this._handle);
    return fromDimsF64(raw);
  }

  set physicalDimensions(value: DimensionsFloat) {
    this._checkHandle();
    this._addon.fdl_canvas_set_physical_dimensions(
      this._handle,
      toDimsF64(value),
    );
  }

  /** framingDecisions collection */
  get framingDecisions(): CollectionWrapper<FramingDecision> {
    this._checkHandle();
    return new CollectionWrapper<FramingDecision>(
      this._handle,
      this._docRef!,
      "fdl_canvas_framing_decisions_count",
      "fdl_canvas_framing_decision_at",
      (h: object, d: import("./base.js").OwnedHandle) =>
        FramingDecision._fromHandle(h, d),
      "fdl_canvas_find_framing_decision_by_id",
    );
  }

  equals(other: Canvas | string): boolean {
    if (typeof other === "string") return this.id === other;
    return this.id === other.id;
  }

  asDict(): Record<string, unknown> {
    this._checkHandle();
    const json = this._addon.fdl_canvas_to_json(this._handle, 0);
    if (!json) throw new Error("fdl_canvas_to_json returned NULL");
    return JSON.parse(json as string);
  }

  asJson(indent = 0): string {
    this._checkHandle();
    const json = this._addon.fdl_canvas_to_json(this._handle, indent);
    if (!json) throw new Error("fdl_canvas_to_json returned NULL");
    return json as string;
  }

  toJSON(): Record<string, unknown> {
    return this.asDict();
  }

  /** Add a framing decision to this canvas. */
  addFramingDecision(
    id: string,
    label: string,
    framingIntentId: string,
    dimensions: DimensionsFloat,
    anchorPoint: PointFloat,
  ): FramingDecision {
    this._checkHandle();
    const handle = this._addon.fdl_canvas_add_framing_decision(
      this._handle,
      id,
      label,
      framingIntentId,
      dimensions.width,
      dimensions.height,
      anchorPoint.x,
      anchorPoint.y,
    );
    if (!handle)
      throw new Error("fdl_canvas_add_framing_decision returned NULL");
    return FramingDecision._fromHandle(handle, this._docRef!);
  }

  /** Set effective dimensions and anchor point on this canvas. */
  setEffective(dims: DimensionsInt, anchor: PointFloat): void {
    this._checkHandle();
    this._addon.fdl_canvas_set_effective_dimensions(
      this._handle,
      toDimsI64(dims),
      toPointF64(anchor),
    );
  }

  /** Get canvas rect as (0, 0, width, height). */
  getRect(): Rect {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_get_rect(this._handle);
    return fromRect(raw);
  }

  /** Get effective rect or None if not defined. */
  getEffectiveRect(): Rect | null {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_get_effective_rect(this._handle);
    if (!raw || raw._return === 0) return null;
    return fromRect(raw);
  }

  private static readonly _CA_PREFIX = "fdl_canvas_";

  setCustomAttr(name: string, value: CustomAttrValue): void {
    this._checkHandle();
    caSet(this._addon, this._handle, Canvas._CA_PREFIX, name, value);
  }

  getCustomAttr(name: string): CustomAttrValue | null {
    this._checkHandle();
    return caGet(this._addon, this._handle, Canvas._CA_PREFIX, name);
  }

  hasCustomAttr(name: string): boolean {
    this._checkHandle();
    return caHas(this._addon, this._handle, Canvas._CA_PREFIX, name);
  }

  removeCustomAttr(name: string): boolean {
    this._checkHandle();
    return caRemove(this._addon, this._handle, Canvas._CA_PREFIX, name);
  }

  get customAttrsCount(): number {
    this._checkHandle();
    return caCount(this._addon, this._handle, Canvas._CA_PREFIX);
  }

  get customAttrs(): Record<string, CustomAttrValue> {
    this._checkHandle();
    return caGetAll(this._addon, this._handle, Canvas._CA_PREFIX);
  }
}
