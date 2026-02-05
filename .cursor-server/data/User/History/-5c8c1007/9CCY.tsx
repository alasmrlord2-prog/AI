"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function MonitorPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/monitor`);
      if (!res.ok) {
        setError(`HTTP ${res.status}`);
        setData(null);
        return;
      }
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("خطأ في الاتصال بالسيرفر");
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
    <main className="p-6 text-slate-200 bg-slate-950 min-h-screen">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          System Monitor
        </h1>
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
  );
}
