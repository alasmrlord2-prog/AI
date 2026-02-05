"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { crmApi, identityApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type User = {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  status: string;
  mfa_enabled: boolean;
  email_verified: boolean;
  last_login_at?: string;
  last_login_ip?: string;
  last_login_location?: string;
  active_sessions_count: number;
  api_tokens_count: number;
  sessions: Array<{
    id: string;
    device_info?: string;
    ip_address?: string;
    user_agent?: string;
    last_activity_at?: string;
    expires_at?: string;
  }>;
};

export default function TenantUsersPage() {
  const params = useParams();
  const router = useRouter();
  const tenantId = params.tenantId as string;
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUsers();
    const interval = setInterval(fetchUsers, 30000);
    return () => clearInterval(interval);
  }, [tenantId]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await crmApi.getTenantUsers(tenantId);
      setUsers(response.users || []);
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId: string, userId: string) => {
    try {
      await identityApi.revokeSession(sessionId);
      fetchUsers();
    } catch (error) {
      console.error("Error revoking session:", error);
      alert("Failed to revoke session");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500/20 text-green-400";
      case "disabled":
        return "bg-red-500/20 text-red-400";
      case "invited":
        return "bg-yellow-500/20 text-yellow-400";
      default:
        return "bg-slate-500/20 text-slate-400";
    }
  };

  return (
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Header */}
          <div className="flex justify-between items-center">
            <div>
              <Button
                variant="ghost"
                onClick={() => router.push(`/crm/tenants/${tenantId}`)}
                className="text-slate-400 hover:text-slate-200 mb-2"
              >
                ← Back to Dashboard
              </Button>
              <h1 className="text-2xl md:text-3xl font-bold">Users Management</h1>
              <p className="text-slate-400 mt-1">{users.length} users</p>
            </div>
            <Button
              onClick={() => router.push(`/crm/tenants/${tenantId}/users/new`)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              + Add User
            </Button>
          </div>

          {/* Users List */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Users List</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-slate-400 text-center py-8">Loading...</div>
                ) : users.length > 0 ? (
                  <div className="space-y-3">
                    {users.map((user) => (
                      <div
                        key={user.id}
                        className={`p-4 bg-slate-800 rounded border-l-4 cursor-pointer transition-colors ${
                          selectedUser?.id === user.id ? "border-blue-500 bg-slate-750" : "border-slate-700"
                        }`}
                        onClick={() => setSelectedUser(user)}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="font-semibold">{user.full_name || user.email}</div>
                            <div className="text-sm text-slate-400 mt-1">{user.email}</div>
                            <div className="flex gap-2 mt-2">
                              <span className={`px-2 py-1 rounded text-xs ${getStatusColor(user.status)}`}>
                                {user.status}
                              </span>
                              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                                {user.role}
                              </span>
                              {user.mfa_enabled && (
                                <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
                                  MFA
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-slate-500 mt-2">
                              Last login: {user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "Never"}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-slate-500 text-center py-8">No users found</div>
                )}
              </CardContent>
            </Card>

            {/* User Details */}
            {selectedUser && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>User Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Basic Info */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Basic Information</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Email:</span>
                        <span className="text-slate-200">{selectedUser.email}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Full Name:</span>
                        <span className="text-slate-200">{selectedUser.full_name || "N/A"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Role:</span>
                        <span className="text-blue-400">{selectedUser.role}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Status:</span>
                        <span className={getStatusColor(selectedUser.status).split(" ")[1]}>
                          {selectedUser.status}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Email Verified:</span>
                        <span className={selectedUser.email_verified ? "text-green-400" : "text-red-400"}>
                          {selectedUser.email_verified ? "Yes" : "No"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">MFA Enabled:</span>
                        <span className={selectedUser.mfa_enabled ? "text-green-400" : "text-red-400"}>
                          {selectedUser.mfa_enabled ? "Yes" : "No"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Last Login */}
                  {selectedUser.last_login_at && (
                    <div>
                      <h3 className="text-lg font-semibold mb-3">Last Login</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Date:</span>
                          <span className="text-slate-200">
                            {new Date(selectedUser.last_login_at).toLocaleString()}
                          </span>
                        </div>
                        {selectedUser.last_login_ip && (
                          <div className="flex justify-between">
                            <span className="text-slate-400">IP Address:</span>
                            <span className="text-slate-200">{selectedUser.last_login_ip}</span>
                          </div>
                        )}
                        {selectedUser.last_login_location && (
                          <div className="flex justify-between">
                            <span className="text-slate-400">Location:</span>
                            <span className="text-slate-200">{selectedUser.last_login_location}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Sessions */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">
                      Active Sessions ({selectedUser.active_sessions_count})
                    </h3>
                    {selectedUser.sessions && selectedUser.sessions.length > 0 ? (
                      <div className="space-y-2">
                        {selectedUser.sessions.map((session) => (
                          <div key={session.id} className="p-3 bg-slate-800 rounded">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="text-sm font-medium">{session.device_info || "Unknown Device"}</div>
                                <div className="text-xs text-slate-400 mt-1">
                                  {session.ip_address && `IP: ${session.ip_address}`}
                                </div>
                                {session.expires_at && (
                                  <div className="text-xs text-slate-500 mt-1">
                                    Expires: {new Date(session.expires_at).toLocaleString()}
                                  </div>
                                )}
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleRevokeSession(session.id, selectedUser.id)}
                                className="text-red-400 hover:text-red-300"
                              >
                                Revoke
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-slate-500 text-sm">No active sessions</div>
                    )}
                  </div>

                  {/* API Tokens */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">API Tokens ({selectedUser.api_tokens_count})</h3>
                    <Button
                      variant="outline"
                      onClick={() => router.push(`/iam/api-tokens?user_id=${selectedUser.id}`)}
                      className="w-full border-slate-700 text-slate-300 mb-2"
                    >
                      Manage API Tokens →
                    </Button>
                    {/* Link to AAA Dashboard */}
                    <Button
                      onClick={() => {
                        // Store user context for AAA
                        localStorage.setItem("aaa_user_id", selectedUser.id);
                        window.open("http://aaa.bankid-sy.com", "_blank");
                      }}
                      className="w-full bg-sw-primary hover:bg-sw-primaryDark text-white mb-2"
                    >
                      Open AAA Dashboard →
                    </Button>
                    <Button
                      onClick={() => {
                        // Open AI Dashboard for this user
                        window.open("http://ai-agent.bankid-sy.com", "_blank");
                      }}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      Open AI Dashboard →
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
  );
}

