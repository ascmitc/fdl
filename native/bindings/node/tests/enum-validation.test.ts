// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Every facade function that takes an enum value must reject an unknown one with a
 * TypeError on every backend, and must not change the document when it does.
 *
 * Python raises KeyError from its enum lookup at the point of use; JS has no KeyError, and
 * TypeError is what the N-API addon already raised for these inputs.
 */

import { describe, it, expect } from "vitest";
import { FDL } from "../src/fdl.js";
import { CanvasTemplate } from "../src/canvas-template.js";
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

const bad = <T>(): T => "wrong" as unknown as T;

function newDoc(): FDL {
  return new FDL({});
}

function addTemplate(doc: FDL, over: Record<string, unknown> = {}) {
  const a = {
    fitSource: GeometryPath.FRAMING_DIMENSIONS,
    fitMethod: FitMethod.FIT_ALL,
    h: HAlign.CENTER,
    v: VAlign.CENTER,
    round: new RoundStrategy(),
    ...over,
  };
  return doc.addCanvasTemplate(
    "CT",
    "ct",
    new DimensionsInt(1920, 1080),
    1.0,
    a.fitSource as GeometryPath,
    a.fitMethod as FitMethod,
    a.h as HAlign,
    a.v as VAlign,
    a.round as RoundStrategy,
  );
}

describe("addCanvasTemplate rejects invalid enums without changing the document", () => {
  const cases: [string, Record<string, unknown>, RegExp][] = [
    ["fitSource", { fitSource: bad() }, /GeometryPath/],
    ["fitMethod", { fitMethod: bad() }, /FitMethod/],
    ["horizontal alignment", { h: bad() }, /HAlign/],
    ["vertical alignment", { v: bad() }, /VAlign/],
    [
      "round even",
      { round: new RoundStrategy(bad<RoundingEven>(), RoundingMode.UP) },
      /RoundingEven/,
    ],
    [
      "round mode",
      { round: new RoundStrategy(RoundingEven.EVEN, bad<RoundingMode>()) },
      /RoundingMode/,
    ],
  ];

  it.each(cases)("%s", (_name, over, message) => {
    const doc = newDoc();
    try {
      expect(() => addTemplate(doc, over)).toThrow(TypeError);
      expect(() => addTemplate(doc, over)).toThrow(message);
      expect(doc.canvasTemplates.length).toBe(0);
    } finally {
      doc.close();
    }
  });
});

describe("other enum-taking functions reject invalid enums", () => {
  it("CanvasTemplate constructor", () => {
    expect(
      () =>
        new CanvasTemplate({
          id: "CT",
          targetDimensions: new DimensionsInt(1920, 1080),
          fitSource: bad<GeometryPath>(),
          fitMethod: FitMethod.FIT_ALL,
        }),
    ).toThrow(TypeError);
  });

  it("preserveFromSourceCanvas setter keeps the value", () => {
    const doc = newDoc();
    try {
      const template = addTemplate(doc, {
        fitSource: GeometryPath.CANVAS_DIMENSIONS,
      });
      const before = template.fitSource;
      expect(() => {
        template.fitSource = bad<GeometryPath>();
      }).toThrow(TypeError);
      expect(template.fitSource).toBe(before);
    } finally {
      doc.close();
    }
  });

  it("DimensionsFloat.round", () => {
    expect(() =>
      new DimensionsFloat(19, 79).round(bad<RoundingEven>(), RoundingMode.UP),
    ).toThrow(TypeError);
  });

  it("PointFloat.round", () => {
    expect(() =>
      new PointFloat(1.5, 2.5).round(RoundingEven.EVEN, bad<RoundingMode>()),
    ).toThrow(TypeError);
  });
});
