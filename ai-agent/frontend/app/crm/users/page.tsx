"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

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
};

type TenantUser = {
  tenant_id: string;
  tenant_name: string;
  users: User[];
};

export default function UsersPage() {
  const router = useRouter();
  const [allUsers, setAllUsers] = useState<TenantUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchAllUsers();
    const interval = setInterval(fetchAllUsers, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAllUsers = async () => {
    try {
      setLoading(true);
      // Get all tenants first
      const tenantsResponse = await crmApi.listTenants(1000, 0);
      const tenants = tenantsResponse.tenants || [];
      
      // Get users for each tenant
      const usersByTenant: TenantUser[] = [];
      for (const tenant of tenants) {
        try {
          const usersResponse = await crmApi.getTenantUsers(tenant.id);
          if (usersResponse.users && usersResponse.users.length > 0) {
            usersByTenant.push({
              tenant_id: tenant.id,
              tenant_name: tenant.name,
              users: usersResponse.users,
            });
          }
        } catch (error) {
          console.error(`Error fetching users for tenant ${tenant.id}:`, error);
        }
      }
      
      setAllUsers(usersByTenant);
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setLoading(false);
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

  const filteredUsers = allUsers.flatMap(tenantUser =>
    tenantUser.users
      .filter(user =>
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (user.full_name && user.full_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        tenantUser.tenant_name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .map(user => ({ ...user, tenant_id: tenantUser.tenant_id, tenant_name: tenantUser.tenant_name }))
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-sw-text">All Users</h2>
          <p className="text-sw-text-muted mt-1">Manage users across all tenants</p>
        </div>
      </div>

      {/* Search */}
      <div className="flex gap-4">
        <Input
          placeholder="Search users by email, name, or tenant..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-sw-surface border-sw-border text-sw-text"
        />
      </div>

      {/* Users List */}
      <Card className="bg-sw-bg-card border-sw-border">
        <CardHeader>
          <CardTitle className="text-sw-text-strong">
            Users ({filteredUsers.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading && allUsers.length === 0 ? (
            <div className="text-sw-text-muted text-center py-8">Loading...</div>
          ) : filteredUsers.length > 0 ? (
            <div className="space-y-3">
              {filteredUsers.map((user) => (
                <div
                  key={`${user.tenant_id}-${user.id}`}
                  className="p-4 bg-slate-800 rounded border-l-4 border-blue-500 hover:bg-slate-750 cursor-pointer transition-colors"
                  onClick={() => router.push(`/crm/tenants/${user.tenant_id}/users`)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-semibold text-lg">{user.full_name || user.email}</div>
                      <div className="text-sm text-slate-400 mt-1">{user.email}</div>
                      <div className="text-xs text-slate-500 mt-1">Tenant: {user.tenant_name}</div>
                      <div className="flex gap-2 mt-3">
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
                        {user.email_verified && (
                          <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                            Verified
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-slate-500 mt-2">
                        Last login: {user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "Never"}
                        {user.active_sessions_count > 0 && (
                          <span className="ml-2">• {user.active_sessions_count} active sessions</span>
                        )}
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
    </div>
  );
}

