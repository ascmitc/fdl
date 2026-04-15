// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT

import type { DimensionsInt } from "./types.js";
import { FitMethod, GeometryPath, HAlign, VAlign } from "./constants.js";
import { RoundStrategy } from "./rounding.js";
import type { NativeAddon } from "./ffi/index.js";
import { getAddon } from "./ffi/index.js";
import { HandleWrapper, OwnedHandle } from "./base.js";
import {
  fromDimsI64,
  fromRoundStrategy,
  toDimsI64,
  toRoundStrategy,
} from "./converters.js";
import {
  FIT_METHOD_FROM_C,
  FIT_METHOD_TO_C,
  GEOMETRY_PATH_FROM_C,
  GEOMETRY_PATH_TO_C,
  H_ALIGN_FROM_C,
  H_ALIGN_TO_C,
  V_ALIGN_FROM_C,
  V_ALIGN_TO_C,
} from "./enum-maps.js";
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
import { FDL } from "./fdl.js";
import { Canvas } from "./canvas.js";
import { FramingDecision } from "./framing-decision.js";
import { Context } from "./context.js";

export class TemplateResult {
  fdl: FDL;
  /** @internal */
  _context_label: string;
  /** @internal */
  _canvas_id: string;
  /** @internal */
  _framing_decision_id: string;

  constructor(
    fdl: FDL,
    _context_label: string,
    _canvas_id: string,
    _framing_decision_id: string,
  ) {
    this.fdl = fdl;
    this._context_label = _context_label;
    this._canvas_id = _canvas_id;
    this._framing_decision_id = _framing_decision_id;
  }

  /** Public accessor for _context_label. */
  get contextLabel(): string {
    return this._context_label;
  }
  /** Public accessor for _canvas_id. */
  get canvasId(): string {
    return this._canvas_id;
  }
  /** Public accessor for _framing_decision_id. */
  get framingDecisionId(): string {
    return this._framing_decision_id;
  }

  /** The new context created by the template apply. */
  get context(): Context | null {
    for (const item of this.fdl.contexts) {
      if (item.label === this._context_label) return item;
    }
    return null;
  }

  /** The new canvas created by the template apply. */
  get canvas(): Canvas | null {
    const _parent = this.context;
    if (!_parent) return null;
    for (const item of _parent.canvases) {
      if (item.id === this._canvas_id) return item;
    }
    return null;
  }

  /** The new framing decision created by the template apply. */
  get framingDecision(): FramingDecision | null {
    const _parent = this.canvas;
    if (!_parent) return null;
    for (const item of _parent.framingDecisions) {
      if (item.id === this._framing_decision_id) return item;
    }
    return null;
  }
}

export class CanvasTemplate extends HandleWrapper {
  /** @internal */
  static override _fromHandle(
    handle: object,
    docRef: OwnedHandle | null,
  ): CanvasTemplate {
    return new CanvasTemplate(handle, docRef);
  }

