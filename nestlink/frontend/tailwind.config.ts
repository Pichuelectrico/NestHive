import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-outfit)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "ui-monospace", "monospace"],
      },
      // Paleta NestHive (espejo de los tokens --hive-* / --nest-* de globals.css).
      // Hex estáticos para que funcionen los modificadores de opacidad (/40, /[0.1]).
      colors: {
        nest: {
          bg: "#fbfbf8",
          panel: "#ffffff",
          border: "rgba(91,57,24,0.12)",
          text: "#5b3918",
          muted: "#8a6d4f",
          accent: "#f9ae08",
          // Miel oscuro para texto pequeño sobre crema (≈5:1, legible en proyector)
          ink: "#8a5a00",
          warm: "#fbc866",
          green: "#059669",
          // Rojo SOLO semántico (alertas / stock crítico / error)
          red: "#e4032e",
        },
      },
      boxShadow: {
        "nest-panel":
          "0 4px 20px rgba(91,57,24,0.06), 0 0 0 1px rgba(91,57,24,0.04)",
        "nest-glow": "0 0 28px rgba(249,174,8,0.12)",
      },
      borderRadius: {
        xl: "0.875rem",
      },
    },
  },
  plugins: [],
};

export default config;
