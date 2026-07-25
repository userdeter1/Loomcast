import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // "loom" accent — a woven indigo/violet
        loom: {
          50: "#eef1ff",
          100: "#e0e5ff",
          200: "#c7cfff",
          300: "#a5adff",
          400: "#8385fb",
          500: "#6d63f2",
          600: "#5c46e0",
          700: "#4f39c5",
          800: "#41319f",
          900: "#382f7e",
        },
      },
      fontFamily: {
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