  constructor(opts: {
    id: string;
    label?: string;
    targetDimensions: DimensionsInt;
    targetAnamorphicSqueeze?: number;
    fitSource?: GeometryPath;
    fitMethod?: FitMethod;
    alignmentMethodHorizontal?: HAlign;
    alignmentMethodVertical?: VAlign;
    round?: RoundStrategy;
    preserveFromSourceCanvas?: GeometryPath | null;
    maximumDimensions?: DimensionsInt | null;
    padToMaximum?: boolean;
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
      targetDimensions: DimensionsInt;
      targetAnamorphicSqueeze?: number;
      fitSource?: GeometryPath;
      fitMethod?: FitMethod;
      alignmentMethodHorizontal?: HAlign;
      alignmentMethodVertical?: VAlign;
      round?: RoundStrategy;
      preserveFromSourceCanvas?: GeometryPath | null;
      maximumDimensions?: DimensionsInt | null;
      padToMaximum?: boolean;
    };
    const addon = getAddon();
    const _label = opts.label ?? "";
    const _targetAnamorphicSqueeze = opts.targetAnamorphicSqueeze ?? 1.0;
    const _fitSource = opts.fitSource ?? GeometryPath.FRAMING_DIMENSIONS;
    const _fitMethod = opts.fitMethod ?? FitMethod.WIDTH;
    const _alignmentMethodHorizontal =
      opts.alignmentMethodHorizontal ?? HAlign.CENTER;
    const _alignmentMethodVertical =
      opts.alignmentMethodVertical ?? VAlign.CENTER;
    const _round = opts.round ?? RoundStrategy.NONE;
    const _preserveFromSourceCanvas = opts.preserveFromSourceCanvas ?? null;
    const _maximumDimensions = opts.maximumDimensions ?? null;
    const _padToMaximum = opts.padToMaximum ?? false;
    const docH = addon.fdl_doc_create_with_header(
      "00000000-0000-0000-0000-000000000000",
      2,
      0,
      "_",
      null,
    );
    const backing = FDL._fromHandle(docH, null);
    const handle = addon.fdl_doc_add_canvas_template(
      docH,
      opts.id,
      _label,
      opts.targetDimensions.width,
      opts.targetDimensions.height,
      _targetAnamorphicSqueeze,
      GEOMETRY_PATH_TO_C.get(_fitSource)!,
      FIT_METHOD_TO_C.get(_fitMethod)!,
      H_ALIGN_TO_C.get(_alignmentMethodHorizontal)!,
      V_ALIGN_TO_C.get(_alignmentMethodVertical)!,
      toRoundStrategy(_round),
    );
    if (!handle) throw new Error("fdl_doc_add_canvas_template returned NULL");
    super(handle, backing);
    if (
      opts.preserveFromSourceCanvas !== undefined &&
      opts.preserveFromSourceCanvas !== null
    ) {
      this.preserveFromSourceCanvas = opts.preserveFromSourceCanvas;
    }
    if (
      opts.maximumDimensions !== undefined &&
      opts.maximumDimensions !== null
    ) {
      this.maximumDimensions = opts.maximumDimensions;
    }
    this.padToMaximum = opts.padToMaximum ?? false;
  }

  /** id */
  get id(): string {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_id(this._handle);
    return raw as string;
  }

  /** label */
  get label(): string {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_label(this._handle);
    return raw as string;
  }

  /** targetDimensions */
  get targetDimensions(): DimensionsInt {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_target_dimensions(
      this._handle,
    );
    return fromDimsI64(raw);
  }

  /** targetAnamorphicSqueeze */
  get targetAnamorphicSqueeze(): number {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_target_anamorphic_squeeze(
      this._handle,
    );
    return raw as number;
  }

  /** fitSource */
  get fitSource(): GeometryPath {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_fit_source(this._handle);
    return GEOMETRY_PATH_FROM_C.get(raw as number)!;
  }

  /** fitMethod */
  get fitMethod(): FitMethod {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_fit_method(this._handle);
    return FIT_METHOD_FROM_C.get(raw as number)!;
  }

  /** alignmentMethodHorizontal */
  get alignmentMethodHorizontal(): HAlign {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_alignment_method_horizontal(
      this._handle,
    );
    return H_ALIGN_FROM_C.get(raw as number)!;
  }

  /** alignmentMethodVertical */
  get alignmentMethodVertical(): VAlign {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_alignment_method_vertical(
      this._handle,
    );
    return V_ALIGN_FROM_C.get(raw as number)!;
  }

  /** round */
  get round(): RoundStrategy {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_round(this._handle);
    return fromRoundStrategy(raw);
  }

  /** preserveFromSourceCanvas */
  get preserveFromSourceCanvas(): GeometryPath | null {
    this._checkHandle();
    if (
      !this._addon.fdl_canvas_template_has_preserve_from_source_canvas(
        this._handle,
      )
    )
      return null;
    const raw = this._addon.fdl_canvas_template_get_preserve_from_source_canvas(
      this._handle,
    );
    return GEOMETRY_PATH_FROM_C.get(raw as number) ?? null;
  }

