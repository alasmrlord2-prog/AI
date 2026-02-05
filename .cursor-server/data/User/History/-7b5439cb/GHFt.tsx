"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Building2, Users, CreditCard, Activity, Shield } from "lucide-react";

type CRMStats = {
  total_tenants: number;
  active_tenants: number;
  total_users: number;
  total_subscriptions: number;
  active_subscriptions: number;
  revenue?: number;
};

export default function CRMPage() {
  const router = useRouter();
  const [stats, setStats] = useState<CRMStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      // Fetch tenants to calculate stats
      const response = await crmApi.listTenants(1000, 0);
      const tenants = response.tenants || [];
      type Tenant = { status?: string; user_count?: number; subscription_status?: string };
      
      const activeTenants = tenants.filter((t: Tenant) => t.status === "active").length;
      const totalUsers = tenants.reduce((sum: number, t: Tenant) => sum + (t.user_count || 0), 0);
      const activeSubscriptions = tenants.filter((t: Tenant) => t.subscription_status === "active").length;
      
      setStats({
        total_tenants: tenants.length,
        active_tenants: activeTenants,
        total_users: totalUsers,
        total_subscriptions: tenants.length,
        active_subscriptions: activeSubscriptions,
      });
    } catch (error) {
      console.error("Error fetching CRM stats:", error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      // If authentication error, redirect to login
      if (errorMessage.includes("Not authenticated") || errorMessage.includes("401")) {
        localStorage.removeItem("auth_token");
        router.push("/crm/login");
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/crm/login");
      return;
    }
    fetchStats();
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, [router, fetchStats]);

  const statCards = [
    {
      title: "Total Tenants",
      value: stats?.total_tenants || 0,
      icon: <Building2 className="w-6 h-6" />,
      color: "text-blue-400",
      bgColor: "bg-blue-500/20",
      href: "/crm/tenants",
    },
    {
      title: "Active Tenants",
      value: stats?.active_tenants || 0,
      icon: <Activity className="w-6 h-6" />,
      color: "text-green-400",
      bgColor: "bg-green-500/20",
      href: "/crm/tenants",
    },
    {
      title: "Total Users",
      value: stats?.total_users || 0,
      icon: <Users className="w-6 h-6" />,
      color: "text-purple-400",
      bgColor: "bg-purple-500/20",
      href: "/crm/tenants",
    },
    {
      title: "Active Subscriptions",
      value: stats?.active_subscriptions || 0,
      icon: <CreditCard className="w-6 h-6" />,
      color: "text-orange-400",
      bgColor: "bg-orange-500/20",
      href: "/crm/tenants",
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-sw-text">CRM Dashboard</h2>
        </div>
        <Button
          onClick={() => router.push("/crm/tenants")}
          className="bg-sw-primary hover:bg-sw-primaryDark text-white"
        >
          View All Tenants →
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, idx) => (
          <div
            key={idx}
            className="p-6 bg-sw-surface rounded-xl border border-sw-border hover:shadow-md transition cursor-pointer"
            onClick={() => router.push(stat.href)}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sw-textLight text-sm mb-2">{stat.title}</p>
                <p className="text-2xl font-bold text-sw-text">
                  {loading ? "..." : stat.value.toLocaleString()}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-sw-primary/10 text-sw-primary">
                {stat.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-6 bg-sw-surface p-6 rounded-xl border border-sw-border">
        <h3 className="text-xl font-semibold mb-4 text-sw-text">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => router.push("/crm/tenants")}
            className="bg-sw-primary hover:bg-sw-primaryDark text-white p-4 rounded-lg font-semibold flex flex-col items-center gap-2"
          >
            <Building2 className="w-6 h-6" />
            <span>Manage Tenants</span>
          </button>
          <button
            onClick={() => router.push("/crm/users")}
            className="bg-sw-accent hover:bg-sw-accent/80 text-white p-4 rounded-lg font-semibold flex flex-col items-center gap-2"
          >
            <Users className="w-6 h-6" />
            <span>Manage Users</span>
          </button>
          <button
            onClick={() => window.open("/aaa", "_blank")}
            className="bg-gradient-to-r from-sw-primary to-sw-accent hover:opacity-90 text-white p-4 rounded-lg font-semibold flex flex-col items-center gap-2"
          >
            <Shield className="w-6 h-6" />
            <span>AAA Dashboard</span>
          </button>
        </div>
      </div>

      {/* Information */}
      <div className="mt-6 bg-sw-surface p-6 rounded-xl border border-sw-border">
        <h3 className="text-xl font-semibold mb-4 text-sw-text">CRM Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-lg font-semibold mb-3 text-sw-primary">Tenant Management</h4>
            <ul className="space-y-2 text-sw-textLight">
              <li>• View all tenants and their status</li>
              <li>• Manage tenant subscriptions</li>
              <li>• Track tenant usage and limits</li>
              <li>• View tenant audit logs</li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-3 text-sw-accent">User Management</h4>
            <ul className="space-y-2 text-sw-textLight">
              <li>• View all users per tenant</li>
              <li>• Create and manage users</li>
              <li>• Track user sessions</li>
              <li>• Monitor user activity</li>
              <li>• Access AAA Dashboard for created users</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

