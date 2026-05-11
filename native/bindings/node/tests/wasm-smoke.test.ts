// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * WASM backend smoke tests — verify the Emscripten-compiled module loads
 * and exposes the same C ABI surface used by the facade layer.
 *
 * This test file imports from `../src/wasm/index.js`, which is the
 * browser/universal entry point. It is gated on the WASM artifacts being
 * present in `wasm/` (built via `python scripts/build_wasm.py`); when they
 * are missing, the suite skips so local `npm test` runs are unaffected.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const wasmFile = join(here, '..', 'wasm', 'fdl_module.wasm');
const wasmAvailable = existsSync(wasmFile);

describe.skipIf(!wasmAvailable)('WASM backend', () => {
  let initialize: typeof import('../src/wasm/index.js')['initialize'];
  let FDL: typeof import('../src/wasm/index.js')['FDL'];
  let getAddon: typeof import('../src/ffi/index.js')['getAddon'];

  beforeAll(async () => {
    const mod = await import('../src/wasm/index.js');
    initialize = mod.initialize;
    FDL = mod.FDL;
    getAddon = (await import('../src/ffi/index.js')).getAddon;
    await initialize();
  });

  it('exposes the ABI version', () => {
    const addon = getAddon();
    const ver = addon.fdl_abi_version();
    expect(ver).toHaveProperty('major');
    expect(ver).toHaveProperty('minor');
    expect(ver).toHaveProperty('patch');
    expect(ver.major).toBe(0);
    expect(ver.minor).toBeGreaterThanOrEqual(3);
  });

  it('creates and frees an empty document', () => {
    const addon = getAddon();
    const doc = addon.fdl_doc_create();
    expect(doc).toBeTruthy();
    addon.fdl_doc_free(doc);
  });

  it('parses JSON and round-trips through the facade', () => {
    const fdl = {
      uuid: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
      version: { major: 2, minor: 0 },
      fdl_creator: 'wasm-test',
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
          context_creator: 'wasm-test',
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
    const doc = FDL.parse(JSON.stringify(fdl));
    try {
      expect(doc.uuid).toBe('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
      expect(doc.fdlCreator).toBe('wasm-test');
      const out = doc.asJson();
      expect(out).toContain('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee');
    } finally {
      doc.close();
    }
  });

  it('handles struct round-trip for dimensions', () => {
    const addon = getAddon();
    const zero = addon.fdl_dimensions_i64_is_zero({ width: 0, height: 0 });
    expect(zero).toBeTruthy();
    const nonZero = addon.fdl_dimensions_i64_is_zero({ width: 1920, height: 1080 });
    expect(nonZero).toBeFalsy();
  });
});
