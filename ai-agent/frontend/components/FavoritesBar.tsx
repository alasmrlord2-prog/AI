// components/FavoritesBar.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getAllServices } from "@/config/services";
import type { ServiceItem } from "@/config/services";

type Props = {
  favorites: string[];
};

export default function FavoritesBar({ favorites }: Props) {
  const [allServices, setAllServices] = useState<ServiceItem[]>([]);
  
  useEffect(() => {
    getAllServices().then(setAllServices).catch(console.error);
  }, []);
  
  const favItems = allServices.filter((item) => favorites.includes(item.id));

  if (favItems.length === 0) return null;

  return (
    <div className="flex items-center gap-2 px-4 py-2 border-b border-sw-border bg-sw-bg-card shadow-sm z-20">
      <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin">
        {favItems.map((s) => (
          <Link
            key={s.id}
            href={s.href}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm border border-sw-border bg-sw-bg-soft hover:bg-sw-bg-hover transition whitespace-nowrap flex-shrink-0"
          >
            <span className="text-base">{s.icon}</span>
            <span className="font-medium text-sw-text">{s.name}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

