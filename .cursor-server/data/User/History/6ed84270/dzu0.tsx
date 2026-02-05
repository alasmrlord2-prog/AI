"use client";

import { useEffect, useState } from "react";
import { accessApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

type Role = {
  id: string;
  name: string;
  description?: string;
  is_system: boolean;
  is_active: boolean;
  created_at: string;
  permissions?: Array<{
    id: string;
    name: string;
    resource: string;
    action: string;
  }>;
};

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchRoles();
    const interval = setInterval(fetchRoles, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const data = await accessApi.getRoles();
      setRoles(data || []);
    } catch (error) {
      console.error("Error fetching roles:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRoles = roles.filter((role) =>
    role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    role.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Header */}
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold">IAM - Roles</h1>
              <p className="text-slate-400 mt-1">Manage roles and permissions</p>
            </div>
            <Button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              + New Role
            </Button>
          </div>

          {/* Search */}
          <Input
            placeholder="Search roles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-slate-900 border-slate-700 text-slate-200"
          />

          {/* Roles List */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>Roles ({filteredRoles.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-slate-400 text-center py-8">Loading...</div>
              ) : filteredRoles.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredRoles.map((role) => (
                    <div
                      key={role.id}
                      className="p-4 bg-slate-800 rounded border-l-4 border-blue-500"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-semibold text-lg">{role.name}</div>
                        {role.is_system && (
                          <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
                            System
                          </span>
                        )}
                      </div>
                      {role.description && (
                        <div className="text-sm text-slate-400 mb-3">{role.description}</div>
                      )}
                      <div className="flex gap-2 mt-3">
                        <span className={`px-2 py-1 rounded text-xs ${
                          role.is_active
                            ? "bg-green-500/20 text-green-400"
                            : "bg-red-500/20 text-red-400"
                        }`}>
                          {role.is_active ? "Active" : "Inactive"}
                        </span>
                        {role.permissions && role.permissions.length > 0 && (
                          <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                            {role.permissions.length} permissions
                          </span>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        className="w-full mt-3 text-slate-300 hover:text-slate-100"
                        onClick={() => {
                          // TODO: Navigate to role details
                          alert("Role details coming soon");
                        }}
                      >
                        View Details →
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-slate-500 text-center py-8">No roles found</div>
              )}
            </CardContent>
          </Card>

          {/* Create Role Modal */}
          {showCreateModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <Card className="bg-slate-900 border-slate-800 w-full max-w-md">
                <CardHeader>
                  <CardTitle>Create New Role</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-slate-400">Role Name</label>
                      <Input
                        placeholder="e.g., Developer, Viewer"
                        className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-400">Description</label>
                      <Input
                        placeholder="Role description"
                        className="bg-slate-800 border-slate-700 text-slate-200 mt-1"
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                        onClick={() => {
                          // TODO: Implement create role
                          alert("Create role functionality coming soon");
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

