"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

interface ToolItem {
  href: string;
  icon: string;
  title: string;
  status?: string;
  count?: number;
}

export default function ToolsPage() {
  const router = useRouter();

  const tools: ToolItem[] = [
    { href: "/threat-detection", icon: "🤖", title: "Threat Detection", status: "Active", count: 3 },
    { href: "/abac", icon: "🛡️", title: "ABAC", status: "Active", count: 12 },
    { href: "/behavior-alerts", icon: "🚨", title: "Behavior Alerts", status: "Active", count: 1 },
    { href: "/digital-twin", icon: "🌍", title: "Digital Twin", status: "Active" },
    { href: "/agent-mesh", icon: "🌐", title: "Agent Mesh", status: "Active" },
    { href: "/code-review", icon: "🔍", title: "Code Review", status: "Active" },
    { href: "/workflow-builder", icon: "🔧", title: "Workflow Builder", status: "Active" },
    { href: "/workflows", icon: "⚙️", title: "Workflows", status: "Active", count: 5 },
    { href: "/snapshots", icon: "📸", title: "Snapshots", status: "Active", count: 8 },
    { href: "/blueprints", icon: "📋", title: "Blueprint Generator", status: "Active" },
    { href: "/plugins", icon: "🧩", title: "Plugins", status: "Active", count: 15 },
    { href: "/global-search", icon: "🔍", title: "Global Search", status: "Active" },
  ];

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold mb-2">AI Tools</h1>
            <p className="text-sm md:text-base text-slate-400">Access all AI-powered automation and security tools</p>
          </div>

          {/* Grid 3x4 like Azure Portal */}
          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4">
            {tools.map((tool, index) => (
              <Link
                key={`tool-${tool.href}-${tool.title}-${index}`}
                href={tool.href}
                prefetch={true}
                onMouseEnter={() => router.prefetch(tool.href)}
              >
                <Card className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-all cursor-pointer h-full">
                  <CardContent className="p-4 md:p-6">
                    <div className="flex flex-col items-center text-center space-y-3 md:space-y-4">
                      {/* Icon */}
                      <div className="text-3xl md:text-5xl">{tool.icon}</div>
                      
                      {/* Title */}
                      <div className="font-semibold text-sm md:text-lg">{tool.title}</div>
                      
                      {/* Status / Count */}
                      <div className="flex items-center gap-2 flex-wrap justify-center">
                        {tool.status && (
                          <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                            {tool.status}
                          </span>
                        )}
                        {tool.count !== undefined && (
                          <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                            {tool.count}
                          </span>
                        )}
                      </div>
                      
                      {/* Open Button */}
                      <button className="w-full mt-2 px-3 md:px-4 py-1.5 md:py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs md:text-sm rounded transition-colors">
                        Open
                      </button>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
