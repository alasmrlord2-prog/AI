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
  loading: () => <div className="p-4 text-slate-400">جاري تحميل Chat...</div>,
});
const ChatContainer = dynamic(() => import("@/components/chat/ChatContainer"), {
  loading: () => <div className="p-4 text-slate-400">جاري تحميل المحادثة...</div>,
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
        const data = await apiRequest("/api/monitor", { method: "GET" }, 5000).catch(() => null);
        if (data) {
          setSystemData(data);
          const now = new Date().toLocaleTimeString();
          if (data.cpu_percent !== undefined && typeof data.cpu_percent === 'number') {
            setCpuHistory((prev) => {
              const newData = { label: now, value: data.cpu_percent };
              const updated = [...prev, newData];
              return updated.slice(-20); // Keep last 20 points
            });
          }
          if (data.memory_percent !== undefined && typeof data.memory_percent === 'number') {
            setMemoryHistory((prev) => {
              const newData = { label: now, value: data.memory_percent };
              const updated = [...prev, newData];
              return updated.slice(-20); // Keep last 20 points
            });
          }
        }
      } catch (e) {
        // Ignore errors
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
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

  const quickAccessItems = [
    { href: "/threat-detection", icon: "🤖", label: "Threat Detection" },
    { href: "/abac", icon: "🛡️", label: "ABAC" },
    { href: "/digital-twin", icon: "🌍", label: "Digital Twin" },
    { href: "/cicd", icon: "🚀", label: "CI/CD" },
    { href: "/agent-mesh", icon: "🌐", label: "Agent Mesh" },
    { href: "/code-review", icon: "🔍", label: "Code Review" },
    { href: "/snapshots", icon: "📸", label: "Snapshots" },
    { href: "/workflow-builder", icon: "🔧", label: "Workflow Builder" },
    { href: "/blueprints", icon: "📋", label: "Blueprint" },
    { href: "/plugins", icon: "🧩", label: "Plugins" },
    { href: "/logs", icon: "📋", label: "Logs" },
    { href: "/visualization", icon: "📊", label: "Visualization" },
  ];

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header locale={locale} setLocale={handleSetLocale} />

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Row 1: System Overview */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 md:gap-4">
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-3 md:p-4">
                <div className="text-xs md:text-sm text-slate-400">Total Modules</div>
                <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-blue-400">31</div>
                <div className="text-xs text-slate-500 mt-1">Active Features</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-3 md:p-4">
                <div className="text-xs md:text-sm text-slate-400">AI Status</div>
                <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-green-400">✅</div>
                <div className="text-xs text-slate-500 mt-1">Operational</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-3 md:p-4">
                <div className="text-xs md:text-sm text-slate-400">Security Health</div>
                <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-green-400">98%</div>
                <div className="text-xs text-slate-500 mt-1">Protected</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-3 md:p-4">
                <div className="text-xs md:text-sm text-slate-400">Incidents Today</div>
                <div className="text-2xl md:text-3xl font-bold mt-1 md:mt-2 text-yellow-400">2</div>
                <div className="text-xs text-slate-500 mt-1">Resolved</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800 col-span-2 sm:col-span-1">
              <CardContent className="p-3 md:p-4">
                <div className="text-xs md:text-sm text-slate-400">CPU / RAM</div>
                <div className="text-xl md:text-2xl font-bold mt-1 md:mt-2">
                  <span className="text-blue-400">{systemData?.cpu_percent?.toFixed(1) || "0"}%</span>
                  {" / "}
                  <span className="text-purple-400">{systemData?.memory_percent?.toFixed(1) || "0"}%</span>
                </div>
                <div className="text-xs text-slate-500 mt-1">Current Usage</div>
              </CardContent>
            </Card>
          </div>

          {/* Row 2: Realtime Health */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-sm">CPU Trend</CardTitle>
              </CardHeader>
              <CardContent>
                {cpuHistory.length > 0 ? (
                  <LineChart
                    data={cpuHistory}
                    color="#3b82f6"
                    height={120}
                  />
                ) : (
                  <div className="h-[120px] flex items-center justify-center text-slate-500">
                    No data
                  </div>
                )}
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-sm">Memory Trend</CardTitle>
              </CardHeader>
              <CardContent>
                {memoryHistory.length > 0 ? (
                  <LineChart
                    data={memoryHistory}
                    color="#a855f7"
                    height={120}
                  />
                ) : (
                  <div className="h-[120px] flex items-center justify-center text-slate-500">
                    No data
                  </div>
                )}
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400 mb-2">Disk I/O</div>
                <div className="text-2xl font-bold text-green-400">
                  {systemData?.disk_read_mbps?.toFixed(2) || "0"} MB/s
                </div>
                <div className="text-xs text-slate-500 mt-1">Read / Write</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400 mb-2">Network Throughput</div>
                <div className="text-2xl font-bold text-cyan-400">
                  {systemData?.network_rx_mbps?.toFixed(2) || "0"} MB/s
                </div>
                <div className="text-xs text-slate-500 mt-1">RX / TX</div>
              </CardContent>
            </Card>
          </div>

          {/* Row 3: Security Overview */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>Security Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-800 rounded">
                  <div className="text-sm text-slate-400">Threats Detected (24h)</div>
                  <div className="text-2xl font-bold mt-2 text-red-400">3</div>
                  <div className="text-xs text-slate-500 mt-1">Auto-blocked</div>
                </div>
                <div className="p-4 bg-slate-800 rounded">
                  <div className="text-sm text-slate-400">Auto-Hardening Results</div>
                  <div className="text-2xl font-bold mt-2 text-green-400">12</div>
                  <div className="text-xs text-slate-500 mt-1">Applied today</div>
                </div>
                <div className="p-4 bg-slate-800 rounded">
                  <div className="text-sm text-slate-400">Behavior Anomalies</div>
                  <div className="text-2xl font-bold mt-2 text-yellow-400">1</div>
                  <div className="text-xs text-slate-500 mt-1">Under review</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Row 4: Quick Access */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-base md:text-lg">Quick Access</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 gap-2 md:gap-3">
                {quickAccessItems.map((item, index) => (
                  <Link
                    key={`quick-access-${item.href}-${item.label}-${index}`}
                    href={item.href}
                    prefetch={true}
                    className="p-3 md:p-4 bg-slate-800 rounded hover:bg-slate-700 transition text-center cursor-pointer border border-slate-700 hover:border-slate-600"
                    onMouseEnter={() => router.prefetch(item.href)}
                  >
                    <div className="text-2xl md:text-3xl mb-1 md:mb-2">{item.icon}</div>
                    <div className="text-xs md:text-sm font-medium">{item.label}</div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Row 5: Agent Console Quick Action */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>
                {locale === "ar" ? "وحدة التحكم" : "Agent Console"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ChatBox
                input={input}
                setInput={setInput}
                onSend={sendQuery}
                loading={loading}
                locale={locale}
              />
              <div className="mt-4 max-h-64 overflow-y-auto">
                <ChatContainer messages={messages} locale={locale} />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
