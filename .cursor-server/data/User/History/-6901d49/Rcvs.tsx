"use client";

import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import LineChart from "@/components/charts/LineChart";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

const PROMETHEUS_URL = process.env.NEXT_PUBLIC_PROMETHEUS_URL || "http://localhost:9090";

export default function MonitoringPage() {
  const searchParams = useSearchParams();
  const tab = searchParams.get("tab") || "system";
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [cpuHistory, setCpuHistory] = useState<Array<{label: string; value: number}>>([]);
  const [memoryHistory, setMemoryHistory] = useState<Array<{label: string; value: number}>>([]);
  const [diskHistory, setDiskHistory] = useState<Array<{label: string; value: number}>>([]);
  const [networkRxHistory, setNetworkRxHistory] = useState<Array<{label: string; value: number}>>([]);
  const [networkTxHistory, setNetworkTxHistory] = useState<Array<{label: string; value: number}>>([]);
  const fetchingRef = useRef(false);

  const fetchStatus = async () => {
    if (fetchingRef.current) return;
    fetchingRef.current = true;
    
    if (!data) setLoading(true);
    
    try {
      const json = await apiRequest("/api/monitor", { method: "GET" }, 15000).catch(() => null);
      
      if (json) {
        setData(json);
        const now = new Date().toLocaleTimeString();
        
        if (json.cpu_percent !== undefined && typeof json.cpu_percent === 'number') {
          setCpuHistory((prev) => {
            const newData = { label: now, value: json.cpu_percent };
            const updated = [...prev, newData];
            return updated.slice(-30); // Keep last 30 points
          });
        }
        if (json.memory_percent !== undefined && typeof json.memory_percent === 'number') {
          setMemoryHistory((prev) => {
            const newData = { label: now, value: json.memory_percent };
            const updated = [...prev, newData];
            return updated.slice(-30); // Keep last 30 points
          });
        }
        if (json.disk_used_percent !== undefined && typeof json.disk_used_percent === 'number') {
          setDiskHistory((prev) => {
            const newData = { label: now, value: json.disk_used_percent };
            const updated = [...prev, newData];
            return updated.slice(-30); // Keep last 30 points
          });
        }
        if (json.network_rx_mbps !== undefined && typeof json.network_rx_mbps === 'number') {
          setNetworkRxHistory((prev) => {
            const newData = { label: now, value: json.network_rx_mbps };
            const updated = [...prev, newData];
            return updated.slice(-30); // Keep last 30 points
          });
        }
        if (json.network_tx_mbps !== undefined && typeof json.network_tx_mbps === 'number') {
          setNetworkTxHistory((prev) => {
            const newData = { label: now, value: json.network_tx_mbps };
            const updated = [...prev, newData];
            return updated.slice(-30); // Keep last 30 points
          });
        }
      }
    } catch (err) {
      console.error("Error fetching monitor data:", err);
    } finally {
      setLoading(false);
      fetchingRef.current = false;
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(() => {
      fetchStatus();
    }, 5000);
    return () => clearInterval(interval);
  }, [data]); // Re-run when data changes to ensure updates

  if (loading && !data) {
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

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Tabs - Scrollable on small screens */}
          <div className="flex gap-2 border-b border-slate-800 overflow-x-auto scrollbar-thin pb-2 -mx-4 md:mx-0 px-4 md:px-0">
            <a
              href="/monitoring"
              className={`px-3 md:px-4 py-2 border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                tab === "system" || !tab
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              System Metrics
            </a>
            <a
              href="/monitoring?tab=kernel"
              className={`px-3 md:px-4 py-2 border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                tab === "kernel"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Kernel Metrics
            </a>
            <a
              href="/monitoring?tab=network"
              className={`px-3 md:px-4 py-2 border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                tab === "network"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Network
            </a>
            <a
              href="/monitoring?tab=performance"
              className={`px-3 md:px-4 py-2 border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                tab === "performance"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Performance Tuner
            </a>
            <a
              href="/monitoring?tab=dependency"
              className={`px-3 md:px-4 py-2 border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                tab === "dependency"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Service Dependency
            </a>
          </div>

          {tab === "system" || !tab ? (
            <>
              {/* Section A: Summary */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4">
                <Card className="bg-slate-900 border-slate-800">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-slate-400">CPU Load</div>
                    <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-blue-400">
                      {data?.cpu_percent?.toFixed(1) || "0"}%
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-slate-400">Memory</div>
                    <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-purple-400">
                      {data?.memory_percent?.toFixed(1) || "0"}%
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-slate-400">Disk</div>
                    <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-green-400">
                      {data?.disk_used_percent?.toFixed(1) || "0"}%
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-slate-400">Uptime</div>
                    <div className="text-lg md:text-xl font-bold mt-1 md:mt-2 text-cyan-400">
                      {data?.uptime_days ? `${data.uptime_days.toFixed(1)}d` : "N/A"}
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800 col-span-2 sm:col-span-1">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-slate-400">Load Avg</div>
                    <div className="text-sm md:text-xl font-bold mt-1 md:mt-2 text-yellow-400 break-words">
                      {data?.load_avg ? (
                        typeof data.load_avg === 'object' 
                          ? `${data.load_avg['1min'] || '0'}, ${data.load_avg['5min'] || '0'}, ${data.load_avg['15min'] || '0'}`
                          : String(data.load_avg)
                      ) : "N/A"}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Section B: Charts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>CPU Trend (1m, 5m, 15m)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {cpuHistory.length > 0 ? (
                      <LineChart data={cpuHistory} color="#3b82f6" height={200} />
                    ) : (
                      <div className="h-[200px] flex items-center justify-center text-slate-500">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Memory Trend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {memoryHistory.length > 0 ? (
                      <LineChart data={memoryHistory} color="#a855f7" height={200} />
                    ) : (
                      <div className="h-[200px] flex items-center justify-center text-slate-500">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Disk Activity</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {diskHistory.length > 0 ? (
                      <LineChart data={diskHistory} color="#10b981" height={200} />
                    ) : (
                      <div className="h-[200px] flex items-center justify-center text-slate-500">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Network RX/TX</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {networkRxHistory.length > 0 || networkTxHistory.length > 0 ? (
                      <div className="space-y-4">
                        <div>
                          <div className="text-sm text-slate-400 mb-2">RX</div>
                          <LineChart data={networkRxHistory} color="#06b6d4" height={90} />
                        </div>
                        <div>
                          <div className="text-sm text-slate-400 mb-2">TX</div>
                          <LineChart data={networkTxHistory} color="#f59e0b" height={90} />
                        </div>
                      </div>
                    ) : (
                      <div className="h-[200px] flex items-center justify-center text-slate-500">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Section C: System Services */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>System Services</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 md:gap-4">
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Backend</div>
                      <div className="text-base md:text-xl font-bold mt-1 md:mt-2 text-green-400">✅ Online</div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Ollama</div>
                      <div className="text-base md:text-xl font-bold mt-1 md:mt-2 text-green-400">✅ Online</div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">DB</div>
                      <div className="text-base md:text-xl font-bold mt-1 md:mt-2 text-green-400">✅ Online</div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Prometheus</div>
                      <div className="text-base md:text-xl font-bold mt-1 md:mt-2 text-yellow-400">⚠️ Optional</div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Grafana</div>
                      <div className="text-base md:text-xl font-bold mt-1 md:mt-2 text-yellow-400">⚠️ Optional</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : tab === "kernel" ? (
            <div className="space-y-4 md:space-y-6">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Kernel Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4">
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Context Switches</div>
                      <div className="text-xl md:text-2xl font-bold mt-2 text-blue-400">
                        {data?.kernel_metrics?.context_switches?.toLocaleString() || "N/A"}
                      </div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Interrupts</div>
                      <div className="text-xl md:text-2xl font-bold mt-2 text-purple-400">
                        {data?.kernel_metrics?.interrupts?.toLocaleString() || "N/A"}
                      </div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Processes</div>
                      <div className="text-xl md:text-2xl font-bold mt-2 text-green-400">
                        {data?.kernel_metrics?.processes || "N/A"}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : tab === "network" ? (
            <div className="space-y-4 md:space-y-6">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Network Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">RX (MB/s)</div>
                      <div className="text-xl md:text-2xl font-bold mt-2 text-cyan-400">
                        {data?.network_rx_mbps?.toFixed(2) || "0.00"}
                      </div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">TX (MB/s)</div>
                      <div className="text-xl md:text-2xl font-bold mt-2 text-orange-400">
                        {data?.network_tx_mbps?.toFixed(2) || "0.00"}
                      </div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Connections</div>
                      <div className="text-xl md:text-2xl font-bold mt-2 text-blue-400">
                        {data?.network_connections || "N/A"}
                      </div>
                    </div>
                    <div className="p-3 md:p-4 bg-slate-800 rounded">
                      <div className="text-xs md:text-sm text-slate-400">Packets/s</div>
                      <div className="text-xl md:text-2xl font-bold mt-2 text-green-400">
                        {data?.network_packets_per_sec?.toFixed(0) || "N/A"}
                      </div>
                    </div>
                  </div>
                  {networkRxHistory.length > 0 || networkTxHistory.length > 0 ? (
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                      <div>
                        <div className="text-sm text-slate-400 mb-2">RX Trend</div>
                        <LineChart data={networkRxHistory} color="#06b6d4" height={150} />
                      </div>
                      <div>
                        <div className="text-sm text-slate-400 mb-2">TX Trend</div>
                        <LineChart data={networkTxHistory} color="#f59e0b" height={150} />
                      </div>
                    </div>
                  ) : null}
                </CardContent>
              </Card>
            </div>
          ) : tab === "performance" ? (
            <div className="space-y-4 md:space-y-6">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Performance Tuner</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-slate-800 rounded">
                      <div className="text-sm font-semibold mb-2">CPU Optimization</div>
                      <div className="text-sm text-slate-400">Current CPU: {data?.cpu_percent?.toFixed(1) || "0"}%</div>
                      <div className="mt-2 text-xs text-slate-500">Suggestions will appear here when available</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded">
                      <div className="text-sm font-semibold mb-2">Memory Optimization</div>
                      <div className="text-sm text-slate-400">Current Memory: {data?.memory_percent?.toFixed(1) || "0"}%</div>
                      <div className="mt-2 text-xs text-slate-500">Suggestions will appear here when available</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded">
                      <div className="text-sm font-semibold mb-2">Disk Optimization</div>
                      <div className="text-sm text-slate-400">Current Disk: {data?.disk_used_percent?.toFixed(1) || "0"}%</div>
                      <div className="mt-2 text-xs text-slate-500">Suggestions will appear here when available</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : tab === "dependency" ? (
            <div className="space-y-4 md:space-y-6">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Service Dependency</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-4 bg-slate-800 rounded border-l-4 border-blue-500">
                      <div className="font-semibold">Backend Service</div>
                      <div className="text-sm text-slate-400 mt-1">Dependencies: Database, Ollama</div>
                      <div className="text-xs text-green-400 mt-1">✅ Online</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded border-l-4 border-purple-500">
                      <div className="font-semibold">Ollama Service</div>
                      <div className="text-sm text-slate-400 mt-1">Dependencies: None</div>
                      <div className="text-xs text-green-400 mt-1">✅ Online</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded border-l-4 border-green-500">
                      <div className="font-semibold">Database Service</div>
                      <div className="text-sm text-slate-400 mt-1">Dependencies: None</div>
                      <div className="text-xs text-green-400 mt-1">✅ Online</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded border-l-4 border-yellow-500">
                      <div className="font-semibold">Prometheus (Optional)</div>
                      <div className="text-sm text-slate-400 mt-1">Dependencies: None</div>
                      <div className="text-xs text-yellow-400 mt-1">⚠️ Optional</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded border-l-4 border-yellow-500">
                      <div className="font-semibold">Grafana (Optional)</div>
                      <div className="text-sm text-slate-400 mt-1">Dependencies: Prometheus</div>
                      <div className="text-xs text-yellow-400 mt-1">⚠️ Optional</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : null}
        </div>
      </div>
    </main>
  );
}
