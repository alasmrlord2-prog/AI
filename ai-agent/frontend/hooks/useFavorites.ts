// hooks/useFavorites.ts
"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "sw-favorites";

export function useFavorites() {
  const [favorites, setFavorites] = useState<string[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as string[];
        // Only update if different from initial state
        setTimeout(() => {
          setFavorites((prev) => {
            const parsedArray = parsed as string[];
            return JSON.stringify(prev) === JSON.stringify(parsedArray) ? prev : parsedArray;
          });
        }, 0);
      }
      setTimeout(() => setHydrated(true), 0);
    } catch (e) {
      console.error("Failed to load favorites", e);
      setTimeout(() => setHydrated(true), 0);
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

