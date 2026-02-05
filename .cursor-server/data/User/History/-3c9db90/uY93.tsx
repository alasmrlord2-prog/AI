"use client";

import { useEffect, useState, useCallback } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";


type LogItem = {
  timestamp: string;
  role: string;
  session_id?: string;
  content: string;
  meta?: Record<string, unknown>;
};

export default function LogsPage() {
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [limit, setLimit] = useState(100);
  const [loading, setLoading] = useState(true);

  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiRequest(`/api/logs?limit=${limit}`, {}, 30000);
      setLogs(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error loading logs:", err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString("ar-SA", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return timestamp;
  }
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 scrollbar-thin">
          <h1 className="text-2xl font-semibold mb-4">Agent Logs</h1>
      
      <div className="flex items-center gap-2 text-sm">
        <span>عدد السطور:</span>
        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="border rounded px-2 py-1 bg-neutral-900 text-neutral-100 border-neutral-700"
        >
          <option value={50}>50</option>
          <option value={100}>100</option>
          <option value={200}>200</option>
          <option value={500}>500</option>
        </select>
        <button
          onClick={loadLogs}
          disabled={loading}
          className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50"
        >
          {loading ? "جاري التحميل..." : "تحديث"}
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-neutral-400">جاري التحميل...</div>
      ) : (
        <div className="border border-neutral-700 rounded-lg overflow-hidden text-sm">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead className="bg-neutral-900">
                <tr>
                  <th className="border border-neutral-700 px-3 py-2 text-left">Time</th>
                  <th className="border border-neutral-700 px-3 py-2 text-left">Role</th>
                  <th className="border border-neutral-700 px-3 py-2 text-left">Session</th>
                  <th className="border border-neutral-700 px-3 py-2 text-left">Content</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, idx) => (
                  <tr key={idx} className="hover:bg-neutral-900/50">
                    <td className="border border-neutral-700 px-3 py-2 align-top">
                      <span className="font-mono text-xs text-neutral-400">
                        {formatTime(log.timestamp)}
                      </span>
                    </td>
                    <td className="border border-neutral-700 px-3 py-2 align-top">
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          log.role === "user"
                            ? "bg-blue-600/20 text-blue-300"
                            : log.role === "assistant"
                            ? "bg-green-600/20 text-green-300"
                            : "bg-red-600/20 text-red-300"
                        }`}
                      >
                        {log.role}
                      </span>
                    </td>
                    <td className="border border-neutral-700 px-3 py-2 align-top">
                      <span className="font-mono text-xs text-neutral-400">
                        {log.session_id || "-"}
                      </span>
                    </td>
                    <td className="border border-neutral-700 px-3 py-2 align-top whitespace-pre-wrap break-words max-w-md">
                      <div className="text-neutral-200">{log.content}</div>
                    </td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td
                      className="border border-neutral-700 px-3 py-4 text-center text-neutral-500"
                      colSpan={4}
                    >
                      لا توجد سجلات بعد.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
        </div>
      </div>
    </main>
  );
}

