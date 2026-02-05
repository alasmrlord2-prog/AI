"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const path = usePathname();

  const item = (href: string, label: string) => (
    <Link
      href={href}
      className={`block p-2 rounded ${
        path === href
          ? "bg-slate-800 text-white"
          : "text-slate-300 hover:text-white"
      }`}
    >
      {label}
    </Link>
  );

  return (
    <aside className="w-64 bg-slate-900 h-screen p-6 border-r border-slate-800 hidden md:block">
      <h2 className="text-xl font-semibold mb-8 text-slate-200">
        AI Dashboard
      </h2>

      <nav className="space-y-3">
        {item("/", "Agent Console")}
        {item("/monitor", "Monitoring")}
        {item("/logs", "Logs")}
        {item("/security", "Security")}
        {item("/settings", "Settings")}
        {item("/tools", "Tools")}
      </nav>
    </aside>
  );
}
