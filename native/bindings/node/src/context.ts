// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT

import type { DimensionsFloat, DimensionsInt } from "./types.js";
import type { NativeAddon } from "./ffi/index.js";
import { getAddon } from "./ffi/index.js";
import { HandleWrapper, OwnedHandle, CollectionWrapper } from "./base.js";
import { toDimsF64 } from "./converters.js";
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
import { ClipID } from "./clip-id.js";
import { Canvas } from "./canvas.js";
import { FramingDecision } from "./framing-decision.js";
import { FDL } from "./fdl.js";

export interface ResolveCanvasResult {
  canvas: Canvas;
  framing_decision: FramingDecision;
  was_resolved: boolean;
}

export class Context extends HandleWrapper {
  /** @internal */
  static override _fromHandle(
    handle: object,
    docRef: OwnedHandle | null,
  ): Context {
    return new Context(handle, docRef);
  }

  constructor(opts: {
    label: string;
    contextCreator?: string | null;
    canvases?: object;
  });
  /** @internal */
  constructor(handle: object, docRef: OwnedHandle | null);
  constructor(first: unknown, docRef?: OwnedHandle | null) {
    if (docRef !== undefined) {
      super(first as object, docRef);
      return;
    }
    const opts = first as {
      label: string;
      contextCreator?: string | null;
      canvases?: object;
    };
    const addon = getAddon();
    const _contextCreator = opts.contextCreator ?? null;
    const docH = addon.fdl_doc_create_with_header(
      "00000000-0000-0000-0000-000000000000",
      2,
      0,
      "_",
      null,
    );
    const backing = FDL._fromHandle(docH, null);
    const handle = addon.fdl_doc_add_context(docH, opts.label, _contextCreator);
    if (!handle) throw new Error("fdl_doc_add_context returned NULL");
    super(handle, backing);
  }

  /** label */
  get label(): string {
    this._checkHandle();
    const raw = this._addon.fdl_context_get_label(this._handle);
    return raw as string;
  }

  /** contextCreator */
  get contextCreator(): string | null {
    this._checkHandle();
    const raw = this._addon.fdl_context_get_context_creator(this._handle);
    return raw as string | null;
  }

  /** clipId */
  get clipId(): ClipID | null {
    this._checkHandle();
    if (!this._addon.fdl_context_has_clip_id(this._handle)) return null;
    const handle = this._addon.fdl_context_clip_id(this._handle);
    if (!handle) return null;
    return ClipID._fromHandle(handle, this._docRef!);
  }

  set clipId(value: ClipID | Record<string, unknown> | null) {
    this._checkHandle();
    if (value === null) {
      this._addon.fdl_context_remove_clip_id(this._handle);
      return;
    }
    const json =
      typeof value === "object" && "_handle" in value
        ? JSON.stringify((value as any).asDict())
        : JSON.stringify(value);
    const err = this._addon.fdl_context_set_clip_id_json(
      this._handle,
      json,
      json.length,
    );
    if (err) throw new Error(err as string);
  }

  /** canvases collection */
  get canvases(): CollectionWrapper<Canvas> {
    this._checkHandle();
    return new CollectionWrapper<Canvas>(
      this._handle,
      this._docRef!,
      "fdl_context_canvases_count",
      "fdl_context_canvas_at",
      (h: object, d: import("./base.js").OwnedHandle) =>
        Canvas._fromHandle(h, d),
      "fdl_context_find_canvas_by_id",
    );
  }

  equals(other: Context | string): boolean {
    if (typeof other === "string") return this.label === other;
    return this.label === other.label;
  }

  asDict(): Record<string, unknown> {
    this._checkHandle();
    const json = this._addon.fdl_context_to_json(this._handle, 0);
    if (!json) throw new Error("fdl_context_to_json returned NULL");
    return JSON.parse(json as string);
  }

  asJson(indent = 0): string {
    this._checkHandle();
    const json = this._addon.fdl_context_to_json(this._handle, indent);
    if (!json) throw new Error("fdl_context_to_json returned NULL");
    return json as string;
  }

  toJSON(): Record<string, unknown> {
    return this.asDict();
  }

  /** Add a canvas to this context. */
  addCanvas(
    id: string,
    label: string,
    sourceCanvasId: string,
    dimensions: DimensionsInt,
    anamorphicSqueeze: number,
  ): Canvas {
    this._checkHandle();
    const handle = this._addon.fdl_context_add_canvas(
      this._handle,
      id,
      label,
      sourceCanvasId,
      dimensions.width,
      dimensions.height,
      anamorphicSqueeze,
    );
    if (!handle) throw new Error("fdl_context_add_canvas returned NULL");
    return Canvas._fromHandle(handle, this._docRef!);
  }

  /** Find matching canvas when input dimensions differ from selected canvas. */
  resolveCanvasForDimensions(
    inputDims: DimensionsFloat,
    canvas: Canvas,
    framing: FramingDecision,
  ): ResolveCanvasResult {
    this._checkHandle();
    const result = this._addon.fdl_context_resolve_canvas_for_dimensions(
      this._handle,
      toDimsF64(inputDims),
      canvas._handle,
      framing._handle,
    );
    if (result.error) {
      const msg = result.error as string;
      throw new FDLValidationError(msg);
    }
    const _canvas = Canvas._fromHandle(result.canvas, this._docRef!);
    const _framing_decision = FramingDecision._fromHandle(
      result.framing_decision,
      this._docRef!,
    );
    const _was_resolved = Boolean(result.was_resolved);
    return {
      canvas: _canvas,
      framing_decision: _framing_decision,
      was_resolved: _was_resolved,
    };
  }

  private static readonly _CA_PREFIX = "fdl_context_";

  setCustomAttr(name: string, value: CustomAttrValue): void {
    this._checkHandle();
    caSet(this._addon, this._handle, Context._CA_PREFIX, name, value);
  }

  getCustomAttr(name: string): CustomAttrValue | null {
    this._checkHandle();
    return caGet(this._addon, this._handle, Context._CA_PREFIX, name);
  }

  hasCustomAttr(name: string): boolean {
    this._checkHandle();
    return caHas(this._addon, this._handle, Context._CA_PREFIX, name);
  }

  removeCustomAttr(name: string): boolean {
    this._checkHandle();
    return caRemove(this._addon, this._handle, Context._CA_PREFIX, name);
  }

  get customAttrsCount(): number {
    this._checkHandle();
    return caCount(this._addon, this._handle, Context._CA_PREFIX);
  }

  get customAttrs(): Record<string, CustomAttrValue> {
    this._checkHandle();
    return caGetAll(this._addon, this._handle, Context._CA_PREFIX);
  }
}
