"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type Alert = {
  id?: string;
  type?: string;
  message?: string;
  description?: string;
  severity?: string;
  timestamp?: string;
};

export default function BehaviorAlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/api/alerts/behavior/", {}, 5000).catch(() => ({ alerts: [] }));
      setAlerts(data.alerts || []);
    } catch (error) {
      console.error("Error loading alerts:", error);
      setAlerts([]);
    } finally {
      setLoading(false);
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
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>🚨 Behavior Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    تنبيهات السلوك - كشف الأنماط غير الطبيعية في النظام
                  </p>
                  <Button onClick={loadAlerts} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Alerts ({alerts.length})</h3>
                  <div className="space-y-3">
                    {alerts.length > 0 ? (
                      alerts.map((alert, idx) => (
                        <Card key={`alert-${alert.id || idx}-${idx}`} className="bg-slate-800 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-semibold">{alert.type || `Alert ${idx + 1}`}</h4>
                                <p className="text-sm text-slate-400 mt-1">{alert.message || alert.description || "No details"}</p>
                                <div className="mt-2 flex gap-2">
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    alert.severity === "critical" ? "bg-red-900 text-red-200" :
                                    alert.severity === "high" ? "bg-orange-900 text-orange-200" :
                                    alert.severity === "medium" ? "bg-yellow-900 text-yellow-200" :
                                    "bg-blue-900 text-blue-200"
                                  }`}>
                                    {alert.severity || "low"}
                                  </span>
                                  <span className="text-xs text-slate-500">{alert.timestamp || "Recently"}</span>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-8">No alerts found</div>
                    )}
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

