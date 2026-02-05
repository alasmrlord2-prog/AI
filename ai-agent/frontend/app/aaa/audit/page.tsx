"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { auditApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Shield } from "lucide-react";

type AuditLog = {
  id: string;
  action: string;
  user_id?: string;
  tenant_id?: string;
  resource_type?: string;
  resource_id?: string;
  feature_key?: string;
  ip_address?: string;
  endpoint?: string;
  status: string;
  created_at: string;
  metadata?: Record<string, unknown>;
};

export default function AuditPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);

  const fetchAuditLogs = useCallback(async () => {
    try {
      setLoading(true);
      const data = await auditApi.getAuditLogs({ limit: 50, offset: 0 });
      setLogs(data.logs || []);
      setTotal(data.total || 0);
    } catch (error) {
      console.error("Error fetching audit logs:", error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      // If authentication error, redirect to login
      if (errorMessage.includes("Not authenticated") || errorMessage.includes("401")) {
        localStorage.removeItem("auth_token");
        router.push("/aaa/login");
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/aaa/login");
      return;
    }
    fetchAuditLogs();
    const interval = setInterval(fetchAuditLogs, 60000);
    return () => clearInterval(interval);
  }, [router, fetchAuditLogs]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Audit Logs</h1>
          <p className="text-gray-500 mt-1">System activity and security logs ({total} total)</p>
        </div>
      </div>

      {/* Audit Logs */}
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="text-gray-900">Recent Activity ({logs.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-gray-500 text-center py-8">Loading...</div>
          ) : logs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-200">
                    <th className="pb-3">Time</th>
                    <th className="pb-3">Action</th>
                    <th className="pb-3">User</th>
                    <th className="pb-3">Resource</th>
                    <th className="pb-3">Feature</th>
                    <th className="pb-3">IP Address</th>
                    <th className="pb-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id} className="border-t border-gray-200 hover:bg-gray-50">
                      <td className="py-3 text-gray-600">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="py-3 font-medium text-gray-900">{log.action}</td>
                      <td className="py-3 text-gray-600">
                        {log.user_id ? log.user_id.substring(0, 8) + "..." : "N/A"}
                      </td>
                      <td className="py-3 text-gray-600">
                        {log.resource_type ? `${log.resource_type}:${log.resource_id?.substring(0, 8) || "N/A"}` : "N/A"}
                      </td>
                      <td className="py-3 text-gray-600">
                        {log.feature_key || "N/A"}
                      </td>
                      <td className="py-3 text-gray-600">{log.ip_address || "N/A"}</td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          log.status === "success" 
                            ? "text-green-600 bg-green-50" 
                            : log.status === "error"
                            ? "text-red-600 bg-red-50"
                            : "text-gray-600 bg-gray-50"
                        }`}>
                          {log.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              <Shield className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No audit logs found</p>
              <p className="text-sm mt-2">All system activities are logged for security and compliance</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

