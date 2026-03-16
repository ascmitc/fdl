// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Tests for complex-type custom attributes (PointFloat, DimensionsFloat, DimensionsInt).
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { FDL } from '../src/fdl.js';
import { PointFloat, DimensionsFloat, DimensionsInt } from '../src/types.js';

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
      context_creator: 'DIT',
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
  return FDL.parse(JSON.stringify(MINIMAL_FDL));
}

// -----------------------------------------------------------------------
// PointFloat custom attrs
// -----------------------------------------------------------------------

describe('PointFloat custom attrs', () => {
  let doc: FDL;
  beforeEach(() => { doc = parseMinimalFdl(); });
  afterEach(() => { doc.close(); });

  it('set and get PointFloat on FDL', () => {
    const pt = new PointFloat(1.5, 2.5);
    doc.setCustomAttr('origin', pt);
    const got = doc.getCustomAttr('origin');
    expect(got).toBeInstanceOf(PointFloat);
    expect((got as PointFloat).x).toBeCloseTo(1.5);
    expect((got as PointFloat).y).toBeCloseTo(2.5);
  });

  it('set and get PointFloat on Canvas', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    canvas.setCustomAttr('offset', new PointFloat(10, 20));
    const got = canvas.getCustomAttr('offset') as PointFloat;
    expect(got).toBeInstanceOf(PointFloat);
    expect(got.x).toBeCloseTo(10);
    expect(got.y).toBeCloseTo(20);
  });

  it('set and get PointFloat on FramingDecision', () => {
    const fd = doc.contexts.at(0)!.canvases.at(0)!.framingDecisions.at(0)!;
    fd.setCustomAttr('center', new PointFloat(-5.5, 3.14));
    const got = fd.getCustomAttr('center') as PointFloat;
    expect(got).toBeInstanceOf(PointFloat);
    expect(got.x).toBeCloseTo(-5.5);
    expect(got.y).toBeCloseTo(3.14);
  });

  it('set and get PointFloat on FramingIntent', () => {
    const fi = doc.framingIntents.at(0)!;
    fi.setCustomAttr('anchor', new PointFloat(0, 0));
    const got = fi.getCustomAttr('anchor') as PointFloat;
    expect(got).toBeInstanceOf(PointFloat);
    expect(got.x).toBeCloseTo(0);
    expect(got.y).toBeCloseTo(0);
  });

  it('set and get PointFloat on Context', () => {
    const ctx = doc.contexts.at(0)!;
    ctx.setCustomAttr('ref_point', new PointFloat(100.5, 200.5));
    const got = ctx.getCustomAttr('ref_point') as PointFloat;
    expect(got).toBeInstanceOf(PointFloat);
    expect(got.x).toBeCloseTo(100.5);
    expect(got.y).toBeCloseTo(200.5);
  });
});

// -----------------------------------------------------------------------
// DimensionsFloat custom attrs
// -----------------------------------------------------------------------

describe('DimensionsFloat custom attrs', () => {
  let doc: FDL;
  beforeEach(() => { doc = parseMinimalFdl(); });
  afterEach(() => { doc.close(); });

  it('set and get DimensionsFloat on FDL', () => {
    const dims = new DimensionsFloat(1920.5, 1080.5);
    doc.setCustomAttr('viewport', dims);
    const got = doc.getCustomAttr('viewport');
    expect(got).toBeInstanceOf(DimensionsFloat);
    expect((got as DimensionsFloat).width).toBeCloseTo(1920.5);
    expect((got as DimensionsFloat).height).toBeCloseTo(1080.5);
  });

  it('set and get DimensionsFloat on Canvas', () => {
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    canvas.setCustomAttr('safe_area', new DimensionsFloat(3200.0, 1800.0));
    const got = canvas.getCustomAttr('safe_area') as DimensionsFloat;
    expect(got).toBeInstanceOf(DimensionsFloat);
    expect(got.width).toBeCloseTo(3200.0);
    expect(got.height).toBeCloseTo(1800.0);
  });
});

