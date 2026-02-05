// components/TopNav.tsx
"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Search, Bell, HelpCircle, Settings, ChevronDown, Menu, Sun, Moon, Zap, Globe } from "lucide-react";
import { getAllServices, ServiceItem } from "@/config/services";

type TopNavProps = {
  user?: string;
  onServicesClick?: () => void;
  locale?: "ar" | "en";
  setLocale?: (locale: "ar" | "en") => void;
};

// Theme Toggle Button for TopNav
function ThemeToggleButton() {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem("theme");
    const shouldBeDark = saved === "dark";
    setIsDark(shouldBeDark);
    
    if (shouldBeDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, []);

  const toggleTheme = () => {
    const html = document.documentElement;
    const currentlyDark = html.classList.contains("dark");
    const newIsDark = !currentlyDark;
    
    if (newIsDark) {
      html.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      html.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
    
    setIsDark(newIsDark);
    void html.offsetHeight;
  };

  if (!mounted) {
    return (
      <button className="hover:text-gray-300 transition-colors" title="Toggle theme">
        <Sun className="w-5 h-5" />
      </button>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className="hover:text-gray-300 transition-colors"
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {isDark ? (
        <Sun className="w-5 h-5" />
      ) : (
        <Moon className="w-5 h-5" />
      )}
    </button>
  );
}

export default function TopNav({ 
  user = "admin@shiftwave.ai", 
  onServicesClick,
  locale: propLocale,
  setLocale: propSetLocale 
}: TopNavProps) {
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const [quickAccessOpen, setQuickAccessOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<ServiceItem[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const [internalLocale, setInternalLocale] = useState<"ar" | "en">("en");
  
  // Use props if provided, otherwise use internal state
  const locale = propLocale ?? internalLocale;
  const handleSetLocale = propSetLocale ?? setInternalLocale;
  
  // Memoize allServices to prevent infinite loop
  const allServices = useMemo(() => getAllServices(), []);

  // Quick Access items - same as page.tsx
  const quickAccessItems = [
    { id: "threat-detection", href: "/threat-detection", icon: "🤖", label: "Threat Detection" },
    { id: "abac", href: "/abac", icon: "🛡️", label: "ABAC" },
    { id: "digital-twin", href: "/digital-twin", icon: "🌍", label: "Digital Twin" },
    { id: "cicd", href: "/cicd", icon: "🚀", label: "CI/CD" },
    { id: "agent-mesh", href: "/agent-mesh", icon: "🌐", label: "Agent Mesh" },
    { id: "code-review", href: "/code-review", icon: "🔍", label: "Code Review" },
    { id: "snapshots", href: "/snapshots", icon: "📸", label: "Snapshots" },
    { id: "workflow-builder", href: "/workflow-builder", icon: "🔧", label: "Workflow Builder" },
    { id: "blueprints", href: "/blueprints", icon: "📋", label: "Blueprint" },
    { id: "plugins", href: "/plugins", icon: "🧩", label: "Plugins" },
    { id: "logs", href: "/logs", icon: "📋", label: "Logs" },
    { id: "visualization", href: "/visualization", icon: "📊", label: "Visualization" },
  ];

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest(".user-menu")) {
        setMenuOpen(false);
      }
      if (!target.closest(".quick-access-menu")) {
        setQuickAccessOpen(false);
      }
    };

    if (menuOpen || quickAccessOpen) {
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }
  }, [menuOpen, quickAccessOpen]);

  // Search functionality
  useEffect(() => {
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const filtered = allServices.filter((service) =>
        service.name.toLowerCase().includes(query) ||
        service.id.toLowerCase().includes(query) ||
        service.href.toLowerCase().includes(query)
      );
      setSearchResults(filtered.slice(0, 8)); // Limit to 8 results
      setShowSearchResults(true);
    } else {
      setSearchResults([]);
      setShowSearchResults(false);
    }
  }, [searchQuery, allServices]);

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchResults(false);
      }
    };

    if (showSearchResults) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [showSearchResults]);

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

  const handleSearchSelect = (service: ServiceItem) => {
    setSearchQuery("");
    setShowSearchResults(false);
    router.push(service.href);
  };

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

      {/* Quick Access Button */}
      <div className="relative quick-access-menu">
        <button
          onClick={() => setQuickAccessOpen(!quickAccessOpen)}
          className="ml-2 px-3 py-1.5 text-sm rounded-md border border-gray-600 bg-[#1f2937] hover:bg-[#374151] transition-colors flex items-center gap-2"
        >
          <Zap className="w-4 h-4" />
          <span>Quick Access</span>
          <ChevronDown className={`w-3 h-3 transition-transform ${quickAccessOpen ? "rotate-180" : ""}`} />
        </button>
        {quickAccessOpen && (
          <div className="absolute top-full left-0 mt-1 w-80 bg-[#1f2937] border border-gray-600 rounded-md shadow-xl z-50 max-h-[500px] overflow-y-auto">
            <div className="p-3 border-b border-gray-700">
              <h3 className="text-sm font-semibold text-white">Quick Access</h3>
            </div>
            <div className="p-3 grid grid-cols-3 gap-2">
              {quickAccessItems.map((item) => (
                <Link
                  key={item.id}
                  href={item.href}
                  onClick={() => setQuickAccessOpen(false)}
                  className="flex flex-col items-center justify-center gap-2 p-3 rounded-md bg-[#111827] hover:bg-[#374151] transition-colors border border-gray-700 hover:border-gray-600"
                >
                  <span className="text-2xl">{item.icon}</span>
                  <span className="text-xs text-white text-center font-medium">{item.label}</span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Search */}
      <div className="flex-1 flex justify-center px-6">
        <div className="relative w-full max-w-xl" ref={searchRef}>
          <input
            type="text"
            placeholder="Search services..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => {
              setSearchFocused(true);
              if (searchQuery.trim()) {
                setShowSearchResults(true);
              }
            }}
            onBlur={() => {
              setSearchFocused(false);
              // Delay hiding results to allow click on results
              setTimeout(() => setShowSearchResults(false), 200);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && searchResults.length > 0) {
                handleSearchSelect(searchResults[0]);
              }
            }}
            className={`w-full bg-[#1f2937] h-9 rounded-md pl-10 pr-16 text-sm outline-none border transition text-white placeholder-gray-400 ${
              searchFocused ? "border-gray-400" : "border-gray-600"
            }`}
          />
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <span className="absolute right-3 top-2 text-gray-500 text-[11px]">Alt+S</span>

          {/* Search Results Dropdown */}
          {showSearchResults && searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-[#1f2937] border border-gray-600 rounded-md shadow-xl z-50 max-h-96 overflow-y-auto">
              <div className="p-2">
                {searchResults.map((service) => (
                  <button
                    key={service.id}
                    onClick={() => handleSearchSelect(service)}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-[#374151] transition-colors text-left text-white"
                  >
                    <span className="text-lg flex-shrink-0">{service.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-white">{service.name}</div>
                      <div className="text-xs text-gray-400 truncate">{service.href}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {showSearchResults && searchQuery.trim() && searchResults.length === 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-[#1f2937] border border-gray-600 rounded-md shadow-xl z-50 p-4">
              <div className="text-sm text-gray-400 text-center">
                No services found for "{searchQuery}"
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right icons */}
      <div className="flex items-center gap-4">
        {/* Language Toggle */}
        <button
          onClick={() => handleSetLocale(locale === "ar" ? "en" : "ar")}
          className="hover:text-gray-300 transition-colors flex items-center gap-1.5 px-2 py-1 rounded text-sm"
          title={locale === "ar" ? "Switch to English" : "التبديل إلى العربية"}
        >
          <Globe className="w-4 h-4" />
          <span className="text-xs">{locale === "ar" ? "EN" : "AR"}</span>
        </button>
        
        {/* Theme Toggle - Custom styled for TopNav */}
        <ThemeToggleButton />
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

