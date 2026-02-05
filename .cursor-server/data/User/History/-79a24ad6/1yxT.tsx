"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { apiRequest } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

type Tenant = {
  id: string;
  name: string;
  domain: string;
  status: "active" | "suspended" | "inactive";
  plan: string;
  created_at: string;
  users_count: number;
  usage?: {
    storage_gb: number;
    api_calls: number;
    compute_hours: number;
  };
};

type Invoice = {
  id: string;
  tenant_id: string;
  tenant_name: string;
  amount: number;
  currency: string;
  status: "paid" | "pending" | "overdue";
  due_date: string;
  created_at: string;
};

type PaymentMethod = {
  id: string;
  type: string;
  last4?: string;
  is_default: boolean;
};

export default function PlatformPage() {
  const searchParams = useSearchParams();
  const tab = searchParams.get("tab") || "tenants";
  
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [tab]);

  const fetchData = async () => {
    try {
      if (tab === "tenants" || !tab) {
        const tenantsData = await apiRequest("/api/tenants", {}, 5000).catch(() => ({ tenants: [] }));
        setTenants(tenantsData.tenants || []);
      } else if (tab === "billing") {
        const [invoicesData, pmData] = await Promise.all([
          apiRequest("/api/billing/invoices", {}, 5000).catch(() => ({ invoices: [] })),
          apiRequest("/api/billing/payment-methods", {}, 5000).catch(() => ({ payment_methods: [] }))
        ]);
        setInvoices(invoicesData.invoices || []);
        setPaymentMethods(pmData.payment_methods || []);
      }
    } catch (err) {
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && tenants.length === 0 && invoices.length === 0) {
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

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Tabs */}
          <div className="flex gap-2 border-b border-slate-800 overflow-x-auto scrollbar-thin pb-2 -mx-4 md:mx-0 px-4 md:px-0">
            <a
              href="/tenants"
              className={`px-4 py-2 border-b-2 transition-colors ${
                tab === "tenants" || !tab
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Tenants
            </a>
            <a
              href="/tenants?tab=billing"
              className={`px-4 py-2 border-b-2 transition-colors ${
                tab === "billing"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Billing
            </a>
          </div>

          {/* Tab 1: Tenants */}
          {tab === "tenants" || !tab ? (
            <div className="space-y-6">
              {/* Tenant List */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Tenant List</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {tenants.length > 0 ? (
                      tenants.map((tenant) => (
                        <div key={tenant.id} className="p-4 bg-slate-800 rounded border-l-4 border-blue-500">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="font-semibold text-lg">{tenant.name}</div>
                              <div className="text-sm text-slate-400 mt-1">{tenant.domain}</div>
                              <div className="flex gap-4 mt-2 text-sm">
                                <span>Plan: <span className="text-blue-400">{tenant.plan}</span></span>
                                <span>Users: <span className="text-purple-400">{tenant.users_count || 0}</span></span>
                                <span className={`px-2 py-1 rounded text-xs ${
                                  tenant.status === "active" ? "bg-green-500/20 text-green-400" :
                                  tenant.status === "suspended" ? "bg-yellow-500/20 text-yellow-400" :
                                  "bg-red-500/20 text-red-400"
                                }`}>
                                  {tenant.status}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No tenants found</div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Usage per Tenant */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Usage per Tenant</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {tenants.length > 0 ? (
                      tenants.map((tenant) => (
                        <div key={tenant.id} className="p-4 bg-slate-800 rounded">
                          <div className="font-medium mb-2">{tenant.name}</div>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <div className="text-slate-400">Storage</div>
                              <div className="text-blue-400 font-semibold">
                                {tenant.usage?.storage_gb?.toFixed(2) || "0"} GB
                              </div>
                            </div>
                            <div>
                              <div className="text-slate-400">API Calls</div>
                              <div className="text-purple-400 font-semibold">
                                {tenant.usage?.api_calls?.toLocaleString() || "0"}
                              </div>
                            </div>
                            <div>
                              <div className="text-slate-400">Compute Hours</div>
                              <div className="text-green-400 font-semibold">
                                {tenant.usage?.compute_hours?.toFixed(2) || "0"}h
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No usage data available</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : tab === "billing" ? (
            /* Tab 2: Billing */
            <div className="space-y-6">
              {/* Billing Logs */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Billing Logs</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {invoices.length > 0 ? (
                      invoices.map((invoice) => (
                        <div key={invoice.id} className="p-4 bg-slate-800 rounded border-l-4 border-blue-500">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{invoice.tenant_name}</div>
                              <div className="text-sm text-slate-400 mt-1">
                                Amount: <span className="text-green-400 font-semibold">
                                  {invoice.amount} {invoice.currency}
                                </span>
                              </div>
                              <div className="text-xs text-slate-500 mt-1">
                                Due: {new Date(invoice.due_date).toLocaleDateString()}
                              </div>
                            </div>
                            <span className={`px-2 py-1 rounded text-xs ${
                              invoice.status === "paid" ? "bg-green-500/20 text-green-400" :
                              invoice.status === "pending" ? "bg-yellow-500/20 text-yellow-400" :
                              "bg-red-500/20 text-red-400"
                            }`}>
                              {invoice.status}
                            </span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No invoices found</div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Payment Methods */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Payment Methods</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {paymentMethods.length > 0 ? (
                      paymentMethods.map((pm) => (
                        <div key={pm.id} className="p-4 bg-slate-800 rounded border-l-4 border-purple-500">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium capitalize">{pm.type}</div>
                              {pm.last4 && (
                                <div className="text-sm text-slate-400 mt-1">
                                  **** {pm.last4}
                                </div>
                              )}
                            </div>
                            {pm.is_default && (
                              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                                Default
                              </span>
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No payment methods configured</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : null}
        </div>
      </div>
    </main>
  );
}
