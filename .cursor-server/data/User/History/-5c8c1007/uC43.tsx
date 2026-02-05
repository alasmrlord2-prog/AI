"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import LineChart from "@/components/charts/LineChart";
import BarChart from "@/components/charts/BarChart";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

import { getApiUrl, apiRequest } from "@/lib/api";
const PROMETHEUS_URL = process.env.NEXT_PUBLIC_PROMETHEUS_URL || "http://localhost:9090";
const GRAFANA_URL = process.env.NEXT_PUBLIC_GRAFANA_URL || "http://localhost:3001";

export default function MonitorPage() {
  const [data, setData] = useState<any>(null);
  const [prometheusData, setPrometheusData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cpuHistory, setCpuHistory] = useState<Array<{label: string; value: number}>>([]);
  const [memoryHistory, setMemoryHistory] = useState<Array<{label: string; value: number}>>([]);
  const [networkRxHistory, setNetworkRxHistory] = useState<Array<{label: string; value: number}>>([]);
  const [networkTxHistory, setNetworkTxHistory] = useState<Array<{label: string; value: number}>>([]);

  const fetchPrometheusMetrics = async () => {
    try {
      // Fetch metrics from Prometheus
      const queries = [
        "system_cpu_load",
        "system_memory_used_bytes",
        "system_disk_used_bytes",
        "chat_requests_total",
        "chat_errors_total",
        "network_rx_mbps",
        "network_tx_mbps",
        "network_connections_total",
      ];

      const metrics: any = {};
      
      for (const query of queries) {
        try {
          const res = await fetch(
            `${PROMETHEUS_URL}/api/v1/query?query=${query}`,
            { 
              mode: 'cors',
              signal: AbortSignal.timeout(2000) // 2 second timeout
            }
          );
          if (res.ok) {
            const data = await res.json();
            if (data.data?.result?.[0]?.value) {
              metrics[query] = parseFloat(data.data.result[0].value[1]);
            }
          }
        } catch (e: any) {
          // Ignore individual query errors (Prometheus may not be available)
          // Only log if it's not a connection error or timeout
          if (e.name !== 'AbortError' && 
              !e.message?.includes('Failed to fetch') && 
              !e.message?.includes('timeout')) {
            console.debug(`Prometheus query failed for ${query}:`, e.message);
          }
        }
      }

      setPrometheusData(metrics);
    } catch (err) {
      // Prometheus is optional, don't fail if it's not available
      console.log("Prometheus not available:", err);
    }
  };

  const fetchStatus = async () => {
    try {
      const json = await apiRequest("/api/monitor", {
        method: "GET",
      }, 15000); // 15 second timeout for monitor data
      
      setData(json);
      setError(null);
      
      // Update history for charts
      const now = new Date();
      const timeLabel = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
      
      // CPU History
      if (json.load_avg?.["1min"]) {
        setCpuHistory(prev => {
          const updated = [...prev, { label: timeLabel, value: json.load_avg["1min"] }];
          return updated.slice(-20); // Keep last 20 data points
        });
      }
      
      // Memory History
      if (json.memory) {
        const memoryPercent = ((json.memory.total - json.memory.available) / json.memory.total) * 100;
        setMemoryHistory(prev => {
          const updated = [...prev, { label: timeLabel, value: memoryPercent }];
          return updated.slice(-20);
        });
      }
      
      // Network History
      if (json.network?.stats?.total) {
        setNetworkRxHistory(prev => {
          const updated = [...prev, { label: timeLabel, value: json.network.stats.total.rx_mbps || 0 }];
          return updated.slice(-20);
        });
        setNetworkTxHistory(prev => {
          const updated = [...prev, { label: timeLabel, value: json.network.stats.total.tx_mbps || 0 }];
          return updated.slice(-20);
        });
      }
      
      // Also fetch Prometheus metrics
      fetchPrometheusMetrics();
    } catch (err) {
      console.error("Error fetching monitor data:", err);
      const errorMessage = err instanceof Error ? err.message : "خطأ غير معروف";
      if (errorMessage.includes("timeout")) {
        setError("⏱️ استغرق الطلب وقتاً طويلاً. تحقق من حالة الـ Backend.");
      } else if (errorMessage.includes("الاتصال")) {
        setError("🌐 خطأ في الاتصال بالخادم. تحقق من اتصال الإنترنت وحالة الـ Backend.");
      } else {
        setError(`❌ خطأ: ${errorMessage}`);
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const getLoadColor = (load: number) => {
    if (load < 1) return "text-green-400";
    if (load < 2) return "text-yellow-400";
    return "text-red-400";
  };

  const getMemoryColor = (used: number, total: number) => {
    const percent = (used / total) * 100;
    if (percent < 60) return "text-green-400";
    if (percent < 80) return "text-yellow-400";
    return "text-red-400";
  };

  const getDiskColor = (used: number, total: number) => {
    const percent = (used / total) * 100;
    if (percent < 70) return "text-green-400";
    if (percent < 85) return "text-yellow-400";
    return "text-red-400";
  };

  if (loading && !data) {
    return (
      <main className="p-6 text-slate-200 bg-slate-950 min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-slate-400">جاري التحميل...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error && !data) {
    return (
      <main className="p-6 text-slate-200 bg-slate-950 min-h-screen">
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
          <p className="text-red-400">خطأ: {error}</p>
          <button
            onClick={fetchStatus}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-500"
          >
            إعادة المحاولة
          </button>
        </div>
      </main>
    );
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                System Monitor
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Real-time system monitoring and metrics visualization
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-slate-400">Live</span>
            </div>
          </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* CPU Load */}
        <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">⚡</span>
              <span>CPU Load Average</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">1 min:</span>
              <span className={`font-mono font-bold ${getLoadColor(data?.load_avg?.["1min"] || 0)}`}>
                {data?.load_avg?.["1min"]?.toFixed(2) || "N/A"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">5 min:</span>
              <span className={`font-mono font-bold ${getLoadColor(data?.load_avg?.["5min"] || 0)}`}>
                {data?.load_avg?.["5min"]?.toFixed(2) || "N/A"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">15 min:</span>
              <span className={`font-mono font-bold ${getLoadColor(data?.load_avg?.["15min"] || 0)}`}>
                {data?.load_avg?.["15min"]?.toFixed(2) || "N/A"}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Memory */}
        <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">💾</span>
              <span>Memory</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data?.memory && (
              <>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Total:</span>
                  <span className="font-mono text-blue-400">
                    {(data.memory.total / 1024 / 1024 / 1024).toFixed(2)} GB
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Available:</span>
                  <span className={`font-mono font-bold ${getMemoryColor(
                    data.memory.total - data.memory.available,
                    data.memory.total
                  )}`}>
                    {(data.memory.available / 1024 / 1024 / 1024).toFixed(2)} GB
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Used:</span>
                  <span className={`font-mono font-bold ${getMemoryColor(
                    data.memory.total - data.memory.available,
                    data.memory.total
                  )}`}>
                    {((data.memory.total - data.memory.available) / 1024 / 1024 / 1024).toFixed(2)} GB
                  </span>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        ((data.memory.total - data.memory.available) / data.memory.total) * 100 < 60
                          ? "bg-green-500"
                          : ((data.memory.total - data.memory.available) / data.memory.total) * 100 < 80
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{
                        width: `${((data.memory.total - data.memory.available) / data.memory.total) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Disk */}
        <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">💿</span>
              <span>Disk Usage</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data?.disk && (
              <>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Total:</span>
                  <span className="font-mono text-blue-400">
                    {data.disk.total_gb?.toFixed(2) || "N/A"} GB
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Used:</span>
                  <span className={`font-mono font-bold ${getDiskColor(
                    data.disk.used_gb || 0,
                    data.disk.total_gb || 1
                  )}`}>
                    {data.disk.used_gb?.toFixed(2) || "N/A"} GB
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Free:</span>
                  <span className={`font-mono font-bold ${getDiskColor(
                    data.disk.used_gb || 0,
                    data.disk.total_gb || 1
                  )}`}>
                    {data.disk.free_gb?.toFixed(2) || "N/A"} GB
                  </span>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        ((data.disk.used_gb || 0) / (data.disk.total_gb || 1)) * 100 < 70
                          ? "bg-green-500"
                          : ((data.disk.used_gb || 0) / (data.disk.total_gb || 1)) * 100 < 85
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{
                        width: `${((data.disk.used_gb || 0) / (data.disk.total_gb || 1)) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* CPU Load Trend */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>CPU Load Trend (1 min)</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart
              data={cpuHistory.length > 0 ? cpuHistory : [
                { label: "00:00", value: 0 },
                { label: "00:05", value: 0 },
              ]}
              color="#3b82f6"
              height={200}
            />
          </CardContent>
        </Card>

        {/* Memory Usage Trend */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Memory Usage Trend (%)</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart
              data={memoryHistory.length > 0 ? memoryHistory : [
                { label: "00:00", value: 0 },
                { label: "00:05", value: 0 },
              ]}
              color="#10b981"
              height={200}
            />
          </CardContent>
        </Card>

        {/* Network RX Trend */}
        {networkRxHistory.length > 0 && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>Network RX Trend (Mbps)</CardTitle>
            </CardHeader>
            <CardContent>
              <LineChart
                data={networkRxHistory}
                color="#06b6d4"
                height={200}
              />
            </CardContent>
          </Card>
        )}

        {/* Network TX Trend */}
        {networkTxHistory.length > 0 && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>Network TX Trend (Mbps)</CardTitle>
            </CardHeader>
            <CardContent>
              <LineChart
                data={networkTxHistory}
                color="#8b5cf6"
                height={200}
              />
            </CardContent>
          </Card>
        )}

        {/* System Metrics Comparison */}
        {data && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>System Metrics Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <BarChart
                data={[
                  {
                    label: "CPU",
                    value: data.load_avg?.["1min"] && !isNaN(data.load_avg["1min"])
                      ? (data.load_avg["1min"] * 20)
                      : 0,
                  },
                  {
                    label: "Memory",
                    value: data.memory && data.memory.total && data.memory.total > 0
                      ? ((data.memory.total - (data.memory.available || 0)) / data.memory.total) * 100
                      : 0,
                  },
                  {
                    label: "Disk",
                    value: data.disk && data.disk.total_gb && data.disk.total_gb > 0
                      ? ((data.disk.used_gb || 0) / data.disk.total_gb) * 100
                      : 0,
                  },
                ].map(item => ({
                  ...item,
                  value: typeof item.value === 'number' && !isNaN(item.value) ? item.value : 0,
                }))}
                color="#ec4899"
                height={200}
              />
            </CardContent>
          </Card>
        )}

        {/* Services Status Chart */}
        {data?.services && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>Services Status</CardTitle>
            </CardHeader>
            <CardContent>
              <BarChart
                data={[
                  {
                    label: "Running",
                    value: Object.values(data.services).filter((s: any) => s === "" || s === "OK").length,
                  },
                  {
                    label: "Failed",
                    value: Object.values(data.services).filter((s: any) => s !== "" && s !== "OK").length,
                  },
                ]}
                color="#f59e0b"
                height={200}
              />
            </CardContent>
          </Card>
        )}
      </div>

      {/* Prometheus Metrics */}
      {prometheusData && Object.keys(prometheusData).length > 0 && (
        <Card className="bg-gradient-to-br from-purple-900/30 to-indigo-900/30 border-purple-700 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">📊</span>
                <span>Prometheus Metrics</span>
              </div>
              <a
                href={PROMETHEUS_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-purple-400 hover:text-purple-300"
              >
                Open Prometheus →
              </a>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {prometheusData.system_cpu_load !== undefined && (
                <div className="p-3 bg-purple-900/20 border border-purple-700 rounded">
                  <div className="text-xs text-slate-400">CPU Load</div>
                  <div className={`text-xl font-bold ${getLoadColor(prometheusData.system_cpu_load)}`}>
                    {prometheusData.system_cpu_load.toFixed(2)}
                  </div>
                </div>
              )}
              {prometheusData.system_memory_used_bytes !== undefined && (
                <div className="p-3 bg-purple-900/20 border border-purple-700 rounded">
                  <div className="text-xs text-slate-400">Memory Used</div>
                  <div className="text-xl font-bold text-purple-400">
                    {(prometheusData.system_memory_used_bytes / 1024 / 1024 / 1024).toFixed(2)} GB
                  </div>
                </div>
              )}
              {prometheusData.system_disk_used_bytes !== undefined && (
                <div className="p-3 bg-purple-900/20 border border-purple-700 rounded">
                  <div className="text-xs text-slate-400">Disk Used</div>
                  <div className="text-xl font-bold text-purple-400">
                    {(prometheusData.system_disk_used_bytes / 1024 / 1024 / 1024).toFixed(2)} GB
                  </div>
                </div>
              )}
              {prometheusData.chat_requests_total !== undefined && (
                <div className="p-3 bg-purple-900/20 border border-purple-700 rounded">
                  <div className="text-xs text-slate-400">Chat Requests</div>
                  <div className="text-xl font-bold text-blue-400">
                    {prometheusData.chat_requests_total.toFixed(0)}
                  </div>
                </div>
              )}
              {prometheusData.chat_errors_total !== undefined && (
                <div className="p-3 bg-purple-900/20 border border-purple-700 rounded">
                  <div className="text-xs text-slate-400">Chat Errors</div>
                  <div className={`text-xl font-bold ${
                    prometheusData.chat_errors_total > 0 ? "text-red-400" : "text-green-400"
                  }`}>
                    {prometheusData.chat_errors_total.toFixed(0)}
                  </div>
                </div>
              )}
              {prometheusData.network_rx_mbps !== undefined && (
                <div className="p-3 bg-purple-900/20 border border-purple-700 rounded">
                  <div className="text-xs text-slate-400">Network RX</div>
                  <div className="text-xl font-bold text-cyan-400">
                    {prometheusData.network_rx_mbps.toFixed(2)} Mbps
                  </div>
                </div>
              )}
              {prometheusData.network_tx_mbps !== undefined && (
                <div className="p-3 bg-purple-900/20 border border-purple-700 rounded">
                  <div className="text-xs text-slate-400">Network TX</div>
                  <div className="text-xl font-bold text-cyan-400">
                    {prometheusData.network_tx_mbps.toFixed(2)} Mbps
                  </div>
                </div>
              )}
              {prometheusData.network_connections_total !== undefined && (
                <div className="p-3 bg-purple-900/20 border border-purple-700 rounded">
                  <div className="text-xs text-slate-400">Connections</div>
                  <div className="text-xl font-bold text-blue-400">
                    {prometheusData.network_connections_total.toFixed(0)}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Grafana Link */}
      <Card className="bg-gradient-to-br from-indigo-900/30 to-blue-900/30 border-indigo-700 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">📈</span>
              <span>Grafana Dashboards</span>
            </div>
            <a
              href={GRAFANA_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded text-sm text-white"
            >
              Open Grafana →
            </a>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-slate-300 text-sm space-y-2">
            <p>Access Grafana dashboards for detailed metrics visualization:</p>
            <ul className="list-disc list-inside space-y-1 text-slate-400">
              <li>System metrics (CPU, Memory, Disk)</li>
              <li>Chat performance (requests, errors)</li>
              <li>Custom dashboards and alerts</li>
            </ul>
            <div className="mt-4 p-3 bg-indigo-900/20 border border-indigo-700 rounded">
              <div className="text-xs text-slate-400 mb-1">Credentials:</div>
              <div className="text-xs font-mono">admin / admin123</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Network Traffic Monitoring */}
      {data && data.network && !data.network.error && (
        <Card className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 border-cyan-700 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🌐</span>
                <span>Network Traffic</span>
              </div>
              <a
                href="/security"
                className="text-xs text-cyan-400 hover:text-cyan-300"
              >
                Security Scan →
              </a>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data.network.stats && (
              <div className="space-y-4">
                {/* Total Traffic */}
                {data.network.stats.total && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-3 bg-cyan-900/20 border border-cyan-700 rounded">
                      <div className="text-xs text-slate-400">RX Total</div>
                      <div className="text-lg font-bold text-cyan-400">
                        {(data.network.stats.total.rx_bytes / 1024 / 1024).toFixed(2)} MB
                      </div>
                      <div className="text-xs text-slate-500">
                        {data.network.stats.total.rx_mbps?.toFixed(2) || "0"} Mbps
                      </div>
                    </div>
                    <div className="p-3 bg-cyan-900/20 border border-cyan-700 rounded">
                      <div className="text-xs text-slate-400">TX Total</div>
                      <div className="text-lg font-bold text-cyan-400">
                        {(data.network.stats.total.tx_bytes / 1024 / 1024).toFixed(2)} MB
                      </div>
                      <div className="text-xs text-slate-500">
                        {data.network.stats.total.tx_mbps?.toFixed(2) || "0"} Mbps
                      </div>
                    </div>
                    <div className="p-3 bg-cyan-900/20 border border-cyan-700 rounded">
                      <div className="text-xs text-slate-400">RX Packets</div>
                      <div className="text-lg font-bold text-blue-400">
                        {data.network.stats.total.rx_packets?.toLocaleString() || "0"}
                      </div>
                    </div>
                    <div className="p-3 bg-cyan-900/20 border border-cyan-700 rounded">
                      <div className="text-xs text-slate-400">TX Packets</div>
                      <div className="text-lg font-bold text-blue-400">
                        {data.network.stats.total.tx_packets?.toLocaleString() || "0"}
                      </div>
                    </div>
                  </div>
                )}

                {/* Network Interfaces */}
                {data.network.stats.interfaces && Object.keys(data.network.stats.interfaces).length > 0 && (
                  <div>
                    <div className="text-sm font-semibold text-slate-300 mb-2">Interfaces:</div>
                    <div className="space-y-2">
                      {Object.entries(data.network.stats.interfaces).map(([iface, stats]: [string, any]) => (
                        <div key={iface} className="p-3 bg-slate-800/50 border border-slate-700 rounded">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-mono text-sm text-cyan-300">{iface}</span>
                            {(stats.rx_errors > 0 || stats.tx_errors > 0) && (
                              <span className="text-xs text-red-400">
                                ⚠️ Errors: RX {stats.rx_errors} / TX {stats.tx_errors}
                              </span>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <span className="text-slate-400">RX:</span>{" "}
                              <span className="text-cyan-400">
                                {(stats.rx_bytes / 1024 / 1024).toFixed(2)} MB
                              </span>{" "}
                              <span className="text-slate-500">
                                ({stats.rx_mbps?.toFixed(2) || "0"} Mbps)
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-400">TX:</span>{" "}
                              <span className="text-cyan-400">
                                {(stats.tx_bytes / 1024 / 1024).toFixed(2)} MB
                              </span>{" "}
                              <span className="text-slate-500">
                                ({stats.tx_mbps?.toFixed(2) || "0"} Mbps)
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Active Connections */}
                {data.network.connections && (
                  <div>
                    <div className="text-sm font-semibold text-slate-300 mb-2">Active Connections:</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      <div className="p-2 bg-slate-800/50 border border-slate-700 rounded text-center">
                        <div className="text-xs text-slate-400">Total</div>
                        <div className="text-lg font-bold text-cyan-400">
                          {data.network.connections.total || 0}
                        </div>
                      </div>
                      <div className="p-2 bg-slate-800/50 border border-slate-700 rounded text-center">
                        <div className="text-xs text-slate-400">TCP Established</div>
                        <div className="text-lg font-bold text-green-400">
                          {data.network.connections.tcp?.established || 0}
                        </div>
                      </div>
                      <div className="p-2 bg-slate-800/50 border border-slate-700 rounded text-center">
                        <div className="text-xs text-slate-400">TCP Listening</div>
                        <div className="text-lg font-bold text-yellow-400">
                          {data.network.connections.tcp?.listening || 0}
                        </div>
                      </div>
                      <div className="p-2 bg-slate-800/50 border border-slate-700 rounded text-center">
                        <div className="text-xs text-slate-400">UDP</div>
                        <div className="text-lg font-bold text-blue-400">
                          {data.network.connections.udp?.listening || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Security Alerts */}
                {data.network.alerts && data.network.alerts.length > 0 && (
                  <div>
                    <div className="text-sm font-semibold text-red-400 mb-2">⚠️ Security Alerts:</div>
                    <div className="space-y-2">
                      {data.network.alerts.map((alert: any, idx: number) => (
                        <div
                          key={idx}
                          className={`p-2 border rounded ${
                            alert.severity === "high"
                              ? "bg-red-900/30 border-red-700 text-red-300"
                              : "bg-yellow-900/30 border-yellow-700 text-yellow-300"
                          }`}
                        >
                          <div className="text-xs font-semibold">{alert.type}</div>
                          <div className="text-xs">{alert.message}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            {data.network.error && (
              <div className="text-red-400 text-sm">{data.network.error}</div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Services */}
      <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">🔧</span>
            <span>Services Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data && data.services && Object.keys(data.services).map((srv) => {
              const status = data.services[srv] === "" ? "OK" : data.services[srv];
              const isOk = status === "OK";
              return (
                <div
                  key={srv}
                  className={`p-3 rounded-lg border ${
                    isOk
                      ? "bg-green-900/20 border-green-700"
                      : "bg-red-900/20 border-red-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm">{srv}</span>
                    <span
                      className={`px-2 py-1 rounded text-xs font-bold ${
                        isOk
                          ? "bg-green-600 text-white"
                          : "bg-red-600 text-white"
                      }`}
                    >
                      {isOk ? "✓" : "✗"}
                    </span>
                  </div>
                  {!isOk && (
                    <p className="text-xs text-red-400 mt-1">{status}</p>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
        </main>
      </div>
    </div>
  );
}
