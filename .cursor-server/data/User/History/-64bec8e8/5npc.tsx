"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function DevOpsPage() {
  const searchParams = useSearchParams();
  const tab = searchParams.get("tab") || "cicd";
  
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [runningJobs, setRunningJobs] = useState<any[]>([]);
  const [deployments, setDeployments] = useState<any[]>([]);
  const [shadowDeployments, setShadowDeployments] = useState<any[]>([]);
  const [backups, setBackups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      if (tab === "cicd") {
        const pipelinesData = await apiRequest("/api/cicd/pipelines", {}, 3000).catch(() => ({ pipelines: [] }));
        const allPipelines = pipelinesData.pipelines || [];
        setPipelines(allPipelines);
        // Filter running jobs from pipelines
        setRunningJobs(allPipelines.filter((p: any) => p.status === "running" || p.status === "pending"));
      } else if (tab === "deployments") {
        const [deployData, shadowData] = await Promise.all([
          apiRequest("/api/cicd/deploy/status", {}, 3000).catch(() => ({ deployments: [] })),
          apiRequest("/api/deployment/shadow/", {}, 3000).catch(() => ({ shadows: [] }))
        ]);
        setDeployments(deployData.deployments || deployData.deployment_status || []);
        setShadowDeployments(shadowData.shadows || shadowData.deployments || []);
      } else if (tab === "backup") {
        const backupData = await apiRequest("/api/backup/list", {}, 3000).catch(() => ({ backups: [] }));
        setBackups(backupData.backups || []);
      }
    } catch (err) {
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && pipelines.length === 0 && deployments.length === 0 && backups.length === 0) {
    return (
      <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-slate-400">Loading...</div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          {/* Tabs */}
          <div className="flex gap-2 border-b border-slate-800 overflow-x-auto scrollbar-thin pb-2 -mx-4 md:mx-0 px-4 md:px-0">
            <a
              href="/cicd"
              className={`px-3 md:px-4 py-2 border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                tab === "cicd" || !tab
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              CI/CD
            </a>
            <a
              href="/cicd?tab=deployments"
              className={`px-3 md:px-4 py-2 border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                tab === "deployments"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Deployments
            </a>
            <a
              href="/cicd?tab=backup"
              className={`px-3 md:px-4 py-2 border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                tab === "backup"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Backup & Restore
            </a>
          </div>

          {/* Tab 1: CI/CD */}
          {tab === "cicd" || !tab ? (
            <div className="space-y-6">
              {/* Pipelines */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Pipelines</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {pipelines.length > 0 ? (
                      pipelines.map((pipeline, idx) => (
                        <div key={`pipeline-${pipeline.id || pipeline.name || idx}-${idx}`} className="p-3 md:p-4 bg-slate-800 rounded border-l-4 border-blue-500">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{pipeline.name || pipeline.repo_name || `Pipeline ${idx + 1}`}</div>
                              <div className="text-sm text-slate-400 mt-1">
                                Status: <span className={pipeline.status === "success" ? "text-green-400" : pipeline.status === "failed" ? "text-red-400" : "text-yellow-400"}>
                                  {pipeline.status || "unknown"}
                                </span>
                              </div>
                            </div>
                            <span className="text-xs text-slate-500">{pipeline.timestamp || "Recently"}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No pipelines found</div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Running Jobs */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Running Jobs</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {runningJobs.length > 0 ? (
                      runningJobs.map((job, idx) => (
                        <div key={`job-${job.id || job.name || idx}-${idx}`} className="p-3 md:p-4 bg-slate-800 rounded border-l-4 border-yellow-500">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{job.name || `Job ${idx + 1}`}</div>
                              <div className="text-sm text-slate-400 mt-1">Running...</div>
                            </div>
                            <span className="text-xs text-yellow-400">Active</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No running jobs</div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* History */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {                      pipelines.slice(0, 20).map((pipeline, idx) => (
                        <div key={`history-${pipeline.id || pipeline.name || idx}-${idx}`} className="p-2 md:p-3 bg-slate-800 rounded text-xs md:text-sm">
                        <div className="flex justify-between">
                          <span>{pipeline.name || `Pipeline ${idx + 1}`}</span>
                          <span className={pipeline.status === "success" ? "text-green-400" : "text-red-400"}>
                            {pipeline.status || "unknown"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : tab === "deployments" ? (
            /* Tab 2: Deployments */
            <div className="space-y-6">
              {/* Live Deployments */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Live Deployments</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {deployments.length > 0 ? (
                      deployments.map((deployment, idx) => (
                        <div key={`deployment-${deployment.id || deployment.name || idx}-${idx}`} className="p-3 md:p-4 bg-slate-800 rounded border-l-4 border-green-500">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{deployment.name || `Deployment ${idx + 1}`}</div>
                              <div className="text-sm text-slate-400 mt-1">
                                Environment: {deployment.environment || "production"}
                              </div>
                            </div>
                            <span className="text-xs text-green-400">Live</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No live deployments</div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Shadow Deployments */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Shadow Deployments</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {shadowDeployments.length > 0 ? (
                      shadowDeployments.map((deployment, idx) => (
                        <div key={`shadow-${deployment.id || deployment.name || idx}-${idx}`} className="p-3 md:p-4 bg-slate-800 rounded border-l-4 border-purple-500">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{deployment.name || `Shadow ${idx + 1}`}</div>
                              <div className="text-sm text-slate-400 mt-1">
                                Traffic: {deployment.traffic_percent || 0}%
                              </div>
                            </div>
                            <span className="text-xs text-purple-400">Shadow</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No shadow deployments</div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Traffic Routing */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Traffic Routing</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-slate-400">Traffic routing configuration will be displayed here</div>
                </CardContent>
              </Card>
            </div>
          ) : tab === "backup" ? (
            /* Tab 3: Backup & Restore */
            <div className="space-y-6">
              {/* Manual Snapshot */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Manual Snapshot</CardTitle>
                </CardHeader>
                <CardContent>
                  <Button
                    onClick={async () => {
                      try {
                        await apiRequest("/api/backup/create", { method: "POST" }, 30000);
                        alert("Snapshot created successfully!");
                        fetchData();
                      } catch (err) {
                        alert("Error creating snapshot");
                      }
                    }}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Create Snapshot
                  </Button>
                </CardContent>
              </Card>

              {/* Auto Restore Rules */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Auto Restore Rules</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-slate-400">Auto restore rules configuration will be displayed here</div>
                </CardContent>
              </Card>

              {/* Storage Usage */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Storage Usage</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {backups.length > 0 ? (
                      backups.map((backup, idx) => (
                        <div key={`backup-${backup.id || backup.name || idx}-${idx}`} className="p-3 md:p-4 bg-slate-800 rounded">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{backup.name || `Backup ${idx + 1}`}</div>
                              <div className="text-sm text-slate-400 mt-1">
                                Size: {backup.size || "N/A"}
                              </div>
                            </div>
                            <span className="text-xs text-slate-500">{backup.timestamp || "Recently"}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-4">No backups found</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : null}
        </div>
      </div>
    </main>
  );
}
