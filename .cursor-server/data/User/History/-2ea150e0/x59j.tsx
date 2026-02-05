"use client";

import { useState } from "react";

type HeaderProps = {
  locale?: string;
  setLocale?: (locale: string) => void;
};

export default function Header({ locale: propLocale, setLocale: propSetLocale }: HeaderProps = {}) {
  const [internalLocale, setInternalLocale] = useState("en");
  
  // Use props if provided, otherwise use internal state
  const locale = propLocale ?? internalLocale;
  const handleSetLocale = propSetLocale ?? setInternalLocale;

  return (
    <header className="w-full p-4 bg-slate-900 border-b border-slate-800 flex justify-between items-center">
      <h1 className="text-lg font-semibold text-slate-200">
        Local AI Agent
      </h1>

      <button
        onClick={() => {
          handleSetLocale(locale === "ar" ? "en" : "ar");
        }}
        className="text-slate-300 hover:text-white px-3 py-1 rounded hover:bg-slate-800 transition-colors"
      >
        {locale === "ar" ? "English" : "العربية"}
      </button>
    </header>
  );
}

