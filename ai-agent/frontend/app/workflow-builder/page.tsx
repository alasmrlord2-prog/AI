"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type Workflow = {
  id?: string;
  name?: string;
  description?: string;
  status?: string;
};

export default function WorkflowBuilderPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    setLoading(true);
    try {
      // Try with trailing slash first (FastAPI standard)
      const data = await apiRequest("/api/workflows/builder/", {}, 5000).catch(async () => {
        // Fallback to without trailing slash
        return await apiRequest("/api/workflows/builder", {}, 5000);
      });
      setWorkflows(data.workflows || []);
    } catch (error) {
      console.error("Error loading workflows:", error);
      // Set empty array on error - don't show error to user, just empty state
      setWorkflows([]);
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
              <CardTitle>🔧 AI Workflow Builder</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    باني workflows ذكي - Auto-complete, Suggestions, Debug, Execution map
                  </p>
                  <Button onClick={loadWorkflows} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Workflows ({workflows.length})</h3>
                  <div className="space-y-3">
                    {workflows.map((workflow, idx) => (
                      <Card key={`workflow-${workflow.id || workflow.name || idx}-${idx}`} className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold">{workflow.name}</h4>
                              <p className="text-sm text-slate-400 mt-1">{workflow.description}</p>
                              <div className="mt-2 flex gap-2">
                                <span className="text-xs text-slate-500">
                                  Steps: {Object.keys(workflow.steps || {}).length}
                                </span>
                                <span className="text-xs text-slate-500">
                                  Created: {new Date(workflow.created_at).toLocaleDateString('ar')}
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

