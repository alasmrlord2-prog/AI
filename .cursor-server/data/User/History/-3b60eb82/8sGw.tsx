"use client";
import { apiRequest } from "@/lib/api";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function DebuggerPage() {
  const [errors, setErrors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [watching, setWatching] = useState(false);
  const [autoFix, setAutoFix] = useState(false);

  useEffect(() => {
    fetchErrors();
    const interval = setInterval(fetchErrors, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchErrors = async () => {
    try {
      const data = await apiRequest("/api/debugger/errors?limit=10", {}, 5000);
      setErrors(data.errors || []);
    } catch (err) {
      console.error("Error fetching errors:", err);
    } finally {
      setLoading(false);
    }
  };

  const startWatching = async () => {
    try {
      const res = await fetch(`${getApiUrl()}/api/debugger/watch/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log_dirs: ["/home/ai/ai-agent/backend/app/logs"] })
      });
      if (res.ok) {
        setWatching(true);
      }
    } catch (err) {
      console.error("Error starting watch:", err);
    }
  };

  const stopWatching = async () => {
    try {
      const res = await fetch(`${getApiUrl()}/api/debugger/watch/stop`, {
        method: "POST"
      });
      if (res.ok) {
        setWatching(false);
      }
    } catch (err) {
      console.error("Error stopping watch:", err);
    }
  };

  const toggleAutoFix = async () => {
    try {
      const endpoint = autoFix ? "/api/debugger/auto-fix/disable" : "/api/debugger/auto-fix/enable";
      const res = await fetch(`${getApiUrl()}${endpoint}`, { method: "POST" });
      if (res.ok) {
        setAutoFix(!autoFix);
      }
    } catch (err) {
      console.error("Error toggling auto-fix:", err);
    }
  };

  const handleAnalyzeError = async (error: any) => {
    try {
      const res = await fetch(`${getApiUrl()}/api/debugger/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_path: error.file,
          errors: error.errors || [],
          context: error.context || ""
        })
      });

      if (res.ok) {
        const analysis = await res.json();
        alert(`تحليل الخطأ:\n\nRoot Cause: ${analysis.root_cause}\n\nSolution: ${analysis.solution}\n\nSafe to Fix: ${analysis.safe_to_fix ? "Yes" : "No"}`);
      }
    } catch (err) {
      console.error("Error analyzing:", err);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold text-slate-800">🔍 AI Debugger</h1>
              <div className="flex gap-2">
                <Button 
                  onClick={watching ? stopWatching : startWatching}
                  className={watching ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"}
                >
                  {watching ? "⏹ Stop Watching" : "▶ Start Watching"}
                </Button>
                <Button 
                  onClick={toggleAutoFix}
                  className={autoFix ? "bg-green-600 hover:bg-green-700" : "bg-gray-600 hover:bg-gray-700"}
                >
                  {autoFix ? "✅ Auto-Fix ON" : "❌ Auto-Fix OFF"}
                </Button>
              </div>
            </div>

            <Card className="border-slate-200 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-t-lg">
                <CardTitle className="text-white">Recent Errors</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {loading ? (
                  <p className="text-slate-500">جاري التحميل...</p>
                ) : errors.length === 0 ? (
                  <p className="text-slate-500 text-center py-8">لا توجد أخطاء</p>
                ) : (
                  <div className="space-y-4">
                    {errors.map((error, idx) => (
                      <div key={idx} className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg hover:shadow-md transition-shadow">
                        <div className="font-semibold text-red-800 mb-2">
                          {error.file || "Unknown File"}
                        </div>
                        {error.errors && error.errors.length > 0 && (
                          <div className="bg-white p-3 rounded border border-red-200 mb-2">
                            <pre className="text-sm text-red-700 whitespace-pre-wrap">
                              {error.errors[0].content}
                            </pre>
                          </div>
                        )}
                        <div className="text-xs text-red-600 mt-2">
                          {error.timestamp && new Date(error.timestamp).toLocaleString()}
                        </div>
                        {error.context && (
                          <details className="mt-2">
                            <summary className="text-sm text-red-700 cursor-pointer">View Context</summary>
                            <pre className="text-xs bg-white p-2 rounded mt-2 border border-red-200 overflow-auto max-h-40">
                              {error.context}
                            </pre>
                          </details>
                        )}
                        <Button
                          size="sm"
                          onClick={() => handleAnalyzeError(error)}
                          className="mt-2 bg-blue-600 hover:bg-blue-700 text-xs"
                        >
                          🔍 Analyze with AI
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
