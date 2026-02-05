"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { API_URL } from "@/lib/api";

export default function BackupPage() {
  const [backups, setBackups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showBackupForm, setShowBackupForm] = useState(false);
  const [backupType, setBackupType] = useState("postgresql");
  const [dbName, setDbName] = useState("");
  const [volumeName, setVolumeName] = useState("");

  useEffect(() => {
    fetchBackups();
    const interval = setInterval(fetchBackups, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchBackups = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/backup/list`);
      if (res.ok) {
        const data = await res.json();
        setBackups(data.backups || []);
      }
    } catch (err) {
      console.error("Error fetching backups:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    try {
      let endpoint = "";
      let body: any = {};

      if (backupType === "postgresql" || backupType === "mysql") {
        endpoint = `${API_URL}/api/backup/${backupType}`;
        body = { db_name: dbName };
      } else if (backupType === "docker-volume") {
        endpoint = `${API_URL}/api/backup/docker-volume`;
        body = { volume_name: volumeName };
      }

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      if (res.ok) {
        setShowBackupForm(false);
        setDbName("");
        setVolumeName("");
        fetchBackups();
      } else {
        const data = await res.json();
        alert(data.detail || "فشل إنشاء Backup");
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDeleteBackup = async (backupId: string) => {
    if (!confirm("هل أنت متأكد من حذف هذا Backup?")) return;

    try {
      const res = await fetch(`${API_URL}/api/backup/${backupId}`, {
        method: "DELETE"
      });

      if (res.ok) {
        fetchBackups();
      } else {
        const data = await res.json();
        alert(data.detail || "فشل الحذف");
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleVerifyBackup = async (backupId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/backup/verify/${backupId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.match) {
          alert("✅ Backup صحيح - MD5 matches");
        } else {
          alert("⚠️ Backup قد يكون تالف - MD5 لا يتطابق");
        }
      } else {
        const data = await res.json();
        alert(data.detail || "فشل التحقق");
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const formatSize = (bytes: number) => {
    if (!bytes) return "0 B";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold text-slate-800">💾 Backup Manager</h1>
              <Button 
                onClick={() => setShowBackupForm(!showBackupForm)}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {showBackupForm ? "إلغاء" : "+ Create Backup"}
              </Button>
            </div>

            {showBackupForm && (
              <Card className="mb-6 border-purple-200 bg-purple-50">
                <CardHeader>
                  <CardTitle className="text-purple-800">Create New Backup</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="backupType">Backup Type</Label>
                    <select
                      id="backupType"
                      value={backupType}
                      onChange={(e) => setBackupType(e.target.value)}
                      className="w-full mt-1 p-2 border rounded"
                    >
                      <option value="postgresql">PostgreSQL</option>
                      <option value="mysql">MySQL</option>
                      <option value="docker-volume">Docker Volume</option>
                    </select>
                  </div>
                  {(backupType === "postgresql" || backupType === "mysql") && (
                    <div>
                      <Label htmlFor="dbName">Database Name</Label>
                      <Input
                        id="dbName"
                        value={dbName}
                        onChange={(e) => setDbName(e.target.value)}
                        placeholder="database_name"
                        className="mt-1"
                      />
                    </div>
                  )}
                  {backupType === "docker-volume" && (
                    <div>
                      <Label htmlFor="volumeName">Volume Name</Label>
                      <Input
                        id="volumeName"
                        value={volumeName}
                        onChange={(e) => setVolumeName(e.target.value)}
                        placeholder="volume_name"
                        className="mt-1"
                      />
                    </div>
                  )}
                  <Button onClick={handleCreateBackup} className="w-full bg-purple-600 hover:bg-purple-700">
                    Create Backup
                  </Button>
                </CardContent>
              </Card>
            )}

            <Card className="border-slate-200 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg">
                <CardTitle className="text-white">Backups</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {loading ? (
                  <p className="text-slate-500">جاري التحميل...</p>
                ) : backups.length === 0 ? (
                  <p className="text-slate-500 text-center py-8">لا توجد backups</p>
                ) : (
                  <div className="space-y-3">
                    {backups.map((backup) => (
                      <div key={backup.id} className="p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="font-semibold text-slate-800">{backup.id}</div>
                            <div className="text-sm text-slate-600 mt-1">
                              Type: <span className="font-medium">{backup.type}</span> | 
                              Size: <span className="font-medium">{formatSize(backup.size || 0)}</span>
                            </div>
                            {backup.database_name && (
                              <div className="text-sm text-slate-600 mt-1">
                                Database: {backup.database_name}
                              </div>
                            )}
                            {backup.volume_name && (
                              <div className="text-sm text-slate-600 mt-1">
                                Volume: {backup.volume_name}
                              </div>
                            )}
                            <div className="text-xs text-slate-500 mt-1">
                              {backup.timestamp && new Date(backup.timestamp).toLocaleString()}
                            </div>
                          </div>
                          <div className="flex gap-2 ml-4">
                            <span className={`px-2 py-1 rounded text-xs ${
                              backup.status === "success" ? "bg-green-100 text-green-700" :
                              "bg-yellow-100 text-yellow-700"
                            }`}>
                              {backup.status}
                            </span>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleVerifyBackup(backup.id)}
                              className="text-xs text-blue-600 hover:text-blue-700"
                            >
                              Verify
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDeleteBackup(backup.id)}
                              className="text-xs text-red-600 hover:text-red-700"
                            >
                              Delete
                            </Button>
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
