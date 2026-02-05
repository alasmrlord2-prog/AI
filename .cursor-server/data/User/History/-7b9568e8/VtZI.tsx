"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function ToolsPage() {
  const [path, setPath] = useState("/app");
  const [fileContent, setFileContent] = useState("");
  const [cmd, setCmd] = useState("ls -la");
  const [cmdOutput, setCmdOutput] = useState("");
  const [svc, setSvc] = useState("ssh");
  const [svcStatus, setSvcStatus] = useState("");

  const runReadFile = async () => {
    const res = await fetch(`${API_URL}/api/tools/read_file`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    const data = await res.json();
    setFileContent(data.content || data.error || "");
  };

  const runShell = async () => {
    const res = await fetch(`${API_URL}/api/tools/run_shell`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd }),
    });
    const data = await res.json();
    setCmdOutput(data.output || data.error || "");
  };

  const checkService = async () => {
    const res = await fetch(`${API_URL}/api/tools/service`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: svc }),
    });
    const data = await res.json();
    setSvcStatus(
      data.status ? JSON.stringify(data.status) : data.error || ""
    );
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              🛠️ Tools & File Explorer
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              System tools for file operations, shell commands, and service management
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Read file */}
            <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-purple-700 shadow-lg">
              <CardHeader>
                <CardTitle className="text-purple-400">📄 Read File</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input
                  value={path}
                  onChange={(e) => setPath(e.target.value)}
                  placeholder="/app/main.py"
                  className="bg-slate-800 border-slate-700 text-slate-200"
                />
                <Button 
                  onClick={runReadFile}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold"
                >
                  📖 Read File
                </Button>
                <Textarea
                  className="min-h-[200px] bg-slate-950 border-slate-700 text-green-400 font-mono text-xs"
                  value={fileContent}
                  readOnly
                />
              </CardContent>
            </Card>

            {/* Run shell */}
            <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-orange-700 shadow-lg">
              <CardHeader>
                <CardTitle className="text-orange-400">💻 Run Shell (حسب الصلاحيات)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input
                  value={cmd}
                  onChange={(e) => setCmd(e.target.value)}
                  placeholder="ls -la"
                  className="bg-slate-800 border-slate-700 text-slate-200"
                />
                <Button 
                  onClick={runShell}
                  className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white font-semibold"
                >
                  ⚡ Execute
                </Button>
                <Textarea
                  className="min-h-[200px] bg-slate-950 border-slate-700 text-green-400 font-mono text-xs"
                  value={cmdOutput}
                  readOnly
                />
              </CardContent>
            </Card>
          </div>

          {/* Service status */}
          <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-cyan-700 shadow-lg max-w-md">
            <CardHeader>
              <CardTitle className="text-cyan-400">🔧 Service Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input
                value={svc}
                onChange={(e) => setSvc(e.target.value)}
                placeholder="ssh"
                className="bg-slate-800 border-slate-700 text-slate-200"
              />
              <Button 
                onClick={checkService}
                className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white font-semibold"
              >
                ✓ Check Status
              </Button>
              <Textarea
                className="min-h-[120px] bg-slate-950 border-slate-700 text-green-400 font-mono text-xs"
                value={svcStatus}
                readOnly
              />
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}

