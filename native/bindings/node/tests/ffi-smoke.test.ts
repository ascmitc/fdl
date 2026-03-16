// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Low-level FFI smoke tests — verify the N-API addon loads and basic
 * C function calls work correctly.
 */

import { describe, it, expect } from 'vitest';
import { getAddon, isAvailable } from '../src/ffi/index.js';

describe('N-API addon', () => {
  it('should be available', () => {
    expect(isAvailable()).toBe(true);
  });

  it('should report ABI version', () => {
    const addon = getAddon();
    const ver = addon.fdl_abi_version();
    expect(ver).toHaveProperty('major');
    expect(ver).toHaveProperty('minor');
    expect(ver).toHaveProperty('patch');
    expect(ver.major).toBe(0);
    expect(ver.minor).toBeGreaterThanOrEqual(3);
  });

  it('should create and free a document', () => {
    const addon = getAddon();
    const doc = addon.fdl_doc_create();
    expect(doc).toBeTruthy();
    addon.fdl_doc_free(doc);
  });

  it('should parse JSON and round-trip', () => {
    const addon = getAddon();
    // Minimal valid FDL document (inner format — no "fdl" wrapper)
    const fdl = {
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
          context_creator: 'test',
          canvases: [
            {
              id: 'C_01',
              label: 'Main',
              source_canvas_id: '',
              dimensions: { width: 3840, height: 2160 },
              photo_site_dimensions: { width: 3840, height: 2160 },
              effective_dimensions: { width: 0, height: 0 },
              effective_anchor_point: { x: 0, y: 0 },
              framing_decisions: [
                {
                  id: 'FD_01',
                  framing_intent_id: 'FI_01',
                  dimensions: { width: 3840, height: 2160 },
                  anchor_point: { x: 0, y: 0 },
                },
              ],
            },
          ],
        },
      ],
    };
    const json = JSON.stringify(fdl);
    const result = addon.fdl_doc_parse_json(json, json.length);
    expect(result).toHaveProperty('doc');
    expect(result.error).toBeFalsy();

    const uuid = addon.fdl_doc_get_uuid(result.doc);
    expect(uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');

    const outJson = addon.fdl_doc_to_json(result.doc, 0);
    expect(outJson).toContain('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');

    addon.fdl_doc_free(result.doc);
  });

  it('should make a rect via addon', () => {
    const addon = getAddon();
    const rect = addon.fdl_make_rect(10, 20, 100, 200);
    expect(rect.x).toBeCloseTo(10);
    expect(rect.y).toBeCloseTo(20);
    expect(rect.width).toBeCloseTo(100);
    expect(rect.height).toBeCloseTo(200);
  });

  it('should do struct round-trip for dimensions', () => {
    const addon = getAddon();
    // fdl_dimensions_i64_is_zero expects a plain object
    const zero = addon.fdl_dimensions_i64_is_zero({ width: 0, height: 0 });
    expect(zero).toBeTruthy();
    const nonZero = addon.fdl_dimensions_i64_is_zero({ width: 1920, height: 1080 });
    expect(nonZero).toBeFalsy();
  });
});
