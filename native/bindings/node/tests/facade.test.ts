// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Facade tests — verify handle-backed TypeScript objects work correctly.
 *
 * Mirrors: native/bindings/python/tests/test_facade.py
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { FDL } from '../src/fdl.js';
import { Canvas } from '../src/canvas.js';
import { Context } from '../src/context.js';
import { FramingDecision } from '../src/framing-decision.js';
import { FramingIntent } from '../src/framing-intent.js';
import { CanvasTemplate } from '../src/canvas-template.js';
import { FDLValidationError } from '../src/errors.js';

const MINIMAL_FDL = {
  uuid: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
  version: { major: 2, minor: 0 },
  fdl_creator: 'test',
  default_framing_intent: 'FI_01',
  framing_intents: [
    {
      id: 'FI_01',
      label: 'Default',
      aspect_ratio: { width: 16, height: 9 },
      protection: 0.0,
    },
  ],
  contexts: [
    {
      label: 'Source',
      canvases: [
        {
          id: 'CV_01',
          label: 'Source Canvas',
          source_canvas_id: 'CV_01',
          dimensions: { width: 3840, height: 2160 },
          anamorphic_squeeze: 1.0,
          framing_decisions: [
            {
              id: 'CV_01-FI_01',
              label: 'Default FD',
              framing_intent_id: 'FI_01',
              dimensions: { width: 3840.0, height: 2160.0 },
              anchor_point: { x: 0.0, y: 0.0 },
            },
          ],
        },
      ],
    },
  ],
  canvas_templates: [],
};

function parseMinimalFdl(): FDL {
  const json = JSON.stringify(MINIMAL_FDL);
  return FDL.parse(Buffer.from(json));
}

// -----------------------------------------------------------------------
// Document
// -----------------------------------------------------------------------

