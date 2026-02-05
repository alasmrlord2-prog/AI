"use client";

import { useEffect, useState } from "react";

export type TenantFeatureMap = Record<
  string,
  { enabled?: boolean; limits?: Record<string, number> }
>;

const FEATURES_KEY = "tenant_features";
const FEATURES_UPDATED_EVENT = "tenant-features-updated";

export function useTenantFeatures(): TenantFeatureMap | null {
  const [features, setFeatures] = useState<TenantFeatureMap | null>(null);

  useEffect(() => {
    const load = () => {
      const raw = localStorage.getItem(FEATURES_KEY);
      if (!raw) {
        setFeatures(null);
        return;
      }
      try {
        setFeatures(JSON.parse(raw));
      } catch {
        setFeatures(null);
      }
    };

    load();
    const handler = () => load();
    window.addEventListener(FEATURES_UPDATED_EVENT, handler);
    window.addEventListener("storage", handler);
    return () => {
      window.removeEventListener(FEATURES_UPDATED_EVENT, handler);
      window.removeEventListener("storage", handler);
    };
  }, []);

  return features;
}
