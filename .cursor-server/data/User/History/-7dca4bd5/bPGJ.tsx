"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

type TenantDashboard = {
  tenant: {
    id: string;
    name: string;
    type: string;
    status: string;
    contact_email?: string;
    contact_phone?: string;
    created_at?: string;
  };
  subscription: {
    id?: string;
    plan_name?: string;
    status: string;
    is_active: boolean;
    is_expired: boolean;
    is_in_grace: boolean;
    days_until_expiry?: number;
    start_at?: string;
    end_at?: string;
  };
  users: Array<{
    id: string;
    email: string;
    full_name?: string;
    role: string;
    status: string;
    last_login_at?: string;
  }>;
  usage: Record<string, any>;
  limits: Record<string, any>;
  recent_activity: Array<{
    action: string;
    user_id?: string;
    created_at?: string;
  }>;
};

export default function TenantDashboardPage() {
  const params = useParams();
  const router = useRouter();
  const tenantId = params.tenantId as string;
  const [activeTab, setActiveTab] = useState("overview");
  const [dashboard, setDashboard] = useState<TenantDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 30000);
    return () => clearInterval(interval);
  }, [tenantId]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const data = await crmApi.getTenantDashboard(tenantId);
      setDashboard(data);
    } catch (error) {
      console.error("Error fetching dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !dashboard) {
    return (
      <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-slate-400">Loading...</div>
          </div>
        </div>
      </main>
    );
  }

  if (!dashboard) {
    return (
      <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-slate-400">Tenant not found</div>
          </div>
        </div>
      </main>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "users", label: "Users" },
    { id: "subscription", label: "Subscription" },
    { id: "usage", label: "Usage Analytics" },
    { id: "audit", label: "Audit Logs" },
    { id: "incidents", label: "Incidents" },
  ];

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Header */}
          <div className="flex justify-between items-center">
            <div>
              <Button
                variant="ghost"
                onClick={() => router.push("/crm/tenants")}
                className="text-slate-400 hover:text-slate-200 mb-2"
              >
                ← Back to Tenants
              </Button>
              <h1 className="text-2xl md:text-3xl font-bold">{dashboard.tenant.name}</h1>
              <p className="text-slate-400 mt-1">{dashboard.tenant.type} • {dashboard.tenant.contact_email}</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-slate-800 overflow-x-auto scrollbar-thin pb-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Subscription Status */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Subscription Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <div className="text-slate-400 text-sm">Plan</div>
                      <div className="text-lg font-semibold text-blue-400">
                        {dashboard.subscription.plan_name || "No Plan"}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-400 text-sm">Status</div>
                      <div className={`text-lg font-semibold ${
                        dashboard.subscription.is_active ? "text-green-400" : "text-red-400"
                      }`}>
                        {dashboard.subscription.status}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-400 text-sm">Days Until Expiry</div>
                      <div className="text-lg font-semibold text-orange-400">
                        {dashboard.subscription.days_until_expiry ?? "N/A"}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Users Summary */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Users ({dashboard.users.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboard.users.slice(0, 5).map((user) => (
                      <div key={user.id} className="flex justify-between items-center p-2 bg-slate-800 rounded">
                        <div>
                          <div className="font-medium">{user.full_name || user.email}</div>
                          <div className="text-sm text-slate-400">{user.email}</div>
                        </div>
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                          {user.role}
                        </span>
                      </div>
                    ))}
                    {dashboard.users.length > 5 && (
                      <Button
                        variant="ghost"
                        onClick={() => setActiveTab("users")}
                        className="w-full text-slate-400 hover:text-slate-200"
                      >
                        View all {dashboard.users.length} users →
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboard.recent_activity.slice(0, 10).map((activity, idx) => (
                      <div key={idx} className="flex justify-between items-center p-2 bg-slate-800 rounded text-sm">
                        <span className="text-slate-300">{activity.action}</span>
                        <span className="text-slate-500 text-xs">
                          {activity.created_at ? new Date(activity.created_at).toLocaleString() : ""}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === "users" && (
            <div>
              <Button
                onClick={() => router.push(`/crm/tenants/${tenantId}/users`)}
                className="mb-4 bg-blue-600 hover:bg-blue-700"
              >
                View All Users →
              </Button>
            </div>
          )}

          {activeTab === "subscription" && (
            <div>
              <Button
                onClick={() => router.push(`/crm/tenants/${tenantId}/subscription`)}
                className="mb-4 bg-blue-600 hover:bg-blue-700"
              >
                Manage Subscription →
              </Button>
            </div>
          )}

          {activeTab === "usage" && (
            <div>
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Usage Analytics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(dashboard.usage).map(([key, value]) => (
                      <div key={key} className="p-4 bg-slate-800 rounded">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-300 capitalize">{key.replace(/_/g, " ")}</span>
                          <span className="text-blue-400 font-semibold">{value as number}</span>
                        </div>
                        {dashboard.limits[key] && (
                          <div className="mt-2">
                            <div className="w-full bg-slate-700 rounded-full h-2">
                              <div
                                className="bg-blue-500 h-2 rounded-full"
                                style={{
                                  width: `${Math.min(100, ((value as number) / dashboard.limits[key]) * 100)}%`,
                                }}
                              />
                            </div>
                            <div className="text-xs text-slate-500 mt-1">
                              {value as number} / {dashboard.limits[key]}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === "audit" && (
            <div>
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Audit Logs</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-400">Full audit logs view coming soon...</p>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === "incidents" && (
            <div>
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Incidents</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-400">Incidents view coming soon...</p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

