"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { identityApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Key, Plus, Trash2, Eye, EyeOff } from "lucide-react";

type ApiToken = {
  id: string;
  name: string;
  user_id: string;
  tenant_id?: string;
  scopes: string[];
  expires_at?: string;
  created_at: string;
  last_used_at?: string;
  is_active: boolean;
};

export default function TokensPage() {
  const router = useRouter();
  const [tokens, setTokens] = useState<ApiToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTokenName, setNewTokenName] = useState("");
  const [newTokenExpires, setNewTokenExpires] = useState("");
  const [createdToken, setCreatedToken] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/aaa/login");
      return;
    }
    fetchTokens();
    const interval = setInterval(fetchTokens, 30000);
    return () => clearInterval(interval);
  }, [router]);

  const fetchTokens = async () => {
    try {
      setLoading(true);
      const data = await identityApi.listApiTokens();
      setTokens(data || []);
    } catch (error) {
      console.error("Error fetching tokens:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateToken = async () => {
    try {
      const expiresAt = newTokenExpires ? new Date(newTokenExpires).toISOString() : undefined;
      const response = await identityApi.createApiToken({
        name: newTokenName,
        scopes: ["read", "write"],
        expires_at: expiresAt,
      });

      if (response.plain_token) {
        setCreatedToken(response.plain_token);
        setNewTokenName("");
        setNewTokenExpires("");
        fetchTokens();
      }
    } catch (error) {
      console.error("Error creating token:", error);
      alert("Failed to create token");
    }
  };

  const handleRevokeToken = async (tokenId: string) => {
    if (!confirm("Are you sure you want to revoke this token?")) return;
    try {
      await identityApi.revokeApiToken(tokenId);
      fetchTokens();
    } catch (error) {
      console.error("Error revoking token:", error);
      alert("Failed to revoke token");
    }
  };

  const getStatus = (token: ApiToken) => {
    if (!token.is_active) return { text: "Revoked", color: "text-red-600 bg-red-50" };
    if (token.expires_at && new Date(token.expires_at) < new Date()) {
      return { text: "Expired", color: "text-orange-600 bg-orange-50" };
    }
    return { text: "Valid", color: "text-green-600 bg-green-50" };
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Issued Tokens</h1>
          <p className="text-gray-500 mt-1">Manage API tokens and access keys</p>
        </div>
        <Button
          onClick={() => setShowCreateModal(true)}
          className="bg-swAuth-primary hover:bg-swAuth-primary/90 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Token
        </Button>
      </div>

      {/* Created Token Modal */}
      {createdToken && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-green-900 mb-2">Token Created Successfully!</h3>
                <p className="text-sm text-green-700 mb-3">
                  Store this token securely - it won't be shown again.
                </p>
                <div className="bg-white p-3 rounded border border-green-200 font-mono text-sm break-all">
                  {createdToken}
                </div>
              </div>
              <Button
                variant="ghost"
                onClick={() => setCreatedToken(null)}
                className="text-green-700 hover:text-green-900"
              >
                ×
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tokens Table */}
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="text-gray-900">Tokens ({tokens.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-gray-500 text-center py-8">Loading...</div>
          ) : tokens.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-200">
                    <th className="pb-3">Name</th>
                    <th className="pb-3">User</th>
                    <th className="pb-3">Scopes</th>
                    <th className="pb-3">Created</th>
                    <th className="pb-3">Expires</th>
                    <th className="pb-3">Last Used</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tokens.map((token) => {
                    const status = getStatus(token);
                    return (
                      <tr key={token.id} className="border-t border-gray-200 hover:bg-gray-50">
                        <td className="py-3 font-medium text-gray-900">{token.name}</td>
                        <td className="py-3 text-gray-600">{token.user_id.substring(0, 8)}...</td>
                        <td className="py-3">
                          <div className="flex gap-1">
                            {token.scopes.map((scope) => (
                              <span
                                key={scope}
                                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                              >
                                {scope}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="py-3 text-gray-600">
                          {new Date(token.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-3 text-gray-600">
                          {token.expires_at
                            ? new Date(token.expires_at).toLocaleDateString()
                            : "Never"}
                        </td>
                        <td className="py-3 text-gray-600">
                          {token.last_used_at
                            ? new Date(token.last_used_at).toLocaleDateString()
                            : "Never"}
                        </td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${status.color}`}>
                            {status.text}
                          </span>
                        </td>
                        <td className="py-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRevokeToken(token.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">No tokens found</div>
          )}
        </CardContent>
      </Card>

      {/* Create Token Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="bg-white border border-gray-200 w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-gray-900">Create New Token</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-700 mb-1 block">Token Name</label>
                  <input
                    type="text"
                    placeholder="e.g., Production API Key"
                    value={newTokenName}
                    onChange={(e) => setNewTokenName(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg text-gray-900"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-700 mb-1 block">Expires At (Optional)</label>
                  <input
                    type="datetime-local"
                    value={newTokenExpires}
                    onChange={(e) => setNewTokenExpires(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg text-gray-900"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    className="flex-1 bg-swAuth-primary hover:bg-swAuth-primary/90 text-white"
                    onClick={handleCreateToken}
                    disabled={!newTokenName}
                  >
                    Create
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1 border-gray-300 text-gray-700"
                    onClick={() => {
                      setShowCreateModal(false);
                      setNewTokenName("");
                      setNewTokenExpires("");
                    }}
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
  );
}

