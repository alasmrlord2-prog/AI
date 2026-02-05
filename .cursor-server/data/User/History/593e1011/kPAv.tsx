"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Shield,
  Key,
  Users,
  Activity,
  Settings,
  LogOut,
  LayoutDashboard,
  Building2,
} from "lucide-react";

interface MenuItem {
  href: string;
  label: string;
  icon: React.ReactNode;
}

export default function AAASidebar() {
  const path = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Use setTimeout to avoid synchronous setState in effect
    setTimeout(() => setMounted(true), 0);
  }, []);

  const menuItems: MenuItem[] = [
    { href: "/aaa", label: "Dashboard", icon: <LayoutDashboard className="w-5 h-5" /> },
    { href: "/aaa/tokens", label: "Tokens", icon: <Key className="w-5 h-5" /> },
    { href: "/aaa/sessions", label: "Sessions", icon: <Activity className="w-5 h-5" /> },
    { href: "/aaa/users", label: "Users", icon: <Users className="w-5 h-5" /> },
    { href: "/aaa/audit", label: "Audit Logs", icon: <Shield className="w-5 h-5" /> },
  ];

  const isActive = (href: string) => {
    if (!mounted) return false;
    if (href === "/aaa") return path === "/aaa";
    return path.startsWith(href);
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    window.location.href = "/aaa/login";
  };

  return (
    <aside
      className="w-[260px] bg-swAuth-surface h-screen border-r border-gray-200 flex flex-col overflow-hidden"
      suppressHydrationWarning
    >
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-5 border-b border-gray-200">
        <Link href="/aaa" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-swAuth-primary to-swAuth-primary/80 flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900 tracking-tight">
              Shiftwave
            </h2>
            <p className="text-xs text-gray-500">AAA</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden sidebar-scroll px-4 py-4">
        <div className="space-y-1">
          {menuItems.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${
                  active
                    ? "bg-swAuth-primary text-white shadow-sm"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                }`}
              >
                <span className={`transition-colors ${
                  active ? "text-white" : "text-gray-500 group-hover:text-swAuth-primary"
                }`}>
                  {item.icon}
                </span>
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="flex-shrink-0 px-4 py-4 border-t border-gray-200 space-y-1">
        <a
          href="http://ai-agent.bankid-sy.com"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-blue-600 hover:text-blue-700 hover:bg-blue-50 border border-blue-200"
        >
          <LayoutDashboard className="w-5 h-5" />
          <span className="text-sm font-medium">AI Dashboard</span>
        </a>
        <a
          href="http://crm.bankid-sy.com"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-gray-600 hover:text-gray-900 hover:bg-gray-50"
        >
          <Building2 className="w-5 h-5" />
          <span className="text-sm font-medium">CRM</span>
        </a>
        <Link
          href="/aaa/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-gray-600 hover:text-gray-900 hover:bg-gray-50"
        >
          <Settings className="w-5 h-5" />
          <span className="text-sm font-medium">Settings</span>
        </Link>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-gray-600 hover:text-swAuth-danger hover:bg-red-50"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
}

