// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * FramingDecision advanced method tests.
 *
 * Mirrors: native/bindings/python/tests/test_framing_decision.py
 */

import { describe, it, expect } from 'vitest';
import { FDL } from '../src/fdl.js';
import { FramingDecision } from '../src/framing-decision.js';
import { DimensionsInt, DimensionsFloat, PointFloat } from '../src/types.js';
import { HAlign, VAlign } from '../src/constants.js';

/** Build an FDL doc with one context + one canvas + one FI for testing. */
function buildDoc(opts: {
  canvasDims: DimensionsInt;
  effectiveDims?: DimensionsInt;
  effectiveAnchor?: PointFloat;
  squeeze?: number;
  fiRatio: DimensionsInt;
  fiProtection: number;
}) {
  const fdl = new FDL({});
  const fi = fdl.addFramingIntent(
    'FI_A', 'Test', opts.fiRatio, opts.fiProtection,
  );
  const ctx = fdl.addContext('Primary', null);
  const canvas = ctx.addCanvas(
    'C1', 'Test Canvas', 'C1', opts.canvasDims, opts.squeeze ?? 1.0,
  );
  if (opts.effectiveDims) {
    canvas.setEffective(
      opts.effectiveDims,
      opts.effectiveAnchor ?? new PointFloat(0, 0),
    );
  }
  return { fdl, fi, ctx, canvas };
}

describe('FramingDecision.fromFramingIntent', () => {
  it('1:1 no squeeze', () => {
    const { fdl, fi, canvas } = buildDoc({
      canvasDims: new DimensionsInt(1920, 1080),
      fiRatio: new DimensionsInt(16, 9),
      fiProtection: 0.0,
    });
    const fd = FramingDecision.fromFramingIntent(canvas, fi);
    expect(fd.dimensions.width).toBeCloseTo(1920, 0);
    expect(fd.dimensions.height).toBeCloseTo(1080, 0);
    expect(fd.protectionDimensions).toBeNull();
    fdl.close();
  });

  it('1:1 with squeeze', () => {
    const { fdl, fi, canvas } = buildDoc({
      canvasDims: new DimensionsInt(960, 1080),
      squeeze: 2.0,
      fiRatio: new DimensionsInt(16, 9),
      fiProtection: 0.0,
    });
    const fd = FramingDecision.fromFramingIntent(canvas, fi);
    expect(fd.dimensions.width).toBeCloseTo(960, 0);
    expect(fd.dimensions.height).toBeCloseTo(1080, 0);
    fdl.close();
  });

  it('wide intent', () => {
    const { fdl, fi, canvas } = buildDoc({
      canvasDims: new DimensionsInt(1920, 1080),
      fiRatio: new DimensionsInt(235, 100),
      fiProtection: 0.0,
    });
    const fd = FramingDecision.fromFramingIntent(canvas, fi);
    // Width fits, height shrinks
    expect(fd.dimensions.width).toBeCloseTo(1920, 0);
    expect(fd.dimensions.height).toBeLessThan(1080);
    fdl.close();
  });

  it('tall intent', () => {
    const { fdl, fi, canvas } = buildDoc({
      canvasDims: new DimensionsInt(1920, 1080),
      fiRatio: new DimensionsInt(4, 3),
      fiProtection: 0.0,
    });
    const fd = FramingDecision.fromFramingIntent(canvas, fi);
    // Height fits, width shrinks
    expect(fd.dimensions.width).toBeLessThan(1920);
    expect(fd.dimensions.height).toBeCloseTo(1080, 0);
    fdl.close();
  });

  it('with protection', () => {
    const { fdl, fi, canvas } = buildDoc({
      canvasDims: new DimensionsInt(1920, 1080),
      effectiveDims: new DimensionsInt(1920, 1080),
      fiRatio: new DimensionsInt(16, 9),
      fiProtection: 0.1,
    });
    const fd = FramingDecision.fromFramingIntent(canvas, fi);
    // With 10% protection, framing dimensions should be smaller
    expect(fd.dimensions.width).toBeLessThan(1920);
    expect(fd.dimensions.height).toBeLessThan(1080);
    expect(fd.protectionDimensions).not.toBeNull();
    fdl.close();
  });
});

describe('FramingDecision.adjustAnchorPoint', () => {
  function buildFdForAdjust() {
    const fdl = new FDL({});
    fdl.addFramingIntent('FI_A', '', new DimensionsInt(16, 9), 0.0);
    const ctx = fdl.addContext('Primary', null);
    const canvas = ctx.addCanvas(
      'C1', '', 'C1', new DimensionsInt(1920, 1080), 1.0,
    );
    canvas.setEffective(new DimensionsInt(1920, 1080), new PointFloat(0, 0));
    // Add FD with dimensions smaller than canvas to allow anchor adjustment
    const fd = canvas.addFramingDecision(
      'C1-FI_A', '', 'FI_A',
      new DimensionsFloat(1600, 900),
      new PointFloat(160, 90),
    );
    return { fdl, canvas, fd };
  }

  it('center-center produces centered anchor', () => {
    const { fdl, canvas, fd } = buildFdForAdjust();
    fd.adjustAnchorPoint(canvas, HAlign.CENTER, VAlign.CENTER);
    expect(fd.anchorPoint.x).toBeCloseTo(160, 0);
    expect(fd.anchorPoint.y).toBeCloseTo(90, 0);
    fdl.close();
  });

  it('left-top produces zero anchor', () => {
    const { fdl, canvas, fd } = buildFdForAdjust();
    fd.adjustAnchorPoint(canvas, HAlign.LEFT, VAlign.TOP);
    expect(fd.anchorPoint.x).toBeCloseTo(0, 0);
    expect(fd.anchorPoint.y).toBeCloseTo(0, 0);
    fdl.close();
  });

  it('right-bottom produces max anchor', () => {
    const { fdl, canvas, fd } = buildFdForAdjust();
    fd.adjustAnchorPoint(canvas, HAlign.RIGHT, VAlign.BOTTOM);
    // anchor = canvas_dim - fd_dim
    expect(fd.anchorPoint.x).toBeCloseTo(320, 0);
    expect(fd.anchorPoint.y).toBeCloseTo(180, 0);
    fdl.close();
  });
});

describe('FramingDecision.populateFromIntent', () => {
  it('populates existing FD from intent', () => {
    const fdl = new FDL({});
    const fi = fdl.addFramingIntent('FI_A', '', new DimensionsInt(16, 9), 0.0);
    const ctx = fdl.addContext('Primary', null);
    const canvas = ctx.addCanvas(
      'C1', '', 'C1', new DimensionsInt(1920, 1080), 1.0,
    );
    const fd = canvas.addFramingDecision(
      'C1-FI_A', '', 'FI_A',
      new DimensionsFloat(0, 0), new PointFloat(0, 0),
    );

    // Initially zero
    expect(fd.dimensions.width).toBe(0);
    expect(fd.dimensions.height).toBe(0);

    // Populate from intent
    fd.populateFromIntent(canvas, fi);
    expect(fd.dimensions.width).toBeCloseTo(1920, 0);
    expect(fd.dimensions.height).toBeCloseTo(1080, 0);
    fdl.close();
  });
});
