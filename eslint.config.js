// eslint.config.js
import globals from "globals";
import js from "@eslint/js";
import tsPlugin from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";

export default [
  // 1️⃣ Core ESLint rules
  js.configs.recommended,

  // 3) Browser files (public/js/*): window, document, fetch, Prism, etc.
  {
    files: ["public/js/**/*.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
        Prism: "readonly", // Prism comes from the <script> tag
      },
    },
  },

  // 4) Node config files (postcss.config.js, tailwind.config.js, etc.)
  {
    files: ["*.config.js"],
    languageOptions: {
      globals: globals.node,
    },
  },

  {
    files: ["src/**/*.{ts,cts,mts,tsx}"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        project: "./tsconfig.json",
      },
      globals: {
        ...globals.browser,
        Prism: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
    },
    rules: {
      // pull in the “recommended” TS rules
      ...tsPlugin.configs.recommended.rules,
    },
  },
];
