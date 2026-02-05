"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

                process.env.NEXT_PUBLIC_BACKEND_URL || 
                "http://ai-agent.bankid-sy.com/api";

type Tenant = {
  id: string;
  name: string;
  domain: string;
  status: "active" | "suspended" | "inactive";
  plan: string;
  created_at: string;
  users_count: number;
  resources: {
    storage_gb: number;
    api_calls: number;
    max_users: number;
  };
  limits: {
    max_storage_gb: number;
    max_api_calls: number;
    max_users: number;
  };
};

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTenant, setNewTenant] = useState({
    name: "",
    domain: "",
    plan: "basic",
  });

  useEffect(() => {
    loadTenants();
  }, []);

  const getAuthToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  };

  const loadTenants = async () => {
    try {
      const token = getAuthToken();
      const res = await fetch(`${getApiUrl()}/api/tenants`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setTenants(data.tenants || []);
      }
    } catch (err) {
      console.error("Failed to load tenants:", err);
    }
  };

  const handleAddTenant = async () => {
    if (!newTenant.name || !newTenant.domain) return;
    setLoading(true);
    try {
      const token = getAuthToken();
      const res = await fetch(`${getApiUrl()}/api/tenants`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newTenant),
      });
      if (res.ok) {
        await loadTenants();
        setNewTenant({ name: "", domain: "", plan: "basic" });
        setShowAddModal(false);
        alert("Tenant created successfully!");
      }
    } catch (err) {
      console.error("Failed to create tenant:", err);
      alert("Failed to create tenant");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (tenantId: string, status: string) => {
    try {
      const token = getAuthToken();
      const res = await fetch(`${getApiUrl()}/api/tenants/${tenantId}/status`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status }),
      });
      if (res.ok) {
        await loadTenants();
      }
    } catch (err) {
      console.error("Failed to update status:", err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-500";
      case "suspended": return "bg-yellow-500";
      case "inactive": return "bg-red-500";
      default: return "bg-slate-500";
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case "enterprise": return "text-purple-400";
      case "professional": return "text-blue-400";
      case "basic": return "text-green-400";
      default: return "text-slate-400";
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 scrollbar-thin">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-500 bg-clip-text text-transparent">
                🏢 Multi-Tenancy Management
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Manage multiple tenants and their resources
              </p>
            </div>
            <Button
              onClick={() => setShowAddModal(true)}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              + Add Tenant
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card className="bg-gradient-to-br from-blue-900/30 to-blue-800/30 border-blue-700">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-400">{tenants.length}</div>
                <div className="text-xs text-slate-400">Total Tenants</div>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-green-900/30 to-green-800/30 border-green-700">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-400">
                  {tenants.filter(t => t.status === "active").length}
                </div>
                <div className="text-xs text-slate-400">Active</div>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/30 border-yellow-700">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-yellow-400">
                  {tenants.filter(t => t.status === "suspended").length}
                </div>
                <div className="text-xs text-slate-400">Suspended</div>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-purple-900/30 to-purple-800/30 border-purple-700">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-purple-400">
                  {tenants.reduce((sum, t) => sum + t.users_count, 0)}
                </div>
                <div className="text-xs text-slate-400">Total Users</div>
              </CardContent>
            </Card>
          </div>

          {/* Tenants List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {tenants.map((tenant) => (
              <Card
                key={tenant.id}
                className={`bg-slate-900 border-slate-800 cursor-pointer hover:border-cyan-500 transition-all ${
                  selectedTenant?.id === tenant.id ? "border-cyan-500" : ""
                }`}
                onClick={() => setSelectedTenant(tenant)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-cyan-400">{tenant.name}</CardTitle>
                      <div className="text-sm text-slate-400 mt-1">{tenant.domain}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={`h-3 w-3 rounded-full ${getStatusColor(tenant.status)}`}></div>
                      <span className="text-xs text-slate-400 capitalize">{tenant.status}</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="text-xs text-slate-400 mb-1">Plan</div>
                      <div className={`font-bold ${getPlanColor(tenant.plan)}`}>
                        {tenant.plan.toUpperCase()}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <div className="text-slate-400">Users</div>
                        <div className="text-slate-300">
                          {tenant.users_count} / {tenant.limits.max_users}
                        </div>
                      </div>
                      <div>
                        <div className="text-slate-400">Storage</div>
                        <div className="text-slate-300">
                          {tenant.resources.storage_gb} / {tenant.limits.max_storage_gb} GB
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-slate-400">
                      Created: {new Date(tenant.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Tenant Details Modal */}
          {selectedTenant && (
            <Card className="bg-slate-900 border-slate-800 mt-6">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Tenant Details: {selectedTenant.name}</CardTitle>
                  <Button
                    onClick={() => setSelectedTenant(null)}
                    className="bg-slate-700 hover:bg-slate-600"
                  >
                    Close
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <div className="text-xs text-slate-400 mb-1">Domain</div>
                      <div className="text-slate-300">{selectedTenant.domain}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-400 mb-1">Status</div>
                      <div className="flex items-center gap-2">
                        <select
                          value={selectedTenant.status}
                          onChange={(e) => handleUpdateStatus(selectedTenant.id, e.target.value)}
                          className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-slate-200"
                        >
                          <option value="active">Active</option>
                          <option value="suspended">Suspended</option>
                          <option value="inactive">Inactive</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-400 mb-1">Plan</div>
                      <div className={`font-bold ${getPlanColor(selectedTenant.plan)}`}>
                        {selectedTenant.plan.toUpperCase()}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <div className="text-xs text-slate-400 mb-2">Resource Usage</div>
                      <div className="space-y-2">
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span>Users</span>
                            <span>
                              {selectedTenant.users_count} / {selectedTenant.limits.max_users}
                            </span>
                          </div>
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{
                                width: `${(selectedTenant.users_count / selectedTenant.limits.max_users) * 100}%`,
                              }}
                            ></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span>Storage</span>
                            <span>
                              {selectedTenant.resources.storage_gb} / {selectedTenant.limits.max_storage_gb} GB
                            </span>
                          </div>
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <div
                              className="bg-green-500 h-2 rounded-full"
                              style={{
                                width: `${(selectedTenant.resources.storage_gb / selectedTenant.limits.max_storage_gb) * 100}%`,
                              }}
                            ></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span>API Calls</span>
                            <span>
                              {selectedTenant.resources.api_calls} / {selectedTenant.limits.max_api_calls}
                            </span>
                          </div>
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <div
                              className="bg-purple-500 h-2 rounded-full"
                              style={{
                                width: `${(selectedTenant.resources.api_calls / selectedTenant.limits.max_api_calls) * 100}%`,
                              }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Add Tenant Modal */}
          {showAddModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <Card className="bg-slate-900 border-slate-800 w-full max-w-md">
                <CardHeader>
                  <CardTitle>Add New Tenant</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-slate-300 mb-2 block">Tenant Name</label>
                      <Input
                        value={newTenant.name}
                        onChange={(e) => setNewTenant({ ...newTenant, name: e.target.value })}
                        placeholder="Company Name"
                        className="bg-slate-800 border-slate-700"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-300 mb-2 block">Domain</label>
                      <Input
                        value={newTenant.domain}
                        onChange={(e) => setNewTenant({ ...newTenant, domain: e.target.value })}
                        placeholder="tenant.example.com"
                        className="bg-slate-800 border-slate-700"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-300 mb-2 block">Plan</label>
                      <select
                        value={newTenant.plan}
                        onChange={(e) => setNewTenant({ ...newTenant, plan: e.target.value })}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200"
                      >
                        <option value="basic">Basic</option>
                        <option value="professional">Professional</option>
                        <option value="enterprise">Enterprise</option>
                      </select>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleAddTenant}
                        disabled={loading}
                        className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                      >
                        {loading ? "Creating..." : "Create Tenant"}
                      </Button>
                      <Button
                        onClick={() => setShowAddModal(false)}
                        className="flex-1 bg-slate-700 hover:bg-slate-600"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

