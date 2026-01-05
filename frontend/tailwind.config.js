/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: "#F9F9F7",
          pure: "#FFFFFF",
          dark: "#F2F2F0",
        },
        ink: {
          DEFAULT: "#1A1A1A",
          light: "#555555",
          lighter: "#888888",
          faint: "#E0E0E0",
        },
        signal: {
          DEFAULT: "#FF4D00",
          hover: "#CC3D00",
        },
        forest: {
          DEFAULT: "#006644",
          light: "#E5F0EB",
        },
        technical: {
          DEFAULT: "#2B5C8A",
          light: "#EAF2F8",
        },
        grade: {
          A: "#006644",
          B: "#8DA399",
          C: "#D4C5A3",
          D: "#D97706",
          F: "#B91C1C",
        },
        surface: {
          DEFAULT: "rgba(255,255,255,0.04)",
          hover: "rgba(255,255,255,0.08)",
        },
      },
      fontFamily: {
        serif: ['"Fraunces"', "serif"],
        sans: ['"Geist Sans"', '"Inter"', "sans-serif"],
        mono: ['"Geist Mono"', "monospace"],
      },
      borderRadius: {
        DEFAULT: "2px",
        sm: "1px",
        md: "2px",
        lg: "4px",
        full: "9999px",
        none: "0px",
      },
      borderWidth: {
        DEFAULT: "1px",
        3: "3px",
      },
      boxShadow: {
        subtle: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        elevated:
          "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "glow-sm": "0 0 10px rgba(0,0,0,0.05)",
        "glow-md": "0 0 20px rgba(0,0,0,0.1)",
      },
      backgroundImage: {
        "grid-pattern":
          "linear-gradient(to right, #E0E0E0 1px, transparent 1px), linear-gradient(to bottom, #E0E0E0 1px, transparent 1px)",
        "dot-pattern": "radial-gradient(#E0E0E0 1px, transparent 1px)",
      },
      animation: {
        snap: "snap 0.2s cubic-bezier(0, 0, 0.2, 1)",
        ticker: "ticker 20s linear infinite",
      },
      keyframes: {
        snap: {
          "0%": { transform: "scale(0.98)" },
          "100%": { transform: "scale(1)" },
        },
        ticker: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-100%)" },
        },
      },
    },
  },
  plugins: [],
};
