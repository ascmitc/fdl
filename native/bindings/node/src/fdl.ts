// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT

import type { FitMethod, GeometryPath, HAlign, VAlign } from "./constants.js";
import type { RoundStrategy } from "./rounding.js";
import type { DimensionsInt } from "./types.js";
import { Version } from "./version.js";
import type { NativeAddon } from "./ffi/index.js";
import { getAddon } from "./ffi/index.js";
import { OwnedHandle, CollectionWrapper } from "./base.js";
import { toRoundStrategy } from "./converters.js";
import {
  FIT_METHOD_TO_C,
  GEOMETRY_PATH_TO_C,
  H_ALIGN_TO_C,
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
import { Context } from "./context.js";
import { FramingIntent } from "./framing-intent.js";
import { CanvasTemplate } from "./canvas-template.js";

export class FDL extends OwnedHandle {
  /** @internal */
  static override _fromHandle(
    handle: object,
    _docRef: OwnedHandle | null,
  ): FDL {
    return new FDL(handle, "fdl_doc_free");
  }

  constructor(opts: {
    uuid?: string | null;
    versionMajor?: number;
    versionMinor?: number;
    fdlCreator?: string;
    defaultFramingIntent?: string | null;
  });
  /** @internal */
  constructor(handle: object, freeFn: string);
  constructor(first: unknown, freeFn?: string) {
    if (typeof freeFn === "string") {
      super(first as object, freeFn);
      return;
    }
    const opts = first as {
      uuid?: string | null;
      versionMajor?: number;
      versionMinor?: number;
      fdlCreator?: string;
      defaultFramingIntent?: string | null;
    };
    const addon = getAddon();
    const _uuid = opts.uuid ?? crypto.randomUUID();
    const _versionMajor = opts.versionMajor ?? 2;
    const _versionMinor = opts.versionMinor ?? 0;
    const _fdlCreator = opts.fdlCreator ?? "";
    const _defaultFramingIntent = opts.defaultFramingIntent ?? null;
    const handle = addon.fdl_doc_create_with_header(
      _uuid,
      _versionMajor,
      _versionMinor,
      _fdlCreator,
      _defaultFramingIntent,
    );
    if (!handle) throw new Error("fdl_doc_create_with_header returned NULL");
    super(handle, "fdl_doc_free");
  }

  /** uuid */
  get uuid(): string | null {
    this._checkHandle();
    const raw = this._addon.fdl_doc_get_uuid(this._handle);
    return raw as string | null;
  }

  set uuid(value: string) {
    this._checkHandle();
    this._addon.fdl_doc_set_uuid(this._handle, value);
  }

  /** fdlCreator */
  get fdlCreator(): string | null {
    this._checkHandle();
    const raw = this._addon.fdl_doc_get_fdl_creator(this._handle);
    return raw as string | null;
  }

  set fdlCreator(value: string) {
    this._checkHandle();
    this._addon.fdl_doc_set_fdl_creator(this._handle, value);
  }

  /** defaultFramingIntent */
  get defaultFramingIntent(): string | null {
    this._checkHandle();
    const raw = this._addon.fdl_doc_get_default_framing_intent(this._handle);
    return raw as string | null;
  }

  set defaultFramingIntent(value: string) {
    this._checkHandle();
    this._addon.fdl_doc_set_default_framing_intent(this._handle, value);
  }

  /** versionMajor */
  get versionMajor(): number {
    this._checkHandle();
    const raw = this._addon.fdl_doc_get_version_major(this._handle);
    return raw as number;
  }

  /** versionMinor */
  get versionMinor(): number {
    this._checkHandle();
    const raw = this._addon.fdl_doc_get_version_minor(this._handle);
    return raw as number;
  }

  /** contexts collection */
  get contexts(): CollectionWrapper<Context> {
    this._checkHandle();
    return new CollectionWrapper<Context>(
      this._handle,
      this._docRef!,
      "fdl_doc_contexts_count",
      "fdl_doc_context_at",
      (h: object, d: import("./base.js").OwnedHandle) =>
        Context._fromHandle(h, d),
      undefined,
      "fdl_doc_context_find_by_label",
    );
  }

  /** framingIntents collection */
  get framingIntents(): CollectionWrapper<FramingIntent> {
    this._checkHandle();
    return new CollectionWrapper<FramingIntent>(
      this._handle,
      this._docRef!,
      "fdl_doc_framing_intents_count",
      "fdl_doc_framing_intent_at",
      (h: object, d: import("./base.js").OwnedHandle) =>
        FramingIntent._fromHandle(h, d),
      "fdl_doc_framing_intent_find_by_id",
    );
  }

  /** canvasTemplates collection */
  get canvasTemplates(): CollectionWrapper<CanvasTemplate> {
    this._checkHandle();
    return new CollectionWrapper<CanvasTemplate>(
      this._handle,
      this._docRef!,
      "fdl_doc_canvas_templates_count",
      "fdl_doc_canvas_template_at",
      (h: object, d: import("./base.js").OwnedHandle) =>
        CanvasTemplate._fromHandle(h, d),
      "fdl_doc_canvas_template_find_by_id",
    );
  }

  asDict(): Record<string, unknown> {
    this._checkHandle();
    const json = this._addon.fdl_doc_to_json(this._handle, 0);
    if (!json) throw new Error("fdl_doc_to_json returned NULL");
    return JSON.parse(json as string);
  }

  asJson(indent = 0): string {
    this._checkHandle();
    const json = this._addon.fdl_doc_to_json(this._handle, indent);
    if (!json) throw new Error("fdl_doc_to_json returned NULL");
    return json as string;
  }

  toJSON(): Record<string, unknown> {
    return this.asDict();
  }

  /** Add a framing intent to the document. */
  addFramingIntent(
    id: string,
    label: string,
    aspectRatio: DimensionsInt,
    protection: number,
  ): FramingIntent {
    this._checkHandle();
    const handle = this._addon.fdl_doc_add_framing_intent(
      this._handle,
      id,
      label,
      aspectRatio.width,
      aspectRatio.height,
      protection,
    );
    if (!handle) throw new Error("fdl_doc_add_framing_intent returned NULL");
    return FramingIntent._fromHandle(handle, this._docRef!);
  }

  /** Add a context to the document. */
  addContext(label: string, contextCreator: string | null = null): Context {
    this._checkHandle();
    const handle = this._addon.fdl_doc_add_context(
      this._handle,
      label,
      contextCreator,
    );
    if (!handle) throw new Error("fdl_doc_add_context returned NULL");
    return Context._fromHandle(handle, this._docRef!);
  }

  /** Add a canvas template to the document. */
  addCanvasTemplate(
    id: string,
    label: string,
    targetDimensions: DimensionsInt,
    targetAnamorphicSqueeze: number,
    fitSource: GeometryPath,
    fitMethod: FitMethod,
    alignmentMethodHorizontal: HAlign,
    alignmentMethodVertical: VAlign,
    round: RoundStrategy,
  ): CanvasTemplate {
    this._checkHandle();
    const handle = this._addon.fdl_doc_add_canvas_template(
      this._handle,
      id,
      label,
      targetDimensions.width,
      targetDimensions.height,
      targetAnamorphicSqueeze,
      GEOMETRY_PATH_TO_C.get(fitSource)!,
      FIT_METHOD_TO_C.get(fitMethod)!,
      H_ALIGN_TO_C.get(alignmentMethodHorizontal)!,
      V_ALIGN_TO_C.get(alignmentMethodVertical)!,
      toRoundStrategy(round),
    );
    if (!handle) throw new Error("fdl_doc_add_canvas_template returned NULL");
    return CanvasTemplate._fromHandle(handle, this._docRef!);
  }

  /** Parse JSON bytes into a facade FDL document. */
  static parse(jsonBytes: string | Buffer): FDL {
    const addon = getAddon();
    const _jsonBytes =
      typeof jsonBytes === "string" ? jsonBytes : jsonBytes.toString("utf-8");
    const result = addon.fdl_doc_parse_json(_jsonBytes, _jsonBytes.length);
    if (result.error) {
      const msg = result.error as string;
      throw new FDLValidationError(msg);
    }
    return FDL._fromHandle(result.doc, null);
  }

  /** Create a new empty FDL document with header fields. */
  static create(
    uuid: string,
    versionMajor: number = 2,
    versionMinor: number = 0,
    fdlCreator: string = "",
    defaultFramingIntent: string | null = null,
  ): FDL {
    const addon = getAddon();
    const handle = addon.fdl_doc_create_with_header(
      uuid,
      versionMajor,
      versionMinor,
      fdlCreator,
      defaultFramingIntent,
    );
    if (!handle) throw new Error("fdl_doc_create_with_header returned NULL");
    return FDL._fromHandle(handle, null);
  }

  /** Run C-core schema + semantic validation. */
  validate(): void {
    this._checkHandle();
    const vr = this._addon.fdl_doc_validate(this._handle);
    try {
      const count = this._addon.fdl_validation_result_error_count(vr) as number;
      if (count > 0) {
        const errors: string[] = [];
        for (let i = 0; i < count; i++) {
          const msg = this._addon.fdl_validation_result_error_at(vr, i);
          if (msg) errors.push(msg as string);
        }
        throw new FDLValidationError(
          "Validation failed!\n" + errors.join("\n"),
        );
      }
    } finally {
      this._addon.fdl_validation_result_free(vr);
    }
  }

  get version(): Version {
    return new Version(this.versionMajor, this.versionMinor);
  }

  private static readonly _CA_PREFIX = "fdl_doc_";

  setCustomAttr(name: string, value: CustomAttrValue): void {
    this._checkHandle();
    caSet(this._addon, this._handle, FDL._CA_PREFIX, name, value);
  }

  getCustomAttr(name: string): CustomAttrValue | null {
    this._checkHandle();
    return caGet(this._addon, this._handle, FDL._CA_PREFIX, name);
  }

  hasCustomAttr(name: string): boolean {
    this._checkHandle();
    return caHas(this._addon, this._handle, FDL._CA_PREFIX, name);
  }

  removeCustomAttr(name: string): boolean {
    this._checkHandle();
    return caRemove(this._addon, this._handle, FDL._CA_PREFIX, name);
  }

  get customAttrsCount(): number {
    this._checkHandle();
    return caCount(this._addon, this._handle, FDL._CA_PREFIX);
  }

  get customAttrs(): Record<string, CustomAttrValue> {
    this._checkHandle();
    return caGetAll(this._addon, this._handle, FDL._CA_PREFIX);
  }
}
