// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Kwargs-construction tests — verify options-object constructors for all classes.
 *
 * Mirrors: native/bindings/python/tests/test_kwargs_construction.py
 */

import { describe, it, expect } from 'vitest';
import { FDL } from '../src/fdl.js';
import { Context } from '../src/context.js';
import { Canvas } from '../src/canvas.js';
import { FramingDecision } from '../src/framing-decision.js';
import { FramingIntent } from '../src/framing-intent.js';
import { CanvasTemplate } from '../src/canvas-template.js';
import { DimensionsInt, DimensionsFloat, PointFloat } from '../src/types.js';
import { RoundStrategy } from '../src/rounding.js';
import { GeometryPath, FitMethod, HAlign, VAlign, RoundingEven, RoundingMode } from '../src/constants.js';

// ---------- FramingIntent ----------

describe('FramingIntent kwargs', () => {
  it('basic construction', () => {
    const fi = new FramingIntent({
      id: 'FI-001',
      label: '1.78-1 Framing',
      aspectRatio: new DimensionsInt(16, 9),
      protection: 0.088,
    });
    expect(fi.id).toBe('FI-001');
    expect(fi.label).toBe('1.78-1 Framing');
    expect(fi.aspectRatio.width).toBe(16);
    expect(fi.aspectRatio.height).toBe(9);
    expect(fi.protection).toBeCloseTo(0.088, 3);
  });

  it('asDict', () => {
    const fi = new FramingIntent({
      id: 'FI-002',
      label: '2.39-1',
      aspectRatio: new DimensionsInt(239, 100),
      protection: 0.0,
    });
    const d = fi.asDict();
    expect(d.id).toBe('FI-002');
    expect(d.label).toBe('2.39-1');
    expect(d.aspect_ratio).toEqual({ width: 239, height: 100 });
    expect(d.protection).toBe(0.0);
  });

  it('equality by id', () => {
    const a = new FramingIntent({
      id: 'FI-X',
      label: 'A',
      aspectRatio: new DimensionsInt(16, 9),
      protection: 0.0,
    });
    const b = new FramingIntent({
      id: 'FI-X',
      label: 'B',
      aspectRatio: new DimensionsInt(4, 3),
      protection: 0.1,
    });
    expect(a.equals(b)).toBe(true);
    expect(a.equals('FI-X')).toBe(true);
  });

  it('default label is empty string', () => {
    const fi = new FramingIntent({
      id: 'FI-003',
      aspectRatio: new DimensionsInt(16, 9),
      protection: 0.0,
    });
    expect(fi.label).toBe('');
  });
});

// ---------- Context ----------

describe('Context kwargs', () => {
  it('basic construction', () => {
    const ctx = new Context({ label: 'Primary' });
    expect(ctx.label).toBe('Primary');
    expect(ctx.contextCreator).toBeNull();
  });

  it('with contextCreator', () => {
    const ctx = new Context({
      label: 'Secondary',
      contextCreator: 'MyTool v1.0',
    });
    expect(ctx.label).toBe('Secondary');
    expect(ctx.contextCreator).toBe('MyTool v1.0');
  });

  it('canvases ignored in constructor', () => {
    const ctx = new Context({
      label: 'Test',
      canvases: ['something'] as unknown as object,
    });
    expect(ctx.label).toBe('Test');
    expect(ctx.canvases.length).toBe(0);
  });

  it('asDict', () => {
    const ctx = new Context({
      label: 'Ctx1',
      contextCreator: 'tool',
    });
    const d = ctx.asDict();
    expect(d.label).toBe('Ctx1');
    expect(d.context_creator).toBe('tool');
  });

  it('equality by label', () => {
    const a = new Context({ label: 'Same' });
    const b = new Context({ label: 'Same', contextCreator: 'diff' });
    expect(a.equals(b)).toBe(true);
    expect(a.equals('Same')).toBe(true);
  });
});

// ---------- Canvas ----------

