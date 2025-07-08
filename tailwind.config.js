/** @type {import('tailwindcss').Config} */
module.exports = {
  darkModeL: "media",

  content: [
    "./index.html", // root-level test page
    "./public/**/*.html", // future pages in /public
    "./src/**/*.{js,ts,jsx,tsx}", // future JS/TS/React files
    "./html+ css practice/**/*.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        cursive: ["'Great Vibes'", "cursive"],
        kaushan: ["'Kaushan Script"],
        marker: ["'Permanent Marker'", "cursive"],
        pacifico: ["Pacifico", "cursive"],
      },

      colors: {
          accent: { 
            DEFAULT: '#10b981',
            ring: '#34d399'
          }
      },
    },
  },
  plugins: [],
};
