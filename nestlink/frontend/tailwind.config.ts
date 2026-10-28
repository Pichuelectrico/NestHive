import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-fira-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-fira-code)", "ui-monospace", "monospace"],
      },
      // Paleta NestHive (espejo de los tokens --hive-* / --nest-* de globals.css).
      // Hex estáticos para que funcionen los modificadores de opacidad (/40, /[0.1]).
      colors: {
        nest: {
          bg: "#f4efe6",
          panel: "#fffcf7",
          border: "rgba(91,57,24,0.14)",
          text: "#5b3918",
          muted: "#674627",
          accent: "#f9ae08",
          // Miel oscuro para texto pequeño sobre crema (≈5.8:1 sobre panel)
          ink: "#8a5a00",
          warm: "#fbc866",
          green: "#065f46",
          // Rojo SOLO semántico (alertas / stock crítico / error)
          red: "#e4032e",
        },
      },
      boxShadow: {
        "nest-panel": "0 1px 2px rgba(36,22,9,0.06)",
        "nest-glow": "0 8px 24px rgba(36,22,9,0.08)",
      },
      borderRadius: {
        xl: "0.875rem",
      },
    },
  },
  plugins: [],
};

export default config;
