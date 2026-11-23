// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * FramingDecision parity tests: the full parameter grids of
 * native/bindings/python/tests/test_framing_decision.py
 *   - test_from_framing_intent (6 cases)
 *   - test_adjust_anchor_point (18 cases)
 *   - test_adjust_protection_anchor_point (9 cases)
 */

import { describe, it, expect } from "vitest";
import { Canvas } from "../src/canvas.js";
import { FramingDecision } from "../src/framing-decision.js";
import { FramingIntent } from "../src/framing-intent.js";
import { RoundStrategy } from "../src/rounding.js";
import { DimensionsInt, DimensionsFloat, PointFloat } from "../src/types.js";
import {
  HAlign,
  VAlign,
  RoundingEven,
  RoundingMode,
} from "../src/constants.js";

type D = { width: number; height: number };
type P = { x: number; y: number };

const dimsF = (d: D) => new DimensionsFloat(d.width, d.height);
const dimsI = (d: D) => new DimensionsInt(d.width, d.height);

interface IntentCase {
  name: string;
  intentRatio: D;
  canvasDim: D;
  canvasEff: D | null;
  canvasSqz: number;
  protection: number;
  expectedDim: D;
  expectedProt: D | null;
}

const intentCases: IntentCase[] = [
  {
    name: "one to one",
    intentRatio: { width: 16, height: 9 },
    canvasDim: { width: 1920, height: 1080 },
    canvasEff: null,
    canvasSqz: 1,
    protection: 0,
    expectedDim: { width: 1920, height: 1080 },
    expectedProt: null,
  },
  {
    name: "one to one squeeze 2",
    intentRatio: { width: 16, height: 9 },
    canvasDim: { width: 960, height: 1080 },
    canvasEff: null,
    canvasSqz: 2,
    protection: 0,
    expectedDim: { width: 960, height: 1080 },
    expectedProt: null,
  },
  {
    name: "10% protection",
    intentRatio: { width: 16, height: 9 },
    canvasDim: { width: 1920, height: 1080 },
    canvasEff: { width: 1920, height: 1080 },
    canvasSqz: 1,
    protection: 0.1,
    expectedDim: { width: 1920 - 192, height: 1080 - 108 },
    expectedProt: { width: 1920, height: 1080 },
  },
  {
    name: "effective canvas and 10% protection",
    intentRatio: { width: 16, height: 9 },
    canvasDim: { width: 1920, height: 1080 },
    canvasEff: { width: 1920 - 192, height: 1080 - 108 },
    canvasSqz: 1,
    protection: 0.1,
    expectedDim: { width: 1556, height: 874 },
    expectedProt: { width: 1920 - 192, height: 1080 - 108 },
  },
  {
    name: "wide intent",
    intentRatio: { width: 235, height: 100 },
    canvasDim: { width: 1920, height: 1080 },
    canvasEff: { width: 1920, height: 1080 },
    canvasSqz: 1,
    protection: 0,
    expectedDim: { width: 1920, height: 818 },
    expectedProt: null,
  },
  {
    name: "tall intent",
    intentRatio: { width: 4, height: 3 },
    canvasDim: { width: 1920, height: 1080 },
    canvasEff: { width: 1920, height: 1080 },
    canvasSqz: 1,
    protection: 0,
    expectedDim: { width: 1440, height: 1080 },
    expectedProt: null,
  },
];

