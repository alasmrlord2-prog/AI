"use client";

import { useEffect, useState, useCallback } from "react";
import { crmApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

type AuditLog = {
  id: string;
  action: string;
  resource_type?: string;
  resource_id?: string;
  feature_key?: string;
  user_id?: string;
  ip_address?: string;
  user_agent?: string;
  endpoint?: string;
  status: string;
  error_message?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
};

type TenantAuditLogs = {
  tenant_id: string;
  tenant_name: string;
  logs: AuditLog[];
  total: number;
};

export default function AuditPage() {
  const [auditLogs, setAuditLogs] = useState<TenantAuditLogs[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [limit] = useState(50);
  const [offset] = useState(0);

  const fetchAuditLogs = useCallback(async () => {
    try {
      setLoading(true);
      // Get all tenants first
      const tenantsResponse = await crmApi.listTenants(1000, 0);
      const tenants = tenantsResponse.tenants || [];
      
      // Get audit logs for each tenant
      const logsByTenant: TenantAuditLogs[] = [];
      for (const tenant of tenants) {
        try {
          const logsResponse = await crmApi.getTenantAuditLogs(tenant.id, {
            limit,
            offset,
          });
          if (logsResponse.logs && logsResponse.logs.length > 0) {
            logsByTenant.push({
              tenant_id: tenant.id,
              tenant_name: tenant.name,
              logs: logsResponse.logs,
              total: logsResponse.total || 0,
            });
          }
        } catch (error) {
          console.error(`Error fetching audit logs for tenant ${tenant.id}:`, error);
        }
      }
      
      setAuditLogs(logsByTenant);
    } catch (error) {
      console.error("Error fetching audit logs:", error);
    } finally {
      setLoading(false);
    }
  }, [limit, offset]);

  useEffect(() => {
    fetchAuditLogs();
    const interval = setInterval(fetchAuditLogs, 30000);
    return () => clearInterval(interval);
  }, [fetchAuditLogs]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-500/20 text-green-400";
      case "failed":
      case "error":
        return "bg-red-500/20 text-red-400";
      default:
        return "bg-slate-500/20 text-slate-400";
    }
  };

  const filteredLogs = auditLogs.flatMap(tenantLogs =>
    tenantLogs.logs
      .filter(log =>
        log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (log.resource_type && log.resource_type.toLowerCase().includes(searchTerm.toLowerCase())) ||
        tenantLogs.tenant_name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .map(log => ({ ...log, tenant_id: tenantLogs.tenant_id, tenant_name: tenantLogs.tenant_name }))
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-sw-text">Audit Logs</h2>
          <p className="text-sw-text-muted mt-1">View audit logs across all tenants</p>
        </div>
      </div>

      {/* Search */}
      <div className="flex gap-4">
        <Input
          placeholder="Search by action, resource type, or tenant..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-sw-surface border-sw-border text-sw-text"
        />
      </div>

      {/* Audit Logs */}
      <Card className="bg-sw-bg-card border-sw-border">
        <CardHeader>
          <CardTitle className="text-sw-text-strong">
            Audit Logs ({filteredLogs.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading && auditLogs.length === 0 ? (
            <div className="text-sw-text-muted text-center py-8">Loading...</div>
          ) : filteredLogs.length > 0 ? (
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {filteredLogs.map((log) => (
                <div
                  key={log.id}
                  className="p-4 bg-slate-800 rounded border-l-4 border-blue-500 hover:bg-slate-750 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-semibold text-sw-text">{log.action}</div>
                      <div className="text-sm text-slate-400 mt-1">
                        Tenant: {log.tenant_name}
                        {log.resource_type && ` • Resource: ${log.resource_type}`}
                        {log.resource_id && ` • Resource ID: ${log.resource_id}`}
                        {log.feature_key && ` • Feature: ${log.feature_key}`}
                        {log.endpoint && ` • Endpoint: ${log.endpoint}`}
                      </div>
                      {log.user_id && (
                        <div className="text-xs text-slate-500 mt-1">User ID: {log.user_id}</div>
                      )}
                      {log.ip_address && (
                        <div className="text-xs text-slate-500 mt-1">IP: {log.ip_address}</div>
                      )}
                      {log.error_message && (
                        <div className="text-xs text-red-400 mt-1">Error: {log.error_message}</div>
                      )}
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <span className={`px-2 py-1 rounded-lg text-xs ${getStatusColor(log.status)}`}>
                        {log.status}
                      </span>
                      <div className="text-xs text-slate-500">
                        {new Date(log.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-500 text-center py-8">No audit logs found</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

