"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type Incident = {
  id?: string;
  title?: string;
  severity?: string;
  status?: string;
  created_at?: string;
  description?: string;
};

export default function IncidentCenterPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/api/incidents/command-center/", {}, 5000).catch(() => ({ incidents: [] }));
      setIncidents(data.incidents || []);
    } catch (error) {
      console.error("Error loading incidents:", error);
      setIncidents([]);
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
              <CardTitle>🎯 Incident Command Center</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    مركز قيادة الحوادث - إدارة وتنسيق الاستجابة للحوادث الأمنية
                  </p>
                  <Button onClick={loadIncidents} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Incidents ({incidents.length})</h3>
                  <div className="space-y-3">
                    {incidents.length > 0 ? (
                      incidents.map((incident, idx) => (
                        <Card key={`incident-${incident.id || idx}-${idx}`} className="bg-slate-800 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-semibold">{incident.title || `Incident ${idx + 1}`}</h4>
                                <p className="text-sm text-slate-400 mt-1">{incident.description || "No description"}</p>
                                <div className="mt-2 flex gap-2">
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    incident.severity === "critical" ? "bg-red-900 text-red-200" :
                                    incident.severity === "high" ? "bg-orange-900 text-orange-200" :
                                    incident.severity === "medium" ? "bg-yellow-900 text-yellow-200" :
                                    "bg-blue-900 text-blue-200"
                                  }`}>
                                    {incident.severity || "unknown"}
                                  </span>
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    incident.status === "resolved" ? "bg-green-900 text-green-200" :
                                    incident.status === "investigating" ? "bg-blue-900 text-blue-200" :
                                    "bg-gray-900 text-gray-200"
                                  }`}>
                                    {incident.status || "open"}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-8">No incidents found</div>
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

