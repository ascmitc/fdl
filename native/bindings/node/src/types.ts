// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file types.ts
 * @brief Value type classes for FDL dimensions, points, rects, etc.
 */

import { getAddon } from "./ffi/index.js";
import { RoundingEven, RoundingMode } from "./constants.js";
import { ROUNDING_EVEN_TO_C, ROUNDING_MODE_TO_C } from "./enum-maps.js";

const _FP_ABS_TOL = 1e-6;

// -----------------------------------------------------------------------
// DimensionsInt
// -----------------------------------------------------------------------

/** Lightweight DimensionsInt value type. */
export class DimensionsInt {
  width: number;
  height: number;

  constructor(width: number = 0, height: number = 0) {
    this.width = width;
    this.height = height;
  }

  /** Value equality. */
  equals(other: DimensionsInt): boolean {
    return this.width === other.width && this.height === other.height;
  }

  /** Cross-type equality with DimensionsFloat. */
  equalsApprox(other: DimensionsFloat): boolean {
    if (Math.abs(this.width - other.width) >= _FP_ABS_TOL) return false;
    if (Math.abs(this.height - other.height) >= _FP_ABS_TOL) return false;
    return true;
  }

  /** Create a shallow copy. */
  clone(): DimensionsInt {
    return new DimensionsInt(this.width, this.height);
  }

  toString(): string {
    return `DimensionsInt(width=${this.width}, height=${this.height})`;
  }

  /** Convert to plain object. */
  toJSON(): Record<string, unknown> {
    return { width: this.width, height: this.height };
  }

  /** isZero */
  isZero(): boolean {
    const addon = getAddon();
    return Boolean(
      addon.fdl_dimensions_i64_is_zero({
        width: this.width,
        height: this.height,
      }),
    );
  }

  /** normalize */
  normalize(squeeze: number): DimensionsFloat {
    const addon = getAddon();
    const _r = addon.fdl_dimensions_i64_normalize(
      { width: this.width, height: this.height },
      squeeze,
    );
    return new DimensionsFloat(_r.width, _r.height);
  }

  /** duplicate */
  duplicate(): DimensionsInt {
    return new DimensionsInt(this.width, this.height);
  }

  /** format */
  format(): string {
    return `DimensionsInt(width=${this.width}, height=${this.height})`;
  }

  /** Operator: __gt__ */
  gt(other: DimensionsInt): boolean {
    const addon = getAddon();
    return Boolean(
      addon.fdl_dimensions_i64_gt(
        { width: this.width, height: this.height },
        { width: other.width, height: other.height },
      ),
    );
  }

  /** Operator: __lt__ */
  lt(other: DimensionsInt): boolean {
    const addon = getAddon();
    return Boolean(
      addon.fdl_dimensions_i64_lt(
        { width: this.width, height: this.height },
        { width: other.width, height: other.height },
      ),
    );
  }

  /** Operator: __bool__ */
  toBool(): boolean {
    return this.width !== 0 || this.height !== 0;
  }
}

// -----------------------------------------------------------------------
// DimensionsFloat
// -----------------------------------------------------------------------

/** Lightweight DimensionsFloat value type. */
export class DimensionsFloat {
  width: number;
  height: number;

  constructor(width: number = 0, height: number = 0) {
    this.width = width;
    this.height = height;
  }

  /** Value equality. */
  equals(other: DimensionsFloat): boolean {
    return (
      Math.abs(this.width - other.width) < _FP_ABS_TOL &&
      Math.abs(this.height - other.height) < _FP_ABS_TOL
    );
  }

  /** Cross-type equality with DimensionsInt. */
  equalsApprox(other: DimensionsInt): boolean {
    if (Math.abs(this.width - other.width) >= _FP_ABS_TOL) return false;
    if (Math.abs(this.height - other.height) >= _FP_ABS_TOL) return false;
    return true;
  }

  /** Create a shallow copy. */
  clone(): DimensionsFloat {
    return new DimensionsFloat(this.width, this.height);
  }

  toString(): string {
    return `DimensionsFloat(width=${this.width}, height=${this.height})`;
  }

  /** Convert to plain object. */
  toJSON(): Record<string, unknown> {
    return { width: this.width, height: this.height };
  }

  /** isZero */
  isZero(): boolean {
    const addon = getAddon();
    return Boolean(
      addon.fdl_dimensions_is_zero({ width: this.width, height: this.height }),
    );
  }

  /** normalize */
  normalize(squeeze: number): DimensionsFloat {
    const addon = getAddon();
    const _r = addon.fdl_dimensions_normalize(
      { width: this.width, height: this.height },
      squeeze,
    );
    return new DimensionsFloat(_r.width, _r.height);
  }

