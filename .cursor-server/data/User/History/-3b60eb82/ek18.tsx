"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { API_URL } from "@/lib/api";

export default function DebuggerPage() {
  const [errors, setErrors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [watching, setWatching] = useState(false);

  useEffect(() => {
    fetchErrors();
    const interval = setInterval(fetchErrors, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchErrors = async () => {
    try {
      const res = await fetch(`${API_URL}/api/debugger/errors?limit=10`);
      if (res.ok) {
        const data = await res.json();
        setErrors(data.errors || []);
      }
    } catch (err) {
      console.error("Error fetching errors:", err);
    } finally {
      setLoading(false);
    }
  };

  const startWatching = async () => {
    try {
      const res = await fetch(`${API_URL}/api/debugger/watch/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log_dirs: ["/home/ai/ai-agent/backend/app/logs"] })
      });
      if (res.ok) {
        setWatching(true);
      }
    } catch (err) {
      console.error("Error starting watch:", err);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold">AI Debugger</h1>
              <Button onClick={startWatching} disabled={watching}>
                {watching ? "Watching..." : "Start Watching"}
              </Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Recent Errors</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : errors.length === 0 ? (
                  <p className="text-gray-500">No errors found</p>
                ) : (
                  <div className="space-y-4">
                    {errors.map((error, idx) => (
                      <div key={idx} className="p-4 bg-red-50 border border-red-200 rounded">
                        <div className="font-semibold text-red-800">
                          {error.file || "Unknown"}
                        </div>
                        <div className="text-sm text-red-600 mt-2">
                          {error.timestamp && new Date(error.timestamp).toLocaleString()}
                        </div>
                        {error.errors && error.errors.length > 0 && (
                          <div className="mt-2 text-sm">
                            {error.errors[0].content}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}

