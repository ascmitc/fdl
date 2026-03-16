// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Canvas template application tests.
 *
 * Mirrors: native/bindings/python/tests/test_canvas_template.py (partial)
 */

import { describe, it, expect } from 'vitest';
import { FDL } from '../src/fdl.js';
import { CanvasTemplate, TemplateResult } from '../src/canvas-template.js';
import { DimensionsInt, DimensionsFloat, PointFloat } from '../src/types.js';
import { GeometryPath, FitMethod, HAlign, VAlign } from '../src/constants.js';

describe('CanvasTemplate.apply', () => {
  it('creates output canvas from template', () => {
    // Build source FDL with a canvas and framing decision
    const fdl = new FDL({});
    fdl.addFramingIntent('FI_A', 'Default', new DimensionsInt(16, 9), 0.0);
    const ctx = fdl.addContext('Primary', null);
    const canvas = ctx.addCanvas(
      'C1', 'Source', 'C1', new DimensionsInt(1920, 1080), 1.0,
    );
    canvas.setEffective(new DimensionsInt(1920, 1080), new PointFloat(0, 0));
    const fd = canvas.addFramingDecision(
      'C1-FI_A', '', 'FI_A',
      new DimensionsFloat(1920, 1080), new PointFloat(0, 0),
    );

    // Create template targeting HD
    const tmpl = new CanvasTemplate({
      id: 'HD',
      label: 'HD Template',
      targetDimensions: new DimensionsInt(1920, 1080),
      fitSource: GeometryPath.FRAMING_DIMENSIONS,
      fitMethod: FitMethod.WIDTH,
      alignmentMethodHorizontal: HAlign.CENTER,
      alignmentMethodVertical: VAlign.CENTER,
    });

    // Apply template
    const result = tmpl.apply(canvas, fd, 'C2', 'C2-FI_A', null, null);
    expect(result.fdl).toBeTruthy();
    expect(result._canvas_id).toBe('C2');
    expect(result._framing_decision_id).toBe('C2-FI_A');

    result.fdl.close();
    fdl.close();
  });

  it('creates scaled output for different target', () => {
    const fdl = new FDL({});
    fdl.addFramingIntent('FI_A', '', new DimensionsInt(16, 9), 0.0);
    const ctx = fdl.addContext('Primary', null);
    const canvas = ctx.addCanvas(
      'C1', '', 'C1', new DimensionsInt(3840, 2160), 1.0,
    );
    canvas.setEffective(new DimensionsInt(3840, 2160), new PointFloat(0, 0));
    const fd = canvas.addFramingDecision(
      'C1-FI_A', '', 'FI_A',
      new DimensionsFloat(3840, 2160), new PointFloat(0, 0),
    );

    // Target is HD (half of UHD)
    const tmpl = new CanvasTemplate({
      id: 'HD',
      targetDimensions: new DimensionsInt(1920, 1080),
      fitSource: GeometryPath.FRAMING_DIMENSIONS,
      fitMethod: FitMethod.WIDTH,
    });

    const result = tmpl.apply(canvas, fd, 'C2', 'C2-FI_A');

    // Navigate into result FDL to find the output canvas by id
    const resultDoc = result.fdl;
    const json = resultDoc.asJson();
    const parsed = JSON.parse(json);
    // Find the output canvas by the returned canvas_id
    let outputCanvas: Record<string, unknown> | undefined;
    for (const ctx of parsed.contexts) {
      for (const c of ctx.canvases) {
        if (c.id === result._canvas_id) {
          outputCanvas = c;
        }
      }
    }
    expect(outputCanvas).toBeDefined();
    expect(outputCanvas!.dimensions).toEqual({ width: 1920, height: 1080 });

    resultDoc.close();
    fdl.close();
  });
});

