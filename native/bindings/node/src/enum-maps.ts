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

/**
 * Facade enum -> C integer map. `require()` rejects a value that is not a member,
 * so a bad enum string raises the same TypeError on every backend instead of
 * reaching the addon as `undefined` (N-API threw by accident; WASM accepted it).
 */
export class EnumToC<E> extends Map<E, number> {
  private readonly enumName: string;

  constructor(enumName: string, entries: Iterable<readonly [E, number]>) {
    super(entries);
    this.enumName = enumName;
  }

  require(value: unknown): number {
    const c = this.get(value as E);
    if (c === undefined) {
      const allowed = [...this.keys()].map((k) => JSON.stringify(k)).join(", ");
      throw new TypeError(
        `Invalid ${this.enumName} value: ${JSON.stringify(value)} (expected one of: ${allowed})`,
      );
    }
    return c;
  }
}

// fdl_rounding_mode_t ↔ RoundingMode
export const ROUNDING_MODE_FROM_C: Map<number, RoundingMode> = new Map([
  [0, RoundingMode.UP],
  [1, RoundingMode.DOWN],
  [2, RoundingMode.ROUND],
]);
export const ROUNDING_MODE_TO_C: EnumToC<RoundingMode> = new EnumToC(
  "RoundingMode",
  [...ROUNDING_MODE_FROM_C].map(([k, v]) => [v, k] as [RoundingMode, number]),
);

// fdl_rounding_even_t ↔ RoundingEven
export const ROUNDING_EVEN_FROM_C: Map<number, RoundingEven> = new Map([
  [0, RoundingEven.WHOLE],
  [1, RoundingEven.EVEN],
]);
export const ROUNDING_EVEN_TO_C: EnumToC<RoundingEven> = new EnumToC(
  "RoundingEven",
  [...ROUNDING_EVEN_FROM_C].map(([k, v]) => [v, k] as [RoundingEven, number]),
);

// fdl_geometry_path_t ↔ GeometryPath
export const GEOMETRY_PATH_FROM_C: Map<number, GeometryPath> = new Map([
  [0, GeometryPath.CANVAS_DIMENSIONS],
  [1, GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS],
  [2, GeometryPath.FRAMING_PROTECTION_DIMENSIONS],
  [3, GeometryPath.FRAMING_DIMENSIONS],
]);
export const GEOMETRY_PATH_TO_C: EnumToC<GeometryPath> = new EnumToC(
  "GeometryPath",
  [...GEOMETRY_PATH_FROM_C].map(([k, v]) => [v, k] as [GeometryPath, number]),
);

// fdl_fit_method_t ↔ FitMethod
export const FIT_METHOD_FROM_C: Map<number, FitMethod> = new Map([
  [0, FitMethod.WIDTH],
  [1, FitMethod.HEIGHT],
  [2, FitMethod.FIT_ALL],
  [3, FitMethod.FILL],
]);
export const FIT_METHOD_TO_C: EnumToC<FitMethod> = new EnumToC(
  "FitMethod",
  [...FIT_METHOD_FROM_C].map(([k, v]) => [v, k] as [FitMethod, number]),
);

// fdl_halign_t ↔ HAlign
export const H_ALIGN_FROM_C: Map<number, HAlign> = new Map([
  [0, HAlign.LEFT],
  [1, HAlign.CENTER],
  [2, HAlign.RIGHT],
]);
export const H_ALIGN_TO_C: EnumToC<HAlign> = new EnumToC(
  "HAlign",
  [...H_ALIGN_FROM_C].map(([k, v]) => [v, k] as [HAlign, number]),
);

// fdl_valign_t ↔ VAlign
export const V_ALIGN_FROM_C: Map<number, VAlign> = new Map([
  [0, VAlign.TOP],
  [1, VAlign.CENTER],
  [2, VAlign.BOTTOM],
]);
export const V_ALIGN_TO_C: EnumToC<VAlign> = new EnumToC(
  "VAlign",
  [...V_ALIGN_FROM_C].map(([k, v]) => [v, k] as [VAlign, number]),
);
