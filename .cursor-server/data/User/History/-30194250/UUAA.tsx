"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://ai-agent.bankid-sy.com";

type LogItem = {
  timestamp: string;
  role: string;
  session_id?: string;
  content: string;
  meta?: Record<string, any>;
};

export default function LogsPage() {
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [limit, setLimit] = useState(100);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/logs?limit=${limit}`)
      .then((res) => res.json())
      .then((data) => {
        setLogs(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
      setLoading(false);
      });
  }, [limit]);

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
    <div className="p-4 space-y-4 bg-slate-950 text-slate-200 min-h-screen">
      <h1 className="text-2xl font-semibold">Agent Logs</h1>
      
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
          onClick={() => {
            setLoading(true);
            fetch(`${API_URL}/api/logs?limit=${limit}`)
              .then((res) => res.json())
              .then((data) => {
                setLogs(data);
                setLoading(false);
              })
              .catch((err) => {
                console.error(err);
                setLoading(false);
              });
          }}
          className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-500"
        >
          تحديث
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
  );
}