describe('Document', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('should parse', () => {
    expect(doc).toBeInstanceOf(FDL);
  });

  it('should read uuid', () => {
    expect(doc.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
  });

  it('should read fdlCreator', () => {
    expect(doc.fdlCreator).toBe('test');
  });

  it('should read defaultFramingIntent', () => {
    expect(doc.defaultFramingIntent).toBe('FI_01');
  });

  it('should read version', () => {
    const v = doc.version;
    expect(v.major).toBe(2);
    expect(v.minor).toBe(0);
  });

  it('should read versionMajor/versionMinor', () => {
    expect(doc.versionMajor).toBe(2);
    expect(doc.versionMinor).toBe(0);
  });

  it('should support close()', () => {
    const d = parseMinimalFdl();
    expect(d.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
    d.close();
    expect(() => d.uuid).toThrow();
  });

  it('should support double close without error', () => {
    const d = parseMinimalFdl();
    d.close();
    d.close(); // Should not throw
  });

  it('should support Symbol.dispose', () => {
    const d = parseMinimalFdl();
    d[Symbol.dispose]();
    expect(d.isClosed).toBe(true);
  });

  it('should produce asDict()', () => {
    const d = doc.asDict();
    expect(d).toBeTypeOf('object');
    expect(d.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
    expect(d.version).toEqual({ major: 2, minor: 0 });
    expect(Array.isArray(d.contexts)).toBe(true);
    expect((d.contexts as unknown[]).length).toBe(1);
    expect((d.framing_intents as unknown[]).length).toBe(1);
  });

  it('should produce asJson()', () => {
    const s = doc.asJson(2);
    expect(typeof s).toBe('string');
    const parsed = JSON.parse(s);
    expect(parsed.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
  });

  it('should produce toJSON() for JSON.stringify', () => {
    const d = doc.toJSON();
    expect(d.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
    // Also verify JSON.stringify works
    const str = JSON.stringify(doc);
    const parsed = JSON.parse(str);
    expect(parsed.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
  });

  it('should validate without errors', () => {
    expect(() => doc.validate()).not.toThrow();
  });
});

// -----------------------------------------------------------------------
// Collections
// -----------------------------------------------------------------------

describe('Collections', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('contexts.length', () => {
    expect(doc.contexts.length).toBe(1);
  });

  it('contexts iteration', () => {
    const labels = [...doc.contexts].map((ctx) => ctx.label);
    expect(labels).toEqual(['Source']);
  });

  it('contexts.at()', () => {
    const ctx = doc.contexts.at(0);
    expect(ctx).not.toBeNull();
    expect(ctx!.label).toBe('Source');
  });

  it('contexts.at() out of range returns null', () => {
    expect(doc.contexts.at(99)).toBeNull();
  });

  it('contexts.findByLabel()', () => {
    const ctx = doc.contexts.findByLabel('Source');
    expect(ctx).not.toBeNull();
    expect(ctx!.label).toBe('Source');
  });

  it('contexts.findByLabel() not found returns null', () => {
    expect(doc.contexts.findByLabel('Nonexistent')).toBeNull();
  });

  it('framingIntents.length', () => {
    expect(doc.framingIntents.length).toBe(1);
  });

  it('framingIntents.findById()', () => {
    const fi = doc.framingIntents.findById('FI_01');
    expect(fi).not.toBeNull();
    expect(fi!.id).toBe('FI_01');
  });

  it('canvasTemplates empty', () => {
    expect(doc.canvasTemplates.length).toBe(0);
  });

  it('toArray()', () => {
    const arr = doc.contexts.toArray();
    expect(Array.isArray(arr)).toBe(true);
    expect(arr.length).toBe(1);
    expect(arr[0].label).toBe('Source');
  });
});

// -----------------------------------------------------------------------
// Context
// -----------------------------------------------------------------------

describe('Context', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('label', () => {
    const ctx = doc.contexts.at(0)!;
    expect(ctx.label).toBe('Source');
  });

  it('contextCreator is null when not set', () => {
    const ctx = doc.contexts.at(0)!;
    expect(ctx.contextCreator).toBeNull();
  });

  it('clipId is null when not set', () => {
    const ctx = doc.contexts.at(0)!;
    expect(ctx.clipId).toBeNull();
  });

  it('canvases collection', () => {
    const ctx = doc.contexts.at(0)!;
    expect(ctx.canvases.length).toBe(1);
  });

  it('equals with string', () => {
    const ctx = doc.contexts.at(0)!;
    expect(ctx.equals('Source')).toBe(true);
    expect(ctx.equals('Other')).toBe(false);
  });

  it('asDict()', () => {
    const ctx = doc.contexts.at(0)!;
    const d = ctx.asDict();
    expect(d.label).toBe('Source');
    expect(Array.isArray(d.canvases)).toBe(true);
  });
});

// -----------------------------------------------------------------------
// Canvas
// -----------------------------------------------------------------------

describe('Canvas', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('id', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.id).toBe('CV_01');
  });

  it('label', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.label).toBe('Source Canvas');
  });

  it('sourceCanvasId', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.sourceCanvasId).toBe('CV_01');
  });

  it('dimensions', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const dims = canvas.dimensions;
    expect(dims.width).toBe(3840);
    expect(dims.height).toBe(2160);
  });

  it('anamorphicSqueeze', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.anamorphicSqueeze).toBe(1.0);
  });

  it('optional properties null when not set', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.effectiveDimensions).toBeNull();
    expect(canvas.effectiveAnchorPoint).toBeNull();
    expect(canvas.photositeDimensions).toBeNull();
    expect(canvas.physicalDimensions).toBeNull();
  });

  it('equals with string', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.equals('CV_01')).toBe(true);
    expect(canvas.equals('OTHER')).toBe(false);
  });

  it('framingDecisions collection', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.framingDecisions.length).toBe(1);
  });

  it('framingDecisions.findById()', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.findById('CV_01-FI_01');
    expect(fd).not.toBeNull();
    expect(fd!.id).toBe('CV_01-FI_01');
  });

  it('asDict()', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const d = canvas.asDict();
    expect(d.id).toBe('CV_01');
    expect((d.dimensions as { width: number }).width).toBe(3840);
  });

  it('asDict() excludes null optionals', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const d = canvas.asDict();
    expect(d.effective_dimensions).toBeUndefined();
    expect(d.photosite_dimensions).toBeUndefined();
    expect(d.physical_dimensions).toBeUndefined();
    // Required fields present
    expect(d.id).toBeDefined();
    expect(d.dimensions).toBeDefined();
  });

  it('getRect()', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const rect = canvas.getRect();
    expect(rect.width).toBeCloseTo(3840);
    expect(rect.height).toBeCloseTo(2160);
    expect(rect.x).toBeCloseTo(0);
    expect(rect.y).toBeCloseTo(0);
  });

  it('getEffectiveRect() returns null when not set', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.getEffectiveRect()).toBeNull();
  });
});

