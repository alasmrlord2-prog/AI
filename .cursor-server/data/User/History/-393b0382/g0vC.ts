// config/services.ts
// Centralized service configuration for AWS-style navigation

export type ServiceItem = {
  id: string;
  name: string;
  href: string;
  icon?: string;
  iconComponent?: string; // Lucide icon name for dynamic import
};

export type ServiceCategory = {
  category: string;
  items: ServiceItem[];
};

export const SERVICES: ServiceCategory[] = [
  {
    category: "CORE",
    items: [
      { id: "dashboard", name: "Dashboard", href: "/", icon: "📊" },
      { id: "agent-console", name: "Agent Console", href: "/", icon: "💻" },
      { id: "global-search", name: "Global Search", href: "/global-search", icon: "🔍" },
      { id: "debugger", name: "AI Debugger", href: "/debugger", icon: "🐛" },
    ],
  },
  {
    category: "OBSERVABILITY",
    items: [
      { id: "monitoring", name: "Monitoring", href: "/monitoring", icon: "📈" },
      { id: "logs", name: "Logs", href: "/logs", icon: "📋" },
      { id: "incidents", name: "Incidents", href: "/incidents", icon: "⚠️" },
      { id: "incident-center", name: "Incident Center", href: "/incident-center", icon: "🚨" },
      { id: "visualization", name: "Visualization", href: "/visualization", icon: "👁️" },
    ],
  },
  {
    category: "AI & AUTOMATION",
    items: [
      { id: "tools", name: "AI Tools", href: "/tools", icon: "🧠" },
      { id: "threat-detection", name: "Threat Detection", href: "/threat-detection", icon: "🛡️" },
      { id: "abac", name: "ABAC", href: "/abac", icon: "🔐" },
      { id: "behavior-alerts", name: "Behavior Alerts", href: "/behavior-alerts", icon: "👁️" },
      { id: "digital-twin", name: "Digital Twin", href: "/digital-twin", icon: "🌍" },
      { id: "agent-mesh", name: "Agent Mesh", href: "/agent-mesh", icon: "🌐" },
      { id: "code-review", name: "Code Review", href: "/code-review", icon: "🔍" },
      { id: "workflow-builder", name: "Workflow Builder", href: "/workflow-builder", icon: "🔧" },
      { id: "workflows", name: "Workflows", href: "/workflows", icon: "⚡" },
      { id: "snapshots", name: "Snapshots", href: "/snapshots", icon: "📸" },
      { id: "blueprints", name: "Blueprint Generator", href: "/blueprints", icon: "📋" },
      { id: "plugins", name: "Plugin Store", href: "/plugins", icon: "🧩" },
    ],
  },
  {
    category: "SECURITY",
    items: [
      { id: "security", name: "Security Center", href: "/security", icon: "🔒" },
      { id: "siem", name: "SIEM/SOC", href: "/siem", icon: "📊" },
      { id: "secrets", name: "Secrets Manager", href: "/secrets", icon: "🔑" },
      { id: "hardening", name: "Auto-Hardening", href: "/hardening", icon: "🧱" },
    ],
  },
  {
    category: "DEVOPS",
    items: [
      { id: "cicd", name: "CI/CD", href: "/cicd", icon: "🚀" },
      { id: "deployments", name: "Deployments", href: "/cicd?tab=deployments", icon: "🚀" },
      { id: "shadow-deploy", name: "Shadow Deployment", href: "/shadow-deploy", icon: "☁️" },
      { id: "backup", name: "Backup & Restore", href: "/backup", icon: "💾" },
      { id: "cost-analyzer", name: "Cost Analyzer", href: "/cost-analyzer", icon: "💰" },
    ],
  },
  {
    category: "PLATFORM",
    items: [
      { id: "tenants", name: "Tenants", href: "/tenants", icon: "🏢" },
      { id: "billing", name: "Billing", href: "/billing", icon: "💳" },
      { id: "approvals", name: "Approvals", href: "/approvals", icon: "✅" },
      { id: "knowledge", name: "Knowledge Base", href: "/knowledge", icon: "📚" },
      { id: "audit", name: "Audit Trail", href: "/audit", icon: "📝" },
      { id: "settings", name: "Settings", href: "/settings", icon: "⚙️" },
    ],
  },
];

// Helper function to get all services as a flat array
export function getAllServices(): ServiceItem[] {
  return SERVICES.flatMap((cat) => cat.items);
}

// Helper function to find a service by ID
export function getServiceById(id: string): ServiceItem | undefined {
  return getAllServices().find((s) => s.id === id);
}

// Helper function to find a service by href
export function getServiceByHref(href: string): ServiceItem | undefined {
  return getAllServices().find((s) => s.href === href || s.href === href.split("?")[0]);
}

