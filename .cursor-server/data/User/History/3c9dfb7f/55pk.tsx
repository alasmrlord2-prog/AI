"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { API_URL } from "@/lib/api";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [workflowName, setWorkflowName] = useState("");
  const [executions, setExecutions] = useState<any[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);

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
      const res = await fetch(`${API_URL}/api/workflows/${workflowId}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });

      if (res.ok) {
        const data = await res.json();
        alert(`Workflow executed! Status: ${data.status}`);
        fetchWorkflows();
      } else {
        const data = await res.json();
        alert(data.detail || "فشل تنفيذ Workflow");
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

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold text-slate-800">⚙️ Workflow Builder</h1>
              <Button className="bg-indigo-600 hover:bg-indigo-700">
                + Create Workflow
              </Button>
            </div>

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
          </div>
        </main>
      </div>
    </div>
  );
}
