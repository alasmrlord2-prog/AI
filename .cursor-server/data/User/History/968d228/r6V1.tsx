"use client";

import { useState, useEffect } from "react";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { User, ChevronDown } from "lucide-react";

export default function CRMHeader() {
  const [user, setUser] = useState<{ email?: string; full_name?: string } | null>(null);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  useEffect(() => {
    // Fetch user info from API or localStorage
    const token = localStorage.getItem("auth_token");
    if (token) {
      // TODO: Fetch user info from API
      setUser({ email: "admin@shiftwave.com", full_name: "CRM Admin" });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <header className="h-16 bg-sw-bg-card border-b border-sw-border flex items-center justify-between px-6 shadow-sm">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-sw-text-strong">Shiftwave CRM</h1>
      </div>

      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <ThemeToggle />

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-sw-bg-hover transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sw-blue to-sw-teal flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="hidden md:block text-left">
              <div className="text-sm font-medium text-sw-text-strong">
                {user?.full_name || "Admin"}
              </div>
              <div className="text-xs text-sw-text-muted">
                {user?.email || "admin@shiftwave.com"}
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-sw-text-muted" />
          </button>

          {showProfileMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowProfileMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-56 bg-sw-bg-card border border-sw-border rounded-lg shadow-lg z-20">
                <div className="p-4 border-b border-sw-border">
                  <div className="text-sm font-medium text-sw-text-strong">
                    {user?.full_name || "Admin"}
                  </div>
                  <div className="text-xs text-sw-text-muted mt-1">
                    {user?.email || "admin@shiftwave.com"}
                  </div>
                </div>
                <div className="p-2">
                  <button
                    onClick={() => {
                      setShowProfileMenu(false);
                      window.location.href = "/crm/settings";
                    }}
                    className="w-full text-left px-3 py-2 text-sm text-sw-text hover:bg-sw-bg-hover rounded-lg transition-colors"
                  >
                    Profile Settings
                  </button>
                  <button
                    onClick={() => {
                      localStorage.removeItem("auth_token");
                      window.location.href = "/crm/login";
                    }}
                    className="w-full text-left px-3 py-2 text-sm text-sw-text hover:bg-sw-bg-hover rounded-lg transition-colors text-sw-danger"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

