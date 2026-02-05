"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type HardeningStatus = {
  recommendations?: unknown[];
  suggestions?: unknown[];
  [key: string]: unknown;
};

type Suggestion = {
  id?: string;
  title?: string;
  description?: string;
  severity?: string;
  category?: string;
};

export default function HardeningPage() {
  const [status, setStatus] = useState<HardeningStatus | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const statusData = await apiRequest("/api/security/hardening/status", {}, 5000).catch(() => ({}));
      setStatus(statusData);
      
      // Convert status to suggestions format if needed
      const recommendations = statusData?.recommendations || statusData?.suggestions || [];
      setSuggestions(Array.isArray(recommendations) ? recommendations : []);
    } catch (error) {
      console.error("Error loading hardening status:", error);
      setStatus(null);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!confirm("هل أنت متأكد من تطبيق التحصين؟")) return;

    setLoading(true);
    try {
      const data = await apiRequest("/api/security/hardening/apply", {
        method: "POST",
      }, 30000);
      
      if (data.success) {
        alert("تم تطبيق التحصين بنجاح");
        loadStatus();
      }
    } catch (error) {
      console.error("Error applying hardening:", error);
      alert(`خطأ في تطبيق التحصين: ${error instanceof Error ? error.message : "خطأ غير معروف"}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header locale={locale} setLocale={handleSetLocale} />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>🔒 Auto-Hardening</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    التحصين التلقائي - تأمين النظام تلقائياً
                  </p>
                  <div className="flex gap-2">
                    <Button onClick={loadStatus} disabled={loading}>
                      {loading ? "جاري التحميل..." : "تحديث"}
                    </Button>
                    <Button onClick={() => handleApply()} disabled={loading} className="bg-green-600 hover:bg-green-700">
                      تطبيق التحصين
                    </Button>
                  </div>
                </div>

                {/* Status */}
                {status && (
                  <div className="mt-4 p-4 bg-slate-800 rounded">
                    <div className="text-sm font-semibold mb-2">Hardening Status</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-xs text-slate-400">Score</div>
                        <div className="text-2xl font-bold text-green-400">
                          {status.score || status.hardening_score || "N/A"}%
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400">Applied</div>
                        <div className="text-2xl font-bold text-blue-400">
                          {status.applied_rules || status.applied || 0}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400">Pending</div>
                        <div className="text-2xl font-bold text-yellow-400">
                          {status.pending_rules || status.pending || 0}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400">Status</div>
                        <div className="text-xl font-bold text-green-400">
                          {status.status === "active" ? "✅ Active" : "⚠️ Inactive"}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Suggestions */}
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Hardening Suggestions ({suggestions.length})</h3>
                  <div className="space-y-3">
                    {suggestions.length > 0 ? (
                      suggestions.map((suggestion, idx) => (
                        <Card key={`suggestion-${suggestion.id || suggestion.title || idx}-${idx}`} className="bg-slate-800 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <h4 className="font-semibold">{suggestion.title || suggestion.name || `Suggestion ${idx + 1}`}</h4>
                                <p className="text-sm text-slate-400 mt-1">{suggestion.description || suggestion.message || "No description"}</p>
                                <div className="mt-2 flex gap-2">
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    suggestion.priority === "high" ? "bg-red-900 text-red-200" :
                                    suggestion.priority === "medium" ? "bg-yellow-900 text-yellow-200" :
                                    "bg-blue-900 text-blue-200"
                                  }`}>
                                    {suggestion.priority || "low"}
                                  </span>
                                </div>
                              </div>
                              <Button
                                onClick={() => handleApply(suggestion.id)}
                                className="bg-blue-600 hover:bg-blue-700"
                                size="sm"
                              >
                                Apply
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-8">No suggestions available</div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

