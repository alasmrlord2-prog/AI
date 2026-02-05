"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { identityApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Users, Calendar, Shield } from "lucide-react";

type User = {
  id: string;
  email: string;
  full_name?: string;
  status: string;
  email_verified: boolean;
  created_at: string;
  last_login_at?: string;
};

export default function AAAUsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await identityApi.listUsers();
      setUsers(data || []);
    } catch (error) {
      console.error("Error fetching users:", error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      // If authentication error, redirect to login
      if (errorMessage.includes("Not authenticated") || errorMessage.includes("401")) {
        localStorage.removeItem("auth_token");
        router.push("/aaa/login");
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/aaa/login");
      return;
    }
    fetchUsers();
  }, [router, fetchUsers]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Users</h1>
          <p className="text-gray-500 mt-1">Manage system users</p>
        </div>
      </div>

      {/* Users List */}
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="text-gray-900">All Users ({users.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-gray-500 text-center py-8">Loading...</div>
          ) : users.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {users.map((user) => (
                <div
                  key={user.id}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-swAuth-primary transition-all"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-swAuth-primary/10 flex items-center justify-center">
                      <Users className="w-5 h-5 text-swAuth-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">
                        {user.full_name || user.email}
                      </div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Shield className="w-4 h-4" />
                      <span className={user.status === "active" ? "text-green-600" : "text-red-600"}>
                        {user.status}
                      </span>
                    </div>
                    {user.last_login_at && (
                      <div className="flex items-center gap-2 text-gray-600">
                        <Calendar className="w-4 h-4" />
                        <span>Last login: {new Date(user.last_login_at).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No users found</p>
              <p className="text-sm mt-2">Users created in CRM will appear here</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

