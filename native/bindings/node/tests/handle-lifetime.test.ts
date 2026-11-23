// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Handle-lifetime tests.
 *
 * Objects constructed standalone (new CanvasTemplate(...), new Canvas(...), ...)
 * live inside a hidden backing document. That document is owned by the object, so
 * closing the object must release it. Objects obtained from a parsed document only
 * borrow their handle, and using anything whose document has been closed must
 * throw rather than touch freed memory.
 *
 * Assertions use `isClosed`, never GC timing.
 */

import { describe, it, expect } from "vitest";
import { FDL } from "../src/fdl.js";
import { Context } from "../src/context.js";
import { Canvas } from "../src/canvas.js";
import { FramingDecision } from "../src/framing-decision.js";
import { FramingIntent } from "../src/framing-intent.js";
import { CanvasTemplate } from "../src/canvas-template.js";
import { DimensionsInt, DimensionsFloat, PointFloat } from "../src/types.js";
import { GeometryPath, FitMethod } from "../src/constants.js";

interface Closable {
  close(): void;
  readonly isClosed: boolean;
}

/** The hidden document a standalone object owns (test-only access to a protected field). */
function backingOf(obj: unknown): Closable {
  return (obj as { _docRef: Closable })._docRef;
}

const standalone: [string, () => Closable & { id?: string }][] = [
  [
    "CanvasTemplate",
    () =>
      new CanvasTemplate({
        id: "CT",
        targetDimensions: new DimensionsInt(1920, 1080),
        fitSource: GeometryPath.FRAMING_DIMENSIONS,
        fitMethod: FitMethod.WIDTH,
      }) as unknown as Closable,
  ],
  [
    "Canvas",
    () =>
      new Canvas({
        id: "CNV",
        sourceCanvasId: "SRC",
        dimensions: new DimensionsInt(1000, 500),
      }) as unknown as Closable,
  ],
  ["Context", () => new Context({ label: "Ctx" }) as unknown as Closable],
  [
    "FramingDecision",
    () =>
      new FramingDecision({
        id: "FD",
        framingIntentId: "FI",
        dimensions: new DimensionsFloat(100, 50),
        anchorPoint: new PointFloat(0, 0),
      }) as unknown as Closable,
  ],
  [
    "FramingIntent",
    () =>
      new FramingIntent({
        id: "FI",
        aspectRatio: new DimensionsInt(16, 9),
        protection: 0,
      }) as unknown as Closable,
  ],
];

describe.each(standalone)("standalone %s", (_name, make) => {
  it("owns its backing document and close() releases it", () => {
    const obj = make();
    const backing = backingOf(obj);
    expect(backing.isClosed).toBe(false);
    expect(obj.isClosed).toBe(false);

    obj.close();

    expect(obj.isClosed).toBe(true);
    expect(backing.isClosed).toBe(true);
  });

  it("close() is idempotent", () => {
    const obj = make();
    obj.close();
    expect(() => obj.close()).not.toThrow();
  });

  it("supports Symbol.dispose", () => {
    const obj = make();
    const backing = backingOf(obj);
    (obj as unknown as { [Symbol.dispose](): void })[Symbol.dispose]();
    expect(backing.isClosed).toBe(true);
  });

  it("throws, instead of crashing, when used after close()", () => {
    const obj = make();
    obj.close();
    const read = obj as unknown as { id?: string; label?: string };
    expect(() => (_name === "Context" ? read.label : read.id)).toThrow(
      /closed/,
    );
  });
});

describe("objects borrowed from a parsed document", () => {
  function parsed(): FDL {
    const fdl = new FDL({});
    const ctx = fdl.addContext("Ctx", "creator");
    ctx.addCanvas("CNV", "Canvas", "SRC", new DimensionsInt(1000, 500), 1.0);
    return fdl;
  }

  it("close() on a child invalidates it but never closes the document", () => {
    const fdl = parsed();
    const ctx = fdl.contexts.at(0)!;

    (ctx as unknown as Closable).close();

    expect((ctx as unknown as Closable).isClosed).toBe(true);
    expect(fdl.isClosed).toBe(false);
    expect(fdl.contexts.length).toBe(1);
    fdl.close();
  });

  it("a child throws, instead of crashing, after its document is closed", () => {
    const fdl = parsed();
    const ctx = fdl.contexts.at(0)!;
    fdl.close();

    expect(() => ctx.label).toThrow(/closed/);
  });

  it("a collection throws, instead of crashing, after its document is closed", () => {
    const fdl = parsed();
    const contexts = fdl.contexts;
    fdl.close();

    expect(() => contexts.length).toThrow(/closed/);
  });
});

describe("template results", () => {
  it("stay valid after the template and the source are closed", () => {
    const source = new FDL({});
    const ctx = source.addContext("Ctx", "creator");
    const canvas = ctx.addCanvas(
      "CNV",
      "Canvas",
      "SRC",
      new DimensionsInt(1000, 500),
      1.0,
    );
    const fd = canvas.addFramingDecision(
      "FD",
      "Framing",
      "FI",
      new DimensionsFloat(1000, 500),
      new PointFloat(0, 0),
    );
    const template = new CanvasTemplate({
      id: "CT",
      targetDimensions: new DimensionsInt(500, 250),
      fitSource: GeometryPath.FRAMING_DIMENSIONS,
      fitMethod: FitMethod.FIT_ALL,
    });

    const result = template.apply(canvas, fd, "OUT", "OUT-FD", "Ctx");
    (template as unknown as Closable).close();
    source.close();

    expect(result.fdl.isClosed).toBe(false);
    expect(() => result.fdl.asJson()).not.toThrow();
    expect(result.canvas.id).toBe("OUT");
    result.fdl.close();
  });
});
