// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Mutation parity tests: builders, setters and template apply.
 *
 * Mirrors: native/bindings/python/tests/test_facade_mutation.py
 * (add_multiple_framing_intents, set_protection, canvas template and apply tests,
 * as_dict_roundtrip) and test_canvas.py (source_canvas_id, add_framing_decision,
 * set_effective).
 */

import { describe, it, expect } from "vitest";
import { FDL } from "../src/fdl.js";
import { Canvas } from "../src/canvas.js";
import { FDLValidationError } from "../src/errors.js";
import { DimensionsFloat, DimensionsInt, PointFloat } from "../src/types.js";
import { RoundStrategy } from "../src/rounding.js";
import {
  FitMethod,
  GeometryPath,
  HAlign,
  RoundingEven,
  RoundingMode,
  VAlign,
} from "../src/constants.js";

const UUID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee";

describe("framing intents", () => {
  it("add multiple framing intents", () => {
    const doc = FDL.create(UUID);
    try {
      doc.addFramingIntent("FI_01", "Default", new DimensionsInt(16, 9), 0.0);
      doc.addFramingIntent("FI_02", "Alt", new DimensionsInt(4, 3), 0.05);
      expect(doc.framingIntents.length).toBe(2);
      expect(doc.framingIntents.at(1)!.id).toBe("FI_02");
      expect(doc.framingIntents.at(1)!.protection).toBeCloseTo(0.05);
    } finally {
      doc.close();
    }
  });
});

describe("framing decision protection", () => {
  it("setProtection", () => {
    const doc = FDL.create(UUID);
    try {
      doc.addFramingIntent("FI_01", "Default", new DimensionsInt(16, 9), 0.05);
      const ctx = doc.addContext("Source");
      const canvas = ctx.addCanvas(
        "CV_01",
        "Source",
        "CV_01",
        new DimensionsInt(3840, 2160),
        1.0,
      );
      const fd = canvas.addFramingDecision(
        "CV_01-FI_01",
        "Default FD",
        "FI_01",
        new DimensionsFloat(3840, 2160),
        new PointFloat(0, 0),
      );
      expect(fd.protectionDimensions).toBeNull();

      fd.setProtection(
        new DimensionsFloat(4032, 2268),
        new PointFloat(-96, -54),
      );
      expect(fd.protectionDimensions!.width).toBeCloseTo(4032);
      expect(fd.protectionDimensions!.height).toBeCloseTo(2268);
      expect(fd.protectionAnchorPoint!.x).toBeCloseTo(-96);
      expect(fd.protectionAnchorPoint!.y).toBeCloseTo(-54);
    } finally {
      doc.close();
    }
  });
});

// -----------------------------------------------------------------------
// Canvas template
// -----------------------------------------------------------------------

function addHdTemplate(
  doc: FDL,
  opts: {
    label?: string;
    squeeze?: number;
    source?: GeometryPath;
    mode?: RoundingMode;
  } = {},
) {
  return doc.addCanvasTemplate(
    "CT_01",
    opts.label ?? "HD Delivery",
    new DimensionsInt(1920, 1080),
    opts.squeeze ?? 1.0,
    opts.source ?? GeometryPath.CANVAS_DIMENSIONS,
    FitMethod.WIDTH,
    HAlign.CENTER,
    VAlign.CENTER,
    new RoundStrategy(RoundingEven.EVEN, opts.mode ?? RoundingMode.ROUND),
  );
}

