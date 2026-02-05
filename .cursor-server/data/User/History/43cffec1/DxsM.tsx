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
    ip?: string;
  }>;
  metrics: {
    total_events: number;
    high_severity: number;
    medium_severity: number;
    low_severity: number;
    critical_severity: number;
    failed_logins_24h: number;
    blocked_ips: number;
    active_threats: number;
    events_by_source?: Record<string, number>;
    events_by_type?: Record<string, number>;
    top_ips?: Array<{ip: string; count: number}>;
    trend_24h?: {
      events: number;
      threats: number;
    };
  };
  threat_intelligence: any;
  network_statistics?: {
    total_connections: number;
    active_connections: number;
    bandwidth: {
      rx_bytes: number;
      tx_bytes: number;
      rx_mbps: number;
      tx_mbps: number;
    };
    top_connections?: Array<{ip: string; count: number}>;
  };
  system_statistics?: {
    cpu: {
      load_avg: {"1min": number; "5min": number; "15min": number};
      usage_percent: number;
    };
    memory: {
      total: number;
      used: number;
      available: number;
      usage_percent: number;
    };
    processes: {
      total: number;
      running: number;
      suspicious: number;
    };
  };
  dashboard?: {
    status: string;
    last_update: string;
    event_rate: number;
    threat_level: string;
  };
  timestamp: string;
};

