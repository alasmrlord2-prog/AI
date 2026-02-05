"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { API_URL } from "@/lib/api";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIncidents();
  }, []);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/incidents?limit=50`);
      if (res.ok) {
        const data = await res.json();
        setIncidents(data.incidents || []);
      }
    } catch (err) {
      console.error("Error fetching incidents:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open": return "bg-red-100 text-red-800";
      case "resolved": return "bg-green-100 text-green-800";
      case "investigating": return "bg-yellow-100 text-yellow-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Incident Management</h1>

            <Card>
              <CardHeader>
                <CardTitle>Incidents</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : incidents.length === 0 ? (
                  <p className="text-gray-500">No incidents found</p>
                ) : (
                  <div className="space-y-3">
                    {incidents.map((incident) => (
                      <div key={incident.id} className="p-4 bg-gray-50 rounded border">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="font-semibold text-lg">{incident.title}</div>
                            <div className="text-sm text-gray-600 mt-1">
                              {incident.description}
                            </div>
                            <div className="text-xs text-gray-500 mt-2">
                              Detected: {incident.detected_at && new Date(incident.detected_at).toLocaleString()}
                              {incident.resolved_at && ` | Resolved: ${new Date(incident.resolved_at).toLocaleString()}`}
                            </div>
                            {incident.root_cause && (
                              <div className="mt-2 text-sm">
                                <span className="font-semibold">Root Cause:</span> {incident.root_cause}
                              </div>
                            )}
                          </div>
                          <div className="ml-4">
                            <span className={`px-2 py-1 rounded text-xs ${getStatusColor(incident.status)}`}>
                              {incident.status}
                            </span>
                            <div className="text-xs text-gray-500 mt-1">
                              {incident.severity}
                            </div>
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

