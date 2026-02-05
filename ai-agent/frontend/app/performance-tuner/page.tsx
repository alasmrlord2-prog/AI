"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type PerformanceAnalysis = {
  recommendations?: unknown[];
  metrics?: Record<string, unknown>;
  [key: string]: unknown;
};

export default function PerformanceTunerPage() {
  const [analysis, setAnalysis] = useState<PerformanceAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadAnalysis();
  }, []);

  const loadAnalysis = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/api/performance/tuner/analyze", {}, 10000); // 10s for analysis
      setAnalysis(data);
    } catch (error) {
      console.error("Error loading analysis:", error);
      setAnalysis(null);
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
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 scrollbar-thin">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>🎛️ AI Performance Tuner</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">جاري التحليل...</div>
              ) : analysis ? (
                <div className="space-y-6">
                  {analysis.current_metrics && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                      <Card className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="text-sm text-slate-400">CPU</div>
                          <div className="text-2xl font-bold mt-1 text-blue-400">
                            {analysis.current_metrics.cpu_percent?.toFixed(1)}%
                          </div>
                        </CardContent>
                      </Card>
                      <Card className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="text-sm text-slate-400">Memory</div>
                          <div className="text-2xl font-bold mt-1 text-green-400">
                            {analysis.current_metrics.memory_percent?.toFixed(1)}%
                          </div>
                        </CardContent>
                      </Card>
                      <Card className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="text-sm text-slate-400">Response Time</div>
                          <div className="text-2xl font-bold mt-1 text-purple-400">
                            {analysis.current_metrics.response_time_ms?.toFixed(0)}ms
                          </div>
                        </CardContent>
                      </Card>
                      <Card className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="text-sm text-slate-400">Error Rate</div>
                          <div className="text-2xl font-bold mt-1 text-red-400">
                            {(analysis.current_metrics.error_rate * 100)?.toFixed(2)}%
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  )}

                  {analysis.recommendations && analysis.recommendations.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold mb-4">
                        التوصيات ({analysis.recommendations.length})
                      </h3>
                      <div className="space-y-3">
                        {Array.isArray(analysis.recommendations) ? analysis.recommendations.map((rec: Record<string, unknown>, idx: number) => {
                          const recObj = rec as { type?: string; severity?: string; issue?: string; recommendation?: string; action?: string; potential_savings?: number };
                          return (
                            <Card key={idx} className="bg-slate-800 border-slate-700">
                              <CardContent className="p-4">
                                <div className="flex justify-between items-start">
                                  <div>
                                    <div className="flex items-center gap-2 mb-2">
                                      <span className={`px-2 py-1 rounded text-xs ${
                                        recObj.severity === "critical" ? "bg-red-900 text-red-200" :
                                        recObj.severity === "high" ? "bg-orange-900 text-orange-200" :
                                        "bg-yellow-900 text-yellow-200"
                                      }`}>
                                        {recObj.severity}
                                      </span>
                                      <span className="text-xs text-slate-400">{recObj.type}</span>
                                    </div>
                                    <h4 className="font-semibold">{recObj.issue}</h4>
                                    <p className="text-sm text-slate-300 mt-1">{recObj.recommendation}</p>
                                    {recObj.action && (
                                      <div className="mt-2 text-xs text-slate-400">
                                        Action: {recObj.action}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          );
                        }) : null}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400">لا توجد بيانات</div>
              )}
              <div className="mt-6">
                <Button onClick={loadAnalysis} disabled={loading}>
                  {loading ? "جاري التحليل..." : "تحليل جديد"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

