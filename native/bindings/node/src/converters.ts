// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file converters.ts
 * @brief Converter functions between N-API addon raw objects and typed classes.
 *
 * The addon returns plain JS objects for struct types.  These functions
 * convert between those raw objects and the typed value classes.
 */

import { DimensionsFloat, DimensionsInt, PointFloat, Rect } from "./types.js";
import { RoundStrategy } from "./rounding.js";
import {
  ROUNDING_EVEN_FROM_C,
  ROUNDING_EVEN_TO_C,
  ROUNDING_MODE_FROM_C,
  ROUNDING_MODE_TO_C,
} from "./enum-maps.js";
import { RoundingEven, RoundingMode } from "./constants.js";

// -----------------------------------------------------------------------
// DimensionsInt
// -----------------------------------------------------------------------

/** Convert addon raw object to DimensionsInt. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function fromDimsI64(raw: any): DimensionsInt {
  return new DimensionsInt(raw.width, raw.height);
}

/** Convert DimensionsInt to addon-compatible plain object. */
export function toDimsI64(val: DimensionsInt): Record<string, unknown> {
  return {
    width: val.width,
    height: val.height,
  };
}

// -----------------------------------------------------------------------
// DimensionsFloat
// -----------------------------------------------------------------------

/** Convert addon raw object to DimensionsFloat. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function fromDimsF64(raw: any): DimensionsFloat {
  return new DimensionsFloat(raw.width, raw.height);
}

/** Convert DimensionsFloat to addon-compatible plain object. */
export function toDimsF64(val: DimensionsFloat): Record<string, unknown> {
  return {
    width: val.width,
    height: val.height,
  };
}

// -----------------------------------------------------------------------
// PointFloat
// -----------------------------------------------------------------------

/** Convert addon raw object to PointFloat. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function fromPointF64(raw: any): PointFloat {
  return new PointFloat(raw.x, raw.y);
}

/** Convert PointFloat to addon-compatible plain object. */
export function toPointF64(val: PointFloat): Record<string, unknown> {
  return {
    x: val.x,
    y: val.y,
  };
}

// -----------------------------------------------------------------------
// Rect
// -----------------------------------------------------------------------

/** Convert addon raw object to Rect. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function fromRect(raw: any): Rect {
  return new Rect(raw.x, raw.y, raw.width, raw.height);
}

/** Convert Rect to addon-compatible plain object. */
export function toRect(val: Rect): Record<string, unknown> {
  return {
    x: val.x,
    y: val.y,
    width: val.width,
    height: val.height,
  };
}

// -----------------------------------------------------------------------
// RoundStrategy
// -----------------------------------------------------------------------

/** Convert addon raw object to RoundStrategy. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function fromRoundStrategy(raw: any): RoundStrategy {
  return new RoundStrategy(
    ROUNDING_EVEN_FROM_C.get(raw.even) ?? RoundingEven.EVEN,
    ROUNDING_MODE_FROM_C.get(raw.mode) ?? RoundingMode.UP,
  );
}

/** Convert RoundStrategy to addon-compatible plain object. */
export function toRoundStrategy(val: RoundStrategy): Record<string, unknown> {
  return {
    even: ROUNDING_EVEN_TO_C.get(val.even)!,
    mode: ROUNDING_MODE_TO_C.get(val.mode)!,
  };
}
