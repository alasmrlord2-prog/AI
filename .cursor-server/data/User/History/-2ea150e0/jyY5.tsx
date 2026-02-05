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
    <header className="w-full px-6 py-4 bg-[oklch(0.12_0_0)] border-b border-[oklch(1_0_0_/_0.10)] flex justify-between items-center flex-shrink-0">
      <h1 className="text-lg font-semibold text-white tracking-tight">
        Local AI Agent
      </h1>

      <button
        onClick={() => {
          handleSetLocale(locale === "ar" ? "en" : "ar");
        }}
        className="text-[oklch(0.70_0_0)] hover:text-white px-4 py-2 rounded-lg hover:bg-[oklch(0.18_0_0)] transition-all duration-200 text-sm font-medium"
      >
        {locale === "ar" ? "English" : "العربية"}
      </button>
    </header>
  );
}

