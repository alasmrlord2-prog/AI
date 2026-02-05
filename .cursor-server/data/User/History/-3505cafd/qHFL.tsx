"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

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
  execution_warning?: string;
  executed_at?: string;
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
      const data = await apiRequest("/api/pending-actions", {}, 5000);
      setActions(data.actions || []);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to load actions";
      setError(errorMsg);
      setActions([]);
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
      setLoading(true);
      setError("");
      
      console.log(`Approving action: ${actionId}`);
      
      const result = await apiRequest(`/api/pending-actions/${actionId}/approve`, {
        method: "POST",
      }, 10000);
      
      console.log("Approval result:", result);
      
      // Update the action in the local state immediately
      if (result.action) {
        setActions(prev => prev.map(a => 
          a.id === actionId ? { ...a, ...result.action } : a
        ));
      }
      
      // Wait a bit for backend to save the result, then reload
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Reload actions to get the latest execution results
      await loadActions();
    } catch (err) {
      console.error("Approval error:", err);
      const errorMsg = err instanceof Error ? err.message : "Failed to approve";
      setError(errorMsg);
      // Reload actions anyway to see current state
      await loadActions();
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (actionId: string) => {
    const reason = prompt("Rejection reason (optional):");
    if (reason === null) return; // User cancelled

    try {
      await apiRequest(`/api/pending-actions/${actionId}/reject`, {
        method: "POST",
        body: JSON.stringify({ reason }),
      }, 5000);

      await loadActions();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to reject";
      setError(errorMsg);
    }
  };

  const pendingActions = actions.filter(a => a.status === "pending");
  const completedActions = actions.filter(a => a.status !== "pending");

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                ⚖️ Pending Actions
              </h1>
              <Button 
                onClick={loadActions} 
                disabled={loading} 
                className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="animate-spin">⏳</span> جاري التحديث...
                  </span>
                ) : (
                  "🔄 تحديث"
                )}
              </Button>
            </div>
            <p className="text-sm text-slate-400">
              Review and approve AI agent actions requiring authorization
            </p>
          </div>

          {error && (
            <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300 flex items-center gap-2">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Pending Actions */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-yellow-400 flex items-center gap-2">
              <span>⏳</span>
              Pending ({pendingActions.length})
            </h2>
            {pendingActions.length === 0 ? (
              <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 shadow-lg">
                <CardContent className="p-8 text-center">
                  <div className="text-6xl mb-4">✅</div>
                  <p className="text-slate-400 text-lg">No pending actions</p>
                  <p className="text-slate-500 text-sm mt-2">All actions have been processed</p>
                </CardContent>
              </Card>
            ) : (
              pendingActions.map((action) => (
                <Card key={action.id} className="bg-gradient-to-br from-slate-900 to-slate-800 border-yellow-600 shadow-lg hover:border-yellow-500 transition-colors">
                  <CardHeader>
                    <CardTitle className="text-yellow-400 flex items-center gap-2">
                      <span>🔔</span>
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
                  <div className="flex gap-3">
                    <Button
                      onClick={() => handleApprove(action.id)}
                      className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold flex-1"
                    >
                      ✅ Approve
                    </Button>
                    <Button
                      onClick={() => handleReject(action.id)}
                      className="bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white font-semibold flex-1"
                    >
                      ❌ Reject
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
              <h2 className="text-xl font-semibold text-slate-300 flex items-center gap-2">
                <span>📋</span>
                Completed ({completedActions.length})
              </h2>
              {completedActions.map((action) => (
                <Card
                  key={action.id}
                  className={`bg-gradient-to-br from-slate-900 to-slate-800 border-${
                    action.status === "approved" ? "green" : "red"
                  }-600 shadow-lg`}
                >
                  <CardHeader>
                    <CardTitle
                      className={`flex items-center gap-2 ${
                        action.status === "approved"
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
                    >
                      <span>{action.status === "approved" ? "✅" : "❌"}</span>
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
                  <div className="mt-3">
                    <div className="text-sm font-semibold text-green-400 mb-1 flex items-center gap-2">
                      ✅ Execution Result:
                      {action.executed_at && (
                        <span className="text-xs text-slate-500 font-normal">
                          ({new Date(action.executed_at).toLocaleString()})
                        </span>
                      )}
                    </div>
                    <div className="bg-slate-800 p-3 rounded mt-1 border border-green-700/30 max-h-96 overflow-auto">
                      <pre className="text-xs whitespace-pre-wrap break-words">
                        {(() => {
                          try {
                            // Try to parse as JSON for better formatting
                            if (typeof action.execution_result === 'string') {
                              const parsed = JSON.parse(action.execution_result);
                              return JSON.stringify(parsed, null, 2);
                            }
                            return JSON.stringify(action.execution_result, null, 2);
                          } catch {
                            // If not JSON, display as-is
                            return String(action.execution_result);
                          }
                        })()}
                      </pre>
                    </div>
                  </div>
                )}
                {action.execution_warning && (
                  <div className="mt-2 text-sm text-yellow-400 bg-yellow-900/20 p-2 rounded border border-yellow-700/30">
                    ⚠️ Warning: {action.execution_warning}
                  </div>
                )}
                {action.execution_error && (
                  <div className="mt-2 text-sm text-red-400 bg-red-900/20 p-2 rounded border border-red-700/30">
                    ❌ Error: {action.execution_error}
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
      </div>
    </div>
  );
}

