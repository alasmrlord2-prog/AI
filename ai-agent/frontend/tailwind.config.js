/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // يدعم Light + Dark mode
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // =============================
        // 🎯 BRAND COLORS (مشتركة بين الوضعين)
        // =============================
        "sw-blue": "var(--sw-blue)",
        "sw-blue-light": "var(--sw-blue-light)",
        "sw-teal": "var(--sw-teal)",
        "sw-teal-light": "var(--sw-teal-light)",

        // =============================
        // 🌗 BACKGROUND COLORS (تتغير حسب الوضع)
        // =============================
        "sw-bg": "var(--sw-bg)",
        "sw-bg-soft": "var(--sw-bg-soft)",
        "sw-bg-card": "var(--sw-bg-card)",
        "sw-bg-hover": "var(--sw-bg-hover)",
        "sw-bg-sidebar": "var(--sw-bg-sidebar)",

        // =============================
        // 🧱 BORDER COLORS
        // =============================
        "sw-border": "var(--sw-border)",

        // =============================
        // ⚪ TEXT COLORS
        // =============================
        "sw-text": "var(--sw-text)",
        "sw-text-soft": "var(--sw-text-soft)",
        "sw-text-muted": "var(--sw-text-muted)",
        "sw-text-strong": "var(--sw-text-strong)",

        // =============================
        // 🟩 STATUS COLORS (مشتركة)
        // =============================
        "sw-success": "var(--sw-success)",
        "sw-warning": "var(--sw-warning)",
        "sw-danger": "var(--sw-danger)",

        // =============================
        // 🎨 CRM THEME COLORS
        // =============================
        sw: {
          primary: "#00FFFF",
          primaryDark: "#00CCCC",
          accent: "#1C2B5F",
          bg: "#F7F9FB",
          surface: "#FFFFFF",
          darkBg: "#0F172A",
          darkSurface: "#1E293B",
          text: "#0A0A0A",
          textLight: "#4A4A4A",
          border: "#E5E9EF",
          darkBorder: "#2C3A4E",
        },

        // =============================
        // 🔐 AAA THEME COLORS (واجهة الإدارة)
        // =============================
        swAuth: {
          bg: "#FFFFFF",
          surface: "#FAFBFC",
          darkBg: "#0C1320",
          darkSurface: "#151E2E",
          primary: "#00FFFF",
          warning: "#F59E0B",
          danger: "#EF4444",
        },
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
        "sw-card": "var(--sw-shadow-card)",
        "sw-card-dark": "var(--sw-shadow-card-dark)",
      },

      backgroundImage: {
        "sw-gradient": "linear-gradient(90deg, var(--sw-blue), var(--sw-teal))",
      },
    },
  },
  plugins: [],
};

