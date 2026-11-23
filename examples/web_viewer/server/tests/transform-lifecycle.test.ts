// SPDX-License-Identifier: Apache-2.0
/** applyTransform creates a CanvasTemplate per request and must close it, even on error. */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { after, describe, it, mock } from "node:test";
import { fileURLToPath } from "node:url";

import { CanvasTemplate } from "@asc-mitc/fdl";

import { evictExpiredSessions, parseFdlFromString } from "../src/services/fdl-service.js";
import { applyTransform } from "../src/services/transform-service.js";
import type { TemplateParams } from "../src/types/api.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../..");
const entry = JSON.parse(readFileSync(path.join(here, "scenario_inputs.json"), "utf-8")).find(
  (e: { id: string }) => e.id === "scen1_B",
);
const sourceJson = readFileSync(path.join(repoRoot, entry.sourceFdl), "utf-8");

// Close the native documents held by sessions once the tests are done.
after(() => evictExpiredSessions(Number.POSITIVE_INFINITY));

describe("applyTransform closes the template it creates", () => {
  it("closes exactly one template on success", () => {
    const close = mock.method(CanvasTemplate.prototype, "close");
    try {
      const { sessionId } = parseFdlFromString(sourceJson);
      applyTransform(sessionId, entry.contextIndex, entry.canvasId, entry.framingId, entry.template);
      assert.equal(close.mock.callCount(), 1);
    } finally {
      close.mock.restore();
    }
  });

  it("closes exactly one template when the transform fails", () => {
    const close = mock.method(CanvasTemplate.prototype, "close");
    try {
      // The source canvas has no effective dimensions, so preserving them is an error.
      const params: TemplateParams = {
        ...entry.template,
        preserveFromSourceCanvas: "canvas.effective_dimensions",
      };
      const { sessionId } = parseFdlFromString(sourceJson);
      assert.throws(() =>
        applyTransform(sessionId, entry.contextIndex, entry.canvasId, entry.framingId, params),
      );
      assert.equal(close.mock.callCount(), 1);
    } finally {
      close.mock.restore();
    }
  });
});
