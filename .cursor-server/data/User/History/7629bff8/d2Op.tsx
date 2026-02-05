"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import LineChart from "@/components/charts/LineChart";
import BarChart from "@/components/charts/BarChart";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 
                process.env.NEXT_PUBLIC_BACKEND_URL || 
                "http://localhost:8000";

type Invoice = {
  id: string;
  tenant_id: string;
  tenant_name: string;
  amount: number;
  currency: string;
  status: "paid" | "pending" | "overdue" | "cancelled";
  due_date: string;
  created_at: string;
  items: Array<{
    description: string;
    quantity: number;
    price: number;
  }>;
};

type Subscription = {
  id: string;
  tenant_id: string;
  tenant_name: string;
  plan: string;
  status: "active" | "cancelled" | "expired";
  current_period_start: string;
  current_period_end: string;
  amount: number;
  currency: string;
};

type PaymentMethod = {
  id: string;
  type: "card" | "bank" | "paypal";
  last4?: string;
  brand?: string;
  expiry_month?: number;
  expiry_year?: number;
  is_default: boolean;
};

export default function BillingPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "invoices" | "subscriptions" | "payment">("overview");
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);

  useEffect(() => {
    loadBillingData();
  }, []);

  const getAuthToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  };

  const loadBillingData = async () => {
    try {
      const token = getAuthToken();
      
      // Load invoices
      const invoicesRes = await fetch(`${API_URL}/api/billing/invoices`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (invoicesRes.ok) {
        const invoicesData = await invoicesRes.json();
        setInvoices(invoicesData.invoices || []);
      }

      // Load subscriptions
      const subsRes = await fetch(`${API_URL}/api/billing/subscriptions`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (subsRes.ok) {
        const subsData = await subsRes.json();
        setSubscriptions(subsData.subscriptions || []);
      }

      // Load payment methods
      const pmRes = await fetch(`${API_URL}/api/billing/payment-methods`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (pmRes.ok) {
        const pmData = await pmRes.json();
        setPaymentMethods(pmData.payment_methods || []);
      }
    } catch (err) {
      console.error("Failed to load billing data:", err);
    }
  };

  const handlePayInvoice = async (invoiceId: string) => {
    setLoading(true);
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/billing/invoices/${invoiceId}/pay`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        await loadBillingData();
        alert("Invoice paid successfully!");
      }
    } catch (err) {
      console.error("Failed to pay invoice:", err);
      alert("Failed to pay invoice");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "paid": return "bg-green-500";
      case "pending": return "bg-yellow-500";
      case "overdue": return "bg-red-500";
      case "cancelled": return "bg-slate-500";
      default: return "bg-slate-500";
    }
  };

  const totalRevenue = invoices
    .filter(i => i.status === "paid")
    .reduce((sum, i) => sum + i.amount, 0);

  const pendingAmount = invoices
    .filter(i => i.status === "pending" || i.status === "overdue")
    .reduce((sum, i) => sum + i.amount, 0);

  const revenueData = invoices
    .filter(i => i.status === "paid")
    .reduce((acc, invoice) => {
      const month = new Date(invoice.created_at).toLocaleDateString('en-US', { month: 'short' });
      acc[month] = (acc[month] || 0) + invoice.amount;
      return acc;
    }, {} as Record<string, number>);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
              💳 Billing System
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Manage invoices, subscriptions, and payments
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b border-slate-800">
            {[
              { id: "overview", label: "Overview", icon: "📊" },
              { id: "invoices", label: "Invoices", icon: "📄" },
              { id: "subscriptions", label: "Subscriptions", icon: "🔄" },
              { id: "payment", label: "Payment Methods", icon: "💳" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? "border-green-500 text-green-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          {/* Overview Tab */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="bg-gradient-to-br from-green-900/30 to-green-800/30 border-green-700">
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-green-400">
                      ${totalRevenue.toLocaleString()}
                    </div>
                    <div className="text-xs text-slate-400">Total Revenue</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/30 border-yellow-700">
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-yellow-400">
                      ${pendingAmount.toLocaleString()}
                    </div>
                    <div className="text-xs text-slate-400">Pending</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-900/30 to-blue-800/30 border-blue-700">
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-blue-400">
                      {invoices.filter(i => i.status === "paid").length}
                    </div>
                    <div className="text-xs text-slate-400">Paid Invoices</div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-purple-900/30 to-purple-800/30 border-purple-700">
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-purple-400">
                      {subscriptions.filter(s => s.status === "active").length}
                    </div>
                    <div className="text-xs text-slate-400">Active Subscriptions</div>
                  </CardContent>
                </Card>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Revenue Trend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <LineChart
                      data={Object.entries(revenueData)
                        .map(([label, value]) => ({ label, value }))}
                      color="#10b981"
                      height={200}
                    />
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Invoice Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <BarChart
                      data={[
                        { label: "Paid", value: invoices.filter(i => i.status === "paid").length },
                        { label: "Pending", value: invoices.filter(i => i.status === "pending").length },
                        { label: "Overdue", value: invoices.filter(i => i.status === "overdue").length },
                        { label: "Cancelled", value: invoices.filter(i => i.status === "cancelled").length },
                      ]}
                      color="#8b5cf6"
                      height={200}
                    />
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* Invoices Tab */}
          {activeTab === "invoices" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Invoices ({invoices.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {invoices.map((invoice) => (
                      <div
                        key={invoice.id}
                        className="p-4 border border-slate-700 rounded-lg hover:bg-slate-800 transition-all"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="font-bold text-green-400">#{invoice.id}</span>
                              <span className="text-sm text-slate-300">{invoice.tenant_name}</span>
                              <div className="flex items-center gap-2">
                                <div className={`h-2 w-2 rounded-full ${getStatusColor(invoice.status)}`}></div>
                                <span className="text-xs text-slate-400 capitalize">{invoice.status}</span>
                              </div>
                            </div>
                            <div className="text-sm text-slate-300 mb-2">
                              Due: {new Date(invoice.due_date).toLocaleDateString()}
                            </div>
                            <div className="text-lg font-bold text-green-400">
                              {invoice.currency} {invoice.amount.toLocaleString()}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              onClick={() => setSelectedInvoice(invoice)}
                              className="bg-slate-700 hover:bg-slate-600"
                            >
                              View
                            </Button>
                            {invoice.status === "pending" && (
                              <Button
                                onClick={() => handlePayInvoice(invoice.id)}
                                disabled={loading}
                                className="bg-green-600 hover:bg-green-700"
                              >
                                Pay
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {selectedInvoice && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Invoice #{selectedInvoice.id}</CardTitle>
                      <Button
                        onClick={() => setSelectedInvoice(null)}
                        className="bg-slate-700 hover:bg-slate-600"
                      >
                        Close
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Tenant</div>
                          <div className="text-slate-300">{selectedInvoice.tenant_name}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Status</div>
                          <div className="text-slate-300 capitalize">{selectedInvoice.status}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Amount</div>
                          <div className="text-lg font-bold text-green-400">
                            {selectedInvoice.currency} {selectedInvoice.amount.toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Due Date</div>
                          <div className="text-slate-300">
                            {new Date(selectedInvoice.due_date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400 mb-2">Items</div>
                        <div className="space-y-2">
                          {selectedInvoice.items.map((item, idx) => (
                            <div key={idx} className="flex justify-between p-2 bg-slate-800 rounded">
                              <div>
                                <div className="text-sm text-slate-300">{item.description}</div>
                                <div className="text-xs text-slate-400">Qty: {item.quantity}</div>
                              </div>
                              <div className="text-sm font-bold text-slate-300">
                                {selectedInvoice.currency} {(item.price * item.quantity).toLocaleString()}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Subscriptions Tab */}
          {activeTab === "subscriptions" && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Subscriptions ({subscriptions.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {subscriptions.map((sub) => (
                    <div
                      key={sub.id}
                      className="p-4 border border-slate-700 rounded-lg"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="font-bold text-blue-400">{sub.tenant_name}</span>
                            <span className="text-sm px-2 py-1 bg-blue-900/30 text-blue-400 rounded">
                              {sub.plan.toUpperCase()}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded ${
                              sub.status === "active" ? "bg-green-900/30 text-green-400" :
                              sub.status === "cancelled" ? "bg-red-900/30 text-red-400" :
                              "bg-slate-700 text-slate-400"
                            }`}>
                              {sub.status}
                            </span>
                          </div>
                          <div className="text-sm text-slate-300 mb-2">
                            Period: {new Date(sub.current_period_start).toLocaleDateString()} - {new Date(sub.current_period_end).toLocaleDateString()}
                          </div>
                          <div className="text-lg font-bold text-green-400">
                            {sub.currency} {sub.amount.toLocaleString()} / month
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Payment Methods Tab */}
          {activeTab === "payment" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Payment Methods</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {paymentMethods.map((pm) => (
                      <div
                        key={pm.id}
                        className="p-4 border border-slate-700 rounded-lg flex items-center justify-between"
                      >
                        <div className="flex items-center gap-4">
                          <div className="text-2xl">
                            {pm.type === "card" ? "💳" : pm.type === "bank" ? "🏦" : "📧"}
                          </div>
                          <div>
                            <div className="font-bold text-slate-300 capitalize">
                              {pm.type} {pm.brand && `(${pm.brand})`}
                            </div>
                            {pm.last4 && (
                              <div className="text-sm text-slate-400">
                                **** **** **** {pm.last4}
                              </div>
                            )}
                            {pm.expiry_month && pm.expiry_year && (
                              <div className="text-xs text-slate-400">
                                Expires: {pm.expiry_month}/{pm.expiry_year}
                              </div>
                            )}
                          </div>
                          {pm.is_default && (
                            <span className="px-2 py-1 bg-green-900/30 text-green-400 text-xs rounded">
                              Default
                            </span>
                          )}
                        </div>
                        <Button className="bg-slate-700 hover:bg-slate-600">
                          {pm.is_default ? "Edit" : "Set as Default"}
                        </Button>
                      </div>
                    ))}
                  </div>
                  <Button className="mt-4 w-full bg-green-600 hover:bg-green-700">
                    + Add Payment Method
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

