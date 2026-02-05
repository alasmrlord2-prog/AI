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
      <div className="mt-6 bg-sw-surface p-6 rounded-xl border border-sw-border">
        {loading && tenants.length === 0 ? (
          <div className="text-sw-textLight text-center py-8">Loading...</div>
        ) : filteredTenants.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTenants.map((tenant) => (
              <div
                key={tenant.id}
                className="p-6 bg-white rounded-xl border border-sw-border hover:shadow-md transition cursor-pointer"
                onClick={() => router.push(`/crm/tenants/${tenant.id}`)}
              >
                <h3 className="text-lg font-bold text-sw-text">{tenant.name}</h3>
                <p className="text-sm text-sw-textLight mt-1 capitalize">{tenant.type}</p>
                <div className="flex gap-4 mt-3 text-sm">
                  <span className="text-sw-textLight">
                    Plan: <span className="text-sw-primary font-medium">{tenant.plan_name || "No Plan"}</span>
                  </span>
                  <span className="text-sw-textLight">
                    Users: <span className="text-sw-accent font-medium">{tenant.user_count}</span>
                  </span>
                </div>
                <span className="mt-3 inline-block px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm">
                  {tenant.status === "active" ? "Active" : tenant.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sw-textLight text-center py-8">No tenants found</div>
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

