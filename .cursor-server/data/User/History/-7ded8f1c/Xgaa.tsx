"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { getApiUrl, apiRequest } from "@/lib/api";
import dynamic from "next/dynamic";
import LineChart from "@/components/charts/LineChart";

// Lazy load heavy components
const ChatBox = dynamic(() => import("@/components/chat/ChatBox"), {
  loading: () => <div className="p-4 text-sw-text-muted">جاري تحميل Chat...</div>,
});
const ChatContainer = dynamic(() => import("@/components/chat/ChatContainer"), {
  loading: () => <div className="p-4 text-sw-text-muted">جاري تحميل المحادثة...</div>,
});

type Message = {
  role: "user" | "agent";
  content: string;
};

export default function Home() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [systemData, setSystemData] = useState<any>(null);
  const [cpuHistory, setCpuHistory] = useState<Array<{label: string; value: number}>>([]);
  const [memoryHistory, setMemoryHistory] = useState<Array<{label: string; value: number}>>([]);
  const [incidentsToday, setIncidentsToday] = useState<number>(0);
  const [threatsDetected, setThreatsDetected] = useState<number>(0);
  const [hardeningResults, setHardeningResults] = useState<number>(0);
  const [behaviorAnomalies, setBehaviorAnomalies] = useState<number>(0);
  const [totalModules, setTotalModules] = useState<number>(0);
  const [aiStatus, setAiStatus] = useState<string>("⚠️");
  const [aiStatusText, setAiStatusText] = useState<string>("Checking...");
  const [securityHealth, setSecurityHealth] = useState<number>(0);
  const wsRef = useRef<WebSocket | null>(null);

  // Check auth on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (!token) {
        router.push("/login");
      } else {
        setAuthToken(token);
      }
    }
  }, [router]);

  // Fetch system metrics
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // OPTIMIZED: Reduced timeout to 8 seconds since backend is now faster
        const data = await apiRequest("/api/monitor", { method: "GET" }, 8000);
        if (data && typeof data === 'object' && !data.error) {
          setSystemData(data);
          const now = new Date().toLocaleTimeString();
          
          // Handle CPU percent - accept number or convert from string/null
          const cpuValue = data.cpu_percent;
          if (cpuValue !== undefined && cpuValue !== null) {
            const cpuNum = typeof cpuValue === 'number' ? cpuValue : parseFloat(cpuValue);
            if (!isNaN(cpuNum) && cpuNum >= 0) {
              setCpuHistory((prev) => {
                const newData = { label: now, value: cpuNum };
                const updated = [...prev, newData];
                return updated.slice(-20); // Keep last 20 points
              });
            }
          }
          
          // Handle Memory percent - accept number or convert from string/null
          const memValue = data.memory_percent;
          if (memValue !== undefined && memValue !== null) {
            const memNum = typeof memValue === 'number' ? memValue : parseFloat(memValue);
            if (!isNaN(memNum) && memNum >= 0) {
              setMemoryHistory((prev) => {
                const newData = { label: now, value: memNum };
                const updated = [...prev, newData];
                return updated.slice(-20); // Keep last 20 points
              });
            }
          }
        }
      } catch (e) {
        // Log error for debugging but don't show to user (metrics are non-critical)
        if (process.env.NODE_ENV === 'development') {
          console.debug('[Metrics] Failed to fetch metrics:', e instanceof Error ? e.message : String(e));
        }
      }
    };

    // Fetch immediately and then every 5 seconds - OPTIMIZED: reduced timeout
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  // Fetch dashboard statistics - OPTIMIZED: parallel API calls instead of sequential
  useEffect(() => {
    const fetchDashboardStats = async () => {
      // OPTIMIZED: Make all API calls in parallel to reduce total time from sum to max
      // Reduced timeout to 10 seconds since backend endpoints are now faster
      const timeout = 10000; // 10 seconds - backend is optimized now
      
      const [
        incidentsData,
        threatsData,
        hardeningData,
        behaviorData,
        dashboardStats
      ] = await Promise.allSettled([
        apiRequest("/api/incidents/stats/today", { method: "GET" }, timeout).catch(() => null),
        apiRequest("/api/security/threat-detection/summary?hours=24", { method: "GET" }, timeout).catch(() => null),
        apiRequest("/api/security/hardening/status", { method: "GET" }, timeout).catch(() => null),
        apiRequest("/api/alerts/behavior/?resolved=false&hours=24", { method: "GET" }, timeout).catch(() => null),
        apiRequest("/api/dashboard/stats", { method: "GET" }, timeout).catch(() => null)
      ]);

      // Process incidents data
      if (incidentsData.status === 'fulfilled' && incidentsData.value) {
        const data = incidentsData.value;
        if (typeof data === 'object' && typeof data.resolved_today === 'number') {
          setIncidentsToday(data.resolved_today);
        }
      }

      // Process threats data
      if (threatsData.status === 'fulfilled' && threatsData.value) {
        const data = threatsData.value;
        if (typeof data === 'object' && typeof data.total_threats === 'number') {
          setThreatsDetected(data.total_threats);
        }
      }

      // Process hardening data
      if (hardeningData.status === 'fulfilled' && hardeningData.value) {
        const data = hardeningData.value;
        if (typeof data === 'object') {
          const actionsToday = data.actions_today || data.actions || 0;
          if (typeof actionsToday === 'number') {
            setHardeningResults(actionsToday);
          }
        }
      }

      // Process behavior data
      if (behaviorData.status === 'fulfilled' && behaviorData.value) {
        const data = behaviorData.value;
        if (typeof data === 'object' && typeof data.count === 'number') {
          setBehaviorAnomalies(data.count);
        }
      }

      // Process dashboard stats
      if (dashboardStats.status === 'fulfilled' && dashboardStats.value) {
        const data = dashboardStats.value;
        if (typeof data === 'object') {
          if (typeof data.total_modules === 'number' && !isNaN(data.total_modules)) {
            setTotalModules(data.total_modules);
          } else if (data.total_modules === null || data.total_modules === undefined) {
            // Keep current value or set to 0 if null/undefined
            setTotalModules(0);
          }
          if (typeof data.ai_status === 'string') {
            setAiStatus(data.ai_status);
          }
          if (typeof data.ai_status_text === 'string') {
            setAiStatusText(data.ai_status_text);
          }
          if (typeof data.security_health === 'number' && !isNaN(data.security_health)) {
            setSecurityHealth(data.security_health);
          } else if (data.security_health === null || data.security_health === undefined) {
            // Keep current value or set to 0 if null/undefined
            setSecurityHealth(0);
          }
        }
      }
    };

    fetchDashboardStats();
    const interval = setInterval(fetchDashboardStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const appendMessage = (msg: Message) => {
    setMessages((prev) => [...prev, msg]);
  };

  const updateLastAgentMessage = (fullText: string) => {
    setMessages((prev) => {
      const copy = [...prev];
      const last = copy[copy.length - 1];
      if (last && last.role === "agent") {
        copy[copy.length - 1] = {
          ...last,
          content: fullText,
        };
      } else {
        copy.push({ role: "agent", content: fullText });
      }
      return copy;
    });
  };

  const sendQuery = async () => {
    if (!input.trim() || loading) return;
    setLoading(true);

    const userMsg: Message = { role: "user", content: input };
    appendMessage(userMsg);

    const textToSend = input;
    setInput("");

    appendMessage({ role: "agent", content: "⏳ جاري المعالجة..." });

    const loadingTimeouts: NodeJS.Timeout[] = [];
    loadingTimeouts.push(setTimeout(() => {
      updateLastAgentMessage("⏳ لا يزال جاري المعالجة... قد يستغرق الأمر بضع ثوانٍ إضافية.");
    }, 10000));
    loadingTimeouts.push(setTimeout(() => {
      updateLastAgentMessage("⏳ المعالجة لا تزال جارية... بدون GPU، قد يستغرق الرد وقتاً أطول.");
    }, 30000));

    try {
      const data = await apiRequest("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message: textToSend }),
      }, 600000);

      loadingTimeouts.forEach(timeout => clearTimeout(timeout));

      const reply = data.reply || data.result || "";
      if (reply) {
        updateLastAgentMessage(reply);
      } else {
        updateLastAgentMessage("لا يوجد رد من السيرفر. تحقق من Backend logs.");
      }
    } catch (error) {
      loadingTimeouts.forEach(timeout => clearTimeout(timeout));
      console.error("Error sending message:", error);
      const errorMessage = error instanceof Error ? error.message : "خطأ غير معروف";
      
      if (errorMessage.includes("timeout")) {
        updateLastAgentMessage("⏱️ استغرق الرد وقتاً طويلاً جداً.");
      } else if (errorMessage.includes("Failed to fetch")) {
        updateLastAgentMessage("🌐 خطأ في الاتصال بالخادم.");
      } else {
        updateLastAgentMessage(`❌ خطأ: ${errorMessage}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  return (
    <main className="flex bg-sw-bg text-sw-text h-screen w-screen overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header locale={locale} setLocale={handleSetLocale} />

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 scrollbar-thin min-h-0">
          <div className="flex gap-4 md:gap-6 h-full">
            {/* Main Content - Agent Console */}
            <div className="flex-1 min-w-0">
              <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark h-full flex flex-col">
                <CardHeader>
                  <CardTitle className="text-sw-text-strong">
                    {locale === "ar" ? "وحدة التحكم" : "Agent Console"}
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col min-h-0">
                  <ChatBox
                    input={input}
                    setInput={setInput}
                    onSend={sendQuery}
                    loading={loading}
                    locale={locale}
                  />
                  <div className="mt-4 flex-1 overflow-y-auto">
                    <ChatContainer messages={messages} locale={locale} />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Sidebar - Metrics */}
            <div className="w-80 flex-shrink-0 space-y-4 md:space-y-6 overflow-y-auto">
              {/* System Overview */}
              <div className="grid grid-cols-2 gap-3 md:gap-4">
                <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-sw-text-soft">Total Modules</div>
                    <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-sw-blue">{totalModules || 0}</div>
                    <div className="text-xs text-sw-text-muted mt-1">Active Features</div>
                  </CardContent>
                </Card>
                <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-sw-text-soft">AI Status</div>
                    <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-sw-success">{aiStatus}</div>
                    <div className="text-xs text-sw-text-muted mt-1">{aiStatusText}</div>
                  </CardContent>
                </Card>
                <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-sw-text-soft">Security Health</div>
                    <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-sw-success">
                      {(securityHealth != null && !isNaN(securityHealth) ? securityHealth.toFixed(1) : "0")}%
                    </div>
                    <div className="text-xs text-sw-text-muted mt-1">Protected</div>
                  </CardContent>
                </Card>
                <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                  <CardContent className="p-3 md:p-4">
                    <div className="text-xs md:text-sm text-sw-text-soft">Incidents Today</div>
                    <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-sw-warning">{incidentsToday}</div>
                    <div className="text-xs text-sw-text-muted mt-1">Resolved</div>
                  </CardContent>
                </Card>
              </div>

              {/* CPU / RAM */}
              <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                <CardContent className="p-3 md:p-4">
                  <div className="text-xs md:text-sm text-sw-text-soft">CPU / RAM</div>
                  <div className="text-xl md:text-2xl font-bold mt-1 md:mt-2">
                    <span className="text-sw-blue">
                      {systemData?.cpu_percent != null && !isNaN(systemData.cpu_percent) 
                        ? systemData.cpu_percent.toFixed(1) 
                        : "0"}%
                    </span>
                    {" / "}
                    <span className="text-sw-teal">
                      {systemData?.memory_percent != null && !isNaN(systemData.memory_percent) 
                        ? systemData.memory_percent.toFixed(1) 
                        : "0"}%
                    </span>
                  </div>
                  <div className="text-xs text-sw-text-muted mt-1">Current Usage</div>
                </CardContent>
              </Card>

              {/* CPU Trend */}
              <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                <CardHeader>
                  <CardTitle className="text-sm text-sw-text-soft">CPU Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  {cpuHistory.length > 0 ? (
                    <LineChart
                      data={cpuHistory}
                      color="#1399FF"
                      height={120}
                    />
                  ) : (
                    <div className="h-[120px] flex items-center justify-center text-sw-text-muted">
                      No data
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Memory Trend */}
              <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                <CardHeader>
                  <CardTitle className="text-sm text-sw-text-soft">Memory Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  {memoryHistory.length > 0 ? (
                    <LineChart
                      data={memoryHistory}
                      color="#00D1CE"
                      height={120}
                    />
                  ) : (
                    <div className="h-[120px] flex items-center justify-center text-sw-text-muted">
                      No data
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Disk I/O */}
              <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                <CardContent className="p-4">
                  <div className="text-sm text-sw-text-soft mb-2">Disk I/O</div>
                  <div className="text-2xl font-bold text-sw-success">
                    {systemData?.disk_read_mbps != null && !isNaN(systemData.disk_read_mbps) 
                      ? systemData.disk_read_mbps.toFixed(2) 
                      : "0"} MB/s
                  </div>
                  <div className="text-xs text-sw-text-muted mt-1">Read / Write</div>
                </CardContent>
              </Card>

              {/* Network Throughput */}
              <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                <CardContent className="p-4">
                  <div className="text-sm text-sw-text-soft mb-2">Network Throughput</div>
                  <div className="text-2xl font-bold text-sw-blue">
                    {systemData?.network_rx_mbps != null && !isNaN(systemData.network_rx_mbps) 
                      ? systemData.network_rx_mbps.toFixed(2) 
                      : "0"} MB/s
                  </div>
                  <div className="text-xs text-sw-text-muted mt-1">RX / TX</div>
                </CardContent>
              </Card>

              {/* Security Overview */}
              <Card className="bg-sw-bg-card border-sw-border shadow-sw-card dark:shadow-sw-card-dark">
                <CardHeader>
                  <CardTitle className="text-sw-text-strong">Security Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-4 bg-sw-bg-soft rounded-md">
                      <div className="text-sm text-sw-text-soft">Threats Detected (24h)</div>
                      <div className="text-2xl font-bold mt-2 text-sw-danger">{threatsDetected}</div>
                      <div className="text-xs text-sw-text-muted mt-1">Auto-blocked</div>
                    </div>
                    <div className="p-4 bg-sw-bg-soft rounded-md">
                      <div className="text-sm text-sw-text-soft">Auto-Hardening Results</div>
                      <div className="text-2xl font-bold mt-2 text-sw-success">{hardeningResults}</div>
                      <div className="text-xs text-sw-text-muted mt-1">Applied today</div>
                    </div>
                    <div className="p-4 bg-sw-bg-soft rounded-md">
                      <div className="text-sm text-sw-text-soft">Behavior Anomalies</div>
                      <div className="text-2xl font-bold mt-2 text-sw-warning">{behaviorAnomalies}</div>
                      <div className="text-xs text-sw-text-muted mt-1">Under review</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