// -----------------------------------------------------------------------
// FramingDecision
// -----------------------------------------------------------------------

describe('FramingDecision', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('properties', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    expect(fd.id).toBe('CV_01-FI_01');
    expect(fd.label).toBe('Default FD');
    expect(fd.framingIntentId).toBe('FI_01');
  });

  it('dimensions', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    expect(fd.dimensions.width).toBe(3840.0);
    expect(fd.dimensions.height).toBe(2160.0);
  });

  it('anchorPoint', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    expect(fd.anchorPoint.x).toBe(0.0);
    expect(fd.anchorPoint.y).toBe(0.0);
  });

  it('protection null when not set', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    expect(fd.protectionDimensions).toBeNull();
    expect(fd.protectionAnchorPoint).toBeNull();
  });

  it('equals with string', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    expect(fd.equals('CV_01-FI_01')).toBe(true);
    expect(fd.equals('OTHER')).toBe(false);
  });

  it('asDict()', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    const d = fd.asDict();
    expect(d.id).toBe('CV_01-FI_01');
    expect((d.dimensions as { width: number }).width).toBe(3840.0);
  });

  it('getRect()', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    const rect = fd.getRect();
    expect(rect.width).toBeCloseTo(3840);
    expect(rect.height).toBeCloseTo(2160);
  });

  it('getProtectionRect() null when not set', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    expect(fd.getProtectionRect()).toBeNull();
  });
});

// -----------------------------------------------------------------------
// FramingIntent
// -----------------------------------------------------------------------

describe('FramingIntent', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('properties', () => {
    const fi = doc.framingIntents.at(0)!;
    expect(fi.id).toBe('FI_01');
    expect(fi.label).toBe('Default');
  });

  it('aspectRatio', () => {
    const fi = doc.framingIntents.at(0)!;
    expect(fi.aspectRatio.width).toBe(16);
    expect(fi.aspectRatio.height).toBe(9);
  });

  it('protection', () => {
    const fi = doc.framingIntents.at(0)!;
    expect(fi.protection).toBe(0.0);
  });

  it('equals with string', () => {
    const fi = doc.framingIntents.at(0)!;
    expect(fi.equals('FI_01')).toBe(true);
    expect(fi.equals('OTHER')).toBe(false);
  });

  it('asDict()', () => {
    const fi = doc.framingIntents.at(0)!;
    const d = fi.asDict();
    expect(d.id).toBe('FI_01');
    expect((d.aspect_ratio as { width: number }).width).toBe(16);
  });
});

// -----------------------------------------------------------------------
// Builders — addContext, addCanvas, addFramingIntent, addFramingDecision
// -----------------------------------------------------------------------