  /** scale */
  scale(scaleFactor: number, targetSqueeze: number): DimensionsFloat {
    const addon = getAddon();
    const _r = addon.fdl_dimensions_scale(
      { width: this.width, height: this.height },
      scaleFactor,
      targetSqueeze,
    );
    return new DimensionsFloat(_r.width, _r.height);
  }

  /** normalizeAndScale */
  normalizeAndScale(
    inputSqueeze: number,
    scaleFactor: number,
    targetSqueeze: number,
  ): DimensionsFloat {
    const addon = getAddon();
    const _r = addon.fdl_dimensions_normalize_and_scale(
      { width: this.width, height: this.height },
      inputSqueeze,
      scaleFactor,
      targetSqueeze,
    );
    return new DimensionsFloat(_r.width, _r.height);
  }

  /** round */
  round(even: RoundingEven, mode: RoundingMode): DimensionsFloat {
    const addon = getAddon();
    const _r = addon.fdl_round_dimensions(
      { width: this.width, height: this.height },
      ROUNDING_EVEN_TO_C.get(even)!,
      ROUNDING_MODE_TO_C.get(mode)!,
    );
    return new DimensionsFloat(_r.width, _r.height);
  }

  /** clampToDims */
  clampToDims(clampDims: DimensionsFloat): {
    result: DimensionsFloat;
    delta: PointFloat;
  } {
    const addon = getAddon();
    const _out = addon.fdl_dimensions_clamp_to_dims(
      { width: this.width, height: this.height },
      { width: clampDims.width, height: clampDims.height },
    );
    const delta = new PointFloat(_out.delta.x, _out.delta.y);
    return {
      result: new DimensionsFloat(_out._return.width, _out._return.height),
      delta,
    };
  }

  /** duplicate */
  duplicate(): DimensionsFloat {
    return new DimensionsFloat(this.width, this.height);
  }

  /** format */
  format(): string {
    return `DimensionsFloat(width=${this.width}, height=${this.height})`;
  }

  /** toInt */
  toInt(): DimensionsInt {
    return new DimensionsInt(Math.trunc(this.width), Math.trunc(this.height));
  }

  /** fromDimensions */
  static fromDimensions(dims: DimensionsFloat): DimensionsFloat {
    return new DimensionsFloat(dims.width, dims.height);
  }

  /** scaleBy */
  scaleBy(factor: number): void {
    this.width *= factor;
    this.height *= factor;
  }

  /** Operator: __sub__ */
  sub(other: DimensionsFloat): DimensionsFloat {
    const addon = getAddon();
    const _r = addon.fdl_dimensions_sub(
      { width: this.width, height: this.height },
      { width: other.width, height: other.height },
    );
    return new DimensionsFloat(_r.width, _r.height);
  }

  /** Operator: __lt__ */
  lt(other: DimensionsFloat): boolean {
    const addon = getAddon();
    return Boolean(
      addon.fdl_dimensions_f64_lt(
        { width: this.width, height: this.height },
        { width: other.width, height: other.height },
      ),
    );
  }

  /** Operator: __gt__ */
  gt(other: DimensionsFloat): boolean {
    const addon = getAddon();
    return Boolean(
      addon.fdl_dimensions_f64_gt(
        { width: this.width, height: this.height },
        { width: other.width, height: other.height },
      ),
    );
  }

  /** Operator: __bool__ */
  toBool(): boolean {
    return this.width !== 0 || this.height !== 0;
  }
}

// -----------------------------------------------------------------------
// PointFloat
// -----------------------------------------------------------------------

/** Lightweight PointFloat value type. */
export class PointFloat {
  x: number;
  y: number;

  constructor(x: number = 0, y: number = 0) {
    this.x = x;
    this.y = y;
  }

  /** Value equality. */
  equals(other: PointFloat): boolean {
    return (
      Math.abs(this.x - other.x) < _FP_ABS_TOL &&
      Math.abs(this.y - other.y) < _FP_ABS_TOL
    );
  }

  /** Create a shallow copy. */
  clone(): PointFloat {
    return new PointFloat(this.x, this.y);
  }

  toString(): string {
    return `PointFloat(x=${this.x}, y=${this.y})`;
  }

  /** Convert to plain object. */
  toJSON(): Record<string, unknown> {
    return { x: this.x, y: this.y };
  }

  /** isZero */
  isZero(): boolean {
    const addon = getAddon();
    return Boolean(addon.fdl_point_is_zero({ x: this.x, y: this.y }));
  }

