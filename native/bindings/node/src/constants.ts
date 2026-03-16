// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file constants.ts
 * @brief TypeScript string enums for FDL constants.
 */

export enum RoundingMode {
  UP = "up",
  DOWN = "down",
  ROUND = "round",
}

export enum RoundingEven {
  WHOLE = "whole",
  EVEN = "even",
}

export enum GeometryPath {
  CANVAS_DIMENSIONS = "canvas.dimensions",
  CANVAS_EFFECTIVE_DIMENSIONS = "canvas.effective_dimensions",
  FRAMING_PROTECTION_DIMENSIONS = "framing_decision.protection_dimensions",
  FRAMING_DIMENSIONS = "framing_decision.dimensions",
}

export enum FitMethod {
  WIDTH = "width",
  HEIGHT = "height",
  FIT_ALL = "fit_all",
  FILL = "fill",
}

export enum HAlign {
  LEFT = "left",
  CENTER = "center",
  RIGHT = "right",
}

export enum VAlign {
  TOP = "top",
  CENTER = "center",
  BOTTOM = "bottom",
}

// ---------------------------------------------------------------------------
// Floating-point comparison
// ---------------------------------------------------------------------------

export const FP_REL_TOL = 1e-9;
export const FP_ABS_TOL = 1e-6;

// ---------------------------------------------------------------------------
// First-class custom attribute name constants
// ---------------------------------------------------------------------------

export const ATTR_SCALE_FACTOR: string = "scale_factor";
export const ATTR_CONTENT_TRANSLATION: string = "content_translation";
export const ATTR_SCALED_BOUNDING_BOX: string = "scaled_bounding_box";
