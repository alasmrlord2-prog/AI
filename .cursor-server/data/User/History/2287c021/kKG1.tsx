"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Check localStorage - default to light mode
    const saved = localStorage.getItem("theme");
    
    const shouldBeDark = saved === "dark";
    setIsDark(shouldBeDark);
    
    if (shouldBeDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, []);

  const toggleTheme = () => {
    const html = document.documentElement;
    const currentlyDark = html.classList.contains("dark");
    const newIsDark = !currentlyDark;
    
    // Toggle the class immediately
    if (newIsDark) {
      html.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      html.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
    
    setIsDark(newIsDark);
    
    // Force update all CSS variables by triggering a reflow
    void html.offsetHeight;
    
    // Force update body and main elements
    const body = document.body;
    const main = document.querySelector("main");
    if (body) {
      body.style.backgroundColor = getComputedStyle(html).getPropertyValue("--sw-bg");
      body.style.color = getComputedStyle(html).getPropertyValue("--sw-text");
    }
    if (main) {
      (main as HTMLElement).style.backgroundColor = getComputedStyle(html).getPropertyValue("--sw-bg");
      (main as HTMLElement).style.color = getComputedStyle(html).getPropertyValue("--sw-text");
    }
  };

  if (!mounted) {
    return (
      <button className="rounded-sw-btn border border-sw-border px-3 py-2 text-xs text-sw-text-muted">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      </button>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className="rounded-sw-btn border border-sw-border bg-sw-bg-card px-3 py-2 text-xs text-sw-text-soft hover:bg-sw-bg-hover transition-colors flex items-center gap-2"
      aria-label="Toggle theme"
    >
      {isDark ? (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <span>Light</span>
        </>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
          <span>Dark</span>
        </>
      )}
    </button>
  );
}