  /** normalize */
  normalize(squeeze: number): PointFloat {
    const addon = getAddon();
    const _r = addon.fdl_point_normalize({ x: this.x, y: this.y }, squeeze);
    return new PointFloat(_r.x, _r.y);
  }

  /** scale */
  scale(scaleFactor: number, targetSqueeze: number): PointFloat {
    const addon = getAddon();
    const _r = addon.fdl_point_scale(
      { x: this.x, y: this.y },
      scaleFactor,
      targetSqueeze,
    );
    return new PointFloat(_r.x, _r.y);
  }

  /** normalizeAndScale */
  normalizeAndScale(
    inputSqueeze: number,
    scaleFactor: number,
    targetSqueeze: number,
  ): PointFloat {
    const addon = getAddon();
    const _r = addon.fdl_point_normalize_and_scale(
      { x: this.x, y: this.y },
      inputSqueeze,
      scaleFactor,
      targetSqueeze,
    );
    return new PointFloat(_r.x, _r.y);
  }

  /** clamp */
  clamp(minVal: number | null, maxVal: number | null): PointFloat {
    const addon = getAddon();
    const _r = addon.fdl_point_clamp(
      { x: this.x, y: this.y },
      minVal ?? 0,
      minVal !== null ? 1 : 0,
      maxVal ?? 0,
      maxVal !== null ? 1 : 0,
    );
    return new PointFloat(_r.x, _r.y);
  }

  /** round */
  round(even: RoundingEven, mode: RoundingMode): PointFloat {
    const addon = getAddon();
    const _r = addon.fdl_round_point(
      { x: this.x, y: this.y },
      ROUNDING_EVEN_TO_C.get(even)!,
      ROUNDING_MODE_TO_C.get(mode)!,
    );
    return new PointFloat(_r.x, _r.y);
  }

  /** format */
  format(): string {
    return `PointFloat(x=${this.x}, y=${this.y})`;
  }

  /** Operator: __add__ */
  add(other: PointFloat): PointFloat {
    const addon = getAddon();
    const _r = addon.fdl_point_add(
      { x: this.x, y: this.y },
      { x: other.x, y: other.y },
    );
    return new PointFloat(_r.x, _r.y);
  }

  /** Operator: __iadd__ */
  iadd(other: PointFloat): PointFloat {
    this.x += other.x;
    this.y += other.y;
    return this;
  }

  /** Operator: __sub__ */
  sub(other: PointFloat): PointFloat {
    const addon = getAddon();
    const _r = addon.fdl_point_sub(
      { x: this.x, y: this.y },
      { x: other.x, y: other.y },
    );
    return new PointFloat(_r.x, _r.y);
  }

  /** Operator: __mul__ */
  mul(other: PointFloat | number): PointFloat {
    const addon = getAddon();
    if (typeof other === "number") {
      const _r = addon.fdl_point_mul_scalar({ x: this.x, y: this.y }, other);
      return new PointFloat(_r.x, _r.y);
    }
    return new PointFloat(
      this.x * (other as PointFloat).x,
      this.y * (other as PointFloat).y,
    );
  }

  /** Operator: __lt__ */
  lt(other: PointFloat): boolean {
    const addon = getAddon();
    return Boolean(
      addon.fdl_point_f64_lt(
        { x: this.x, y: this.y },
        { x: other.x, y: other.y },
      ),
    );
  }

  /** Operator: __gt__ */
  gt(other: PointFloat): boolean {
    const addon = getAddon();
    return Boolean(
      addon.fdl_point_f64_gt(
        { x: this.x, y: this.y },
        { x: other.x, y: other.y },
      ),
    );
  }
}

// -----------------------------------------------------------------------
// Rect
// -----------------------------------------------------------------------

/** Lightweight Rect value type. */
export class Rect {
  x: number;
  y: number;
  width: number;
  height: number;

  constructor(
    x: number = 0,
    y: number = 0,
    width: number = 0,
    height: number = 0,
  ) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
  }

  /** Value equality. */
  equals(other: Rect): boolean {
    return (
      Math.abs(this.x - other.x) < _FP_ABS_TOL &&
      Math.abs(this.y - other.y) < _FP_ABS_TOL &&
      Math.abs(this.width - other.width) < _FP_ABS_TOL &&
      Math.abs(this.height - other.height) < _FP_ABS_TOL
    );
  }

  /** Create a shallow copy. */
  clone(): Rect {
    return new Rect(this.x, this.y, this.width, this.height);
  }

  toString(): string {
    return `Rect(x=${this.x}, y=${this.y}, width=${this.width}, height=${this.height})`;
  }

  /** Convert to plain object. */
  toJSON(): Record<string, unknown> {
    return { x: this.x, y: this.y, width: this.width, height: this.height };
  }
}
