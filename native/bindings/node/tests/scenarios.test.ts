// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Parameterized scenario tests — mirrors Python's TestFDLTemplatesParameterized.
 *
 * Loads the same FDL fixture files from resources/FDL/Scenarios_For_Implementers/,
 * applies the same templates with the same parameters, and compares every field
 * of the result against the expected output FDL.
 */

import { describe, it, expect } from 'vitest';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { existsSync, readFileSync } from 'node:fs';

import { FDL } from '../src/fdl.js';
import { FP_REL_TOL, FP_ABS_TOL } from '../src/constants.js';
import type { Context } from '../src/context.js';
import type { Canvas } from '../src/canvas.js';
import type { FramingDecision } from '../src/framing-decision.js';
import type { CanvasTemplate } from '../src/canvas-template.js';
import type { DimensionsFloat, DimensionsInt, PointFloat } from '../src/types.js';

// ---------------------------------------------------------------------------
// Path helpers
// ---------------------------------------------------------------------------

const __dirname = dirname(fileURLToPath(import.meta.url));
// native/bindings/node/tests/ -> repo root -> resources/FDL
const FDL_ROOT = resolve(__dirname, '..', '..', '..', '..', 'resources', 'FDL');
const SCENARIOS_DIR = resolve(FDL_ROOT, 'Scenarios_For_Implementers');

// ---------------------------------------------------------------------------
// Tolerance-aware comparison helpers (matching Python's FDLComparison)
// ---------------------------------------------------------------------------

function isClose(a: number, b: number): boolean {
  // Matches Python's math.isclose(a, b, rel_tol=FP_REL_TOL, abs_tol=FP_ABS_TOL)
  return Math.abs(a - b) <= Math.max(FP_REL_TOL * Math.max(Math.abs(a), Math.abs(b)), FP_ABS_TOL);
}

function expectDimsIntEqual(label: string, expected: DimensionsInt, actual: DimensionsInt): void {
  expect(actual.width, `${label}.width`).toBe(expected.width);
  expect(actual.height, `${label}.height`).toBe(expected.height);
}

function expectDimsFloatClose(label: string, expected: DimensionsFloat, actual: DimensionsFloat): void {
  expect(isClose(expected.width, actual.width), `${label}.width: expected ${expected.width}, got ${actual.width}`).toBe(true);
  expect(isClose(expected.height, actual.height), `${label}.height: expected ${expected.height}, got ${actual.height}`).toBe(true);
}

function expectPointClose(label: string, expected: PointFloat, actual: PointFloat): void {
  expect(isClose(expected.x, actual.x), `${label}.x: expected ${expected.x}, got ${actual.x}`).toBe(true);
  expect(isClose(expected.y, actual.y), `${label}.y: expected ${expected.y}, got ${actual.y}`).toBe(true);
}

function expectOptionalDimsIntEqual(label: string, expected: DimensionsInt | null, actual: DimensionsInt | null): void {
  if (expected === null) {
    expect(actual, `${label} should be null`).toBeNull();
  } else {
    expect(actual, `${label} should not be null`).not.toBeNull();
    expectDimsIntEqual(label, expected, actual!);
  }
}

function expectOptionalDimsFloatClose(label: string, expected: DimensionsFloat | null, actual: DimensionsFloat | null): void {
  if (expected === null) {
    expect(actual, `${label} should be null`).toBeNull();
  } else {
    expect(actual, `${label} should not be null`).not.toBeNull();
    expectDimsFloatClose(label, expected, actual!);
  }
}

function expectOptionalPointClose(label: string, expected: PointFloat | null, actual: PointFloat | null): void {
  if (expected === null) {
    expect(actual, `${label} should be null`).toBeNull();
  } else {
    expect(actual, `${label} should not be null`).not.toBeNull();
    expectPointClose(label, expected, actual!);
  }
}

// ---------------------------------------------------------------------------
// FDL component comparison (mirrors Python's FDLComparison)
// ---------------------------------------------------------------------------

function compareContext(expected: Context, actual: Context): void {
  expect(actual.label, 'context.label').toBe(expected.label);
  expect(actual.contextCreator, 'context.contextCreator').toBe(expected.contextCreator);
}