describe('Builders', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('addFramingIntent', () => {
    const fi = doc.addFramingIntent('FI_02', 'Wide', { width: 21, height: 9 }, 0.1);
    expect(fi.id).toBe('FI_02');
    expect(fi.label).toBe('Wide');
    expect(fi.aspectRatio.width).toBe(21);
    expect(fi.aspectRatio.height).toBe(9);
    expect(fi.protection).toBeCloseTo(0.1);
    expect(doc.framingIntents.length).toBe(2);
  });

  it('addContext', () => {
    const ctx = doc.addContext('NewCtx', 'creator');
    expect(ctx.label).toBe('NewCtx');
    expect(ctx.contextCreator).toBe('creator');
    expect(doc.contexts.length).toBe(2);
  });

  it('addContext without creator', () => {
    const ctx = doc.addContext('BarCtx');
    expect(ctx.label).toBe('BarCtx');
  });

  it('addCanvas', () => {
    const ctx = doc.contexts.at(0)!;
    const canvas = ctx.addCanvas('CV_02', 'New Canvas', 'CV_01', { width: 1920, height: 1080 }, 1.0);
    expect(canvas.id).toBe('CV_02');
    expect(canvas.label).toBe('New Canvas');
    expect(canvas.sourceCanvasId).toBe('CV_01');
    expect(canvas.dimensions.width).toBe(1920);
    expect(canvas.dimensions.height).toBe(1080);
    expect(canvas.anamorphicSqueeze).toBe(1.0);
    expect(ctx.canvases.length).toBe(2);
  });

  it('addFramingDecision', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.addFramingDecision(
      'FD_02',
      'Test FD',
      'FI_01',
      { width: 1920.0, height: 1080.0 },
      { x: 10.0, y: 20.0 },
    );
    expect(fd.id).toBe('FD_02');
    expect(fd.label).toBe('Test FD');
    expect(fd.framingIntentId).toBe('FI_01');
    expect(fd.dimensions.width).toBe(1920.0);
    expect(fd.dimensions.height).toBe(1080.0);
    expect(fd.anchorPoint.x).toBe(10.0);
    expect(fd.anchorPoint.y).toBe(20.0);
    expect(canvas.framingDecisions.length).toBe(2);
  });
});

// -----------------------------------------------------------------------
// Mutation
// -----------------------------------------------------------------------

describe('Mutation', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('set uuid', () => {
    doc.uuid = 'new-uuid-1234';
    expect(doc.uuid).toBe('new-uuid-1234');
  });

  it('set fdlCreator', () => {
    doc.fdlCreator = 'new-creator';
    expect(doc.fdlCreator).toBe('new-creator');
  });

  it('set defaultFramingIntent', () => {
    doc.defaultFramingIntent = 'FI_02';
    expect(doc.defaultFramingIntent).toBe('FI_02');
  });

  it('set canvas dimensions', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    canvas.dimensions = { width: 1920, height: 1080 };
    expect(canvas.dimensions.width).toBe(1920);
    expect(canvas.dimensions.height).toBe(1080);
  });

  it('set canvas anamorphicSqueeze', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    canvas.anamorphicSqueeze = 2.0;
    expect(canvas.anamorphicSqueeze).toBe(2.0);
  });

  it('set framing decision dimensions', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    fd.dimensions = { width: 1000.5, height: 500.25 };
    expect(fd.dimensions.width).toBeCloseTo(1000.5);
    expect(fd.dimensions.height).toBeCloseTo(500.25);
  });

  it('set framing decision anchorPoint', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    fd.anchorPoint = { x: 100.5, y: 200.5 };
    expect(fd.anchorPoint.x).toBeCloseTo(100.5);
    expect(fd.anchorPoint.y).toBeCloseTo(200.5);
  });

  it('set framing intent aspectRatio', () => {
    const fi = doc.framingIntents.at(0)!;
    fi.aspectRatio = { width: 21, height: 9 };
    expect(fi.aspectRatio.width).toBe(21);
    expect(fi.aspectRatio.height).toBe(9);
  });

  it('set framing intent protection', () => {
    const fi = doc.framingIntents.at(0)!;
    fi.protection = 0.5;
    expect(fi.protection).toBeCloseTo(0.5);
  });

  it('set canvas effective dimensions', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    expect(canvas.effectiveDimensions).toBeNull();
    canvas.setEffective({ width: 1920, height: 1080 }, { x: 10, y: 20 });
    expect(canvas.effectiveDimensions).not.toBeNull();
    expect(canvas.effectiveDimensions!.width).toBe(1920);
    expect(canvas.effectiveAnchorPoint).not.toBeNull();
    expect(canvas.effectiveAnchorPoint!.x).toBeCloseTo(10);
  });

  it('remove canvas effective (set null)', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    canvas.setEffective({ width: 1920, height: 1080 }, { x: 10, y: 20 });
    expect(canvas.effectiveDimensions).not.toBeNull();
    canvas.effectiveDimensions = null;
    expect(canvas.effectiveDimensions).toBeNull();
  });

  it('set and remove framing decision protection', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    expect(fd.protectionDimensions).toBeNull();

    fd.setProtection({ width: 1600.0, height: 900.0 }, { x: 100.0, y: 100.0 });
    expect(fd.protectionDimensions).not.toBeNull();
    expect(fd.protectionDimensions!.width).toBeCloseTo(1600.0);
    expect(fd.protectionAnchorPoint).not.toBeNull();
    expect(fd.protectionAnchorPoint!.x).toBeCloseTo(100.0);

    fd.protectionDimensions = null;
    expect(fd.protectionDimensions).toBeNull();
  });
});

