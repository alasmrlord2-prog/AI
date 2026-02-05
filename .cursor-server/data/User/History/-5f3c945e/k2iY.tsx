"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === "ai-agent.bankid-sy.com" || hostname.includes("bankid-sy.com")) {
      return "http://ai-agent.bankid-sy.com";
    }
    return "http://localhost:8000";
  }
  return "http://localhost:8000";
};

export default function DigitalTwinPage() {
  const [twins, setTwins] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadTwins();
  }, []);

  const loadTwins = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/digital-twin`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setTwins(data.twins || []);
    } catch (error) {
      console.error("Error loading twins:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header locale={locale} setLocale={handleSetLocale} />
        <div className="p-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>🌍 Digital Twin Mode</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    Simulation للبنية التحتية - تجربة Updates, Deploys, Failures بدون لمس الإنتاج
                  </p>
                  <Button onClick={loadTwins} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Digital Twins ({twins.length})</h3>
                  <div className="space-y-3">
                    {twins.map((twin, idx) => (
                      <Card key={idx} className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold">{twin.name}</h4>
                              <p className="text-sm text-slate-400 mt-1">{twin.twin_id}</p>
                              <div className="mt-2 flex gap-2">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  twin.status === "created" ? "bg-green-900 text-green-200" :
                                  "bg-yellow-900 text-yellow-200"
                                }`}>
                                  {twin.status}
                                </span>
                                <span className="text-xs text-slate-500">
                                  Created: {new Date(twin.created_at).toLocaleDateString('ar')}
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

