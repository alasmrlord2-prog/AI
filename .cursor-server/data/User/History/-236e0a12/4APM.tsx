"use client";

import { useEffect, useState } from "react";
import { Shield } from "lucide-react";

interface UserInfo {
  email: string;
}

export default function AAAHeader() {
  const [user, setUser] = useState<UserInfo | null>(null);

  useEffect(() => {
    // Get user info from token or API
    const token = localStorage.getItem("auth_token");
    if (token) {
      // Decode token or fetch user info
      try {
        const payload = JSON.parse(atob(token.split(".")[1])) as { email?: string };
        setUser({ email: payload.email || "admin@shiftwave.com" });
      } catch {
        setUser({ email: "admin@shiftwave.com" });
      }
    }
  }, []);

  return (
    <header className="flex-shrink-0 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <Shield className="w-5 h-5 text-swAuth-primary" />
        <h1 className="text-lg font-semibold text-gray-900">AAA System</h1>
      </div>
      <div className="flex items-center gap-4">
        {user && (
          <div className="text-sm text-gray-600">
            <span className="font-medium">{user.email}</span>
          </div>
        )}
      </div>
    </header>
  );
}

