// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Facade parity tests: collections, clip id, canvas resolution and dump shape.
 *
 * Mirrors: native/bindings/python/tests/test_facade.py
 * (TestCollections, TestContext clip-id tests, TestModelDumpParity, TestResolveCanvas)
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { FDL } from "../src/fdl.js";
import { DimensionsFloat, DimensionsInt, PointFloat } from "../src/types.js";

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

// -----------------------------------------------------------------------
// Collections (Python TestCollections)
// -----------------------------------------------------------------------

describe("Collections parity", () => {
  // JS deliberately differs from Python here: a miss returns null rather than raising, but
  // negative indexes count from the end, as Array.prototype.at does.
  it("contexts negative index counts from the end", () => {
    expect(doc.contexts.at(-1)!.label).toBe("Source");
    expect(
      doc.contexts.at(-1)!.equals(doc.contexts.at(doc.contexts.length - 1)!),
    ).toBe(true);
  });

  it("contexts negative index past the start returns null", () => {
    expect(doc.contexts.at(-(doc.contexts.length + 1))).toBeNull();
  });

  it("contexts out-of-range index returns null (Python raises IndexError)", () => {
    expect(doc.contexts.at(99)).toBeNull();
  });

  // Contexts have no id in the schema, so only the label finder exists (Python's get_by_id
  // falls back to the label). The error says what to use instead.
  it("contexts findById explains that contexts are found by label", () => {
    expect(() => doc.contexts.findById("Source")).toThrow(/findByLabel/);
  });

  it("contexts findByLabel (Python get_by_id)", () => {
    const ctx = doc.contexts.findByLabel("Source");
    expect(ctx).not.toBeNull();
    expect(ctx!.label).toBe("Source");
  });

  it("contexts findByLabel not found", () => {
    expect(doc.contexts.findByLabel("Nonexistent")).toBeNull();
  });

  it("contexts contains", () => {
    const ctx = doc.contexts.at(0)!;
    expect(doc.contexts.toArray().some((c) => c.equals(ctx))).toBe(true);
  });

  it("contexts non-empty is truthy by length", () => {
    expect(doc.contexts.length > 0).toBe(true);
  });

  it("empty canvasTemplates has length zero", () => {
    expect(doc.canvasTemplates.length).toBe(0);
  });

  it("framingIntents findById", () => {
    expect(doc.framingIntents.findById("FI_01")!.id).toBe("FI_01");
  });
});

// -----------------------------------------------------------------------
// Context clip id and hash
// -----------------------------------------------------------------------

describe("Context clip id parity", () => {
  // Python hashes by label; JS Map/Set use object identity and every collection access wraps
  // a fresh object, so a hash would be useless. Use equals() and the label as the key.
  it("equals() compares by content and the label works as a Map key", () => {
    const a = doc.contexts.at(0)!;
    const b = doc.contexts.at(0)!;
    expect(a).not.toBe(b);
    expect(a.equals(b)).toBe(true);
    const byLabel = new Map([[a.label, a]]);
    expect(byLabel.get(b.label)!.equals(b)).toBe(true);
  });

  it("set clipId from object", () => {
    const ctx = doc.contexts.at(0)!;
    expect(ctx.clipId).toBeNull();
    ctx.clipId = { clip_name: "A001", file: "A001C001.ari" };
    const cid = ctx.clipId;
    expect(cid).not.toBeNull();
    expect(cid!.clipName).toBe("A001");
    expect(cid!.file).toBe("A001C001.ari");
    expect(cid!.sequence).toBeNull();
  });

  it("set clipId with sequence", () => {
    const ctx = doc.contexts.at(0)!;
    ctx.clipId = {
      clip_name: "B001",
      sequence: { value: "B001.####.exr", idx: "#", min: 0, max: 100 },
    };
    const cid = ctx.clipId;
    expect(cid).not.toBeNull();
    expect(cid!.clipName).toBe("B001");
    expect(cid!.file).toBeNull();
    expect(cid!.sequence).not.toBeNull();
    expect(cid!.sequence!.value).toBe("B001.####.exr");
  });

  it("remove clipId", () => {
    const ctx = doc.contexts.at(0)!;
    ctx.clipId = { clip_name: "A001", file: "A001C001.ari" };
    expect(ctx.clipId).not.toBeNull();
    ctx.clipId = null;
    expect(ctx.clipId).toBeNull();
  });
});

