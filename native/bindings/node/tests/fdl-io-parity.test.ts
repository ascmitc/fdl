// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * FDL construction and file I/O parity tests.
 *
 * Mirrors: native/bindings/python/tests/test_fdl.py
 * (read_from_file unvalidated/validated, setting_default_framing_id,
 * add_canvas_to_context).
 */

import { describe, it, expect } from "vitest";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { FDL } from "../src/fdl.js";
import { FDLValidationError } from "../src/errors.js";
import { DimensionsInt } from "../src/types.js";
import { readFromFile } from "../src/utils-node.js";

const here = dirname(fileURLToPath(import.meta.url));
const SAMPLE_FILE = resolve(
  here,
  "../../python/tests/sample_data/Scenario-9__FDL_DeliveredToVFXVendor.fdl",
);

// readFromFile is the Node-only helper (src/utils-node.ts): it reads the file with node:fs and
// hands the string to the active backend, so it is exercised under both N-API and WASM.
describe("readFromFile", () => {
  it("unvalidated", () => {
    const doc = readFromFile(SAMPLE_FILE, false);
    try {
      expect(doc).toBeInstanceOf(FDL);
    } finally {
      doc.close();
    }
  });

  it("validated", () => {
    const doc = readFromFile(SAMPLE_FILE, true);
    try {
      expect(doc).toBeInstanceOf(FDL);
    } finally {
      doc.close();
    }
  });
});

describe("FDL construction", () => {
  it("setting default framing intent", () => {
    const doc = new FDL({});
    try {
      const fi = doc.addFramingIntent(
        "FDLSMP03",
        "1.78-1 Framing",
        new DimensionsInt(16, 9),
        0.088,
      );
      doc.defaultFramingIntent = fi.id;
      expect(doc.defaultFramingIntent).toBe(fi.id);

      doc.defaultFramingIntent = "nogood";
      expect(() => doc.validate()).toThrow(FDLValidationError);
      expect(() => doc.validate()).toThrow(/nogood/);
    } finally {
      doc.close();
    }
  });

  it("add canvas to context", () => {
    const doc = new FDL({});
    try {
      const ctx = doc.addContext("PanavisionDXL2", "ASC FDL Committee");
      const canvas = ctx.addCanvas(
        "20220310",
        "Open Gate RAW",
        "20220310",
        new DimensionsInt(5184, 4320),
        1.3,
      );
      expect(ctx.canvases.findById("20220310")!.equals(canvas)).toBe(true);
      expect(ctx.canvases.length).toBe(1);

      const ctx2 = doc.addContext("SecondContext");
      const canvas2 = ctx2.addCanvas(
        "20220310",
        "Open Gate RAW",
        "20220310",
        new DimensionsInt(5184, 4320),
        1.3,
      );
      expect(ctx2.canvases.findById("20220310")!.equals(canvas2)).toBe(true);
    } finally {
      doc.close();
    }
  });
});
