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
    <aside className="w-64 bg-slate-900 h-screen p-6 border-r border-slate-800 hidden md:block flex flex-col overflow-hidden">
      <h2 className="text-xl font-semibold mb-8 text-slate-200 flex-shrink-0">
        AI Dashboard
      </h2>

      <nav className="space-y-3 flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin">
        {item("/", "Agent Console")}
        {item("/monitor", "Monitoring")}
        {item("/logs", "Logs")}
        {item("/cicd", "🚀 CI/CD")}
        {item("/debugger", "🔍 AI Debugger")}
        {item("/audit", "📋 Audit Trail")}
        {item("/backup", "💾 Backup")}
        {item("/incidents", "🚨 Incidents")}
        {item("/workflows", "⚙️ Workflows")}
        {item("/visualization", "📊 Visualization")}
        {item("/security", "🔒 Security (SIEM/SOC)")}
        {item("/knowledge", "📚 Knowledge Base")}
        {item("/tenants", "🏢 Tenants")}
        {item("/billing", "💳 Billing")}
        {item("/approvals", "Approvals")}
        {item("/settings", "Settings")}
        {item("/tools", "Tools")}
        
        {/* New Modules */}
        <div className="pt-4 mt-4 border-t border-slate-800">
          <h3 className="text-sm font-semibold text-slate-400 mb-2">Advanced Modules</h3>
          {item("/abac", "🛡️ ABAC Access Control")}
          {item("/threat-detection", "🤖 AI Threat Detection")}
          {item("/log-timeline", "📈 Intelligent Log Timeline")}
          {item("/config-drift", "⚙️ Config Drift")}
          {item("/cost-analyzer", "💰 Cost Analyzer")}
          {item("/user-behavior", "👤 User Behavior")}
          {item("/global-search", "🔍 Global Search")}
          {item("/snapshots", "📸 Snapshots & Rollback")}
          {item("/incident-center", "🎯 Incident Command Center")}
          {item("/secrets", "🔐 Secret Management")}
          {item("/service-dependency", "🔗 Service Dependency")}
          {item("/kernel-metrics", "⚡ Kernel Metrics")}
          {item("/hardening", "🔒 Auto-Hardening")}
          {item("/shadow-deploy", "👻 Shadow Deployment")}
          {item("/performance-tuner", "🎛️ Performance Tuner")}
          {item("/behavior-alerts", "🚨 Behavior Alerts")}
          {item("/blueprints", "📋 Blueprint Generator")}
          {item("/code-review", "🔍 Code Review")}
          {item("/plugins", "🧩 Plugin Store")}
          {item("/workflow-builder", "🔧 Workflow Builder")}
          {item("/agent-mesh", "🌐 Agent Mesh")}
          {item("/digital-twin", "🌍 Digital Twin")}
        </div>
      </nav>
    </aside>
  );
}
