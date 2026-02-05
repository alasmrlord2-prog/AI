// components/TopNav.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Search, Bell, HelpCircle, Settings, ChevronDown, Menu } from "lucide-react";

type TopNavProps = {
  user?: string;
  onServicesClick?: () => void;
};

export default function TopNav({ user = "admin@shiftwave.ai", onServicesClick }: TopNavProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest(".user-menu")) {
        setMenuOpen(false);
      }
    };

    if (menuOpen) {
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }
  }, [menuOpen]);

  // Keyboard shortcut for search (Alt+S)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key === "s") {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement;
        if (searchInput) {
          searchInput.focus();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <header className="w-full bg-[#111827] text-white h-14 flex items-center px-4 border-b border-gray-700 flex-shrink-0 z-30">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <img
          src="/shiftwave-logo.svg"
          alt="SHIFTWAVE Logo"
          className="w-7 h-7 flex-shrink-0"
        />
        <span className="font-semibold text-lg tracking-wide">SHIFTWAVE</span>
      </div>

      {/* Services Button */}
      <button
        onClick={onServicesClick}
        className="ml-4 px-3 py-1.5 text-sm rounded-md border border-gray-600 bg-[#1f2937] hover:bg-[#374151] transition-colors flex items-center gap-2"
      >
        <Menu className="w-4 h-4" />
        <span>Services</span>
      </button>

      {/* Search */}
      <div className="flex-1 flex justify-center px-6">
        <div className="relative w-full max-w-xl">
          <input
            type="text"
            placeholder="Search"
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
            className={`w-full bg-[#1f2937] h-9 rounded-md pl-10 pr-16 text-sm outline-none border transition ${
              searchFocused ? "border-gray-400" : "border-gray-600"
            }`}
          />
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <span className="absolute right-3 top-2 text-gray-500 text-[11px]">Alt+S</span>
        </div>
      </div>

      {/* Right icons */}
      <div className="flex items-center gap-4">
        <button
          className="hover:text-gray-300 transition-colors"
          title="Notifications"
        >
          <Bell className="w-5 h-5" />
        </button>
        <button
          className="hover:text-gray-300 transition-colors"
          title="Help & Support"
        >
          <HelpCircle className="w-5 h-5" />
        </button>
        <button
          className="hover:text-gray-300 transition-colors"
          title="Settings"
        >
          <Settings className="w-5 h-5" />
        </button>

        {/* User Menu */}
        <div className="relative user-menu">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-1 hover:text-gray-300 transition-colors"
          >
            <span className="text-sm">{user}</span>
            <ChevronDown className={`w-4 h-4 transition-transform ${menuOpen ? "rotate-180" : ""}`} />
          </button>
          {menuOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white text-black rounded-md shadow-lg border border-gray-200 z-50">
              <div className="p-2 text-xs text-gray-500 border-b border-gray-200">Account</div>
              <Link
                href="/profile"
                className="block px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                Profile
              </Link>
              <Link
                href="/settings"
                className="block px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                Settings
              </Link>
              <Link
                href="/billing"
                className="block px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                Billing
              </Link>
              <div className="border-t border-gray-200"></div>
              <button
                className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                onClick={() => {
                  localStorage.removeItem("auth_token");
                  window.location.href = "/login";
                }}
              >
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

