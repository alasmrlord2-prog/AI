"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { subscriptionApi, crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type Plan = {
  id: string;
  name: string;
  description?: string;
  price_monthly?: number;
  price_yearly?: number;
  max_users?: number;
  max_requests?: number;
  max_tokens?: number;
  max_storage_gb?: number;
  max_workflow_runs?: number;
  max_agents?: number;
  max_log_volume_gb?: number;
  features_json?: Record<string, boolean>;
};

type TenantSubscription = {
  tenant_id: string;
  tenant_name: string;
  subscription_status: string;
  plan_name?: string;
  days_until_expiry?: number;
  is_active: boolean;
};

export default function SubscriptionsPage() {
  const router = useRouter();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [tenantSubscriptions, setTenantSubscriptions] = useState<TenantSubscription[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [plansData, tenantsResponse] = await Promise.all([
        subscriptionApi.getPlans(),
        crmApi.listTenants(1000, 0),
      ]);
      
      setPlans(plansData || []);
      
      const subscriptions: TenantSubscription[] = (tenantsResponse.tenants || []).map((tenant: any) => ({
        tenant_id: tenant.id,
        tenant_name: tenant.name,
        subscription_status: tenant.subscription_status,
        plan_name: tenant.plan_name,
        days_until_expiry: tenant.days_until_expiry,
        is_active: tenant.subscription_status === "active",
      }));
      
      setTenantSubscriptions(subscriptions);
    } catch (error) {
      console.error("Error fetching subscription data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500/20 text-green-400";
      case "expired":
        return "bg-red-500/20 text-red-400";
      case "trial":
        return "bg-blue-500/20 text-blue-400";
      case "cancelled":
        return "bg-slate-500/20 text-slate-400";
      default:
        return "bg-yellow-500/20 text-yellow-400";
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-sw-text">Subscription Plans</h2>
          <p className="text-sw-text-muted mt-1">Manage subscription plans and tenant subscriptions</p>
        </div>
      </div>

      {/* Available Plans */}
      <Card className="bg-sw-bg-card border-sw-border">
        <CardHeader>
          <CardTitle className="text-sw-text-strong">Available Plans</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-sw-text-muted text-center py-8">Loading...</div>
          ) : plans.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  className="p-4 bg-slate-800 rounded border-2 border-slate-700 hover:border-blue-500 transition-colors"
                >
                  <div className="font-semibold text-lg text-sw-text">{plan.name}</div>
                  {plan.description && (
                    <div className="text-sm text-slate-400 mt-1">{plan.description}</div>
                  )}
                  <div className="mt-3 space-y-1 text-sm">
                    {plan.price_monthly && (
                      <div className="text-slate-300">
                        ${plan.price_monthly}/month
                      </div>
                    )}
                    {plan.max_users && (
                      <div className="text-slate-400">Max Users: {plan.max_users}</div>
                    )}
                    {plan.max_requests && (
                      <div className="text-slate-400">
                        Max Requests: {plan.max_requests.toLocaleString()}
                      </div>
                    )}
                    {plan.max_tokens && (
                      <div className="text-slate-400">
                        Max Tokens: {plan.max_tokens.toLocaleString()}
                      </div>
                    )}
                    {plan.max_storage_gb && (
                      <div className="text-slate-400">Max Storage: {plan.max_storage_gb} GB</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-500 text-center py-8">No plans found</div>
          )}
        </CardContent>
      </Card>

      {/* Tenant Subscriptions */}
      <Card className="bg-sw-bg-card border-sw-border">
        <CardHeader>
          <CardTitle className="text-sw-text-strong">
            Tenant Subscriptions ({tenantSubscriptions.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-sw-text-muted text-center py-8">Loading...</div>
          ) : tenantSubscriptions.length > 0 ? (
            <div className="space-y-3">
              {tenantSubscriptions.map((sub) => (
                <div
                  key={sub.tenant_id}
                  className="p-4 bg-slate-800 rounded border-l-4 border-blue-500 hover:bg-slate-750 cursor-pointer transition-colors"
                  onClick={() => router.push(`/crm/tenants/${sub.tenant_id}/subscription`)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-semibold text-lg">{sub.tenant_name}</div>
                      <div className="text-sm text-slate-400 mt-1">
                        Plan: {sub.plan_name || "No Plan"}
                      </div>
                      {sub.days_until_expiry !== null && sub.days_until_expiry !== undefined && (
                        <div className="text-sm text-slate-400 mt-1">
                          Expires in: {sub.days_until_expiry} days
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <span className={`px-3 py-1 rounded text-xs font-medium ${getStatusColor(sub.subscription_status)}`}>
                        {sub.subscription_status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-500 text-center py-8">No subscriptions found</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

