// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * FDL validation tests (C core semantic validators).
 *
 * Mirrors: native/bindings/python/tests/test_validation.py and the validate
 * tests in test_fdl.py.
 */

import { describe, it, expect } from "vitest";
import { FDL } from "../src/fdl.js";
import { FDLValidationError } from "../src/errors.js";
import { DimensionsInt, DimensionsFloat, PointFloat } from "../src/types.js";

type Obj = Record<string, any>;

const HEADER = {
  uuid: "12345678-1234-5678-1234-567812345678",
  version: { major: 2, minor: 0 },
  fdl_creator: "Test",
  default_framing_intent: "1",
};

function build(opts: {
  protectionIntent?: boolean;
  canvasDims: Obj;
  effective?: boolean;
  fd: Obj;
}): Obj {
  const intent: Obj = {
    id: "1",
    label: "Test Intent",
    aspect_ratio: { width: 16, height: 9 },
  };
  if (opts.protectionIntent) intent.protection = 0.1;
  const canvas: Obj = {
    id: "1",
    label: "Test Canvas",
    source_canvas_id: "1",
    dimensions: opts.canvasDims,
    anamorphic_squeeze: 1.0,
    framing_decisions: [
      {
        id: "1-1",
        label: "Test FD",
        framing_intent_id: "1",
        ...opts.fd,
      },
    ],
  };
  if (opts.effective) {
    canvas.effective_dimensions = { width: 3800, height: 2000 };
    canvas.effective_anchor_point = { x: 100, y: 80 };
  }
  return {
    ...HEADER,
    framing_intents: [intent],
    contexts: [
      {
        label: "Test Context",
        context_creator: "Test",
        canvases: [canvas],
      },
    ],
  };
}

// Base FDL with protection dimensions
const baseWithProtection = (): Obj =>
  build({
    protectionIntent: true,
    canvasDims: { width: 4096, height: 2160 },
    fd: {
      dimensions: { width: 3000, height: 1500 },
      anchor_point: { x: 100, y: 100 },
      protection_dimensions: { width: 3500, height: 1800 },
      protection_anchor_point: { x: 50, y: 50 },
    },
  });

// Base FDL with effective + protection + framing anchors
const baseWithEffective = (): Obj =>
  build({
    protectionIntent: true,
    effective: true,
    canvasDims: { width: 4096, height: 2160 },
    fd: {
      dimensions: { width: 3000, height: 1500 },
      anchor_point: { x: 300, y: 200 },
      protection_dimensions: { width: 3500, height: 1800 },
      protection_anchor_point: { x: 200, y: 150 },
    },
  });

// Simple base without protection
const baseSimple = (): Obj =>
  build({
    canvasDims: { width: 4096, height: 2160 },
    fd: {
      dimensions: { width: 3840, height: 2160 },
      anchor_point: { x: 100, y: 50 },
    },
  });

// Small canvas base
const baseSmallCanvas = (): Obj =>
  build({
    canvasDims: { width: 1920, height: 1080 },
    fd: {
      dimensions: { width: 1600, height: 900 },
      anchor_point: { x: 100, y: 50 },
    },
  });

const canvasOf = (d: Obj): Obj => d.contexts[0].canvases[0];
const fdOf = (d: Obj): Obj => canvasOf(d).framing_decisions[0];

function expectValid(data: Obj): void {
  const fdl = FDL.parse(JSON.stringify(data));
  try {
    expect(() => fdl.validate()).not.toThrow();
  } finally {
    fdl.close();
  }
}

function expectInvalid(data: Obj, pattern: RegExp): void {
  const fdl = FDL.parse(JSON.stringify(data));
  try {
    expect(() => fdl.validate()).toThrow(FDLValidationError);
    expect(() => fdl.validate()).toThrow(pattern);
  } finally {
    fdl.close();
  }
}

