"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type Incident = {
  id: string;
  title: string;
  description?: string;
  severity: string;
  status: string;
  created_at?: string;
  resolved_at?: string;
};

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("medium");

  const fetchIncidents = useCallback(async () => {
    try {
      // Don't show loading if we already have data - allows fast navigation
      if (incidents.length === 0) {
        setLoading(true);
      }
      const data = await apiRequest("/api/incidents?limit=50", {}, 3000); // Faster timeout
      setIncidents(data.incidents || []);
    } catch (err) {
      console.error("Error fetching incidents:", err);
    } finally {
      setLoading(false);
    }
  }, [incidents.length]);

  useEffect(() => {
    fetchIncidents();
    // Less frequent updates for better performance
    const interval = setInterval(fetchIncidents, 15000); // 15 seconds
    return () => clearInterval(interval);
  }, [fetchIncidents]);

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
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      alert(errorMessage);
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
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      alert(errorMessage);
    }
  };

  const handleUpdateIncident = async (incidentId: string, status: string) => {
    try {
      await apiRequest(`/api/incidents/${incidentId}`, {
        method: "PUT",
        body: JSON.stringify({ status })
      }, 5000);
      
      fetchIncidents();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      alert(errorMessage);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open": return "bg-sw-bg-soft text-sw-blue border-sw-blue";
      case "resolved": return "bg-sw-bg-soft text-sw-teal border-sw-teal";
      case "investigating": return "bg-sw-bg-soft text-sw-secondary border-sw-secondary";
      default: return "bg-sw-bg-soft text-sw-text-muted border-sw-border";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-sw-teal";
      case "high": return "bg-sw-primary-dark";
      case "medium": return "bg-sw-secondary-light";
      default: return "bg-sw-blue";
    }
  };

  return (
    <div className="flex h-screen bg-sw-bg">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold text-sw-text-strong">🚨 Incident Management</h1>
              <Button 
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-sw-blue hover:bg-sw-blue-light"
              >
                {showCreateForm ? "إلغاء" : "+ Create Incident"}
              </Button>
            </div>

            {showCreateForm && (
              <Card className="mb-6 border-sw-border bg-sw-bg-soft">
                <CardHeader>
                  <CardTitle className="text-sw-text-strong">Create New Incident</CardTitle>
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
                  <Button onClick={handleCreateIncident} className="w-full bg-sw-blue hover:bg-sw-blue-light">
                    Create Incident
                  </Button>
                </CardContent>
              </Card>
            )}

            <Card className="border-sw-border shadow-sw-card">
              <CardHeader className="bg-gradient-to-r from-sw-blue to-sw-teal text-sw-text rounded-t-lg">
                <CardTitle className="text-sw-text-strong">Incidents</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {loading ? (
                  <p className="text-sw-text-muted">جاري التحميل...</p>
                ) : incidents.length === 0 ? (
                  <p className="text-sw-text-muted text-center py-8">لا توجد incidents</p>
                ) : (
                  <div className="space-y-3">
                    {incidents.map((incident) => (
                      <div key={incident.id} className="p-4 bg-sw-bg-soft rounded-lg border border-sw-border hover:shadow-sw-card transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <div className={`w-3 h-3 rounded-full ${getSeverityColor(incident.severity || "medium")}`} />
                              <div className="font-semibold text-lg text-sw-text-strong">{incident.title}</div>
                            </div>
                            <div className="text-sm text-sw-text-soft mt-1">
                              {incident.description}
                            </div>
                            {incident.root_cause && (
                              <div className="mt-2 text-sm bg-sw-bg-card p-2 rounded">
                                <span className="font-semibold">Root Cause:</span> {incident.root_cause}
                              </div>
                            )}
                            <div className="text-xs text-sw-text-muted mt-2">
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
                                className="bg-sw-secondary hover:bg-sw-secondary-light text-xs"
                              >
                                Investigating
                              </Button>
                            )}
                            {incident.status !== "resolved" && (
                              <Button
                                size="sm"
                                onClick={() => handleResolve(incident.id)}
                                className="bg-sw-teal hover:bg-sw-teal-light text-xs"
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
