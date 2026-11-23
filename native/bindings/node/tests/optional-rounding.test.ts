// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Optional rounding in canvas templates.
 *
 * Mirrors: native/bindings/python/tests/test_optional_rounding.py
 */

import { describe, it, expect } from "vitest";
import { FDL } from "../src/fdl.js";
import { Canvas } from "../src/canvas.js";
import { FramingDecision } from "../src/framing-decision.js";
import { CanvasTemplate, TemplateResult } from "../src/canvas-template.js";
import { RoundStrategy } from "../src/rounding.js";
import { DimensionsInt, DimensionsFloat, PointFloat } from "../src/types.js";
import {
  FitMethod,
  GeometryPath,
  RoundingEven,
  RoundingMode,
} from "../src/constants.js";

/** Source FDL: ARRI Alexa LF open gate with a 2.39:1 framing decision. */
function buildSourceFdl(): FDL {
  const doc = FDL.create(
    "00000000-0000-0000-0000-000000000099",
    2,
    0,
    "optional-rounding-test",
    "1",
  );
  doc.addFramingIntent(
    "1",
    "2.39:1 Theatrical",
    new DimensionsInt(239, 100),
    0.0,
  );
  const ctx = doc.addContext("Source Camera", "Test");
  const canvas = ctx.addCanvas(
    "C1",
    "4.5K LF Open Gate",
    "C1",
    new DimensionsInt(4448, 3096),
    1.0,
  );
  canvas.addFramingDecision(
    "1",
    "2.39:1 Theatrical",
    "1",
    new DimensionsFloat(4096.0, 1714.6443514644),
    new PointFloat(176.0, 690.6778242678),
  );
  return doc;
}

function applyTemplate(doc: FDL, template: CanvasTemplate): TemplateResult {
  const ctx = doc.contexts.at(0)!;
  const canvas = ctx.canvases.at(0)!;
  const fd = canvas.framingDecisions.at(0)!;
  return template.apply(canvas, fd, "OUT", "1", ctx.label, "Test");
}

function assertCanvasDimensionsInteger(canvas: Canvas): void {
  expect(canvas.dimensions.width).toBe(Math.trunc(canvas.dimensions.width));
  expect(canvas.dimensions.height).toBe(Math.trunc(canvas.dimensions.height));
}

function assertEffectiveDimensionsInteger(canvas: Canvas): void {
  const eff = canvas.effectiveDimensions;
  if (eff !== null) {
    expect(eff.width).toBe(Math.trunc(eff.width));
    expect(eff.height).toBe(Math.trunc(eff.height));
  }
}

/** Inner geometry is not rounded: framing height stays fractional. */
function assertFramingFloat(fd: FramingDecision): void {
  expect(fd.dimensions.height).not.toBe(Math.trunc(fd.dimensions.height));
}

function paddedTemplate(round?: RoundStrategy): CanvasTemplate {
  return new CanvasTemplate({
    id: "E",
    label: "Editorial",
    targetDimensions: new DimensionsInt(1920, 1080),
    fitSource: GeometryPath.FRAMING_DIMENSIONS,
    fitMethod: FitMethod.WIDTH,
    preserveFromSourceCanvas: GeometryPath.CANVAS_DIMENSIONS,
    maximumDimensions: new DimensionsInt(1920, 1080),
    padToMaximum: true,
    ...(round ? { round } : {}),
  });
}

/** Run `fn` with a source doc, template and result, closing everything. */
function withApplied(
  template: CanvasTemplate,
  fn: (r: TemplateResult) => void,
): void {
  const doc = buildSourceFdl();
  try {
    const result = applyTemplate(doc, template);
    try {
      fn(result);
    } finally {
      result.fdl.close();
    }
  } finally {
    template.close();
    doc.close();
  }
}

