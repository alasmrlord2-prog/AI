"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Tenant = {
  id: string;
  name: string;
  type: string;
  status: string;
  subscription_status: string;
  plan_name?: string;
  user_count: number;
  days_until_expiry?: number;
  created_at: string;
};

export default function TenantsPage() {
  const router = useRouter();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  useEffect(() => {
    fetchTenants();
    const interval = setInterval(fetchTenants, 30000);
    return () => clearInterval(interval);
  }, [offset]);

  const fetchTenants = async () => {
    try {
      setLoading(true);
      const response = await crmApi.listTenants(limit, offset);
      setTenants(response.tenants || []);
      setTotal(response.total || 0);
    } catch (error) {
      console.error("Error fetching tenants:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTenants = tenants.filter((tenant) =>
    tenant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tenant.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-sw-success/20 text-sw-success";
      case "suspended":
        return "bg-sw-warning/20 text-sw-warning";
      case "trial":
        return "bg-sw-blue/20 text-sw-blue";
      case "cancelled":
        return "bg-sw-danger/20 text-sw-danger";
      default:
        return "bg-sw-bg-soft text-sw-text-muted";
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-sw-text-strong">Tenants</h1>
          <p className="text-sw-text-muted mt-1">Manage customers and organizations</p>
        </div>
        <Button
          onClick={() => router.push("/crm/tenants/new")}
          className="bg-sw-blue hover:bg-sw-blue-light text-white"
        >
          + New Tenant
        </Button>
      </div>

      {/* Search */}
      <div className="flex gap-4">
        <Input
          placeholder="Search tenants..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-sw-bg-soft border-sw-border text-sw-text"
        />
      </div>

      {/* Tenants List */}
      <Card className="bg-sw-bg-card border-sw-border">
        <CardHeader>
          <CardTitle className="text-sw-text-strong">Tenants ({total})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading && tenants.length === 0 ? (
            <div className="text-sw-text-muted text-center py-8">Loading...</div>
          ) : filteredTenants.length > 0 ? (
            <div className="space-y-3">
              {filteredTenants.map((tenant) => (
                <div
                  key={tenant.id}
                  className="p-4 bg-sw-bg-soft rounded-lg border-l-4 border-sw-blue hover:bg-sw-bg-hover cursor-pointer transition-all"
                  onClick={() => router.push(`/crm/tenants/${tenant.id}`)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-semibold text-lg text-sw-text-strong">{tenant.name}</div>
                      <div className="text-sm text-sw-text-muted mt-1 capitalize">{tenant.type}</div>
                      <div className="flex gap-4 mt-3 text-sm">
                        <span className="text-sw-text-muted">
                          Plan: <span className="text-sw-blue font-medium">{tenant.plan_name || "No Plan"}</span>
                        </span>
                        <span className="text-sw-text-muted">
                          Users: <span className="text-sw-teal font-medium">{tenant.user_count}</span>
                        </span>
                        {tenant.days_until_expiry !== null && tenant.days_until_expiry !== undefined && (
                          <span className="text-sw-text-muted">
                            Expires: <span className="text-sw-warning font-medium">{tenant.days_until_expiry} days</span>
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <span className={`px-3 py-1 rounded-lg text-xs font-medium ${getStatusColor(tenant.status)}`}>
                        {tenant.status}
                      </span>
                      <span className={`px-3 py-1 rounded-lg text-xs font-medium ${getStatusColor(tenant.subscription_status)}`}>
                        {tenant.subscription_status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sw-text-muted text-center py-8">No tenants found</div>
          )}

          {/* Pagination */}
          {total > limit && (
            <div className="flex justify-between items-center mt-6 pt-4 border-t border-sw-border">
              <Button
                variant="outline"
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
                className="border-sw-border text-sw-text hover:bg-sw-bg-hover"
              >
                Previous
              </Button>
              <span className="text-sw-text-muted text-sm">
                Showing {offset + 1} - {Math.min(offset + limit, total)} of {total}
              </span>
              <Button
                variant="outline"
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= total}
                className="border-sw-border text-sw-text hover:bg-sw-bg-hover"
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

