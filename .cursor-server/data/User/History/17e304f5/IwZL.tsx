"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
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
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-6 scrollbar-thin min-h-0">
          {/* Header */}
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold">CRM Dashboard</h1>
              <p className="text-slate-400 mt-1">Customer Relationship Management</p>
            </div>
            <Button
              onClick={() => router.push("/crm/tenants")}
              className="bg-blue-600 hover:bg-blue-700"
            >
              View All Tenants →
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {statCards.map((stat, idx) => (
              <Card
                key={idx}
                className="bg-slate-900 border-slate-800 hover:border-blue-500 transition-colors cursor-pointer"
                onClick={() => router.push(stat.href)}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-sm mb-2">{stat.title}</p>
                      <p className={`text-2xl font-bold ${stat.color}`}>
                        {loading ? "..." : stat.value.toLocaleString()}
                      </p>
                    </div>
                    <div className={`p-3 rounded-lg ${stat.bgColor} ${stat.color}`}>
                      {stat.icon}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Quick Actions */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button
                  onClick={() => router.push("/crm/tenants")}
                  className="bg-blue-600 hover:bg-blue-700 h-auto py-4 flex flex-col items-center gap-2"
                >
                  <Building2 className="w-6 h-6" />
                  <span>Manage Tenants</span>
                </Button>
                <Button
                  onClick={() => router.push("/iam/roles")}
                  className="bg-purple-600 hover:bg-purple-700 h-auto py-4 flex flex-col items-center gap-2"
                >
                  <Users className="w-6 h-6" />
                  <span>Manage Roles</span>
                </Button>
                <Button
                  onClick={() => router.push("/iam/policies")}
                  className="bg-green-600 hover:bg-green-700 h-auto py-4 flex flex-col items-center gap-2"
                >
                  <Shield className="w-6 h-6" />
                  <span>Manage Policies</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Information */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>CRM Features</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-blue-400">Tenant Management</h3>
                  <ul className="space-y-2 text-slate-400">
                    <li>• View all tenants and their status</li>
                    <li>• Manage tenant subscriptions</li>
                    <li>• Track tenant usage and limits</li>
                    <li>• View tenant audit logs</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-purple-400">User Management</h3>
                  <ul className="space-y-2 text-slate-400">
                    <li>• View all users per tenant</li>
                    <li>• Manage user roles and permissions</li>
                    <li>• Track user sessions</li>
                    <li>• Monitor user activity</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