// -----------------------------------------------------------------------
// DimensionsInt custom attrs
// -----------------------------------------------------------------------

describe('DimensionsInt custom attrs', () => {
  let doc: FDL;
  beforeEach(() => { doc = parseMinimalFdl(); });
  afterEach(() => { doc.close(); });

  it('set and get DimensionsInt on FDL', () => {
    const dims = new DimensionsInt(1920, 1080);
    doc.setCustomAttr('resolution', dims);
    const got = doc.getCustomAttr('resolution');
    expect(got).toBeInstanceOf(DimensionsInt);
    expect((got as DimensionsInt).width).toBe(1920);
    expect((got as DimensionsInt).height).toBe(1080);
  });

  it('set and get DimensionsInt on FramingIntent', () => {
    const fi = doc.framingIntents.at(0)!;
    fi.setCustomAttr('grid', new DimensionsInt(4, 3));
    const got = fi.getCustomAttr('grid') as DimensionsInt;
    expect(got).toBeInstanceOf(DimensionsInt);
    expect(got.width).toBe(4);
    expect(got.height).toBe(3);
  });
});

// -----------------------------------------------------------------------
// Mixed types in customAttrs dict
// -----------------------------------------------------------------------

describe('Mixed custom attrs dict', () => {
  let doc: FDL;
  beforeEach(() => { doc = parseMinimalFdl(); });
  afterEach(() => { doc.close(); });

  it('customAttrs returns all types including complex', () => {
    doc.setCustomAttr('name', 'test');
    doc.setCustomAttr('count', 42);
    doc.setCustomAttr('origin', new PointFloat(1, 2));
    doc.setCustomAttr('size', new DimensionsFloat(100, 200));
    doc.setCustomAttr('res', new DimensionsInt(1920, 1080));
    const attrs = doc.customAttrs;
    expect(attrs['name']).toBe('test');
    expect(attrs['count']).toBe(42);
    expect(attrs['origin']).toBeInstanceOf(PointFloat);
    expect(attrs['size']).toBeInstanceOf(DimensionsFloat);
    expect(attrs['res']).toBeInstanceOf(DimensionsInt);
  });
});

// -----------------------------------------------------------------------
// Roundtrip — complex attrs survive serialize → re-parse
// -----------------------------------------------------------------------

describe('Complex custom attrs roundtrip', () => {
  it('PointFloat survives JSON roundtrip', () => {
    const doc = parseMinimalFdl();
    doc.setCustomAttr('pt', new PointFloat(3.14, 2.72));
    const json = doc.asJson();
    doc.close();

    const doc2 = FDL.parse(json);
    const got = doc2.getCustomAttr('pt') as PointFloat;
    expect(got).toBeInstanceOf(PointFloat);
    expect(got.x).toBeCloseTo(3.14);
    expect(got.y).toBeCloseTo(2.72);
    doc2.close();
  });

  it('DimensionsFloat survives JSON roundtrip', () => {
    const doc = parseMinimalFdl();
    doc.setCustomAttr('dims', new DimensionsFloat(1920.5, 1080.5));
    const json = doc.asJson();
    doc.close();

    const doc2 = FDL.parse(json);
    const got = doc2.getCustomAttr('dims') as DimensionsFloat;
    expect(got).toBeInstanceOf(DimensionsFloat);
    expect(got.width).toBeCloseTo(1920.5);
    expect(got.height).toBeCloseTo(1080.5);
    doc2.close();
  });

  it('DimensionsInt survives JSON roundtrip', () => {
    const doc = parseMinimalFdl();
    doc.setCustomAttr('res', new DimensionsInt(4096, 2160));
    const json = doc.asJson();
    doc.close();

    const doc2 = FDL.parse(json);
    const got = doc2.getCustomAttr('res') as DimensionsInt;
    expect(got).toBeInstanceOf(DimensionsInt);
    expect(got.width).toBe(4096);
    expect(got.height).toBe(2160);
    doc2.close();
  });
});
