"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Incident = {
  id: string;
  title: string;
  severity: string;
  status: string;
  created_at?: string;
  resolved_at?: string;
};

type TenantIncidents = {
  tenant_id: string;
  tenant_name: string;
  incidents: Incident[];
  total: number;
};

export default function IncidentsPage() {
  const router = useRouter();
  const [incidents, setIncidents] = useState<TenantIncidents[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [limit] = useState(50);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 30000);
    return () => clearInterval(interval);
  }, [offset]);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      // Get all tenants first
      const tenantsResponse = await crmApi.listTenants(1000, 0);
      const tenants = tenantsResponse.tenants || [];
      
      // Get incidents for each tenant
      const incidentsByTenant: TenantIncidents[] = [];
      for (const tenant of tenants) {
        try {
          const incidentsResponse = await crmApi.getTenantIncidents(tenant.id, limit, offset);
          if (incidentsResponse.incidents && incidentsResponse.incidents.length > 0) {
            incidentsByTenant.push({
              tenant_id: tenant.id,
              tenant_name: tenant.name,
              incidents: incidentsResponse.incidents,
              total: incidentsResponse.total || 0,
            });
          }
        } catch (error) {
          console.error(`Error fetching incidents for tenant ${tenant.id}:`, error);
        }
      }
      
      setIncidents(incidentsByTenant);
    } catch (error) {
      console.error("Error fetching incidents:", error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
      case "high":
        return "bg-red-500/20 text-red-400";
      case "medium":
        return "bg-orange-500/20 text-orange-400";
      case "low":
        return "bg-yellow-500/20 text-yellow-400";
      default:
        return "bg-slate-500/20 text-slate-400";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "resolved":
        return "bg-green-500/20 text-green-400";
      case "open":
        return "bg-red-500/20 text-red-400";
      case "in_progress":
        return "bg-blue-500/20 text-blue-400";
      default:
        return "bg-slate-500/20 text-slate-400";
    }
  };

  const filteredIncidents = incidents.flatMap(tenantIncidents =>
    tenantIncidents.incidents
      .filter(incident =>
        incident.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        incident.severity.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tenantIncidents.tenant_name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .map(incident => ({ ...incident, tenant_id: tenantIncidents.tenant_id, tenant_name: tenantIncidents.tenant_name }))
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-sw-text">Incidents</h2>
          <p className="text-sw-text-muted mt-1">View and manage incidents across all tenants</p>
        </div>
      </div>

      {/* Search */}
      <div className="flex gap-4">
        <Input
          placeholder="Search by title, severity, or tenant..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-sw-surface border-sw-border text-sw-text"
        />
      </div>

      {/* Incidents List */}
      <Card className="bg-sw-bg-card border-sw-border">
        <CardHeader>
          <CardTitle className="text-sw-text-strong">
            Incidents ({filteredIncidents.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading && incidents.length === 0 ? (
            <div className="text-sw-text-muted text-center py-8">Loading...</div>
          ) : filteredIncidents.length > 0 ? (
            <div className="space-y-3">
              {filteredIncidents.map((incident) => (
                <div
                  key={incident.id}
                  className="p-4 bg-slate-800 rounded border-l-4 border-red-500 hover:bg-slate-750 cursor-pointer transition-colors"
                  onClick={() => router.push(`/crm/tenants/${incident.tenant_id}`)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-semibold text-lg text-sw-text">{incident.title}</div>
                      <div className="text-sm text-slate-400 mt-1">Tenant: {incident.tenant_name}</div>
                      <div className="flex gap-2 mt-3">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(incident.severity)}`}>
                          {incident.severity}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(incident.status)}`}>
                          {incident.status}
                        </span>
                      </div>
                      {incident.created_at && (
                        <div className="text-xs text-slate-500 mt-2">
                          Created: {new Date(incident.created_at).toLocaleString()}
                        </div>
                      )}
                      {incident.resolved_at && (
                        <div className="text-xs text-green-400 mt-1">
                          Resolved: {new Date(incident.resolved_at).toLocaleString()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-500 text-center py-8">No incidents found</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

