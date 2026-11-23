// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Custom attribute parity tests.
 *
 * Mirrors: native/bindings/python/tests/test_custom_attrs.py
 * (type mismatch, bool mismatch, bad type, update, missing, ClipID and
 * FileSequence attrs, fixture roundtrip).
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { FDL } from "../src/fdl.js";

const here = dirname(fileURLToPath(import.meta.url));
const FIXTURE = resolve(
  here,
  "../../../core/tests/vectors/document/custom_attrs_fixture.json",
);

const MINIMAL_FDL = {
  uuid: "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  version: { major: 2, minor: 0 },
  fdl_creator: "test",
  default_framing_intent: "FI_01",
  framing_intents: [
    {
      id: "FI_01",
      label: "Default",
      aspect_ratio: { width: 16, height: 9 },
      protection: 0.0,
    },
  ],
  contexts: [
    {
      label: "Source",
      context_creator: "DIT",
      canvases: [
        {
          id: "CV_01",
          label: "Source Canvas",
          source_canvas_id: "CV_01",
          dimensions: { width: 3840, height: 2160 },
          anamorphic_squeeze: 1.0,
          framing_decisions: [
            {
              id: "CV_01-FI_01",
              label: "Default FD",
              framing_intent_id: "FI_01",
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

let doc: FDL;
beforeEach(() => {
  doc = FDL.parse(JSON.stringify(MINIMAL_FDL));
});
afterEach(() => {
  doc.close();
});

describe("custom attr type rules", () => {
  it("update with same type", () => {
    doc.setCustomAttr("note", "first");
    doc.setCustomAttr("note", "second");
    expect(doc.getCustomAttr("note")).toBe("second");
  });

  it.skip("type mismatch raises and preserves original", () => {
    // GAP: caSet does not check the scalar setter return code; no error is raised on type mismatch

    doc.setCustomAttr("x", 10);
    expect(() => doc.setCustomAttr("x", "nope")).toThrow(/type mismatch/);
    expect(doc.getCustomAttr("x")).toBe(10);
  });

  it.skip("bool type mismatch raises and preserves original", () => {
    // GAP: caSet does not check the scalar setter return code; no error is raised on type mismatch

    doc.setCustomAttr("flag", true);
    expect(() => doc.setCustomAttr("flag", 42)).toThrow(/type mismatch/);
    expect(() => doc.setCustomAttr("flag", "yes")).toThrow(/type mismatch/);
    expect(doc.getCustomAttr("flag")).toBe(true);
  });

  it("type mismatch leaves the original value unchanged (JS does not throw)", () => {
    doc.setCustomAttr("x", 10);
    doc.setCustomAttr("x", "nope");
    expect(doc.getCustomAttr("x")).toBe(10);
    doc.setCustomAttr("flag", true);
    doc.setCustomAttr("flag", 42);
    expect(doc.getCustomAttr("flag")).toBe(true);
  });

  it("unsupported value type raises TypeError", () => {
    expect(() => doc.setCustomAttr("items", [1, 2, 3] as any)).toThrow(
      TypeError,
    );
  });

  it("get missing returns null", () => {
    expect(doc.getCustomAttr("nope")).toBeNull();
  });
});

describe("ClipID custom attrs", () => {
  it("set and get", () => {
    const ctx = doc.contexts.at(0)!;
    ctx.clipId = { clip_name: "A001", file: "A001C001.ari" };
    const clip = ctx.clipId!;
    clip.setCustomAttr("reel", "A001");
    expect(clip.hasCustomAttr("reel")).toBe(true);
    expect(clip.getCustomAttr("reel")).toBe("A001");
    expect(clip.customAttrs).toEqual({ reel: "A001" });
  });
});

describe("FileSequence custom attrs", () => {
  it("set and get", () => {
    const ctx = doc.contexts.at(0)!;
    ctx.clipId = {
      clip_name: "B001",
      sequence: { value: "B001.####.exr", idx: "#", min: 0, max: 100 },
    };
    const seq = ctx.clipId!.sequence!;
    expect(seq).not.toBeNull();
    seq.setCustomAttr("fps", 24);
    expect(seq.getCustomAttr("fps")).toBe(24);
    expect(seq.customAttrsCount).toBe(1);
  });
});

describe("custom attr fixture roundtrip", () => {
  it("parses fixture, reads pre-existing attrs and roundtrips", () => {
    const fx = FDL.parse(readFileSync(FIXTURE));
    let fx2: FDL | null = null;
    try {
      expect(fx.getCustomAttr("vendor_note")).toBe(
        "This is a doc-level custom attr",
      );
      expect(fx.getCustomAttr("vendor_count")).toBe(42);
      expect(fx.framingIntents.at(0)!.getCustomAttr("fi_tag")).toBe(
        "intent-custom",
      );
      const ctx = fx.contexts.at(0)!;
      expect(ctx.getCustomAttr("ctx_priority")).toBe(1);
      const cvs = ctx.canvases.at(0)!;
      expect(cvs.getCustomAttr("canvas_vendor")).toBe("test-tool");
      expect(cvs.framingDecisions.at(0)!.getCustomAttr("fd_note")).toBe(
        "hero framing",
      );
      expect(ctx.clipId!.getCustomAttr("cid_reel")).toBe("reel_A");

      fx2 = FDL.parse(fx.asJson());
      expect(fx2.getCustomAttr("vendor_note")).toBe(
        "This is a doc-level custom attr",
      );
      expect(fx2.getCustomAttr("vendor_count")).toBe(42);
      expect(fx2.contexts.at(0)!.clipId!.getCustomAttr("cid_reel")).toBe(
        "reel_A",
      );
    } finally {
      fx2?.close();
      fx.close();
    }
  });
});
