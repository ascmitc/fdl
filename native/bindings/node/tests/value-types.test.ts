// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Value type class tests — DimensionsInt, DimensionsFloat, PointFloat, Rect.
 */

import { describe, it, expect } from 'vitest';
import {
  DimensionsInt,
  DimensionsFloat,
  PointFloat,
  Rect,
} from '../src/types.js';

describe('DimensionsInt', () => {
  it('should construct with defaults', () => {
    const d = new DimensionsInt();
    expect(d.width).toBe(0);
    expect(d.height).toBe(0);
  });

  it('should construct with values', () => {
    const d = new DimensionsInt(1920, 1080);
    expect(d.width).toBe(1920);
    expect(d.height).toBe(1080);
  });

  it('should support equality', () => {
    const a = new DimensionsInt(1920, 1080);
    const b = new DimensionsInt(1920, 1080);
    const c = new DimensionsInt(3840, 2160);
    expect(a.equals(b)).toBe(true);
    expect(a.equals(c)).toBe(false);
  });

  it('should clone', () => {
    const a = new DimensionsInt(1920, 1080);
    const b = a.clone();
    expect(b.equals(a)).toBe(true);
    b.width = 0;
    expect(a.width).toBe(1920); // original unchanged
  });

  it('should serialize to JSON', () => {
    const d = new DimensionsInt(1920, 1080);
    expect(d.toJSON()).toEqual({ width: 1920, height: 1080 });
  });

  it('should report isZero', () => {
    expect(new DimensionsInt(0, 0).isZero()).toBe(true);
    expect(new DimensionsInt(1, 0).isZero()).toBe(false);
  });

  it('should normalize to float', () => {
    const d = new DimensionsInt(1920, 1080);
    const f = d.normalize(1.0);
    expect(f).toBeInstanceOf(DimensionsFloat);
    expect(f.width).toBeCloseTo(1920);
    expect(f.height).toBeCloseTo(1080);
  });

  it('should compare gt/lt', () => {
    const a = new DimensionsInt(3840, 2160);
    const b = new DimensionsInt(1920, 1080);
    expect(a.gt(b)).toBe(true);
    expect(b.lt(a)).toBe(true);
    expect(a.lt(b)).toBe(false);
  });

  it('should support toBool', () => {
    expect(new DimensionsInt(0, 0).toBool()).toBe(false);
    expect(new DimensionsInt(1, 0).toBool()).toBe(true);
  });

  it('should duplicate', () => {
    const d = new DimensionsInt(1920, 1080);
    const d2 = d.duplicate();
    expect(d2.equals(d)).toBe(true);
  });

  it('should format as string', () => {
    const d = new DimensionsInt(1920, 1080);
    expect(d.format()).toBe('DimensionsInt(width=1920, height=1080)');
    expect(d.toString()).toBe(d.format());
  });

  it('should cross-type equalsApprox with DimensionsFloat', () => {
    const i = new DimensionsInt(1920, 1080);
    const f = new DimensionsFloat(1920.0, 1080.0);
    expect(i.equalsApprox(f)).toBe(true);
  });
});

describe('DimensionsFloat', () => {
  it('should construct with defaults', () => {
    const d = new DimensionsFloat();
    expect(d.width).toBe(0);
    expect(d.height).toBe(0);
  });

  it('should construct with values', () => {
    const d = new DimensionsFloat(1920.5, 1080.25);
    expect(d.width).toBeCloseTo(1920.5);
    expect(d.height).toBeCloseTo(1080.25);
  });

  it('should support approximate equality', () => {
    const a = new DimensionsFloat(1.0, 2.0);
    const b = new DimensionsFloat(1.0 + 1e-8, 2.0 - 1e-8);
    expect(a.equals(b)).toBe(true);
  });

  it('should scale', () => {
    const d = new DimensionsFloat(1920, 1080);
    const scaled = d.scale(2.0, 1.0);
    expect(scaled.width).toBeCloseTo(3840);
    expect(scaled.height).toBeCloseTo(2160);
  });

  it('should convert toInt by truncation', () => {
    const d = new DimensionsFloat(1920.7, 1080.3);
    const i = d.toInt();
    expect(i).toBeInstanceOf(DimensionsInt);
    expect(i.width).toBe(1920);
    expect(i.height).toBe(1080);

    // Negative values truncate toward zero (same as Python int())
    const d2 = new DimensionsFloat(-1.9, -2.1);
    const i2 = d2.toInt();
    expect(i2.width).toBe(-1);
    expect(i2.height).toBe(-2);
  });

  it('should scaleBy (mutating)', () => {
    const d = new DimensionsFloat(100, 200);
    d.scaleBy(2);
    expect(d.width).toBeCloseTo(200);
    expect(d.height).toBeCloseTo(400);
  });

  it('should subtract', () => {
    const a = new DimensionsFloat(3840, 2160);
    const b = new DimensionsFloat(1920, 1080);
    const c = a.sub(b);
    expect(c.width).toBeCloseTo(1920);
    expect(c.height).toBeCloseTo(1080);
  });

  it('should fromDimensions (static)', () => {
    const original = new DimensionsFloat(1920, 1080);
    const copy = DimensionsFloat.fromDimensions(original);
    expect(copy.equals(original)).toBe(true);
  });

  it('should clampToDims', () => {
    const d = new DimensionsFloat(4000, 3000);
    const clamp = new DimensionsFloat(1920, 1080);
    const { result, delta } = d.clampToDims(clamp);
    expect(result.width).toBeLessThanOrEqual(1920);
    expect(result.height).toBeLessThanOrEqual(1080);
    expect(delta).toBeInstanceOf(PointFloat);
  });
});

