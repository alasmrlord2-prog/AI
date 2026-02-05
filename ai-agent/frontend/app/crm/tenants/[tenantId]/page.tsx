"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type Incident = {
  id: string;
  title: string;
  severity: string;
  status: string;
  created_at?: string;
};

// Incidents Tab Component
function IncidentsTab({ tenantId }: { tenantId: string }) {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const data = await crmApi.getTenantIncidents(tenantId);
        setIncidents(data.incidents || []);
      } catch (error) {
        console.error("Error fetching incidents:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchIncidents();
  }, [tenantId]);

  if (loading) {
    return <div className="text-sw-text-muted text-center py-8">Loading incidents...</div>;
  }

  if (incidents.length === 0) {
    return <div className="text-sw-text-muted text-center py-8">No incidents found</div>;
  }

  return (
    <div className="space-y-2 max-h-96 overflow-y-auto">
      {incidents.map((incident) => (
        <div key={incident.id} className="p-3 bg-sw-bg-soft rounded-lg border-l-4 border-sw-danger">
          <div className="flex justify-between items-start">
            <div>
              <div className="font-medium text-sw-text-strong">{incident.title}</div>
              <div className="text-xs text-sw-text-muted mt-1">
                Severity: <span className="text-sw-danger">{incident.severity}</span>
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              <span className={`px-2 py-1 rounded-lg text-xs ${
                incident.status === "resolved" ? "bg-sw-success/20 text-sw-success" :
                incident.status === "open" ? "bg-sw-danger/20 text-sw-danger" :
                "bg-sw-warning/20 text-sw-warning"
              }`}>
                {incident.status}
              </span>
              <div className="text-xs text-sw-text-muted">
                {incident.created_at ? new Date(incident.created_at).toLocaleString() : ""}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

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
  usage: Record<string, number>;
  limits: Record<string, number>;
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

  const fetchDashboard = useCallback(async () => {
    // Don't fetch if tenantId is "new" or invalid
    if (!tenantId || tenantId === "new" || tenantId === "undefined") {
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      const data = await crmApi.getTenantDashboard(tenantId);
      setDashboard(data);
    } catch (error) {
      console.error("Error fetching dashboard:", error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      // If tenant not found, show error message
      if (errorMessage.includes("404") || errorMessage.includes("not found")) {
        setDashboard(null);
      }
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboard]);

  if (loading && !dashboard) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-sw-text-muted">Loading...</div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-sw-text-muted">Tenant not found</div>
      </div>
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
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <Button
            variant="ghost"
            onClick={() => router.push("/crm/tenants")}
            className="text-sw-text-muted hover:text-sw-text mb-2"
          >
            ← Back to Tenants
          </Button>
          <h1 className="text-2xl md:text-3xl font-bold text-sw-text-strong">{dashboard.tenant.name}</h1>
          <p className="text-sw-text-muted mt-1">{dashboard.tenant.type} • {dashboard.tenant.contact_email}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-sw-border overflow-x-auto scrollbar-thin pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? "border-sw-blue text-sw-blue font-medium"
                : "border-transparent text-sw-text-muted hover:text-sw-text"
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
          <Card className="bg-sw-bg-card border-sw-border">
            <CardHeader>
              <CardTitle className="text-sw-text-strong">Subscription Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-sw-text-muted text-sm">Plan</div>
                  <div className="text-lg font-semibold text-sw-blue">
                    {dashboard.subscription.plan_name || "No Plan"}
                  </div>
                </div>
                <div>
                  <div className="text-sw-text-muted text-sm">Status</div>
                  <div className={`text-lg font-semibold ${
                    dashboard.subscription.is_active ? "text-sw-success" : "text-sw-danger"
                  }`}>
                    {dashboard.subscription.status}
                  </div>
                </div>
                <div>
                  <div className="text-sw-text-muted text-sm">Days Until Expiry</div>
                  <div className="text-lg font-semibold text-sw-warning">
                    {dashboard.subscription.days_until_expiry ?? "N/A"}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Users Summary */}
          <Card className="bg-sw-bg-card border-sw-border">
            <CardHeader>
              <CardTitle className="text-sw-text-strong">Users ({dashboard.users.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {dashboard.users.slice(0, 5).map((user) => (
                  <div key={user.id} className="flex justify-between items-center p-3 bg-sw-bg-soft rounded-lg">
                    <div>
                      <div className="font-medium text-sw-text-strong">{user.full_name || user.email}</div>
                      <div className="text-sm text-sw-text-muted">{user.email}</div>
                    </div>
                    <span className="px-2 py-1 bg-sw-blue/20 text-sw-blue text-xs rounded-lg">
                      {user.role}
                    </span>
                  </div>
                ))}
                {dashboard.users.length > 5 && (
                  <Button
                    variant="ghost"
                    onClick={() => setActiveTab("users")}
                    className="w-full text-sw-text-muted hover:text-sw-text"
                  >
                    View all {dashboard.users.length} users →
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="bg-sw-bg-card border-sw-border">
            <CardHeader>
              <CardTitle className="text-sw-text-strong">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {dashboard.recent_activity.slice(0, 10).map((activity, idx) => (
                  <div key={idx} className="flex justify-between items-center p-3 bg-sw-bg-soft rounded-lg text-sm">
                    <span className="text-sw-text">{activity.action}</span>
                    <span className="text-sw-text-muted text-xs">
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
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-sw-text-strong">Users Management</h2>
            <Button
              onClick={() => router.push(`/crm/tenants/${tenantId}/users`)}
              className="bg-sw-blue hover:bg-sw-blue-light text-white"
            >
              View All Users →
            </Button>
          </div>
          <Card className="bg-sw-bg-card border-sw-border">
            <CardHeader>
              <CardTitle className="text-sw-text-strong">Users ({dashboard.users.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {dashboard.users.slice(0, 10).map((user) => (
                  <div key={user.id} className="flex justify-between items-center p-3 bg-sw-bg-soft rounded-lg">
                    <div>
                      <div className="font-medium text-sw-text-strong">{user.full_name || user.email}</div>
                      <div className="text-sm text-sw-text-muted">{user.email}</div>
                    </div>
                    <div className="flex gap-2">
                      <span className="px-2 py-1 bg-sw-blue/20 text-sw-blue text-xs rounded-lg">
                        {user.role}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded-lg ${
                        user.status === "active" ? "bg-sw-success/20 text-sw-success" : "bg-sw-danger/20 text-sw-danger"
                      }`}>
                        {user.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === "subscription" && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-sw-text-strong">Subscription Management</h2>
            <Button
              onClick={() => router.push(`/crm/tenants/${tenantId}/subscription`)}
              className="bg-sw-blue hover:bg-sw-blue-light text-white"
            >
              Manage Subscription →
            </Button>
          </div>
          <Card className="bg-sw-bg-card border-sw-border">
            <CardHeader>
              <CardTitle className="text-sw-text-strong">Current Subscription</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-sw-text-muted text-sm">Plan</div>
                  <div className="text-lg font-semibold text-sw-blue">
                    {dashboard.subscription.plan_name || "No Plan"}
                  </div>
                </div>
                <div>
                  <div className="text-sw-text-muted text-sm">Status</div>
                  <div className={`text-lg font-semibold ${
                    dashboard.subscription.is_active ? "text-sw-success" : "text-sw-danger"
                  }`}>
                    {dashboard.subscription.status}
                  </div>
                </div>
                <div>
                  <div className="text-sw-text-muted text-sm">Days Until Expiry</div>
                  <div className="text-lg font-semibold text-sw-warning">
                    {dashboard.subscription.days_until_expiry ?? "N/A"}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === "usage" && (
        <div className="space-y-6">
          <Card className="bg-sw-bg-card border-sw-border">
            <CardHeader>
              <CardTitle className="text-sw-text-strong">Usage Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              {Object.keys(dashboard.usage).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(dashboard.usage).map(([key, value]) => (
                    <div key={key} className="p-4 bg-sw-bg-soft rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sw-text capitalize font-medium">
                          {key.replace(/_/g, " ")}
                        </span>
                        <span className="text-sw-blue font-semibold">
                          {value as number} {dashboard.limits[key] ? `/ ${dashboard.limits[key]}` : ""}
                        </span>
                      </div>
                      {dashboard.limits[key] && (
                        <div className="mt-2">
                          <div className="w-full bg-sw-bg-hover rounded-full h-3">
                            <div
                              className={`h-3 rounded-full transition-all ${
                                ((value as number) / dashboard.limits[key]) * 100 > 90 ? "bg-sw-danger" :
                                ((value as number) / dashboard.limits[key]) * 100 > 75 ? "bg-sw-warning" :
                                "bg-sw-blue"
                              }`}
                              style={{
                                width: `${Math.min(100, ((value as number) / dashboard.limits[key]) * 100)}%`,
                              }}
                            />
                          </div>
                          <div className="text-xs text-sw-text-muted mt-1">
                            {Math.round(((value as number) / dashboard.limits[key]) * 100)}% used
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sw-text-muted text-center py-8">No usage data available</div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === "audit" && (
        <div className="space-y-6">
          <Card className="bg-sw-bg-card border-sw-border">
            <CardHeader>
              <CardTitle className="text-sw-text-strong">Audit Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {dashboard.recent_activity.length > 0 ? (
                  dashboard.recent_activity.map((activity, idx) => (
                    <div key={idx} className="p-3 bg-sw-bg-soft rounded-lg">
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-medium text-sw-text-strong">{activity.action}</div>
                          {activity.user_id && (
                            <div className="text-xs text-sw-text-muted mt-1">User: {activity.user_id}</div>
                          )}
                        </div>
                        <div className="text-xs text-sw-text-muted">
                          {activity.created_at ? new Date(activity.created_at).toLocaleString() : ""}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-sw-text-muted text-center py-8">No audit logs available</div>
                )}
              </div>
              <div className="mt-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    // TODO: Navigate to full audit logs page
                    alert("Full audit logs page coming soon");
                  }}
                  className="w-full border-sw-border text-sw-text hover:bg-sw-bg-hover"
                >
                  View All Audit Logs →
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === "incidents" && (
        <div className="space-y-6">
          <Card className="bg-sw-bg-card border-sw-border">
            <CardHeader>
              <CardTitle className="text-sw-text-strong">Incidents</CardTitle>
            </CardHeader>
            <CardContent>
              <IncidentsTab tenantId={tenantId} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

