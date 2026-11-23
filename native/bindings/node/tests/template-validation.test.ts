// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Template validation tests.
 *
 * Mirrors: TestFitSourceValidation and TestPreserveFromSourceCanvasValidation
 * (native/bindings/python/fdl/testing/template_tests.py) and
 * native/bindings/python/tests/test_template_width_rounding.py.
 */

import { describe, it, expect } from "vitest";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";

import { FDL } from "../src/fdl.js";
import { CanvasTemplate } from "../src/canvas-template.js";
import { DimensionsInt } from "../src/types.js";
import { RoundStrategy } from "../src/rounding.js";
import {
  GeometryPath,
  FitMethod,
  HAlign,
  VAlign,
  RoundingEven,
  RoundingMode,
} from "../src/constants.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FDL_ROOT = resolve(__dirname, "..", "..", "..", "..", "resources", "FDL");

// Error-test defaults (Python ScenarioConfig error_* defaults)
const ERROR_SOURCE = resolve(
  FDL_ROOT,
  "New_Source_Files/Test_34_Sony_FX3_Priority.fdl",
);
const ERROR_CONTEXT_LABEL = "Sony FX3";
const ERROR_CANVAS_LABEL = "4K";
const FRAMING_INTENT_ID = "1";

function loadErrorSource() {
  const fdl = FDL.parse(readFileSync(ERROR_SOURCE, "utf-8"));
  fdl.validate();
  let context = null;
  for (const c of fdl.contexts)
    if (c.label === ERROR_CONTEXT_LABEL) context = c;
  expect(context, "source context").not.toBeNull();
  let canvas = null;
  for (const c of context!.canvases)
    if (c.label === ERROR_CANVAS_LABEL) canvas = c;
  expect(canvas, "source canvas").not.toBeNull();
  let fd = null;
  for (const f of canvas!.framingDecisions)
    if (f.framingIntentId === FRAMING_INTENT_ID) fd = f;
  expect(fd, "source framing decision").not.toBeNull();
  expect(canvas!.effectiveDimensions).toBeNull();
  return { fdl, context: context!, canvas: canvas!, fd: fd! };
}

describe("TestFitSourceValidation (scenario 21)", () => {
  it("fit_source effective_dimensions missing", () => {
    const { fdl, context, canvas, fd } = loadErrorSource();
    const template = new CanvasTemplate({
      label: "Test Template - Effective Dims",
      id: "test-effective-dims",
      targetDimensions: new DimensionsInt(3840, 2160),
      targetAnamorphicSqueeze: 1.0,
      fitSource: GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
      fitMethod: FitMethod.FIT_ALL,
      alignmentMethodVertical: VAlign.CENTER,
      alignmentMethodHorizontal: HAlign.CENTER,
      round: new RoundStrategy(RoundingEven.EVEN, RoundingMode.ROUND),
    });
    try {
      expect(() =>
        template.apply(canvas, fd, "test", "", context.label, "ASC FDL Tools"),
      ).toThrow(/effective_dimensions/);
    } finally {
      template.close();
      fdl.close();
    }
  });
});

describe("TestPreserveFromSourceCanvasValidation (scenario 22)", () => {
  it("preserve_from_source_canvas effective_dimensions missing", () => {
    const { fdl, context, canvas, fd } = loadErrorSource();
    const template = new CanvasTemplate({
      label: "Test Template - Preserve Effective Dims",
      id: "test-preserve-effective-dims",
      targetDimensions: new DimensionsInt(3840, 2160),
      targetAnamorphicSqueeze: 1.0,
      fitSource: GeometryPath.FRAMING_DIMENSIONS,
      fitMethod: FitMethod.FIT_ALL,
      alignmentMethodVertical: VAlign.CENTER,
      alignmentMethodHorizontal: HAlign.CENTER,
      preserveFromSourceCanvas: GeometryPath.CANVAS_EFFECTIVE_DIMENSIONS,
      round: new RoundStrategy(RoundingEven.EVEN, RoundingMode.ROUND),
    });
    try {
      expect(() =>
        template.apply(canvas, fd, "test", "", context.label, "ASC FDL Tools"),
      ).toThrow(/effective_dimensions/);
    } finally {
      template.close();
      fdl.close();
    }
  });
});

describe("Template width rounding regression (3840 not 3838)", () => {
  function applyFailureExample() {
    const fdl = FDL.parse(
      readFileSync(
        resolve(FDL_ROOT, "Simple_FDL2.0.1_Failure_Example.fdl"),
        "utf-8",
      ),
    );
    let template = null;
    for (const t of fdl.canvasTemplates)
      if (t.label === "Custom Template") template = t;
    expect(template, "template").not.toBeNull();
    let context = null;
    for (const c of fdl.contexts)
      if (c.label === "Custom Template") context = c;
    expect(context, "context").not.toBeNull();
    let canvas = null;
    for (const c of context!.canvases) if (c.id === "1") canvas = c;
    expect(canvas, "canvas").not.toBeNull();
    let fd = null;
    for (const f of canvas!.framingDecisions)
      if (f.framingIntentId === "A") fd = f;
    expect(fd, "framing decision").not.toBeNull();
    const result = template!.apply(
      canvas!,
      fd!,
      "12345678123456781234567812345678".slice(0, 30),
      "",
      context!.label,
      "Test",
    );
    return { fdl, result };
  }

  it("output canvas dimensions", () => {
    const { fdl, result } = applyFailureExample();
    try {
      const dims = result.canvas!.dimensions;
      expect(dims.width).toBe(3840);
      expect(dims.height).toBe(1608);
    } finally {
      result.fdl.close();
      fdl.close();
    }
  });

  it("output framing decision dimensions", () => {
    const { fdl, result } = applyFailureExample();
    try {
      const dims = result.framingDecision!.dimensions;
      expect(dims.width).toBe(3840);
      expect(dims.height).toBe(1608);
    } finally {
      result.fdl.close();
      fdl.close();
    }
  });
});
