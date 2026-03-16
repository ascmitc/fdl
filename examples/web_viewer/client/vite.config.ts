import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

const serverPort = process.env.SERVER_PORT || "3001";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      "/api": `http://localhost:${serverPort}`,
    },
  },
});
