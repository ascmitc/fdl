// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Utility function tests — makeRect, Version, errors, I/O, abiVersion, computeFramingFromIntent.
 */

import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterAll, describe, expect, it } from 'vitest';
import {
  abiVersion,
  computeFramingFromIntent,
  getAnchorFromPath,
  getDimensionsFromPath,
  makeRect,
  writeToFile,
  writeToString,
} from '../src/utils.js';
import { FDL } from '../src/fdl.js';
import { Rect, DimensionsFloat, DimensionsInt, PointFloat } from '../src/types.js';
import { Version } from '../src/version.js';
import { FDLError, FDLValidationError } from '../src/errors.js';
import { RoundStrategy } from '../src/rounding.js';
import { RoundingEven, RoundingMode } from '../src/constants.js';

describe('makeRect', () => {
  it('should create a Rect from coordinates', () => {
    const r = makeRect(10, 20, 100, 200);
    expect(r).toBeInstanceOf(Rect);
    expect(r.x).toBeCloseTo(10);
    expect(r.y).toBeCloseTo(20);
    expect(r.width).toBeCloseTo(100);
    expect(r.height).toBeCloseTo(200);
  });
});

describe('Version', () => {
  it('should construct with defaults', () => {
    const v = new Version();
    expect(v.major).toBe(2);
    expect(v.minor).toBe(0);
  });

  it('should construct with custom values', () => {
    const v = new Version(3, 1);
    expect(v.major).toBe(3);
    expect(v.minor).toBe(1);
  });

  it('should support equality', () => {
    expect(new Version(2, 0).equals(new Version(2, 0))).toBe(true);
    expect(new Version(2, 0).equals(new Version(2, 1))).toBe(false);
  });

  it('should have patch field', () => {
    const v = new Version(2, 1, 3);
    expect(v.patch).toBe(3);
    const v0 = new Version(2, 0);
    expect(v0.patch).toBe(0);
  });

  it('should include patch in equality', () => {
    expect(new Version(2, 0, 0).equals(new Version(2, 0, 1))).toBe(false);
    expect(new Version(2, 0, 1).equals(new Version(2, 0, 1))).toBe(true);
  });

  it('should have toString', () => {
    const v = new Version(2, 0);
    expect(v.toString()).toBe('Version(major=2, minor=0, patch=0)');
    const v2 = new Version(1, 2, 3);
    expect(v2.toString()).toBe('Version(major=1, minor=2, patch=3)');
  });
});

describe('Errors', () => {
  it('should be instanceof Error', () => {
    expect(new FDLError('test')).toBeInstanceOf(Error);
  });

  it('should have correct names', () => {
    expect(new FDLError('x').name).toBe('FDLError');
    expect(new FDLValidationError('y').name).toBe('FDLValidationError');
  });

  it('FDLValidationError should be subclass of FDLError', () => {
    const err = new FDLValidationError('bad');
    expect(err).toBeInstanceOf(FDLError);
    expect(err).toBeInstanceOf(Error);
  });
});

// -----------------------------------------------------------------------
// Shared fixture
// -----------------------------------------------------------------------

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

const MINIMAL_JSON = JSON.stringify(MINIMAL_FDL);

// -----------------------------------------------------------------------
// I/O convenience functions
// -----------------------------------------------------------------------
// Note: readFromString/readFromFile use createRequire for lazy loading,
// which doesn't work in vitest (runs .ts source, no compiled .js files).
// Those functions are tested via the compiled package. Here we test
// writeToString and writeToFile which don't use the lazy loader.

describe('writeToString', () => {
  it('serializes FDL to JSON string', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const json = writeToString(doc);
    expect(typeof json).toBe('string');
    const parsed = JSON.parse(json);
    expect(parsed.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
    doc.close();
  });

  it('can skip validation', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const json = writeToString(doc, false);
    expect(JSON.parse(json).uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
    doc.close();
  });
});

// Temp directory for file I/O tests
const testTmpDir = mkdtempSync(join(tmpdir(), 'fdl-test-'));
afterAll(() => {
  rmSync(testTmpDir, { recursive: true, force: true });
});

describe('writeToFile', () => {
  it('writes FDL to disk', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const filePath = join(testTmpDir, 'test-write.fdl');
    writeToFile(doc, filePath);
    doc.close();

    expect(existsSync(filePath)).toBe(true);
    const contents = readFileSync(filePath, 'utf-8');
    expect(JSON.parse(contents).uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
  });

  it('validates by default', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const filePath = join(testTmpDir, 'test-validate.fdl');
    // Should not throw for valid FDL
    writeToFile(doc, filePath, true);
    expect(existsSync(filePath)).toBe(true);
    doc.close();
  });
});

// -----------------------------------------------------------------------
// abiVersion
// -----------------------------------------------------------------------

describe('abiVersion', () => {
  it('returns a Version object', () => {
    const v = abiVersion();
    expect(v).toBeInstanceOf(Version);
    expect(typeof v.major).toBe('number');
    expect(typeof v.minor).toBe('number');
  });

  it('has non-negative version numbers', () => {
    const v = abiVersion();
    expect(v.major).toBeGreaterThanOrEqual(0);
    expect(v.minor).toBeGreaterThanOrEqual(0);
  });

  it('includes patch component', () => {
    const v = abiVersion();
    expect(typeof v.patch).toBe('number');
    expect(v.patch).toBeGreaterThanOrEqual(0);
  });
});

// -----------------------------------------------------------------------
// getDimensionsFromPath / getAnchorFromPath
// -----------------------------------------------------------------------

