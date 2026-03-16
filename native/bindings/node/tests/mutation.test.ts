// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Mutation tests — verify property setters work correctly.
 *
 * Mirrors: native/bindings/python/tests/test_facade.py (mutation section)
 */

import { describe, it, expect } from 'vitest';
import { FDL } from '../src/fdl.js';
import { DimensionsInt, DimensionsFloat, PointFloat } from '../src/types.js';

describe('Property mutation', () => {
  function buildDoc() {
    const fdl = new FDL({
      uuid: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
      fdlCreator: 'test',
      defaultFramingIntent: 'FI_01',
    });
    fdl.addFramingIntent('FI_01', 'Default', new DimensionsInt(16, 9), 0.0);
    const ctx = fdl.addContext('Primary', null);
    const canvas = ctx.addCanvas(
      'C1', 'Test', 'C1', new DimensionsInt(1920, 1080), 1.0,
    );
    canvas.setEffective(new DimensionsInt(1920, 1080), new PointFloat(0, 0));
    const fd = canvas.addFramingDecision(
      'C1-FI_01', 'Test FD', 'FI_01',
      new DimensionsFloat(1920, 1080), new PointFloat(0, 0),
    );
    return { fdl, ctx, canvas, fd };
  }

  it('FDL fdlCreator mutation', () => {
    const { fdl } = buildDoc();
    expect(fdl.fdlCreator).toBe('test');
    fdl.fdlCreator = 'updated';
    expect(fdl.fdlCreator).toBe('updated');
    fdl.close();
  });

  it('Canvas dimensions remain after setEffective', () => {
    const { fdl, canvas } = buildDoc();
    // Original effective dimensions
    expect(canvas.effectiveDimensions!.width).toBe(1920);

    // Update effective
    canvas.setEffective(new DimensionsInt(1600, 900), new PointFloat(160, 90));
    expect(canvas.effectiveDimensions!.width).toBe(1600);
    expect(canvas.effectiveAnchorPoint!.x).toBeCloseTo(160);

    // Original dimensions unchanged
    expect(canvas.dimensions.width).toBe(1920);
    fdl.close();
  });

  it('Canvas remove effective via null setter', () => {
    const { fdl, canvas } = buildDoc();
    expect(canvas.effectiveDimensions).not.toBeNull();
    canvas.effectiveDimensions = null;
    expect(canvas.effectiveDimensions).toBeNull();
    expect(canvas.effectiveAnchorPoint).toBeNull();
    fdl.close();
  });

  it('Canvas photosite mutation', () => {
    const { fdl, canvas } = buildDoc();
    expect(canvas.photositeDimensions).toBeNull();
    canvas.photositeDimensions = new DimensionsInt(6000, 5000);
    expect(canvas.photositeDimensions!.width).toBe(6000);
    // Update to different value
    canvas.photositeDimensions = new DimensionsInt(7000, 6000);
    expect(canvas.photositeDimensions!.width).toBe(7000);
    fdl.close();
  });

  it('Canvas physical dimensions mutation', () => {
    const { fdl, canvas } = buildDoc();
    expect(canvas.physicalDimensions).toBeNull();
    canvas.physicalDimensions = new DimensionsFloat(36.0, 24.0);
    expect(canvas.physicalDimensions!.width).toBeCloseTo(36.0);
    // Update to different value
    canvas.physicalDimensions = new DimensionsFloat(24.0, 18.0);
    expect(canvas.physicalDimensions!.width).toBeCloseTo(24.0);
    fdl.close();
  });

  it('FramingDecision dimensions mutation', () => {
    const { fdl, fd } = buildDoc();
    expect(fd.dimensions.width).toBeCloseTo(1920);
    fd.dimensions = new DimensionsFloat(1600, 900);
    expect(fd.dimensions.width).toBeCloseTo(1600);
    fdl.close();
  });

  it('FramingDecision anchor mutation', () => {
    const { fdl, fd } = buildDoc();
    expect(fd.anchorPoint.x).toBeCloseTo(0);
    fd.anchorPoint = new PointFloat(100, 50);
    expect(fd.anchorPoint.x).toBeCloseTo(100);
    fdl.close();
  });

  it('FramingDecision protection mutation', () => {
    const { fdl, fd } = buildDoc();
    expect(fd.protectionDimensions).toBeNull();

    // Set protection
    fd.setProtection(new DimensionsFloat(2000, 1200), new PointFloat(40, 60));
    expect(fd.protectionDimensions).not.toBeNull();
    expect(fd.protectionDimensions!.width).toBeCloseTo(2000);
    expect(fd.protectionAnchorPoint!.x).toBeCloseTo(40);

    // Remove protection via null setter
    fd.protectionDimensions = null;
    expect(fd.protectionDimensions).toBeNull();
    expect(fd.protectionAnchorPoint).toBeNull();
    fdl.close();
  });

  it('JSON roundtrip after mutation', () => {
    const { fdl, canvas } = buildDoc();
    canvas.setEffective(new DimensionsInt(1600, 900), new PointFloat(160, 90));
    const json = fdl.asJson();
    const parsed = JSON.parse(json);
    const canvasData = parsed.contexts[0].canvases[0];
    expect(canvasData.effective_dimensions.width).toBe(1600);
    expect(canvasData.effective_anchor_point.x).toBe(160);
    fdl.close();
  });
});
