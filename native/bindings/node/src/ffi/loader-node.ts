// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * Node.js-only N-API addon loader.
 *
 * This module locates and loads the compiled `fdl_addon.node` from disk and
 * registers it with the backend-agnostic registry in `./index.ts`. It is the
 * ONLY binding module that imports Node.js built-ins, so it must never be
 * reachable from the browser/WASM entry point. The Node.js entry (`index.ts`)
 * imports it for its side effect; the browser entry does not.
 *
 * Importing this module is sufficient to wire up the N-API backend — it calls
 * `registerLoader()` at module load so the first `getAddon()` lazily loads and
 * ABI-verifies the addon.
 */

import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { registerLoader, verifyAbi, type NativeAddon } from "./index.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);

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

  verifyAbi(addon);
  return addon;
}

// Register the N-API loader with the backend-agnostic registry. The first
// getAddon() call will invoke loadAndVerify() lazily.
registerLoader(loadAndVerify);