describe('Canvas kwargs', () => {
  it('basic construction', () => {
    const canvas = new Canvas({
      id: 'CNV-001',
      label: 'Main Canvas',
      sourceCanvasId: 'SRC-001',
      dimensions: new DimensionsInt(5184, 4320),
    });
    expect(canvas.id).toBe('CNV-001');
    expect(canvas.label).toBe('Main Canvas');
    expect(canvas.sourceCanvasId).toBe('SRC-001');
    expect(canvas.dimensions.width).toBe(5184);
    expect(canvas.dimensions.height).toBe(4320);
    expect(canvas.anamorphicSqueeze).toBeCloseTo(1.0);
  });

  it('with anamorphicSqueeze', () => {
    const canvas = new Canvas({
      id: 'CNV-002',
      sourceCanvasId: 'SRC-002',
      dimensions: new DimensionsInt(2700, 2160),
      anamorphicSqueeze: 2.0,
    });
    expect(canvas.anamorphicSqueeze).toBeCloseTo(2.0);
  });

  it('with effective dimensions', () => {
    const canvas = new Canvas({
      id: 'CNV-003',
      sourceCanvasId: 'SRC-003',
      dimensions: new DimensionsInt(5184, 4320),
      effectiveDimensions: new DimensionsInt(5184, 4320),
      effectiveAnchorPoint: new PointFloat(0, 0),
    });
    expect(canvas.effectiveDimensions).not.toBeNull();
    expect(canvas.effectiveDimensions!.width).toBe(5184);
    expect(canvas.effectiveAnchorPoint).not.toBeNull();
    expect(canvas.effectiveAnchorPoint!.x).toBe(0);
  });

  it('optional fields default to null', () => {
    const canvas = new Canvas({
      id: 'CNV-004',
      sourceCanvasId: 'SRC-004',
      dimensions: new DimensionsInt(1920, 1080),
    });
    expect(canvas.effectiveDimensions).toBeNull();
    expect(canvas.effectiveAnchorPoint).toBeNull();
    expect(canvas.photositeDimensions).toBeNull();
    expect(canvas.physicalDimensions).toBeNull();
  });

  it('with photosite dimensions', () => {
    const canvas = new Canvas({
      id: 'CNV-005',
      sourceCanvasId: 'SRC-005',
      dimensions: new DimensionsInt(5184, 4320),
      photositeDimensions: new DimensionsInt(6000, 5000),
    });
    expect(canvas.photositeDimensions).not.toBeNull();
    expect(canvas.photositeDimensions!.width).toBe(6000);
  });

  it('with physical dimensions', () => {
    const canvas = new Canvas({
      id: 'CNV-006',
      sourceCanvasId: 'SRC-006',
      dimensions: new DimensionsInt(5184, 4320),
      physicalDimensions: new DimensionsFloat(36.0, 24.0),
    });
    expect(canvas.physicalDimensions).not.toBeNull();
    expect(canvas.physicalDimensions!.width).toBeCloseTo(36.0);
  });

  it('framingDecisions ignored', () => {
    const canvas = new Canvas({
      id: 'CNV-007',
      sourceCanvasId: 'SRC-007',
      dimensions: new DimensionsInt(1920, 1080),
      framingDecisions: ['ignored'] as unknown as object,
    });
    expect(canvas.framingDecisions.length).toBe(0);
  });

  it('asDict', () => {
    const canvas = new Canvas({
      id: 'CNV-008',
      label: 'Test',
      sourceCanvasId: 'SRC-008',
      dimensions: new DimensionsInt(1920, 1080),
      effectiveDimensions: new DimensionsInt(1920, 1080),
      effectiveAnchorPoint: new PointFloat(0, 0),
    });
    const d = canvas.asDict();
    expect(d.id).toBe('CNV-008');
    expect(d.dimensions).toEqual({ width: 1920, height: 1080 });
    expect(d.effective_dimensions).toEqual({ width: 1920, height: 1080 });
    expect(d.effective_anchor_point).toEqual({ x: 0, y: 0 });
  });

  it('all optional fields', () => {
    const canvas = new Canvas({
      id: 'CNV-009',
      label: 'Full',
      sourceCanvasId: 'SRC-009',
      dimensions: new DimensionsInt(5184, 4320),
      anamorphicSqueeze: 1.3,
      effectiveDimensions: new DimensionsInt(5184, 4320),
      effectiveAnchorPoint: new PointFloat(0, 0),
      photositeDimensions: new DimensionsInt(5184, 4320),
      physicalDimensions: new DimensionsFloat(25.92, 21.6),
    });
    expect(canvas.anamorphicSqueeze).toBeCloseTo(1.3);
    expect(canvas.effectiveDimensions!.width).toBe(5184);
    expect(canvas.photositeDimensions!.width).toBe(5184);
    expect(canvas.physicalDimensions!.width).toBeCloseTo(25.92);
  });

  it('equality by id', () => {
    const a = new Canvas({
      id: 'CNV-X',
      sourceCanvasId: 'SRC',
      dimensions: new DimensionsInt(1920, 1080),
    });
    const b = new Canvas({
      id: 'CNV-X',
      sourceCanvasId: 'OTHER',
      dimensions: new DimensionsInt(3840, 2160),
    });
    expect(a.equals(b)).toBe(true);
    expect(a.equals('CNV-X')).toBe(true);
  });
});

