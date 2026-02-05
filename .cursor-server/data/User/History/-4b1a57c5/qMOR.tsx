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
          <h2 className="text-2xl font-semibold text-sw-text">Tenants</h2>
        </div>
        <Button
          onClick={() => router.push("/crm/tenants/new")}
          className="bg-sw-primary hover:bg-sw-primaryDark text-white"
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
          className="bg-sw-surface border-sw-border text-sw-text"
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
                  className="p-4 bg-slate-800 rounded border-l-4 border-blue-500 hover:bg-slate-750 cursor-pointer transition-colors"
                  onClick={() => router.push(`/crm/tenants/${tenant.id}`)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-semibold text-lg">{tenant.name}</div>
                      <div className="text-sm text-slate-400 mt-1 capitalize">{tenant.type}</div>
                      <div className="flex gap-4 mt-3 text-sm">
                        <span>
                          Plan: <span className="text-blue-400">{tenant.plan_name || "No Plan"}</span>
                        </span>
                        <span>
                          Users: <span className="text-purple-400">{tenant.user_count}</span>
                        </span>
                        {tenant.days_until_expiry !== null && tenant.days_until_expiry !== undefined && (
                          <span>
                            Expires: <span className="text-orange-400">{tenant.days_until_expiry} days</span>
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <span className={`px-3 py-1 rounded text-xs font-medium ${getStatusColor(tenant.status)}`}>
                        {tenant.status}
                      </span>
                      <span className={`px-3 py-1 rounded text-xs font-medium ${getStatusColor(tenant.subscription_status)}`}>
                        {tenant.subscription_status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-500 text-center py-8">No tenants found</div>
          )}

          {/* Pagination */}
          {total > limit && (
            <div className="flex justify-between items-center mt-6 pt-4 border-t border-slate-800">
              <Button
                variant="outline"
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
                className="border-slate-700 text-slate-300"
              >
                Previous
              </Button>
              <span className="text-slate-400 text-sm">
                Showing {offset + 1} - {Math.min(offset + limit, total)} of {total}
              </span>
              <Button
                variant="outline"
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= total}
                className="border-slate-700 text-slate-300"
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

