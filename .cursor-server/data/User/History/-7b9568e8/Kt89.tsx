"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

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
    <main className="p-6 text-slate-200 space-y-6">
      <h1 className="text-2xl mb-2">Tools & File Explorer</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Read file */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Read File</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="/app/main.py"
            />
            <Button onClick={runReadFile}>Read</Button>
            <Textarea
              className="min-h-[150px] bg-black text-green-400 font-mono text-xs"
              value={fileContent}
              readOnly
            />
          </CardContent>
        </Card>

        {/* Run shell */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Run Shell (حسب الصلاحيات)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input
              value={cmd}
              onChange={(e) => setCmd(e.target.value)}
              placeholder="ls -la"
            />
            <Button onClick={runShell}>Execute</Button>
            <Textarea
              className="min-h-[150px] bg-black text-green-400 font-mono text-xs"
              value={cmdOutput}
              readOnly
            />
          </CardContent>
        </Card>
      </div>

      {/* Service status */}
      <Card className="bg-slate-900 border-slate-800 max-w-md">
        <CardHeader>
          <CardTitle>Service Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input
            value={svc}
            onChange={(e) => setSvc(e.target.value)}
            placeholder="ssh"
          />
          <Button onClick={checkService}>Check</Button>
          <Textarea
            className="min-h-[100px] bg-black text-green-400 font-mono text-xs"
            value={svcStatus}
            readOnly
          />
        </CardContent>
      </Card>
    </main>
  );
}

