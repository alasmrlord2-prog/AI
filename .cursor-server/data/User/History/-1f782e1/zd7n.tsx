"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

interface MenuItem {
  href: string;
  label: string;
  icon?: string;
  children?: MenuItem[];
}

interface MenuGroup {
  title: string;
  items: MenuItem[];
}

export default function Sidebar() {
  const path = usePathname();
  const [mounted, setMounted] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    observability: true,
    ai: true,
  });

  useEffect(() => {
    setMounted(true);
  }, []);

  const menuGroups: MenuGroup[] = [
    {
      title: "CORE",
      items: [
        { href: "/", label: "Dashboard" },
        { href: "/", label: "Agent Console" },
        { href: "/global-search", label: "Global Search" },
        { href: "/debugger", label: "AI Debugger" },
      ],
    },
    {
      title: "OBSERVABILITY",
      items: [
        {
          href: "/monitoring",
          label: "Monitoring",
          children: [
            { href: "/monitoring", label: "System Metrics" },
            { href: "/monitoring?tab=kernel", label: "Kernel Metrics" },
            { href: "/monitoring?tab=network", label: "Network" },
            { href: "/monitoring?tab=performance", label: "Performance Tuner" },
            { href: "/monitoring?tab=dependency", label: "Service Dependency" },
            { href: "/visualization", label: "Visualization" },
          ],
        },
        { href: "/logs", label: "Logs" },
        { href: "/incidents", label: "Incidents" },
        { href: "/incident-center", label: "Incident Center" },
      ],
    },
    {
      title: "AI & AUTOMATION",
      items: [
        { href: "/tools", label: "AI Tools" },
        { href: "/threat-detection", label: "Threat Detection" },
        { href: "/abac", label: "ABAC" },
        { href: "/behavior-alerts", label: "Behavior Alerts" },
        { href: "/digital-twin", label: "Digital Twin" },
        { href: "/agent-mesh", label: "Agent Mesh" },
        { href: "/code-review", label: "Code Review" },
        { href: "/workflow-builder", label: "Workflow Builder" },
        { href: "/workflows", label: "Workflows" },
        { href: "/snapshots", label: "Snapshots" },
        { href: "/blueprints", label: "Blueprint Generator" },
        { href: "/plugins", label: "Plugin Store" },
      ],
    },
    {
      title: "SECURITY",
      items: [
        { href: "/security", label: "Security Center" },
        { href: "/siem", label: "SIEM/SOC" },
        { href: "/secrets", label: "Secrets Manager" },
        { href: "/hardening", label: "Auto-Hardening" },
      ],
    },
    {
      title: "DEVOPS",
      items: [
        { href: "/cicd", label: "CI/CD" },
        { href: "/cicd?tab=deployments", label: "Deployments" },
        { href: "/shadow-deploy", label: "Shadow Deployment" },
        { href: "/backup", label: "Backup & Restore" },
        { href: "/cost-analyzer", label: "Cost Analyzer" },
      ],
    },
    {
      title: "PLATFORM",
      items: [
        { href: "/tenants", label: "Tenants" },
        { href: "/billing", label: "Billing" },
        { href: "/approvals", label: "Approvals" },
        { href: "/knowledge", label: "Knowledge Base" },
        { href: "/audit", label: "Audit Trail" },
        { href: "/settings", label: "Settings" },
      ],
    },
  ];

  const isActive = (href: string) => {
    if (!mounted) return false;
    if (href === "/") return path === "/";
    return path.startsWith(href);
  };

  const toggleGroup = (groupTitle: string) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [groupTitle.toLowerCase()]: !prev[groupTitle.toLowerCase()],
    }));
  };

  const renderMenuItem = (item: MenuItem, level: number = 0, groupTitle?: string) => {
    const active = isActive(item.href);
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedGroups[item.label.toLowerCase()] ?? false;
    // Use label + groupTitle as key to ensure uniqueness
    const uniqueKey = `${groupTitle || ''}-${item.label}-${item.href}`;

    if (hasChildren) {
      return (
        <div key={uniqueKey} className="space-y-1">
          <button
            onClick={() => toggleGroup(item.label)}
            className={`w-full flex items-center justify-between p-2 rounded transition-colors text-left ${
              active
                ? "bg-slate-800 text-white"
                : "text-slate-300 hover:text-white hover:bg-slate-800/50"
            }`}
            style={{ paddingLeft: `${level * 12 + 8}px` }}
          >
            <span className="flex items-center gap-2">
              {item.icon && <span>{item.icon}</span>}
              <span>{item.label}</span>
            </span>
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>
          {isExpanded && (
            <div className="ml-4 space-y-1">
              {item.children?.map((child) => renderMenuItem(child, level + 1, groupTitle))}
            </div>
          )}
        </div>
      );
    }

    return (
      <Link
        key={uniqueKey}
        href={item.href}
        className={`block p-2 rounded transition-colors ${
          active
            ? "bg-slate-800 text-white"
            : "text-slate-300 hover:text-white hover:bg-slate-800/50"
        }`}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
      >
        <span className="flex items-center gap-2">
          {item.icon && <span>{item.icon}</span>}
          <span>{item.label}</span>
        </span>
      </Link>
    );
  };

  return (
    <aside
      className="w-64 bg-slate-900 h-screen p-6 border-r border-slate-800 hidden md:block flex flex-col overflow-hidden"
      suppressHydrationWarning
    >
      <h2 className="text-xl font-semibold mb-6 text-slate-200 flex-shrink-0">
        AI Dashboard
      </h2>

      <nav className="space-y-4 flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin">
        {menuGroups.map((group) => (
          <div key={group.title} className="space-y-1">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2 py-1">
              {group.title}
            </h3>
            <div className="space-y-1">
              {group.items.map((item) => renderMenuItem(item))}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}
