"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import LineChart from "@/components/charts/LineChart";
import BarChart from "@/components/charts/BarChart";
import PieChart from "@/components/charts/PieChart";
import AlertNotification from "@/components/alerts/AlertNotification";

const API_URL = (process.env.NEXT_PUBLIC_AGENT_API_URL || 
                process.env.NEXT_PUBLIC_BACKEND_URL || 
                "http://ai-agent.bankid-sy.com").replace(/\/api$/, "");

type ScanResult = {
  path?: string;
  secrets_found?: Array<{
    file: string;
    secrets: Array<{
      type: string;
      line: number;
      preview: string;
    }>;
    count: number;
  }>;
  risky_files?: Array<{
    file: string;
    risk: string;
    reason: string;
  }>;
  summary?: {
    total_files: number;
    scanned_files: number;
    secrets_count: number;
    high_risk: number;
    medium_risk: number;
    low_risk: number;
  };
  issues?: Array<{
    file: string;
    type: string;
    severity: string;
    message: string;
  }>;
  failed_logins?: Array<{
    ip: string;
    line?: string;
    file?: string;
    type?: string;
    attempts?: number;
    severity?: string;
  }>;
  suspicious_ips?: Record<string, number>;
  system_info?: any;
  security_issues?: Array<{
    type: string;
    severity: string;
    message: string;
    details?: string;
  }>;
  users?: Array<any>;
  services?: Array<string>;
  processes?: Array<any>;
  dockerfiles?: Array<{
    file: string;
    issues: Array<any>;
  }>;
  docker_compose_files?: Array<{
    file: string;
    issues: Array<any>;
  }>;
  containers?: Array<any>;
  listening_ports?: Array<any>;
  active_connections?: Array<any>;
  firewall_status?: any;
  network_interfaces?: Array<any>;
  dns_servers?: Array<string>;
  vulnerabilities?: Array<any>;
  packages?: Array<any>;
  monitored_files?: Array<any>;
  changed_files?: Array<any>;
  suspicious_files?: Array<any>;
  suspicious_processes?: Array<any>;
  intrusions?: Array<any>;
  anomalies?: Array<any>;
  open_ports?: Array<any>;
  closed_ports?: Array<any>;
  findings?: Array<any>;
  exploits?: Array<any>;
  suspicious_connections?: Array<{
    ip: string;
    connections: number;
    risk: string;
  }>;
  checks?: Array<{
    type: string;
    status: string;
    details?: string;
    source?: string;
    message?: string;
    check?: string;
    expected?: string;
    actual?: string;
  }>;
  ip?: string;
  reputation?: string | {
    score: number;
    status: string;
  };
  threat_level?: string;
  top_connections?: Array<{
    ip: string;
    connections: number;
    risk: string;
  }> | Array<[string, number]>;
  cve_database?: Array<{
    id: string;
    severity: string;
    description: string;
    service?: string;
    cve?: string;
    risk?: string;
  }> | {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  headers?: Record<string, string>;
  url?: string;
  status?: number;
  response?: string;
  runtime_issues?: Array<{
    type: string;
    severity: string;
    message: string;
    container?: string;
  }>;
  pods?: Array<{
    name: string;
    namespace: string;
    status: string;
  }>;
  secrets?: Array<{
    name: string;
    namespace: string;
    type: string;
  }>;
  s3_buckets?: Array<{
    name: string;
    region: string;
    public: boolean;
  }>;
  actual?: any;
  check?: any;
  compliance_score?: number;
  connections?: Array<any>;
  container?: any;
  endpoints?: Array<any>;
  expected?: any;
  failed?: Array<any>;
  hidden_files?: Array<any>;
  passed?: Array<any>;
  password_policies?: Array<any>;
  ports?: Array<any>;
  protocols?: Array<any>;
  standard?: string;
  suspicious_activity?: Array<any>;
  suspicious_traffic?: Array<any>;
  target?: string;
  error?: string;
};

export default function SecurityPage() {
  const [activeTab, setActiveTab] = useState<"scans" | "siem" | "soc">("scans");
  const [scanType, setScanType] = useState<"repo" | "infra" | "logs" | "network" | "system" | "docker" | "network_detailed" | "vulnerabilities" | "file_integrity" | "malware" | "intrusion_detection" | "port_scan" | "penetration_test" | "threat_intelligence" | "network_forensics" | "advanced_vulnerability" | "web_scan" | "advanced_container" | "kubernetes" | "aws" | "memory_forensics" | "disk_forensics" | "password_audit" | "compliance" | "burp_suite" | "metasploit" | "packet_analysis">("repo");
  const [scanPath, setScanPath] = useState("/home/ai/ai-agent/backend");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState("");
  const [pendingActionId, setPendingActionId] = useState<string | null>(null);
  const [pendingScanType, setPendingScanType] = useState<string | null>(null);
  
  // SIEM State
  const [siemData, setSiemData] = useState<any>(null);
  const [siemLoading, setSiemLoading] = useState(true);
  const [siemAutoRefresh, setSiemAutoRefresh] = useState(true);
  const [siemAlerts, setSiemAlerts] = useState<any[]>([]);
  const [siemEventHistory, setSiemEventHistory] = useState<Array<{label: string; value: number}>>([]);
  
  // SOC State
  const [socIncidents, setSocIncidents] = useState<any[]>([]);
  const [socThreatData, setSocThreatData] = useState<any[]>([]);
  const [socAlerts, setSocAlerts] = useState<any[]>([]);

  const getAuthToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  };

  // SIEM Functions
  const fetchSIEMData = async () => {
    try {
      const token = getAuthToken();
      if (!token) {
        setSiemLoading(false);
        return;
      }

      const res = await fetch(`${API_URL}/api/security/siem`, {
        headers: { "Authorization": `Bearer ${token}` },
      });

      if (!res.ok) {
        throw new Error("Failed to fetch SIEM data");
      }

      const json = await res.json();
      setSiemData(json);
      
      // Generate alerts
      if (json.events && json.events.length > 0) {
        const newAlerts = json.events
          .filter((e: any) => e.severity === "critical" || e.severity === "high")
          .slice(0, 5)
          .map((e: any) => ({
            id: `alert-${Date.now()}-${Math.random()}`,
            type: e.severity.toLowerCase(),
            title: `${e.severity} Alert: ${e.type}`,
            message: e.message,
            timestamp: e.timestamp,
            source: e.source,
            read: false,
          }));
        setSiemAlerts(prev => [...newAlerts, ...prev].slice(0, 20));
      }
      
      // Update event history
      if (json.metrics) {
        const now = new Date();
        const timeLabel = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        setSiemEventHistory(prev => {
          const updated = [...prev, { label: timeLabel, value: json.metrics.total_events }];
          return updated.slice(-12);
        });
      }
    } catch (err) {
      console.error("SIEM fetch error:", err);
    } finally {
      setSiemLoading(false);
    }
  };

  const handleDismissSiemAlert = (id: string) => {
    setSiemAlerts(prev => prev.filter(a => a.id !== id));
  };

  const handleMarkReadSiemAlert = (id: string) => {
    setSiemAlerts(prev => prev.map(a => a.id === id ? { ...a, read: true } : a));
  };

  // SOC Functions
  const loadSOCIncidents = async () => {
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/security/siem`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        const incidents = (data.events || []).slice(0, 20).map((event: any, idx: number) => ({
          id: `inc-${idx}`,
          title: `${event.type} - ${event.source}`,
          severity: event.severity.toLowerCase(),
          status: "open",
          source: event.source,
          timestamp: event.timestamp,
          description: event.message,
          affected_assets: event.ip ? [event.ip] : [],
        }));
        setSocIncidents(incidents);
        
        // Generate alerts
        const criticalIncidents = incidents.filter((i: any) => i.severity === "critical" || i.severity === "high");
        const newAlerts = criticalIncidents.slice(0, 5).map((inc: any) => ({
          id: `alert-${inc.id}`,
          type: inc.severity,
          title: `Incident: ${inc.title}`,
          message: inc.description,
          timestamp: inc.timestamp,
          source: inc.source,
          read: false,
        }));
        setSocAlerts(prev => [...newAlerts, ...prev].slice(0, 20));
      }
    } catch (err) {
      console.error("Failed to load SOC incidents:", err);
    }
  };

  const handleDismissSocAlert = (id: string) => {
    setSocAlerts(prev => prev.filter(a => a.id !== id));
  };

  const handleMarkReadSocAlert = (id: string) => {
    setSocAlerts(prev => prev.map(a => a.id === id ? { ...a, read: true } : a));
  };

  useEffect(() => {
    if (activeTab === "siem" && siemAutoRefresh) {
      fetchSIEMData();
      const interval = setInterval(fetchSIEMData, 5000);
      return () => clearInterval(interval);
    }
  }, [activeTab, siemAutoRefresh]);

  useEffect(() => {
    if (activeTab === "soc") {
      loadSOCIncidents();
    }
  }, [activeTab]);

  const runScan = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    setPendingActionId(null);
    setPendingScanType(null);

    try {
      const token = getAuthToken();
      if (!token) {
        setError("Not authenticated. Please login first.");
        return;
      }

      let endpoint = "";
      let body: any = {};

      if (scanType === "repo") {
        endpoint = "/api/security/scan_repo";
        body = { path: scanPath, max_files: 1000 };
      } else if (scanType === "infra") {
        endpoint = "/api/security/scan_infra";
        body = { path: scanPath };
      } else if (scanType === "logs") {
        endpoint = "/api/security/scan_logs";
        body = { path: scanPath, lines: 1000 };
            } else if (scanType === "network") {
              endpoint = "/api/security/scan_network";
              body = {};
            } else if (scanType === "system") {
              endpoint = "/api/security/scan_system";
              body = {};
            } else if (scanType === "docker") {
              endpoint = "/api/security/scan_docker";
              body = {};
            } else if (scanType === "network_detailed") {
              endpoint = "/api/security/scan_network_detailed";
              body = {};
            } else if (scanType === "vulnerabilities") {
              endpoint = "/api/security/scan_vulnerabilities";
              body = {};
            } else if (scanType === "file_integrity") {
              endpoint = "/api/security/scan_file_integrity";
              body = { path: scanPath };
            } else if (scanType === "malware") {
              endpoint = "/api/security/scan_malware";
              body = { path: scanPath };
            } else if (scanType === "intrusion_detection") {
              endpoint = "/api/security/scan_intrusion_detection";
              body = {};
            } else if (scanType === "port_scan") {
              endpoint = "/api/security/scan_port_scan";
              body = { target: scanPath || "localhost" };
            } else if (scanType === "penetration_test") {
              endpoint = "/api/security/scan_penetration_test";
              body = {};
            } else if (scanType === "threat_intelligence") {
              endpoint = "/api/security/advanced/threat_intelligence";
              body = { ip: scanPath || "127.0.0.1" };
            } else if (scanType === "network_forensics") {
              endpoint = "/api/security/advanced/network_forensics";
              body = {};
            } else if (scanType === "advanced_vulnerability") {
              endpoint = "/api/security/advanced/vulnerability";
              body = {};
            } else if (scanType === "web_scan") {
              endpoint = "/api/security/advanced/web_scan";
              body = { url: scanPath || "http://localhost" };
            } else if (scanType === "advanced_container") {
              endpoint = "/api/security/advanced/container";
              body = {};
            } else if (scanType === "kubernetes") {
              endpoint = "/api/security/advanced/kubernetes";
              body = {};
            } else if (scanType === "aws") {
              endpoint = "/api/security/advanced/aws";
              body = {};
            } else if (scanType === "memory_forensics") {
              endpoint = "/api/security/advanced/memory_forensics";
              body = {};
            } else if (scanType === "disk_forensics") {
              endpoint = "/api/security/advanced/disk_forensics";
              body = { path: scanPath || "/" };
            } else if (scanType === "password_audit") {
              endpoint = "/api/security/advanced/password_audit";
              body = {};
            } else if (scanType === "compliance") {
              endpoint = "/api/security/advanced/compliance";
              body = { standard: "CIS" };
            } else if (scanType === "burp_suite") {
              endpoint = "/api/security/advanced/burp_suite";
              body = { url: scanPath || "http://localhost" };
            } else if (scanType === "metasploit") {
              endpoint = "/api/security/advanced/metasploit";
              body = { target: scanPath || "localhost" };
            } else if (scanType === "packet_analysis") {
              endpoint = "/api/security/advanced/packet_analysis";
              body = { file_path: scanPath || null };
            }

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      // Handle 202 Accepted (pending approval)
      if (res.status === 202) {
        const data = await res.json().catch(() => ({ detail: { status: "pending", message: "Action requires approval" } }));
        const errorDetail = data.detail || data.error || {};
        const actionId = typeof errorDetail === 'object' ? errorDetail.action_id : null;
        if (actionId) {
          setPendingActionId(actionId);
          setPendingScanType(scanType);
        }
        const errorMsg = typeof errorDetail === 'object' 
          ? `⏳ Action requires approval.\nAction ID: ${actionId || 'N/A'}\n${errorDetail.message || 'Please approve this action in the Approvals page.'}\n\nAfter approval, click "Get Result" button to fetch the result.`
          : String(errorDetail);
        setError(errorMsg);
        setResult({ error: errorMsg });
        return;
      }

      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: "Scan failed" }));
        throw new Error(data.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      
      // Check if response contains an error object (approval pending, etc.)
      if (data.error && typeof data.error === 'object' && data.error.status === 'pending') {
        const actionId = data.error.action_id;
        if (actionId) {
          setPendingActionId(actionId);
          setPendingScanType(scanType);
        }
        // Set error as string for display
        const errorMsg = `⏳ Action requires approval.\nAction ID: ${actionId || 'N/A'}\n${data.error.message || 'Please approve this action in the Approvals page.'}\n\nAfter approval, click "Get Result" button to fetch the result.`;
        setError(errorMsg);
        setResult({ ...data, error: errorMsg });
      } else {
        setResult(data);
        setError("");
        setPendingActionId(null);
        setPendingScanType(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  const getResultByActionId = async () => {
    if (!pendingActionId || !pendingScanType) return;
    
    setLoading(true);
    setError("");
    
    try {
      const token = getAuthToken();
      if (!token) {
        setError("Not authenticated. Please login first.");
        return;
      }

      let endpoint = "";
      let body: any = {};

      if (pendingScanType === "repo") {
        endpoint = `/api/security/scan_repo?action_id=${pendingActionId}`;
        body = { path: scanPath, max_files: 1000 };
      } else if (pendingScanType === "infra") {
        endpoint = `/api/security/scan_infra?action_id=${pendingActionId}`;
        body = { path: scanPath };
      } else if (pendingScanType === "logs") {
        endpoint = `/api/security/scan_logs?action_id=${pendingActionId}`;
        body = { path: scanPath, lines: 1000 };
      } else if (pendingScanType === "network") {
        endpoint = `/api/security/scan_network?action_id=${pendingActionId}`;
        body = {};
      } else if (pendingScanType === "system") {
        endpoint = `/api/security/scan_system?action_id=${pendingActionId}`;
        body = {};
      } else if (pendingScanType === "docker") {
        endpoint = `/api/security/scan_docker?action_id=${pendingActionId}`;
        body = {};
      } else {
        setError("This scan type doesn't support result retrieval yet");
        return;
      }

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (res.status === 202) {
        const data = await res.json().catch(() => ({ error: { status: "pending", message: "Action is still pending approval" } }));
        const errorDetail = data.error || data.detail || {};
        const errorMsg = typeof errorDetail === 'object' 
          ? `⏳ Action is still pending approval. Please wait or check the Approvals page.`
          : String(errorDetail);
        setError(errorMsg);
        setResult({ error: errorMsg });
        return;
      }

      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: "Failed to get result" }));
        throw new Error(data.detail || data.error || `HTTP ${res.status}`);
      }

      const data = await res.json();
      
      if (data.error && typeof data.error === 'object' && data.error.status === 'pending') {
        setError(`⏳ Action is still pending approval. Please wait or check the Approvals page.`);
        setResult({ error: data.error });
      } else {
        setResult(data);
        setError("");
        setPendingActionId(null);
        setPendingScanType(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get result");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
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

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "critical": return "text-red-500 bg-red-900/30 border-red-700";
      case "high": return "text-orange-400 bg-orange-900/20 border-orange-700";
      case "medium": return "text-yellow-400 bg-yellow-900/20 border-yellow-700";
      case "low": return "text-green-400 bg-green-900/20 border-green-700";
      default: return "text-slate-400 bg-slate-900/20 border-slate-700";
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case "high": return "text-red-400 bg-red-900/30";
      case "medium": return "text-yellow-400 bg-yellow-900/30";
      case "low": return "text-green-400 bg-green-900/30";
      default: return "text-slate-400 bg-slate-900/30";
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent">
              🔒 Security Center
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Comprehensive Security Analysis, SIEM, and SOC Operations
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b border-slate-800">
            {[
              { id: "scans", label: "Security Scans", icon: "🔍" },
              { id: "siem", label: "SIEM", icon: "📊" },
              { id: "soc", label: "SOC", icon: "🛡️" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? "border-red-500 text-red-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          {/* Security Scans Tab */}
          {activeTab === "scans" && (
            <div className="space-y-6">

      {/* Scan Controls */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle>Run Security Scan</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Scan Type</Label>
                    <select
                      value={scanType}
                      onChange={(e) => setScanType(e.target.value as any)}
                      className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-slate-200"
                    >
                      <optgroup label="Code & Infrastructure">
                        <option value="repo">Repository Scan (Secrets)</option>
                        <option value="infra">Infrastructure Scan (Docker/K8s)</option>
                        <option value="logs">Logs Scan (Brute-force)</option>
                      </optgroup>
                      <optgroup label="System Security">
                        <option value="system">System Security Scan (OS, Services, Users)</option>
                        <option value="docker">Docker Security Scan (Dockerfiles, Containers)</option>
                      </optgroup>
                      <optgroup label="Network Security">
                        <option value="network">Network Security Scan (Basic)</option>
                        <option value="network_detailed">Network Security Scan (Detailed)</option>
                        <option value="port_scan">Port Scanning</option>
                      </optgroup>
                      <optgroup label="Advanced Security">
                        <option value="vulnerabilities">Vulnerability Scan</option>
                        <option value="file_integrity">File Integrity Monitoring</option>
                        <option value="malware">Malware Detection Scan</option>
                        <option value="intrusion_detection">Intrusion Detection (IDS)</option>
                        <option value="penetration_test">Penetration Testing</option>
                      </optgroup>
                      <optgroup label="🔬 Advanced Tools (Enterprise)">
                        <option value="threat_intelligence">Threat Intelligence</option>
                        <option value="network_forensics">Network Forensics</option>
                        <option value="advanced_vulnerability">Advanced Vulnerability Scan</option>
                        <option value="web_scan">Web Application Scan</option>
                        <option value="advanced_container">Advanced Container Scan</option>
                        <option value="kubernetes">Kubernetes Security</option>
                        <option value="aws">AWS Security Scan</option>
                        <option value="memory_forensics">Memory Forensics</option>
                        <option value="disk_forensics">Disk Forensics</option>
                        <option value="password_audit">Password Audit</option>
                        <option value="compliance">Compliance Check (CIS/STIG)</option>
                        <option value="burp_suite">Burp Suite Web Scan</option>
                        <option value="metasploit">Metasploit Exploit Scan</option>
                        <option value="packet_analysis">Advanced Packet Analysis</option>
                      </optgroup>
                    </select>
          </div>

                  {scanType !== "network" && scanType !== "system" && scanType !== "docker" && scanType !== "network_detailed" && scanType !== "vulnerabilities" && scanType !== "intrusion_detection" && scanType !== "penetration_test" && scanType !== "network_forensics" && scanType !== "advanced_vulnerability" && scanType !== "advanced_container" && scanType !== "kubernetes" && scanType !== "aws" && scanType !== "memory_forensics" && scanType !== "password_audit" && scanType !== "compliance" && scanType !== "packet_analysis" && (
            <div className="space-y-2">
              <Label>Path</Label>
              <Input
                value={scanPath}
                onChange={(e) => setScanPath(e.target.value)}
                placeholder="/app"
                className="bg-neutral-800 border-neutral-700 text-slate-200"
              />
            </div>
          )}

          <div className="flex gap-2">
            <Button
              onClick={runScan}
              disabled={loading}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700"
            >
              {loading ? "جاري الفحص..." : "تشغيل الفحص"}
            </Button>
            {pendingActionId && pendingScanType && (
              <Button
                onClick={getResultByActionId}
                disabled={loading}
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="animate-spin">⏳</span>
                ) : (
                  "✅ Get Result"
                )}
              </Button>
            )}
          </div>

          {error && (
            <div className="p-3 bg-red-900/50 border border-red-700 rounded text-red-200 text-sm">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Summary */}
          {result.summary && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm text-slate-400">Total Files</div>
                    <div className="text-2xl font-bold">{result.summary.total_files}</div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-400">Scanned</div>
                    <div className="text-2xl font-bold">{result.summary.scanned_files}</div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-400">Secrets Found</div>
                    <div className="text-2xl font-bold text-yellow-400">
                      {result.summary.secrets_count}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-400">High Risk</div>
                    <div className="text-2xl font-bold text-red-400">
                      {result.summary.high_risk}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Secrets Found */}
          {result.secrets_found && result.secrets_found.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Secrets Found</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {result.secrets_found.map((file, idx) => (
                    <div key={idx} className="border border-red-700 rounded p-3">
                      <div className="font-mono text-sm text-red-300 mb-2">{file.file}</div>
                      <div className="text-xs text-slate-400 mb-2">
                        {file.count} secret(s) found
                      </div>
                      <div className="space-y-1">
                        {file.secrets.map((secret, sIdx) => (
                          <div key={sIdx} className="text-xs text-slate-300">
                            <span className="text-yellow-400">Line {secret.line}:</span>{" "}
                            <span className="text-red-400">{secret.type}</span> - {secret.preview}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Risky Files */}
          {result.risky_files && result.risky_files.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Risky Files</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.risky_files.map((file, idx) => (
                    <div
                      key={idx}
                      className={`p-3 border rounded ${getRiskColor(file.risk)}`}
                    >
                      <div className="font-mono text-sm mb-1">{file.file}</div>
                      <div className="text-xs">{file.reason}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Infrastructure Issues */}
          {result.issues && result.issues.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Infrastructure Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.issues.map((issue, idx) => (
                    <div
                      key={idx}
                      className={`p-3 border rounded ${getRiskColor(issue.severity)}`}
                    >
                      <div className="font-mono text-sm mb-1">{issue.file}</div>
                      <div className="text-xs font-semibold mb-1">{issue.type}</div>
                      <div className="text-xs">{issue.message}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Failed Logins / Brute-force */}
          {result.failed_logins && result.failed_logins.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Failed Login Attempts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.failed_logins.map((login, idx) => (
                    <div key={idx} className="border border-red-700 rounded p-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-mono text-sm text-red-300">{login.ip}</div>
                        {login.attempts && (
                          <div className="text-xs text-red-400">
                            {login.attempts} attempts
                          </div>
                        )}
                      </div>
                      {login.type === "brute_force" && (
                        <div className="text-xs text-red-400 font-semibold">
                          ⚠️ Brute-force detected!
                        </div>
                      )}
                      {login.line && (
                        <div className="text-xs text-slate-400 mt-1 font-mono">
                          {login.line.substring(0, 100)}...
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Network Security Results */}
          {result.open_ports && result.open_ports.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-yellow-400">Open Ports</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.open_ports.map((port: any, idx: number) => (
                    <div
                      key={idx}
                      className={`p-3 border rounded ${getRiskColor(port.risk)}`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-mono text-sm">Port {port.port}</div>
                          <div className="text-xs text-slate-400">{port.service}</div>
                        </div>
                        <div className={`text-xs px-2 py-1 rounded ${
                          port.risk === "high" ? "bg-red-600" : "bg-yellow-600"
                        }`}>
                          {port.risk.toUpperCase()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.suspicious_connections && result.suspicious_connections.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Suspicious Connections</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.suspicious_connections.map((conn: any, idx: number) => (
                    <div
                      key={idx}
                      className={`p-3 border rounded ${getRiskColor(conn.risk)}`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="font-mono text-sm">{conn.ip}</div>
                        <div className="text-sm font-bold">
                          {conn.connections} connections
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Suspicious IPs */}
          {result.suspicious_ips && Object.keys(result.suspicious_ips).length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Suspicious IPs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(result.suspicious_ips).map(([ip, count]) => (
                    <div key={ip} className="flex items-center justify-between p-2 border rounded">
                      <div className="font-mono text-sm">{ip}</div>
                      <div className={`text-sm ${count > 10 ? "text-red-400" : "text-yellow-400"}`}>
                        {count} attempts
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* System Security Results */}
          {result.system_info && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>System Information</CardTitle>
              </CardHeader>
              <CardContent>
                {result.system_info.os && (
                  <div className="text-sm">
                    <span className="text-slate-400">OS:</span>{" "}
                    <span className="text-slate-200 font-mono">{result.system_info.os}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {result.security_issues && result.security_issues.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Security Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.security_issues.map((issue, idx) => (
                    <div
                      key={idx}
                      className={`p-3 border rounded ${getRiskColor(issue.severity)}`}
                    >
                      <div className="text-sm font-semibold mb-1">{issue.type}</div>
                      <div className="text-xs">{issue.message}</div>
                      {issue.details && (
                        <div className="text-xs text-slate-400 mt-1 font-mono">
                          {issue.details}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.users && result.users.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>System Users</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  {result.users.slice(0, 10).map((user, idx) => (
                    <div key={idx} className="text-sm text-slate-300">
                      <span className="font-mono">{user.name}</span> (UID: {user.uid}, Shell: {user.shell})
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.services && result.services.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Running Services</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {result.services.map((service, idx) => (
                    <div key={idx} className="text-xs text-slate-300 font-mono">
                      {service}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.processes && result.processes.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Suspicious Processes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.processes.map((proc, idx) => (
                    <div key={idx} className="border border-red-700 rounded p-2">
                      <div className="text-sm text-red-300">
                        PID: {proc.pid} | User: {proc.user}
                      </div>
                      <div className="text-xs text-slate-400 font-mono mt-1">
                        {proc.cmd}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Docker Security Results */}
          {result.dockerfiles && result.dockerfiles.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-yellow-400">Dockerfiles Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.dockerfiles.map((df, idx) => (
                    <div key={idx} className="border border-yellow-700 rounded p-3">
                      <div className="font-mono text-sm text-yellow-300 mb-2">{df.file}</div>
                      <div className="space-y-1">
                        {df.issues.map((issue, iIdx) => (
                          <div
                            key={iIdx}
                            className={`text-xs p-2 rounded ${getRiskColor(issue.severity)}`}
                          >
                            {issue.message}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.docker_compose_files && result.docker_compose_files.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-yellow-400">Docker Compose Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.docker_compose_files.map((dc, idx) => (
                    <div key={idx} className="border border-yellow-700 rounded p-3">
                      <div className="font-mono text-sm text-yellow-300 mb-2">{dc.file}</div>
                      <div className="space-y-1">
                        {dc.issues.map((issue, iIdx) => (
                          <div
                            key={iIdx}
                            className={`text-xs p-2 rounded ${getRiskColor(issue.severity)}`}
                          >
                            {issue.message}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.containers && result.containers.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Running Containers</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.containers.map((container, idx) => (
                    <div key={idx} className="border border-slate-700 rounded p-2">
                      <div className="text-sm text-slate-300">
                        <span className="font-mono">{container.name}</span> - {container.image}
                      </div>
                      <div className="text-xs text-slate-400">{container.status}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Detailed Network Security Results */}
          {result.listening_ports && result.listening_ports.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Listening Ports</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.listening_ports.map((port, idx) => (
                    <div
                      key={idx}
                      className={`p-2 border rounded ${getRiskColor(port.risk)}`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-mono text-sm">Port {port.port}</span>
                          {port.service && (
                            <span className="text-xs text-slate-400 ml-2">({port.service})</span>
                          )}
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${getRiskColor(port.risk)}`}>
                          {port.risk}
                        </span>
                      </div>
                      {port.interface && (
                        <div className="text-xs text-slate-400 mt-1">
                          Interface: {port.interface}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.firewall_status && Object.keys(result.firewall_status).length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Firewall Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="text-slate-400">Type:</span>{" "}
                    <span className="text-slate-200">{result.firewall_status.type || "Unknown"}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-slate-400">Status:</span>{" "}
                    <span className={`${
                      result.firewall_status.status === "enabled" ? "text-green-400" : "text-red-400"
                    }`}>
                      {result.firewall_status.status || "Unknown"}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {result.network_interfaces && result.network_interfaces.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Network Interfaces</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.network_interfaces.map((iface, idx) => (
                    <div key={idx} className="border border-slate-700 rounded p-2">
                      <div className="font-mono text-sm text-slate-300">{iface.name}</div>
                      {iface.addresses && iface.addresses.length > 0 && (
                        <div className="text-xs text-slate-400 mt-1">
                          {iface.addresses.join(", ")}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.dns_servers && result.dns_servers.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>DNS Servers</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  {result.dns_servers.map((dns, idx) => (
                    <div key={idx} className="text-sm text-slate-300 font-mono">
                      {dns}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Vulnerability Scan Results */}
          {result.vulnerabilities && result.vulnerabilities.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Vulnerabilities Found</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.vulnerabilities.map((vuln, idx) => (
                    <div key={idx} className={`p-3 border rounded ${getRiskColor(vuln.risk)}`}>
                      <div className="font-semibold">{vuln.service}</div>
                      <div className="text-xs text-slate-400">{vuln.version}</div>
                      <div className="text-xs">{vuln.message}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* File Integrity Results */}
          {result.monitored_files && result.monitored_files.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>File Integrity Monitoring</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.monitored_files.map((file, idx) => (
                    <div key={idx} className="border border-slate-700 rounded p-2">
                      <div className="font-mono text-sm text-slate-300">{file.file}</div>
                      <div className="text-xs text-slate-400">Hash: {file.hash}</div>
                      <div className="text-xs text-slate-400">Modified: {file.modified}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Malware Scan Results */}
          {result.suspicious_files && result.suspicious_files.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Suspicious Files</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.suspicious_files.map((file, idx) => (
                    <div key={idx} className="border border-red-700 rounded p-2">
                      <div className="font-mono text-sm text-red-300">{file.file}</div>
                      <div className="text-xs text-red-400">{file.reason}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* IDS Results */}
          {result.intrusions && result.intrusions.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Intrusions Detected</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.intrusions.map((intrusion, idx) => (
                    <div key={idx} className={`p-3 border rounded ${getRiskColor(intrusion.severity)}`}>
                      <div className="font-semibold">{intrusion.type}</div>
                      <div className="text-sm">IP: {intrusion.ip}</div>
                      <div className="text-xs">{intrusion.message}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Port Scan Results */}
          {result.open_ports && result.open_ports.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Port Scan Results</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {result.open_ports.map((port, idx) => (
                    <div key={idx} className="border border-green-700 rounded p-2 text-center">
                      <div className="font-mono text-sm text-green-400">Port {port.port}</div>
                      <div className="text-xs text-slate-400">{port.service}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Penetration Test Results */}
          {result.findings && result.findings.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Penetration Test Findings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.findings.map((finding, idx) => (
                    <div key={idx} className={`p-3 border rounded ${getRiskColor(finding.severity)}`}>
                      <div className="font-semibold">{finding.type}</div>
                      <div className="text-xs">{finding.message}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Threat Intelligence Results */}
          {result.checks && result.checks.length > 0 && result.ip && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Threat Intelligence: {result.ip}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="text-slate-400">Reputation:</span>{" "}
                    <span className={`${
                      (typeof result.reputation === "string" && result.reputation === "malicious") || 
                      (typeof result.reputation === "object" && result.reputation?.status === "malicious")
                        ? "text-red-400" : "text-green-400"
                    }`}>
                      {typeof result.reputation === "string" 
                        ? result.reputation 
                        : result.reputation?.status || "unknown"}
                    </span>
                  </div>
                  <div className="text-sm">
                    <span className="text-slate-400">Threat Level:</span>{" "}
                    <span className={getRiskColor(result.threat_level || "low")}>
                      {result.threat_level || "low"}
                    </span>
                  </div>
                  {result.checks.map((check, idx) => (
                    <div key={idx} className="border border-slate-700 rounded p-2">
                      <div className="text-sm text-slate-300">{check.source}</div>
                      <div className="text-xs text-slate-400">{check.message}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Network Forensics Results */}
          {result.top_connections && result.top_connections.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Network Traffic Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-sm font-semibold mb-2">Top Connections:</div>
                  {result.top_connections.map((conn, idx) => {
                    const ip = Array.isArray(conn) ? conn[0] : conn.ip;
                    const connections = Array.isArray(conn) ? conn[1] : conn.connections;
                    return (
                    <div key={idx} className="flex items-center justify-between border border-slate-700 rounded p-2">
                        <div className="font-mono text-sm text-slate-300">{ip}</div>
                        <div className="text-sm text-blue-400">{connections} connections</div>
                    </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Advanced Vulnerability Results */}
          {result.cve_database && Array.isArray(result.cve_database) && result.cve_database.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">CVE Database</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.cve_database.map((cve, idx) => (
                    <div key={idx} className={`p-3 border rounded ${getRiskColor(cve.risk || cve.severity || "low")}`}>
                      <div className="font-semibold">{cve.service || cve.id}</div>
                      <div className="text-xs text-slate-400">CVE: {cve.cve || cve.id}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Web Scan Results */}
          {result.headers && Object.keys(result.headers).length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Web Scan: {result.url}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.vulnerabilities && result.vulnerabilities.length > 0 && (
                    <div>
                      <div className="text-sm font-semibold mb-2 text-red-400">Vulnerabilities:</div>
                      {result.vulnerabilities.map((vuln, idx) => (
                        <div key={idx} className={`p-2 border rounded ${getRiskColor(vuln.severity)}`}>
                          <div className="text-xs">{vuln.message}</div>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="text-sm">
                    <span className="text-slate-400">Security Headers:</span>
                    <div className="mt-1 space-y-1">
                      {Object.entries(result.headers).slice(0, 10).map(([key, value]) => (
                        <div key={key} className="text-xs text-slate-300">
                          <span className="font-mono">{key}:</span> {String(value).substring(0, 50)}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Advanced Container Results */}
          {result.runtime_issues && result.runtime_issues.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Container Runtime Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.runtime_issues.map((issue, idx) => (
                    <div key={idx} className={`p-3 border rounded ${getRiskColor(issue.severity)}`}>
                      <div className="font-semibold">{issue.container}</div>
                      <div className="text-xs">{issue.message}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Kubernetes Results */}
          {result.pods && result.pods.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Kubernetes Resources</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="text-slate-400">Pods:</span> {result.pods.length}
                  </div>
                  {result.secrets && result.secrets.length > 0 && (
                    <div className="text-sm">
                      <span className="text-slate-400">Secrets:</span> {result.secrets.length}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* AWS Results */}
          {result.s3_buckets && result.s3_buckets.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>AWS Resources</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-sm font-semibold mb-2">S3 Buckets:</div>
                  {result.s3_buckets.map((bucket, idx) => (
                    <div key={idx} className="text-sm text-slate-300 font-mono">
                      {typeof bucket === "string" ? bucket : bucket.name}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Memory Forensics Results */}
          {result.suspicious_activity && result.suspicious_activity.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-red-400">Memory Forensics - Suspicious Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.suspicious_activity.map((activity, idx) => (
                    <div key={idx} className="border border-red-700 rounded p-2">
                      <div className="text-sm text-red-300">PID: {activity.pid} | User: {activity.user}</div>
                      <div className="text-xs text-slate-400 font-mono mt-1">{activity.cmd}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Disk Forensics Results */}
          {result.hidden_files && result.hidden_files.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Disk Forensics - Hidden Files</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  {result.hidden_files.slice(0, 20).map((file, idx) => (
                    <div key={idx} className="text-xs text-slate-300 font-mono">{file}</div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Password Audit Results */}
          {result.password_policies && Object.keys(result.password_policies).length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Password Security Audit</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(result.password_policies).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <span className="text-slate-400">{key}:</span>{" "}
                      <span className="text-slate-200">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Burp Suite Results */}
          {result.endpoints && result.endpoints.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Burp Suite Scan: {result.url}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {result.vulnerabilities && result.vulnerabilities.length > 0 && (
                    <div>
                      <div className="text-sm font-semibold mb-2 text-red-400">Vulnerabilities Found:</div>
                      {result.vulnerabilities.map((vuln, idx) => (
                        <div key={idx} className={`p-3 border rounded mb-2 ${getRiskColor(vuln.severity)}`}>
                          <div className="font-semibold">{vuln.type}</div>
                          <div className="text-xs text-slate-300">URL: {vuln.url}</div>
                          <div className="text-xs">{vuln.message}</div>
                        </div>
                      ))}
                    </div>
                  )}
                  <div>
                    <div className="text-sm font-semibold mb-2">Endpoints Tested:</div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {result.endpoints.map((endpoint, idx) => (
                        <div key={idx} className="border border-slate-700 rounded p-2">
                          <div className="font-mono text-xs text-slate-300">{endpoint.url}</div>
                          <div className="text-xs text-slate-400">Status: {endpoint.status}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Metasploit Results */}
          {result.ports && result.ports.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Metasploit Scan: {result.target}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-semibold mb-2">Open Ports:</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {result.ports.map((port, idx) => (
                        <div key={idx} className="border border-green-700 rounded p-2 text-center">
                          <div className="font-mono text-sm text-green-400">Port {port.port}</div>
                          <div className="text-xs text-slate-400">{port.service}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  {result.exploits && result.exploits.length > 0 && (
                    <div>
                      <div className="text-sm font-semibold mb-2 text-red-400">Exploits Available:</div>
                      {result.exploits.map((exploit, idx) => (
                        <div key={idx} className={`p-3 border rounded ${getRiskColor(exploit.risk)}`}>
                          <div className="font-semibold">{exploit.service}</div>
                          <div className="text-xs text-slate-300">Target: {exploit.target}</div>
                          <div className="text-xs">Exploit: {exploit.exploit}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Packet Analysis Results */}
          {result.protocols && Object.keys(result.protocols).length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Packet Analysis Results</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-semibold mb-2">Protocols Detected:</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {Object.entries(result.protocols).map(([protocol, count]) => (
                        <div key={protocol} className="border border-blue-700 rounded p-2 text-center">
                          <div className="font-mono text-sm text-blue-400">{protocol}</div>
                          <div className="text-xs text-slate-400">{String(count)} packets</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  {result.suspicious_traffic && result.suspicious_traffic.length > 0 && (
                    <div>
                      <div className="text-sm font-semibold mb-2 text-red-400">Suspicious Traffic:</div>
                      {result.suspicious_traffic.map((traffic, idx) => (
                        <div key={idx} className={`p-3 border rounded ${getRiskColor(traffic.risk)}`}>
                          <div className="font-mono text-sm">{traffic.ip}</div>
                          <div className="text-xs">{traffic.reason}</div>
                          <div className="text-xs text-slate-400">Connections: {traffic.connections}</div>
                        </div>
                      ))}
                    </div>
                  )}
                  {result.connections && result.connections.length > 0 && (
                    <div>
                      <div className="text-sm font-semibold mb-2">Top Connections:</div>
                      {result.connections.slice(0, 10).map((conn, idx) => (
                        <div key={idx} className="flex items-center justify-between border border-slate-700 rounded p-2 mb-1">
                          <div className="font-mono text-sm text-slate-300">{conn.connection}</div>
                          <div className="text-sm text-blue-400">{conn.count}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Compliance Results */}
          {result.checks && result.checks.length > 0 && result.standard && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Compliance Check: {result.standard}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {result.compliance_score !== undefined && (
                    <div className="text-lg font-bold mb-4">
                      <span className="text-slate-400">Compliance Score:</span>{" "}
                      <span className={`${
                        result.compliance_score >= 80 ? "text-green-400" :
                        result.compliance_score >= 60 ? "text-yellow-400" : "text-red-400"
                      }`}>
                        {result.compliance_score.toFixed(1)}%
                      </span>
                    </div>
                  )}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center p-3 bg-green-900/20 border border-green-700 rounded">
                      <div className="text-2xl font-bold text-green-400">{result.passed || 0}</div>
                      <div className="text-xs text-slate-400">Passed</div>
                    </div>
                    <div className="text-center p-3 bg-red-900/20 border border-red-700 rounded">
                      <div className="text-2xl font-bold text-red-400">{result.failed || 0}</div>
                      <div className="text-xs text-slate-400">Failed</div>
                    </div>
                  </div>
                  <div className="space-y-1">
                    {result.checks.map((check, idx) => (
                      <div key={idx} className={`p-2 border rounded ${
                        check.status === "passed" ? "border-green-700 bg-green-900/20" : "border-red-700 bg-red-900/20"
                      }`}>
                        <div className="flex items-center justify-between">
                          <div className="text-sm text-slate-300">{check.check}</div>
                          <span className={`text-xs px-2 py-1 rounded ${
                            check.status === "passed" ? "bg-green-600" : "bg-red-600"
                          }`}>
                            {check.status}
                          </span>
                        </div>
                        {check.expected && (
                          <div className="text-xs text-slate-400 mt-1">
                            Expected: {check.expected} | Actual: {check.actual}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error */}
          {result.error && (
            <Card className="bg-slate-900 border-red-800">
              <CardContent className="p-4">
                <div className="text-red-400">
                  {typeof result.error === 'string' 
                    ? result.error 
                    : result.error.status === 'pending'
                      ? `⏳ Action requires approval. Action ID: ${result.error.action_id || 'N/A'}\n${result.error.message || 'Please approve this action in the Approvals page.'}`
                      : JSON.stringify(result.error, null, 2)
                  }
                </div>
              </CardContent>
            </Card>
          )}

          {/* No Results */}
          {!result.secrets_found &&
            !result.risky_files &&
            !result.issues &&
            !result.failed_logins &&
            !result.security_issues &&
            !result.dockerfiles &&
            !result.docker_compose_files &&
            !result.listening_ports &&
            !result.vulnerabilities &&
            !result.suspicious_files &&
            !result.intrusions &&
            !result.open_ports &&
            !result.findings &&
            !result.checks &&
            !result.top_connections &&
            !result.cve_database &&
            !result.headers &&
            !result.runtime_issues &&
            !result.pods &&
            !result.s3_buckets &&
            !result.suspicious_activity &&
            !result.hidden_files &&
            !result.password_policies &&
            !result.compliance_score &&
            !result.error && (
              <Card className="bg-slate-900 border-slate-800">
                <CardContent className="p-4 text-center text-slate-400">
                  No issues found. System appears secure.
                </CardContent>
              </Card>
            )}
        </div>
      )}
          </div>
          )}

          {/* SIEM Tab - Layered Analytics Dashboard */}
          {activeTab === "siem" && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                    SRG Layered Analytics
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Showing data for <strong>Last 7 days</strong> from {new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toLocaleDateString()} to {new Date().toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <Button
                    onClick={() => setSiemAutoRefresh(!siemAutoRefresh)}
                    className={siemAutoRefresh ? "bg-green-600 hover:bg-green-700" : "bg-slate-700 hover:bg-slate-600"}
                  >
                    {siemAutoRefresh ? "🟢 Auto Refresh ON" : "⚫ Auto Refresh OFF"}
                  </Button>
                  <Button onClick={fetchSIEMData} className="bg-indigo-600 hover:bg-indigo-700">
                    🔄 Refresh
                  </Button>
                </div>
              </div>

              {siemLoading && !siemData ? (
                <div className="text-center p-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
                  <p className="mt-4 text-slate-400">Loading SIEM Dashboard...</p>
                </div>
              ) : (
                <>
                  {/* Use Real SIEM Data with Fallback to Mock */}
                  {(() => {
                    // Use real data from API if available, otherwise use calculated/mock data
                    const realMetrics = siemData?.metrics || {};
                    const realEvents = siemData?.events || [];
                    
                    // Calculate cases from real events
                    const casesFromEvents = {
                      catastrophic: realEvents.filter((e: any) => e.severity === "critical" || e.severity === "catastrophic").length,
                      critical: realEvents.filter((e: any) => e.severity === "high").length,
                      marginal: realEvents.filter((e: any) => e.severity === "medium").length,
                      insignificant: realEvents.filter((e: any) => e.severity === "low").length,
                      none: realEvents.filter((e: any) => !e.severity || e.severity === "info").length,
                    };
                    
                    const totalCases = Object.values(casesFromEvents).reduce((sum: number, val: any) => sum + val, 0) || 44;
                    
                    // Generate timeline from real events or mock
                    const now = new Date();
                    const caseTimeline = [];
                    for (let i = 6; i >= 0; i--) {
                      const date = new Date(now);
                      date.setDate(date.getDate() - i);
                      const dateStr = date.toISOString().split('T')[0];
                      const dayEvents = realEvents.filter((e: any) => e.timestamp?.startsWith(dateStr));
                      caseTimeline.push({
                        date: dateStr,
                        catastrophic: dayEvents.filter((e: any) => e.severity === "critical" || e.severity === "catastrophic").length || Math.floor(Math.random() * 2),
                        critical: dayEvents.filter((e: any) => e.severity === "high").length || Math.floor(Math.random() * 3),
                        marginal: dayEvents.filter((e: any) => e.severity === "medium").length || Math.floor(Math.random() * 5),
                        insignificant: dayEvents.filter((e: any) => e.severity === "low").length || Math.floor(Math.random() * 8),
                        none: dayEvents.filter((e: any) => !e.severity || e.severity === "info").length || Math.floor(Math.random() * 10),
                      });
                    }

                    const cases = totalCases > 0 ? casesFromEvents : {
                      catastrophic: 3,
                      critical: 6,
                      marginal: 7,
                      insignificant: 10,
                      none: 18,
                    };

                    const workflow = {
                      queued: Math.floor(totalCases * 0.32),
                      initial: Math.floor(totalCases * 0.20),
                      followup: Math.floor(totalCases * 0.23),
                      final: Math.floor(totalCases * 0.25),
                      closed: 0,
                    };

                    const threatAnalysis = {
                      analyzed: realMetrics.total_events || 8858,
                      found: (realMetrics.total_events || 8858) * 0.8,
                      created: totalCases,
                    };

                    // Use real entities if available, otherwise mock
                    const entities = siemData?.entities || {
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

                    const highRiskEntities = Object.values(entities).reduce((sum: number, entity: any) => sum + (entity.high_risk || 0), 0);

                    return (
                      <>
                        {/* Entity Count Overview */}
                        <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 mb-6">
                          <CardHeader>
                            <CardTitle className="text-xl">
                              There are <span className="text-red-400">{highRiskEntities} entities with extremely high risk scores</span>
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                              {Object.entries(entities).map(([key, entity]) => (
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
                                  data={caseTimeline.map((d) => ({
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
                                      { label: "4-Catastrophic", value: cases.catastrophic, color: "#ef4444" },
                                      { label: "3-Critical", value: cases.critical, color: "#f97316" },
                                      { label: "2-Marginal", value: cases.marginal, color: "#eab308" },
                                      { label: "1-Insignificant", value: cases.insignificant, color: "#60a5fa" },
                                      { label: "0-None", value: cases.none, color: "#475569" },
                                    ]}
                                    size={200}
                                  />
                                  <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="text-center">
                                      <div className="text-2xl font-bold text-slate-200">TOTAL</div>
                                      <div className="text-3xl font-bold text-indigo-400">{totalCases}</div>
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
                                  <span className="font-semibold">{cases.catastrophic} ({((cases.catastrophic / totalCases) * 100).toFixed(2)}%)</span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded bg-orange-500"></div>
                                    <span>3-Critical</span>
                                  </div>
                                  <span className="font-semibold">{cases.critical} ({((cases.critical / totalCases) * 100).toFixed(2)}%)</span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded bg-yellow-500"></div>
                                    <span>2-Marginal</span>
                                  </div>
                                  <span className="font-semibold">{cases.marginal} ({((cases.marginal / totalCases) * 100).toFixed(2)}%)</span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded bg-blue-400"></div>
                                    <span>1-Insignificant</span>
                                  </div>
                                  <span className="font-semibold">{cases.insignificant} ({((cases.insignificant / totalCases) * 100).toFixed(2)}%)</span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded bg-slate-600"></div>
                                    <span>0-None</span>
                                  </div>
                                  <span className="font-semibold">{cases.none} ({((cases.none / totalCases) * 100).toFixed(2)}%)</span>
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
                                    name="workflow-period"
                                    defaultChecked
                                    className="w-3 h-3"
                                  />
                                  <span>Selected Period</span>
                                </label>
                                <label className="flex items-center gap-2 text-xs cursor-pointer">
                                  <input
                                    type="radio"
                                    name="workflow-period"
                                    className="w-3 h-3"
                                  />
                                  <span>As of Now</span>
                                </label>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="flex items-center justify-between mb-4">
                                {[
                                  { name: "Queued", count: workflow.queued, percentage: ((workflow.queued / totalCases) * 100).toFixed(2) },
                                  { name: "Initial", count: workflow.initial, percentage: ((workflow.initial / totalCases) * 100).toFixed(2) },
                                  { name: "Follow-up", count: workflow.followup, percentage: ((workflow.followup / totalCases) * 100).toFixed(2) },
                                  { name: "Final", count: workflow.final, percentage: ((workflow.final / totalCases) * 100).toFixed(2) },
                                  { name: "Closed", count: workflow.closed, percentage: "0.00" },
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
                                    {threatAnalysis.analyzed.toLocaleString()} Events
                                  </div>
                                  <div className="text-sm text-slate-400">Analyzed</div>
                                </div>
                                
                                {/* Arrow */}
                                <div className="flex justify-center">
                                  <div className="text-center">
                                    <div className="text-lg font-bold text-indigo-400 mb-1">
                                      {((threatAnalysis.found / threatAnalysis.analyzed) * 100).toFixed(2)}%
                                    </div>
                                    <div className="w-0.5 h-12 bg-indigo-400 mx-auto"></div>
                                  </div>
                                </div>

                                {/* Found */}
                                <div className="text-center">
                                  <div className="text-2xl font-bold text-purple-400 mb-2">
                                    {threatAnalysis.found.toLocaleString()} Correlation Events
                                  </div>
                                  <div className="text-sm text-slate-400">Found</div>
                                </div>

                                {/* Arrow */}
                                <div className="flex justify-center">
                                  <div className="text-center">
                                    <div className="text-lg font-bold text-indigo-400 mb-1">
                                      {((threatAnalysis.created / threatAnalysis.found) * 100).toFixed(2)}%
                                    </div>
                                    <div className="w-0.5 h-12 bg-indigo-400 mx-auto"></div>
                                  </div>
                                </div>

                                {/* Created */}
                                <div className="text-center">
                                  <div className="text-2xl font-bold text-green-400 mb-2">
                                    {threatAnalysis.created} Cases
                                  </div>
                                  <div className="text-sm text-slate-400">Created</div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      </>
                    );
                  })()}
                </>
              )}
            </div>
          )}

          {/* SOC Tab - Enhanced with Graphs */}
          {activeTab === "soc" && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent">
                    🛡️ Security Operations Center
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Real-time threat detection, incident response, and security monitoring
                  </p>
                </div>
                <Button onClick={fetchSIEMData} className="bg-indigo-600 hover:bg-indigo-700">
                  🔄 Refresh
                </Button>
              </div>

              {/* Stats Overview */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="bg-gradient-to-br from-red-900/30 to-red-800/30 border-red-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-xs text-slate-400">Critical Incidents</div>
                      <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                    </div>
                    <div className="text-3xl font-bold text-red-400">
                      {socIncidents.filter((i: any) => i.severity === "critical").length}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Requires immediate action</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-orange-900/30 to-orange-800/30 border-orange-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-xs text-slate-400">High Severity</div>
                      <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                    </div>
                    <div className="text-3xl font-bold text-orange-400">
                      {socIncidents.filter((i: any) => i.severity === "high").length}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Needs attention</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/30 border-yellow-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-xs text-slate-400">Open Cases</div>
                      <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    </div>
                    <div className="text-3xl font-bold text-yellow-400">
                      {socIncidents.filter((i: any) => i.status === "open").length}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Under investigation</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-900/30 to-blue-800/30 border-blue-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-xs text-slate-400">Total Incidents</div>
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    </div>
                    <div className="text-3xl font-bold text-blue-400">{socIncidents.length}</div>
                    <div className="text-xs text-slate-400 mt-1">All time</div>
                  </CardContent>
                </Card>
              </div>

              {/* Charts Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Incident Trend Chart */}
                <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle>Incident Trend (Last 7 Days)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <LineChart
                      data={(() => {
                        const now = new Date();
                        const trendData = [];
                        for (let i = 6; i >= 0; i--) {
                          const date = new Date(now);
                          date.setDate(date.getDate() - i);
                          const dateStr = date.toISOString().split('T')[0];
                          const dayIncidents = socIncidents.filter((inc: any) => 
                            inc.timestamp?.startsWith(dateStr)
                          );
                          trendData.push({
                            label: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                            value: dayIncidents.length || Math.floor(Math.random() * 5),
                          });
                        }
                        return trendData.length > 0 ? trendData : [
                          { label: "Nov 12", value: 3 },
                          { label: "Nov 13", value: 5 },
                          { label: "Nov 14", value: 2 },
                          { label: "Nov 15", value: 4 },
                          { label: "Nov 16", value: 3 },
                          { label: "Nov 17", value: 6 },
                          { label: "Nov 18", value: 4 },
                        ];
                      })()}
                      color="#ef4444"
                      height={250}
                    />
                  </CardContent>
                </Card>

                {/* Incident Severity Distribution */}
                <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle>Incident Severity Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-center">
                      <PieChart
                        data={[
                          { 
                            label: "Critical", 
                            value: socIncidents.filter((i: any) => i.severity === "critical").length || 3, 
                            color: "#ef4444" 
                          },
                          { 
                            label: "High", 
                            value: socIncidents.filter((i: any) => i.severity === "high").length || 6, 
                            color: "#f97316" 
                          },
                          { 
                            label: "Medium", 
                            value: socIncidents.filter((i: any) => i.severity === "medium").length || 8, 
                            color: "#eab308" 
                          },
                          { 
                            label: "Low", 
                            value: socIncidents.filter((i: any) => i.severity === "low").length || 12, 
                            color: "#10b981" 
                          },
                        ].filter(d => d.value > 0)}
                        size={200}
                      />
                    </div>
                    <div className="mt-4 space-y-2 text-sm">
                      {[
                        { label: "Critical", count: socIncidents.filter((i: any) => i.severity === "critical").length || 3, color: "red" },
                        { label: "High", count: socIncidents.filter((i: any) => i.severity === "high").length || 6, color: "orange" },
                        { label: "Medium", count: socIncidents.filter((i: any) => i.severity === "medium").length || 8, color: "yellow" },
                        { label: "Low", count: socIncidents.filter((i: any) => i.severity === "low").length || 12, color: "green" },
                      ].map((item) => (
                        <div key={item.label} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded bg-${item.color}-500`}></div>
                            <span>{item.label}</span>
                          </div>
                          <span className="font-semibold">{item.count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Incident Status Breakdown */}
                <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle>Incident Status Breakdown</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <BarChart
                      data={[
                        { label: "Open", value: socIncidents.filter((i: any) => i.status === "open").length || 15 },
                        { label: "Investigating", value: socIncidents.filter((i: any) => i.status === "investigating").length || 8 },
                        { label: "Resolved", value: socIncidents.filter((i: any) => i.status === "resolved").length || 12 },
                        { label: "Closed", value: socIncidents.filter((i: any) => i.status === "closed").length || 9 },
                      ]}
                      color="#8b5cf6"
                      height={200}
                    />
                  </CardContent>
                </Card>

                {/* Top Threat Sources */}
                <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle>Top Threat Sources</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {(() => {
                        const sources: Record<string, number> = {};
                        socIncidents.forEach((inc: any) => {
                          const source = inc.source || "Unknown";
                          sources[source] = (sources[source] || 0) + 1;
                        });
                        const topSources = Object.entries(sources)
                          .sort((a, b) => b[1] - a[1])
                          .slice(0, 5)
                          .map(([source, count]) => ({ source, count }));
                        
                        return topSources.length > 0 ? topSources.map((item, idx) => (
                          <div key={idx} className="flex items-center justify-between p-2 bg-slate-800/50 rounded">
                            <span className="text-sm text-slate-300">{item.source}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-24 bg-slate-700 rounded-full h-2">
                                <div
                                  className="bg-indigo-500 h-2 rounded-full"
                                  style={{ width: `${(item.count / socIncidents.length) * 100}%` }}
                                ></div>
                              </div>
                              <span className="text-sm font-bold text-indigo-400 w-8 text-right">{item.count}</span>
                            </div>
                          </div>
                        )) : (
                          <div className="text-center text-slate-400 py-4">No threat sources detected</div>
                        );
                      })()}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Incidents List */}
              <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Incident Cases</span>
                    <span className="text-sm text-slate-400 font-normal">
                      {socIncidents.length} total incidents
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {socIncidents.length > 0 ? socIncidents.map((incident: any) => (
                      <div
                        key={incident.id}
                        className={`p-4 border rounded-lg cursor-pointer hover:bg-slate-800/50 transition-all ${getSeverityColor(incident.severity)}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className={`text-xs font-semibold px-2 py-1 rounded ${getSeverityColor(incident.severity)}`}>
                                {incident.severity?.toUpperCase() || "UNKNOWN"}
                              </span>
                              <span className="text-sm font-semibold text-slate-300">{incident.title || "Untitled Incident"}</span>
                              <span className={`text-xs px-2 py-1 rounded ${
                                incident.status === "open" ? "bg-red-900/30 text-red-400" :
                                incident.status === "investigating" ? "bg-yellow-900/30 text-yellow-400" :
                                incident.status === "resolved" ? "bg-green-900/30 text-green-400" :
                                "bg-slate-700 text-slate-400"
                              }`}>
                                {incident.status?.toUpperCase() || "UNKNOWN"}
                              </span>
                              <span className="text-xs text-slate-500 ml-auto">
                                {incident.timestamp ? new Date(incident.timestamp).toLocaleString() : "N/A"}
                              </span>
                            </div>
                            <div className="text-sm text-slate-200 mb-2">{incident.description || "No description available"}</div>
                            <div className="flex gap-4 mt-2 text-xs">
                              {incident.source && (
                                <span className="text-slate-400">
                                  <span className="font-semibold">Source:</span> {incident.source}
                                </span>
                              )}
                              {incident.affected_assets && incident.affected_assets.length > 0 && (
                                <span className="text-slate-400">
                                  <span className="font-semibold">Assets:</span> {incident.affected_assets.join(", ")}
                                </span>
                              )}
                              {incident.ip && (
                                <span className="text-blue-400 font-mono">
                                  <span className="font-semibold text-slate-400">IP:</span> {incident.ip}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    )) : (
                      <div className="text-center p-8 text-slate-400">
                        <div className="text-4xl mb-2">🛡️</div>
                        <p className="text-lg mb-1">No incidents detected</p>
                        <p className="text-sm">System appears secure</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
      
      {/* Real-time Alerts */}
      <AlertNotification
        alerts={activeTab === "siem" ? siemAlerts : socAlerts}
        onDismiss={activeTab === "siem" ? handleDismissSiemAlert : handleDismissSocAlert}
        onMarkRead={activeTab === "siem" ? handleMarkReadSiemAlert : handleMarkReadSocAlert}
      />
    </div>
  );
}

