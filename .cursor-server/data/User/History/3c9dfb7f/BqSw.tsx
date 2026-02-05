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

  useEffect(() => {
    fetchWorkflows();
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

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Workflow Builder</h1>

            <Card>
              <CardHeader>
                <CardTitle>Workflows</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : workflows.length === 0 ? (
                  <p className="text-gray-500">No workflows found</p>
                ) : (
                  <div className="space-y-3">
                    {workflows.map((workflow) => (
                      <div key={workflow.id} className="p-4 bg-gray-50 rounded border">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-semibold text-lg">{workflow.name}</div>
                            <div className="text-sm text-gray-600 mt-1">
                              Nodes: {workflow.nodes?.length || 0} | Edges: {workflow.edges?.length || 0}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              Created: {workflow.created_at && new Date(workflow.created_at).toLocaleString()}
                            </div>
                          </div>
                          <Button size="sm">Execute</Button>
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

