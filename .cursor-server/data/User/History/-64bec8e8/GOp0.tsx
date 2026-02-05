"use client";
import { apiRequest } from "@/lib/api";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function CICDPage() {
  const [repos, setRepos] = useState<any[]>([]);
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCloneForm, setShowCloneForm] = useState(false);
  const [cloneUrl, setCloneUrl] = useState("");
  const [cloneName, setCloneName] = useState("");
  const [cloneBranch, setCloneBranch] = useState("main");
  const [selectedPipeline, setSelectedPipeline] = useState<string | null>(null);
  const [pipelineLogs, setPipelineLogs] = useState<string[]>([]);
  const [showDeployForm, setShowDeployForm] = useState(false);
  const [deployType, setDeployType] = useState("docker-compose");
  const [deployFile, setDeployFile] = useState("");

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedPipeline) {
      fetchPipelineLogs(selectedPipeline);
      const interval = setInterval(() => fetchPipelineLogs(selectedPipeline), 3000);
      return () => clearInterval(interval);
    }
  }, [selectedPipeline]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [reposData, pipelinesData] = await Promise.all([
        apiRequest("/api/cicd/repos", {}, 5000).catch(() => ({ repos: [] })),
        apiRequest("/api/cicd/pipelines", {}, 5000).catch(() => ({ pipelines: [] }))
      ]);

      setRepos(reposData.repos || []);
      setPipelines(pipelinesData.pipelines || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClone = async () => {
    if (!cloneUrl || !cloneName) {
      setError("يرجى إدخال URL واسم المستودع");
      return;
    }

    try {
      await apiRequest("/api/cicd/clone", {
        method: "POST",
        body: JSON.stringify({
          repo_url: cloneUrl,
          repo_name: cloneName,
          branch: cloneBranch
        })
      }, 30000); // 30s timeout for clone
      
      setShowCloneForm(false);
      setCloneUrl("");
      setCloneName("");
      fetchData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleRunPipeline = async (repoName: string) => {
    try {
      await apiRequest("/api/cicd/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_name: repoName })
      });

      if (res.ok) {
        fetchData();
      } else {
        const data = await res.json();
        setError(data.detail || "فشل تشغيل Pipeline");
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handlePull = async (repoName: string) => {
    try {
      await apiRequest("/api/cicd/pull`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_name: repoName, branch: "main" })
      });

      if (res.ok) {
        fetchData();
      } else {
        const data = await res.json();
        setError(data.detail || "فشل Pull");
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const fetchPipelineLogs = async (pipelineId: string) => {
    try {
      const data = await apiRequest("/api/cicd/logs/${pipelineId}?tail=100`);
      if (res.ok) {
        const data = await res.json();
        setPipelineLogs(data.logs || []);
      }
    } catch (err) {
      console.error("Error fetching pipeline logs:", err);
    }
  };

  const handleDeploy = async () => {
    if (!deployFile) {
      setError("يرجى إدخال مسار الملف");
      return;
    }

    try {
      let endpoint = "";
      let body: any = {};

      if (deployType === "docker-compose") {
        endpoint = "/api/cicd/deploy/docker-compose`;
        body = { compose_file: deployFile };
      } else if (deployType === "kubernetes") {
        endpoint = "/api/cicd/deploy/kubernetes`;
        body = { manifest_file: deployFile };
      } else if (deployType === "rsync") {
        endpoint = "/api/cicd/deploy/rsync`;
        body = { source: deployFile, destination: "/var/www/html" };
      }

      const data = await apiRequest(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      if (res.ok) {
        setShowDeployForm(false);
        setDeployFile("");
        alert("تم Deploy بنجاح!");
      } else {
        const data = await res.json();
        setError(data.detail || "فشل Deploy");
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleRollback = async (pipelineId: string) => {
    if (!confirm("هل أنت متأكد من Rollback?")) return;

    try {
      await apiRequest("/api/cicd/rollback/${pipelineId}`, {
        method: "POST"
      });

      if (res.ok) {
        alert("تم Rollback بنجاح!");
        fetchData();
      } else {
        const data = await res.json();
        setError(data.detail || "فشل Rollback");
      }
    } catch (err: any) {
      setError(err.message);
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
              <h1 className="text-3xl font-bold text-slate-800">🚀 CI/CD Pipeline</h1>
              <div className="flex gap-2">
                <Button 
                  onClick={() => setShowDeployForm(!showDeployForm)}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  {showDeployForm ? "إلغاء" : "🚢 Deploy"}
                </Button>
                <Button 
                  onClick={() => setShowCloneForm(!showCloneForm)}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {showCloneForm ? "إلغاء" : "+ Clone Repository"}
                </Button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            {showDeployForm && (
              <Card className="mb-6 border-purple-200 bg-purple-50">
                <CardHeader>
                  <CardTitle className="text-purple-800">Deploy Application</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="deployType">Deployment Type</Label>
                    <select
                      id="deployType"
                      value={deployType}
                      onChange={(e) => setDeployType(e.target.value)}
                      className="w-full mt-1 p-2 border rounded"
                    >
                      <option value="docker-compose">Docker Compose</option>
                      <option value="kubernetes">Kubernetes</option>
                      <option value="rsync">RSync</option>
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="deployFile">
                      {deployType === "docker-compose" ? "Compose File Path" :
                       deployType === "kubernetes" ? "Manifest File Path" :
                       "Source Path"}
                    </Label>
                    <Input
                      id="deployFile"
                      value={deployFile}
                      onChange={(e) => setDeployFile(e.target.value)}
                      placeholder={deployType === "docker-compose" ? "/path/to/docker-compose.yml" :
                                   deployType === "kubernetes" ? "/path/to/manifest.yaml" :
                                   "/path/to/source"}
                      className="mt-1"
                    />
                  </div>
                  <Button onClick={handleDeploy} className="w-full bg-purple-600 hover:bg-purple-700">
                    Deploy
                  </Button>
                </CardContent>
              </Card>
            )}

            {showCloneForm && (
              <Card className="mb-6 border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="text-blue-800">Clone New Repository</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="cloneUrl">Repository URL</Label>
                    <Input
                      id="cloneUrl"
                      value={cloneUrl}
                      onChange={(e) => setCloneUrl(e.target.value)}
                      placeholder="https://github.com/user/repo.git"
                      className="mt-1"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="cloneName">Repository Name</Label>
                      <Input
                        id="cloneName"
                        value={cloneName}
                        onChange={(e) => setCloneName(e.target.value)}
                        placeholder="my-repo"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="cloneBranch">Branch</Label>
                      <Input
                        id="cloneBranch"
                        value={cloneBranch}
                        onChange={(e) => setCloneBranch(e.target.value)}
                        placeholder="main"
                        className="mt-1"
                      />
                    </div>
                  </div>
                  <Button onClick={handleClone} className="w-full bg-blue-600 hover:bg-blue-700">
                    Clone
                  </Button>
                </CardContent>
              </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-t-lg">
                  <CardTitle className="text-white">Repositories</CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  {loading ? (
                    <p className="text-slate-500">جاري التحميل...</p>
                  ) : repos.length === 0 ? (
                    <p className="text-slate-500 text-center py-8">لا توجد مستودعات</p>
                  ) : (
                    <div className="space-y-3">
                      {repos.map((repo) => (
                        <div key={repo.name} className="p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="font-semibold text-slate-800">{repo.name}</div>
                              <div className="text-sm text-slate-600 mt-1">
                                Branch: <span className="font-medium">{repo.branch || "N/A"}</span>
                              </div>
                              {repo.last_commit && (
                                <div className="text-xs text-slate-500 mt-1">
                                  {repo.last_commit.message}
                                </div>
                              )}
                            </div>
                            <div className="flex gap-2 ml-4">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handlePull(repo.name)}
                                className="text-xs"
                              >
                                Pull
                              </Button>
                              <Button
                                size="sm"
                                onClick={() => handleRunPipeline(repo.name)}
                                className="bg-green-600 hover:bg-green-700 text-xs"
                              >
                                Run
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg">
                  <CardTitle className="text-white">Recent Pipelines</CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  {loading ? (
                    <p className="text-slate-500">جاري التحميل...</p>
                  ) : pipelines.length === 0 ? (
                    <p className="text-slate-500 text-center py-8">لا توجد pipelines</p>
                  ) : (
                    <div className="space-y-3">
                      {pipelines.slice(0, 5).map((pipeline) => (
                        <div key={pipeline.id} className="p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200">
                          <div className="flex justify-between items-center">
                            <div className="flex-1">
                              <div className="font-semibold text-slate-800">{pipeline.repo_name}</div>
                              <div className="text-sm text-slate-600 mt-1">
                                Status: <span className={`font-semibold px-2 py-1 rounded ${
                                  pipeline.status === "success" ? "bg-green-100 text-green-700" :
                                  pipeline.status === "failed" ? "bg-red-100 text-red-700" :
                                  pipeline.status === "running" ? "bg-blue-100 text-blue-700" :
                                  "bg-yellow-100 text-yellow-700"
                                }`}>
                                  {pipeline.status}
                                </span>
                              </div>
                              <div className="text-xs text-slate-500 mt-1">
                                {pipeline.started_at && new Date(pipeline.started_at).toLocaleString()}
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setSelectedPipeline(selectedPipeline === pipeline.id ? null : pipeline.id)}
                                className="text-xs"
                              >
                                {selectedPipeline === pipeline.id ? "Hide Logs" : "Logs"}
                              </Button>
                              {pipeline.status === "success" && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleRollback(pipeline.id)}
                                  className="text-xs text-orange-600 hover:text-orange-700"
                                >
                                  Rollback
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

            {selectedPipeline && (
              <Card className="mt-6 border-slate-200 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-t-lg">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-white">Pipeline Logs</CardTitle>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setSelectedPipeline(null)}
                      className="text-white border-white hover:bg-white hover:text-gray-600"
                    >
                      ✕ Close
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="bg-slate-900 text-green-400 p-4 rounded font-mono text-sm max-h-96 overflow-y-auto">
                    {pipelineLogs.length === 0 ? (
                      <p className="text-slate-500">جاري تحميل الـ logs...</p>
                    ) : (
                      pipelineLogs.map((log, idx) => (
                        <div key={idx} className="mb-1">{log}</div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