describe('PointFloat', () => {
  it('should construct with defaults', () => {
    const p = new PointFloat();
    expect(p.x).toBe(0);
    expect(p.y).toBe(0);
  });

  it('should add', () => {
    const a = new PointFloat(1, 2);
    const b = new PointFloat(3, 4);
    const c = a.add(b);
    expect(c.x).toBeCloseTo(4);
    expect(c.y).toBeCloseTo(6);
  });

  it('should sub', () => {
    const a = new PointFloat(5, 7);
    const b = new PointFloat(2, 3);
    const c = a.sub(b);
    expect(c.x).toBeCloseTo(3);
    expect(c.y).toBeCloseTo(4);
  });

  it('should iadd (mutating)', () => {
    const a = new PointFloat(1, 2);
    const b = new PointFloat(3, 4);
    const result = a.iadd(b);
    expect(result).toBe(a); // same reference
    expect(a.x).toBeCloseTo(4);
    expect(a.y).toBeCloseTo(6);
  });

  it('should mul by scalar', () => {
    const p = new PointFloat(3, 4);
    const r = p.mul(2);
    expect(r.x).toBeCloseTo(6);
    expect(r.y).toBeCloseTo(8);
  });

  it('should mul by point', () => {
    const a = new PointFloat(3, 4);
    const b = new PointFloat(2, 5);
    const r = a.mul(b);
    expect(r.x).toBeCloseTo(6);
    expect(r.y).toBeCloseTo(20);
  });

  it('should normalize', () => {
    const p = new PointFloat(100, 200);
    const n = p.normalize(2.0);
    expect(n).toBeInstanceOf(PointFloat);
  });

  it('should isZero', () => {
    expect(new PointFloat(0, 0).isZero()).toBe(true);
    expect(new PointFloat(1, 0).isZero()).toBe(false);
  });

  it('should format as string', () => {
    const p = new PointFloat(1.5, 2.5);
    expect(p.format()).toBe('PointFloat(x=1.5, y=2.5)');
  });
});

describe('Rect', () => {
  it('should construct with defaults', () => {
    const r = new Rect();
    expect(r.x).toBe(0);
    expect(r.y).toBe(0);
    expect(r.width).toBe(0);
    expect(r.height).toBe(0);
  });

  it('should construct with values', () => {
    const r = new Rect(10, 20, 100, 200);
    expect(r.x).toBeCloseTo(10);
    expect(r.y).toBeCloseTo(20);
    expect(r.width).toBeCloseTo(100);
    expect(r.height).toBeCloseTo(200);
  });

  it('should support equality', () => {
    const a = new Rect(1, 2, 3, 4);
    const b = new Rect(1, 2, 3, 4);
    const c = new Rect(0, 0, 3, 4);
    expect(a.equals(b)).toBe(true);
    expect(a.equals(c)).toBe(false);
  });

  it('should clone', () => {
    const r = new Rect(10, 20, 100, 200);
    const c = r.clone();
    expect(c.equals(r)).toBe(true);
  });

  it('should serialize to JSON', () => {
    const r = new Rect(1, 2, 3, 4);
    expect(r.toJSON()).toEqual({ x: 1, y: 2, width: 3, height: 4 });
  });
});
