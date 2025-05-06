/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",              // root-level test page
    "./public/**/*.html",        // future pages in /public
    "./src/**/*.{js,ts,jsx,tsx}" // future JS/TS/React files
  ],
  theme: { extend: {} },
  plugins: [],
};