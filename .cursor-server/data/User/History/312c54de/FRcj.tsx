"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type TenantAnalytics = {
  tenant_id: string;
  tenant_name: string;
  usage: Record<string, number>;
  limits: Record<string, number>;
  usage_history?: Record<string, Array<{ date: string; value: number }>>;
};

export default function AnalyticsPage() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState<TenantAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDays, setSelectedDays] = useState(30);

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      // Get all tenants first
      const tenantsResponse = await crmApi.listTenants(1000, 0);
      const tenants = tenantsResponse.tenants || [];
      
      // Get usage analytics for each tenant
      const analyticsData: TenantAnalytics[] = [];
      for (const tenant of tenants) {
        try {
          const usageData = await crmApi.getTenantUsage(tenant.id, selectedDays);
          if (usageData && usageData.current_usage) {
            analyticsData.push({
              tenant_id: tenant.id,
              tenant_name: tenant.name,
              usage: usageData.current_usage || {},
              limits: usageData.limits || {},
              usage_history: usageData.usage_history || {},
            });
          }
        } catch (error) {
          console.error(`Error fetching analytics for tenant ${tenant.id}:`, error);
        }
      }
      
      setAnalytics(analyticsData);
    } catch (error) {
      console.error("Error fetching analytics:", error);
    } finally {
      setLoading(false);
    }
  }, [selectedDays]);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 60000);
    return () => clearInterval(interval);
  }, [fetchAnalytics]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-sw-text">Analytics</h2>
          <p className="text-sw-text-muted mt-1">Usage analytics across all tenants</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={selectedDays === 7 ? "default" : "outline"}
            onClick={() => setSelectedDays(7)}
            className="border-sw-border"
          >
            7 Days
          </Button>
          <Button
            variant={selectedDays === 30 ? "default" : "outline"}
            onClick={() => setSelectedDays(30)}
            className="border-sw-border"
          >
            30 Days
          </Button>
          <Button
            variant={selectedDays === 90 ? "default" : "outline"}
            onClick={() => setSelectedDays(90)}
            className="border-sw-border"
          >
            90 Days
          </Button>
        </div>
      </div>

      {/* Analytics Cards */}
      {loading ? (
        <div className="text-sw-text-muted text-center py-8">Loading analytics...</div>
      ) : analytics.length > 0 ? (
        <div className="space-y-6">
          {analytics.map((tenantAnalytics) => (
            <Card
              key={tenantAnalytics.tenant_id}
              className="bg-sw-bg-card border-sw-border"
            >
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle className="text-sw-text-strong">
                    {tenantAnalytics.tenant_name}
                  </CardTitle>
                  <Button
                    variant="ghost"
                    onClick={() => router.push(`/crm/tenants/${tenantAnalytics.tenant_id}`)}
                    className="text-sw-text-muted hover:text-sw-text"
                  >
                    View Details →
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(tenantAnalytics.usage).map(([key, value]) => {
                    const limit = tenantAnalytics.limits[key];
                    const percentage = limit ? (value / limit) * 100 : 0;
                    return (
                      <div key={key} className="p-4 bg-slate-800 rounded">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-slate-300 capitalize font-medium">
                            {key.replace(/_/g, " ")}
                          </span>
                          <span className="text-blue-400 font-semibold">
                            {value.toLocaleString()} {limit ? `/ ${limit.toLocaleString()}` : ""}
                          </span>
                        </div>
                        {limit && (
                          <>
                            <div className="w-full bg-slate-700 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full transition-all ${
                                  percentage > 90 ? "bg-red-500" :
                                  percentage > 75 ? "bg-orange-500" :
                                  "bg-blue-500"
                                }`}
                                style={{ width: `${Math.min(100, percentage)}%` }}
                              />
                            </div>
                            <div className="text-xs text-slate-400 mt-1">
                              {Math.round(percentage)}% used
                            </div>
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-sw-bg-card border-sw-border">
          <CardContent>
            <div className="text-slate-500 text-center py-8">No analytics data available</div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

