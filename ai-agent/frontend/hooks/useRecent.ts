// hooks/useRecent.ts
"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

const STORAGE_KEY = "sw-recent";

export function useRecent() {
  const path = usePathname();

  useEffect(() => {
    if (!path) return;

    try {
      const saved: string[] = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      // Remove current path if exists, then add it to the beginning
      const updated = [path, ...saved.filter((x) => x !== path)].slice(0, 10);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch (e) {
      console.error("Failed to update recent", e);
    }
  }, [path]);
}

export function getRecentFromStorage(): string[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

