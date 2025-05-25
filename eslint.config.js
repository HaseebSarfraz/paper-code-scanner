// eslint.config.js
import globals from "globals";
import js from "@eslint/js";
import eslintPluginPrettier from "eslint-plugin-prettier";
import eslintConfigPrettier from "eslint-config-prettier/flat";

export default [
  // 1️⃣ Core ESLint rules
  js.configs.recommended,

  // 2️⃣ Prettier plugin + report formatting errors
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
    },
    plugins: {
      prettier: eslintPluginPrettier,
    },
    rules: {
      "prettier/prettier": "error",
    },
  },

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

  // 5) Finally, turn off any rules conflicting with Prettier
  eslintConfigPrettier,
];
