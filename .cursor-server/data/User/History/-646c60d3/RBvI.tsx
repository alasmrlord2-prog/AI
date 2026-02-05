"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === "ai-agent.bankid-sy.com" || hostname.includes("bankid-sy.com")) {
      return "http://ai-agent.bankid-sy.com";
    }
    return "http://localhost:8000";
  }
  return "http://localhost:8000";
};

export default function ThreatDetectionPage() {
  const [status, setStatus] = useState<any>(null);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadStatus();
    loadIncidents();
  }, []);

  const loadStatus = async () => {
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/security/threat-detection/status`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setStatus(data);
    } catch (error) {
      console.error("Error loading status:", error);
    }
  };

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/security/threat-detection/incidents?hours=24`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setIncidents(data.incidents || []);
    } catch (error) {
      console.error("Error loading incidents:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async () => {
    try {
      const token = localStorage.getItem("auth_token");
      await fetch(`${getApiUrl()}/api/security/threat-detection/start`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      loadStatus();
    } catch (error) {
      console.error("Error starting:", error);
    }
  };

  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header locale={locale} setLocale={handleSetLocale} />
        <div className="p-6">
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

