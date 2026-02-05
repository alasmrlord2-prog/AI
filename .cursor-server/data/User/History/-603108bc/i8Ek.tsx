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

export default function SnapshotsPage() {
  const [snapshots, setSnapshots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadSnapshots();
  }, []);

  const loadSnapshots = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/snapshots/list`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setSnapshots(data.snapshots || []);
    } catch (error) {
      console.error("Error loading snapshots:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (snapshotId: string) => {
    if (!confirm("هل أنت متأكد من استعادة هذا الـsnapshot؟")) return;
    
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/snapshots/rollback/${snapshotId}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      if (data.success) {
        alert("تم الاستعادة بنجاح");
      }
    } catch (error) {
      console.error("Error rolling back:", error);
      alert("خطأ في الاستعادة");
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
              <CardTitle>📸 Snapshots & Rollback Engine</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    نظام snapshots وrollback شامل (Containers, Volumes, Configs, Full System)
                  </p>
                  <Button onClick={loadSnapshots} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">الـSnapshots ({snapshots.length})</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {snapshots.map((snapshot, idx) => (
                      <Card key={idx} className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h4 className="font-semibold">{snapshot.snapshot_id}</h4>
                              <div className="mt-2 flex gap-2">
                                <span className="px-2 py-1 rounded text-xs bg-blue-900 text-blue-200">
                                  {snapshot.type}
                                </span>
                                <span className="text-sm text-slate-400">{snapshot.target}</span>
                              </div>
                              <div className="mt-2 text-xs text-slate-500">
                                {new Date(snapshot.timestamp).toLocaleString('ar')}
                              </div>
                            </div>
                            <Button
                              onClick={() => handleRollback(snapshot.snapshot_id)}
                              className="bg-orange-600 hover:bg-orange-700"
                              size="sm"
                            >
                              Rollback
                            </Button>
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

