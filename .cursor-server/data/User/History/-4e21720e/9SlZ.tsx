"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { identityApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Shield, Key, Users, Activity, TrendingUp } from "lucide-react";

type AAAStats = {
  total_tokens: number;
  active_tokens: number;
  total_sessions: number;
  active_sessions: number;
  total_users: number;
};

export default function AAAPage() {
  const router = useRouter();
  const [stats, setStats] = useState<AAAStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/aaa/login");
      return;
    }
    fetchStats();
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, [router]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      // Fetch tokens
      const tokens = await identityApi.listApiTokens();
      const activeTokens = (tokens || []).filter((t: any) => {
        if (!t.expires_at) return true;
        return new Date(t.expires_at) > new Date();
      });

      // Fetch sessions
      const sessions = await identityApi.getSessions();
      const activeSessions = (sessions || []).filter((s: any) => {
        if (!s.expires_at) return true;
        return new Date(s.expires_at) > new Date();
      });

      setStats({
        total_tokens: (tokens || []).length,
        active_tokens: activeTokens.length,
        total_sessions: (sessions || []).length,
        active_sessions: activeSessions.length,
        total_users: 0, // TODO: Fetch from API
      });
    } catch (error: any) {
      console.error("Error fetching AAA stats:", error);
      // If authentication error, redirect to login
      if (error?.message?.includes("Not authenticated") || error?.message?.includes("401")) {
        localStorage.removeItem("auth_token");
        router.push("/aaa/login");
      }
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: "Total Tokens",
      value: stats?.total_tokens || 0,
      icon: <Key className="w-6 h-6" />,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      href: "/aaa/tokens",
    },
    {
      title: "Active Tokens",
      value: stats?.active_tokens || 0,
      icon: <Key className="w-6 h-6" />,
      color: "text-green-600",
      bgColor: "bg-green-50",
      href: "/aaa/tokens",
    },
    {
      title: "Active Sessions",
      value: stats?.active_sessions || 0,
      icon: <Activity className="w-6 h-6" />,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      href: "/aaa/sessions",
    },
    {
      title: "Total Users",
      value: stats?.total_users || 0,
      icon: <Users className="w-6 h-6" />,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      href: "/aaa/users",
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">AAA Dashboard</h1>
          <p className="text-gray-500 mt-1">Authentication, Authorization, and Accounting</p>
        </div>
        <div className="flex items-center gap-2">
          <Shield className="w-6 h-6 text-swAuth-primary" />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, idx) => (
          <Card
            key={idx}
            className="bg-white border border-gray-200 hover:border-swAuth-primary transition-all cursor-pointer hover:shadow-md"
            onClick={() => router.push(stat.href)}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm mb-2">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">
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
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="text-gray-900">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push("/aaa/tokens")}
              className="bg-swAuth-primary hover:bg-swAuth-primary/90 text-white p-4 rounded-lg font-semibold flex flex-col items-center gap-2"
            >
              <Key className="w-6 h-6" />
              <span>Manage Tokens</span>
            </button>
            <button
              onClick={() => router.push("/aaa/sessions")}
              className="bg-gray-600 hover:bg-gray-700 text-white p-4 rounded-lg font-semibold flex flex-col items-center gap-2"
            >
              <Activity className="w-6 h-6" />
              <span>View Sessions</span>
            </button>
            <button
              onClick={() => router.push("/aaa/users")}
              className="bg-gradient-to-r from-swAuth-primary to-swAuth-primary/80 hover:opacity-90 text-white p-4 rounded-lg font-semibold flex flex-col items-center gap-2"
            >
              <Users className="w-6 h-6" />
              <span>Manage Users</span>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