describe("Dimension hierarchy", () => {
  it("valid FDL passes", () => expectValid(baseWithProtection()));

  it("protection exceeds canvas width", () => {
    const d = baseWithProtection();
    fdOf(d).protection_dimensions.width = 5000;
    expectInvalid(d, /protection.*canvas/i);
  });

  it("protection exceeds canvas height", () => {
    const d = baseWithProtection();
    fdOf(d).protection_dimensions.height = 3000;
    expectInvalid(d, /protection/i);
  });

  it("framing exceeds protection width", () => {
    const d = baseWithProtection();
    fdOf(d).dimensions.width = 4000;
    expectInvalid(d, /framing.*protection/i);
  });

  it("framing exceeds protection height", () => {
    const d = baseWithProtection();
    fdOf(d).dimensions.height = 2000;
    expectInvalid(d, /framing/i);
  });

  it("framing exceeds canvas without protection", () => {
    const d = baseWithProtection();
    delete fdOf(d).protection_dimensions;
    delete fdOf(d).protection_anchor_point;
    fdOf(d).dimensions.width = 5000;
    expectInvalid(d, /framing.*canvas/i);
  });

  it("effective exceeds canvas", () => {
    const d = baseWithProtection();
    canvasOf(d).effective_dimensions = { width: 5000, height: 2160 };
    canvasOf(d).effective_anchor_point = { x: 0, y: 0 };
    expectInvalid(d, /effective.*canvas/i);
  });

  it("protection exceeds effective", () => {
    const d = baseWithProtection();
    canvasOf(d).effective_dimensions = { width: 3000, height: 1600 };
    canvasOf(d).effective_anchor_point = { x: 10, y: 10 };
    expectInvalid(d, /protection.*effective/i);
  });

  it("optional fields skipped when missing", () => {
    const d = baseWithProtection();
    delete fdOf(d).protection_dimensions;
    delete fdOf(d).protection_anchor_point;
    expectValid(d);
  });
});

describe("Anchor hierarchy", () => {
  it("valid anchor hierarchy passes", () => expectValid(baseWithEffective()));

  it("protection anchor outside effective x", () => {
    const d = baseWithEffective();
    fdOf(d).protection_anchor_point.x = 50;
    expectInvalid(d, /is outside/i);
  });

  it("protection anchor outside effective y", () => {
    const d = baseWithEffective();
    fdOf(d).protection_anchor_point.y = 50;
    expectInvalid(d, /is outside/i);
  });

  it("framing anchor outside protection x", () => {
    const d = baseWithEffective();
    fdOf(d).anchor_point.x = 100;
    expectInvalid(d, /is outside/i);
  });

  it("framing anchor outside protection y", () => {
    const d = baseWithEffective();
    fdOf(d).anchor_point.y = 100;
    expectInvalid(d, /is outside/i);
  });

  it("framing anchor outside effective without protection", () => {
    const d = baseWithEffective();
    delete fdOf(d).protection_dimensions;
    delete fdOf(d).protection_anchor_point;
    fdOf(d).anchor_point = { x: 50, y: 50 };
    expectInvalid(d, /is outside/i);
  });

  it("equal anchors valid", () => {
    const d = baseWithEffective();
    canvasOf(d).effective_anchor_point = { x: 100, y: 100 };
    fdOf(d).protection_anchor_point = { x: 100, y: 100 };
    fdOf(d).anchor_point = { x: 100, y: 100 };
    expectValid(d);
  });
});

describe("Non-negative anchors", () => {
  it("valid anchors pass", () => expectValid(baseSimple()));

  it("negative framing anchor x", () => {
    const d = baseSimple();
    fdOf(d).anchor_point.x = -10;
    expectInvalid(d, /minimum.*0/i);
  });

  it("negative framing anchor y", () => {
    const d = baseSimple();
    fdOf(d).anchor_point.y = -5;
    expectInvalid(d, /minimum.*0/i);
  });

  it("negative protection anchor x", () => {
    const d = baseSimple();
    fdOf(d).protection_dimensions = { width: 3900, height: 2100 };
    fdOf(d).protection_anchor_point = { x: -20, y: 30 };
    expectInvalid(d, /minimum.*0/i);
  });

  it("negative protection anchor y", () => {
    const d = baseSimple();
    fdOf(d).protection_dimensions = { width: 3900, height: 2100 };
    fdOf(d).protection_anchor_point = { x: 20, y: -30 };
    expectInvalid(d, /minimum.*0/i);
  });

  it("negative effective anchor x", () => {
    const d = baseSimple();
    canvasOf(d).effective_dimensions = { width: 4000, height: 2100 };
    canvasOf(d).effective_anchor_point = { x: -10, y: 30 };
    expectInvalid(d, /minimum.*0/i);
  });

  it("negative effective anchor y", () => {
    const d = baseSimple();
    canvasOf(d).effective_dimensions = { width: 4000, height: 2100 };
    canvasOf(d).effective_anchor_point = { x: 10, y: -30 };
    expectInvalid(d, /minimum.*0/i);
  });

  it("zero anchors valid", () => {
    const d = baseSimple();
    fdOf(d).anchor_point = { x: 0, y: 0 };
    expectValid(d);
  });
});

