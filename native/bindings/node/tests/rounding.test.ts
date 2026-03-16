// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Rounding tests — RoundStrategy, fdlRound, calculateScaleFactor.
 */

import { describe, it, expect, afterEach } from 'vitest';
import { RoundingMode, RoundingEven, FitMethod } from '../src/constants.js';
import {
  RoundStrategy,
  DEFAULT_ROUNDING_STRATEGY,
  getRounding,
  setRounding,
  fdlRound,
  calculateScaleFactor,
} from '../src/rounding.js';
import { DimensionsFloat } from '../src/types.js';

describe('RoundStrategy', () => {
  it('should construct with defaults', () => {
    const rs = new RoundStrategy();
    expect(rs.even).toBe(RoundingEven.EVEN);
    expect(rs.mode).toBe(RoundingMode.UP);
  });

  it('should construct with specific values', () => {
    const rs = new RoundStrategy(RoundingEven.WHOLE, RoundingMode.DOWN);
    expect(rs.even).toBe(RoundingEven.WHOLE);
    expect(rs.mode).toBe(RoundingMode.DOWN);
  });

  it('should support equality', () => {
    const a = new RoundStrategy(RoundingEven.EVEN, RoundingMode.UP);
    const b = new RoundStrategy(RoundingEven.EVEN, RoundingMode.UP);
    const c = new RoundStrategy(RoundingEven.WHOLE, RoundingMode.DOWN);
    expect(a.equals(b)).toBe(true);
    expect(a.equals(c)).toBe(false);
  });

  it('should clone', () => {
    const rs = new RoundStrategy(RoundingEven.WHOLE, RoundingMode.ROUND);
    const copy = rs.clone();
    expect(copy.equals(rs)).toBe(true);
  });

  it('should serialize', () => {
    const rs = new RoundStrategy();
    expect(rs.toJSON()).toEqual({
      even: RoundingEven.EVEN,
      mode: RoundingMode.UP,
    });
  });
});

describe('Global rounding', () => {
  afterEach(() => {
    // Reset to default
    setRounding(DEFAULT_ROUNDING_STRATEGY);
  });

  it('should return default rounding', () => {
    const r = getRounding();
    expect(r.equals(DEFAULT_ROUNDING_STRATEGY)).toBe(true);
  });

  it('should set and restore rounding', () => {
    const custom = new RoundStrategy(RoundingEven.WHOLE, RoundingMode.DOWN);
    const prev = setRounding(custom);
    expect(prev.equals(DEFAULT_ROUNDING_STRATEGY)).toBe(true);
    expect(getRounding().equals(custom)).toBe(true);
  });
});

describe('fdlRound', () => {
  it('should round up', () => {
    const result = fdlRound(1.3, RoundingEven.EVEN, RoundingMode.UP);
    expect(result).toBe(2);
  });

  it('should round down', () => {
    const result = fdlRound(1.7, RoundingEven.EVEN, RoundingMode.DOWN);
    expect(result).toBe(0);
  });

  it('should round nearest', () => {
    const result = fdlRound(1.5, RoundingEven.EVEN, RoundingMode.ROUND);
    expect(result).toBe(2);
  });
});

describe('calculateScaleFactor', () => {
  it('should compute a scale factor', () => {
    const fit = new DimensionsFloat(1920, 1080);
    const target = new DimensionsFloat(3840, 2160);
    const scale = calculateScaleFactor(fit, target, FitMethod.WIDTH);
    expect(scale).toBeGreaterThan(0);
    expect(scale).toBeCloseTo(2.0);
  });

  it('should handle FIT_ALL', () => {
    const fit = new DimensionsFloat(1920, 1080);
    const target = new DimensionsFloat(960, 540);
    const scale = calculateScaleFactor(fit, target, FitMethod.FIT_ALL);
    expect(scale).toBeCloseTo(0.5);
  });
});