export default function SIEMPage() {
  const [data, setData] = useState<SIEMData | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");
  const [selectedSource, setSelectedSource] = useState<string>("all");

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
      case "critical":
        return "text-red-500 bg-red-900/30 border-red-700";
      case "high":
        return "text-orange-400 bg-orange-900/20 border-orange-700";
      case "medium":
        return "text-yellow-400 bg-yellow-900/20 border-yellow-700";
      case "low":
        return "text-green-400 bg-green-900/20 border-green-700";
      default:
        return "text-slate-400 bg-slate-900/20 border-slate-700";
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case "high":
        return "text-red-400 bg-red-900/30";
      case "medium":
        return "text-yellow-400 bg-yellow-900/30";
      case "low":
        return "text-green-400 bg-green-900/30";
      default:
        return "text-slate-400 bg-slate-900/30";
    }
  };

  const filteredEvents = data?.events.filter(event => {
    if (selectedSeverity !== "all" && event.severity !== selectedSeverity) return false;
    if (selectedSource !== "all" && event.source !== selectedSource) return false;
    return true;
  }) || [];

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
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent">
                🔒 SIEM Security Operations Center
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Real-time Security Information and Event Management
              </p>
            </div>
            <div className="flex items-center gap-4">
              {data?.dashboard && (
                <div className={`px-4 py-2 rounded ${getThreatLevelColor(data.dashboard.threat_level)}`}>
                  <div className="text-xs text-slate-400">Threat Level</div>
                  <div className="text-lg font-bold">{data.dashboard.threat_level.toUpperCase()}</div>
                </div>
              )}
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

          {/* Dashboard Status */}
          {data?.dashboard && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">System Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <div className={`h-3 w-3 rounded-full ${
                      data.dashboard.status === "operational" ? "bg-green-500 animate-pulse" : "bg-red-500"
                    }`}></div>
                    <span className="text-lg font-bold text-green-400 capitalize">{data.dashboard.status}</span>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Event Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-400">{data.dashboard.event_rate}</div>
                  <div className="text-xs text-slate-400">events/min</div>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Last Update</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm font-mono text-slate-300">
                    {new Date(data.dashboard.last_update).toLocaleTimeString()}
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Threat Level</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getThreatLevelColor(data.dashboard.threat_level)}`}>
                    {data.dashboard.threat_level.toUpperCase()}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Metrics Overview */}
          {data?.metrics && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <Card className="bg-gradient-to-br from-red-900/30 to-red-800/30 border-red-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Total Events</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-red-400">{data.metrics.total_events}</div>
                  <div className="text-xs text-slate-400 mt-1">All time</div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-900/30 to-orange-800/30 border-orange-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Critical</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-orange-400">{data.metrics.critical_severity || 0}</div>
                  <div className="text-xs text-slate-400 mt-1">Requires immediate action</div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/30 border-yellow-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">High Severity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-yellow-400">{data.metrics.high_severity}</div>
                  <div className="text-xs text-slate-400 mt-1">Needs attention</div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-900/30 to-purple-800/30 border-purple-700">
                <CardHeader>
                  <CardTitle className="text-sm text-slate-300">Active Threats</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-purple-400">{data.metrics.active_threats}</div>
                  <div className="text-xs text-slate-400 mt-1">Currently detected</div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* System & Network Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* System Statistics */}
            {data?.system_statistics && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>System Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* CPU */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-slate-400">CPU Load Average</span>
                        <span className="text-sm font-mono text-slate-300">
                          {data.system_statistics.cpu.load_avg["1min"].toFixed(2)} / {data.system_statistics.cpu.load_avg["5min"].toFixed(2)} / {data.system_statistics.cpu.load_avg["15min"].toFixed(2)}
                        </span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            data.system_statistics.cpu.load_avg["1min"] < 1 ? "bg-green-500" :
                            data.system_statistics.cpu.load_avg["1min"] < 2 ? "bg-yellow-500" : "bg-red-500"
                          }`}
                          style={{ width: `${Math.min(data.system_statistics.cpu.load_avg["1min"] * 20, 100)}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Memory */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-slate-400">Memory Usage</span>
                        <span className="text-sm font-mono text-slate-300">
                          {data.system_statistics.memory.usage_percent.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            data.system_statistics.memory.usage_percent < 60 ? "bg-green-500" :
                            data.system_statistics.memory.usage_percent < 80 ? "bg-yellow-500" : "bg-red-500"
                          }`}
                          style={{ width: `${data.system_statistics.memory.usage_percent}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        {(data.system_statistics.memory.used / 1024 / 1024).toFixed(0)} MB / {(data.system_statistics.memory.total / 1024 / 1024).toFixed(0)} MB
                      </div>
                    </div>

                    {/* Processes */}
                    <div className="grid grid-cols-3 gap-2">
                      <div className="text-center p-2 bg-slate-800 rounded">
                        <div className="text-lg font-bold text-blue-400">{data.system_statistics.processes.total}</div>
                        <div className="text-xs text-slate-400">Total</div>
                      </div>
                      <div className="text-center p-2 bg-slate-800 rounded">
                        <div className="text-lg font-bold text-green-400">{data.system_statistics.processes.running}</div>
                        <div className="text-xs text-slate-400">Running</div>
                      </div>
                      <div className="text-center p-2 bg-slate-800 rounded">
                        <div className="text-lg font-bold text-red-400">{data.system_statistics.processes.suspicious}</div>
                        <div className="text-xs text-slate-400">Suspicious</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Network Statistics */}
            {data?.network_statistics && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Network Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Connections */}
                    <div className="grid grid-cols-2 gap-2">
                      <div className="text-center p-3 bg-slate-800 rounded">
                        <div className="text-2xl font-bold text-blue-400">{data.network_statistics.total_connections}</div>
                        <div className="text-xs text-slate-400">Total Connections</div>
                      </div>
                      <div className="text-center p-3 bg-slate-800 rounded">
                        <div className="text-2xl font-bold text-green-400">{data.network_statistics.active_connections}</div>
                        <div className="text-xs text-slate-400">Active</div>
                      </div>
                    </div>

                    {/* Bandwidth */}
                    <div>
                      <div className="text-sm text-slate-400 mb-2">Bandwidth Usage</div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-300">RX:</span>
                          <span className="text-sm font-mono text-cyan-400">
                            {data.network_statistics.bandwidth.rx_mbps.toFixed(2)} Mbps
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-300">TX:</span>
                          <span className="text-sm font-mono text-cyan-400">
                            {data.network_statistics.bandwidth.tx_mbps.toFixed(2)} Mbps
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Top Connections */}
                    {data.network_statistics.top_connections && data.network_statistics.top_connections.length > 0 && (
                      <div>
                        <div className="text-sm text-slate-400 mb-2">Top Connections</div>
                        <div className="space-y-1">
                          {data.network_statistics.top_connections.slice(0, 5).map((conn, idx) => (
                            <div key={idx} className="flex items-center justify-between text-xs">
                              <span className="font-mono text-slate-300">{conn.ip}</span>
                              <span className="text-blue-400">{conn.count}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Events by Source & Type */}
          {data?.metrics && (data.metrics.events_by_source || data.metrics.events_by_type) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Events by Source */}
              {data.metrics.events_by_source && Object.keys(data.metrics.events_by_source).length > 0 && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Events by Source</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(data.metrics.events_by_source)
                        .sort((a, b) => b[1] - a[1])
                        .map(([source, count]) => (
                          <div key={source} className="flex items-center justify-between">
                            <span className="text-sm text-slate-300 capitalize">{source}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-24 bg-slate-700 rounded-full h-2">
                                <div
                                  className="bg-blue-500 h-2 rounded-full"
                                  style={{ width: `${(count / data.metrics.total_events) * 100}%` }}
                                ></div>
                              </div>
                              <span className="text-sm font-bold text-blue-400 w-8 text-right">{count}</span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Events by Type */}
              {data.metrics.events_by_type && Object.keys(data.metrics.events_by_type).length > 0 && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Events by Type</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(data.metrics.events_by_type)
                        .sort((a, b) => b[1] - a[1])
                        .map(([type, count]) => (
                          <div key={type} className="flex items-center justify-between">
                            <span className="text-sm text-slate-300">{type.replace(/_/g, " ")}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-24 bg-slate-700 rounded-full h-2">
                                <div
                                  className="bg-purple-500 h-2 rounded-full"
                                  style={{ width: `${(count / data.metrics.total_events) * 100}%` }}
                                ></div>
                              </div>
                              <span className="text-sm font-bold text-purple-400 w-8 text-right">{count}</span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Top IPs */}
          {data?.metrics.top_ips && data.metrics.top_ips.length > 0 && (
            <Card className="bg-slate-900 border-slate-800 mb-6">
              <CardHeader>
                <CardTitle className="text-red-400">Top Threat IPs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.metrics.top_ips.map((ip_data, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-red-900/20 border border-red-700 rounded">
                      <div className="font-mono text-sm text-red-300">{ip_data.ip}</div>
                      <div className="text-lg font-bold text-red-400">{ip_data.count}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Security Events Timeline */}
          <Card className="bg-slate-900 border-slate-800 mb-6">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Security Events Timeline</span>
                <div className="flex items-center gap-4">
                  <select
                    value={selectedSeverity}
                    onChange={(e) => setSelectedSeverity(e.target.value)}
                    className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-sm text-slate-200"
                  >
                    <option value="all">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                  <select
                    value={selectedSource}
                    onChange={(e) => setSelectedSource(e.target.value)}
                    className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-sm text-slate-200"
                  >
                    <option value="all">All Sources</option>
                    {data?.metrics.events_by_source && Object.keys(data.metrics.events_by_source).map(source => (
                      <option key={source} value={source}>{source}</option>
                    ))}
                  </select>
                  <span className="text-sm text-slate-400">
                    Showing {filteredEvents.length} of {data?.events.length || 0} events
                  </span>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredEvents.length > 0 ? (
                  filteredEvents.map((event, idx) => (
                    <div
                      key={idx}
                      className={`p-4 border rounded-lg ${getSeverityColor(event.severity)} hover:bg-opacity-50 transition-all`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`text-xs font-semibold px-2 py-1 rounded ${getSeverityColor(event.severity)}`}>
                              {event.severity.toUpperCase()}
                            </span>
                            <span className="text-xs text-slate-400 capitalize">{event.type.replace(/_/g, " ")}</span>
                            <span className="text-xs text-slate-500">from {event.source}</span>
                            {event.ip && (
                              <span className="text-xs font-mono text-blue-400">{event.ip}</span>
                            )}
                            <span className="text-xs text-slate-500 ml-auto">
                              {new Date(event.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <div className="text-sm text-slate-200 font-mono bg-slate-800/50 p-2 rounded mt-2">
                            {event.message}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center p-8 text-slate-400">
                    <p>No events match the selected filters</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Threat Intelligence */}
          {data?.threat_intelligence && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Threat Intelligence Feed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-slate-800 rounded">
                    <div className="text-2xl font-bold text-blue-400">
                      {data.threat_intelligence.suspicious_ips?.length || 0}
                    </div>
                    <div className="text-xs text-slate-400">Suspicious IPs</div>
                  </div>
                  <div className="text-center p-3 bg-slate-800 rounded">
                    <div className="text-2xl font-bold text-purple-400">
                      {data.threat_intelligence.known_malware_hashes?.length || 0}
                    </div>
                    <div className="text-xs text-slate-400">Malware Hashes</div>
                  </div>
                  <div className="text-center p-3 bg-slate-800 rounded">
                    <div className="text-sm font-mono text-slate-300">
                      {new Date(data.threat_intelligence.threat_feed_updates).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-slate-400">Last Update</div>
                  </div>
                  <div className="text-center p-3 bg-slate-800 rounded">
                    <div className="text-sm text-green-400">Active</div>
                    <div className="text-xs text-slate-400">Feed Status</div>
                  </div>
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