function compareCanvas(expected: Canvas, actual: Canvas, expectedId?: string): void {
  if (expectedId) {
    expect(actual.id, 'canvas.id').toBe(expectedId);
  }
  expect(actual.sourceCanvasId, 'canvas.sourceCanvasId').toBe(expected.sourceCanvasId);
  expect(actual.label, 'canvas.label').toBe(expected.label);
  expectDimsIntEqual('canvas.dimensions', expected.dimensions, actual.dimensions);
  expectOptionalDimsIntEqual('canvas.effectiveDimensions', expected.effectiveDimensions, actual.effectiveDimensions);
  expectOptionalPointClose('canvas.effectiveAnchorPoint', expected.effectiveAnchorPoint, actual.effectiveAnchorPoint);
  expectOptionalDimsIntEqual('canvas.photositeDimensions', expected.photositeDimensions, actual.photositeDimensions);
  expectOptionalDimsFloatClose('canvas.physicalDimensions', expected.physicalDimensions, actual.physicalDimensions);
  expect(
    isClose(expected.anamorphicSqueeze, actual.anamorphicSqueeze),
    `canvas.anamorphicSqueeze: expected ${expected.anamorphicSqueeze}, got ${actual.anamorphicSqueeze}`,
  ).toBe(true);
  compareCustomAttrs(expected, actual, 'canvas');
}

function compareFramingDecision(expected: FramingDecision, actual: FramingDecision, expectedId?: string): void {
  if (expectedId) {
    expect(actual.id, 'framingDecision.id').toBe(expectedId);
  }
  expect(actual.framingIntentId, 'framingDecision.framingIntentId').toBe(expected.framingIntentId);
  expect(actual.label, 'framingDecision.label').toBe(expected.label);
  expectDimsFloatClose('framingDecision.dimensions', expected.dimensions, actual.dimensions);
  expectPointClose('framingDecision.anchorPoint', expected.anchorPoint, actual.anchorPoint);
  expectOptionalDimsFloatClose('framingDecision.protectionDimensions', expected.protectionDimensions, actual.protectionDimensions);
  expectOptionalPointClose('framingDecision.protectionAnchorPoint', expected.protectionAnchorPoint, actual.protectionAnchorPoint);
  compareCustomAttrs(expected, actual, 'framingDecision');
}

function compareCanvasTemplate(expected: CanvasTemplate, actual: CanvasTemplate): void {
  expect(actual.id, 'template.id').toBe(expected.id);
  expectDimsIntEqual('template.targetDimensions', expected.targetDimensions, actual.targetDimensions);
  expect(
    isClose(expected.targetAnamorphicSqueeze, actual.targetAnamorphicSqueeze),
    `template.targetAnamorphicSqueeze`,
  ).toBe(true);
  expect(actual.fitSource, 'template.fitSource').toBe(expected.fitSource);
  expect(actual.fitMethod, 'template.fitMethod').toBe(expected.fitMethod);
  expect(actual.label, 'template.label').toBe(expected.label);
  expect(actual.alignmentMethodVertical, 'template.alignmentMethodVertical').toBe(expected.alignmentMethodVertical);
  expect(actual.alignmentMethodHorizontal, 'template.alignmentMethodHorizontal').toBe(expected.alignmentMethodHorizontal);
  expect(actual.preserveFromSourceCanvas, 'template.preserveFromSourceCanvas').toBe(expected.preserveFromSourceCanvas);
  expectOptionalDimsIntEqual('template.maximumDimensions', expected.maximumDimensions, actual.maximumDimensions);
  expect(actual.padToMaximum, 'template.padToMaximum').toBe(expected.padToMaximum);
  expect(actual.round.even, 'template.round.even').toBe(expected.round.even);
  expect(actual.round.mode, 'template.round.mode').toBe(expected.round.mode);
  compareCustomAttrs(expected, actual, 'template');
}

function compareCustomAttrs(
  expected: { customAttrs: Record<string, unknown> },
  actual: { customAttrs: Record<string, unknown> },
  prefix: string,
): void {
  const expectedAttrs = expected.customAttrs;
  const actualAttrs = actual.customAttrs;
  const expectedKeys = new Set(Object.keys(expectedAttrs));
  const actualKeys = new Set(Object.keys(actualAttrs));

  for (const key of expectedKeys) {
    expect(actualKeys.has(key), `${prefix}.customAttrs missing key '${key}'`).toBe(true);
  }
  for (const key of actualKeys) {
    expect(expectedKeys.has(key), `${prefix}.customAttrs unexpected key '${key}'`).toBe(true);
  }
  for (const key of expectedKeys) {
    if (!actualKeys.has(key)) continue;
    const ev = expectedAttrs[key];
    const av = actualAttrs[key];
    if (typeof ev === 'number' && typeof av === 'number') {
      expect(isClose(ev, av), `${prefix}.customAttrs['${key}']: expected ${ev}, got ${av}`).toBe(true);
    } else {
      expect(av, `${prefix}.customAttrs['${key}']`).toEqual(ev);
    }
  }
}