// ---------- FramingDecision ----------

describe('FramingDecision kwargs', () => {
  it('basic construction', () => {
    const fd = new FramingDecision({
      id: 'CNV-FI',
      label: '1.78-1 Framing',
      framingIntentId: 'FI-001',
      dimensions: new DimensionsFloat(4728, 3456),
      anchorPoint: new PointFloat(228, 432),
    });
    expect(fd.id).toBe('CNV-FI');
    expect(fd.label).toBe('1.78-1 Framing');
    expect(fd.framingIntentId).toBe('FI-001');
    expect(fd.dimensions.width).toBeCloseTo(4728);
    expect(fd.dimensions.height).toBeCloseTo(3456);
    expect(fd.anchorPoint.x).toBeCloseTo(228);
    expect(fd.anchorPoint.y).toBeCloseTo(432);
    expect(fd.protectionDimensions).toBeNull();
    expect(fd.protectionAnchorPoint).toBeNull();
  });

  it('with protection', () => {
    const fd = new FramingDecision({
      id: 'CNV-FI2',
      framingIntentId: 'FI-001',
      dimensions: new DimensionsFloat(4728, 3456),
      anchorPoint: new PointFloat(228, 432),
      protectionDimensions: new DimensionsFloat(5184, 3790),
      protectionAnchorPoint: new PointFloat(0, 265),
    });
    expect(fd.protectionDimensions).not.toBeNull();
    expect(fd.protectionDimensions!.width).toBeCloseTo(5184);
    expect(fd.protectionAnchorPoint).not.toBeNull();
    expect(fd.protectionAnchorPoint!.y).toBeCloseTo(265);
  });

  it('asDict', () => {
    const fd = new FramingDecision({
      id: 'CNV-FI3',
      label: 'Test',
      framingIntentId: 'FI-003',
      dimensions: new DimensionsFloat(1920, 1080),
      anchorPoint: new PointFloat(0, 0),
    });
    const d = fd.asDict();
    expect(d.id).toBe('CNV-FI3');
    expect(d.label).toBe('Test');
    expect(d.framing_intent_id).toBe('FI-003');
  });

  it('asDict with protection', () => {
    const fd = new FramingDecision({
      id: 'CNV-FI4',
      framingIntentId: 'FI-004',
      dimensions: new DimensionsFloat(1920, 1080),
      anchorPoint: new PointFloat(0, 0),
      protectionDimensions: new DimensionsFloat(2000, 1200),
      protectionAnchorPoint: new PointFloat(40, 60),
    });
    const d = fd.asDict();
    expect(d.protection_dimensions).toEqual({ width: 2000, height: 1200 });
    expect(d.protection_anchor_point).toEqual({ x: 40, y: 60 });
  });

  it('equality by id', () => {
    const a = new FramingDecision({
      id: 'FD-SAME',
      framingIntentId: 'FI-A',
    });
    const b = new FramingDecision({
      id: 'FD-SAME',
      framingIntentId: 'FI-B',
      dimensions: new DimensionsFloat(100, 100),
    });
    expect(a.equals(b)).toBe(true);
    expect(a.equals('FD-SAME')).toBe(true);
  });

  it('default dimensions are zero', () => {
    const fd = new FramingDecision({
      id: 'CNV-FI5',
      framingIntentId: 'FI-005',
    });
    expect(fd.dimensions.width).toBe(0);
    expect(fd.dimensions.height).toBe(0);
    expect(fd.anchorPoint.x).toBe(0);
    expect(fd.anchorPoint.y).toBe(0);
  });
});

