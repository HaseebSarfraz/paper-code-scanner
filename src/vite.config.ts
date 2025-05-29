// vite.config.ts
import { defineConfig } from "vite";
import { resolve } from "path";


export default defineConfig({
  // point Vite at your `public/` folder
  root: "public",

  build: {
    // emit the production build into `dist/`
    outDir: "../dist",
    emptyOutDir: true,
    rollupOptions: {
      // ensure it picks up your index.html
      input: "public/index.html",
    },
  },

  resolve: {
    alias: {
      // now you can import from "~/foo" to mean "src/foo"
      "~": resolve(process.cwd(), "src"),
    },
  },
});