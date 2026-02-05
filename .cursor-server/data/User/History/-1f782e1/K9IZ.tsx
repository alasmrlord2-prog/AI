"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  ChevronDown,
  ChevronRight,
  LayoutDashboard,
  Terminal,
  Search,
  Bug,
  Activity,
  FileText,
  AlertTriangle,
  AlertCircle,
  Brain,
  Shield,
  Eye,
  Network,
  Code,
  Workflow,
  Layers,
  Package,
  FileCode,
  Settings,
  Building2,
  CreditCard,
  CheckCircle2,
  BookOpen,
  FileCheck,
  GitBranch,
  Rocket,
  Cloud,
  Database,
  DollarSign,
  Lock,
  Scan,
  HardDrive,
} from "lucide-react";

interface MenuItem {
  href: string;
  label: string;
  icon?: React.ReactNode;
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
        { href: "/", label: "Dashboard", icon: <LayoutDashboard className="w-4 h-4" /> },
        { href: "/", label: "Agent Console", icon: <Terminal className="w-4 h-4" /> },
        { href: "/global-search", label: "Global Search", icon: <Search className="w-4 h-4" /> },
        { href: "/debugger", label: "AI Debugger", icon: <Bug className="w-4 h-4" /> },
      ],
    },
    {
      title: "OBSERVABILITY",
      items: [
        {
          href: "/monitoring",
          label: "Monitoring",
          icon: <Activity className="w-4 h-4" />,
          children: [
            { href: "/monitoring", label: "System Metrics", icon: <Activity className="w-3.5 h-3.5" /> },
            { href: "/monitoring?tab=kernel", label: "Kernel Metrics", icon: <Activity className="w-3.5 h-3.5" /> },
            { href: "/monitoring?tab=network", label: "Network", icon: <Network className="w-3.5 h-3.5" /> },
            { href: "/monitoring?tab=performance", label: "Performance Tuner", icon: <Settings className="w-3.5 h-3.5" /> },
            { href: "/monitoring?tab=dependency", label: "Service Dependency", icon: <Layers className="w-3.5 h-3.5" /> },
            { href: "/visualization", label: "Visualization", icon: <Eye className="w-3.5 h-3.5" /> },
          ],
        },
        { href: "/logs", label: "Logs", icon: <FileText className="w-4 h-4" /> },
        { href: "/incidents", label: "Incidents", icon: <AlertTriangle className="w-4 h-4" /> },
        { href: "/incident-center", label: "Incident Center", icon: <AlertCircle className="w-4 h-4" /> },
      ],
    },
    {
      title: "AI & AUTOMATION",
      items: [
        { href: "/tools", label: "AI Tools", icon: <Brain className="w-4 h-4" /> },
        { href: "/threat-detection", label: "Threat Detection", icon: <Scan className="w-4 h-4" /> },
        { href: "/abac", label: "ABAC", icon: <Shield className="w-4 h-4" /> },
        { href: "/behavior-alerts", label: "Behavior Alerts", icon: <Eye className="w-4 h-4" /> },
        { href: "/digital-twin", label: "Digital Twin", icon: <Network className="w-4 h-4" /> },
        { href: "/agent-mesh", label: "Agent Mesh", icon: <Network className="w-4 h-4" /> },
        { href: "/code-review", label: "Code Review", icon: <Code className="w-4 h-4" /> },
        { href: "/workflow-builder", label: "Workflow Builder", icon: <Workflow className="w-4 h-4" /> },
        { href: "/workflows", label: "Workflows", icon: <Workflow className="w-4 h-4" /> },
        { href: "/snapshots", label: "Snapshots", icon: <HardDrive className="w-4 h-4" /> },
        { href: "/blueprints", label: "Blueprint Generator", icon: <FileCode className="w-4 h-4" /> },
        { href: "/plugins", label: "Plugin Store", icon: <Package className="w-4 h-4" /> },
      ],
    },
    {
      title: "SECURITY",
      items: [
        { href: "/security", label: "Security Center", icon: <Shield className="w-4 h-4" /> },
        { href: "/siem", label: "SIEM/SOC", icon: <Shield className="w-4 h-4" /> },
        { href: "/secrets", label: "Secrets Manager", icon: <Lock className="w-4 h-4" /> },
        { href: "/hardening", label: "Auto-Hardening", icon: <Shield className="w-4 h-4" /> },
      ],
    },
    {
      title: "DEVOPS",
      items: [
        { href: "/cicd", label: "CI/CD", icon: <GitBranch className="w-4 h-4" /> },
        { href: "/cicd?tab=deployments", label: "Deployments", icon: <Rocket className="w-4 h-4" /> },
        { href: "/shadow-deploy", label: "Shadow Deployment", icon: <Cloud className="w-4 h-4" /> },
        { href: "/backup", label: "Backup & Restore", icon: <Database className="w-4 h-4" /> },
        { href: "/cost-analyzer", label: "Cost Analyzer", icon: <DollarSign className="w-4 h-4" /> },
      ],
    },
    {
      title: "PLATFORM",
      items: [
        { href: "/tenants", label: "Tenants", icon: <Building2 className="w-4 h-4" /> },
        { href: "/billing", label: "Billing", icon: <CreditCard className="w-4 h-4" /> },
        { href: "/approvals", label: "Approvals", icon: <CheckCircle2 className="w-4 h-4" /> },
        { href: "/knowledge", label: "Knowledge Base", icon: <BookOpen className="w-4 h-4" /> },
        { href: "/audit", label: "Audit Trail", icon: <FileCheck className="w-4 h-4" /> },
        { href: "/settings", label: "Settings", icon: <Settings className="w-4 h-4" /> },
      ],
    },
  ];

  const isActive = (href: string) => {
    if (!mounted) return false;
    if (href === "/") return path === "/";
    return path.startsWith(href);
  };

  const toggleGroup = (groupTitle: string, itemLabel: string) => {
    const key = `${groupTitle}-${itemLabel}`.toLowerCase();
    setExpandedGroups((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const isGroupExpanded = (groupTitle: string, itemLabel: string) => {
    const key = `${groupTitle}-${itemLabel}`.toLowerCase();
    return expandedGroups[key] ?? false;
  };

  const renderMenuItem = (
    item: MenuItem,
    level: number = 0,
    groupTitle: string,
    parentPath: string = ""
  ) => {
    const active = isActive(item.href);
    const hasChildren = item.children && item.children.length > 0;
    const groupKey = `${groupTitle}-${item.label}`.toLowerCase();
    const isExpanded = isGroupExpanded(groupTitle, item.label);
    
    // Create a truly unique key using group title, label, href, and parent path
    const uniqueKey = `${groupTitle}-${parentPath}-${item.label}-${item.href}-${level}`;

    if (hasChildren) {
      return (
        <div key={uniqueKey} className="space-y-1">
          <button
            onClick={() => toggleGroup(groupTitle, item.label)}
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
              {item.children?.map((child, index) => 
                renderMenuItem(child, level + 1, groupTitle, `${item.label}-${index}`)
              )}
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
              {group.items.map((item, index) => 
                renderMenuItem(item, 0, group.title, `root-${index}`)
              )}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}
