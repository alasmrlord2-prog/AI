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
        
        if (json.cpu_percent !== undefined) {
          setCpuHistory((prev) => [...prev.slice(-29), { label: now, value: json.cpu_percent }]);
        }
        if (json.memory_percent !== undefined) {
          setMemoryHistory((prev) => [...prev.slice(-29), { label: now, value: json.memory_percent }]);
        }
        if (json.disk_used_percent !== undefined) {
          setDiskHistory((prev) => [...prev.slice(-29), { label: now, value: json.disk_used_percent }]);
        }
        if (json.network_rx_mbps !== undefined) {
          setNetworkRxHistory((prev) => [...prev.slice(-29), { label: now, value: json.network_rx_mbps }]);
        }
        if (json.network_tx_mbps !== undefined) {
          setNetworkTxHistory((prev) => [...prev.slice(-29), { label: now, value: json.network_tx_mbps }]);
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
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

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
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <div className="p-4 bg-slate-800 rounded">
                      <div className="text-sm text-slate-400">Backend</div>
                      <div className="text-xl font-bold mt-2 text-green-400">✅ Online</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded">
                      <div className="text-sm text-slate-400">Ollama</div>
                      <div className="text-xl font-bold mt-2 text-green-400">✅ Online</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded">
                      <div className="text-sm text-slate-400">DB</div>
                      <div className="text-xl font-bold mt-2 text-green-400">✅ Online</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded">
                      <div className="text-sm text-slate-400">Prometheus</div>
                      <div className="text-xl font-bold mt-2 text-yellow-400">⚠️ Optional</div>
                    </div>
                    <div className="p-4 bg-slate-800 rounded">
                      <div className="text-sm text-slate-400">Grafana</div>
                      <div className="text-xl font-bold mt-2 text-yellow-400">⚠️ Optional</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : tab === "kernel" ? (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Kernel Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-slate-400">Kernel metrics will be displayed here</div>
              </CardContent>
            </Card>
          ) : tab === "network" ? (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Network Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-slate-400">Network metrics will be displayed here</div>
              </CardContent>
            </Card>
          ) : tab === "performance" ? (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Performance Tuner</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-slate-400">Performance tuning options will be displayed here</div>
              </CardContent>
            </Card>
          ) : tab === "dependency" ? (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Service Dependency</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-slate-400">Service dependency graph will be displayed here</div>
              </CardContent>
            </Card>
          ) : null}
        </div>
      </div>
    </main>
  );
}
