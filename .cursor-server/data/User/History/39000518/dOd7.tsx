"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { API_URL } from "@/lib/api";

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [filterUser, setFilterUser] = useState("");
  const [filterAction, setFilterAction] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, [filterUser, filterAction]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      let url = `${API_URL}/api/audit/logs?limit=50`;
      if (filterUser) url += `&user=${filterUser}`;
      if (filterAction) url += `&action=${filterAction}`;
      
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs || []);
        setTotal(data.total || 0);
      }
    } catch (err) {
      console.error("Error fetching audit logs:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const res = await fetch(`${API_URL}/api/audit/export?output_file=audit_export.json`);
      if (res.ok) {
        const data = await res.json();
        alert(`تم التصدير بنجاح: ${data.file}`);
      } else {
        alert("فشل التصدير");
      }
    } catch (err) {
      alert("خطأ في التصدير");
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
              <div>
                <h1 className="text-3xl font-bold text-slate-800">📋 Audit Trail</h1>
                <p className="text-slate-600 mt-1">Total logs: {total}</p>
              </div>
              <div className="flex gap-2">
                <Button 
                  onClick={() => setShowFilters(!showFilters)}
                  className="bg-gray-600 hover:bg-gray-700"
                >
                  {showFilters ? "إخفاء" : "🔍 Filters"}
                </Button>
                <Button onClick={handleExport} className="bg-indigo-600 hover:bg-indigo-700">
                  Export Logs
                </Button>
              </div>
            </div>

            {showFilters && (
              <Card className="mb-6 border-indigo-200 bg-indigo-50">
                <CardHeader>
                  <CardTitle className="text-indigo-800">Filters</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="filterUser">Filter by User</Label>
                    <Input
                      id="filterUser"
                      value={filterUser}
                      onChange={(e) => setFilterUser(e.target.value)}
                      placeholder="user@example.com"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="filterAction">Filter by Action</Label>
                    <Input
                      id="filterAction"
                      value={filterAction}
                      onChange={(e) => setFilterAction(e.target.value)}
                      placeholder="api_call"
                      className="mt-1"
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            <Card className="border-slate-200 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-t-lg">
                <CardTitle className="text-white">Activity Log</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {loading ? (
                  <p className="text-slate-500">جاري التحميل...</p>
                ) : logs.length === 0 ? (
                  <p className="text-slate-500 text-center py-8">لا توجد سجلات</p>
                ) : (
                  <div className="space-y-2">
                    {logs.map((log) => (
                      <div key={log.id} className="p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="font-semibold text-slate-800">{log.action}</div>
                            <div className="text-sm text-slate-600 mt-1">
                              User: <span className="font-medium">{log.user}</span> | 
                              IP: <span className="font-medium">{log.ip || "N/A"}</span>
                            </div>
                            {log.payload && (
                              <div className="text-xs text-slate-500 mt-2 bg-white p-2 rounded border">
                                {JSON.stringify(log.payload, null, 2)}
                              </div>
                            )}
                            <div className="text-xs text-slate-500 mt-1">
                              {log.timestamp && new Date(log.timestamp).toLocaleString()}
                            </div>
                          </div>
                          <span className={`px-3 py-1 rounded text-xs font-semibold ${
                            log.status === "success" ? "bg-green-100 text-green-700" :
                            "bg-red-100 text-red-700"
                          }`}>
                            {log.status}
                          </span>
                        </div>
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

    </div>
  );
}

}
