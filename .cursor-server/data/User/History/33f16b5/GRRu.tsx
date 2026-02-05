"use client";

import { useEffect, useState, useCallback } from "react";
import { policyApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

type RelationTuple = {
  id: string;
  subject_type: string;
  subject_id: string;
  object_type: string;
  object_id: string;
  relation: string;
  tenant_id?: string;
  is_active: boolean;
  created_at: string;
};

type PolicyRule = {
  id: string;
  name: string;
  description?: string;
  rule_definition: string;
  tenant_id?: string;
  resource_type?: string;
  priority: number;
  is_active: boolean;
};

export default function PoliciesPage() {
  const [activeTab, setActiveTab] = useState<"relations" | "rules">("relations");
  const [relations, setRelations] = useState<RelationTuple[]>([]);
  const [rules, setRules] = useState<PolicyRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      if (activeTab === "relations") {
        const data = await policyApi.getRelations({});
        setRelations(data || []);
      } else {
        const data = await policyApi.getPolicyRules();
        setRules(data || []);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Header */}
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold">IAM - Policies</h1>
              <p className="text-slate-400 mt-1">Zanzibar-style policy engine</p>
            </div>
            <Button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              + New {activeTab === "relations" ? "Relation" : "Rule"}
            </Button>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-slate-800 overflow-x-auto scrollbar-thin pb-2">
            <button
              onClick={() => setActiveTab("relations")}
              className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                activeTab === "relations"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Relation Tuples
            </button>
            <button
              onClick={() => setActiveTab("rules")}
              className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                activeTab === "rules"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Policy Rules
            </button>
          </div>

          {/* Relations Tab */}
          {activeTab === "relations" && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Relation Tuples ({relations.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-slate-400 text-center py-8">Loading...</div>
                ) : relations.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-slate-700">
                          <th className="text-left p-3 text-slate-400">Subject</th>
                          <th className="text-left p-3 text-slate-400">Relation</th>
                          <th className="text-left p-3 text-slate-400">Object</th>
                          <th className="text-left p-3 text-slate-400">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {relations.map((rel) => (
                          <tr key={rel.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                            <td className="p-3">
                              <div className="text-slate-200">
                                <span className="text-blue-400">{rel.subject_type}</span>
                                <span className="text-slate-500 mx-1">:</span>
                                <span className="text-slate-300">{rel.subject_id}</span>
                              </div>
                            </td>
                            <td className="p-3">
                              <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
                                {rel.relation}
                              </span>
                            </td>
                            <td className="p-3">
                              <div className="text-slate-200">
                                <span className="text-blue-400">{rel.object_type}</span>
                                <span className="text-slate-500 mx-1">:</span>
                                <span className="text-slate-300">{rel.object_id}</span>
                              </div>
                            </td>
                            <td className="p-3">
                              <span className={`px-2 py-1 rounded text-xs ${
                                rel.is_active
                                  ? "bg-green-500/20 text-green-400"
                                  : "bg-red-500/20 text-red-400"
                              }`}>
                                {rel.is_active ? "Active" : "Inactive"}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-slate-500 text-center py-8">No relation tuples found</div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Rules Tab */}
          {activeTab === "rules" && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Policy Rules ({rules.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-slate-400 text-center py-8">Loading...</div>
                ) : rules.length > 0 ? (
                  <div className="space-y-3">
                    {rules.map((rule) => (
                      <div
                        key={rule.id}
                        className="p-4 bg-slate-800 rounded border-l-4 border-blue-500"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="font-semibold text-lg">{rule.name}</div>
                            {rule.description && (
                              <div className="text-sm text-slate-400 mt-1">{rule.description}</div>
                            )}
                            <div className="flex gap-2 mt-3">
                              {rule.resource_type && (
                                <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                                  {rule.resource_type}
                                </span>
                              )}
                              <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
                                Priority: {rule.priority}
                              </span>
                              <span className={`px-2 py-1 rounded text-xs ${
                                rule.is_active
                                  ? "bg-green-500/20 text-green-400"
                                  : "bg-red-500/20 text-red-400"
                              }`}>
                                {rule.is_active ? "Active" : "Inactive"}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-slate-500 text-center py-8">No policy rules found</div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Create Modal */}
          {showCreateModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <Card className="bg-slate-900 border-slate-800 w-full max-w-md">
                <CardHeader>
                  <CardTitle>
                    Create New {activeTab === "relations" ? "Relation Tuple" : "Policy Rule"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {activeTab === "relations" ? (
                      <>
                        <div>
                          <label className="text-sm text-slate-400">Subject Type</label>
                          <Input
                            placeholder="e.g., user, group"
                            className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-sm text-slate-400">Subject ID</label>
                          <Input
                            placeholder="Subject identifier"
                            className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-sm text-slate-400">Relation</label>
                          <Input
                            placeholder="e.g., owner, member, viewer"
                            className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-sm text-slate-400">Object Type</label>
                          <Input
                            placeholder="e.g., project, workflow"
                            className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-sm text-slate-400">Object ID</label>
                          <Input
                            placeholder="Object identifier"
                            className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                          />
                        </div>
                      </>
                    ) : (
                      <>
                        <div>
                          <label className="text-sm text-slate-400">Rule Name</label>
                          <Input
                            placeholder="Rule name"
                            className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-sm text-slate-400">Description</label>
                          <Input
                            placeholder="Rule description"
                            className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-sm text-slate-400">Priority</label>
                          <Input
                            type="number"
                            placeholder="0"
                            className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                          />
                        </div>
                      </>
                    )}
                    <div className="flex gap-2">
                      <Button
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                        onClick={() => {
                          alert("Create functionality coming soon");
                          setShowCreateModal(false);
                        }}
                      >
                        Create
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1 border-slate-700 text-slate-300"
                        onClick={() => setShowCreateModal(false)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

