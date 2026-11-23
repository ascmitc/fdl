// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Rounding parity tests.
 *
 * Mirrors: native/bindings/python/tests/test_rounding.py
 *   - test_rounding_strategy_validation
 *   - test_rounding_strategy_rounding (8 parametrized cases)
 */

import { describe, it, expect } from "vitest";
import { RoundingEven, RoundingMode } from "../src/constants.js";
import { RoundStrategy } from "../src/rounding.js";
import { DimensionsFloat } from "../src/types.js";

describe("rounding strategy validation", () => {
  it("rejects an invalid even value when used", () => {
    const dim = new DimensionsFloat(19, 79);
    const bad = new RoundStrategy("wrong" as RoundingEven, RoundingMode.UP);
    expect(() => dim.round(bad.even, bad.mode)).toThrow(TypeError);
    expect(() => dim.round(bad.even, bad.mode)).toThrow(/RoundingEven/);
  });

  it("rejects an invalid mode value when used", () => {
    const dim = new DimensionsFloat(19, 79);
    const bad = new RoundStrategy(RoundingEven.EVEN, "wrong" as RoundingMode);
    expect(() => dim.round(bad.even, bad.mode)).toThrow(TypeError);
    expect(() => dim.round(bad.even, bad.mode)).toThrow(/RoundingMode/);
  });
});

describe("rounding strategy rounding", () => {
  const cases: [
    RoundingEven,
    RoundingMode,
    [number, number],
    [number, number],
  ][] = [
    [RoundingEven.EVEN, RoundingMode.UP, [19, 79], [20, 80]],
    [RoundingEven.EVEN, RoundingMode.DOWN, [19, 79], [18, 78]],
    [RoundingEven.EVEN, RoundingMode.ROUND, [19, 79], [20, 80]],
    [RoundingEven.EVEN, RoundingMode.ROUND, [19.456, 79.456], [20, 80]],
    [RoundingEven.WHOLE, RoundingMode.UP, [19.5, 79.5], [20, 80]],
    [RoundingEven.WHOLE, RoundingMode.DOWN, [19.5, 79.5], [19, 79]],
    [RoundingEven.WHOLE, RoundingMode.ROUND, [19.5, 79.5], [20, 80]],
    [RoundingEven.WHOLE, RoundingMode.ROUND, [19.456, 79.456], [19, 79]],
  ];

  it.each(cases)("%s/%s of %j -> %j", (even, mode, input, expected) => {
    const rnd = new RoundStrategy(even, mode);
    const result = new DimensionsFloat(input[0], input[1]).round(
      rnd.even,
      rnd.mode,
    );
    expect([result.width, result.height]).toEqual(expected);
  });
});