// ---------------------------------------------------------------------------
// Component lookup helpers
// ---------------------------------------------------------------------------

function findContext(fdl: FDL, label: string): Context | null {
  for (const c of fdl.contexts) {
    if (c.label === label) return c;
  }
  return null;
}

function findCanvas(ctx: Context, label: string): Canvas | null {
  for (const c of ctx.canvases) {
    if (c.label === label) return c;
  }
  return null;
}

function findFD(canvas: Canvas, framingIntentId: string): FramingDecision | null {
  for (const fd of canvas.framingDecisions) {
    if (fd.framingIntentId === framingIntentId) return fd;
  }
  return null;
}

function findTemplate(fdl: FDL, label: string): CanvasTemplate | null {
  for (const t of fdl.canvasTemplates) {
    if (t.label === label) return t;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Scenario configuration (mirrors Python's scenario_config.py)
// ---------------------------------------------------------------------------

interface SourceVariant {
  letter: string;
  fdlBasename: string;
  contextLabel: string;
  canvasLabel: string;
}

interface ScenarioConfig {
  number: number;
  name: string;
  dirName: string;
  templateFilename: string;
  variants: SourceVariant[];
  resultPattern: string;
  contextLabel?: string;
  canvasLabel?: string;
  customTemplateDir?: string;
  customTemplatePath?: string;
  customSourceDir?: string;
  customResultsDir?: string;
  framingIntentId?: string;
  contextCreator?: string;
  templateLabel?: string;
}

// Deterministic UUID matching Python tests
const DETERMINISTIC_UUID = '12345678123456781234567812345678'.slice(0, 30);

function getScenarioPaths(
  config: ScenarioConfig,
  variant: SourceVariant,
): { template: string; sourceFdl: string; expectedFdl: string } {
  // Template path
  let templateDir: string;
  if (config.customTemplatePath) {
    templateDir = resolve(FDL_ROOT, config.customTemplatePath);
  } else if (config.customTemplateDir) {
    templateDir = resolve(SCENARIOS_DIR, config.customTemplateDir);
  } else {
    templateDir = resolve(SCENARIOS_DIR, config.dirName);
  }

  // Source path
  let sourceDir: string;
  if (config.customSourceDir) {
    sourceDir = resolve(FDL_ROOT, config.customSourceDir);
  } else {
    sourceDir = resolve(SCENARIOS_DIR, config.dirName, 'Source_Files');
  }

  // Results path
  let resultsDir: string;
  if (config.customResultsDir) {
    resultsDir = resolve(FDL_ROOT, config.customResultsDir);
  } else {
    resultsDir = resolve(SCENARIOS_DIR, config.dirName, 'Results');
  }

  const resultFdlName = config.resultPattern.replace('{variant}', variant.fdlBasename);

  return {
    template: resolve(templateDir, config.templateFilename),
    sourceFdl: resolve(sourceDir, `${variant.fdlBasename}.fdl`),
    expectedFdl: resolve(resultsDir, resultFdlName),
  };
}

// ---------------------------------------------------------------------------
// Scenario registry (exact mirror of Python SCENARIO_CONFIGS)
// ---------------------------------------------------------------------------

const SCENARIOS: ScenarioConfig[] = [
  {
    number: 1, name: 'FitDecision-into-UHD',
    dirName: 'Scen_1_FitDecision-into-UHD',
    templateFilename: 'Scen_1_FitDecision-into-UHD-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen1-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'D', fdlBasename: 'D_8640x5760_1x_10PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
    ],
  },
  {
    number: 2, name: 'FitProtection-into-UHD',
    dirName: 'Scen_2_FitProtection-into-UHD',
    templateFilename: 'Scen_2_FitProtection-into-UHD-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen2-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'D', fdlBasename: 'D_8640x5760_1x_10PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
    ],
  },
  {
    number: 3, name: 'Preserving-Protection',
    dirName: 'Scen_3_Preserving-Protection',
    templateFilename: 'Scen_3_Preserving-Protection-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen3-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'D', fdlBasename: 'D_8640x5760_1x_10PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
      { letter: 'E', fdlBasename: 'E_8640x5760_1x_15PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
      { letter: 'F', fdlBasename: 'F_8640x5760_1x_20PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
    ],
  },
  {
    number: 4, name: 'Preserving-Canvas',
    dirName: 'Scen_4_Preserving-Canvas',
    templateFilename: 'Scen_4_Preserving-Canvas-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen4-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'D', fdlBasename: 'D_8640x5760_1x_10PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
      { letter: 'E', fdlBasename: 'E_8640x5760_1x_15PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
      { letter: 'F', fdlBasename: 'F_8640x5760_1x_20PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
    ],
  },
  {
    number: 5, name: 'Normalizing_LensSqueezeTo1',
    dirName: 'Scen_5_Normalizing_LensSqueezeTo1',
    templateFilename: 'Scen_5_Normalizing_LensSqueezeTo1-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen5-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'A', fdlBasename: 'A_4448x3096_1-3x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'C', fdlBasename: 'C_4448x3096_2x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
    ],
  },
  {
    number: 6, name: 'Normalizing_LensSqueezeTo2',
    dirName: 'Scen_6_Normalizing_LensSqueezeTo2',
    templateFilename: 'Scen_6_Normalizing_LensSqueezeTo2-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen6-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'A', fdlBasename: 'A_4448x3096_1-3x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'C', fdlBasename: 'C_4448x3096_2x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
    ],
  },
  {
    number: 7, name: 'TopAlignedSource-PreserveProtection-Centered',
    dirName: 'Scen_7_TopAlignedSource-PreserveProtection-Centered',
    templateFilename: 'Scen_7_TopAlignedSource-PreserveProtection-Centered-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen7-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'G', fdlBasename: 'G_5040x3780_1x_TopAligned-FramingChart', contextLabel: 'RED V-RAPTOR 8K S35', canvasLabel: '7K 4:3 2x' },
    ],
  },
  {
    number: 8, name: 'TopAlignedSource-PreserveCanvas-Centered',
    dirName: 'Scen_8_TopAlignedSource-PreserveCanvas-Centered',
    templateFilename: 'Scen_8_TopAlignedSource-PreserveCanvas-Centered-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen8-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'G', fdlBasename: 'G_5040x3780_1x_TopAligned-FramingChart', contextLabel: 'RED V-RAPTOR 8K S35', canvasLabel: '7K 4:3 2x' },
    ],
  },
  {
    number: 9, name: 'PadToMax',
    dirName: 'Scen_9_PadToMax',
    templateFilename: 'Scen_9_PadToMax-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen9-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'G', fdlBasename: 'G_5040x3780_1x_TopAligned-FramingChart', contextLabel: 'RED V-RAPTOR 8K S35', canvasLabel: '7K 4:3 2x' },
    ],
  },
  {
    number: 10, name: 'FitWidth_MaintainAspectRatio',
    dirName: 'Scen_10_FitWidth_MaintainAspectRatio',
    templateFilename: 'Scen_10_FitWidth_MaintainAspectRatio-CANVAS-TEMPLATE.fdl',
    resultPattern: '{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'J', fdlBasename: 'J_4320x3456_2x_FramingChart', contextLabel: 'RED DSMC2 MONSTRO 8K VV', canvasLabel: '4.5K 5:4' },
    ],
  },
  {
    number: 11, name: 'FitHeight_MaintainAspectRatio',
    dirName: 'Scen_11_FitHeight_MaintainAspectRatio',
    templateFilename: 'Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl',
    resultPattern: '{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'J', fdlBasename: 'J_4320x3456_2x_FramingChart', contextLabel: 'RED DSMC2 MONSTRO 8K VV', canvasLabel: '4.5K 5:4' },
    ],
  },
  {
    number: 12, name: 'FitDecision_Fill',
    dirName: 'Scen_12_FitDecision_Fill',
    templateFilename: 'Scen_12_FitDecision-Fill.fdl',
    resultPattern: 'Scen12-RESULT{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'D', fdlBasename: 'D_8640x5760_1x_10PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
    ],
  },
  {
    number: 13, name: 'FitDecision_With_Protection_Fill',
    dirName: 'Scen_13_FitDecision_With_Protection_Fill',
    templateFilename: 'Scen_13_FitDecision-With-ProtectionFill.fdl',
    resultPattern: 'Scen13-RESULT{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'D', fdlBasename: 'D_8640x5760_1x_10PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
    ],
  },
  {
    number: 14, name: 'Preserving-Protection-WithMaxDim-Cropping',
    dirName: 'Scen_14_Preserving-Protection-WithMaxDim-Cropping',
    templateFilename: 'Scen_14_Preserving-Protection-WithMaxDim-Cropping-TEMPLATE.fdl',
    resultPattern: 'Scen14-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'D', fdlBasename: 'D_8640x5760_1x_10PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
      { letter: 'E', fdlBasename: 'E_8640x5760_1x_15PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
      { letter: 'F', fdlBasename: 'F_8640x5760_1x_20PercentSafety-FramingChart', contextLabel: 'Sony VENICE 2 8K', canvasLabel: '8.6K 3:2' },
    ],
  },
  {
    number: 15, name: 'Retention_Of_Relative_Anchors',
    dirName: 'Scen_15_Retention_Of_Relative_Anchors',
    templateFilename: 'Scen_15_Retention_of_relative_anchors.fdl',
    resultPattern: 'Scen15-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'A', fdlBasename: 'A_4448x3096_1-3x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'C', fdlBasename: 'C_4448x3096_2x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
    ],
  },
  {
    number: 16, name: 'Retention_Of_Relative_Anchors_pad_to_max_top_left',
    dirName: 'Scen_16_Retention_Of_Relative_Anchors_pad_to_max_top_left',
    templateFilename: 'Scen_16_Retention_Of_Relative_Anchors_pad_to_max_top_left.fdl',
    resultPattern: 'Scen16-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'A', fdlBasename: 'A_4448x3096_1-3x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'C', fdlBasename: 'C_4448x3096_2x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
    ],
  },
  {
    number: 17, name: 'Retention_Of_Relative_Anchors_pad_to_max_bottom_left',
    dirName: 'Scen_17_Retention_Of_Relative_Anchors_pad_to_max_bottom_left',
    templateFilename: 'Scen_17_Retention_Of_Relative_Anchors_pad_to_max_bottom_left.fdl',
    resultPattern: 'Scen17-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'A', fdlBasename: 'A_4448x3096_1-3x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'C', fdlBasename: 'C_4448x3096_2x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
    ],
  },
  {
    number: 18, name: 'Normalizing_LensSqueezeTo2_PadToMax_NonUniform_Crop',
    dirName: 'Scen_18_Normalizing_LensSqueezeTo2_PadToMax_NonUniform_Crop',
    templateFilename: 'Scen_18_Normalizing_LensSqueezeTo2-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen18-RESULT-{variant}.fdl',
    customSourceDir: 'Original_Source_Files',
    variants: [
      { letter: 'A', fdlBasename: 'A_4448x3096_1-3x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'B', fdlBasename: 'B_4448x3096_1x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
      { letter: 'C', fdlBasename: 'C_4448x3096_2x_FramingChart', contextLabel: 'ARRI ALEXA Mini LF', canvasLabel: '4.5K LF Open Gate' },
    ],
  },
  {
    number: 19, name: 'PadToMax_RED_EPIC_Dragon_6K',
    dirName: 'Scen_19_PadToMax_RED_EPIC_Dragon_6K',
    templateFilename: 'Scen_9_PadToMax-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen19-RESULT-{variant}.fdl',
    customTemplateDir: 'Scen_9_PadToMax',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'RED_EPIC', fdlBasename: 'Test_06_RED_EPIC_Dragon_6K', contextLabel: 'RED EPIC DRAGON 6K S35', canvasLabel: '4K 2:1' },
    ],
  },
  {
    number: 20, name: 'Preserving_Protection_WithMaxDim_Cropping_Sony_FX3',
    dirName: 'Scen_20_Preserving_Protection_WithMaxDim_Cropping_Sony_FX3',
    templateFilename: 'Scen_14_Preserving-Protection-WithMaxDim-Cropping-TEMPLATE.fdl',
    resultPattern: 'Scen20-RESULT-{variant}.fdl',
    customTemplateDir: 'Scen_14_Preserving-Protection-WithMaxDim-Cropping',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'SONY_FX3', fdlBasename: 'Test_01_Sony_FX3', contextLabel: 'Sony FX3', canvasLabel: '4K' },
    ],
  },
  // Scenarios 21-22 are error tests — handled separately
  {
    number: 23, name: 'FitDecision_With_Protection_Fill_Blackmagic_17K_65',
    dirName: 'Scen_23_FitDecision_With_Protection_Fill_Blackmagic_17K_65',
    templateFilename: 'Scen_13_FitDecision-With-ProtectionFill.fdl',
    resultPattern: 'Scen23-RESULT-{variant}.fdl',
    customTemplateDir: 'Scen_13_FitDecision_With_Protection_Fill',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'BLACKMAGIC_17K_65', fdlBasename: 'Test_09_Blackmagic_URSA_Cine_17K_65', contextLabel: 'Blackmagic Design URSA Cine 17K 65', canvasLabel: '12K 16:9' },
    ],
  },
  {
    number: 24, name: 'Preserving_Protection_WithMaxDim_Cropping_ARRI_Alexa_65',
    dirName: 'Scen_24_Preserving_Protection_WithMaxDim_Cropping_ARRI_Alexa_65',
    templateFilename: 'Scen_14_Preserving-Protection-WithMaxDim-Cropping-TEMPLATE.fdl',
    resultPattern: 'Scen24-RESULT-{variant}.fdl',
    customTemplateDir: 'Scen_14_Preserving-Protection-WithMaxDim-Cropping',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'ARRI_ALEXA_65_19', fdlBasename: 'Test_19_ARRI_Alexa_65', contextLabel: 'ARRI Alexa 65', canvasLabel: '6500' },
    ],
  },
  {
    number: 25, name: 'FitDecision_With_Protection_Fill_ARRI_Alexa_65',
    dirName: 'Scen_25_FitDecision_With_Protection_Fill_ARRI_Alexa_65',
    templateFilename: 'Scen_13_FitDecision-With-ProtectionFill.fdl',
    resultPattern: 'Scen25-RESULT-{variant}.fdl',
    customTemplateDir: 'Scen_13_FitDecision_With_Protection_Fill',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'ARRI_ALEXA_65_20', fdlBasename: 'Test_20_ARRI_Alexa_65', contextLabel: 'ARRI Alexa 65', canvasLabel: '6500' },
    ],
  },
  {
    number: 26, name: 'FitHeight_MaintainAspectRatio_Blackmagic_12K_LF_CustomFraming',
    dirName: 'Scen_26_FitHeight_MaintainAspectRatio_Blackmagic_12K_LF_CustomFraming',
    templateFilename: 'Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen26-RESULT-{variant}.fdl',
    customTemplateDir: 'Scen_11_FitHeight_MaintainAspectRatio',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'BLACKMAGIC_12K_LF_CUSTOM', fdlBasename: 'Test_58_Blackmagic_URSA_Cine_12K_LF_CustomFraming', contextLabel: 'Blackmagic URSA Cine 12K LF', canvasLabel: '12K 16:9' },
    ],
  },
  {
    number: 27, name: 'FitHeight_MaintainAspectRatio_RED_EPIC_CustomFraming',
    dirName: 'Scen_27_FitHeight_MaintainAspectRatio_RED_EPIC_CustomFraming',
    templateFilename: 'Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen27-RESULT-{variant}.fdl',
    customTemplateDir: 'Scen_11_FitHeight_MaintainAspectRatio',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'RED_EPIC_CUSTOM', fdlBasename: 'Test_60_RED_EPIC_Dragon_6K_CustomFraming', contextLabel: 'RED EPIC Dragon 6K', canvasLabel: '4K 2:1' },
    ],
  },
  {
    number: 28, name: 'FitHeight_MaintainAspectRatio_ARRI_Alexa_65_CustomFraming',
    dirName: 'Scen_28_FitHeight_MaintainAspectRatio_ARRI_Alexa_65_CustomFraming',
    templateFilename: 'Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl',
    resultPattern: 'Scen28-RESULT-{variant}.fdl',
    customTemplateDir: 'Scen_11_FitHeight_MaintainAspectRatio',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'ARRI_ALEXA_65_CUSTOM', fdlBasename: 'Test_62_ARRI_Alexa_65_CustomFraming', contextLabel: 'ARRI Alexa 65', canvasLabel: '6500' },
    ],
  },
  {
    number: 29, name: 'FitDecision_With_Protection_Fill_Sony_FX3_01',
    dirName: 'Scen_29_FitDecision_With_Protection_Fill_Sony_FX3_01',
    templateFilename: 'Scen_13_FitDecision-With-ProtectionFill.fdl',
    resultPattern: 'Scen29-RESULT-{variant}.fdl',
    contextLabel: 'Sony FX3',
    canvasLabel: '4K',
    customTemplateDir: 'Scen_13_FitDecision_With_Protection_Fill',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'SONY_FX3_01', fdlBasename: 'Test_01_Sony_FX3', contextLabel: 'Sony FX3', canvasLabel: '4K' },
    ],
  },
  {
    number: 30, name: 'FitDecision_With_Protection_Fill_Sony_FX3_02',
    dirName: 'Scen_30_FitDecision_With_Protection_Fill_Sony_FX3_02',
    templateFilename: 'Scen_13_FitDecision-With-ProtectionFill.fdl',
    resultPattern: 'Scen30-RESULT-{variant}.fdl',
    contextLabel: 'Sony FX3',
    canvasLabel: '4K',
    customTemplateDir: 'Scen_13_FitDecision_With_Protection_Fill',
    customSourceDir: 'New_Source_Files',
    variants: [
      { letter: 'SONY_FX3_02', fdlBasename: 'Test_02_Sony_FX3', contextLabel: 'Sony FX3', canvasLabel: '4K' },
    ],
  },
  {
    number: 31, name: 'Alignment_Combo_TopLeft_To_TopCenter',
    dirName: 'EdgeCases',
    templateFilename: 'combo_src_topleft_tpl_topcenter_template.fdl',
    resultPattern: 'Scen31-RESULT-combo_src_topleft_tpl_topcenter.fdl',
    contextLabel: 'Off-Center Source top-left',
    canvasLabel: '4K Canvas - Source top-left',
    templateLabel: 'Template: top-center alignment',
    framingIntentId: 'combo_intent',
    contextCreator: 'Edge Case Generator',
    customTemplatePath: 'EdgeCases/alignment_combos/templates',
    customSourceDir: 'EdgeCases/alignment_combos/source',
    customResultsDir: 'EdgeCases/alignment_combos/Results',
    variants: [
      { letter: 'TOPLEFT_TOPCENTER', fdlBasename: 'combo_src_topleft_tpl_topcenter_source', contextLabel: 'Off-Center Source top-left', canvasLabel: '4K Canvas - Source top-left' },
    ],
  },
  {
    number: 32, name: 'EffTopLeft_To_BottomRight',
    dirName: 'Scen_32_EffTopLeft_To_BottomRight',
    templateFilename: 'eff_topleft_to_bottomright_template.fdl',
    resultPattern: 'Scen32-RESULT-eff_topleft_to_bottomright.fdl',
    contextLabel: 'Effective Area eff_topleft_to_bottomright',
    canvasLabel: '6K with offset effective area',
    templateLabel: 'Template: bottom-right from effective',
    framingIntentId: 'eff_combo_intent',
    contextCreator: 'Edge Case Generator',
    customTemplatePath: 'EdgeCases/alignment_combos/templates',
    customSourceDir: 'EdgeCases/alignment_combos/source',
    variants: [
      { letter: 'EFF_TOPLEFT_BOTTOMRIGHT', fdlBasename: 'eff_topleft_to_bottomright_source', contextLabel: 'Effective Area eff_topleft_to_bottomright', canvasLabel: '6K with offset effective area' },
    ],
  },
];

