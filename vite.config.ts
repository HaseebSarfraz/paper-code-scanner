// vite.config.ts
///<reference types="node" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],

  // Optional: nice alias so you can import from "~/components/…"
  resolve: {
    alias: {
      "~": resolve(__dirname, "src"),
    },
  },
});