"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("medium");

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const data = await apiRequest("/api/incidents?limit=50", {}, 5000);
      setIncidents(data.incidents || []);
    } catch (err) {
      console.error("Error fetching incidents:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateIncident = async () => {
    if (!title || !description) {
      alert("يرجى إدخال العنوان والوصف");
      return;
    }

    try {
      await apiRequest("/api/incidents", {
        method: "POST",
        body: JSON.stringify({ title, description, severity })
      }, 10000);
      
      setShowCreateForm(false);
      setTitle("");
      setDescription("");
      setSeverity("medium");
      fetchIncidents();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleResolve = async (incidentId: string) => {
    const rootCause = prompt("أدخل Root Cause (اختياري):");
    try {
      await apiRequest(`/api/incidents/${incidentId}/resolve`, {
        method: "POST",
        body: JSON.stringify({ root_cause: rootCause || null })
      }, 5000);
      
      fetchIncidents();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleUpdateIncident = async (incidentId: string, status: string) => {
    try {
      await apiRequest(`/api/incidents/${incidentId}`, {
        method: "PUT",
        body: JSON.stringify({ status }),
        body: JSON.stringify({ status })
      });

      if (res.ok) {
        fetchIncidents();
      } else {
        const data = await res.json();
        alert(data.detail || "فشل التحديث");
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open": return "bg-red-100 text-red-700 border-red-300";
      case "resolved": return "bg-green-100 text-green-700 border-green-300";
      case "investigating": return "bg-yellow-100 text-yellow-700 border-yellow-300";
      default: return "bg-gray-100 text-gray-700 border-gray-300";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-500";
      case "high": return "bg-orange-500";
      case "medium": return "bg-yellow-500";
      default: return "bg-blue-500";
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
              <h1 className="text-3xl font-bold text-slate-800">🚨 Incident Management</h1>
              <Button 
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-red-600 hover:bg-red-700"
              >
                {showCreateForm ? "إلغاء" : "+ Create Incident"}
              </Button>
            </div>

            {showCreateForm && (
              <Card className="mb-6 border-red-200 bg-red-50">
                <CardHeader>
                  <CardTitle className="text-red-800">Create New Incident</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Incident title"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Description</Label>
                    <textarea
                      id="description"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Incident description"
                      className="w-full mt-1 p-2 border rounded"
                      rows={4}
                    />
                  </div>
                  <div>
                    <Label htmlFor="severity">Severity</Label>
                    <select
                      id="severity"
                      value={severity}
                      onChange={(e) => setSeverity(e.target.value)}
                      className="w-full mt-1 p-2 border rounded"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  <Button onClick={handleCreateIncident} className="w-full bg-red-600 hover:bg-red-700">
                    Create Incident
                  </Button>
                </CardContent>
              </Card>
            )}

            <Card className="border-slate-200 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-red-500 to-red-600 text-white rounded-t-lg">
                <CardTitle className="text-white">Incidents</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {loading ? (
                  <p className="text-slate-500">جاري التحميل...</p>
                ) : incidents.length === 0 ? (
                  <p className="text-slate-500 text-center py-8">لا توجد incidents</p>
                ) : (
                  <div className="space-y-3">
                    {incidents.map((incident) => (
                      <div key={incident.id} className="p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <div className={`w-3 h-3 rounded-full ${getSeverityColor(incident.severity || "medium")}`} />
                              <div className="font-semibold text-lg text-slate-800">{incident.title}</div>
                            </div>
                            <div className="text-sm text-slate-600 mt-1">
                              {incident.description}
                            </div>
                            {incident.root_cause && (
                              <div className="mt-2 text-sm bg-slate-100 p-2 rounded">
                                <span className="font-semibold">Root Cause:</span> {incident.root_cause}
                              </div>
                            )}
                            <div className="text-xs text-slate-500 mt-2">
                              Detected: {incident.detected_at && new Date(incident.detected_at).toLocaleString()}
                              {incident.resolved_at && ` | Resolved: ${new Date(incident.resolved_at).toLocaleString()}`}
                            </div>
                          </div>
                          <div className="ml-4 flex flex-col gap-2">
                            <span className={`px-3 py-1 rounded text-xs font-semibold border ${getStatusColor(incident.status)}`}>
                              {incident.status}
                            </span>
                            {incident.status === "open" && (
                              <Button
                                size="sm"
                                onClick={() => handleUpdateIncident(incident.id, "investigating")}
                                className="bg-yellow-600 hover:bg-yellow-700 text-xs"
                              >
                                Investigating
                              </Button>
                            )}
                            {incident.status !== "resolved" && (
                              <Button
                                size="sm"
                                onClick={() => handleResolve(incident.id)}
                                className="bg-green-600 hover:bg-green-700 text-xs"
                              >
                                Resolve
                              </Button>
                            )}
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
