"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 
                process.env.NEXT_PUBLIC_BACKEND_URL || 
                "http://localhost:8000";

type PendingAction = {
  id: string;
  user_email: string;
  tool_name: string;
  tool_args: Record<string, any>;
  reason: string;
  status: string;
  created_at: string;
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  execution_result?: string;
  execution_error?: string;
};

export default function ApprovalsPage() {
  const [actions, setActions] = useState<PendingAction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const getAuthToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  };

  const loadActions = async () => {
    setLoading(true);
    setError("");

    try {
      const token = getAuthToken();
      if (!token) {
        setError("Not authenticated");
        return;
      }

      const res = await fetch(`${API_URL}/api/pending-actions`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setActions(data.actions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load actions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActions();
    // Refresh every 5 seconds
    const interval = setInterval(loadActions, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (actionId: string) => {
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/pending-actions/${actionId}/approve`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to approve");
      }

      await loadActions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to approve");
    }
  };

  const handleReject = async (actionId: string) => {
    const reason = prompt("Rejection reason (optional):");
    if (reason === null) return; // User cancelled

    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/pending-actions/${actionId}/reject`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ reason }),
      });

      if (!res.ok) {
        throw new Error("Failed to reject");
      }

      await loadActions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject");
    }
  };

  const pendingActions = actions.filter(a => a.status === "pending");
  const completedActions = actions.filter(a => a.status !== "pending");

  return (
    <main className="p-6 text-slate-200 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Pending Actions</h1>
        <Button onClick={loadActions} disabled={loading} className="bg-indigo-600">
          {loading ? "جاري التحديث..." : "تحديث"}
        </Button>
      </div>

      {error && (
        <div className="p-3 bg-red-900/50 border border-red-700 rounded text-red-200">
          {error}
        </div>
      )}

      {/* Pending Actions */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">
          Pending ({pendingActions.length})
        </h2>
        {pendingActions.length === 0 ? (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-4 text-center text-slate-400">
              No pending actions
            </CardContent>
          </Card>
        ) : (
          pendingActions.map((action) => (
            <Card key={action.id} className="bg-slate-900 border-yellow-700">
              <CardHeader>
                <CardTitle className="text-yellow-400">
                  {action.tool_name} - {action.user_email}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm text-slate-400">Arguments:</div>
                  <pre className="text-xs bg-slate-800 p-2 rounded mt-1 overflow-x-auto">
                    {JSON.stringify(action.tool_args, null, 2)}
                  </pre>
                </div>
                {action.reason && (
                  <div>
                    <div className="text-sm text-slate-400">Reason:</div>
                    <div className="text-sm">{action.reason}</div>
                  </div>
                )}
                <div className="text-xs text-slate-400">
                  Created: {new Date(action.created_at).toLocaleString()}
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleApprove(action.id)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Approve
                  </Button>
                  <Button
                    onClick={() => handleReject(action.id)}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    Reject
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Completed Actions */}
      {completedActions.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">
            Completed ({completedActions.length})
          </h2>
          {completedActions.map((action) => (
            <Card
              key={action.id}
              className={`bg-slate-900 border-${
                action.status === "approved" ? "green" : "red"
              }-700`}
            >
              <CardHeader>
                <CardTitle
                  className={
                    action.status === "approved"
                      ? "text-green-400"
                      : "text-red-400"
                  }
                >
                  {action.tool_name} - {action.user_email} ({action.status})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-xs text-slate-400">
                  {action.status === "approved"
                    ? `Approved by ${action.approved_by} at ${new Date(action.approved_at || "").toLocaleString()}`
                    : `Rejected by ${action.approved_by} at ${new Date(action.approved_at || "").toLocaleString()}`}
                </div>
                {action.execution_result && (
                  <div>
                    <div className="text-sm text-slate-400">Execution Result:</div>
                    <pre className="text-xs bg-slate-800 p-2 rounded mt-1 overflow-x-auto">
                      {action.execution_result}
                    </pre>
                  </div>
                )}
                {action.execution_error && (
                  <div className="text-sm text-red-400">
                    Error: {action.execution_error}
                  </div>
                )}
                {action.rejection_reason && (
                  <div className="text-sm text-red-400">
                    Reason: {action.rejection_reason}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </main>
  );
}

