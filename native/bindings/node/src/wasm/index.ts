// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file wasm/index.ts
 * @brief Browser-friendly WebAssembly entry point for @asc-mitc/fdl.
 *
 * Loads the Emscripten-compiled fdl_module (Embind bindings) and installs it
 * as the active addon implementation via `setAddon()`. The same facade
 * classes used by the Node.js N-API path are re-exported here, so consumer
 * code is identical aside from the initial `await initialize()` call.
 *
 * Usage:
 *   import { initialize, FDL } from '@asc-mitc/fdl/wasm';
 *   await initialize();
 *   const doc = new FDL({ uuid: crypto.randomUUID() });
 */
import { setAddon, verifyAbi, type NativeAddon } from "../ffi/index.js";

/** Resolves once the WASM module is loaded and the addon is installed. */
let _initPromise: Promise<void> | null = null;

/**
 * Load the WASM module and install it as the active addon.
 *
 * Idempotent: subsequent calls return the same promise. Must be awaited
 * before instantiating any facade class.
 *
 * @param overrides - Optional Emscripten Module overrides (e.g. custom
 *   `locateFile` for unusual hosting setups).
 */
export async function initialize(
  overrides: Record<string, unknown> = {},
): Promise<void> {
  if (_initPromise) return _initPromise;
  _initPromise = (async () => {
    // The compiled .mjs sits two levels up from dist/wasm/index.js
    // (i.e. <package>/wasm/fdl_module.mjs). The dynamic import URL is
    // computed at runtime so bundlers don't try to inline it.
    const url = new URL("../../wasm/fdl_module.mjs", import.meta.url).href;
    const mod = await import(/* @vite-ignore */ /* webpackIgnore: true */ url);
    const factory = (mod.default ?? mod) as (
      o?: Record<string, unknown>,
    ) => Promise<Record<string, unknown>>;
    const instance = (await factory(overrides)) as unknown as NativeAddon;
    verifyAbi(instance);
    setAddon(instance);
  })();
  return _initPromise;
}

// Re-export the entire facade surface (same as the Node.js entry).
export { FDL } from "../fdl.js";
export { Canvas } from "../canvas.js";
export { CanvasTemplate } from "../canvas-template.js";
export { ClipID } from "../clip-id.js";
export { Context } from "../context.js";
export { FileSequence } from "../file-sequence.js";
export { FramingDecision } from "../framing-decision.js";
export { FramingIntent } from "../framing-intent.js";

export { DimensionsInt, DimensionsFloat, PointFloat, Rect } from "../types.js";
export { RoundStrategy } from "../rounding.js";

export {
  FitMethod,
  GeometryPath,
  HAlign,
  RoundingEven,
  RoundingMode,
  VAlign,
  FP_REL_TOL,
  FP_ABS_TOL,
  ATTR_SCALE_FACTOR,
  ATTR_CONTENT_TRANSLATION,
  ATTR_SCALED_BOUNDING_BOX,
} from "../constants.js";

export { Version } from "../version.js";

export { FDLError, FDLValidationError } from "../errors.js";

export type { CustomAttrValue } from "../custom-attrs.js";

export {
  DEFAULT_ROUNDING_STRATEGY,
  getRounding,
  setRounding,
  fdlRound,
  calculateScaleFactor,
} from "../rounding.js";

export {
  abiVersion,
  computeFramingFromIntent,
  getAnchorFromPath,
  getDimensionsFromPath,
  makeRect,
  readFromFile,
  readFromString,
  writeToFile,
  writeToString,
} from "../utils.js";

export type { FramingFromIntentResult } from "../utils.js";
export type { ResolveCanvasResult } from "../context.js";
export { TemplateResult } from "../canvas-template.js";

export { isAvailable } from "../ffi/index.js";
