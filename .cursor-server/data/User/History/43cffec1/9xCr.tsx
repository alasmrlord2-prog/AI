"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 
                process.env.NEXT_PUBLIC_BACKEND_URL || 
                "http://localhost:8000";

type SIEMData = {
  events: Array<{
    timestamp: string;
    source: string;
    type: string;
    severity: string;
    message: string;
  }>;
  metrics: {
    total_events: number;
    high_severity: number;
    medium_severity: number;
    low_severity: number;
    failed_logins_24h: number;
    blocked_ips: number;
    active_threats: number;
  };
  threat_intelligence: any;
  timestamp: string;
};

export default function SIEMPage() {
  const [data, setData] = useState<SIEMData | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchSIEMData = async () => {
    try {
      const token = localStorage.getItem("auth_token");
      if (!token) {
        setLoading(false);
        return;
      }

      const res = await fetch(`${API_URL}/api/security/siem`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to fetch SIEM data");
      }

      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("SIEM fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSIEMData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchSIEMData, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "high":
        return "text-red-400 bg-red-900/20 border-red-700";
      case "medium":
        return "text-yellow-400 bg-yellow-900/20 border-yellow-700";
      case "low":
        return "text-green-400 bg-green-900/20 border-green-700";
      default:
        return "text-slate-400 bg-slate-900/20 border-slate-700";
    }
  };

  if (loading && !data) {
    return (
      <div className="flex h-screen bg-slate-950 text-slate-200">
        <Sidebar />
        <div className="flex flex-col flex-1">
          <Header />
          <main className="flex-1 overflow-y-auto p-6 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
              <p className="mt-4 text-slate-400">Loading SIEM Dashboard...</p>
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent">
              🔒 SIEM Dashboard
            </h1>
            <div className="flex items-center gap-4">
              <Button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={autoRefresh ? "bg-green-600 hover:bg-green-700" : "bg-slate-700 hover:bg-slate-600"}
              >
                {autoRefresh ? "🟢 Auto Refresh ON" : "⚫ Auto Refresh OFF"}
              </Button>
              <Button onClick={fetchSIEMData} className="bg-indigo-600 hover:bg-indigo-700">
                🔄 Refresh
              </Button>
            </div>
          </div>

          {/* Metrics Overview */}
          {data?.metrics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card className="bg-gradient-to-br from-red-900/30 to-red-800/30 border-red-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Total Events</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-red-400">{data.metrics.total_events}</div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-900/30 to-orange-800/30 border-orange-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">High Severity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-orange-400">{data.metrics.high_severity}</div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/30 border-yellow-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Failed Logins (24h)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-yellow-400">{data.metrics.failed_logins_24h}</div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-900/30 to-purple-800/30 border-purple-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Active Threats</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-purple-400">{data.metrics.active_threats}</div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Security Events Timeline */}
          {data?.events && data.events.length > 0 && (
            <Card className="bg-slate-900 border-slate-800 mb-6">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Security Events Timeline</span>
                  <span className="text-sm text-slate-400">
                    Last updated: {new Date(data.timestamp).toLocaleTimeString()}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {data.events.map((event, idx) => (
                    <div
                      key={idx}
                      className={`p-3 border rounded ${getSeverityColor(event.severity)}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-semibold">{event.type}</span>
                            <span className="text-xs text-slate-400">from {event.source}</span>
                            <span className="text-xs text-slate-500">
                              {new Date(event.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <div className="text-sm text-slate-200">{event.message}</div>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${getSeverityColor(event.severity)}`}>
                          {event.severity}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Threat Intelligence */}
          {data?.threat_intelligence && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Threat Intelligence</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-slate-400">
                  Last updated: {new Date(data.threat_intelligence.threat_feed_updates).toLocaleString()}
                </div>
              </CardContent>
            </Card>
          )}

          {(!data || data.events.length === 0) && (
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-8 text-center">
                <div className="text-slate-400">
                  <p className="text-lg mb-2">No security events detected</p>
                  <p className="text-sm">System appears secure</p>
                </div>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
}

