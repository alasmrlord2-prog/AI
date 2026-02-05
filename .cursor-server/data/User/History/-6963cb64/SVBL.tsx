"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type Policy = {
  name: string;
  description?: string;
  effect: "allow" | "deny";
  priority: number;
};

export default function ABACPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/api/abac/policies", {}, 5000);
      setPolicies(data.policies || []);
    } catch (error) {
      console.error("Error loading policies:", error);
      setPolicies([]);
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
              <CardTitle>🛡️ Zero-Trust Access Control (ABAC)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    نظام صلاحيات متقدم يعتمد على الصفات والظروف
                  </p>
                  <Button onClick={loadPolicies} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>
                
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">السياسات ({policies.length})</h3>
                  <div className="space-y-3">
                    {policies.map((policy, idx) => (
                      <Card key={idx} className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold">{policy.name}</h4>
                              <p className="text-sm text-slate-400 mt-1">{policy.description}</p>
                              <div className="mt-2 flex gap-2">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  policy.effect === "allow" ? "bg-green-900 text-green-200" : "bg-red-900 text-red-200"
                                }`}>
                                  {policy.effect}
                                </span>
                                <span className="px-2 py-1 rounded text-xs bg-slate-700">
                                  Priority: {policy.priority}
                                </span>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
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

