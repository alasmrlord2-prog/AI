"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { API_URL } from "@/lib/api";

export default function VisualizationPage() {
  const [networkMap, setNetworkMap] = useState<any>(null);
  const [architecture, setArchitecture] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [networkRes, archRes, metricsRes] = await Promise.all([
        fetch(`${API_URL}/api/visualization/network-map`),
        fetch(`${API_URL}/api/visualization/architecture`),
        fetch(`${API_URL}/api/visualization/metrics`)
      ]);

      if (networkRes.ok) {
        const data = await networkRes.json();
        setNetworkMap(data);
      }

      if (archRes.ok) {
        const data = await archRes.json();
        setArchitecture(data);
      }

      if (metricsRes.ok) {
        const data = await metricsRes.json();
        setMetrics(data);
      }
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

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Visualization</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <Card>
                <CardHeader>
                  <CardTitle>Network Map</CardTitle>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <p>Loading...</p>
                  ) : networkMap ? (
                    <div>
                      <p className="text-sm text-gray-600 mb-2">
                        Services: {networkMap.services?.length || 0}
                      </p>
                      <div className="space-y-2">
                        {networkMap.services?.slice(0, 5).map((service: any) => (
                          <div key={service.id} className="p-2 bg-gray-50 rounded text-sm">
                            {service.name} - {service.status}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-500">No data</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Metrics Heatmap</CardTitle>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <p>Loading...</p>
                  ) : metrics ? (
                    <div className="space-y-3">
                      {Object.entries(metrics).map(([key, value]: [string, any]) => (
                        <div key={key}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="capitalize">{key}</span>
                            <span>{value.value?.toFixed(1) || 0}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${getStatusColor(value.status || "healthy")}`}
                              style={{ width: `${Math.min(value.value || 0, 100)}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No data</p>
                  )}
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Architecture</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : architecture ? (
                  <div className="space-y-3">
                    {architecture.services?.map((service: any) => (
                      <div key={service.name} className="p-3 bg-gray-50 rounded">
                        <div className="font-semibold">{service.name}</div>
                        <div className="text-sm text-gray-600">
                          Type: {service.type} | Depends on: {service.depends_on?.join(", ") || "None"}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No data</p>
                )}
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}

