// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Value type parity tests.
 *
 * Mirrors: native/bindings/python/tests/test_common.py
 *   test_dimensions_init, test_dimensions_scale, test_dimensions_duplicate,
 *   test_dimensions_eq / _gt / _lt, test_point_init
 */

import { describe, it, expect } from "vitest";
import { RoundingEven, RoundingMode } from "../src/constants.js";
import { DimensionsInt, DimensionsFloat, PointFloat } from "../src/types.js";

type Dim = [number, number];

describe("dimensions init", () => {
  it("DimensionsInt keeps width/height", () => {
    const d = new DimensionsInt(1000, 1000);
    expect([d.width, d.height]).toEqual([1000, 1000]);
  });

  it("DimensionsFloat keeps width/height", () => {
    const d = new DimensionsFloat(1000.0, 1000.0);
    expect([d.width, d.height]).toEqual([1000.0, 1000.0]);
  });
});

describe("dimensions scale", () => {
  it("scale returns a DimensionsFloat", () => {
    const result = new DimensionsFloat(1.0, 2.0).scale(2.0, 1.0);
    expect(result).toBeInstanceOf(DimensionsFloat);
    expect(result.width).toBe(2.0);
    expect(result.height).toBe(4.0);
  });

  it("scaleBy is an in-place multiply", () => {
    const d = new DimensionsFloat(1.1, 2.2);
    d.scaleBy(2);
    expect(d.width).toBeCloseTo(2.2);
    expect(d.height).toBeCloseTo(4.4);
  });

  it("scale then round with explicit strategy", () => {
    const scaled = new DimensionsFloat(1.0, 2.0).scale(2.1, 1.0);
    const rounded = scaled.round(RoundingEven.WHOLE, RoundingMode.UP);
    expect([Math.trunc(rounded.width), Math.trunc(rounded.height)]).toEqual([
      3, 5,
    ]);
  });
});

describe("dimensions duplicate", () => {
  it("duplicate is equal but a distinct object", () => {
    const a = new DimensionsFloat(1.1, 2.2);
    const b = a.duplicate();
    expect(a.equals(b)).toBe(true);
    expect(b).toBeInstanceOf(DimensionsFloat);
    expect(b).not.toBe(a);
  });
});

describe("dimensions comparison (DimensionsInt 1920x1080 vs other)", () => {
  const eq: [Dim, boolean][] = [
    [[1921, 1080], false],
    [[1920, 1081], false],
    [[1920, 1080], true],
  ];
  it.each(eq)("eq %j -> %s", (other, expected) => {
    expect(
      new DimensionsInt(1920, 1080).equals(new DimensionsInt(...other)),
    ).toBe(expected);
  });

  const gt: [Dim, boolean][] = [
    [[1921, 1080], false],
    [[1920, 1081], false],
    [[1921, 1081], false],
    [[1919, 1080], true],
    [[1920, 1079], true],
    [[1920, 1080], false],
  ];
  it.each(gt)("gt %j -> %s", (other, expected) => {
    expect(new DimensionsInt(1920, 1080).gt(new DimensionsInt(...other))).toBe(
      expected,
    );
  });

  const lt: [Dim, boolean][] = [
    [[1921, 1080], true],
    [[1920, 1081], true],
    [[1921, 1081], true],
    [[1919, 1080], false],
    [[1920, 1079], false],
    [[1920, 1080], false],
  ];
  it.each(lt)("lt %j -> %s", (other, expected) => {
    expect(new DimensionsInt(1920, 1080).lt(new DimensionsInt(...other))).toBe(
      expected,
    );
  });
});

describe("point init", () => {
  it("PointFloat keeps x/y as numbers", () => {
    const p = new PointFloat(1000.0, 1000.0);
    expect(typeof p.x).toBe("number");
    expect(typeof p.y).toBe("number");
    expect([p.x, p.y]).toEqual([1000.0, 1000.0]);
  });

  it("default PointFloat is the origin", () => {
    const p = new PointFloat();
    expect(p.x).toBe(0);
    expect(p.y).toBe(0);
  });
});
