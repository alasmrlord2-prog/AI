"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import LineChart from "@/components/charts/LineChart";
import BarChart from "@/components/charts/BarChart";
import PieChart from "@/components/charts/PieChart";
import AlertNotification from "@/components/alerts/AlertNotification";

                process.env.NEXT_PUBLIC_BACKEND_URL || 
                "http://ai-agent.bankid-sy.com/api";

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
  entities?: {
    users?: { total: number; high_risk: number; medium_risk: number; low_risk: number };
    controllers?: { total: number; high_risk: number; medium_risk: number; low_risk: number };
    websites?: { total: number; high_risk: number; medium_risk: number; low_risk: number };
    [key: string]: any;
  };
  cases?: Array<{
    id: string;
    severity: number;
    status: string;
    created_at: string;
    type: string;
  }>;
  threat_analysis?: {
    analyzed_events: number;
    correlation_events: number;
    created_cases: number;
  };
  timestamp: string;
};

type Alert = {
  id: string;
  type: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  message: string;
  timestamp: string;
  source?: string;
  read: boolean;
};

export default function SIEMPage() {
  const [data, setData] = useState<SIEMData | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<"7days" | "30days" | "now">("7days");
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [eventHistory, setEventHistory] = useState<Array<{label: string; value: number}>>([]);

  const fetchSIEMData = async () => {
    try {
      const json = await apiRequest("/api/security/siem", {}, 5000);
      setData(json);
      
      // Generate alerts from new events
      if (json.events && json.events.length > 0) {
        const newAlerts: Alert[] = json.events
          .filter((e: any) => e.severity === "critical" || e.severity === "high")
          .slice(0, 5)
          .map((e: any) => ({
            id: `alert-${Date.now()}-${Math.random()}`,
            type: e.severity.toLowerCase() as any,
            title: `${e.severity} Alert: ${e.type}`,
            message: e.message,
            timestamp: e.timestamp,
            source: e.source,
            read: false,
          }));
        
        setAlerts(prev => [...newAlerts, ...prev].slice(0, 20));
      }
      
      // Update event history for charts
      if (json.metrics) {
        const now = new Date();
        const timeLabel = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        setEventHistory(prev => {
          const updated = [...prev, { label: timeLabel, value: json.metrics.total_events }];
          return updated.slice(-12);
        });
      }
    } catch (err) {
      console.error("SIEM fetch error:", err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDismissAlert = (id: string) => {
    setAlerts(prev => prev.filter(a => a.id !== id));
  };
  
  const handleMarkReadAlert = (id: string) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, read: true } : a));
  };

  useEffect(() => {
    fetchSIEMData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchSIEMData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // Generate mock data for Layered Analytics Dashboard
  const generateMockData = () => {
    const now = new Date();
    const sevenDaysAgo = new Date(now);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    // Generate case timeline data (last 7 days)
    const caseTimeline = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      caseTimeline.push({
        date: date.toISOString().split('T')[0],
        catastrophic: Math.floor(Math.random() * 5),
        critical: Math.floor(Math.random() * 8),
        marginal: Math.floor(Math.random() * 10),
        insignificant: Math.floor(Math.random() * 15),
        none: Math.floor(Math.random() * 20),
      });
    }

    // Generate cases
    const totalCases = 44;
    const cases = {
      catastrophic: 3,
      critical: 6,
      marginal: 7,
      insignificant: 10,
      none: 18,
    };

    // Generate workflow stages
    const workflow = {
      queued: 14,
      initial: 9,
      followup: 10,
      final: 11,
      closed: 0,
    };

    // Generate threat analysis funnel
    const threatAnalysis = {
      analyzed: 8858,
      found: 7056,
      created: 55,
    };

    // Generate entity counts
    const entities = {
      users: { total: 1000, high_risk: 2, medium_risk: 31, low_risk: 415 },
      controllers: { total: 1000, high_risk: 1, medium_risk: 51, low_risk: 538 },
      websites: { total: 282, high_risk: 3, medium_risk: 1, low_risk: 4 },
      shares: { total: 0, high_risk: 0, medium_risk: 0, low_risk: 0 },
      projects: { total: 0, high_risk: 0, medium_risk: 0, low_risk: 0 },
      ip_addresses: { total: 0, high_risk: 0, medium_risk: 0, low_risk: 0 },
      printers: { total: 0, high_risk: 0, medium_risk: 0, low_risk: 0 },
      machines: { total: 0, high_risk: 0, medium_risk: 0, low_risk: 0 },
      resources: { total: 0, high_risk: 0, medium_risk: 0, low_risk: 0 },
      files: { total: 0, high_risk: 0, medium_risk: 0, low_risk: 0 },
      servers: { total: 0, high_risk: 0, medium_risk: 0, low_risk: 0 },
    };

    return {
      caseTimeline,
      cases,
      workflow,
      threatAnalysis,
      entities,
      totalCases,
    };
  };

  const mockData = generateMockData();

  // Calculate high risk entities count
  const highRiskEntities = Object.values(mockData.entities).reduce((sum, entity) => sum + entity.high_risk, 0);

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
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                SRG Layered Analytics
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Showing data for <strong>Last 7 days</strong> from {new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toLocaleDateString()} to {new Date().toLocaleDateString()}
              </p>
            </div>
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

          {/* Entity Count Overview */}
          <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 mb-6">
            <CardHeader>
              <CardTitle className="text-xl">
                There are <span className="text-red-400">{highRiskEntities} entities with extremely high risk scores</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {Object.entries(mockData.entities).map(([key, entity]) => (
                  <div key={key} className="bg-slate-800/50 p-3 rounded border border-slate-700">
                    <div className="text-xs text-slate-400 mb-2 capitalize">{key.replace(/_/g, " ")}</div>
                    <div className="text-lg font-bold text-slate-200">{entity.total}</div>
                    <div className="flex gap-2 mt-2 text-xs">
                      {entity.high_risk > 0 && (
                        <span className="text-red-400 font-semibold">{entity.high_risk}</span>
                      )}
                      {entity.medium_risk > 0 && (
                        <span className="text-orange-400">{entity.medium_risk}</span>
                      )}
                      {entity.low_risk > 0 && (
                        <span className="text-yellow-400">{entity.low_risk}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Main Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Case Timeline */}
            <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle>Case Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <LineChart
                    data={mockData.caseTimeline.map((d, idx) => ({
                      label: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                      value: d.catastrophic + d.critical + d.marginal + d.insignificant + d.none,
                    }))}
                    color="#3b82f6"
                    height={240}
                  />
                </div>
                <div className="flex flex-wrap gap-3 mt-4 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-red-500"></div>
                    <span>4-Catastrophic</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-orange-500"></div>
                    <span>3-Critical</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-yellow-500"></div>
                    <span>2-Marginal</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-blue-400"></div>
                    <span>1-Insignificant</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-slate-600"></div>
                    <span>0-None</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Case Breakdown */}
            <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle>Case Breakdown</CardTitle>
                <p className="text-xs text-slate-400 mt-1">As of now</p>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center">
                  <div className="relative">
                    <PieChart
                      data={[
                        { label: "4-Catastrophic", value: mockData.cases.catastrophic, color: "#ef4444" },
                        { label: "3-Critical", value: mockData.cases.critical, color: "#f97316" },
                        { label: "2-Marginal", value: mockData.cases.marginal, color: "#eab308" },
                        { label: "1-Insignificant", value: mockData.cases.insignificant, color: "#60a5fa" },
                        { label: "0-None", value: mockData.cases.none, color: "#475569" },
                      ]}
                      size={200}
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-slate-200">TOTAL</div>
                        <div className="text-3xl font-bold text-indigo-400">{mockData.totalCases}</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-red-500"></div>
                      <span>4-Catastrophic</span>
                    </div>
                    <span className="font-semibold">{mockData.cases.catastrophic} ({((mockData.cases.catastrophic / mockData.totalCases) * 100).toFixed(2)}%)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-orange-500"></div>
                      <span>3-Critical</span>
                    </div>
                    <span className="font-semibold">{mockData.cases.critical} ({((mockData.cases.critical / mockData.totalCases) * 100).toFixed(2)}%)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-yellow-500"></div>
                      <span>2-Marginal</span>
                    </div>
                    <span className="font-semibold">{mockData.cases.marginal} ({((mockData.cases.marginal / mockData.totalCases) * 100).toFixed(2)}%)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-blue-400"></div>
                      <span>1-Insignificant</span>
                    </div>
                    <span className="font-semibold">{mockData.cases.insignificant} ({((mockData.cases.insignificant / mockData.totalCases) * 100).toFixed(2)}%)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-slate-600"></div>
                      <span>0-None</span>
                    </div>
                    <span className="font-semibold">{mockData.cases.none} ({((mockData.cases.none / mockData.totalCases) * 100).toFixed(2)}%)</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Case Workflow Analysis & Threat Analysis Funnel */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Case Workflow Analysis */}
            <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle>Case Workflow Analysis</CardTitle>
                <div className="flex gap-4 mt-2">
                  <label className="flex items-center gap-2 text-xs cursor-pointer">
                    <input
                      type="radio"
                      name="period"
                      checked={selectedPeriod === "7days"}
                      onChange={() => setSelectedPeriod("7days")}
                      className="w-3 h-3"
                    />
                    <span>Selected Period</span>
                  </label>
                  <label className="flex items-center gap-2 text-xs cursor-pointer">
                    <input
                      type="radio"
                      name="period"
                      checked={selectedPeriod === "now"}
                      onChange={() => setSelectedPeriod("now")}
                      className="w-3 h-3"
                    />
                    <span>As of Now</span>
                  </label>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-4">
                  {[
                    { name: "Queued", count: mockData.workflow.queued, percentage: ((mockData.workflow.queued / mockData.totalCases) * 100).toFixed(2) },
                    { name: "Initial", count: mockData.workflow.initial, percentage: ((mockData.workflow.initial / mockData.totalCases) * 100).toFixed(2) },
                    { name: "Follow-up", count: mockData.workflow.followup, percentage: ((mockData.workflow.followup / mockData.totalCases) * 100).toFixed(2) },
                    { name: "Final", count: mockData.workflow.final, percentage: ((mockData.workflow.final / mockData.totalCases) * 100).toFixed(2) },
                    { name: "Closed", count: mockData.workflow.closed, percentage: "0.00" },
                  ].map((stage, idx) => (
                    <div key={idx} className="flex flex-col items-center">
                      <div className="w-16 h-16 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold mb-2 relative">
                        {stage.count}
                        {idx < 4 && (
                          <div className="absolute -right-8 top-1/2 transform -translate-y-1/2">
                            <div className="w-8 h-0.5 bg-indigo-400"></div>
                            <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-0 h-0 border-l-4 border-l-indigo-400 border-t-2 border-t-transparent border-b-2 border-b-transparent"></div>
                          </div>
                        )}
                      </div>
                      <div className="text-xs text-center">
                        <div className="font-semibold">{stage.name}</div>
                        <div className="text-slate-400">{stage.percentage}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Threat Analysis Funnel */}
            <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle>Threat Analysis Funnel</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Analyzed */}
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400 mb-2">
                      {mockData.threatAnalysis.analyzed.toLocaleString()} Events
                    </div>
                    <div className="text-sm text-slate-400">Analyzed</div>
                  </div>
                  
                  {/* Arrow */}
                  <div className="flex justify-center">
                    <div className="text-center">
                      <div className="text-lg font-bold text-indigo-400 mb-1">
                        {((mockData.threatAnalysis.found / mockData.threatAnalysis.analyzed) * 100).toFixed(2)}%
                      </div>
                      <div className="w-0.5 h-12 bg-indigo-400 mx-auto"></div>
                    </div>
                  </div>

                  {/* Found */}
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400 mb-2">
                      {mockData.threatAnalysis.found.toLocaleString()} Correlation Events
                    </div>
                    <div className="text-sm text-slate-400">Found</div>
                  </div>

                  {/* Arrow */}
                  <div className="flex justify-center">
                    <div className="text-center">
                      <div className="text-lg font-bold text-indigo-400 mb-1">
                        {((mockData.threatAnalysis.created / mockData.threatAnalysis.found) * 100).toFixed(2)}%
                      </div>
                      <div className="w-0.5 h-12 bg-indigo-400 mx-auto"></div>
                    </div>
                  </div>

                  {/* Created */}
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400 mb-2">
                      {mockData.threatAnalysis.created} Cases
                    </div>
                    <div className="text-sm text-slate-400">Created</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Security Events Timeline */}
          {data?.events && data.events.length > 0 && (
            <Card className="bg-slate-900 border-slate-800 mb-6">
              <CardHeader>
                <CardTitle>Security Events Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {data.events.slice(0, 20).map((event, idx) => (
                    <div
                      key={idx}
                      className={`p-4 border rounded-lg ${
                        event.severity === "critical" ? "bg-red-900/20 border-red-700" :
                        event.severity === "high" ? "bg-orange-900/20 border-orange-700" :
                        event.severity === "medium" ? "bg-yellow-900/20 border-yellow-700" :
                        "bg-slate-800/50 border-slate-700"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`text-xs font-semibold px-2 py-1 rounded ${
                              event.severity === "critical" ? "bg-red-700 text-red-200" :
                              event.severity === "high" ? "bg-orange-700 text-orange-200" :
                              event.severity === "medium" ? "bg-yellow-700 text-yellow-200" :
                              "bg-slate-700 text-slate-200"
                            }`}>
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
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
      
      {/* Real-time Alerts */}
      <AlertNotification
        alerts={alerts}
        onDismiss={handleDismissAlert}
        onMarkRead={handleMarkReadAlert}
      />
    </div>
  );
}
