"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { API_URL } from "@/lib/api";

export default function CICDPage() {
  const [repos, setRepos] = useState<any[]>([]);
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [reposRes, pipelinesRes] = await Promise.all([
        fetch(`${API_URL}/api/cicd/repos`),
        fetch(`${API_URL}/api/cicd/pipelines`)
      ]);

      if (reposRes.ok) {
        const reposData = await reposRes.json();
        setRepos(reposData.repos || []);
      }

      if (pipelinesRes.ok) {
        const pipelinesData = await pipelinesRes.json();
        setPipelines(pipelinesData.pipelines || []);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">CI/CD Pipeline</h1>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Repositories</CardTitle>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <p>Loading...</p>
                  ) : repos.length === 0 ? (
                    <p className="text-gray-500">No repositories found</p>
                  ) : (
                    <div className="space-y-2">
                      {repos.map((repo) => (
                        <div key={repo.name} className="p-3 bg-gray-50 rounded">
                          <div className="font-semibold">{repo.name}</div>
                          <div className="text-sm text-gray-600">
                            Branch: {repo.branch || "N/A"}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Pipelines</CardTitle>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <p>Loading...</p>
                  ) : pipelines.length === 0 ? (
                    <p className="text-gray-500">No pipelines found</p>
                  ) : (
                    <div className="space-y-2">
                      {pipelines.slice(0, 5).map((pipeline) => (
                        <div key={pipeline.id} className="p-3 bg-gray-50 rounded">
                          <div className="flex justify-between items-center">
                            <div>
                              <div className="font-semibold">{pipeline.repo_name}</div>
                              <div className="text-sm text-gray-600">
                                Status: <span className={`font-semibold ${
                                  pipeline.status === "success" ? "text-green-600" :
                                  pipeline.status === "failed" ? "text-red-600" :
                                  "text-yellow-600"
                                }`}>
                                  {pipeline.status}
                                </span>
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
          </div>
        </main>
      </div>
    </div>
  );
}

