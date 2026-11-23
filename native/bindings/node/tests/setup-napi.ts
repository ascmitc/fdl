// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Vitest setup file for the default (N-API) backend.
 *
 * Runs once per test worker BEFORE any test file. Test files import facade
 * classes directly (e.g. `../src/fdl.js`) rather than through the package
 * entry `index.ts`, so the N-API loader's self-registration side effect would
 * otherwise never run. Importing loader-node here registers the loader so the
 * first `getAddon()` call lazily loads and ABI-verifies the native addon.
 */

import "../src/ffi/loader-node.js";