describe("Canvas hash parity", () => {
  it("equals() compares by content and the id works as a Map key", () => {
    const ctx = doc.contexts.at(0)!;
    const a = ctx.canvases.at(0)!;
    const b = ctx.canvases.at(0)!;
    expect(a).not.toBe(b);
    expect(a.equals(b)).toBe(true);
    const byId = new Map([[a.id, a]]);
    expect(byId.get(b.id)!.equals(b)).toBe(true);
  });
});

// -----------------------------------------------------------------------
// Dump parity
// -----------------------------------------------------------------------

describe("Model dump parity", () => {
  it("excludes unset optional fields", () => {
    const dump = doc.contexts.at(0)!.canvases.at(0)!.asDict();
    expect(dump).not.toHaveProperty("effective_dimensions");
    expect(dump).not.toHaveProperty("photosite_dimensions");
    expect(dump).not.toHaveProperty("physical_dimensions");
    expect(dump).toHaveProperty("id");
    expect(dump).toHaveProperty("dimensions");
  });
});

// -----------------------------------------------------------------------
// resolveCanvasForDimensions
// -----------------------------------------------------------------------

describe("resolveCanvasForDimensions", () => {
  let rdoc: FDL;

  beforeEach(() => {
    rdoc = new FDL({ fdlCreator: "test" });
    rdoc.addFramingIntent("fi_main", "Main FI", new DimensionsInt(16, 9), 0.0);
  });
  afterEach(() => {
    rdoc.close();
  });

  function build() {
    const ctx = rdoc.addContext("ctx", "tester");
    const canvas1 = ctx.addCanvas(
      "cvs1",
      "Canvas 1920x1080",
      "cvs1",
      new DimensionsInt(1920, 1080),
      1.0,
    );
    const fd1 = canvas1.addFramingDecision(
      "fd1",
      "Main",
      "fi_main",
      new DimensionsFloat(1920, 1080),
      new PointFloat(0, 0),
    );
    const canvas2 = ctx.addCanvas(
      "cvs2",
      "Canvas 3840x2160",
      "cvs1",
      new DimensionsInt(3840, 2160),
      1.0,
    );
    const fd2 = canvas2.addFramingDecision(
      "fd2",
      "Main",
      "fi_main",
      new DimensionsFloat(3840, 2160),
      new PointFloat(0, 0),
    );
    return { ctx, canvas1, fd1, canvas2, fd2 };
  }

  it("exact match", () => {
    const { ctx, canvas1, fd1 } = build();
    const result = ctx.resolveCanvasForDimensions(
      new DimensionsFloat(1920, 1080),
      canvas1,
      fd1,
    );
    expect(result.was_resolved).toBe(false);
    expect(result.canvas.id).toBe("cvs1");
  });

  it("resolution via sibling", () => {
    const { ctx, canvas2, fd2 } = build();
    const result = ctx.resolveCanvasForDimensions(
      new DimensionsFloat(1920, 1080),
      canvas2,
      fd2,
    );
    expect(result.was_resolved).toBe(true);
    expect(result.canvas.id).toBe("cvs1");
    expect(result.framing_decision.id).toBe("fd1");
  });

  it("no match throws", () => {
    const { ctx, canvas2, fd2 } = build();
    expect(() =>
      ctx.resolveCanvasForDimensions(
        new DimensionsFloat(9999, 9999),
        canvas2,
        fd2,
      ),
    ).toThrow();
  });
});
