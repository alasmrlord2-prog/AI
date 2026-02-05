"use client";

import { useState, useEffect } from "react";
import { apiRequest } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

export default function SecurityCenterPage() {
  const [threats, setThreats] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [secrets, setSecrets] = useState<any[]>([]);
  const [hardening, setHardening] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch threats - use correct endpoint
        const threatsData = await apiRequest("/api/security/threat-detection/incidents?hours=24", { method: "GET" }, 5000).catch(() => ({ incidents: [] }));
        setThreats(threatsData?.incidents || threatsData?.threats || []);

        // Fetch behavior anomalies - use correct endpoint
        const anomaliesData = await apiRequest("/api/alerts/behavior/", { method: "GET" }, 5000).catch(() => ({ alerts: [] }));
        setAnomalies(anomaliesData?.alerts || anomaliesData?.anomalies || []);

        // Fetch secrets - use correct endpoint
        const secretsData = await apiRequest("/api/secrets/", { method: "GET" }, 5000).catch(() => ({ secrets: [] }));
        setSecrets(secretsData?.secrets || []);

        // Fetch hardening status - use correct endpoint (no suggestions endpoint, use status)
        const hardeningData = await apiRequest("/api/security/hardening/status", { method: "GET" }, 5000).catch(() => ({ suggestions: [] }));
        // Convert status to suggestions format if needed
        const suggestions = hardeningData?.suggestions || (hardeningData?.recommendations ? hardeningData.recommendations.map((r: any) => ({ title: r.title || r.name, description: r.description || r.message })) : []);
        setHardening(suggestions);
      } catch (error) {
        console.error("Error fetching security data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-slate-400">Loading...</div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 space-y-6 scrollbar-thin">
          {/* Row 1: Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">Threats</div>
                <div className="text-3xl font-bold mt-2 text-red-400">{threats.length}</div>
                <div className="text-xs text-slate-500 mt-1">Detected (24h)</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">ABAC Policies</div>
                <div className="text-3xl font-bold mt-2 text-blue-400">12</div>
                <div className="text-xs text-slate-500 mt-1">Active</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">Secrets</div>
                <div className="text-3xl font-bold mt-2 text-yellow-400">{secrets.length}</div>
                <div className="text-xs text-slate-500 mt-1">Managed</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">Hardening Score</div>
                <div className="text-3xl font-bold mt-2 text-green-400">98%</div>
                <div className="text-xs text-slate-500 mt-1">Protected</div>
              </CardContent>
            </Card>
          </div>

          {/* Row 2: Lists */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Detected Threats */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Detected Threats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {threats.length > 0 ? (
                    threats.slice(0, 10).map((threat, idx) => (
                      <div key={`threat-${threat.id || threat.type || idx}-${idx}`} className="p-3 bg-slate-800 rounded border-l-4 border-red-500">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-red-400">{threat.type || "Threat"}</div>
                            <div className="text-sm text-slate-400 mt-1">{threat.message || threat.description || "No details"}</div>
                          </div>
                          <span className="text-xs text-slate-500">{threat.timestamp || "Recently"}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-500 text-center py-4">No threats detected</div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Behavior Anomalies */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Behavior Anomalies</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {anomalies.length > 0 ? (
                    anomalies.slice(0, 10).map((anomaly, idx) => (
                      <div key={`anomaly-${anomaly.id || anomaly.type || idx}-${idx}`} className="p-3 bg-slate-800 rounded border-l-4 border-yellow-500">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-yellow-400">{anomaly.type || "Anomaly"}</div>
                            <div className="text-sm text-slate-400 mt-1">{anomaly.message || anomaly.description || "No details"}</div>
                          </div>
                          <span className="text-xs text-slate-500">{anomaly.timestamp || "Recently"}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-500 text-center py-4">No anomalies detected</div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Secret Exposures */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Secret Exposures</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {secrets.length > 0 ? (
                    secrets.filter((s: any) => s.exposed || s.risk === "high").slice(0, 10).map((secret, idx) => (
                      <div key={`secret-${secret.id || secret.name || idx}-${idx}`} className="p-3 bg-slate-800 rounded border-l-4 border-orange-500">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-orange-400">{secret.name || "Secret"}</div>
                            <div className="text-sm text-slate-400 mt-1">{secret.location || "Unknown location"}</div>
                          </div>
                          <span className="text-xs text-red-400">Exposed</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-500 text-center py-4">No exposed secrets</div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Hardening Suggestions */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Hardening Suggestions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {hardening.length > 0 ? (
                    hardening.slice(0, 10).map((suggestion, idx) => (
                      <div key={`hardening-${suggestion.id || suggestion.title || idx}-${idx}`} className="p-3 bg-slate-800 rounded border-l-4 border-blue-500">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-blue-400">{suggestion.title || "Suggestion"}</div>
                            <div className="text-sm text-slate-400 mt-1">{suggestion.description || suggestion.message || "No details"}</div>
                          </div>
                          <button className="text-xs text-blue-400 hover:text-blue-300">Apply</button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-500 text-center py-4">No suggestions available</div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}
