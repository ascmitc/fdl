import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
    globals: true,
    // Register the N-API loader before any test file. Tests import facades
    // directly (not via index.ts), so this is where getAddon() gets its loader.
    setupFiles: ["./tests/setup-napi.ts"],
  },
});