describe("CanvasTemplate default round", () => {
  it("default round is even/up", () => {
    const ct = new CanvasTemplate({
      id: "T",
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    expect(ct.round.even).toBe(RoundingEven.EVEN);
    expect(ct.round.mode).toBe(RoundingMode.UP);
    ct.close();
  });

  it("explicit round is preserved", () => {
    const ct = new CanvasTemplate({
      id: "T",
      targetDimensions: new DimensionsInt(1920, 1080),
      round: new RoundStrategy(RoundingEven.EVEN, RoundingMode.ROUND),
    });
    expect(ct.round.even).toBe(RoundingEven.EVEN);
    expect(ct.round.mode).toBe(RoundingMode.ROUND);
    ct.close();
  });

  it("default round is emitted in asDict", () => {
    const ct = new CanvasTemplate({
      id: "T",
      targetDimensions: new DimensionsInt(1920, 1080),
    });
    const d = ct.asDict() as { round: { even: string; mode: string } };
    expect(d).toHaveProperty("round");
    expect(d.round.even).toBe("even");
    expect(d.round.mode).toBe("up");
    ct.close();
  });

  it("explicit round in asDict", () => {
    const ct = new CanvasTemplate({
      id: "T",
      targetDimensions: new DimensionsInt(1920, 1080),
      round: new RoundStrategy(RoundingEven.EVEN, RoundingMode.UP),
    });
    const d = ct.asDict() as { round: { even: string; mode: string } };
    expect(d).toHaveProperty("round");
    expect(d.round.even).toBe("even");
    expect(d.round.mode).toBe("up");
    ct.close();
  });
});

describe("apply template without rounding", () => {
  it("framing dimensions are float", () => {
    withApplied(paddedTemplate(), (result) => {
      const fd = result.framingDecision!;
      expect(fd.dimensions.width).toBeCloseTo(1920.0, 1);
      assertFramingFloat(fd);
    });
  });

  it("framing anchor is float", () => {
    withApplied(paddedTemplate(), (result) => {
      const fd = result.framingDecision!;
      expect(fd.anchorPoint.y).not.toBe(Math.trunc(fd.anchorPoint.y));
    });
  });

  it("effective dimensions are integer", () => {
    withApplied(paddedTemplate(), (result) => {
      assertEffectiveDimensionsInteger(result.canvas!);
    });
  });
});

describe("apply template with explicit round (pad to max)", () => {
  const round = () => new RoundStrategy(RoundingEven.EVEN, RoundingMode.ROUND);

  it("framing dimensions are float even with explicit round", () => {
    withApplied(paddedTemplate(round()), (result) => {
      const fd = result.framingDecision!;
      expect(fd.dimensions.width).toBeCloseTo(1920.0, 1);
      assertFramingFloat(fd);
    });
  });

  it("framing anchor is float even with explicit round", () => {
    withApplied(paddedTemplate(round()), (result) => {
      const fd = result.framingDecision!;
      expect(fd.anchorPoint.y).not.toBe(Math.trunc(fd.anchorPoint.y));
    });
  });
});

describe("context-dependent rounding default", () => {
  function plain(
    extra: Partial<ConstructorParameters<typeof CanvasTemplate>[0]>,
  ) {
    return new CanvasTemplate({
      id: "T",
      targetDimensions: new DimensionsInt(1920, 1080),
      fitSource: GeometryPath.FRAMING_DIMENSIONS,
      fitMethod: FitMethod.WIDTH,
      preserveFromSourceCanvas: GeometryPath.CANVAS_DIMENSIONS,
      ...extra,
    });
  }

  it("no pad, no round: canvas integer, framing float", () => {
    withApplied(plain({}), (result) => {
      assertCanvasDimensionsInteger(result.canvas!);
      assertFramingFloat(result.framingDecision!);
    });
  });

  it("pad to max with no round preserves floats", () => {
    withApplied(paddedTemplate(), (result) => {
      const fd = result.framingDecision!;
      expect(fd.dimensions.height).not.toBe(Math.trunc(fd.dimensions.height));
    });
  });

  it("max dims without pad: canvas integer, framing float", () => {
    withApplied(
      plain({
        maximumDimensions: new DimensionsInt(1920, 1080),
        padToMaximum: false,
      }),
      (result) => {
        assertCanvasDimensionsInteger(result.canvas!);
        assertFramingFloat(result.framingDecision!);
      },
    );
  });
});

describe("rounding mode variations", () => {
  const GRID_ALL: [RoundingEven, RoundingMode][] = [
    [RoundingEven.EVEN, RoundingMode.UP],
    [RoundingEven.EVEN, RoundingMode.DOWN],
    [RoundingEven.EVEN, RoundingMode.ROUND],
    [RoundingEven.WHOLE, RoundingMode.UP],
    [RoundingEven.WHOLE, RoundingMode.DOWN],
    [RoundingEven.WHOLE, RoundingMode.ROUND],
  ];
  const GRID_EVEN = GRID_ALL.slice(0, 3);

  function templateWith(even?: RoundingEven, mode?: RoundingMode) {
    return new CanvasTemplate({
      id: "T",
      targetDimensions: new DimensionsInt(1920, 1080),
      fitSource: GeometryPath.FRAMING_DIMENSIONS,
      fitMethod: FitMethod.WIDTH,
      preserveFromSourceCanvas: GeometryPath.CANVAS_DIMENSIONS,
      padToMaximum: false,
      ...(even !== undefined && mode !== undefined
        ? { round: new RoundStrategy(even, mode) }
        : {}),
    });
  }

  /** Apply with (even, mode), hand the result to fn, clean up. */
  function run<T>(
    doc: FDL,
    even: RoundingEven | undefined,
    mode: RoundingMode | undefined,
    fn: (r: TemplateResult) => T,
  ): T {
    const t = templateWith(even, mode);
    const result = applyTemplate(doc, t);
    try {
      return fn(result);
    } finally {
      result.fdl.close();
      t.close();
    }
  }

  const canvasDims = (r: TemplateResult) => r.canvas!.dimensions.clone();
  const framingHeight = (r: TemplateResult) =>
    r.framingDecision!.dimensions.height;

  function withDoc(fn: (doc: FDL) => void) {
    const doc = buildSourceFdl();
    try {
      fn(doc);
    } finally {
      doc.close();
    }
  }

  it("even up vs even down canvas dims", () =>
    withDoc((doc) => {
      const up = run(doc, RoundingEven.EVEN, RoundingMode.UP, canvasDims);
      const down = run(doc, RoundingEven.EVEN, RoundingMode.DOWN, canvasDims);
      expect(up.height).toBeGreaterThanOrEqual(down.height);
    }));

  it("whole up vs whole down canvas dims", () =>
    withDoc((doc) => {
      const up = run(doc, RoundingEven.WHOLE, RoundingMode.UP, canvasDims);
      const down = run(doc, RoundingEven.WHOLE, RoundingMode.DOWN, canvasDims);
      expect(up.height).toBeGreaterThanOrEqual(down.height);
    }));

  it("default even/up matches explicit even/up canvas", () =>
    withDoc((doc) => {
      const [dDims, dH] = run(doc, undefined, undefined, (r) => [
        canvasDims(r),
        framingHeight(r),
      ]) as [DimensionsInt, number];
      const [eDims, eH] = run(doc, RoundingEven.EVEN, RoundingMode.UP, (r) => [
        canvasDims(r),
        framingHeight(r),
      ]) as [DimensionsInt, number];
      expect(dDims.equals(eDims)).toBe(true);
      expect(dH).toBeCloseTo(eH, 6);
    }));

  it("even up vs even round: inner geometry matches", () =>
    withDoc((doc) => {
      const up = run(doc, RoundingEven.EVEN, RoundingMode.UP, (r) => {
        assertCanvasDimensionsInteger(r.canvas!);
        return framingHeight(r);
      });
      const rnd = run(doc, RoundingEven.EVEN, RoundingMode.ROUND, (r) => {
        assertCanvasDimensionsInteger(r.canvas!);
        return framingHeight(r);
      });
      expect(up).toBeCloseTo(rnd, 6);
    }));

  it.each(GRID_ALL)("canvas dimensions integer: %s/%s", (even, mode) =>
    withDoc((doc) =>
      run(doc, even, mode, (r) => assertCanvasDimensionsInteger(r.canvas!)),
    ),
  );

  it.each(GRID_ALL)("effective dimensions integer: %s/%s", (even, mode) =>
    withDoc((doc) =>
      run(doc, even, mode, (r) => assertEffectiveDimensionsInteger(r.canvas!)),
    ),
  );

  it.each(GRID_EVEN)(
    "even rounding gives even canvas dims: %s/%s",
    (even, mode) =>
      withDoc((doc) =>
        run(doc, even, mode, (r) => {
          const cd = r.canvas!.dimensions;
          expect(cd.width % 2).toBe(0);
          expect(cd.height % 2).toBe(0);
        }),
      ),
  );

  it.each(GRID_EVEN)("framing dimensions remain float: %s/%s", (even, mode) =>
    withDoc((doc) =>
      run(doc, even, mode, (r) => assertFramingFloat(r.framingDecision!)),
    ),
  );

  it("distinct rounding modes can change canvas height", () =>
    withDoc((doc) => {
      const heights = new Set(
        [RoundingMode.UP, RoundingMode.DOWN, RoundingMode.ROUND].map((m) =>
          run(doc, RoundingEven.EVEN, m, (r) => r.canvas!.dimensions.height),
        ),
      );
      expect(heights.size).toBeGreaterThan(1);
    }));
});

describe("JSON round-trip", () => {
  function docJson(uuid: string, label: string, round?: object) {
    return JSON.stringify({
      uuid,
      version: { major: 2, minor: 0 },
      fdl_creator: "test",
      default_framing_intent: "1",
      framing_intents: [
        {
          id: "1",
          label: "Test",
          aspect_ratio: { width: 16, height: 9 },
          protection: 0.0,
        },
      ],
      canvas_templates: [
        {
          id: "T",
          label,
          target_dimensions: { width: 1920, height: 1080 },
          target_anamorphic_squeeze: 1.0,
          fit_source: "framing_decision.dimensions",
          fit_method: "width",
          ...(round ? { round } : {}),
        },
      ],
    });
  }

  it("parse template without round yields even/up", () => {
    const doc = FDL.parse(
      docJson("00000000-0000-0000-0000-000000000001", "No-Round Template"),
    );
    expect(doc.canvasTemplates.length).toBe(1);
    const t = doc.canvasTemplates.at(0)!;
    expect(t.round.even).toBe(RoundingEven.EVEN);
    expect(t.round.mode).toBe(RoundingMode.UP);
    doc.close();
  });

  it("parse template with explicit round", () => {
    const doc = FDL.parse(
      docJson("00000000-0000-0000-0000-000000000002", "Rounded Template", {
        even: "even",
        mode: "round",
      }),
    );
    expect(doc.canvasTemplates.length).toBe(1);
    const t = doc.canvasTemplates.at(0)!;
    expect(t.round.even).toBe(RoundingEven.EVEN);
    expect(t.round.mode).toBe(RoundingMode.ROUND);
    doc.close();
  });
});
