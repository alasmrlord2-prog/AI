"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function AgentMeshPage() {
  const [status, setStatus] = useState<any>(null);
  const [nodes, setNodes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/api/agents/mesh/status", {}, 5000); // 5 second timeout
      setStatus(data);
      setNodes(data.nodes || []);
    } catch (error) {
      console.error("Error loading status:", error);
      setStatus(null);
      setNodes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async () => {
    try {
      await apiRequest("/api/agents/mesh/start", {
        method: "POST",
      });
      loadStatus();
    } catch (error) {
      console.error("Error starting:", error);
      alert(`خطأ في بدء الشبكة: ${error instanceof Error ? error.message : "خطأ غير معروف"}`);
    }
  };

  const handleStop = async () => {
    try {
      await apiRequest("/api/agents/mesh/stop", {
        method: "POST",
      });
      loadStatus();
    } catch (error) {
      console.error("Error stopping:", error);
      alert(`خطأ في إيقاف الشبكة: ${error instanceof Error ? error.message : "خطأ غير معروف"}`);
    }
  };

  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header locale={locale} setLocale={handleSetLocale} />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 scrollbar-thin">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>🌐 Distributed Agent Mesh</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {status && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">الحالة</div>
                        <div className={`text-2xl font-bold mt-1 ${
                          status.running ? "text-green-400" : "text-red-400"
                        }`}>
                          {status.running ? "نشط" : "معطل"}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">إجمالي Nodes</div>
                        <div className="text-2xl font-bold mt-1 text-blue-400">
                          {status.total_nodes || 0}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">Nodes نشطة</div>
                        <div className="text-2xl font-bold mt-1 text-green-400">
                          {status.active_nodes || 0}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">Nodes فاشلة</div>
                        <div className="text-2xl font-bold mt-1 text-red-400">
                          {status.failed_nodes || 0}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                <div className="flex gap-2 mb-4">
                  <Button onClick={handleStart} className="bg-green-600 hover:bg-green-700">
                    بدء الشبكة
                  </Button>
                  <Button onClick={handleStop} className="bg-red-600 hover:bg-red-700">
                    إيقاف الشبكة
                  </Button>
                  <Button onClick={loadStatus} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Nodes ({nodes.length})</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {nodes.map((node, idx) => (
                      <Card key={idx} className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold">{node.node_id}</h4>
                              <p className="text-sm text-slate-400 mt-1">
                                {node.host}:{node.port}
                              </p>
                              <div className="mt-2 flex gap-2">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  node.status === "active" ? "bg-green-900 text-green-200" :
                                  node.status === "failed" ? "bg-red-900 text-red-200" :
                                  "bg-yellow-900 text-yellow-200"
                                }`}>
                                  {node.status}
                                </span>
                                <span className="text-xs text-slate-400">
                                  {node.capabilities?.join(", ")}
                                </span>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