describe("FramingDecision.fromFramingIntent (parity grid)", () => {
  it.each(intentCases)("$name", (c) => {
    const intent = new FramingIntent({
      label: "1.78-1 Framing",
      id: "FDLSMP03",
      aspectRatio: new DimensionsInt(16, 9),
      protection: 0.088,
    });
    intent.aspectRatio = dimsI(c.intentRatio);
    intent.protection = c.protection;
    const canvas = new Canvas({
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
    canvas.dimensions = dimsI(c.canvasDim);
    canvas.anamorphicSqueeze = c.canvasSqz;
    canvas.effectiveDimensions = c.canvasEff ? dimsI(c.canvasEff) : null;

    // Match the rounding used by the samples.
    const fd = FramingDecision.fromFramingIntent(
      canvas,
      intent,
      new RoundStrategy(RoundingEven.EVEN, RoundingMode.ROUND),
    );
    expect(fd.dimensions.equals(dimsF(c.expectedDim))).toBe(true);
    if (c.expectedProt !== null) {
      expect(fd.protectionDimensions).not.toBeNull();
      expect(fd.protectionDimensions!.equals(dimsF(c.expectedProt))).toBe(true);
    } else {
      expect(fd.protectionDimensions).toBeNull();
    }
    fd.close();
    canvas.close();
    intent.close();
  });
});

const H = { left: HAlign.LEFT, center: HAlign.CENTER, right: HAlign.RIGHT };
const V = { top: VAlign.TOP, center: VAlign.CENTER, bottom: VAlign.BOTTOM };
type HK = keyof typeof H;
type VK = keyof typeof V;

const PD: D = { width: 550, height: 550 };
const anchorCases: [HK, VK, D | null, P | null, P][] = [
  ["left", "top", null, null, { x: 0, y: 0 }],
  ["left", "top", PD, { x: 0, y: 0 }, { x: 0, y: 0 }],
  ["left", "center", null, null, { x: 0, y: 250 }],
  ["left", "center", PD, { x: 0, y: 255 }, { x: 0, y: 250 }],
  ["left", "bottom", null, null, { x: 0, y: 500 }],
  ["left", "bottom", PD, { x: 0, y: 450 }, { x: 0, y: 500 }],
  ["center", "top", null, null, { x: 250, y: 0 }],
  ["center", "top", PD, { x: 225, y: 0 }, { x: 250, y: 0 }],
  ["center", "center", null, null, { x: 250, y: 250 }],
  ["center", "center", PD, { x: 225, y: 225 }, { x: 250, y: 250 }],
  ["center", "bottom", null, null, { x: 250, y: 500 }],
  ["center", "bottom", PD, { x: 225, y: 450 }, { x: 250, y: 500 }],
  ["right", "top", null, null, { x: 500, y: 0 }],
  ["right", "top", PD, { x: 450, y: 0 }, { x: 500, y: 0 }],
  ["right", "center", null, null, { x: 500, y: 250 }],
  ["right", "center", PD, { x: 450, y: 225 }, { x: 500, y: 250 }],
  ["right", "bottom", null, null, { x: 500, y: 500 }],
  ["right", "bottom", PD, { x: 450, y: 450 }, { x: 500, y: 500 }],
];

describe("FramingDecision.adjustAnchorPoint (parity grid)", () => {
  it.each(anchorCases)(
    "%s/%s protection=%j",
    (h, v, protDim, protPnt, expected) => {
      const canvas = new Canvas({
        id: "test_canvas",
        sourceCanvasId: "test_canvas",
        dimensions: new DimensionsInt(1000, 1000),
      });
      const fd = new FramingDecision({
        id: "test_decision",
        framingIntentId: "test_intent",
        dimensions: new DimensionsFloat(500, 500),
      });
      if (protDim !== null && protPnt !== null) {
        fd.protectionDimensions = dimsF(protDim);
        fd.protectionAnchorPoint = new PointFloat(protPnt.x, protPnt.y);
      }
      fd.adjustAnchorPoint(canvas, H[h], V[v]);
      expect(
        fd.anchorPoint.equals(new PointFloat(expected.x, expected.y)),
      ).toBe(true);
      fd.close();
      canvas.close();
    },
  );
});

const protAnchorCases: [HK, VK, P][] = [
  ["left", "top", { x: 0, y: 0 }],
  ["left", "center", { x: 0, y: 225 }],
  ["left", "bottom", { x: 0, y: 450 }],
  ["center", "top", { x: 225, y: 0 }],
  ["center", "center", { x: 225, y: 225 }],
  ["center", "bottom", { x: 225, y: 450 }],
  ["right", "top", { x: 450, y: 0 }],
  ["right", "center", { x: 450, y: 225 }],
  ["right", "bottom", { x: 450, y: 450 }],
];

describe("FramingDecision.adjustProtectionAnchorPoint (parity grid)", () => {
  it.each(protAnchorCases)("%s/%s", (h, v, expected) => {
    const canvas = new Canvas({
      id: "test_canvas",
      sourceCanvasId: "test_canvas",
      dimensions: new DimensionsInt(1000, 1000),
    });
    const fd = new FramingDecision({
      id: "test_decision",
      framingIntentId: "test_intent",
      protectionDimensions: new DimensionsFloat(550, 550),
    });
    fd.adjustProtectionAnchorPoint(canvas, H[h], V[v]);
    expect(fd.protectionAnchorPoint).not.toBeNull();
    expect(
      fd.protectionAnchorPoint!.equals(new PointFloat(expected.x, expected.y)),
    ).toBe(true);
    fd.close();
    canvas.close();
  });
});
