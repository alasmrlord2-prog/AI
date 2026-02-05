"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function VisualizationPage() {
  const [networkMap, setNetworkMap] = useState<any>(null);
  const [architecture, setArchitecture] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initial fetch - don't block page load
    setTimeout(() => {
      fetchData();
    }, 100);
    
    // Update interval - less frequent to keep page fast
    const interval = setInterval(fetchData, 15000); // 15 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Don't show loading if we already have data - allows fast navigation
      if (!networkMap && !architecture && !metrics) {
        setLoading(true);
      }
      
      // Try to fetch data with longer timeout and better error handling
      const [networkData, archData, metricsData] = await Promise.all([
        apiRequest("/api/visualization/network-map", {}, 10000).catch((err) => {
          console.warn("Network map fetch failed:", err);
          return null;
        }),
        apiRequest("/api/visualization/architecture", {}, 10000).catch((err) => {
          console.warn("Architecture fetch failed:", err);
          return null;
        }),
        apiRequest("/api/visualization/metrics", {}, 10000).catch((err) => {
          console.warn("Metrics fetch failed:", err);
          return null;
        })
      ]);

      if (networkData) setNetworkMap(networkData);
      if (archData) setArchitecture(archData);
      if (metricsData) setMetrics(metricsData);
    } catch (err) {
      console.error("Error fetching visualization data:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy": return "bg-green-500";
      case "warning": return "bg-yellow-500";
      case "critical": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getStatusTextColor = (status: string) => {
    switch (status) {
      case "healthy": return "text-green-700";
      case "warning": return "text-yellow-700";
      case "critical": return "text-red-700";
      default: return "text-gray-700";
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold text-slate-800 mb-6">📊 Visualization</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <Card className="border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-t-lg">
                  <CardTitle className="text-white">Network Map</CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  {loading ? (
                    <p className="text-slate-500">جاري التحميل...</p>
                  ) : networkMap ? (
                    <div>
                      <p className="text-sm text-slate-600 mb-3">
                        Services: <span className="font-semibold">{networkMap.services?.length || 0}</span> | 
                        Links: <span className="font-semibold">{networkMap.links?.length || 0}</span>
                      </p>
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {networkMap.services?.slice(0, 10).map((service: any) => (
                          <div key={service.id} className="p-3 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200">
                            <div className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${
                                service.status === "running" ? "bg-green-500" : "bg-red-500"
                              }`} />
                              <div className="flex-1">
                                <div className="font-semibold text-sm text-slate-800">{service.name}</div>
                                <div className="text-xs text-slate-600">{service.image}</div>
                                {service.ports && service.ports.length > 0 && (
                                  <div className="text-xs text-slate-500 mt-1">
                                    Ports: {service.ports.map((p: any) => p.host_port).filter(Boolean).join(", ")}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-slate-500 mb-2">لا توجد بيانات</p>
                      <p className="text-xs text-slate-400">
                        تحقق من أن الـ Backend يعمل على: {typeof window !== 'undefined' ? window.location.hostname + ':8000' : 'localhost:8000'}
                      </p>
                      <Button
                        onClick={fetchData}
                        className="mt-3 text-xs"
                        size="sm"
                      >
                        إعادة المحاولة
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg">
                  <CardTitle className="text-white">Metrics Heatmap</CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  {loading ? (
                    <p className="text-slate-500">جاري التحميل...</p>
                  ) : metrics ? (
                    <div className="space-y-4">
                      {Object.entries(metrics).map(([key, value]: [string, any]) => (
                        <div key={key}>
                          <div className="flex justify-between items-center text-sm mb-2">
                            <span className="capitalize font-medium text-slate-700">{key}</span>
                            <div className="flex items-center gap-2">
                              <span className={`font-semibold ${getStatusTextColor(value.status || "healthy")}`}>
                                {value.value?.toFixed(1) || 0}%
                              </span>
                              <span className={`px-2 py-1 rounded text-xs ${getStatusTextColor(value.status || "healthy")} bg-opacity-20`}>
                                {value.status || "healthy"}
                              </span>
                            </div>
                          </div>
                          <div className="w-full bg-slate-200 rounded-full h-3">
                            <div
                              className={`h-3 rounded-full transition-all ${getStatusColor(value.status || "healthy")}`}
                              style={{ width: `${Math.min(value.value || 0, 100)}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-slate-500 mb-2">لا توجد بيانات</p>
                      <p className="text-xs text-slate-400">
                        تحقق من أن الـ Backend يعمل على: {typeof window !== 'undefined' ? window.location.hostname + ':8000' : 'localhost:8000'}
                      </p>
                      <Button
                        onClick={fetchData}
                        className="mt-3 text-xs"
                        size="sm"
                      >
                        إعادة المحاولة
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <Card className="border-slate-200 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-t-lg">
                <CardTitle className="text-white">Architecture</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {loading ? (
                  <p className="text-slate-500">جاري التحميل...</p>
                ) : architecture ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {architecture.services?.map((service: any) => (
                      <div key={service.name} className="p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                        <div className="font-semibold text-slate-800 mb-2">{service.name}</div>
                        <div className="text-sm text-slate-600">
                          Type: <span className="font-medium">{service.type}</span>
                        </div>
                        {service.depends_on && service.depends_on.length > 0 && (
                          <div className="text-sm text-slate-600 mt-1">
                            Depends on: <span className="font-medium">{service.depends_on.join(", ")}</span>
                          </div>
                        )}
                        {service.ports && service.ports.length > 0 && (
                          <div className="text-xs text-slate-500 mt-1">
                            Ports: {service.ports.join(", ")}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-center py-8">لا توجد بيانات</p>
                )}
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