describe("Anchors within canvas", () => {
  it("valid anchors within canvas pass", () => expectValid(baseSmallCanvas()));

  it("anchors at canvas bounds valid", () => {
    const d = baseSmallCanvas();
    fdOf(d).anchor_point = { x: 1920, y: 1080 };
    expectValid(d);
  });

  it("framing anchor exceeds canvas x", () => {
    const d = baseSmallCanvas();
    fdOf(d).anchor_point.x = 2000;
    expectInvalid(d, /exceeds.*canvas/i);
  });

  it("framing anchor exceeds canvas y", () => {
    const d = baseSmallCanvas();
    fdOf(d).anchor_point.y = 1200;
    expectInvalid(d, /exceeds.*canvas/i);
  });

  it("protection anchor exceeds canvas x", () => {
    const d = baseSmallCanvas();
    fdOf(d).protection_dimensions = { width: 1700, height: 950 };
    fdOf(d).protection_anchor_point = { x: 2000, y: 50 };
    expectInvalid(d, /protection.*exceeds/i);
  });

  it("protection anchor exceeds canvas y", () => {
    const d = baseSmallCanvas();
    fdOf(d).protection_dimensions = { width: 1700, height: 950 };
    fdOf(d).protection_anchor_point = { x: 50, y: 1200 };
    expectInvalid(d, /protection.*exceeds/i);
  });

  it("effective anchor exceeds canvas x", () => {
    const d = baseSmallCanvas();
    canvasOf(d).effective_dimensions = { width: 1800, height: 1000 };
    canvasOf(d).effective_anchor_point = { x: 2000, y: 40 };
    expectInvalid(d, /effective.*exceeds/i);
  });

  it("effective anchor exceeds canvas y", () => {
    const d = baseSmallCanvas();
    canvasOf(d).effective_dimensions = { width: 1800, height: 1000 };
    canvasOf(d).effective_anchor_point = { x: 60, y: 1200 };
    expectInvalid(d, /effective.*exceeds/i);
  });
});

describe("ID tree", () => {
  it("duplicate framing intent id", () => {
    const d = baseSimple();
    d.framing_intents.push({
      id: "1",
      label: "Duplicate Intent",
      aspect_ratio: { width: 16, height: 9 },
    });
    expectInvalid(d, /duplicated/i);
  });

  it("invalid framing decision id format", () => {
    const d = baseSimple();
    fdOf(d).id = "wrong-format";
    expectInvalid(d, /expected/i);
  });

  it("invalid framing intent reference", () => {
    const d = baseSimple();
    fdOf(d).framing_intent_id = "999";
    fdOf(d).id = "1-999";
    expectInvalid(d, /not in framing_intents/i);
  });
});

describe("Builder-API validation (test_fdl.py)", () => {
  it("validate schema rule", () => {
    const fdl = new FDL({});
    try {
      // id too long violates JSON schema maxLength 32
      fdl.addFramingIntent(
        "x".repeat(33),
        "test",
        new DimensionsInt(16, 9),
        0.0,
      );
      expect(() => fdl.validate()).toThrow(FDLValidationError);
    } finally {
      fdl.close();
    }
  });

  it("validate missing source framing intent", () => {
    const fdl = new FDL({});
    try {
      const ctx = fdl.addContext("test");
      const canvas = ctx.addCanvas(
        "20220310",
        "Open Gate RAW",
        "20220310",
        new DimensionsInt(5184, 4320),
        1.0,
      );
      // Intent "FDLSMP03" is NOT in the doc's framing_intents
      canvas.addFramingDecision(
        "fd1",
        "1.78-1 Framing",
        "FDLSMP03",
        new DimensionsFloat(4728.0, 3456.0),
        new PointFloat(228.0, 432.0),
      );
      expect(() => fdl.validate()).toThrow(FDLValidationError);
    } finally {
      fdl.close();
    }
  });

  it("validate missing source canvas id", () => {
    const fdl = new FDL({});
    try {
      const ctx = fdl.addContext("test");
      ctx.addCanvas(
        "20220310",
        "Open Gate RAW",
        "shouldnotbethere",
        new DimensionsInt(5184, 4320),
        1.0,
      );
      expect(() => fdl.validate()).toThrow(FDLValidationError);
    } finally {
      fdl.close();
    }
  });
});
