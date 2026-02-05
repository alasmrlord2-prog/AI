// hooks/useFavorites.ts
"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "sw-favorites";

export function useFavorites() {
  const [favorites, setFavorites] = useState<string[]>([]);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setFavorites(JSON.parse(saved));
      }
      setHydrated(true);
    } catch (e) {
      console.error("Failed to load favorites", e);
      setHydrated(true);
    }
  }, []);

  const toggleFavorite = (id: string) => {
    setFavorites((prev) => {
      let updated: string[];
      if (prev.includes(id)) {
        updated = prev.filter((x) => x !== id);
      } else {
        updated = [...prev, id];
      }
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (e) {
        console.error("Failed to save favorites", e);
      }
      return updated;
    });
  };

  return { favorites, toggleFavorite, hydrated };
}

