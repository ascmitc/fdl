// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * ClipID and FileSequence tests.
 *
 * Mirrors: native/bindings/python/tests/test_clipid.py
 */

import { describe, it, expect } from "vitest";
import { FDL } from "../src/fdl.js";
import { ClipID } from "../src/clip-id.js";
import { FileSequence } from "../src/file-sequence.js";

function parseWithClipId(clipId: Record<string, unknown>): FDL {
  return FDL.parse(
    JSON.stringify({
      uuid: "4ff5d6b1-aaf2-48fd-a947-2d61e45d676a",
      version: { major: 2, minor: 0 },
      fdl_creator: "ASC FDL Tools",
      framing_intents: [],
      contexts: [{ label: "test_clipid", clip_id: clipId, canvases: [] }],
      canvas_templates: [],
    }),
  );
}

describe("ClipID", () => {
  it("deserializing clip id", () => {
    const doc = parseWithClipId({
      clip_name: "ABX_001_110_911",
      file: "ABX_001_110_911.mov",
    });
    try {
      const clip = doc.contexts.at(0)!.clipId;
      expect(clip).toBeInstanceOf(ClipID);
      expect(clip!.clipName).toBe("ABX_001_110_911");
      expect(clip!.file).toBe("ABX_001_110_911.mov");
      expect(clip!.sequence).toBeNull();
    } finally {
      doc.close();
    }
  });

  it("deserializing file sequence", () => {
    const doc = parseWithClipId({
      clip_name: "ABX_001_110_911",
      sequence: {
        value: "ABX_001_110_911.####.exr",
        idx: "#",
        min: 0,
        max: 100,
      },
    });
    try {
      const seq = doc.contexts.at(0)!.clipId!.sequence;
      expect(seq).toBeInstanceOf(FileSequence);
      expect(seq!.value).toBe("ABX_001_110_911.####.exr");
      expect(seq!.idx).toBe("#");
      expect(seq!.min).toBe(0);
      expect(seq!.max).toBe(100);
    } finally {
      doc.close();
    }
  });

  it("clip id properties", () => {
    const doc = parseWithClipId({
      clip_name: "A002_C307_0523JT",
      sequence: {
        value: "A002_C307_0523JT.####.exr",
        idx: "#",
        min: 0,
        max: 100,
      },
    });
    try {
      const cid = doc.contexts.at(0)!.clipId!;
      expect(cid.clipName).toBe("A002_C307_0523JT");
      expect(cid.file).toBeNull();
      expect(cid.sequence).not.toBeNull();
      expect(cid.sequence!.value).toBe("A002_C307_0523JT.####.exr");
    } finally {
      doc.close();
    }
  });

  it("clip id asDict", () => {
    const doc = parseWithClipId({ clip_name: "A001", file: "A001C001.ari" });
    try {
      const d = doc.contexts.at(0)!.clipId!.asDict();
      expect(d.clip_name).toBe("A001");
      expect(d.file).toBe("A001C001.ari");
      expect(d).not.toHaveProperty("sequence");
    } finally {
      doc.close();
    }
  });

  it("set clip id via object", () => {
    const doc = FDL.parse(
      JSON.stringify({
        uuid: "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        version: { major: 2, minor: 0 },
        fdl_creator: "test",
        framing_intents: [],
        contexts: [{ label: "Source", canvases: [] }],
        canvas_templates: [],
      }),
    );
    try {
      const ctx = doc.contexts.at(0)!;
      expect(ctx.clipId).toBeNull();
      ctx.clipId = { clip_name: "A001", file: "A001C001.ari" };
      const cid = ctx.clipId;
      expect(cid).not.toBeNull();
      expect(cid!.clipName).toBe("A001");
      expect(cid!.file).toBe("A001C001.ari");
    } finally {
      doc.close();
    }
  });
});
