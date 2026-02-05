"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { API_URL } from "@/lib/api";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [workflowName, setWorkflowName] = useState("");
  const [executions, setExecutions] = useState<any[]>([]);
  const [showExecutions, setShowExecutions] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [executionResult, setExecutionResult] = useState<any>(null);

  useEffect(() => {
    fetchWorkflows();
    const interval = setInterval(fetchWorkflows, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/workflows`);
      if (res.ok) {
        const data = await res.json();
        setWorkflows(data.workflows || []);
      }
    } catch (err) {
      console.error("Error fetching workflows:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async (workflowId: string) => {
    try {
      setSelectedWorkflow(workflowId);
      const res = await fetch(`${API_URL}/api/workflows/${workflowId}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });

      if (res.ok) {
        const data = await res.json();
        setExecutionResult(data);
        fetchWorkflows();
        // Refresh executions after execution
        setTimeout(() => fetchExecutions(workflowId), 1000);
      } else {
        const data = await res.json();
        alert(data.detail || "فشل تنفيذ Workflow");
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCreateWorkflow = async () => {
    if (!workflowName) {
      alert("يرجى إدخال اسم Workflow");
      return;
    }

    // Create a simple workflow with one trigger and one action
    const workflow = {
      name: workflowName,
      nodes: [
        {
          id: "trigger1",
          type: "trigger",
          config: {}
        },
        {
          id: "action1",
          type: "action",
          config: {
            action_type: "run_shell",
            command: "echo 'Hello from workflow'"
          }
        }
      ],
      edges: [
        {
          source: "trigger1",
          target: "action1"
        }
      ]
    };

    try {
      const res = await fetch(`${API_URL}/api/workflows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(workflow)
      });

      if (res.ok) {
        setShowCreateForm(false);
        setWorkflowName("");
        fetchWorkflows();
      } else {
        const data = await res.json();
        alert(data.detail || "فشل إنشاء Workflow");
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (workflowId: string) => {
    if (!confirm("هل أنت متأكد من حذف هذا Workflow?")) return;

    try {
      const res = await fetch(`${API_URL}/api/workflows/${workflowId}`, {
        method: "DELETE"
      });

      if (res.ok) {
        fetchWorkflows();
      } else {
        const data = await res.json();
        alert(data.detail || "فشل الحذف");
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const fetchExecutions = async (workflowId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/workflows/executions?workflow_id=${workflowId}&limit=10`);
      if (res.ok) {
        const data = await res.json();
        setExecutions(data.executions || []);
        setShowExecutions(true);
      }
    } catch (err) {
      console.error("Error fetching executions:", err);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold text-slate-800">⚙️ Workflow Builder</h1>
              <Button 
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {showCreateForm ? "إلغاء" : "+ Create Workflow"}
              </Button>
            </div>

            {showCreateForm && (
              <Card className="mb-6 border-indigo-200 bg-indigo-50">
                <CardHeader>
                  <CardTitle className="text-indigo-800">Create New Workflow</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="workflowName">Workflow Name</Label>
                    <Input
                      id="workflowName"
                      value={workflowName}
                      onChange={(e) => setWorkflowName(e.target.value)}
                      placeholder="My Workflow"
                      className="mt-1"
                    />
                  </div>
                  <p className="text-sm text-slate-600">
                    سيتم إنشاء workflow بسيط مع trigger و action. يمكنك تعديله لاحقاً.
                  </p>
                  <Button onClick={handleCreateWorkflow} className="w-full bg-indigo-600 hover:bg-indigo-700">
                    Create Workflow
                  </Button>
                </CardContent>
              </Card>
            )}

            <Card className="border-slate-200 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-t-lg">
                <CardTitle className="text-white">Workflows</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {loading ? (
                  <p className="text-slate-500">جاري التحميل...</p>
                ) : workflows.length === 0 ? (
                  <p className="text-slate-500 text-center py-8">لا توجد workflows</p>
                ) : (
                  <div className="space-y-3">
                    {workflows.map((workflow) => (
                      <div key={workflow.id} className="p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="font-semibold text-lg text-slate-800">{workflow.name}</div>
                            <div className="text-sm text-slate-600 mt-1">
                              Nodes: <span className="font-medium">{workflow.nodes?.length || 0}</span> | 
                              Edges: <span className="font-medium">{workflow.edges?.length || 0}</span>
                            </div>
                            <div className="text-xs text-slate-500 mt-1">
                              Created: {workflow.created_at && new Date(workflow.created_at).toLocaleString()}
                            </div>
                          </div>
                          <div className="flex gap-2 ml-4">
                            <Button
                              size="sm"
                              onClick={() => handleExecute(workflow.id)}
                              className="bg-green-600 hover:bg-green-700 text-xs"
                            >
                              Execute
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => fetchExecutions(workflow.id)}
                              className="text-xs"
                            >
                              Executions
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDelete(workflow.id)}
                              className="text-xs text-red-600 hover:text-red-700"
                            >
                              Delete
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {executionResult && selectedWorkflow && (
              <Card className="mt-6 border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="text-green-800">Execution Result</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div><strong>Status:</strong> <span className={`px-2 py-1 rounded ${
                      executionResult.status === "success" ? "bg-green-100 text-green-700" :
                      executionResult.status === "failed" ? "bg-red-100 text-red-700" :
                      "bg-yellow-100 text-yellow-700"
                    }`}>{executionResult.status}</span></div>
                    {executionResult.result && (
                      <div>
                        <strong>Result:</strong>
                        <pre className="bg-white p-2 rounded mt-1 text-xs overflow-auto max-h-40">
                          {JSON.stringify(executionResult.result, null, 2)}
                        </pre>
                      </div>
                    )}
                    {executionResult.error && (
                      <div className="text-red-600">
                        <strong>Error:</strong> {executionResult.error}
                      </div>
                    )}
                    {executionResult.steps && executionResult.steps.length > 0 && (
                      <div>
                        <strong>Steps:</strong>
                        <div className="mt-2 space-y-1">
                          {executionResult.steps.map((step: any, idx: number) => (
                            <div key={idx} className="text-xs bg-white p-2 rounded">
                              {step.node_type}: {step.result?.output ? JSON.stringify(step.result.output) : "OK"}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <Button
                    size="sm"
                    onClick={() => {
                      setExecutionResult(null);
                      setSelectedWorkflow(null);
                    }}
                    className="mt-4"
                  >
                    Close
                  </Button>
                </CardContent>
              </Card>
            )}

            {showExecutions && (
              <Card className="mt-6 border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-t-lg">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-white">Executions</CardTitle>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setShowExecutions(false);
                        setExecutions([]);
                      }}
                      className="text-white border-white hover:bg-white hover:text-indigo-600"
                    >
                      ✕ Close
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="p-4">
                  {executions.length === 0 ? (
                    <p className="text-slate-500 text-center py-8">لا توجد executions</p>
                  ) : (
                    <div className="space-y-3">
                      {executions.map((exec) => (
                        <div key={exec.id} className="p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="font-semibold text-slate-800">{exec.id}</div>
                              <div className="text-sm text-slate-600 mt-1">
                                Status: <span className={`font-semibold px-2 py-1 rounded ${
                                  exec.status === "success" ? "bg-green-100 text-green-700" :
                                  exec.status === "failed" ? "bg-red-100 text-red-700" :
                                  "bg-yellow-100 text-yellow-700"
                                }`}>
                                  {exec.status}
                                </span>
                              </div>
                              <div className="text-xs text-slate-500 mt-1">
                                Started: {exec.started_at && new Date(exec.started_at).toLocaleString()}
                                {exec.finished_at && ` | Finished: ${new Date(exec.finished_at).toLocaleString()}`}
                              </div>
                              {exec.error && (
                                <div className="text-xs text-red-600 mt-2 bg-red-50 p-2 rounded">
                                  {exec.error}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
