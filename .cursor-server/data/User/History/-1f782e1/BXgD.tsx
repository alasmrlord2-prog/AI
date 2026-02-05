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
    {
      title: "IAM",
      items: [
        { href: "/iam/roles", label: "Roles", icon: <Shield className="w-4 h-4" /> },
        { href: "/iam/permissions", label: "Permissions", icon: <Lock className="w-4 h-4" /> },
        { href: "/iam/policies", label: "Policies", icon: <Shield className="w-4 h-4" /> },
        { href: "/iam/access-control", label: "Access Control", icon: <Eye className="w-4 h-4" /> },
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
        <div key={uniqueKey} className="space-y-0.5">
          <button
            onClick={() => toggleGroup(groupTitle, item.label)}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-sw-btn transition-all duration-200 text-left group ${
              active
                ? "bg-gradient-to-r from-sw-blue to-sw-teal text-white shadow-sm"
                : "text-sw-text-muted hover:text-sw-text hover:bg-sw-bg-hover"
            }`}
            style={{ paddingLeft: `${level * 12 + 12}px` }}
          >
            <span className="flex items-center gap-2.5">
              {item.icon && (
                <span className={`transition-colors ${
                  active ? "text-white" : "text-sw-text-muted group-hover:text-sw-text"
                }`}>
                  {item.icon}
                </span>
              )}
              <span className="text-sm font-medium">{item.label}</span>
            </span>
            <span className={`transition-transform duration-200 ${
              isExpanded ? "rotate-0" : "-rotate-90"
            }`}>
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </span>
          </button>
          {isExpanded && (
            <div className="ml-2 space-y-0.5 mt-0.5 border-l border-sw-border pl-2">
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
        className={`block px-3 py-2 rounded-sw-btn transition-all duration-200 group ${
          active
            ? "bg-gradient-to-r from-sw-blue to-sw-teal text-white shadow-sm"
            : "text-sw-text-muted hover:text-sw-text hover:bg-sw-bg-hover"
        }`}
        style={{ paddingLeft: `${level * 12 + 12}px` }}
      >
        <span className="flex items-center gap-2.5">
          {item.icon && (
            <span className={`transition-colors ${
              active ? "text-white" : "text-sw-text-muted group-hover:text-sw-text"
            }`}>
              {item.icon}
            </span>
          )}
          <span className="text-sm font-medium">{item.label}</span>
        </span>
      </Link>
    );
  };

  return (
    <aside
      className="w-64 bg-sw-bg-sidebar h-screen border-r border-sw-border hidden md:flex flex-col overflow-hidden"
      suppressHydrationWarning
    >
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-5 border-b border-sw-border">
        <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer">
          <img 
            src="/shiftwave-logo.svg" 
            alt="SHIFTWAVE Logo" 
            className="w-10 h-10 flex-shrink-0"
          />
          <h2 className="text-xl font-bold text-sw-text-strong tracking-tight">
            SHIFTWAVE AI
          </h2>
        </Link>
      </div>

      {/* Scrollable Navigation */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden sidebar-scroll px-4 py-4">
        <div className="space-y-6">
          {menuGroups.map((group) => (
            <div key={group.title} className="space-y-1.5">
              <h3 className="text-[10px] font-bold text-sw-text-muted uppercase tracking-wider px-3 py-1.5">
                {group.title}
              </h3>
              <div className="space-y-0.5">
                {group.items.map((item, index) => 
                  renderMenuItem(item, 0, group.title, `root-${index}`)
                )}
              </div>
            </div>
          ))}
        </div>
      </nav>
    </aside>
  );
}