describe('getDimensionsFromPath', () => {
  it('returns zero dims for "none"', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    const dims = getDimensionsFromPath(canvas, fd, 'none');
    expect(dims).toBeInstanceOf(DimensionsFloat);
    expect(dims!.width).toBe(0);
    expect(dims!.height).toBe(0);
    doc.close();
  });

  it('returns zero dims for empty string', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    const dims = getDimensionsFromPath(canvas, fd, '');
    expect(dims!.width).toBe(0);
    expect(dims!.height).toBe(0);
    doc.close();
  });

  it('resolves canvas.dimensions', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    const dims = getDimensionsFromPath(canvas, fd, 'canvas.dimensions');
    expect(dims).toBeInstanceOf(DimensionsFloat);
    expect(dims!.width).toBeCloseTo(3840);
    expect(dims!.height).toBeCloseTo(2160);
    doc.close();
  });

  it('resolves framing_decision.dimensions', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    const dims = getDimensionsFromPath(canvas, fd, 'framing_decision.dimensions');
    expect(dims).toBeInstanceOf(DimensionsFloat);
    expect(dims!.width).toBeCloseTo(3840);
    expect(dims!.height).toBeCloseTo(2160);
    doc.close();
  });

  it('throws for unsupported path', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    expect(() => getDimensionsFromPath(canvas, fd, 'bogus.path')).toThrow(
      'Unsupported source path',
    );
    doc.close();
  });

  it('returns null when not required and data missing', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    // effective_dimensions is not set on our minimal FDL
    const dims = getDimensionsFromPath(
      canvas,
      fd,
      'canvas.effective_dimensions',
      false,
    );
    expect(dims).toBeNull();
    doc.close();
  });
});

describe('getAnchorFromPath', () => {
  it('returns zero for "none"', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    const pt = getAnchorFromPath(canvas, fd, 'none');
    expect(pt).toBeInstanceOf(PointFloat);
    expect(pt.x).toBe(0);
    expect(pt.y).toBe(0);
    doc.close();
  });

  it('returns zero for "canvas.dimensions"', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    const pt = getAnchorFromPath(canvas, fd, 'canvas.dimensions');
    expect(pt.x).toBe(0);
    expect(pt.y).toBe(0);
    doc.close();
  });

  it('resolves framing_decision anchor', () => {
    const doc = FDL.parse(MINIMAL_JSON);
    const canvas = doc.contexts.at(0)!.canvases.at(0)!;
    const fd = canvas.framingDecisions.at(0)!;
    const pt = getAnchorFromPath(canvas, fd, 'framing_decision.dimensions');
    expect(pt).toBeInstanceOf(PointFloat);
    // Anchor for our minimal FDL (framing matches canvas → anchor 0,0)
    expect(pt.x).toBeCloseTo(0);
    expect(pt.y).toBeCloseTo(0);
    doc.close();
  });
});

// -----------------------------------------------------------------------
// computeFramingFromIntent
// -----------------------------------------------------------------------

describe('computeFramingFromIntent', () => {
  it('computes letterbox framing without protection', () => {
    // Matches from_intent_vectors.json "letterbox_no_protection_even_up"
    const result = computeFramingFromIntent(
      new DimensionsFloat(4096, 2160),
      new DimensionsFloat(4096, 2160),
      1.0,
      new DimensionsInt(239, 100),
      0.0,
      new RoundStrategy(RoundingEven.EVEN, RoundingMode.UP),
    );
    expect(result.dimensions).toBeInstanceOf(DimensionsFloat);
    expect(result.dimensions.width).toBeCloseTo(4096);
    expect(result.dimensions.height).toBeCloseTo(1714);
    expect(result.anchorPoint).toBeInstanceOf(PointFloat);
    expect(result.anchorPoint.x).toBeCloseTo(0);
    expect(result.anchorPoint.y).toBeCloseTo(223);
    expect(result.protectionDimensions).toBeNull();
    expect(result.protectionAnchorPoint).toBeNull();
  });

  it('computes letterbox framing with protection', () => {
    // Matches from_intent_vectors.json "letterbox_with_protection"
    const result = computeFramingFromIntent(
      new DimensionsFloat(4096, 2160),
      new DimensionsFloat(4096, 2160),
      1.0,
      new DimensionsInt(239, 100),
      0.1,
      new RoundStrategy(RoundingEven.EVEN, RoundingMode.UP),
    );
    expect(result.dimensions.width).toBeCloseTo(3688);
    expect(result.dimensions.height).toBeCloseTo(1544);
    expect(result.anchorPoint.x).toBeCloseTo(204);
    expect(result.anchorPoint.y).toBeCloseTo(308);
    expect(result.protectionDimensions).not.toBeNull();
    expect(result.protectionDimensions!.width).toBeCloseTo(4096);
    expect(result.protectionDimensions!.height).toBeCloseTo(1714);
    expect(result.protectionAnchorPoint).not.toBeNull();
    expect(result.protectionAnchorPoint!.x).toBeCloseTo(0);
    expect(result.protectionAnchorPoint!.y).toBeCloseTo(223);
  });

  it('uses default rounding when null', () => {
    // Should not throw; uses global default rounding
    const result = computeFramingFromIntent(
      new DimensionsFloat(1920, 1080),
      new DimensionsFloat(1920, 1080),
      1.0,
      new DimensionsInt(16, 9),
      0.0,
      null,
    );
    expect(result.dimensions).toBeInstanceOf(DimensionsFloat);
    expect(result.anchorPoint).toBeInstanceOf(PointFloat);
  });
});