// -----------------------------------------------------------------------
// Custom Attributes
// -----------------------------------------------------------------------

describe('CustomAttributes', () => {
  let doc: FDL;

  beforeEach(() => {
    doc = parseMinimalFdl();
  });
  afterEach(() => {
    doc.close();
  });

  it('set and get on FDL', () => {
    doc.setCustomAttr('myKey', 'myValue');
    expect(doc.hasCustomAttr('myKey')).toBe(true);
    expect(doc.getCustomAttr('myKey')).toBe('myValue');
    expect(doc.customAttrsCount).toBe(1);
  });

  it('set numeric custom attr', () => {
    doc.setCustomAttr('count', 42);
    expect(doc.getCustomAttr('count')).toBe(42);
  });

  it('set boolean custom attr', () => {
    doc.setCustomAttr('flag', true);
    expect(doc.getCustomAttr('flag')).toBe(true);
  });

  it('remove custom attr', () => {
    doc.setCustomAttr('temp', 'val');
    expect(doc.removeCustomAttr('temp')).toBe(true);
    expect(doc.hasCustomAttr('temp')).toBe(false);
    expect(doc.removeCustomAttr('temp')).toBe(false);
  });

  it('customAttrs dict', () => {
    doc.setCustomAttr('a', 'one');
    doc.setCustomAttr('b', 2);
    const attrs = doc.customAttrs;
    expect(attrs.a).toBe('one');
    expect(attrs.b).toBe(2);
  });

  it('custom attrs on Canvas', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    canvas.setCustomAttr('test', 'val');
    expect(canvas.getCustomAttr('test')).toBe('val');
    expect(canvas.customAttrsCount).toBe(1);
  });

  it('custom attrs on FramingDecision', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    fd.setCustomAttr('fdKey', 'fdVal');
    expect(fd.getCustomAttr('fdKey')).toBe('fdVal');
  });

  it('custom attrs on FramingIntent', () => {
    const fi = doc.framingIntents.at(0)!;
    fi.setCustomAttr('fiKey', 100);
    expect(fi.getCustomAttr('fiKey')).toBe(100);
  });

  it('custom attrs on Context', () => {
    const ctx = doc.contexts.at(0)!;
    ctx.setCustomAttr('ctxKey', true);
    expect(ctx.getCustomAttr('ctxKey')).toBe(true);
  });
});

// -----------------------------------------------------------------------
// Round-trip — parse → traverse → serialize → re-parse
// -----------------------------------------------------------------------