describe("canvas template", () => {
  it("addCanvasTemplate", () => {
    const doc = FDL.create(UUID);
    try {
      const ct = addHdTemplate(doc);
      expect(ct.id).toBe("CT_01");
      expect(ct.label).toBe("HD Delivery");
      expect(ct.targetDimensions.width).toBe(1920);
      expect(ct.targetDimensions.height).toBe(1080);
      expect(ct.targetAnamorphicSqueeze).toBe(1.0);
      expect(ct.fitSource).toBe(GeometryPath.CANVAS_DIMENSIONS);
      expect(ct.fitMethod).toBe(FitMethod.WIDTH);
      expect(ct.alignmentMethodHorizontal).toBe(HAlign.CENTER);
      expect(ct.alignmentMethodVertical).toBe(VAlign.CENTER);
      expect(doc.canvasTemplates.length).toBe(1);
    } finally {
      doc.close();
    }
  });

  it("set optional properties", () => {
    const doc = FDL.create(UUID);
    try {
      const ct = addHdTemplate(doc);
      expect(ct.preserveFromSourceCanvas).toBeNull();
      expect(ct.maximumDimensions).toBeNull();
      expect(ct.padToMaximum).toBe(false);

      ct.preserveFromSourceCanvas = GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS;
      ct.maximumDimensions = new DimensionsInt(4096, 2160);
      ct.padToMaximum = true;

      expect(ct.preserveFromSourceCanvas).toBe(
        GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
      );
      expect(ct.maximumDimensions!.width).toBe(4096);
      expect(ct.maximumDimensions!.height).toBe(2160);
      expect(ct.padToMaximum).toBe(true);
    } finally {
      doc.close();
    }
  });
});

describe("apply canvas template", () => {
  it("apply", () => {
    const doc = FDL.create(UUID, 2, 0, "test", "FI_01");
    try {
      doc.addFramingIntent("FI_01", "Default", new DimensionsInt(16, 9), 0.0);
      const ctx = doc.addContext("Source", "test");
      const canvas = ctx.addCanvas(
        "CV_01",
        "Source Canvas",
        "CV_01",
        new DimensionsInt(3840, 2160),
        1.0,
      );
      const fd = canvas.addFramingDecision(
        "CV_01-FI_01",
        "Default FD",
        "FI_01",
        new DimensionsFloat(3840, 2160),
        new PointFloat(0, 0),
      );
      const ct = addHdTemplate(doc);
      const result = ct.apply(canvas, fd, "CV_02", "HD FD", "Source", "test");
      try {
        expect(result.canvas!.getCustomAttr("scale_factor")).toBeCloseTo(0.5);
        expect(result.fdl).not.toBeNull();
      } finally {
        result.fdl.close();
      }
    } finally {
      doc.close();
    }
  });

  it("squeeze zero inherits source squeeze", () => {
    const doc = FDL.create(UUID, 2, 0, "test", "FI_01");
    try {
      doc.addFramingIntent("FI_01", "Default", new DimensionsInt(16, 9), 0.0);
      const ctx = doc.addContext("Source", "test");
      const canvas = ctx.addCanvas(
        "CV_01",
        "Anamorphic",
        "CV_01",
        new DimensionsInt(4096, 3432),
        2.0,
      );
      const fd = canvas.addFramingDecision(
        "CV_01-FI_01",
        "Default FD",
        "FI_01",
        new DimensionsFloat(4096, 1714),
        new PointFloat(0, 859),
      );
      const ct = addHdTemplate(doc, {
        label: "Squeeze Zero",
        squeeze: 0.0,
        source: GeometryPath.FRAMING_DIMENSIONS,
        mode: RoundingMode.UP,
      });
      const result = ct.apply(
        canvas,
        fd,
        "CV_02",
        "Inherited Squeeze",
        "Source",
        "test",
      );
      try {
        expect(result.canvas!.anamorphicSqueeze).toBeCloseTo(2.0);
        expect(result.fdl).not.toBeNull();
      } finally {
        result.fdl.close();
      }
    } finally {
      doc.close();
    }
  });
});

describe("asDict after mutation", () => {
  it("roundtrip", () => {
    const doc = FDL.create(UUID, 2, 0, "test", "FI_01");
    try {
      doc.addFramingIntent("FI_01", "Default", new DimensionsInt(16, 9), 0.0);
      const ctx = doc.addContext("Source", "test");
      const canvas = ctx.addCanvas(
        "CV_01",
        "Source Canvas",
        "CV_01",
        new DimensionsInt(3840, 2160),
        1.0,
      );
      canvas.addFramingDecision(
        "CV_01-FI_01",
        "Default FD",
        "FI_01",
        new DimensionsFloat(3840, 2160),
        new PointFloat(0, 0),
      );

      const data = doc.asDict() as any;
      expect(data.uuid).toBe(UUID);
      expect(data.fdl_creator).toBe("test");
      expect(data.default_framing_intent).toBe("FI_01");
      expect(data.framing_intents).toHaveLength(1);
      expect(data.contexts).toHaveLength(1);
      expect(data.contexts[0].canvases).toHaveLength(1);
      expect(data.contexts[0].canvases[0].framing_decisions).toHaveLength(1);

      const reparsed = JSON.parse(doc.asJson(2));
      expect(reparsed.uuid).toBe(data.uuid);
      expect(reparsed.framing_intents[0].id).toBe("FI_01");
    } finally {
      doc.close();
    }
  });
});