// ---------------------------------------------------------------------------
// Build parameterized test cases
// ---------------------------------------------------------------------------

interface TestCase {
  scenarioNumber: number;
  scenarioName: string;
  variant: SourceVariant;
  config: ScenarioConfig;
}

const TEST_CASES: TestCase[] = [];
for (const config of SCENARIOS) {
  for (const variant of config.variants) {
    TEST_CASES.push({
      scenarioNumber: config.number,
      scenarioName: config.name,
      variant,
      config,
    });
  }
}

// ---------------------------------------------------------------------------
// Parameterized tests
// ---------------------------------------------------------------------------

describe('Scenario template tests (parity with Python)', () => {
  it.each(TEST_CASES)(
    'scen$scenarioNumber $variant.letter',
    ({ config, variant }) => {
      const defaults = {
        templateLabel: 'VFX Pull - Custom',
        framingIntentId: '1',
        contextCreator: 'ASC FDL Tools',
      };
      const templateLabel = config.templateLabel ?? defaults.templateLabel;
      const framingIntentId = config.framingIntentId ?? defaults.framingIntentId;
      const contextCreator = config.contextCreator ?? defaults.contextCreator;
      const contextLabel = variant.contextLabel;
      const canvasLabel = variant.canvasLabel;

      const paths = getScenarioPaths(config, variant);

      // Verify fixture files exist
      expect(existsSync(paths.template), `Template not found: ${paths.template}`).toBe(true);
      expect(existsSync(paths.sourceFdl), `Source FDL not found: ${paths.sourceFdl}`).toBe(true);
      expect(existsSync(paths.expectedFdl), `Expected FDL not found: ${paths.expectedFdl}`).toBe(true);

      // Load template FDL and extract template
      const templateFdl = FDL.parse(readFileSync(paths.template, 'utf-8'));
      templateFdl.validate();
      const template = findTemplate(templateFdl, templateLabel);
      expect(template, `Template '${templateLabel}' not found`).not.toBeNull();

      // Load source FDL and extract components
      const sourceFdl = FDL.parse(readFileSync(paths.sourceFdl, 'utf-8'));
      const context = findContext(sourceFdl, contextLabel);
      expect(context, `Context '${contextLabel}' not found`).not.toBeNull();

      const canvas = findCanvas(context!, canvasLabel);
      expect(canvas, `Canvas '${canvasLabel}' not found`).not.toBeNull();

      const fd = findFD(canvas!, framingIntentId);
      expect(fd, `FD with intent '${framingIntentId}' not found`).not.toBeNull();

      // Apply template with deterministic UUID (same as Python)
      const result = template!.apply(
        canvas!,
        fd!,
        DETERMINISTIC_UUID,
        '',
        contextLabel,
        contextCreator,
      );

      const expectedCanvasId = DETERMINISTIC_UUID;
      const expectedFdId = `${expectedCanvasId}-${framingIntentId}`;

      // Load expected result FDL
      const expectedFdl = FDL.parse(readFileSync(paths.expectedFdl, 'utf-8'));
      expectedFdl.validate();

      // Extract expected components
      const expectedContext = findContext(expectedFdl, templateLabel);
      expect(expectedContext, `Expected context '${templateLabel}' not found`).not.toBeNull();

      const expectedCanvasLabel = `${templateLabel}: ${contextLabel} ${canvasLabel}`;
      const expectedCanvas = findCanvas(expectedContext!, expectedCanvasLabel);
      expect(expectedCanvas, `Expected canvas '${expectedCanvasLabel}' not found`).not.toBeNull();

      const expectedFd = findFD(expectedCanvas!, framingIntentId);
      expect(expectedFd, `Expected FD with intent '${framingIntentId}' not found`).not.toBeNull();

      // Extract actual components from result
      const actualContext = result.context;
      expect(actualContext, 'Actual context not found in result').not.toBeNull();

      const actualCanvas = result.canvas;
      expect(actualCanvas, 'Actual canvas not found in result').not.toBeNull();

      const actualFd = result.framingDecision;
      expect(actualFd, 'Actual FD not found in result').not.toBeNull();

      // Compare all fields (same as Python's FDLComparison)
      compareContext(expectedContext!, actualContext!);
      compareCanvas(expectedCanvas!, actualCanvas!, expectedCanvasId);
      compareFramingDecision(expectedFd!, actualFd!, expectedFdId);

      // Compare canvas template
      const expectedTemplate = findTemplate(expectedFdl, templateLabel);
      const actualTemplate = findTemplate(result.fdl, templateLabel);
      expect(expectedTemplate, `Expected template '${templateLabel}' not found`).not.toBeNull();
      expect(actualTemplate, `Actual template '${templateLabel}' not found`).not.toBeNull();
      compareCanvasTemplate(expectedTemplate!, actualTemplate!);

      // Clean up
      result.fdl.close();
      expectedFdl.close();
      sourceFdl.close();
      templateFdl.close();
    },
  );
});
