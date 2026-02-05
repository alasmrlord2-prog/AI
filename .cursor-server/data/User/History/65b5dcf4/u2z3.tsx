"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { identityApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Trash2, Monitor } from "lucide-react";

type Session = {
  id: string;
  user_id: string;
  user_email?: string;
  device_info?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
  last_activity_at?: string;
  expires_at?: string;
  is_active: boolean;
};

export default function SessionsPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const data = await identityApi.getSessions();
      setSessions(data || []);
    } catch (error) {
      console.error("Error fetching sessions:", error);
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
    fetchSessions();
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval);
  }, [router, fetchSessions]);

  const handleRevokeSession = async (sessionId: string) => {
    if (!confirm("Are you sure you want to revoke this session?")) return;
    try {
      await identityApi.revokeSession(sessionId);
      fetchSessions();
    } catch (error) {
      console.error("Error revoking session:", error);
      alert("Failed to revoke session");
    }
  };

  const getStatus = (session: Session) => {
    if (!session.is_active) return { text: "Revoked", color: "text-red-600 bg-red-50" };
    if (session.expires_at && new Date(session.expires_at) < new Date()) {
      return { text: "Expired", color: "text-orange-600 bg-orange-50" };
    }
    return { text: "Active", color: "text-green-600 bg-green-50" };
  };

  const activeSessions = sessions.filter((s) => {
    if (!s.is_active) return false;
    if (s.expires_at && new Date(s.expires_at) < new Date()) return false;
    return true;
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Active Sessions</h1>
          <p className="text-gray-500 mt-1">
            {activeSessions.length} active sessions out of {sessions.length} total
          </p>
        </div>
      </div>

      {/* Sessions Table */}
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="text-gray-900">Sessions ({sessions.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-gray-500 text-center py-8">Loading...</div>
          ) : sessions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-200">
                    <th className="pb-3">User</th>
                    <th className="pb-3">Device</th>
                    <th className="pb-3">IP Address</th>
                    <th className="pb-3">Created</th>
                    <th className="pb-3">Last Activity</th>
                    <th className="pb-3">Expires</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map((session) => {
                    const status = getStatus(session);
                    return (
                      <tr key={session.id} className="border-t border-gray-200 hover:bg-gray-50">
                        <td className="py-3 font-medium text-gray-900">
                          {session.user_email || session.user_id.substring(0, 8) + "..."}
                        </td>
                        <td className="py-3 text-gray-600">
                          <div className="flex items-center gap-2">
                            <Monitor className="w-4 h-4 text-gray-400" />
                            {session.device_info || "Unknown Device"}
                          </div>
                        </td>
                        <td className="py-3 text-gray-600">{session.ip_address || "N/A"}</td>
                        <td className="py-3 text-gray-600">
                          {new Date(session.created_at).toLocaleString()}
                        </td>
                        <td className="py-3 text-gray-600">
                          {session.last_activity_at
                            ? new Date(session.last_activity_at).toLocaleString()
                            : "Never"}
                        </td>
                        <td className="py-3 text-gray-600">
                          {session.expires_at
                            ? new Date(session.expires_at).toLocaleString()
                            : "Never"}
                        </td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${status.color}`}>
                            {status.text}
                          </span>
                        </td>
                        <td className="py-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRevokeSession(session.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">No sessions found</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

