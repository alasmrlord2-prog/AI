"use client";

import { useState } from "react";
import { policyApi, accessApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

export default function AccessControlPage() {
  const [testType, setTestType] = useState<"relation" | "permission">("relation");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Relation test fields
  const [subjectType, setSubjectType] = useState("user");
  const [subjectId, setSubjectId] = useState("");
  const [objectType, setObjectType] = useState("project");
  const [objectId, setObjectId] = useState("");
  const [relation, setRelation] = useState("owner");
  const [tenantId, setTenantId] = useState("");

  // Permission test fields
  const [userId, setUserId] = useState("");
  const [resource, setResource] = useState("dashboard");
  const [action, setAction] = useState("read");

  const handleRelationTest = async () => {
    try {
      setLoading(true);
      setResult(null);
      const checkData = {
        subject_type: subjectType,
        subject_id: subjectId,
        object_type: objectType,
        object_id: objectId,
        relation: relation,
        tenant_id: tenantId || undefined,
      };
      const response = await policyApi.checkRelation(checkData);
      setResult(response);
    } catch (error: any) {
      setResult({
        allowed: false,
        reason: error.message || "Error checking relation",
        error: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePermissionTest = async () => {
    try {
      setLoading(true);
      setResult(null);
      // TODO: Implement permission check via access API
      // For now, show placeholder
      setResult({
        allowed: false,
        reason: "Permission check functionality coming soon",
        error: false,
      });
    } catch (error: any) {
      setResult({
        allowed: false,
        reason: error.message || "Error checking permission",
        error: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Header */}
          <div>
            <h1 className="text-2xl md:text-3xl font-bold">IAM - Access Control Testing</h1>
            <p className="text-slate-400 mt-1">Test permissions and relations</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Test Form */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Test Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Test Type Selector */}
                <div>
                  <label className="text-sm text-slate-400 mb-2 block">Test Type</label>
                  <div className="flex gap-2">
                    <Button
                      variant={testType === "relation" ? "default" : "outline"}
                      onClick={() => setTestType("relation")}
                      className={testType === "relation" ? "bg-blue-600" : "border-slate-700"}
                    >
                      Relation Check
                    </Button>
                    <Button
                      variant={testType === "permission" ? "default" : "outline"}
                      onClick={() => setTestType("permission")}
                      className={testType === "permission" ? "bg-blue-600" : "border-slate-700"}
                    >
                      Permission Check
                    </Button>
                  </div>
                </div>

                {/* Relation Test Form */}
                {testType === "relation" && (
                  <>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">Subject Type</label>
                      <Input
                        value={subjectType}
                        onChange={(e) => setSubjectType(e.target.value)}
                        placeholder="e.g., user, group"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">Subject ID</label>
                      <Input
                        value={subjectId}
                        onChange={(e) => setSubjectId(e.target.value)}
                        placeholder="Subject identifier"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">Relation</label>
                      <Input
                        value={relation}
                        onChange={(e) => setRelation(e.target.value)}
                        placeholder="e.g., owner, member, viewer"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">Object Type</label>
                      <Input
                        value={objectType}
                        onChange={(e) => setObjectType(e.target.value)}
                        placeholder="e.g., project, workflow"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">Object ID</label>
                      <Input
                        value={objectId}
                        onChange={(e) => setObjectId(e.target.value)}
                        placeholder="Object identifier"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">Tenant ID (Optional)</label>
                      <Input
                        value={tenantId}
                        onChange={(e) => setTenantId(e.target.value)}
                        placeholder="Tenant identifier"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <Button
                      onClick={handleRelationTest}
                      disabled={loading || !subjectId || !objectId}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      {loading ? "Testing..." : "Test Relation"}
                    </Button>
                  </>
                )}

                {/* Permission Test Form */}
                {testType === "permission" && (
                  <>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">User ID</label>
                      <Input
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        placeholder="User identifier"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">Resource</label>
                      <Input
                        value={resource}
                        onChange={(e) => setResource(e.target.value)}
                        placeholder="e.g., dashboard, workflow"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-slate-400 mb-1 block">Action</label>
                      <Input
                        value={action}
                        onChange={(e) => setAction(e.target.value)}
                        placeholder="e.g., read, write, delete"
                        className="bg-slate-800 border-slate-700 text-slate-200"
                      />
                    </div>
                    <Button
                      onClick={handlePermissionTest}
                      disabled={loading || !userId}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      {loading ? "Testing..." : "Test Permission"}
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Result */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>Test Result</CardTitle>
              </CardHeader>
              <CardContent>
                {result ? (
                  <div className="space-y-4">
                    <div className={`p-4 rounded border-2 ${
                      result.allowed
                        ? "bg-green-500/10 border-green-500/50"
                        : result.error
                        ? "bg-red-500/10 border-red-500/50"
                        : "bg-red-500/10 border-red-500/50"
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-3 h-3 rounded-full ${
                          result.allowed ? "bg-green-500" : "bg-red-500"
                        }`} />
                        <span className="font-semibold text-lg">
                          {result.allowed ? "Access Granted" : "Access Denied"}
                        </span>
                      </div>
                      <div className="text-slate-300 text-sm">{result.reason}</div>
                    </div>

                    {result.matched_tuples && result.matched_tuples.length > 0 && (
                      <div>
                        <div className="text-slate-400 text-sm mb-2">Matched Tuples:</div>
                        <div className="space-y-1">
                          {result.matched_tuples.map((tupleId: string, idx: number) => (
                            <div key={idx} className="text-xs text-slate-500 font-mono bg-slate-800 p-2 rounded">
                              {tupleId}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {result.paths && result.paths.length > 0 && (
                      <div>
                        <div className="text-slate-400 text-sm mb-2">Paths Found:</div>
                        <div className="space-y-1">
                          {result.paths.map((path: string[], idx: number) => (
                            <div key={idx} className="text-xs text-slate-500 font-mono bg-slate-800 p-2 rounded">
                              {path.join(" → ")}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="pt-4 border-t border-slate-800">
                      <div className="text-xs text-slate-500">
                        <div>Relation Type: {result.relation_type || "N/A"}</div>
                        {result.matched_rules && result.matched_rules.length > 0 && (
                          <div className="mt-1">
                            Matched Rules: {result.matched_rules.join(", ")}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-slate-500 text-center py-8">
                    Run a test to see results here
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}

