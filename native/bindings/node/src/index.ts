// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file index.ts
 * @brief Public API for @asc-mitc/fdl — re-exports all facade classes, types, and utilities.
 */

// Register the N-API loader (Node.js entry only). This side-effect import wires
// the native addon into the backend-agnostic registry so getAddon() can lazily
// load it. The browser/WASM entry (./wasm/index.ts) never imports this module.
import "./ffi/loader-node.js";

// Facade classes
export { FDL } from "./fdl.js";
export { Canvas } from "./canvas.js";
export { CanvasTemplate } from "./canvas-template.js";
export { ClipID } from "./clip-id.js";
export { Context } from "./context.js";
export { FileSequence } from "./file-sequence.js";
export { FramingDecision } from "./framing-decision.js";
export { FramingIntent } from "./framing-intent.js";

// Value types
export { DimensionsInt, DimensionsFloat, PointFloat, Rect } from "./types.js";
export { RoundStrategy } from "./rounding.js";

// Enums and constants
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
} from "./constants.js";

// Version
export { Version } from "./version.js";

// Errors
export { FDLError } from "./errors.js";
export { FDLValidationError } from "./errors.js";

// Custom attribute value type
export type { CustomAttrValue } from "./custom-attrs.js";

// Rounding functions
export {
  DEFAULT_ROUNDING_STRATEGY,
  getRounding,
  setRounding,
  fdlRound,
  calculateScaleFactor,
} from "./rounding.js";

// Utility functions
export {
  abiVersion,
  computeFramingFromIntent,
  getAnchorFromPath,
  getDimensionsFromPath,
  makeRect,
  readFromString,
  writeToString,
} from "./utils.js";

// Node.js-only file I/O (uses node:fs; not exported from the browser/WASM entry)
export { readFromFile, writeToFile } from "./utils-node.js";

// Utility types
export type { FramingFromIntentResult } from "./utils.js";

// Result types
export type { ResolveCanvasResult } from "./context.js";
export { TemplateResult } from "./canvas-template.js";

// FFI availability check
export { isAvailable } from "./ffi/index.js";
