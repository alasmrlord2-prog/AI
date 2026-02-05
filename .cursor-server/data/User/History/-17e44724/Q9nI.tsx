"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users, Building2, Search, Filter } from "lucide-react";

type Tenant = {
  id: string;
  name: string;
  status: string;
  user_count?: number;
};

type User = {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  status: string;
  tenant_id?: string;
  tenant_name?: string;
  last_login_at?: string;
};

export default function CRMUsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTenant, setSelectedTenant] = useState<string>("all");

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/crm/login");
      return;
    }
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [router]);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Fetch all tenants
      const tenantsResponse = await crmApi.listTenants(1000, 0);
      const tenantsList = tenantsResponse.tenants || [];
      setTenants(tenantsList);

      // Fetch users from all tenants
      const allUsers: User[] = [];
      for (const tenant of tenantsList) {
        try {
          const usersResponse = await crmApi.getTenantUsers(tenant.id);
          const tenantUsers = (usersResponse.users || []).map((user: any) => ({
            ...user,
            tenant_id: tenant.id,
            tenant_name: tenant.name,
          }));
          allUsers.push(...tenantUsers);
        } catch (error) {
          console.error(`Error fetching users for tenant ${tenant.id}:`, error);
        }
      }
      setUsers(allUsers);
    } catch (error: any) {
      console.error("Error fetching data:", error);
      if (error?.message?.includes("Not authenticated") || error?.message?.includes("401")) {
        localStorage.removeItem("auth_token");
        router.push("/crm/login");
      }
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (user.full_name && user.full_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (user.tenant_name && user.tenant_name.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesTenant = selectedTenant === "all" || user.tenant_id === selectedTenant;
    return matchesSearch && matchesTenant;
  });

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
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <Button
            variant="ghost"
            onClick={() => router.push("/crm")}
            className="text-slate-400 hover:text-slate-200 mb-2"
          >
            ← Back to CRM Dashboard
          </Button>
          <h2 className="text-2xl font-semibold text-sw-text">All Users</h2>
          <p className="text-sw-textLight mt-1">{filteredUsers.length} users found</p>
        </div>
      </div>

      {/* Filters */}
      <Card className="bg-sw-surface border-sw-border">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-sw-textLight" />
              <input
                type="text"
                placeholder="Search by email, name, or tenant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-sw-bg border border-sw-border rounded-lg text-sw-text placeholder-sw-textLight focus:outline-none focus:ring-2 focus:ring-sw-primary"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-sw-textLight" />
              <select
                value={selectedTenant}
                onChange={(e) => setSelectedTenant(e.target.value)}
                className="px-4 py-2 bg-sw-bg border border-sw-border rounded-lg text-sw-text focus:outline-none focus:ring-2 focus:ring-sw-primary"
              >
                <option value="all">All Tenants</option>
                {tenants.map((tenant) => (
                  <option key={tenant.id} value={tenant.id}>
                    {tenant.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      {loading ? (
        <div className="text-center py-12 text-sw-textLight">Loading users...</div>
      ) : filteredUsers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredUsers.map((user) => (
            <Card
              key={user.id}
              className="bg-sw-surface border-sw-border hover:shadow-lg transition cursor-pointer"
              onClick={() => {
                if (user.tenant_id) {
                  router.push(`/crm/tenants/${user.tenant_id}/users`);
                }
              }}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="font-semibold text-sw-text">
                      {user.full_name || user.email}
                    </div>
                    <div className="text-sm text-sw-textLight mt-1">{user.email}</div>
                    {user.tenant_name && (
                      <div className="flex items-center gap-1 mt-2 text-xs text-sw-textLight">
                        <Building2 className="w-3 h-3" />
                        {user.tenant_name}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(user.status)}`}>
                    {user.status}
                  </span>
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                    {user.role}
                  </span>
                </div>
                {user.last_login_at && (
                  <div className="text-xs text-sw-textLight mt-2">
                    Last login: {new Date(user.last_login_at).toLocaleDateString()}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-sw-surface border-sw-border">
          <CardContent className="p-12 text-center">
            <Users className="w-12 h-12 mx-auto mb-4 text-sw-textLight" />
            <p className="text-sw-textLight">
              {searchTerm || selectedTenant !== "all"
                ? "No users found matching your filters"
                : "No users found"}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

