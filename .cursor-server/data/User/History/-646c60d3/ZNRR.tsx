"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function ThreatDetectionPage() {
  const [status, setStatus] = useState<any>(null);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    // Load status first (quick 3s timeout), then incidents after a short delay
    loadStatus();
    // Delay incidents loading slightly to improve initial page load speed
    const timer = setTimeout(() => {
      loadIncidents();
    }, 200);
    return () => clearTimeout(timer);
  }, []);

  const loadStatus = async () => {
    try {
      const data = await apiRequest("/api/security/threat-detection/status", {}, 3000); // 3 second timeout for quick status
      setStatus(data);
    } catch (error) {
      console.error("Error loading status:", error);
      setStatus(null);
    }
  };

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/api/security/threat-detection/incidents?hours=24", {}, 5000); // 5 second timeout
      setIncidents(data.incidents || []);
    } catch (error) {
      console.error("Error loading incidents:", error);
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async () => {
    try {
      await apiRequest("/api/security/threat-detection/start", {
        method: "POST",
      });
      loadStatus();
    } catch (error) {
      console.error("Error starting:", error);
      alert(`خطأ في بدء النظام: ${error instanceof Error ? error.message : "خطأ غير معروف"}`);
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
              <CardTitle>🤖 AI Threat Detection - 100% Local</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {status && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">الحالة</div>
                        <div className={`text-2xl font-bold mt-1 ${
                          status.enabled ? "text-green-400" : "text-red-400"
                        }`}>
                          {status.enabled ? "نشط" : "معطل"}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">الحوادث</div>
                        <div className="text-2xl font-bold mt-1 text-blue-400">
                          {status.incidents_count || 0}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">IPs محظورة</div>
                        <div className="text-2xl font-bold mt-1 text-orange-400">
                          {status.blocked_ips || 0}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">Offline Mode</div>
                        <div className={`text-2xl font-bold mt-1 ${
                          status.offline_mode ? "text-green-400" : "text-red-400"
                        }`}>
                          {status.offline_mode ? "✅" : "❌"}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                <div className="flex gap-2 mb-4">
                  <Button onClick={handleStart} className="bg-green-600 hover:bg-green-700">
                    بدء النظام
                  </Button>
                  <Button onClick={loadIncidents} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">الحوادث الأخيرة ({incidents.length})</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {incidents.map((incident, idx) => (
                      <Card key={idx} className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold">{incident.id}</h4>
                              <p className="text-sm text-slate-400 mt-1">
                                {incident.threat?.pattern || "Unknown threat"}
                              </p>
                              <div className="mt-2">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  incident.severity === "critical" ? "bg-red-900 text-red-200" :
                                  incident.severity === "high" ? "bg-orange-900 text-orange-200" :
                                  "bg-yellow-900 text-yellow-200"
                                }`}>
                                  {incident.severity}
                                </span>
                              </div>
                            </div>
                            <div className="text-xs text-slate-500">
                              {new Date(incident.timestamp).toLocaleString('ar')}
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