// -----------------------------------------------------------------------
// test_canvas.py
// -----------------------------------------------------------------------

function buildDoc(uuid: string, canvasId: string, sourceId: string) {
  const doc = FDL.create(uuid);
  const fi = doc.addFramingIntent(
    "FI1",
    "1.78-1",
    new DimensionsInt(16, 9),
    0.0,
  );
  const ctx = doc.addContext("context1");
  const canvas = ctx.addCanvas(
    canvasId,
    "Open Gate RAW",
    sourceId,
    new DimensionsInt(5184, 4320),
    1.3,
  );
  canvas.addFramingDecision(
    `${canvasId}-FI1`,
    "1.78-1",
    fi.id,
    new DimensionsFloat(5184, 4320),
    new PointFloat(0, 0),
  );
  return doc;
}

describe("canvas source_canvas_id", () => {
  it("valid", () => {
    const doc = buildDoc(
      "00000000-0000-0000-0000-000000000001",
      "20220310",
      "20220310",
    );
    try {
      expect(() => doc.validate()).not.toThrow();
    } finally {
      doc.close();
    }
  });

  it("invalid", () => {
    const doc = buildDoc("00000000-0000-0000-0000-000000000002", "456", "123");
    try {
      expect(() => doc.validate()).toThrow(FDLValidationError);
      expect(() => doc.validate()).toThrow(/123/);
    } finally {
      doc.close();
    }
  });
});

function sampleCanvas(): Canvas {
  return new Canvas({
    label: "Open Gate RAW",
    id: "20220310",
    sourceCanvasId: "20220310",
    dimensions: new DimensionsInt(5184, 4320),
    effectiveDimensions: new DimensionsInt(5184, 4320),
    effectiveAnchorPoint: new PointFloat(0, 0),
    photositeDimensions: new DimensionsInt(5184, 4320),
    physicalDimensions: new DimensionsFloat(25.92, 21.6),
    anamorphicSqueeze: 1.3,
  });
}

describe("canvas mutation", () => {
  it("addFramingDecision", () => {
    const canvas = sampleCanvas();
    try {
      const fd = canvas.addFramingDecision(
        "20220310-FDLSMP03",
        "1.78-1 Framing",
        "FDLSMP03",
        new DimensionsFloat(4728, 3456),
        new PointFloat(228, 432),
      );
      expect(fd.id).toBe("20220310-FDLSMP03");
      expect(fd.label).toBe("1.78-1 Framing");
      expect(fd.framingIntentId).toBe("FDLSMP03");
      expect(fd.dimensions.equals(new DimensionsFloat(4728, 3456))).toBe(true);
      expect(fd.anchorPoint.equals(new PointFloat(228, 432))).toBe(true);

      const found = canvas.framingDecisions.findById("20220310-FDLSMP03");
      expect(found).not.toBeNull();
      expect(found!.id).toBe(fd.id);
    } finally {
      canvas.close();
    }
  });

  it("setEffective", () => {
    const canvas = sampleCanvas();
    try {
      expect(
        canvas.effectiveDimensions!.equals(new DimensionsInt(5184, 4320)),
      ).toBe(true);
      expect(canvas.effectiveAnchorPoint!.equals(new PointFloat(0, 0))).toBe(
        true,
      );

      canvas.setEffective(
        new DimensionsInt(3840, 2160),
        new PointFloat(10, 20),
      );
      expect(
        canvas.effectiveDimensions!.equals(new DimensionsInt(3840, 2160)),
      ).toBe(true);
      expect(canvas.effectiveAnchorPoint!.equals(new PointFloat(10, 20))).toBe(
        true,
      );

      canvas.setEffective(new DimensionsInt(3840, 2160), new PointFloat(0, 0));
      expect(canvas.effectiveAnchorPoint!.equals(new PointFloat(0, 0))).toBe(
        true,
      );
    } finally {
      canvas.close();
    }
  });
});
