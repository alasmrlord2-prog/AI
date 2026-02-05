"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type CostMetrics = {
  cpu?: { cost_per_hour?: number; cost_30d?: number };
  memory?: { cost_per_hour?: number; cost_30d?: number };
  storage?: { cost_per_hour?: number; cost_30d?: number };
  total?: { cost_per_hour?: number; cost_per_year?: number };
};

type Recommendation = {
  type: string;
  message: string;
  potential_savings?: number;
};

export default function CostAnalyzerPage() {
  const [metrics, setMetrics] = useState<CostMetrics | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadMetrics();
    loadRecommendations();
  }, []);

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/api/cost/metrics", {}, 5000); // 5 second timeout
      setMetrics(data);
    } catch (error) {
      console.error("Error loading metrics:", error);
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const data = await apiRequest("/api/cost/recommendations", {}, 5000); // 5 second timeout
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error("Error loading recommendations:", error);
      setRecommendations([]);
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
              <CardTitle>💰 Infrastructure Cost Analyzer</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">جاري التحميل...</div>
              ) : metrics ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">CPU Cost/Hour</div>
                        <div className="text-2xl font-bold mt-1 text-blue-400">
                          ${metrics.cpu?.cost_per_hour?.toFixed(4) || "0.0000"}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          Monthly: ${metrics.cpu?.cost_30d?.toFixed(2) || "0.00"}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">Memory Cost/Hour</div>
                        <div className="text-2xl font-bold mt-1 text-green-400">
                          ${metrics.memory?.cost_per_hour?.toFixed(4) || "0.0000"}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          Monthly: ${metrics.memory?.cost_30d?.toFixed(2) || "0.00"}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">Storage Cost/Hour</div>
                        <div className="text-2xl font-bold mt-1 text-purple-400">
                          ${metrics.storage?.cost_per_hour?.toFixed(4) || "0.0000"}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          Monthly: ${metrics.storage?.cost_30d?.toFixed(2) || "0.00"}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-slate-800 border-slate-700">
                      <CardContent className="p-4">
                        <div className="text-sm text-slate-400">Total Cost/Hour</div>
                        <div className="text-2xl font-bold mt-1 text-yellow-400">
                          ${metrics.total?.cost_per_hour?.toFixed(4) || "0.0000"}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          Yearly: ${metrics.total?.cost_per_year?.toFixed(2) || "0.00"}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {recommendations.length > 0 && (
                    <div className="mt-6">
                      <h3 className="text-lg font-semibold mb-4">توصيات لتقليل التكاليف</h3>
                      <div className="space-y-3">
                        {recommendations.map((rec, idx) => (
                          <Card key={idx} className="bg-slate-800 border-slate-700">
                            <CardContent className="p-4">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h4 className="font-semibold">{rec.type}</h4>
                                  <p className="text-sm text-slate-300 mt-1">{rec.message}</p>
                                  <div className="mt-2 text-sm text-green-400">
                                    توفير محتمل: ${rec.potential_savings?.toFixed(2)}
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400">لا توجد بيانات</div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

