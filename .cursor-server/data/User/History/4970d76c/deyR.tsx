"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import LineChart from "@/components/charts/LineChart";
import BarChart from "@/components/charts/BarChart";
import PieChart from "@/components/charts/PieChart";
import AlertNotification from "@/components/alerts/AlertNotification";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 
                process.env.NEXT_PUBLIC_BACKEND_URL || 
                "http://localhost:8000";

type IncidentCase = {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "open" | "investigating" | "contained" | "resolved" | "closed";
  source: string;
  timestamp: string;
  description: string;
  affected_assets?: string[];
  assigned_to?: string;
  tags?: string[];
  evidence?: Array<{type: string; data: string; timestamp: string}>;
  timeline?: Array<{event: string; timestamp: string}>;
};

type ThreatIntelligence = {
  ip: string;
  reputation: string;
  threat_level: string;
  checks: Array<{source: string; status: string; message: string}>;
  related_ips?: string[];
  related_domains?: string[];
  malware_samples?: Array<{hash: string; type: string}>;
};

type AttackSimulation = {
  id: string;
  type: string;
  status: "pending" | "running" | "completed" | "failed";
  target: string;
  started_at?: string;
  completed_at?: string;
  results?: any;
};

type AutoresponseRule = {
  id: string;
  name: string;
  enabled: boolean;
  conditions: {
    severity?: string[];
    source?: string[];
    type?: string[];
  };
  actions: {
    type: "block_ip" | "isolate_asset" | "notify" | "escalate" | "quarantine";
    params?: Record<string, any>;
  }[];
};

