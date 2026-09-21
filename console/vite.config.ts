/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The console talks to the engine on the SAME ORIGIN (relative paths). In dev,
// Vite proxies the engine's routes to a locally-running engine; in production
// the static bundle is served behind a reverse proxy that forwards the same
// paths. This keeps the engine free of CORS (16-security-model) — no engine code
// change is needed to ship the console.
const ENGINE_URL = process.env.VITE_ENGINE_URL ?? "http://localhost:8000";
const proxied = ["/v1", "/health", "/metrics"];

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: Object.fromEntries(
      proxied.map((path) => [path, { target: ENGINE_URL, changeOrigin: true }]),
    ),
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: false,
  },
});
