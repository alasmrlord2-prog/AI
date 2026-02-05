"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Shield, Clock, User, Activity } from "lucide-react";

export default function AuditPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/aaa/login");
      return;
    }
    setLoading(false);
  }, [router]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Audit Logs</h1>
          <p className="text-gray-500 mt-1">System activity and security logs</p>
        </div>
      </div>

      {/* Audit Logs */}
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="text-gray-900">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-gray-500 text-center py-8">Loading...</div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              <Shield className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Audit logs will appear here</p>
              <p className="text-sm mt-2">All system activities are logged for security and compliance</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