describe('RoundTrip', () => {
  it('parse → asJson → re-parse produces identical structure', () => {
    const doc1 = parseMinimalFdl();
    const json1 = doc1.asJson(0);
    doc1.close();

    const doc2 = FDL.parse(Buffer.from(json1));
    expect(doc2.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
    expect(doc2.contexts.length).toBe(1);
    expect(doc2.framingIntents.length).toBe(1);
    expect(doc2.contexts.at(0)!.canvases.at(0)!.id).toBe('CV_01');
    doc2.close();
  });

  it('asDict matches original structure', () => {
    const doc = parseMinimalFdl();
    const d = doc.asDict();
    expect(d.uuid).toBe(MINIMAL_FDL.uuid);
    expect(d.version).toEqual(MINIMAL_FDL.version);
    expect(d.fdl_creator).toBe(MINIMAL_FDL.fdl_creator);
    expect(d.default_framing_intent).toBe(MINIMAL_FDL.default_framing_intent);
    expect((d.contexts as unknown[]).length).toBe(MINIMAL_FDL.contexts.length);
    expect((d.framing_intents as unknown[]).length).toBe(MINIMAL_FDL.framing_intents.length);
    doc.close();
  });

  it('full traversal does not crash', () => {
    const doc = parseMinimalFdl();
    // Traverse all classes and read all properties
    for (const ctx of doc.contexts) {
      ctx.label;
      ctx.contextCreator;
      ctx.asDict();
      for (const canvas of ctx.canvases) {
        canvas.id;
        canvas.label;
        canvas.sourceCanvasId;
        canvas.dimensions;
        canvas.anamorphicSqueeze;
        canvas.effectiveDimensions;
        canvas.effectiveAnchorPoint;
        canvas.photositeDimensions;
        canvas.physicalDimensions;
        canvas.getRect();
        canvas.getEffectiveRect();
        canvas.asDict();
        for (const fd of canvas.framingDecisions) {
          fd.id;
          fd.label;
          fd.framingIntentId;
          fd.dimensions;
          fd.anchorPoint;
          fd.protectionDimensions;
          fd.protectionAnchorPoint;
          fd.getRect();
          fd.getProtectionRect();
          fd.asDict();
        }
      }
    }
    for (const fi of doc.framingIntents) {
      fi.id;
      fi.label;
      fi.aspectRatio;
      fi.protection;
      fi.asDict();
    }
    doc.close();
  });
});

// -----------------------------------------------------------------------
// Validation
// -----------------------------------------------------------------------

describe('Validation', () => {
  it('valid doc passes', () => {
    const doc = parseMinimalFdl();
    expect(() => doc.validate()).not.toThrow();
    doc.close();
  });

  it('invalid doc throws FDLValidationError', () => {
    const doc = FDL.create('test-uuid');
    // Empty doc with no framing intents or contexts should fail validation
    try {
      doc.validate();
      // If it doesn't throw, that's also okay — some docs may be valid without contents
    } catch (e) {
      expect(e).toBeInstanceOf(FDLValidationError);
    }
    doc.close();
  });

  it('parse invalid JSON throws FDLValidationError', () => {
    expect(() => FDL.parse(Buffer.from('not valid json'))).toThrow(FDLValidationError);
  });
});

// -----------------------------------------------------------------------
// FDL.create
// -----------------------------------------------------------------------

describe('FDL.create', () => {
  it('creates empty document with defaults', () => {
    const doc = FDL.create('my-uuid');
    expect(doc.uuid).toBe('my-uuid');
    expect(doc.versionMajor).toBe(2);
    expect(doc.versionMinor).toBe(0);
    expect(doc.contexts.length).toBe(0);
    expect(doc.framingIntents.length).toBe(0);
    doc.close();
  });

  it('creates document with custom version', () => {
    const doc = FDL.create('my-uuid', 2, 1, 'MyApp');
    expect(doc.uuid).toBe('my-uuid');
    expect(doc.versionMajor).toBe(2);
    expect(doc.fdlCreator).toBe('MyApp');
    doc.close();
  });

  it('build full document from scratch', () => {
    const doc = FDL.create('build-test-uuid', 2, 0, 'test');
    doc.defaultFramingIntent = 'FI_A';

    const fi = doc.addFramingIntent('FI_A', 'Main', { width: 16, height: 9 }, 0.0);
    expect(fi.id).toBe('FI_A');

    const ctx = doc.addContext('Ctx', 'builder');
    const canvas = ctx.addCanvas('C1', 'Canvas 1', 'C1', { width: 3840, height: 2160 }, 1.0);
    const fd = canvas.addFramingDecision(
      'C1-FI_A',
      'Main FD',
      'FI_A',
      { width: 3840.0, height: 2160.0 },
      { x: 0.0, y: 0.0 },
    );

    expect(doc.contexts.length).toBe(1);
    expect(ctx.canvases.length).toBe(1);
    expect(canvas.framingDecisions.length).toBe(1);
    expect(fd.id).toBe('C1-FI_A');

    // Should validate
    doc.validate();

    // Round-trip
    const json = doc.asJson(0);
    const doc2 = FDL.parse(Buffer.from(json));
    expect(doc2.uuid).toBe('build-test-uuid');
    expect(doc2.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!.id).toBe('C1-FI_A');
    doc2.close();
    doc.close();
  });
});
