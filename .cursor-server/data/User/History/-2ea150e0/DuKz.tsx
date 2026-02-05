"use client";

import { useState } from "react";

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
    <header className="w-full px-6 py-4 bg-slate-900 border-b border-slate-800/50 flex justify-between items-center flex-shrink-0">
      <h1 className="text-lg font-semibold text-white tracking-tight">
        Local AI Agent
      </h1>

      <button
        onClick={() => {
          handleSetLocale(locale === "ar" ? "en" : "ar");
        }}
        className="text-slate-300 hover:text-white px-4 py-2 rounded-lg hover:bg-slate-800/50 transition-all duration-200 text-sm font-medium"
      >
        {locale === "ar" ? "English" : "العربية"}
      </button>
    </header>
  );
}

