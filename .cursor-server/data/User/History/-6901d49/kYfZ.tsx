"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function MonitoringPage() {
  const [services, setServices] = useState<any[]>([]);
  const [containers, setContainers] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [serviceName, setServiceName] = useState("");
  const [containerName, setContainerName] = useState("");

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [metricsData, alertsData, containersData] = await Promise.all([
        apiRequest("/api/monitor/server-metrics", {}, 5000).catch(() => null),
        apiRequest("/api/monitor/alerts?limit=10&unread_only=true", {}, 5000).catch(() => ({ alerts: [] })),
        apiRequest("/api/monitor/containers", {}, 5000).catch(() => ({ containers: {} }))
      ]);

      if (metricsData) setMetrics(metricsData);
      if (alertsData) setAlerts(alertsData.alerts || []);
      if (containersData) {
        const containersList = Object.values(containersData.containers || {});
        setContainers(containersList as any[]);
      }
    } catch (err) {
      console.error("Error fetching monitoring data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAutoRepairService = async () => {
    if (!serviceName) {
      alert("يرجى إدخال اسم الخدمة");
      return;
    }

    try {
      const data = await apiRequest(`/api/monitor/auto-repair/service/${serviceName}`, {
        method: "POST"
      }, 30000); // 30s timeout for auto-repair
      
      alert(data.success ? "✅ تم إصلاح الخدمة!" : `⚠️ ${data.message || data.error || "فشل الإصلاح"}`);
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleAutoRepairContainer = async () => {
    if (!containerName) {
      alert("يرجى إدخال اسم Container");
      return;
    }

    try {
      const data = await apiRequest(`/api/monitor/auto-repair/container/${containerName}`, {
        method: "POST"
      }, 30000); // 30s timeout for auto-repair
      
      alert(data.success ? "✅ تم إصلاح Container!" : `⚠️ ${data.error || data.message || "فشل الإصلاح"}`);
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCheckService = async () => {
    if (!serviceName) {
      alert("يرجى إدخال اسم الخدمة");
      return;
    }

    try {
      const data = await apiRequest("/api/monitor/service-status/${serviceName}`);
      if (res.ok) {
        const data = await res.json();
        alert(`Status: ${data.status}\nActive: ${data.active ? "Yes" : "No"}`);
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCheckContainer = async () => {
    if (!containerName) {
      alert("يرجى إدخال اسم Container");
      return;
    }

    try {
      const data = await apiRequest("/api/monitor/container-status/${containerName}`);
      if (res.ok) {
        const data = await res.json();
        alert(`Status: ${data.status}\nRunning: ${data.running ? "Yes" : "No"}`);
      }
    } catch (err: any) {
      alert(err.message);
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
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold text-slate-800 mb-6">📊 Monitoring & Auto Repair</h1>

            {metrics && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <Card className="border-slate-200 shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-t-lg">
                    <CardTitle className="text-white">CPU</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="text-3xl font-bold">{metrics.cpu?.percent?.toFixed(1) || 0}%</div>
                    <div className={`w-full bg-gray-200 rounded-full h-2 mt-2`}>
                      <div
                        className={`h-2 rounded-full ${getStatusColor(metrics.cpu?.status || "healthy")}`}
                        style={{ width: `${Math.min(metrics.cpu?.percent || 0, 100)}%` }}
                      />
                    </div>
                    <div className="text-sm text-slate-600 mt-1">Status: {metrics.cpu?.status || "N/A"}</div>
                  </CardContent>
                </Card>

                <Card className="border-slate-200 shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg">
                    <CardTitle className="text-white">Memory</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="text-3xl font-bold">{metrics.memory?.percent?.toFixed(1) || 0}%</div>
                    <div className={`w-full bg-gray-200 rounded-full h-2 mt-2`}>
                      <div
                        className={`h-2 rounded-full ${getStatusColor(metrics.memory?.status || "healthy")}`}
                        style={{ width: `${Math.min(metrics.memory?.percent || 0, 100)}%` }}
                      />
                    </div>
                    <div className="text-sm text-slate-600 mt-1">Status: {metrics.memory?.status || "N/A"}</div>
                  </CardContent>
                </Card>

                <Card className="border-slate-200 shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-t-lg">
                    <CardTitle className="text-white">Disk</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="text-3xl font-bold">{metrics.disk?.percent?.toFixed(1) || 0}%</div>
                    <div className={`w-full bg-gray-200 rounded-full h-2 mt-2`}>
                      <div
                        className={`h-2 rounded-full ${getStatusColor(metrics.disk?.status || "healthy")}`}
                        style={{ width: `${Math.min(metrics.disk?.percent || 0, 100)}%` }}
                      />
                    </div>
                    <div className="text-sm text-slate-600 mt-1">Status: {metrics.disk?.status || "N/A"}</div>
                  </CardContent>
                </Card>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <Card className="border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-lg">
                  <CardTitle className="text-white">Auto Repair Service</CardTitle>
                </CardHeader>
                <CardContent className="p-4 space-y-4">
                  <div>
                    <Input
                      value={serviceName}
                      onChange={(e) => setServiceName(e.target.value)}
                      placeholder="Service name (e.g., nginx)"
                      className="mb-2"
                    />
                    <div className="flex gap-2">
                      <Button
                        onClick={handleCheckService}
                        variant="outline"
                        className="flex-1"
                      >
                        Check Status
                      </Button>
                      <Button
                        onClick={handleAutoRepairService}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        Auto Repair
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-t-lg">
                  <CardTitle className="text-white">Auto Repair Container</CardTitle>
                </CardHeader>
                <CardContent className="p-4 space-y-4">
                  <div>
                    <Input
                      value={containerName}
                      onChange={(e) => setContainerName(e.target.value)}
                      placeholder="Container name"
                      className="mb-2"
                    />
                    <div className="flex gap-2">
                      <Button
                        onClick={handleCheckContainer}
                        variant="outline"
                        className="flex-1"
                      >
                        Check Status
                      </Button>
                      <Button
                        onClick={handleAutoRepairContainer}
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                      >
                        Auto Repair
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-t-lg">
                  <CardTitle className="text-white">Containers</CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  {loading ? (
                    <p className="text-slate-500">جاري التحميل...</p>
                  ) : containers.length === 0 ? (
                    <p className="text-slate-500 text-center py-8">لا توجد containers</p>
                  ) : (
                    <div className="space-y-2">
                      {containers.slice(0, 10).map((container: any) => (
                        <div key={container.container} className="p-3 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200">
                          <div className="flex justify-between items-center">
                            <div>
                              <div className="font-semibold text-slate-800">{container.container}</div>
                              <div className="text-sm text-slate-600">
                                Status: <span className={`font-semibold ${
                                  container.running ? "text-green-600" : "text-red-600"
                                }`}>
                                  {container.status}
                                </span>
                              </div>
                            </div>
                            {!container.running && (
                              <Button
                                size="sm"
                                onClick={() => {
                                  setContainerName(container.container);
                                  handleAutoRepairContainer();
                                }}
                                className="bg-green-600 hover:bg-green-700 text-xs"
                              >
                                Repair
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-red-500 to-red-600 text-white rounded-t-lg">
                  <CardTitle className="text-white">Alerts</CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  {alerts.length === 0 ? (
                    <p className="text-slate-500 text-center py-8">لا توجد تنبيهات</p>
                  ) : (
                    <div className="space-y-2">
                      {alerts.map((alert: any) => (
                        <div key={alert.id} className={`p-3 rounded-lg border ${
                          alert.level === "critical" ? "bg-red-50 border-red-200" :
                          alert.level === "error" ? "bg-red-50 border-red-200" :
                          alert.level === "warning" ? "bg-yellow-50 border-yellow-200" :
                          "bg-blue-50 border-blue-200"
                        }`}>
                          <div className="font-semibold">{alert.title}</div>
                          <div className="text-sm mt-1">{alert.message}</div>
                          <div className="text-xs text-slate-500 mt-1">
                            {alert.timestamp && new Date(alert.timestamp).toLocaleString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

