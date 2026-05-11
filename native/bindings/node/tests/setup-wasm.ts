// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Vitest setup file for the WASM backend.
 *
 * Runs once per test worker BEFORE any test file executes. Loads the
 * Emscripten-compiled module and installs it as the active addon via
 * `setAddon()`. Because the TypeScript facade resolves `getAddon()`
 * lazily inside class constructors (not at import time), every test that
 * subsequently constructs an `FDL`, `Canvas`, etc. transparently runs
 * against the WASM backend.
 *
 * Activate by running `vitest -c vitest.wasm.config.ts` (or via the
 * `test:wasm` npm script).
 */

import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { initialize } from "../src/wasm/index.js";

const here = dirname(fileURLToPath(import.meta.url));
const wasmFile = join(here, "..", "wasm", "fdl_module.wasm");

if (!existsSync(wasmFile)) {
  throw new Error(
    `WASM artifact missing at ${wasmFile}.\n` +
      `Build it first:  python scripts/build_wasm.py`,
  );
}

await initialize();
