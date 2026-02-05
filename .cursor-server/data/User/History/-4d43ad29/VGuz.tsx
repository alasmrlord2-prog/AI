// components/ServicesDrawer.tsx
"use client";

import Link from "next/link";
import { SERVICES, ServiceItem } from "@/config/services";
import { X } from "lucide-react";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  favorites: string[];
  toggleFavorite: (id: string) => void;
};

export default function ServicesDrawer({
  isOpen,
  onClose,
  favorites,
  toggleFavorite,
}: Props) {
  const drawerBase =
    "fixed top-0 left-0 h-full bg-sw-bg-sidebar shadow-xl border-r border-sw-border transition-transform duration-200 z-50";

  return (
    <>
      {/* Background overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-40 backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      <div
        className={`${drawerBase} ${
          isOpen ? "translate-x-0 w-80" : "-translate-x-full w-80"
        }`}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-sw-border">
          <h2 className="font-semibold text-lg text-sw-text-strong">All Services</h2>
          <button
            onClick={onClose}
            className="text-sw-text-muted hover:text-sw-text transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-6 overflow-y-auto h-[calc(100%-64px)] sidebar-scroll">
          {/* Favorites section */}
          {favorites.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-sw-text-muted mb-2 uppercase tracking-wider">
                Favorites
              </h3>
              <div className="space-y-1">
                {SERVICES.flatMap((c) => c.items)
                  .filter((i) => favorites.includes(i.id))
                  .map((item) => (
                    <ServiceRow
                      key={item.id}
                      item={item}
                      isFavorite={true}
                      onToggleFavorite={toggleFavorite}
                      onNavigate={onClose}
                    />
                  ))}
              </div>
            </div>
          )}

          {/* Categories */}
          {SERVICES.map((cat) => (
            <div key={cat.category}>
              <h3 className="text-xs font-semibold text-sw-text-muted mb-2 uppercase tracking-wider">
                {cat.category}
              </h3>
              <div className="space-y-1">
                {cat.items.map((item) => (
                  <ServiceRow
                    key={item.id}
                    item={item}
                    isFavorite={favorites.includes(item.id)}
                    onToggleFavorite={toggleFavorite}
                    onNavigate={onClose}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

type RowProps = {
  item: ServiceItem;
  isFavorite: boolean;
  onToggleFavorite: (id: string) => void;
  onNavigate: () => void;
};

function ServiceRow({ item, isFavorite, onToggleFavorite, onNavigate }: RowProps) {
  return (
    <div className="flex items-center justify-between group">
      <Link
        href={item.href}
        onClick={onNavigate}
        className="flex items-center gap-2 px-2 py-1.5 rounded-md text-sm hover:bg-sw-bg-hover flex-1 transition-colors"
      >
        <span className="text-base w-6 text-center">{item.icon}</span>
        <span className="text-sw-text">{item.name}</span>
      </Link>
      <button
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          onToggleFavorite(item.id);
        }}
        className="ml-1 text-xs px-1 text-yellow-500 hover:text-yellow-600 transition-colors"
        title={isFavorite ? "Remove from favorites" : "Add to favorites"}
      >
        {isFavorite ? "★" : "☆"}
      </button>
    </div>
  );
}