  set preserveFromSourceCanvas(value: GeometryPath) {
    this._checkHandle();
    this._addon.fdl_canvas_template_set_preserve_from_source_canvas(
      this._handle,
      GEOMETRY_PATH_TO_C.get(value)!,
    );
  }

  /** maximumDimensions */
  get maximumDimensions(): DimensionsInt | null {
    this._checkHandle();
    if (!this._addon.fdl_canvas_template_has_maximum_dimensions(this._handle))
      return null;
    const raw = this._addon.fdl_canvas_template_get_maximum_dimensions(
      this._handle,
    );
    return fromDimsI64(raw);
  }

  set maximumDimensions(value: DimensionsInt) {
    this._checkHandle();
    this._addon.fdl_canvas_template_set_maximum_dimensions(
      this._handle,
      toDimsI64(value),
    );
  }

  /** padToMaximum */
  get padToMaximum(): boolean {
    this._checkHandle();
    const raw = this._addon.fdl_canvas_template_get_pad_to_maximum(
      this._handle,
    );
    return Boolean(raw);
  }

  set padToMaximum(value: boolean) {
    this._checkHandle();
    this._addon.fdl_canvas_template_set_pad_to_maximum(
      this._handle,
      value ? 1 : 0,
    );
  }

  equals(other: CanvasTemplate | string): boolean {
    if (typeof other === "string") return this.id === other;
    return this.id === other.id;
  }

  asDict(): Record<string, unknown> {
    this._checkHandle();
    const json = this._addon.fdl_canvas_template_to_json(this._handle, 0);
    if (!json) throw new Error("fdl_canvas_template_to_json returned NULL");
    return JSON.parse(json as string);
  }

  asJson(indent = 0): string {
    this._checkHandle();
    const json = this._addon.fdl_canvas_template_to_json(this._handle, indent);
    if (!json) throw new Error("fdl_canvas_template_to_json returned NULL");
    return json as string;
  }

  toJSON(): Record<string, unknown> {
    return this.asDict();
  }

  /** Apply this canvas template to a source canvas/framing decision. */
  apply(
    sourceCanvas: Canvas,
    sourceFraming: FramingDecision,
    newCanvasId: string,
    newFdName: string,
    sourceContextLabel: string | null = null,
    contextCreator: string | null = null,
  ): TemplateResult {
    this._checkHandle();
    const result = this._addon.fdl_apply_canvas_template(
      this._handle,
      sourceCanvas._handle,
      sourceFraming._handle,
      newCanvasId,
      newFdName,
      sourceContextLabel,
      contextCreator,
    );
    if (result.error) {
      const msg = result.error as string;
      throw new FDLValidationError(msg);
    }
    const _fdl = FDL._fromHandle(result.output_fdl, null);
    const _context_label = result.context_label as string;
    const _canvas_id = result.canvas_id as string;
    const _framing_decision_id = result.framing_decision_id as string;
    return new TemplateResult(
      _fdl,
      _context_label,
      _canvas_id,
      _framing_decision_id,
    );
  }

  private static readonly _CA_PREFIX = "fdl_canvas_template_";

  setCustomAttr(name: string, value: CustomAttrValue): void {
    this._checkHandle();
    caSet(this._addon, this._handle, CanvasTemplate._CA_PREFIX, name, value);
  }

  getCustomAttr(name: string): CustomAttrValue | null {
    this._checkHandle();
    return caGet(this._addon, this._handle, CanvasTemplate._CA_PREFIX, name);
  }

  hasCustomAttr(name: string): boolean {
    this._checkHandle();
    return caHas(this._addon, this._handle, CanvasTemplate._CA_PREFIX, name);
  }

  removeCustomAttr(name: string): boolean {
    this._checkHandle();
    return caRemove(this._addon, this._handle, CanvasTemplate._CA_PREFIX, name);
  }

  get customAttrsCount(): number {
    this._checkHandle();
    return caCount(this._addon, this._handle, CanvasTemplate._CA_PREFIX);
  }

  get customAttrs(): Record<string, CustomAttrValue> {
    this._checkHandle();
    return caGetAll(this._addon, this._handle, CanvasTemplate._CA_PREFIX);
  }
}
