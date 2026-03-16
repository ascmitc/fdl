// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file enum-maps.ts
 * @brief Bidirectional maps between C integer enum values and TypeScript enums.
 */

import {
  RoundingMode,
  RoundingEven,
  GeometryPath,
  FitMethod,
  HAlign,
  VAlign,
} from "./constants.js";

// fdl_rounding_mode_t ↔ RoundingMode
export const ROUNDING_MODE_FROM_C: Map<number, RoundingMode> = new Map([
  [0, RoundingMode.UP],
  [1, RoundingMode.DOWN],
  [2, RoundingMode.ROUND],
]);
export const ROUNDING_MODE_TO_C: Map<RoundingMode, number> = new Map(
  [...ROUNDING_MODE_FROM_C].map(([k, v]) => [v, k]),
);

// fdl_rounding_even_t ↔ RoundingEven
export const ROUNDING_EVEN_FROM_C: Map<number, RoundingEven> = new Map([
  [0, RoundingEven.WHOLE],
  [1, RoundingEven.EVEN],
]);
export const ROUNDING_EVEN_TO_C: Map<RoundingEven, number> = new Map(
  [...ROUNDING_EVEN_FROM_C].map(([k, v]) => [v, k]),
);

// fdl_geometry_path_t ↔ GeometryPath
export const GEOMETRY_PATH_FROM_C: Map<number, GeometryPath> = new Map([
  [0, GeometryPath.CANVAS_DIMENSIONS],
  [1, GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS],
  [2, GeometryPath.FRAMING_PROTECTION_DIMENSIONS],
  [3, GeometryPath.FRAMING_DIMENSIONS],
]);
export const GEOMETRY_PATH_TO_C: Map<GeometryPath, number> = new Map(
  [...GEOMETRY_PATH_FROM_C].map(([k, v]) => [v, k]),
);

// fdl_fit_method_t ↔ FitMethod
export const FIT_METHOD_FROM_C: Map<number, FitMethod> = new Map([
  [0, FitMethod.WIDTH],
  [1, FitMethod.HEIGHT],
  [2, FitMethod.FIT_ALL],
  [3, FitMethod.FILL],
]);
export const FIT_METHOD_TO_C: Map<FitMethod, number> = new Map(
  [...FIT_METHOD_FROM_C].map(([k, v]) => [v, k]),
);

// fdl_halign_t ↔ HAlign
export const H_ALIGN_FROM_C: Map<number, HAlign> = new Map([
  [0, HAlign.LEFT],
  [1, HAlign.CENTER],
  [2, HAlign.RIGHT],
]);
export const H_ALIGN_TO_C: Map<HAlign, number> = new Map(
  [...H_ALIGN_FROM_C].map(([k, v]) => [v, k]),
);

// fdl_valign_t ↔ VAlign
export const V_ALIGN_FROM_C: Map<number, VAlign> = new Map([
  [0, VAlign.TOP],
  [1, VAlign.CENTER],
  [2, VAlign.BOTTOM],
]);
export const V_ALIGN_TO_C: Map<VAlign, number> = new Map(
  [...V_ALIGN_FROM_C].map(([k, v]) => [v, k]),
);
