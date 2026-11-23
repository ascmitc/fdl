// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Backend-agnostic addon registry and ABI verification.
 *
 * This module holds the active addon singleton and the compatibility check
 * shared by both backends. It deliberately imports NO Node.js built-ins so it
 * stays safe to bundle for the browser via the `@asc-mitc/fdl/wasm` entry.
 *
 * The N-API loader (which does use Node built-ins) lives in the separate
 * `./loader-node.ts` module and registers itself via `registerLoader()` when
 * imported. The WASM entry instead injects its addon via `setAddon()`.
 */

/** Expected ABI version range. */
export const ABI_MAJOR = 0;
export const ABI_MINOR_MIN = 3;

/**
 * NativeAddon interface — all functions exported by the C++ addon.
 * The full interface is generated in ffi/types.ts; this file provides
 * the loader and singleton accessor.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type NativeAddon = Record<string, (...args: any[]) => any>;

/**
 * Verify that the addon's ABI version is compatible with this facade.
 * Used by both the N-API loader and the WASM `initialize()` path so they
 * apply the same compatibility check.
 *
 * @throws Error if the major version does not match or the minor is below the minimum.
 */
export function verifyAbi(addon: NativeAddon): void {
  const ver = addon.fdl_abi_version() as {
    major: number;
    minor: number;
    patch: number;
  };
  if (ver.major !== ABI_MAJOR || ver.minor < ABI_MINOR_MIN) {
    throw new Error(
      `fdl_core ABI ${ver.major}.${ver.minor}.${ver.patch} is incompatible. ` +
        `Expected ${ABI_MAJOR}.>=${ABI_MINOR_MIN}.x`,
    );
  }
}

let _addon: NativeAddon | null = null;
let _loader: (() => NativeAddon) | null = null;

/**
 * Register a backend loader that lazily produces the addon on first use.
 *
 * The Node.js path registers the N-API loader (see `./loader-node.ts`); the
 * WASM path does not use this and instead calls `setAddon()` directly.
 */
export function registerLoader(fn: () => NativeAddon): void {
  _loader = fn;
}

/**
 * Get the active addon singleton. Invokes the registered loader on first call
 * (Node.js path); throws if no addon has been installed or loader registered.
 */
export function getAddon(): NativeAddon {
  if (_addon) return _addon;
  if (_loader) {
    _addon = _loader();
    return _addon;
  }
  throw new Error(
    "No FDL addon available. For Node.js, import '@asc-mitc/fdl' " +
      "(which registers the N-API loader); for the browser, call " +
      "initialize() from '@asc-mitc/fdl/wasm' before using any FDL API.",
  );
}

/**
 * Install a pre-built addon implementation, bypassing the N-API loader.
 *
 * Used by the `@asc-mitc/fdl/wasm` entry point to inject the Emscripten-built
 * adapter as the addon. Must be called *before* any facade class is
 * instantiated; subsequent calls overwrite the previous addon. Mixing
 * backends in a single process is not supported.
 */
export function setAddon(addon: NativeAddon): void {
  _addon = addon;
}

/**
 * Check if the addon is available without throwing.
 */
export function isAvailable(): boolean {
  try {
    getAddon();
    return true;
  } catch {
    return false;
  }
}
