"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { getApiUrl, apiRequest } from "@/lib/api";
import dynamic from "next/dynamic";

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

const getWsUrl = () => {
  if (process.env.NEXT_PUBLIC_AGENT_WS_URL) {
    return process.env.NEXT_PUBLIC_AGENT_WS_URL;
  }
  
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    // If accessing via domain, use WS
    if (host === "ai-agent.bankid-sy.com" || host.includes("bankid-sy.com")) {
      return "ws://ai-agent.bankid-sy.com/ws/chat";
    }
    return `ws://${host}:8000/ws/chat`;
  }
  return "ws://ai-agent.bankid-sy.com/ws/chat";
};

export default function Home() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");
  const [authToken, setAuthToken] = useState<string | null>(null);
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

  const sendViaHttp = async (text: string) => {
    const apiUrl = getApiUrl();
    const res = await fetch(`${apiUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();
    updateLastAgentMessage(data.reply || data.result || "");
  };

  const sendQuery = async () => {
    if (!input.trim() || loading) return;
    setLoading(true);

    const userMsg: Message = { role: "user", content: input };
    appendMessage(userMsg);

    const textToSend = input;
    setInput("");

    // Add placeholder for agent message immediately with loading indicator
    appendMessage({ role: "agent", content: "⏳ جاري المعالجة..." });

    // Update loading messages at intervals
    const loadingTimeouts: NodeJS.Timeout[] = [];
    
    loadingTimeouts.push(setTimeout(() => {
      updateLastAgentMessage("⏳ لا يزال جاري المعالجة... قد يستغرق الأمر بضع ثوانٍ إضافية.");
    }, 5000));
    
    loadingTimeouts.push(setTimeout(() => {
      updateLastAgentMessage("⏳ المعالجة لا تزال جارية... قد يستغرق الرد وقتاً أطول للأسئلة المعقدة.");
    }, 15000));
    
    loadingTimeouts.push(setTimeout(() => {
      updateLastAgentMessage("⏳ المعالجة مستمرة... يرجى الانتظار، قد يستغرق الأمر حتى دقيقة واحدة.");
    }, 30000));

    try {
      const data = await apiRequest("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message: textToSend }),
      }, 120000); // 120 second timeout for chat (AI responses can take longer for complex queries)

      // Clear all loading timeouts
      loadingTimeouts.forEach(timeout => clearTimeout(timeout));

      const reply = data.reply || data.result || "";
      
      if (reply) {
        updateLastAgentMessage(reply);
      } else {
        updateLastAgentMessage("لا يوجد رد من السيرفر. تحقق من Backend logs.");
      }
    } catch (error) {
      // Clear all loading timeouts
      loadingTimeouts.forEach(timeout => clearTimeout(timeout));
      
      console.error("Error sending message:", error);
      const errorMessage = error instanceof Error ? error.message : "خطأ غير معروف";
      
      // Provide more helpful error messages
      if (errorMessage.includes("timeout")) {
        updateLastAgentMessage("⏱️ استغرق الرد وقتاً طويلاً جداً (أكثر من دقيقتين).\n\n💡 نصائح:\n- جرب سؤالاً أقصر أو أبسط\n- تحقق من اتصال الإنترنت\n- تأكد من أن الـ Backend يعمل بشكل صحيح\n- قد يكون السؤال معقداً جداً ويتطلب وقتاً أطول\n\n🔄 يمكنك المحاولة مرة أخرى");
      } else if (errorMessage.includes("Failed to fetch") || errorMessage.includes("NetworkError")) {
        updateLastAgentMessage("🌐 خطأ في الاتصال بالخادم.\n\n💡 تحقق من:\n- اتصال الإنترنت\n- حالة الـ Backend (قد يكون متوقفاً)\n- عنوان URL الصحيح\n- Firewall أو Proxy settings");
      } else {
        updateLastAgentMessage(`❌ خطأ: ${errorMessage}\n\n💡 يرجى المحاولة مرة أخرى أو التحقق من Backend logs.`);
      }
    } finally {
      setLoading(false);
    }
  };

  // Wrapper function to match Header's expected type
  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header locale={locale} setLocale={handleSetLocale} />

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 space-y-6 scrollbar-thin">
          {/* Dashboard Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">Total Modules</div>
                <div className="text-3xl font-bold mt-2 text-blue-400">22</div>
                <div className="text-xs text-slate-500 mt-1">Advanced Modules</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">Security Modules</div>
                <div className="text-3xl font-bold mt-2 text-green-400">8</div>
                <div className="text-xs text-slate-500 mt-1">Active Protection</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">AI Modules</div>
                <div className="text-3xl font-bold mt-2 text-purple-400">6</div>
                <div className="text-xs text-slate-500 mt-1">100% Local</div>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">System Status</div>
                <div className="text-3xl font-bold mt-2 text-green-400">✅</div>
                <div className="text-xs text-slate-500 mt-1">All Systems Operational</div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Access */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>Quick Access - Advanced Modules</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                <Link href="/threat-detection" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🤖</div>
                  <div className="text-xs">Threat Detection</div>
                </Link>
                <Link href="/abac" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🛡️</div>
                  <div className="text-xs">ABAC</div>
                </Link>
                <Link href="/cost-analyzer" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">💰</div>
                  <div className="text-xs">Cost Analyzer</div>
                </Link>
                <Link href="/performance-tuner" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🎛️</div>
                  <div className="text-xs">Performance</div>
                </Link>
                <Link href="/global-search" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🔍</div>
                  <div className="text-xs">Global Search</div>
                </Link>
                <Link href="/plugins" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🧩</div>
                  <div className="text-xs">Plugins</div>
                </Link>
                <Link href="/workflow-builder" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🔧</div>
                  <div className="text-xs">Workflows</div>
                </Link>
                <Link href="/snapshots" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">📸</div>
                  <div className="text-xs">Snapshots</div>
                </Link>
                <Link href="/agent-mesh" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🌐</div>
                  <div className="text-xs">Agent Mesh</div>
                </Link>
                <Link href="/digital-twin" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🌍</div>
                  <div className="text-xs">Digital Twin</div>
                </Link>
                <Link href="/code-review" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">🔍</div>
                  <div className="text-xs">Code Review</div>
                </Link>
                <Link href="/blueprints" prefetch={true} className="p-3 bg-slate-800 rounded hover:bg-slate-700 transition text-center">
                  <div className="text-2xl mb-1">📋</div>
                  <div className="text-xs">Blueprints</div>
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Agent Console */}
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

              <ChatContainer messages={messages} locale={locale} />
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
