"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

type Blueprint = {
  id?: string;
  name?: string;
  description?: string;
  type?: string;
  created_at?: string;
};

export default function BlueprintsPage() {
  const [blueprints, setBlueprints] = useState<Blueprint[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadBlueprints();
  }, []);

  const loadBlueprints = async () => {
    setLoading(true);
    try {
      // Blueprints API only has POST endpoints (generate, docker-compose, kubernetes, nginx)
      // No list endpoint available, so we'll show empty state
      setBlueprints([]);
    } catch (error) {
      console.error("Error loading blueprints:", error);
      setBlueprints([]);
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
              <CardTitle>📋 Blueprint Generator</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    مولد المخططات - إنشاء blueprints للبنية التحتية والتطبيقات
                  </p>
                  <Button onClick={loadBlueprints} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Blueprints ({blueprints.length})</h3>
                  <div className="space-y-3">
                    {blueprints.length > 0 ? (
                      blueprints.map((blueprint, idx) => (
                        <Card key={`blueprint-${blueprint.id || idx}-${idx}`} className="bg-slate-800 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-semibold">{blueprint.name || `Blueprint ${idx + 1}`}</h4>
                                <p className="text-sm text-slate-400 mt-1">{blueprint.description || "No description"}</p>
                                <div className="mt-2 flex gap-2">
                                  <span className="px-2 py-1 rounded text-xs bg-blue-900 text-blue-200">
                                    {blueprint.type || "infrastructure"}
                                  </span>
                                  <span className="text-xs text-slate-500">
                                    {blueprint.created_at ? new Date(blueprint.created_at).toLocaleDateString() : "Recently"}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-8">No blueprints found</div>
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

