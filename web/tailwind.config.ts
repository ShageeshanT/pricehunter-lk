import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}", "./lib/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#071018",
        limeglow: "#c8ff65",
        ember: "#ff6b35"
      },
      boxShadow: {
        glow: "0 0 28px rgba(200, 255, 101, 0.35)"
      }
    }
  },
  plugins: []
};

export default config;
