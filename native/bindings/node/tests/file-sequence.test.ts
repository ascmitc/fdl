// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Tests for FileSequence serialization (asDict, asJson, toJSON).
 */

import { describe, it, expect } from 'vitest';
import { FDL } from '../src/fdl.js';
import { FileSequence } from '../src/file-sequence.js';

function parseWithClipId(clipIdDict: Record<string, unknown>): FDL {
  const fdlData = {
    uuid: '4ff5d6b1-aaf2-48fd-a947-2d61e45d676a',
    version: { major: 2, minor: 0 },
    fdl_creator: 'ASC FDL Tools',
    framing_intents: [],
    contexts: [
      {
        label: 'test_clipid',
        clip_id: clipIdDict,
        canvases: [],
      },
    ],
    canvas_templates: [],
  };
  return FDL.parse(JSON.stringify(fdlData));
}

describe('FileSequence', () => {
  it('deserializes with correct properties', () => {
    const doc = parseWithClipId({
      clip_name: 'ABX_001_110_911',
      sequence: {
        value: 'ABX_001_110_911.####.exr',
        idx: '#',
        min: 0,
        max: 100,
      },
    });
    const clip = doc.contexts.at(0)!.clipId!;
    const seq = clip.sequence!;
    expect(seq).toBeInstanceOf(FileSequence);
    expect(seq.value).toBe('ABX_001_110_911.####.exr');
    expect(seq.idx).toBe('#');
    expect(seq.min).toBe(0);
    expect(seq.max).toBe(100);
    doc.close();
  });
});

describe('FileSequence.asDict', () => {
  it('returns all properties as a dict', () => {
    const doc = parseWithClipId({
      clip_name: 'A002',
      sequence: {
        value: 'A002.####.exr',
        idx: '#',
        min: 10,
        max: 200,
      },
    });
    const seq = doc.contexts.at(0)!.clipId!.sequence!;
    const d = seq.asDict();
    expect(d).toEqual({
      value: 'A002.####.exr',
      idx: '#',
      min: 10,
      max: 200,
    });
    doc.close();
  });
});

describe('FileSequence.asJson', () => {
  it('returns valid JSON string', () => {
    const doc = parseWithClipId({
      clip_name: 'B001',
      sequence: {
        value: 'B001.####.dpx',
        idx: '#',
        min: 0,
        max: 50,
      },
    });
    const seq = doc.contexts.at(0)!.clipId!.sequence!;
    const jsonStr = seq.asJson();
    const parsed = JSON.parse(jsonStr);
    expect(parsed.value).toBe('B001.####.dpx');
    expect(parsed.idx).toBe('#');
    expect(parsed.min).toBe(0);
    expect(parsed.max).toBe(50);
    doc.close();
  });

  it('supports indented output', () => {
    const doc = parseWithClipId({
      clip_name: 'C001',
      sequence: { value: 'C001.####.exr', idx: '#', min: 1, max: 99 },
    });
    const seq = doc.contexts.at(0)!.clipId!.sequence!;
    const jsonStr = seq.asJson(2);
    expect(jsonStr).toContain('\n');
    expect(JSON.parse(jsonStr).max).toBe(99);
    doc.close();
  });
});

describe('FileSequence.toJSON', () => {
  it('works with JSON.stringify', () => {
    const doc = parseWithClipId({
      clip_name: 'D001',
      sequence: { value: 'D001.####.exr', idx: '#', min: 5, max: 500 },
    });
    const seq = doc.contexts.at(0)!.clipId!.sequence!;
    const json = JSON.stringify(seq);
    const parsed = JSON.parse(json);
    expect(parsed.value).toBe('D001.####.exr');
    expect(parsed.min).toBe(5);
    expect(parsed.max).toBe(500);
    doc.close();
  });
});