type Investigation = {
  id: string;
  case_id: string;
  type: "network" | "malware" | "forensics" | "threat_intel";
  status: "pending" | "running" | "completed";
  started_at: string;
  results?: any;
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

export default function SOCPage() {
  const [activeTab, setActiveTab] = useState<"incidents" | "threat_intel" | "simulation" | "autoresponse" | "investigation" | "malware" | "forensics" | "reporting" | "ml_patterns">("incidents");
  const [incidents, setIncidents] = useState<IncidentCase[]>([]);
  const [threatData, setThreatData] = useState<ThreatIntelligence[]>([]);
  const [simulations, setSimulations] = useState<AttackSimulation[]>([]);
  const [autoresponseRules, setAutoresponseRules] = useState<AutoresponseRule[]>([]);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<IncidentCase | null>(null);
  const [threatIpInput, setThreatIpInput] = useState("");
  const [simulationType, setSimulationType] = useState("port_scan");
  const [simulationTarget, setSimulationTarget] = useState("");
  const [incidentTrend, setIncidentTrend] = useState<Array<{label: string; value: number}>>([]);
  const [mlPatterns, setMlPatterns] = useState<Array<{pattern: string; confidence: number; description: string}>>([]);
  const [threatFeeds, setThreatFeeds] = useState<Array<{source: string; status: string; last_update: string; threats: number}>>([]);

  useEffect(() => {
    loadIncidents();
    loadThreatIntelligence();
    loadSimulations();
    loadAutoresponseRules();
    loadInvestigations();
    loadThreatFeeds();
    loadMLPatterns();
  }, []);

  const getAuthToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  };

  const loadIncidents = async () => {
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/security/siem`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        // Convert SIEM events to incidents
        const incidentCases: IncidentCase[] = (data.events || []).slice(0, 20).map((event: any, idx: number) => ({
          id: `inc-${idx}`,
          title: `${event.type} - ${event.source}`,
          severity: event.severity.toLowerCase() as any,
          status: "open" as any,
          source: event.source,
          timestamp: event.timestamp,
          description: event.message,
          affected_assets: event.ip ? [event.ip] : [],
          tags: [event.type, event.source],
        }));
        setIncidents(incidentCases);
        
        // Generate alerts from critical incidents
        const criticalIncidents = incidentCases.filter(i => i.severity === "critical" || i.severity === "high");
        const newAlerts: Alert[] = criticalIncidents.slice(0, 5).map(inc => ({
          id: `alert-${inc.id}`,
          type: inc.severity as any,
          title: `Incident: ${inc.title}`,
          message: inc.description,
          timestamp: inc.timestamp,
          source: inc.source,
          read: false,
        }));
        setAlerts(prev => [...newAlerts, ...prev].slice(0, 20));
        
        // Update incident trend
        const now = new Date();
        const timeLabel = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        setIncidentTrend(prev => {
          const updated = [...prev, { label: timeLabel, value: incidentCases.length }];
          return updated.slice(-12);
        });
      }
    } catch (err) {
      console.error("Failed to load incidents:", err);
    }
  };
  
  const handleDismissAlert = (id: string) => {
    setAlerts(prev => prev.filter(a => a.id !== id));
  };
  
  const handleMarkReadAlert = (id: string) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, read: true } : a));
  };
  
  const loadThreatFeeds = async () => {
    // Simulate threat feed data
    setThreatFeeds([
      { source: "AbuseIPDB", status: "active", last_update: new Date().toISOString(), threats: 1250 },
      { source: "VirusTotal", status: "active", last_update: new Date().toISOString(), threats: 3420 },
      { source: "Shodan", status: "active", last_update: new Date().toISOString(), threats: 890 },
      { source: "AlienVault OTX", status: "active", last_update: new Date().toISOString(), threats: 2100 },
    ]);
  };
  
  const loadMLPatterns = async () => {
    // Simulate ML pattern detection
    setMlPatterns([
      { pattern: "Brute Force Attack Pattern", confidence: 0.94, description: "Multiple failed login attempts from same IP" },
      { pattern: "Port Scanning Pattern", confidence: 0.87, description: "Sequential port scanning detected" },
      { pattern: "Data Exfiltration Pattern", confidence: 0.82, description: "Unusual outbound data transfer" },
      { pattern: "Privilege Escalation Pattern", confidence: 0.79, description: "Suspicious privilege escalation attempts" },
      { pattern: "Malware Communication Pattern", confidence: 0.91, description: "Communication with known C2 servers" },
    ]);
  };

  const loadThreatIntelligence = async () => {
    // Load threat intelligence data
    setThreatData([]);
  };

  const loadSimulations = async () => {
    setSimulations([]);
  };

  const loadAutoresponseRules = async () => {
    const defaultRules: AutoresponseRule[] = [
      {
        id: "rule-1",
        name: "Auto-block Critical Threats",
        enabled: true,
        conditions: { severity: ["critical"] },
        actions: [{ type: "block_ip" }],
      },
      {
        id: "rule-2",
        name: "Isolate Suspicious Assets",
        enabled: true,
        conditions: { severity: ["high", "critical"] },
        actions: [{ type: "isolate_asset" }],
      },
    ];
    setAutoresponseRules(defaultRules);
  };

  const loadInvestigations = async () => {
    setInvestigations([]);
  };

  const handleThreatIntelligenceCheck = async () => {
    if (!threatIpInput) return;
    setLoading(true);
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/security/advanced/threat_intelligence`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ip: threatIpInput }),
      });
      if (res.ok) {
        const data = await res.json();
        setThreatData([...threatData, data]);
        setThreatIpInput("");
      }
    } catch (err) {
      console.error("Threat intelligence check failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSimulation = async () => {
    if (!simulationTarget) return;
    setLoading(true);
    try {
      const token = getAuthToken();
      let endpoint = "";
      let body: any = {};

      switch (simulationType) {
        case "port_scan":
          endpoint = "/api/security/scan_port_scan";
          body = { target: simulationTarget };
          break;
        case "penetration_test":
          endpoint = "/api/security/scan_penetration_test";
          body = { target: simulationTarget };
          break;
        case "vulnerability":
          endpoint = "/api/security/scan_vulnerabilities";
          body = { path: simulationTarget };
          break;
      }

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        const data = await res.json();
        const newSim: AttackSimulation = {
          id: `sim-${Date.now()}`,
          type: simulationType,
          status: "completed",
          target: simulationTarget,
          started_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
          results: data,
        };
        setSimulations([...simulations, newSim]);
        setSimulationTarget("");
      }
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleMalwareAnalysis = async (filePath: string) => {
    setLoading(true);
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/security/scan_malware`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path: filePath }),
      });
      if (res.ok) {
        const data = await res.json();
        // Add to investigations
        const inv: Investigation = {
          id: `inv-${Date.now()}`,
          case_id: "malware-analysis",
          type: "malware",
          status: "completed",
          started_at: new Date().toISOString(),
          results: data,
        };
        setInvestigations([...investigations, inv]);
      }
    } catch (err) {
      console.error("Malware analysis failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleForensicsAnalysis = async (type: "memory" | "disk" | "network", path?: string) => {
    setLoading(true);
    try {
      const token = getAuthToken();
      let endpoint = "";
      let body: any = {};
      
      if (type === "memory") {
        endpoint = "/api/security/advanced/memory_forensics";
        body = {};
      } else if (type === "disk") {
        endpoint = "/api/security/advanced/disk_forensics";
        body = { path: path || "/" };
      } else if (type === "network") {
        endpoint = "/api/security/advanced/network_forensics";
        body = { path: path || "/tmp" };
      }
      
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        const data = await res.json();
        const inv: Investigation = {
          id: `inv-${Date.now()}`,
          case_id: "forensics",
          type: "forensics",
          status: "completed",
          started_at: new Date().toISOString(),
          results: data,
        };
        setInvestigations([...investigations, inv]);
      }
    } catch (err) {
      console.error("Forensics analysis failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "critical": return "text-red-500 bg-red-900/30 border-red-700";
      case "high": return "text-orange-400 bg-orange-900/20 border-orange-700";
      case "medium": return "text-yellow-400 bg-yellow-900/20 border-yellow-700";
      case "low": return "text-green-400 bg-green-900/20 border-green-700";
      default: return "text-slate-400 bg-slate-900/20 border-slate-700";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open": return "bg-red-500";
      case "investigating": return "bg-yellow-500";
      case "contained": return "bg-blue-500";
      case "resolved": return "bg-green-500";
      case "closed": return "bg-slate-500";
      default: return "bg-slate-500";
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-500 bg-clip-text text-transparent">
              🛡️ Security Operations Center (SOC)
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Comprehensive Security Operations and Incident Response
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b border-slate-800 overflow-x-auto">
            {[
              { id: "incidents", label: "Incident Cases", icon: "📋" },
              { id: "threat_intel", label: "Threat Intelligence", icon: "🌐" },
              { id: "simulation", label: "Attack Simulation", icon: "🎯" },
              { id: "autoresponse", label: "Autoresponse", icon: "⚡" },
              { id: "investigation", label: "Investigation Tools", icon: "🔍" },
              { id: "malware", label: "Malware Analysis", icon: "🦠" },
              { id: "forensics", label: "Forensics", icon: "🔬" },
              { id: "reporting", label: "Advanced Reporting", icon: "📊" },
              { id: "ml_patterns", label: "ML Patterns", icon: "🤖" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? "border-cyan-500 text-cyan-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          {/* Incident Cases Tab */}
          {activeTab === "incidents" && (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-4 mb-6">
                <Card className="bg-gradient-to-br from-red-900/30 to-red-800/30 border-red-700">
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-red-400">
                      {incidents.filter(i => i.severity === "critical").length}
                    </div>
                    <div className="text-xs text-slate-400">Critical</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-orange-900/30 to-orange-800/30 border-orange-700">
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-orange-400">
                      {incidents.filter(i => i.severity === "high").length}
                    </div>
                    <div className="text-xs text-slate-400">High</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/30 border-yellow-700">
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-yellow-400">
                      {incidents.filter(i => i.status === "open").length}
                    </div>
                    <div className="text-xs text-slate-400">Open Cases</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-900/30 to-blue-800/30 border-blue-700">
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-blue-400">{incidents.length}</div>
                    <div className="text-xs text-slate-400">Total Incidents</div>
                  </CardContent>
                </Card>
              </div>

              {/* Charts for Incidents */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Incident Trend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <LineChart
                      data={incidentTrend.length > 0 ? incidentTrend : [
                        { label: "00:00", value: 0 },
                        { label: "00:05", value: 0 },
                      ]}
                      color="#3b82f6"
                      height={200}
                    />
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Incidents by Severity</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <PieChart
                      data={[
                        { label: "Critical", value: incidents.filter(i => i.severity === "critical").length, color: "#ef4444" },
                        { label: "High", value: incidents.filter(i => i.severity === "high").length, color: "#f59e0b" },
                        { label: "Medium", value: incidents.filter(i => i.severity === "medium").length, color: "#eab308" },
                        { label: "Low", value: incidents.filter(i => i.severity === "low").length, color: "#10b981" },
                      ].filter(d => d.value > 0)}
                      size={200}
                    />
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Incidents by Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <BarChart
                      data={[
                        { label: "Open", value: incidents.filter(i => i.status === "open").length },
                        { label: "Investigating", value: incidents.filter(i => i.status === "investigating").length },
                        { label: "Contained", value: incidents.filter(i => i.status === "contained").length },
                        { label: "Resolved", value: incidents.filter(i => i.status === "resolved").length },
                        { label: "Closed", value: incidents.filter(i => i.status === "closed").length },
                      ].filter(d => d.value > 0)}
                      color="#8b5cf6"
                      height={200}
                    />
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Incidents by Source</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <BarChart
                      data={Object.entries(
                        incidents.reduce((acc, inc) => {
                          acc[inc.source] = (acc[inc.source] || 0) + 1;
                          return acc;
                        }, {} as Record<string, number>)
                      )
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 8)
                        .map(([label, value]) => ({ label, value }))}
                      color="#ec4899"
                      height={200}
                    />
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Incident Cases</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {incidents.map((incident) => (
                      <div
                        key={incident.id}
                        onClick={() => setSelectedIncident(incident)}
                        className={`p-4 border rounded-lg cursor-pointer hover:bg-slate-800 transition-all ${getSeverityColor(incident.severity)}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className={`text-xs font-semibold px-2 py-1 rounded ${getSeverityColor(incident.severity)}`}>
                                {incident.severity.toUpperCase()}
                              </span>
                              <span className={`h-2 w-2 rounded-full ${getStatusColor(incident.status)}`}></span>
                              <span className="text-sm text-slate-300">{incident.title}</span>
                              <span className="text-xs text-slate-500 ml-auto">
                                {new Date(incident.timestamp).toLocaleString()}
                              </span>
                            </div>
                            <div className="text-sm text-slate-300">{incident.description}</div>
                            <div className="flex gap-2 mt-2">
                              <span className="text-xs text-slate-400">Source: {incident.source}</span>
                              {incident.affected_assets && incident.affected_assets.length > 0 && (
                                <span className="text-xs text-slate-400">
                                  Assets: {incident.affected_assets.join(", ")}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {selectedIncident && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Incident Details</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-lg font-bold mb-2">{selectedIncident.title}</h3>
                        <p className="text-sm text-slate-300">{selectedIncident.description}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs text-slate-400">Severity</div>
                          <div className={`text-sm font-bold ${getSeverityColor(selectedIncident.severity)}`}>
                            {selectedIncident.severity.toUpperCase()}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400">Status</div>
                          <div className="text-sm font-bold text-slate-300">{selectedIncident.status}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400">Source</div>
                          <div className="text-sm text-slate-300">{selectedIncident.source}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400">Timestamp</div>
                          <div className="text-sm text-slate-300">
                            {new Date(selectedIncident.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <Button onClick={() => setSelectedIncident(null)} className="bg-slate-700">
                        Close
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Threat Intelligence Tab */}
          {activeTab === "threat_intel" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Threat Intelligence Check</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2 mb-4">
                    <Input
                      value={threatIpInput}
                      onChange={(e) => setThreatIpInput(e.target.value)}
                      placeholder="Enter IP address or domain"
                      className="bg-slate-800 border-slate-700"
                    />
                    <Button
                      onClick={handleThreatIntelligenceCheck}
                      disabled={loading}
                      className="bg-cyan-600 hover:bg-cyan-700"
                    >
                      {loading ? "Checking..." : "Check"}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {threatData.map((threat, idx) => (
                  <Card key={idx} className="bg-slate-900 border-slate-800">
                    <CardHeader>
                      <CardTitle className="text-cyan-400">{threat.ip}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div>
                          <span className="text-xs text-slate-400">Reputation: </span>
                          <span className={`text-sm font-bold ${
                            threat.reputation === "malicious" ? "text-red-400" :
                            threat.reputation === "suspicious" ? "text-yellow-400" :
                            "text-green-400"
                          }`}>
                            {threat.reputation}
                          </span>
                        </div>
                        <div>
                          <span className="text-xs text-slate-400">Threat Level: </span>
                          <span className="text-sm font-bold text-orange-400">{threat.threat_level}</span>
                        </div>
                        <div className="mt-4">
                          <div className="text-xs text-slate-400 mb-2">Intelligence Checks:</div>
                          {threat.checks.map((check, cidx) => (
                            <div key={cidx} className="text-xs p-2 bg-slate-800 rounded mb-1">
                              <span className="font-mono text-cyan-400">{check.source}:</span> {check.message}
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Threat Intelligence Graph Visualization */}
              {threatData.length > 0 && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Threat Intelligence Graph</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 bg-slate-800 rounded flex items-center justify-center">
                      <div className="text-center text-slate-400">
                        <div className="text-4xl mb-2">🌐</div>
                        <div>Threat Intelligence Network Graph</div>
                        <div className="text-xs mt-2">
                          {threatData.length} threat(s) analyzed
                        </div>
                        {/* In a real implementation, you would use a graph library like vis.js or d3.js */}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Attack Simulation Tab */}
          {activeTab === "simulation" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Attack Self Simulation</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-slate-400 mb-2 block">Simulation Type</label>
                      <select
                        value={simulationType}
                        onChange={(e) => setSimulationType(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200"
                      >
                        <option value="port_scan">Port Scan</option>
                        <option value="penetration_test">Penetration Test</option>
                        <option value="vulnerability">Vulnerability Scan</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-sm text-slate-400 mb-2 block">Target</label>
                      <Input
                        value={simulationTarget}
                        onChange={(e) => setSimulationTarget(e.target.value)}
                        placeholder="IP address, domain, or path"
                        className="bg-slate-800 border-slate-700"
                      />
                    </div>
                    <Button
                      onClick={handleRunSimulation}
                      disabled={loading || !simulationTarget}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      {loading ? "Running..." : "Run Simulation"}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Simulation History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {simulations.map((sim) => (
                      <div key={sim.id} className="p-4 border border-slate-700 rounded">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-bold text-purple-400">{sim.type}</span>
                          <span className={`text-xs px-2 py-1 rounded ${
                            sim.status === "completed" ? "bg-green-900/30 text-green-400" :
                            sim.status === "running" ? "bg-yellow-900/30 text-yellow-400" :
                            "bg-slate-700 text-slate-400"
                          }`}>
                            {sim.status}
                          </span>
                        </div>
                        <div className="text-sm text-slate-300">Target: {sim.target}</div>
                        {sim.completed_at && (
                          <div className="text-xs text-slate-400 mt-1">
                            Completed: {new Date(sim.completed_at).toLocaleString()}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Autoresponse Tab */}
          {activeTab === "autoresponse" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Autoresponse Rules</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {autoresponseRules.map((rule) => (
                      <div key={rule.id} className="p-4 border border-slate-700 rounded">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={rule.enabled}
                              onChange={(e) => {
                                const updated = autoresponseRules.map(r =>
                                  r.id === rule.id ? { ...r, enabled: e.target.checked } : r
                                );
                                setAutoresponseRules(updated);
                              }}
                              className="w-4 h-4"
                            />
                            <span className="font-bold text-cyan-400">{rule.name}</span>
                          </div>
                        </div>
                        <div className="text-sm text-slate-300 mb-2">
                          Conditions: {JSON.stringify(rule.conditions)}
                        </div>
                        <div className="text-sm text-slate-300">
                          Actions: {rule.actions.map(a => a.type).join(", ")}
                        </div>
                      </div>
                    ))}
                    <Button className="bg-cyan-600 hover:bg-cyan-700">
                      + Add New Rule
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Investigation Tools Tab */}
          {activeTab === "investigation" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Investigation Tools</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Button
                      onClick={() => handleForensicsAnalysis("network")}
                      className="bg-blue-600 hover:bg-blue-700 h-20"
                    >
                      <div>
                        <div className="text-2xl mb-1">🌐</div>
                        <div className="text-xs">Network Forensics</div>
                      </div>
                    </Button>
                    <Button
                      onClick={() => handleForensicsAnalysis("memory")}
                      className="bg-purple-600 hover:bg-purple-700 h-20"
                    >
                      <div>
                        <div className="text-2xl mb-1">💾</div>
                        <div className="text-xs">Memory Forensics</div>
                      </div>
                    </Button>
                    <Button
                      onClick={() => handleForensicsAnalysis("disk", "/")}
                      className="bg-orange-600 hover:bg-orange-700 h-20"
                    >
                      <div>
                        <div className="text-2xl mb-1">💿</div>
                        <div className="text-xs">Disk Forensics</div>
                      </div>
                    </Button>
                    <Button
                      onClick={() => handleThreatIntelligenceCheck()}
                      className="bg-cyan-600 hover:bg-cyan-700 h-20"
                    >
                      <div>
                        <div className="text-2xl mb-1">🔍</div>
                        <div className="text-xs">Threat Intel</div>
                      </div>
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Investigation History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {investigations.map((inv) => (
                      <div key={inv.id} className="p-4 border border-slate-700 rounded">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-bold text-blue-400">{inv.type}</span>
                          <span className={`text-xs px-2 py-1 rounded ${
                            inv.status === "completed" ? "bg-green-900/30 text-green-400" :
                            "bg-yellow-900/30 text-yellow-400"
                          }`}>
                            {inv.status}
                          </span>
                        </div>
                        <div className="text-sm text-slate-300">
                          Started: {new Date(inv.started_at).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Malware Analysis Tab */}
          {activeTab === "malware" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Malware Analysis Tools</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-slate-400 mb-2 block">File Path to Analyze</label>
                      <div className="flex gap-2">
                        <Input
                          id="malware-path"
                          placeholder="/path/to/file"
                          className="bg-slate-800 border-slate-700"
                        />
                        <Button
                          onClick={() => {
                            const input = document.getElementById("malware-path") as HTMLInputElement;
                            if (input?.value) handleMalwareAnalysis(input.value);
                          }}
                          disabled={loading}
                          className="bg-red-600 hover:bg-red-700"
                        >
                          {loading ? "Analyzing..." : "Analyze"}
                        </Button>
                      </div>
                    </div>
                    <div className="text-xs text-slate-400">
                      Supported: File hash analysis, signature detection, behavioral analysis
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Analysis Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {investigations.filter(i => i.type === "malware").map((inv) => (
                      <div key={inv.id} className="p-4 border border-red-700 rounded bg-red-900/10">
                        <div className="text-sm text-red-400 font-bold mb-2">Malware Analysis</div>
                        <pre className="text-xs text-slate-300 overflow-auto max-h-64">
                          {JSON.stringify(inv.results, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Forensics Tab */}
          {activeTab === "forensics" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Forensics Interface</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="bg-slate-800 border-slate-700">
                      <CardHeader>
                        <CardTitle className="text-lg">Memory Forensics</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-slate-400 mb-4">
                          Analyze running processes, memory dumps, and volatile data
                        </p>
                        <Button
                          onClick={() => handleForensicsAnalysis("memory")}
                          disabled={loading}
                          className="w-full bg-purple-600 hover:bg-purple-700"
                        >
                          {loading ? "Analyzing..." : "Run Memory Forensics"}
                        </Button>
                      </CardContent>
                    </Card>

                    <Card className="bg-slate-800 border-slate-700">
                      <CardHeader>
                        <CardTitle className="text-lg">Disk Forensics</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 mb-4">
                          <Input
                            id="disk-path"
                            placeholder="/path/to/analyze"
                            defaultValue="/"
                            className="bg-slate-700 border-slate-600"
                          />
                        </div>
                        <Button
                          onClick={() => {
                            const input = document.getElementById("disk-path") as HTMLInputElement;
                            handleForensicsAnalysis("disk", input?.value || "/");
                          }}
                          disabled={loading}
                          className="w-full bg-orange-600 hover:bg-orange-700"
                        >
                          {loading ? "Analyzing..." : "Run Disk Forensics"}
                        </Button>
                      </CardContent>
                    </Card>

                    <Card className="bg-slate-800 border-slate-700">
                      <CardHeader>
                        <CardTitle className="text-lg">Network Forensics</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-slate-400 mb-4">
                          Analyze network traffic, packet captures, and connections
                        </p>
                        <Button
                          onClick={() => handleForensicsAnalysis("network")}
                          disabled={loading}
                          className="w-full bg-blue-600 hover:bg-blue-700"
                        >
                          {loading ? "Analyzing..." : "Run Network Forensics"}
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Forensics Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {investigations.filter(i => i.type === "forensics").map((inv) => (
                      <div key={inv.id} className="p-4 border border-slate-700 rounded">
                        <div className="text-sm font-bold text-cyan-400 mb-2">Forensics Analysis</div>
                        <pre className="text-xs text-slate-300 overflow-auto max-h-96">
                          {JSON.stringify(inv.results, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Advanced Reporting Tab */}
          {activeTab === "reporting" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Advanced Reporting</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Button className="bg-blue-600 hover:bg-blue-700 h-20">
                        <div>
                          <div className="text-2xl mb-1">📄</div>
                          <div className="text-xs">Generate Security Report</div>
                        </div>
                      </Button>
                      <Button className="bg-purple-600 hover:bg-purple-700 h-20">
                        <div>
                          <div className="text-2xl mb-1">📊</div>
                          <div className="text-xs">Incident Summary</div>
                        </div>
                      </Button>
                      <Button className="bg-green-600 hover:bg-green-700 h-20">
                        <div>
                          <div className="text-2xl mb-1">📈</div>
                          <div className="text-xs">Trend Analysis</div>
                        </div>
                      </Button>
                    </div>

                    <div className="mt-6">
                      <h3 className="text-lg font-bold mb-4">Report Templates</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Card className="bg-slate-800 border-slate-700">
                          <CardHeader>
                            <CardTitle className="text-sm">Daily Security Report</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-xs text-slate-400 mb-2">
                              Summary of all security events and incidents for the day
                            </p>
                            <Button className="w-full bg-slate-700 hover:bg-slate-600 text-xs">
                              Generate Report
                            </Button>
                          </CardContent>
                        </Card>
                        <Card className="bg-slate-800 border-slate-700">
                          <CardHeader>
                            <CardTitle className="text-sm">Weekly Threat Intelligence</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-xs text-slate-400 mb-2">
                              Comprehensive threat intelligence and pattern analysis
                            </p>
                            <Button className="w-full bg-slate-700 hover:bg-slate-600 text-xs">
                              Generate Report
                            </Button>
                          </CardContent>
                        </Card>
                        <Card className="bg-slate-800 border-slate-700">
                          <CardHeader>
                            <CardTitle className="text-sm">Incident Response Report</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-xs text-slate-400 mb-2">
                              Detailed analysis of incident response activities
                            </p>
                            <Button className="w-full bg-slate-700 hover:bg-slate-600 text-xs">
                              Generate Report
                            </Button>
                          </CardContent>
                        </Card>
                        <Card className="bg-slate-800 border-slate-700">
                          <CardHeader>
                            <CardTitle className="text-sm">Compliance Report</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-xs text-slate-400 mb-2">
                              Security compliance and audit report
                            </p>
                            <Button className="w-full bg-slate-700 hover:bg-slate-600 text-xs">
                              Generate Report
                            </Button>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* ML Patterns Tab */}
          {activeTab === "ml_patterns" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Machine Learning Pattern Detection</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                      <Card className="bg-slate-800 border-slate-700">
                        <CardHeader>
                          <CardTitle className="text-sm">Detected Patterns</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold text-cyan-400">{mlPatterns.length}</div>
                          <div className="text-xs text-slate-400">Active Patterns</div>
                        </CardContent>
                      </Card>
                      <Card className="bg-slate-800 border-slate-700">
                        <CardHeader>
                          <CardTitle className="text-sm">Average Confidence</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold text-green-400">
                            {mlPatterns.length > 0
                              ? (mlPatterns.reduce((sum, p) => sum + p.confidence, 0) / mlPatterns.length * 100).toFixed(1)
                              : "0"}%
                          </div>
                          <div className="text-xs text-slate-400">ML Accuracy</div>
                        </CardContent>
                      </Card>
                    </div>

                    <div className="space-y-2">
                      {mlPatterns.map((pattern, idx) => (
                        <Card key={idx} className="bg-slate-800 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-lg">🤖</span>
                                  <span className="font-bold text-cyan-400">{pattern.pattern}</span>
                                  <span className={`text-xs px-2 py-1 rounded ${
                                    pattern.confidence > 0.9 ? "bg-green-900/30 text-green-400" :
                                    pattern.confidence > 0.8 ? "bg-yellow-900/30 text-yellow-400" :
                                    "bg-orange-900/30 text-orange-400"
                                  }`}>
                                    {(pattern.confidence * 100).toFixed(0)}% confidence
                                  </span>
                                </div>
                                <p className="text-sm text-slate-300">{pattern.description}</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Threat Feeds Integration */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>External Threat Feeds Integration</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {threatFeeds.map((feed, idx) => (
                      <div key={idx} className="p-4 border border-slate-700 rounded flex items-center justify-between">
                        <div>
                          <div className="font-bold text-blue-400">{feed.source}</div>
                          <div className="text-xs text-slate-400">
                            Status: <span className={feed.status === "active" ? "text-green-400" : "text-red-400"}>{feed.status}</span>
                          </div>
                          <div className="text-xs text-slate-400">
                            Last Update: {new Date(feed.last_update).toLocaleString()}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-purple-400">{feed.threats}</div>
                          <div className="text-xs text-slate-400">Threats</div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4">
                    <Button className="bg-cyan-600 hover:bg-cyan-700">
                      🔄 Refresh Threat Feeds
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
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

