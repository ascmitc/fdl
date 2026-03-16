// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Enum and converter tests — bidirectional maps, converter round-trips.
 */

import { describe, it, expect } from 'vitest';
import {
  RoundingMode,
  RoundingEven,
  GeometryPath,
  FitMethod,
  HAlign,
  VAlign,
  FP_REL_TOL,
  FP_ABS_TOL,
  ATTR_SCALE_FACTOR,
  ATTR_CONTENT_TRANSLATION,
  ATTR_SCALED_BOUNDING_BOX,
} from '../src/constants.js';
import {
  ROUNDING_MODE_FROM_C,
  ROUNDING_MODE_TO_C,
  ROUNDING_EVEN_FROM_C,
  ROUNDING_EVEN_TO_C,
  FIT_METHOD_FROM_C,
  FIT_METHOD_TO_C,
  GEOMETRY_PATH_FROM_C,
  GEOMETRY_PATH_TO_C,
  H_ALIGN_FROM_C,
  H_ALIGN_TO_C,
  V_ALIGN_FROM_C,
  V_ALIGN_TO_C,
} from '../src/enum-maps.js';
import {
  fromDimsI64,
  toDimsI64,
  fromDimsF64,
  toDimsF64,
  fromPointF64,
  toPointF64,
  fromRect,
  toRect,
  fromRoundStrategy,
  toRoundStrategy,
} from '../src/converters.js';
import { DimensionsInt, DimensionsFloat, PointFloat, Rect } from '../src/types.js';
import { RoundStrategy } from '../src/rounding.js';

describe('Enum maps', () => {
  it('should have correct RoundingMode bidirectional mapping', () => {
    expect(ROUNDING_MODE_FROM_C.get(0)).toBe(RoundingMode.UP);
    expect(ROUNDING_MODE_FROM_C.get(1)).toBe(RoundingMode.DOWN);
    expect(ROUNDING_MODE_FROM_C.get(2)).toBe(RoundingMode.ROUND);
    expect(ROUNDING_MODE_TO_C.get(RoundingMode.UP)).toBe(0);
    expect(ROUNDING_MODE_TO_C.get(RoundingMode.DOWN)).toBe(1);
    expect(ROUNDING_MODE_TO_C.get(RoundingMode.ROUND)).toBe(2);
  });

  it('should have correct RoundingEven bidirectional mapping', () => {
    expect(ROUNDING_EVEN_FROM_C.get(0)).toBe(RoundingEven.WHOLE);
    expect(ROUNDING_EVEN_FROM_C.get(1)).toBe(RoundingEven.EVEN);
    expect(ROUNDING_EVEN_TO_C.get(RoundingEven.WHOLE)).toBe(0);
    expect(ROUNDING_EVEN_TO_C.get(RoundingEven.EVEN)).toBe(1);
  });

  it('should have correct FitMethod mapping', () => {
    expect(FIT_METHOD_FROM_C.size).toBe(4);
    expect(FIT_METHOD_TO_C.get(FitMethod.WIDTH)).toBe(0);
    expect(FIT_METHOD_TO_C.get(FitMethod.FILL)).toBe(3);
  });

  it('should have correct GeometryPath mapping', () => {
    expect(GEOMETRY_PATH_FROM_C.size).toBe(4);
    expect(GEOMETRY_PATH_FROM_C.get(0)).toBe(GeometryPath.CANVAS_DIMENSIONS);
  });

  it('should have correct HAlign mapping', () => {
    expect(H_ALIGN_FROM_C.size).toBe(3);
    expect(H_ALIGN_TO_C.get(HAlign.CENTER)).toBe(1);
  });

  it('should have correct VAlign mapping', () => {
    expect(V_ALIGN_FROM_C.size).toBe(3);
    expect(V_ALIGN_TO_C.get(VAlign.BOTTOM)).toBe(2);
  });

  it('should be fully reversible for all enums', () => {
    // Every FROM_C entry should round-trip
    for (const [k, v] of ROUNDING_MODE_FROM_C) {
      expect(ROUNDING_MODE_TO_C.get(v)).toBe(k);
    }
    for (const [k, v] of FIT_METHOD_FROM_C) {
      expect(FIT_METHOD_TO_C.get(v)).toBe(k);
    }
  });
});

describe('Converters', () => {
  it('should round-trip DimensionsInt', () => {
    const original = new DimensionsInt(1920, 1080);
    const raw = toDimsI64(original);
    const restored = fromDimsI64(raw);
    expect(restored.equals(original)).toBe(true);
  });

  it('should round-trip DimensionsFloat', () => {
    const original = new DimensionsFloat(1920.5, 1080.25);
    const raw = toDimsF64(original);
    const restored = fromDimsF64(raw);
    expect(restored.equals(original)).toBe(true);
  });

  it('should round-trip PointFloat', () => {
    const original = new PointFloat(0.5, -0.3);
    const raw = toPointF64(original);
    const restored = fromPointF64(raw);
    expect(restored.equals(original)).toBe(true);
  });

  it('should round-trip Rect', () => {
    const original = new Rect(10, 20, 100, 200);
    const raw = toRect(original);
    const restored = fromRect(raw);
    expect(restored.equals(original)).toBe(true);
  });

  it('should round-trip RoundStrategy', () => {
    const original = new RoundStrategy(RoundingEven.WHOLE, RoundingMode.DOWN);
    const raw = toRoundStrategy(original);
    const restored = fromRoundStrategy(raw);
    expect(restored.equals(original)).toBe(true);
  });
});

describe('FP tolerance constants', () => {
  it('should export FP_REL_TOL', () => {
    expect(FP_REL_TOL).toBe(1e-9);
  });

  it('should export FP_ABS_TOL', () => {
    expect(FP_ABS_TOL).toBe(1e-6);
  });
});

describe('ATTR_* constants', () => {
  it('should export ATTR_SCALE_FACTOR', () => {
    expect(ATTR_SCALE_FACTOR).toBe('scale_factor');
  });

  it('should export ATTR_CONTENT_TRANSLATION', () => {
    expect(ATTR_CONTENT_TRANSLATION).toBe('content_translation');
  });

  it('should export ATTR_SCALED_BOUNDING_BOX', () => {
    expect(ATTR_SCALED_BOUNDING_BOX).toBe('scaled_bounding_box');
  });
});
