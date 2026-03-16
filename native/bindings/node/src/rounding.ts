// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file rounding.ts
 * @brief Rounding strategy and rounding-related free functions.
 */

import { getAddon } from "./ffi/index.js";
import { FitMethod, RoundingEven, RoundingMode } from "./constants.js";
import {
  FIT_METHOD_TO_C,
  ROUNDING_EVEN_TO_C,
  ROUNDING_MODE_TO_C,
} from "./enum-maps.js";
import { DimensionsFloat } from "./types.js";

// -----------------------------------------------------------------------
// RoundStrategy
// -----------------------------------------------------------------------

/** Rounding strategy: combination of even/odd and direction. */
export class RoundStrategy {
  even: RoundingEven;
  mode: RoundingMode;

  constructor(
    even: RoundingEven = RoundingEven.EVEN,
    mode: RoundingMode = RoundingMode.UP,
  ) {
    this.even = even;
    this.mode = mode;
  }

  equals(other: RoundStrategy): boolean {
    return this.even === other.even && this.mode === other.mode;
  }

  clone(): RoundStrategy {
    return new RoundStrategy(this.even, this.mode);
  }

  toString(): string {
    return `RoundStrategy(even=${this.even}, mode=${this.mode})`;
  }

  toJSON(): Record<string, unknown> {
    return { even: this.even, mode: this.mode };
  }
}

/** Default rounding strategy. */
export const DEFAULT_ROUNDING_STRATEGY = new RoundStrategy();

let _currentRounding: RoundStrategy = DEFAULT_ROUNDING_STRATEGY;

/** Get the current global rounding strategy. */
export function getRounding(): RoundStrategy {
  return _currentRounding;
}

/** Set the global rounding strategy. Returns the previous value. */
export function setRounding(strategy: RoundStrategy): RoundStrategy {
  const prev = _currentRounding;
  _currentRounding = strategy;
  return prev;
}

// -----------------------------------------------------------------------
// Rounding free functions
// -----------------------------------------------------------------------

/** Round a single float value according to FDL rounding rules. */
export function fdlRound(
  value: number,
  even: RoundingEven,
  mode: RoundingMode,
): number {
  const addon = getAddon();
  return addon.fdl_round(
    value,
    ROUNDING_EVEN_TO_C.get(even)!,
    ROUNDING_MODE_TO_C.get(mode)!,
  ) as number;
}

/** Calculate scale factor based on fit method. */
export function calculateScaleFactor(
  fitNorm: DimensionsFloat,
  targetNorm: DimensionsFloat,
  fitMethod: FitMethod,
): number {
  const addon = getAddon();
  return addon.fdl_calculate_scale_factor(
    { width: fitNorm.width, height: fitNorm.height },
    { width: targetNorm.width, height: targetNorm.height },
    FIT_METHOD_TO_C.get(fitMethod)!,
  ) as number;
}
