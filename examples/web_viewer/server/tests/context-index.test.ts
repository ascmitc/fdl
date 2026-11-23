// SPDX-License-Identifier: Apache-2.0
/**
 * Context indexes arrive as untrusted query/body values. CollectionWrapper.at() now treats a
 * negative index as "from the end", so the server must only accept non-negative integers.
 */
import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { parseContextIndex } from "../src/services/fdl-service.js";

describe("parseContextIndex", () => {
  it("accepts non-negative integers, as numbers or numeric strings", () => {
    assert.equal(parseContextIndex(0), 0);
    assert.equal(parseContextIndex("0"), 0);
    assert.equal(parseContextIndex("3"), 3);
    assert.equal(parseContextIndex(7), 7);
  });

  it("rejects negative indexes", () => {
    assert.equal(parseContextIndex(-1), null);
    assert.equal(parseContextIndex("-1"), null);
  });

  it("rejects non-integers and non-numbers", () => {
    for (const bad of [1.5, "1.5", "abc", "", undefined, null, NaN, Infinity, {}, []]) {
      assert.equal(parseContextIndex(bad), null, `should reject ${String(bad)}`);
    }
  });
});
