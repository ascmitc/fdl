// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Vitest config for the WASM backend. Runs the full existing test suite
 * against the Emscripten-compiled module via tests/setup-wasm.ts.
 *
 * The N-API-specific FFI smoke test is excluded — it asserts behavior of
 * the .node addon's pointer wrapping which differs in WASM.
 */
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
    exclude: [
      "tests/ffi-smoke.test.ts",
    ],
    globals: true,
    setupFiles: ["./tests/setup-wasm.ts"],
    pool: "forks",
  },
});
