"use client";

import { useEffect, useState } from "react";
import { accessApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

type Permission = {
  id: string;
  name: string;
  resource: string;
  action: string;
  description?: string;
  is_active: boolean;
};

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterResource, setFilterResource] = useState<string>("all");
  const [filterAction, setFilterAction] = useState<string>("all");

  useEffect(() => {
    fetchPermissions();
    const interval = setInterval(fetchPermissions, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchPermissions = async () => {
    try {
      setLoading(true);
      const data = await accessApi.getPermissions();
      setPermissions(data || []);
    } catch (error) {
      console.error("Error fetching permissions:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredPermissions = permissions.filter((perm) => {
    const matchesSearch = perm.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      perm.resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
      perm.action.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesResource = filterResource === "all" || perm.resource === filterResource;
    const matchesAction = filterAction === "all" || perm.action === filterAction;
    return matchesSearch && matchesResource && matchesAction;
  });

  const resources = Array.from(new Set(permissions.map((p) => p.resource)));
  const actions = Array.from(new Set(permissions.map((p) => p.action)));

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Header */}
          <div>
            <h1 className="text-2xl md:text-3xl font-bold">IAM - Permissions</h1>
            <p className="text-slate-400 mt-1">Permission matrix and management</p>
          </div>

          {/* Filters */}
          <div className="flex gap-4 flex-wrap">
            <Input
              placeholder="Search permissions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900 border-slate-700 text-slate-200 flex-1 min-w-[200px]"
            />
            <select
              value={filterResource}
              onChange={(e) => setFilterResource(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-3 py-2"
            >
              <option value="all">All Resources</option>
              {resources.map((resource) => (
                <option key={resource} value={resource}>
                  {resource}
                </option>
              ))}
            </select>
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-3 py-2"
            >
              <option value="all">All Actions</option>
              {actions.map((action) => (
                <option key={action} value={action}>
                  {action}
                </option>
              ))}
            </select>
          </div>

          {/* Permissions Matrix */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>Permissions ({filteredPermissions.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-slate-400 text-center py-8">Loading...</div>
              ) : filteredPermissions.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left p-3 text-slate-400">Name</th>
                        <th className="text-left p-3 text-slate-400">Resource</th>
                        <th className="text-left p-3 text-slate-400">Action</th>
                        <th className="text-left p-3 text-slate-400">Description</th>
                        <th className="text-left p-3 text-slate-400">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredPermissions.map((perm) => (
                        <tr key={perm.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                          <td className="p-3">
                            <div className="font-medium text-slate-200">{perm.name}</div>
                          </td>
                          <td className="p-3">
                            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                              {perm.resource}
                            </span>
                          </td>
                          <td className="p-3">
                            <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
                              {perm.action}
                            </span>
                          </td>
                          <td className="p-3 text-slate-400 text-sm">
                            {perm.description || "—"}
                          </td>
                          <td className="p-3">
                            <span className={`px-2 py-1 rounded text-xs ${
                              perm.is_active
                                ? "bg-green-500/20 text-green-400"
                                : "bg-red-500/20 text-red-400"
                            }`}>
                              {perm.is_active ? "Active" : "Inactive"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-slate-500 text-center py-8">No permissions found</div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

