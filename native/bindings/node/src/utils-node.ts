// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file utils-node.ts
 * @brief Node.js-only file I/O helpers for FDL documents.
 *
 * These use node:fs and must NOT be imported by the browser/WASM entry. The
 * Node.js entry (index.ts) re-exports them; browser callers use readFromString
 * / writeToString with their own fetch/Blob I/O instead.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { readFromString, writeToString } from "./utils.js";
import type { FDL } from "./fdl.js";

/** Read an FDL document from a file on disk. */
export function readFromFile(filePath: string, validate = true): FDL {
  const contents = readFileSync(filePath, "utf-8");
  return readFromString(contents, validate);
}

/** Write an FDL document to a file on disk. */
export function writeToFile(doc: FDL, filePath: string, validate = true): void {
  writeFileSync(filePath, writeToString(doc, validate), "utf-8");
}
