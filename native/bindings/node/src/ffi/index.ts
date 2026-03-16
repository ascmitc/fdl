// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Loads the compiled N-API addon and verifies ABI version compatibility.
 *
 * The addon is a thin C++ bridge that wraps every C function from
 * libfdl_core into N-API functions, handling string encoding, pointer
 * wrapping, struct conversion, and error propagation.
 */

import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);

/** Expected ABI version range. */
const ABI_MAJOR = 0;
const ABI_MINOR_MIN = 3;

/**
 * NativeAddon interface — all functions exported by the C++ addon.
 * The full interface is generated in ffi/types.ts; this file provides
 * the loader and singleton accessor.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type NativeAddon = Record<string, (...args: any[]) => any>;

let _addon: NativeAddon | null = null;

/**
 * Get the loaded addon singleton. Loads and verifies ABI on first call.
 */
export function getAddon(): NativeAddon {
  if (!_addon) {
    _addon = loadAndVerify();
  }
  return _addon;
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

function candidatePaths(): string[] {
  const paths: string[] = [];

  // 1. FDL_NODE_ADDON_PATH env var (explicit)
  const envPath = process.env.FDL_NODE_ADDON_PATH;
  if (envPath) paths.push(envPath);

  // 2. Prebuilds directory (npm-published binaries)
  const { platform, arch } = process;
  paths.push(
    join(
      __dirname,
      "..",
      "..",
      "prebuilds",
      `${platform}-${arch}`,
      "fdl_addon.node",
    ),
  );

  // 3. Build output directory (standard cmake-js location)
  paths.push(join(__dirname, "..", "..", "build", "fdl_addon.node"));

  // 4. Build output at package root (alternative)
  paths.push(join(__dirname, "..", "..", "build", "Release", "fdl_addon.node"));
  paths.push(join(__dirname, "..", "..", "build", "Debug", "fdl_addon.node"));

  return paths;
}

function loadAndVerify(): NativeAddon {
  let addon: NativeAddon | null = null;

  for (const p of candidatePaths()) {
    if (existsSync(p)) {
      addon = require(p) as NativeAddon;
      break;
    }
  }

  if (!addon) {
    const searched = candidatePaths().join("\n  ");
    throw new Error(
      `Could not load fdl_addon.node. Build the addon first with:\n` +
        `  npm run build:addon\n` +
        `Or set FDL_NODE_ADDON_PATH to the .node file.\n` +
        `Searched:\n  ${searched}`,
    );
  }

  // Verify ABI version
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

  return addon;
}
