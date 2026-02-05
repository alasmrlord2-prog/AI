"use client";

import { useState } from "react";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import TopNav from "@/components/TopNav";
import FavoritesBar from "@/components/FavoritesBar";
import ServicesDrawer from "@/components/ServicesDrawer";
import { useFavorites } from "@/hooks/useFavorites";
import { useRecent } from "@/hooks/useRecent";

type HeaderProps = {
  locale?: string;
  setLocale?: (locale: string) => void;
};

export default function Header(props: HeaderProps = {}) {
  const { locale: propLocale, setLocale: propSetLocale } = props;
  const [internalLocale, setInternalLocale] = useState<"ar" | "en">("en");
  const [drawerOpen, setDrawerOpen] = useState(false);
  
  // Use props if provided, otherwise use internal state
  const locale = propLocale ?? internalLocale;
  const handleSetLocale = propSetLocale ?? setInternalLocale;

  // Favorites and Recent hooks
  const { favorites, toggleFavorite, hydrated } = useFavorites();
  useRecent();

  return (
    <>
      <TopNav 
        onServicesClick={() => setDrawerOpen(true)}
        locale={locale}
        setLocale={handleSetLocale}
      />
      {hydrated && <FavoritesBar favorites={favorites} />}
      <ServicesDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        favorites={favorites}
        toggleFavorite={toggleFavorite}
      />
    </>
  );
}

