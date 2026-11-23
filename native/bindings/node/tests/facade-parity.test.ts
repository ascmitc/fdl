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
  it.skip("contexts negative index", () => {
    // GAP: CollectionWrapper.at() has no negative indexing (returns null for -1)
    expect(doc.contexts.at(-1)!.label).toBe("Source");
  });

  it("contexts out-of-range index returns null (Python raises IndexError)", () => {
    expect(doc.contexts.at(99)).toBeNull();
  });

  it.skip("contexts out-of-range index raises", () => {
    // GAP: CollectionWrapper.at() returns null instead of throwing for an out-of-range index
    expect(() => doc.contexts.at(99)).toThrow();
  });

  it.skip("contexts findById", () => {
    // GAP: contexts collection has no findById (it throws); Python get_by_id matches the label
    expect(doc.contexts.findById("Source")!.label).toBe("Source");
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
  it.skip("hash", () => {
    // GAP: no hash() equivalent on Context in JS
    expect.fail("not implemented");
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
  it.skip("hash", () => {
    // GAP: no hash() equivalent on Canvas in JS
    expect.fail("not implemented");
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
