/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // خلي الداشبورد داكنة
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // =============================
        // 🎯 BRAND COLORS
        // =============================
        "sw-primary": "#1399FF",
        "sw-primary-light": "#4BB8FF",
        "sw-primary-dark": "#0D6BD0",

        "sw-secondary": "#00D1CE",
        "sw-secondary-light": "#2EE3E0",
        "sw-secondary-dark": "#00A3A0",

        // =============================
        // ⚫ BACKGROUND COLORS
        // =============================
        "sw-bg": "#0A0F16",
        "sw-bg-soft": "#0E1622",
        "sw-bg-card": "#121C27",
        "sw-bg-card-dark": "#101621",
        "sw-bg-hover": "#182332",
        "sw-bg-sidebar": "#0A1A2F", // Sidebar background

        // =============================
        // 🧱 BORDER COLORS
        // =============================
        "sw-border": "#1F2A37",

        // =============================
        // ⚪ TEXT COLORS
        // =============================
        "sw-text": "#FFFFFF",
        "sw-text-soft": "#C8D1E0",
        "sw-text-muted": "#8A94A6",
        "sw-text-strong": "#E4EBF5",

        // =============================
        // 🟩 STATUS COLORS
        // =============================
        "sw-success": "#10B981",
        "sw-warning": "#F59E0B",
        "sw-danger": "#EF4444",
      },

      fontFamily: {
        // English fonts
        sans: ["Inter", "system-ui", "sans-serif"],
        // Arabic fonts
        arabic: ["Cairo", "system-ui", "sans-serif"],
      },

      spacing: {
        // نظام مسافات موحّد
        "xxs": "4px",
        "xs": "8px",
        "sm": "12px",
        "md": "16px",
        "lg": "24px",
        "xl": "32px",
        "2xl": "48px",
      },

      borderRadius: {
        "sw-card": "14px",
        "sw-btn": "8px",
      },

      boxShadow: {
        "sw-soft": "0 8px 20px rgba(0,0,0,0.35)",
        "sw-glow": "0 0 20px rgba(19,153,255,0.3)",
      },

      backgroundImage: {
        "sw-gradient": "linear-gradient(90deg, #1399FF, #00D1CE)",
      },
    },
  },
  plugins: [],
};

