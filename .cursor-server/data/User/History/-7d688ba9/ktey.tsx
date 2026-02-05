"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  Building2,
  Users,
  CreditCard,
  TrendingUp,
  FileText,
  AlertTriangle,
  LogOut,
  Settings,
} from "lucide-react";

interface MenuItem {
  href: string;
  label: string;
  icon: React.ReactNode;
}

export default function CRMSidebar() {
  const path = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const menuItems: MenuItem[] = [
    { href: "/crm", label: "Dashboard", icon: <LayoutDashboard className="w-5 h-5" /> },
    { href: "/crm/tenants", label: "Tenants", icon: <Building2 className="w-5 h-5" /> },
    { href: "/crm/users", label: "Users", icon: <Users className="w-5 h-5" /> },
    { href: "/crm/subscriptions", label: "Subscription Plans", icon: <CreditCard className="w-5 h-5" /> },
    { href: "/crm/analytics", label: "Analytics", icon: <TrendingUp className="w-5 h-5" /> },
    { href: "/crm/audit", label: "Audit Logs", icon: <FileText className="w-5 h-5" /> },
    { href: "/crm/incidents", label: "Incidents", icon: <AlertTriangle className="w-5 h-5" /> },
  ];

  const isActive = (href: string) => {
    if (!mounted) return false;
    if (href === "/crm") return path === "/crm";
    return path.startsWith(href);
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    window.location.href = "/crm/login";
  };

  return (
    <aside
      className="w-[260px] bg-sw-bg-sidebar h-screen border-r border-sw-border flex flex-col overflow-hidden"
      suppressHydrationWarning
    >
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-5 border-b border-sw-border">
        <Link href="/crm" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-sw-blue to-sw-teal flex items-center justify-center">
            <Building2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-sw-text-strong tracking-tight">
              Shiftwave
            </h2>
            <p className="text-xs text-sw-text-muted">CRM</p>
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
                    ? "bg-sw-blue text-white shadow-sm"
                    : "text-sw-text-muted hover:text-sw-text hover:bg-sw-bg-hover"
                }`}
              >
                <span className={`transition-colors ${
                  active ? "text-white" : "text-sw-text-muted group-hover:text-sw-blue"
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
      <div className="flex-shrink-0 px-4 py-4 border-t border-sw-border space-y-1">
        <Link
          href="/crm/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sw-text-muted hover:text-sw-text hover:bg-sw-bg-hover"
        >
          <Settings className="w-5 h-5" />
          <span className="text-sm font-medium">Settings</span>
        </Link>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sw-text-muted hover:text-sw-danger hover:bg-red-50 dark:hover:bg-red-950/20"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
}