describe('TemplateResult convenience properties', () => {
  it('context returns the created Context', () => {
    const fdl = new FDL({});
    fdl.addFramingIntent('FI_A', '', new DimensionsInt(16, 9), 0.0);
    const ctx = fdl.addContext('Primary', null);
    const canvas = ctx.addCanvas(
      'C1', '', 'C1', new DimensionsInt(1920, 1080), 1.0,
    );
    canvas.setEffective(new DimensionsInt(1920, 1080), new PointFloat(0, 0));
    const fd = canvas.addFramingDecision(
      'C1-FI_A', '', 'FI_A',
      new DimensionsFloat(1920, 1080), new PointFloat(0, 0),
    );

    const tmpl = new CanvasTemplate({
      id: 'HD',
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    const result = tmpl.apply(canvas, fd, 'C2', 'C2-FI_A');

    expect(result).toBeInstanceOf(TemplateResult);
    expect(result.context).not.toBeNull();
    expect(result.context!.label).toBe(result._context_label);

    result.fdl.close();
    fdl.close();
  });

  it('canvas returns the created Canvas', () => {
    const fdl = new FDL({});
    fdl.addFramingIntent('FI_A', '', new DimensionsInt(16, 9), 0.0);
    const ctx = fdl.addContext('Primary', null);
    const canvas = ctx.addCanvas(
      'C1', '', 'C1', new DimensionsInt(1920, 1080), 1.0,
    );
    canvas.setEffective(new DimensionsInt(1920, 1080), new PointFloat(0, 0));
    const fd = canvas.addFramingDecision(
      'C1-FI_A', '', 'FI_A',
      new DimensionsFloat(1920, 1080), new PointFloat(0, 0),
    );

    const tmpl = new CanvasTemplate({
      id: 'HD',
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    const result = tmpl.apply(canvas, fd, 'C2', 'C2-FI_A');

    expect(result.canvas).not.toBeNull();
    expect(result.canvas!.id).toBe('C2');

    result.fdl.close();
    fdl.close();
  });

  it('framingDecision returns the created FramingDecision', () => {
    const fdl = new FDL({});
    fdl.addFramingIntent('FI_A', '', new DimensionsInt(16, 9), 0.0);
    const ctx = fdl.addContext('Primary', null);
    const canvas = ctx.addCanvas(
      'C1', '', 'C1', new DimensionsInt(1920, 1080), 1.0,
    );
    canvas.setEffective(new DimensionsInt(1920, 1080), new PointFloat(0, 0));
    const fd = canvas.addFramingDecision(
      'C1-FI_A', '', 'FI_A',
      new DimensionsFloat(1920, 1080), new PointFloat(0, 0),
    );

    const tmpl = new CanvasTemplate({
      id: 'HD',
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    const result = tmpl.apply(canvas, fd, 'C2', 'C2-FI_A');

    expect(result.framingDecision).not.toBeNull();
    expect(result.framingDecision!.id).toBe('C2-FI_A');

    result.fdl.close();
    fdl.close();
  });
});

describe('CanvasTemplate JSON roundtrip', () => {
  it('asJson and asDict are consistent', () => {
    const ct = new CanvasTemplate({
      id: 'CT-RT',
      label: 'RoundTrip',
      targetDimensions: new DimensionsInt(1920, 1080),
      fitSource: GeometryPath.CANVAS_DIMENSIONS,
      fitMethod: FitMethod.FIT_ALL,
      alignmentMethodHorizontal: HAlign.LEFT,
      alignmentMethodVertical: VAlign.TOP,
    });
    const json = ct.asJson(2);
    const dict = ct.asDict();
    const fromJson = JSON.parse(json);
    expect(fromJson).toEqual(dict);
  });

  it('toJSON works with JSON.stringify', () => {
    const ct = new CanvasTemplate({
      id: 'CT-JSON',
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    const str = JSON.stringify(ct);
    const parsed = JSON.parse(str);
    expect(parsed.id).toBe('CT-JSON');
  });
});
