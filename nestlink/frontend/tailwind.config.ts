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
      colors: {
        nest: {
          bg: "#f4f5f7",
          panel: "#ffffff",
          border: "rgba(15,23,42,0.08)",
          text: "#1b1f24",
          muted: "#6b7280",
          accent: "#e4032e",
          warm: "#d97706",
          green: "#059669",
        },
      },
      boxShadow: {
        "nest-panel":
          "0 4px 20px rgba(15,23,42,0.06), 0 0 0 1px rgba(15,23,42,0.04)",
        "nest-glow": "0 0 28px rgba(228,3,46,0.1)",
      },
      borderRadius: {
        xl: "0.875rem",
      },
    },
  },
  plugins: [],
};

export default config;
