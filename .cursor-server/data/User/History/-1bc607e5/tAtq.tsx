"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { subscriptionApi, crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

type SubscriptionStatus = {
  subscription: {
    id: string;
    tenant_id: string;
    plan_id: string;
    start_at: string;
    end_at: string;
    status: string;
    plan?: {
      name: string;
      description?: string;
    };
  };
  is_active: boolean;
  is_expired: boolean;
  is_in_grace: boolean;
  days_until_expiry?: number;
  usage: Record<string, number>;
  limits: Record<string, number>;
};

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
  features_json?: Record<string, boolean>;
};

export default function SubscriptionPage() {
  const params = useParams();
  const router = useRouter();
  const tenantId = params.tenantId as string;
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [tenantId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [subData, plansData] = await Promise.all([
        subscriptionApi.getSubscriptionStatus(tenantId),
        subscriptionApi.getPlans(),
      ]);
      setSubscription(subData);
      setPlans(plansData || []);
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

  if (loading && !subscription) {
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

  if (!subscription) {
    return (
      <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-slate-400">No subscription found</div>
          </div>
        </div>
      </main>
    );
  }

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
                onClick={() => router.push(`/crm/tenants/${tenantId}`)}
                className="text-slate-400 hover:text-slate-200 mb-2"
              >
                ← Back to Dashboard
              </Button>
              <h1 className="text-2xl md:text-3xl font-bold">Subscription Management</h1>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Current Subscription */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Current Subscription</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-slate-400 text-sm">Plan</div>
                  <div className="text-xl font-semibold text-blue-400">
                    {subscription.subscription.plan?.name || "No Plan"}
                  </div>
                </div>

                <div>
                  <div className="text-slate-400 text-sm">Status</div>
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(subscription.subscription.status)}`}>
                    {subscription.subscription.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-slate-400 text-sm">Start Date</div>
                    <div className="text-slate-200">
                      {new Date(subscription.subscription.start_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-slate-400 text-sm">End Date</div>
                    <div className="text-slate-200">
                      {new Date(subscription.subscription.end_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                {subscription.days_until_expiry !== null && subscription.days_until_expiry !== undefined && (
                  <div>
                    <div className="text-slate-400 text-sm">Days Until Expiry</div>
                    <div className={`text-2xl font-bold ${
                      subscription.days_until_expiry < 7 ? "text-red-400" :
                      subscription.days_until_expiry < 30 ? "text-orange-400" :
                      "text-green-400"
                    }`}>
                      {subscription.days_until_expiry}
                    </div>
                  </div>
                )}

                {subscription.is_in_grace && (
                  <div className="p-3 bg-yellow-500/20 border border-yellow-500/50 rounded">
                    <div className="text-yellow-400 font-medium">Grace Period Active</div>
                    <div className="text-yellow-300/80 text-sm mt-1">
                      Subscription has expired but is still in grace period.
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Usage & Limits */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Usage & Limits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(subscription.usage).map(([key, value]) => {
                    const limit = subscription.limits[key];
                    const percentage = limit ? (value / limit) * 100 : 0;
                    return (
                      <div key={key} className="p-3 bg-slate-800 rounded">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-slate-300 capitalize text-sm">
                            {key.replace(/_/g, " ")}
                          </span>
                          <span className="text-blue-400 font-semibold">
                            {value} {limit ? `/ ${limit}` : ""}
                          </span>
                        </div>
                        {limit && (
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                percentage > 90 ? "bg-red-500" :
                                percentage > 75 ? "bg-orange-500" :
                                "bg-blue-500"
                              }`}
                              style={{ width: `${Math.min(100, percentage)}%` }}
                            />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Available Plans */}
            <Card className="bg-slate-900 border-slate-800 lg:col-span-2">
              <CardHeader>
                <CardTitle>Available Plans</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {plans.map((plan) => (
                    <div
                      key={plan.id}
                      className={`p-4 bg-slate-800 rounded border-2 ${
                        subscription.subscription.plan_id === plan.id
                          ? "border-blue-500"
                          : "border-slate-700"
                      }`}
                    >
                      <div className="font-semibold text-lg">{plan.name}</div>
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
                          <div className="text-slate-400">
                            Max Users: {plan.max_users}
                          </div>
                        )}
                        {plan.max_requests && (
                          <div className="text-slate-400">
                            Max Requests: {plan.max_requests.toLocaleString()}
                          </div>
                        )}
                      </div>
                      {subscription.subscription.plan_id !== plan.id && (
                        <Button
                          className="w-full mt-4 bg-blue-600 hover:bg-blue-700"
                          onClick={() => {
                            // TODO: Implement upgrade/downgrade
                            alert("Upgrade/Downgrade functionality coming soon");
                          }}
                        >
                          {subscription.subscription.plan_id ? "Switch Plan" : "Subscribe"}
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}

