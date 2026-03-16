// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file errors.ts
 * @brief Error classes for FDL operations.
 */

/** Base error for FDL operations. */
export class FDLError extends Error {
  constructor(message?: string) {
    super(message);
    this.name = "FDLError";
  }
}

/** Raised when FDL validation fails. */
export class FDLValidationError extends FDLError {
  constructor(message?: string) {
    super(message);
    this.name = "FDLValidationError";
  }
}
