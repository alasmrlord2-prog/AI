"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, Users, CreditCard, TrendingUp, Activity, AlertTriangle, Shield } from "lucide-react";

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

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      // Fetch tenants to calculate stats
      const response = await crmApi.listTenants(1000, 0);
      const tenants = response.tenants || [];
      
      const activeTenants = tenants.filter((t: any) => t.status === "active").length;
      const totalUsers = tenants.reduce((sum: number, t: any) => sum + (t.user_count || 0), 0);
      const activeSubscriptions = tenants.filter((t: any) => t.subscription_status === "active").length;
      
      setStats({
        total_tenants: tenants.length,
        active_tenants: activeTenants,
        total_users: totalUsers,
        total_subscriptions: tenants.length,
        active_subscriptions: activeSubscriptions,
      });
    } catch (error) {
      console.error("Error fetching CRM stats:", error);
    } finally {
      setLoading(false);
    }
  };

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
          <h1 className="text-2xl md:text-3xl font-bold text-sw-text-strong">CRM Dashboard</h1>
          <p className="text-sw-text-muted mt-1">Customer Relationship Management</p>
        </div>
        <Button
          onClick={() => router.push("/crm/tenants")}
          className="bg-sw-blue hover:bg-sw-blue-light text-white"
        >
          View All Tenants →
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, idx) => (
          <Card
            key={idx}
            className="bg-sw-bg-card border-sw-border hover:border-sw-blue transition-all cursor-pointer hover:shadow-md"
            onClick={() => router.push(stat.href)}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sw-text-muted text-sm mb-2">{stat.title}</p>
                  <p className="text-2xl font-bold text-sw-text-strong">
                    {loading ? "..." : stat.value.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-sw-blue/10 text-sw-blue">
                  {stat.icon}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <Card className="bg-sw-bg-card border-sw-border">
        <CardHeader>
          <CardTitle className="text-sw-text-strong">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              onClick={() => router.push("/crm/tenants")}
              className="bg-sw-blue hover:bg-sw-blue-light text-white h-auto py-4 flex flex-col items-center gap-2"
            >
              <Building2 className="w-6 h-6" />
              <span>Manage Tenants</span>
            </Button>
            <Button
              onClick={() => router.push("/crm/users")}
              className="bg-sw-teal hover:bg-sw-teal-light text-white h-auto py-4 flex flex-col items-center gap-2"
            >
              <Users className="w-6 h-6" />
              <span>Manage Users</span>
            </Button>
            <Button
              onClick={() => router.push("/crm/subscriptions")}
              className="bg-gradient-to-r from-sw-blue to-sw-teal hover:opacity-90 text-white h-auto py-4 flex flex-col items-center gap-2"
            >
              <CreditCard className="w-6 h-6" />
              <span>Subscription Plans</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Information */}
      <Card className="bg-sw-bg-card border-sw-border">
        <CardHeader>
          <CardTitle className="text-sw-text-strong">CRM Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-3 text-sw-blue">Tenant Management</h3>
              <ul className="space-y-2 text-sw-text-muted">
                <li>• View all tenants and their status</li>
                <li>• Manage tenant subscriptions</li>
                <li>• Track tenant usage and limits</li>
                <li>• View tenant audit logs</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-3 text-sw-teal">User Management</h3>
              <ul className="space-y-2 text-sw-text-muted">
                <li>• View all users per tenant</li>
                <li>• Create and manage users</li>
                <li>• Track user sessions</li>
                <li>• Monitor user activity</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