// ---------- CanvasTemplate ----------

describe('CanvasTemplate kwargs', () => {
  it('basic construction', () => {
    const ct = new CanvasTemplate({
      id: 'CT-001',
      label: 'HD Template',
      targetDimensions: new DimensionsInt(1920, 1080),
      fitSource: GeometryPath.CANVAS_DIMENSIONS,
      fitMethod: FitMethod.FIT_ALL,
      alignmentMethodHorizontal: HAlign.CENTER,
      alignmentMethodVertical: VAlign.CENTER,
      round: new RoundStrategy(RoundingEven.EVEN, RoundingMode.ROUND),
    });
    expect(ct.id).toBe('CT-001');
    expect(ct.label).toBe('HD Template');
    expect(ct.targetDimensions.width).toBe(1920);
    expect(ct.targetDimensions.height).toBe(1080);
    expect(ct.fitSource).toBe(GeometryPath.CANVAS_DIMENSIONS);
    expect(ct.fitMethod).toBe(FitMethod.FIT_ALL);
    expect(ct.alignmentMethodHorizontal).toBe(HAlign.CENTER);
    expect(ct.alignmentMethodVertical).toBe(VAlign.CENTER);
    expect(ct.targetAnamorphicSqueeze).toBeCloseTo(1.0);
    expect(ct.preserveFromSourceCanvas).toBeNull();
    expect(ct.maximumDimensions).toBeNull();
    expect(ct.padToMaximum).toBe(false);
  });

  it('with optional fields', () => {
    const ct = new CanvasTemplate({
      id: 'CT-002',
      targetDimensions: new DimensionsInt(3840, 2160),
      preserveFromSourceCanvas: GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
      maximumDimensions: new DimensionsInt(4096, 2160),
      padToMaximum: true,
    });
    expect(ct.preserveFromSourceCanvas).toBe(GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS);
    expect(ct.maximumDimensions!.width).toBe(4096);
    expect(ct.padToMaximum).toBe(true);
  });

  it('with anamorphicSqueeze', () => {
    const ct = new CanvasTemplate({
      id: 'CT-003',
      targetDimensions: new DimensionsInt(1920, 1080),
      targetAnamorphicSqueeze: 2.0,
    });
    expect(ct.targetAnamorphicSqueeze).toBeCloseTo(2.0);
  });

  it('asDict', () => {
    const ct = new CanvasTemplate({
      id: 'CT-004',
      label: 'Test',
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    const d = ct.asDict();
    expect(d.id).toBe('CT-004');
    expect(d.target_dimensions).toEqual({ width: 1920, height: 1080 });
  });

  it('padToMaximum defaults to false', () => {
    const ct = new CanvasTemplate({
      id: 'CT-005',
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    expect(ct.padToMaximum).toBe(false);
    const d = ct.asDict();
    expect(d.pad_to_maximum).toBe(false);
  });

  it('equality by id', () => {
    const a = new CanvasTemplate({
      id: 'CT-SAME',
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    const b = new CanvasTemplate({
      id: 'CT-SAME',
      targetDimensions: new DimensionsInt(3840, 2160),
    });
    expect(a.equals(b)).toBe(true);
    expect(a.equals('CT-SAME')).toBe(true);
  });

  it('default enum values', () => {
    const ct = new CanvasTemplate({
      id: 'CT-006',
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    // Defaults from YAML: fitSource=FRAMING_DIMENSIONS, fitMethod=WIDTH, etc.
    expect(ct.fitSource).toBe(GeometryPath.FRAMING_DIMENSIONS);
    expect(ct.fitMethod).toBe(FitMethod.WIDTH);
    expect(ct.alignmentMethodHorizontal).toBe(HAlign.CENTER);
    expect(ct.alignmentMethodVertical).toBe(VAlign.CENTER);
  });
});

// ---------- FDL ----------

describe('FDL kwargs', () => {
  it('default construction', () => {
    const fdl = new FDL({});
    expect(fdl.uuid).toBeTruthy();
    expect(fdl.versionMajor).toBe(2);
    expect(fdl.versionMinor).toBe(0);
    fdl.close();
  });

  it('with custom values', () => {
    const fdl = new FDL({
      uuid: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
      versionMajor: 2,
      versionMinor: 1,
      fdlCreator: 'TestTool v1.0',
    });
    expect(fdl.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
    expect(fdl.versionMajor).toBe(2);
    expect(fdl.versionMinor).toBe(1);
    expect(fdl.fdlCreator).toBe('TestTool v1.0');
    fdl.close();
  });

  it('generates random UUID by default', () => {
    const a = new FDL({});
    const b = new FDL({});
    expect(a.uuid).not.toBe(b.uuid);
    // Both should be valid UUID format
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    expect(a.uuid).toMatch(uuidRegex);
    expect(b.uuid).toMatch(uuidRegex);
    a.close();
    b.close();
  });

  it('with defaultFramingIntent', () => {
    const fdl = new FDL({
      defaultFramingIntent: 'FI-001',
    });
    expect(fdl.defaultFramingIntent).toBe('FI-001');
    fdl.close();
  });
});

// ---------- Kwargs vs Builder parity ----------

describe('Kwargs vs Builder parity', () => {
  it('FramingIntent kwargs matches builder', () => {
    // Kwargs path
    const fi = new FramingIntent({
      id: 'FI-TEST',
      label: 'Test',
      aspectRatio: new DimensionsInt(16, 9),
      protection: 0.1,
    });
    // Builder path
    const fdl = new FDL({});
    const builtFi = fdl.addFramingIntent('FI-TEST', 'Test', new DimensionsInt(16, 9), 0.1);
    expect(fi.asDict()).toEqual(builtFi.asDict());
    fdl.close();
  });

  it('Context kwargs matches builder', () => {
    const ctx = new Context({
      label: 'Test',
      contextCreator: 'Tool',
    });
    const fdl = new FDL({});
    fdl.addFramingIntent('FI-01', '', new DimensionsInt(16, 9), 0.0);
    const builtCtx = fdl.addContext('Test', 'Tool');
    expect(ctx.asDict().label).toEqual(builtCtx.asDict().label);
    expect(ctx.asDict().context_creator).toEqual(builtCtx.asDict().context_creator);
    fdl.close();
  });
});

// ---------- Backing doc invisibility ----------

describe('Backing document invisibility', () => {
  it('standalone FramingIntent does not leak scaffold', () => {
    const fi = new FramingIntent({
      id: 'FI-SOLO',
      aspectRatio: new DimensionsInt(16, 9),
      protection: 0.0,
    });
    const d = fi.asDict();
    // Should only contain FI fields, no doc/context/canvas
    expect(d.id).toBe('FI-SOLO');
    expect(Object.keys(d)).toContain('id');
    expect(Object.keys(d)).toContain('aspect_ratio');
    expect(Object.keys(d)).toContain('protection');
    expect(Object.keys(d)).not.toContain('uuid');
    expect(Object.keys(d)).not.toContain('contexts');
  });

  it('standalone Canvas does not leak scaffold', () => {
    const canvas = new Canvas({
      id: 'CNV-SOLO',
      sourceCanvasId: 'SRC',
      dimensions: new DimensionsInt(1920, 1080),
    });
    const d = canvas.asDict();
    expect(d.id).toBe('CNV-SOLO');
    expect(Object.keys(d)).not.toContain('uuid');
    expect(Object.keys(d)).not.toContain('contexts');
  });
});
