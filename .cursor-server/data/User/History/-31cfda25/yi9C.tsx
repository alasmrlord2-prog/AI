"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Building2, Mail, Lock, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function CRMLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Check if already logged in
    const token = localStorage.getItem("auth_token");
    if (token) {
      router.push("/crm");
    }
  }, [router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      // Use same hostname as frontend (nginx proxies /api to backend)
      const apiUrl = typeof window !== 'undefined' 
        ? `${window.location.protocol}//${window.location.hostname}${window.location.port ? `:${window.location.port}` : ''}`
        : (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000");
      
      const response = await fetch(`${apiUrl}/api/identity/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Login failed" }));
        setError(errorData.detail || "Invalid credentials");
        setLoading(false);
        return;
      }

      const data = await response.json();

      if (response.ok && data.access_token) {
        localStorage.setItem("auth_token", data.access_token);
        // Check if user has CRM admin role
        // TODO: Verify user has crm_admin role
        router.push("/crm");
      } else {
        setError(data.detail || "Invalid credentials");
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error");
      if (error.name === 'AbortError') {
        setError("Login took too long. Please try again.");
      } else if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
        setError("Cannot connect to server. Please check your connection.");
      } else {
        setError(error.message || "Connection error. Please try again.");
      }
      console.error("Login error:", err);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sw-blue via-sw-blue to-sw-teal flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-sw-bg-card border-sw-border shadow-xl">
        <CardHeader className="text-center pb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-sw-blue to-sw-teal flex items-center justify-center">
              <Building2 className="w-8 h-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-sw-text-strong">
            Shiftwave CRM
          </CardTitle>
          <p className="text-sm text-sw-text-muted mt-2">
            Sign in to manage your customers
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 rounded-lg flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-sw-text-soft">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-sw-text-muted" />
                <Input
                  id="email"
                  type="email"
                  placeholder="admin@shiftwave.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="pl-10 bg-sw-bg-soft border-sw-border text-sw-text"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-sw-text-soft">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-sw-text-muted" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pl-10 bg-sw-bg-soft border-sw-border text-sw-text"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-sw-blue hover:bg-sw-blue-light text-white h-11 font-medium"
            >
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-sw-text-muted">
              Only authorized CRM administrators can access this system
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

