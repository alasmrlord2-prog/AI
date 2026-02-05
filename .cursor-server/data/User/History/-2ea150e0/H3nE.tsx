"use client";

import { useState } from "react";
import { ThemeToggle } from "@/components/ui/theme-toggle";

type HeaderProps = {
  locale?: string;
  setLocale?: (locale: string) => void;
};

export default function Header(props: HeaderProps = {}) {
  const { locale: propLocale, setLocale: propSetLocale } = props;
  const [internalLocale, setInternalLocale] = useState("en");
  
  // Use props if provided, otherwise use internal state
  const locale = propLocale ?? internalLocale;
  const handleSetLocale = propSetLocale ?? setInternalLocale;

  return (
    <header className="w-full px-6 py-4 bg-sw-bg-soft border-b border-sw-border flex justify-between items-center flex-shrink-0">
      <h1 className="text-lg font-semibold text-sw-text-strong tracking-tight">
        SHIFTWAVE AI
      </h1>

      <div className="flex items-center gap-3">
        <ThemeToggle />
        <button
          onClick={() => {
            handleSetLocale(locale === "ar" ? "en" : "ar");
          }}
          className="rounded-sw-btn border border-sw-border bg-sw-bg-card px-4 py-2 text-xs text-sw-text-soft hover:bg-sw-bg-hover transition-colors font-medium"
        >
          {locale === "ar" ? "English" : "العربية"}
        </button>
      </div>
    </header>
  );
}

