// SPDX-License-Identifier: Apache-2.0
/**
 * Parity tests for the web viewer server's FDL transform (N-API binding).
 *
 * For every scenario variant in scenario_inputs.json (generated from the Python
 * scenario config, see tests/scenario_inputs.py), apply the template through
 * transform-service exactly as the client request would, and compare the output
 * canvas geometry and custom attributes with the committed Results FDL that the
 * Python implementation is tested against.
 *
 * Run: npm test -w server   (from examples/web_viewer)
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

import {
  ATTR_CONTENT_TRANSLATION,
  ATTR_SCALE_FACTOR,
  ATTR_SCALED_BOUNDING_BOX,
  readFromFile,
} from "@asc-mitc/fdl";
import type { Canvas } from "@asc-mitc/fdl";

import {
  computeGeometry,
  findCanvasAndFraming,
  getSession,
  parseFdlFromString,
} from "../src/services/fdl-service.js";
import { applyTransform } from "../src/services/transform-service.js";
import type { TemplateParams } from "../src/types/api.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../..");

interface ScenarioEntry {
  id: string;
  sourceFdl: string;
  expectedFdl: string;
  contextIndex: number;
  canvasId: string;
  framingId: string;
  template: TemplateParams;
}

const entries: ScenarioEntry[] = JSON.parse(
  readFileSync(path.join(here, "scenario_inputs.json"), "utf-8"),
);

// Same tolerances as the core FDL comparisons (FP_REL_TOL / FP_ABS_TOL).
const REL_TOL = 1e-9;
const ABS_TOL = 1e-6;

function close(a: number, b: number): boolean {
  return Math.abs(a - b) <= Math.max(REL_TOL * Math.max(Math.abs(a), Math.abs(b)), ABS_TOL);
}

function assertClose(actual: unknown, expected: unknown, label: string): void {
  if (typeof expected === "number" && typeof actual === "number") {
    assert.ok(close(actual, expected), `${label}: expected ${expected}, got ${actual}`);
  } else if (expected !== null && typeof expected === "object") {
    assert.ok(actual !== null && typeof actual === "object", `${label}: expected an object, got ${actual}`);
    for (const key of Object.keys(expected as object)) {
      assertClose((actual as never)[key], (expected as never)[key], `${label}.${key}`);
    }
  } else {
    assert.deepEqual(actual, expected, label);
  }
}

/** The output canvas of a Results FDL is the one carrying the scale-factor attribute. */
function findOutputCanvas(fdl: ReturnType<typeof readFromFile>): Canvas {
  for (const ctx of fdl.contexts) {
    for (const canvas of ctx.canvases) {
      if (canvas.getCustomAttr(ATTR_SCALE_FACTOR) !== null) return canvas;
    }
  }
  throw new Error("expected FDL has no output canvas");
}

describe("web viewer transform matches the committed Results FDLs", () => {
  for (const entry of entries) {
    it(entry.id, () => {
      const source = parseFdlFromString(readFileSync(path.join(repoRoot, entry.sourceFdl), "utf-8"));
      const result = applyTransform(
        source.sessionId,
        entry.contextIndex,
        entry.canvasId,
        entry.framingId,
        entry.template,
      );

      const actualSession = getSession(result.outputSessionId);
      assert.ok(actualSession, "output session should exist");
      const actual = findCanvasAndFraming(
        actualSession.fdl,
        result.outputContextIndex,
        result.outputCanvasId,
        result.outputFramingId,
      );
      assert.ok(actual, "output canvas and framing should be found");

      const expectedFdl = readFromFile(path.join(repoRoot, entry.expectedFdl), true);
      const expectedCanvas = findOutputCanvas(expectedFdl);
      const expectedFraming = expectedCanvas.framingDecisions.at(0);
      assert.ok(expectedFraming, "expected canvas should have a framing decision");

      assertClose(
        computeGeometry(actual.canvas, actual.framing),
        computeGeometry(expectedCanvas, expectedFraming),
        "geometry",
      );
      for (const attr of [ATTR_SCALE_FACTOR, ATTR_CONTENT_TRANSLATION, ATTR_SCALED_BOUNDING_BOX]) {
        assertClose(actual.canvas.getCustomAttr(attr), expectedCanvas.getCustomAttr(attr), attr);
      }
    });
  }
});

describe("contexts without labels", () => {
  it("are addressed by index, including a second unlabeled context", () => {
    const entry = entries.find((e) => e.id === "scen1_B");
    assert.ok(entry);
    const fdl = JSON.parse(readFileSync(path.join(repoRoot, entry.sourceFdl), "utf-8"));
    const second = JSON.parse(JSON.stringify(fdl.contexts[0]));
    second.canvases[0].id = "SECOND";
    second.canvases[0].framing_decisions[0].id = "SECOND-1";
    for (const context of [...fdl.contexts, second]) delete context.label;
    fdl.contexts.push(second);

    const source = parseFdlFromString(JSON.stringify(fdl));
    const result = applyTransform(source.sessionId, 1, "SECOND", "SECOND-1", entry.template);
    assert.equal(result.outputCanvasId, "SECOND_output");
  });
});
