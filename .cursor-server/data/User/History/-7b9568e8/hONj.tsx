"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function ToolsPage() {
  const [path, setPath] = useState("/app");
  const [fileContent, setFileContent] = useState("");
  const [cmd, setCmd] = useState("ls -la");
  const [cmdOutput, setCmdOutput] = useState("");
  const [svc, setSvc] = useState("ssh");
  const [svcStatus, setSvcStatus] = useState("");
  const [loadingRead, setLoadingRead] = useState(false);
  const [loadingShell, setLoadingShell] = useState(false);
  const [loadingService, setLoadingService] = useState(false);
  const [error, setError] = useState("");
  const [pendingActionId, setPendingActionId] = useState<string | null>(null);
  const [pendingActionType, setPendingActionType] = useState<'read_file' | 'run_shell' | 'service' | null>(null);

  const runReadFile = async () => {
    setLoadingRead(true);
    setError("");
    setFileContent("");
    setPendingActionId(null);
    setPendingActionType(null);
    
    try {
      const data = await apiRequest("/api/tools/read_file", {
        method: "POST",
        body: JSON.stringify({ path }),
      }, 30000); // 30s timeout for file read
      console.log("Read File Response:", JSON.stringify(data, null, 2));
      
      // Check if there's an error in the response
      if (data.error) {
          // Handle error object (approval pending, etc.)
          if (typeof data.error === 'object' && data.error.status === 'pending') {
            const errorObj = data.error;
            const actionId = errorObj.action_id;
            if (actionId) {
              setPendingActionId(actionId);
              setPendingActionType('read_file');
            }
            setFileContent(`⏳ Action requires approval\n\nAction ID: ${actionId || 'N/A'}\nMessage: ${errorObj.message || 'Please approve this action in the Approvals page.'}\n\n💡 Go to Approvals page to approve this action.\n\nAfter approval, click "Get Result" button below to fetch the result.`);
            setError("Action pending approval");
            return;
          }
          
          // Handle string error
          const errorMsg = typeof data.error === 'string' ? data.error : JSON.stringify(data.error);
          setFileContent(`❌ Error: ${errorMsg}\n\n💡 Tip: ${errorMsg.includes("disabled") ? 'Enable "Allow Read File" in Settings page' : 'Check the error message above'}`);
          setError(errorMsg);
          return;
        }
      }
      
      // Handle success case
      const content = data.content || data.result || data.message || "";
      if (content) {
        // Check if it's an error message from the backend
        if (content.includes("[Errno 21]") || content.includes("Is a directory")) {
          setFileContent(`⚠️ Error: The path "${path}" is a directory, not a file.\n\n💡 Tip: Specify a file path, for example:\n- /app/main.py\n- /app/auth.py\n- /etc/hosts`);
          setError("Path is a directory");
        } else if (content.includes("Errno") || (content.includes("Error") && !content.includes("127.0.0.1")) || content.includes("No such file")) {
          setFileContent(`❌ Error: ${content}\n\n💡 Tip: Make sure the file path is correct and the file exists.`);
          setError(content);
        } else if (content.includes("not available")) {
          // This shouldn't happen if imports work, but handle it
          setFileContent(`⚠️ Warning: ${content}\n\n💡 The backend may need to be restarted. Check backend logs.`);
          setError(content);
        } else {
          setFileContent(content);
        }
      } else {
        setFileContent("File read successfully but content is empty");
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to read file";
      setFileContent(`Error: ${errorMsg}`);
      setError(errorMsg);
    } finally {
      setLoadingRead(false);
    }
  };

  const runShell = async () => {
    setLoadingShell(true);
    setError("");
    setCmdOutput("");
    setPendingActionId(null);
    setPendingActionType(null);
    
    try {
      const data = await apiRequest("/api/tools/run_shell", {
        method: "POST",
        body: JSON.stringify({ cmd }),
      }, 30000); // 30s timeout for shell commands
      
      console.log("Run Shell Response:", JSON.stringify(data, null, 2));
      
      // Check if there's an error in the response
      if (data.error) {
          // Handle error object (approval pending, etc.)
          if (typeof data.error === 'object' && data.error.status === 'pending') {
            const errorObj = data.error;
            const actionId = errorObj.action_id;
            if (actionId) {
              setPendingActionId(actionId);
              setPendingActionType('run_shell');
            }
            setCmdOutput(`⏳ Action requires approval\n\nAction ID: ${actionId || 'N/A'}\nMessage: ${errorObj.message || 'Please approve this action in the Approvals page.'}\n\n💡 Go to Approvals page to approve this action.\n\nAfter approval, click "Get Result" button below to fetch the result.`);
            setError("Action pending approval");
            return;
          }
          
          // Handle string error
          const errorMsg = typeof data.error === 'string' ? data.error : JSON.stringify(data.error);
          setCmdOutput(`❌ Error: ${errorMsg}\n\n💡 Tip: ${errorMsg.includes("disabled") ? 'Enable "Allow Shell" in Settings page' : 'Check the error message above'}`);
          setError(errorMsg);
          return;
        }
        
        // Handle pending approval case (legacy format)
        if (data.status === "pending") {
          setCmdOutput(`⏳ Action requires approval. Action ID: ${data.action_id}\n${data.message || ""}`);
          setError("Action pending approval");
          return;
        }
        
        const output = data.output || data.result || data.message || "";
        if (output) {
          if (output.includes("not available")) {
            setCmdOutput(`⚠️ Warning: ${output}\n\n💡 The backend may need to be restarted. Check backend logs.`);
            setError(output);
          } else {
            setCmdOutput(output);
          }
        } else {
            setCmdOutput("Command executed successfully but output is empty");
          }
        }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to execute command";
      setCmdOutput(`Error: ${errorMsg}`);
      setError(errorMsg);
    } finally {
      setLoadingShell(false);
    }
  };

  const getResultByActionId = async (actionId: string, toolType: 'read_file' | 'run_shell' | 'service') => {
    try {
      let endpoint = '';
      let body: any = {};
      
      if (toolType === 'read_file') {
        endpoint = `/api/tools/read_file?action_id=${actionId}`;
        body = { path };
        setLoadingRead(true);
      } else if (toolType === 'run_shell') {
        endpoint = `/api/tools/run_shell?action_id=${actionId}`;
        body = { cmd };
        setLoadingShell(true);
      } else if (toolType === 'service') {
        endpoint = `/api/tools/service?action_id=${actionId}`;
        body = { name: svc };
        setLoadingService(true);
      }
      
      setError("");
      
      const data = await apiRequest(endpoint, {
        method: "POST",
        body: JSON.stringify(body),
      }, 30000); // 30s timeout for result retrieval
      
      if (data) {
        if (data.error) {
          if (typeof data.error === 'object' && data.error.status === 'pending') {
            if (toolType === 'read_file') {
              setFileContent(`⏳ Action is still pending approval. Please wait or check the Approvals page.`);
            } else if (toolType === 'run_shell') {
              setCmdOutput(`⏳ Action is still pending approval. Please wait or check the Approvals page.`);
            } else {
              setSvcStatus(`⏳ Action is still pending approval. Please wait or check the Approvals page.`);
            }
            setError("Action still pending");
          } else {
            const errorMsg = typeof data.error === 'string' ? data.error : JSON.stringify(data.error);
            if (toolType === 'read_file') {
              setFileContent(`❌ Error: ${errorMsg}`);
            } else if (toolType === 'run_shell') {
              setCmdOutput(`❌ Error: ${errorMsg}`);
            } else {
              setSvcStatus(`❌ Error: ${errorMsg}`);
            }
            setError(errorMsg);
          }
        } else {
          // Success - got the result
          if (toolType === 'read_file') {
            setFileContent(data.content || data.result || "");
            setPendingActionId(null);
            setPendingActionType(null);
          } else if (toolType === 'run_shell') {
            setCmdOutput(data.output || data.result || "");
            setPendingActionId(null);
            setPendingActionType(null);
          } else {
            setSvcStatus(data.status || data.result || "");
            setPendingActionId(null);
            setPendingActionType(null);
          }
          setError("");
        }
      } else {
        const errorMsg = data.error || data.detail || "Failed to get result";
        if (toolType === 'read_file') {
          setFileContent(`❌ Error: ${errorMsg}`);
        } else if (toolType === 'run_shell') {
          setCmdOutput(`❌ Error: ${errorMsg}`);
        } else {
          setSvcStatus(`❌ Error: ${errorMsg}`);
        }
        setError(errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to get result";
      if (toolType === 'read_file') {
        setFileContent(`Error: ${errorMsg}`);
      } else if (toolType === 'run_shell') {
        setCmdOutput(`Error: ${errorMsg}`);
      } else {
        setSvcStatus(`Error: ${errorMsg}`);
      }
      setError(errorMsg);
    } finally {
      if (toolType === 'read_file') {
        setLoadingRead(false);
      } else if (toolType === 'run_shell') {
        setLoadingShell(false);
      } else {
        setLoadingService(false);
      }
    }
  };

  const checkService = async () => {
    setLoadingService(true);
    setError("");
    setSvcStatus("");
    setPendingActionId(null);
    setPendingActionType(null);
    
    try {
      const data = await apiRequest("/api/tools/service", {
        method: "POST",
        body: JSON.stringify({ name: svc }),
      }, 30000); // 30s timeout for service operations
      
      console.log("Service Status Response:", JSON.stringify(data, null, 2));
      
      // Check if there's an error in the response
      if (data.error) {
          // Handle error object (approval pending, etc.)
          if (typeof data.error === 'object' && data.error.status === 'pending') {
            const errorObj = data.error;
            const actionId = errorObj.action_id;
            if (actionId) {
              setPendingActionId(actionId);
              setPendingActionType('service');
            }
            setSvcStatus(`⏳ Action requires approval\n\nAction ID: ${actionId || 'N/A'}\nMessage: ${errorObj.message || 'Please approve this action in the Approvals page.'}\n\n💡 Go to Approvals page to approve this action.\n\nAfter approval, click "Get Result" button below to fetch the result.`);
            setError("Action pending approval");
            setLoadingService(false);
            return;
          }
          
          // Handle string error
          const errorMsg = typeof data.error === 'string' ? data.error : JSON.stringify(data.error);
          setSvcStatus(`❌ Error: ${errorMsg}\n\n💡 Tip: Check backend logs`);
          setError(errorMsg);
          return;
        }
        
        // Service status can be a string or object
        const statusValue = data.status || data.result || "";
        
        if (typeof statusValue === "string") {
          if (statusValue.trim()) {
            if (statusValue.includes("not available")) {
              setSvcStatus(`⚠️ Warning: ${statusValue}\n\n💡 The backend may need to be restarted. Check backend logs.`);
              setError(statusValue);
            } else {
              setSvcStatus(statusValue);
            }
          } else {
            // Try to get service status using alternative method
            setSvcStatus(`⚠️ Service "${svc}" status is empty.\n\nPossible reasons:\n- Service is not installed\n- Service name is incorrect\n- Service is not managed by systemd\n- No status information available\n\n💡 Try these service names:\n- ssh (SSH daemon)\n- docker (Docker service)\n- nginx (Nginx web server)\n- mysql (MySQL database)\n- postgresql (PostgreSQL database)\n\nOr check manually: systemctl status ${svc}`);
          }
        } else if (typeof statusValue === "object" && statusValue !== null) {
          setSvcStatus(JSON.stringify(statusValue, null, 2));
        } else {
          setSvcStatus(`⚠️ Service "${svc}" status is empty.\n\nPossible reasons:\n- Service is not installed\n- Service name is incorrect\n- Service is not managed by systemd\n\n💡 Try: systemctl status ${svc}`);
        }
      } else {
        const errorMsg = data.error || data.detail || "Failed to check service";
        setSvcStatus(`❌ Error: ${errorMsg}\n\n💡 Tip: Make sure the service name is correct and systemctl is available.`);
        setError(errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to check service";
      setSvcStatus(`Error: ${errorMsg}`);
      setError(errorMsg);
    } finally {
      setLoadingService(false);
    }
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

          {error && (
            <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
              ⚠️ {error}
            </div>
          )}

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
                <div className="flex gap-2">
                  <Button 
                    onClick={runReadFile}
                    disabled={loadingRead}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex-1"
                  >
                    {loadingRead ? (
                      <span className="flex items-center gap-2">
                        <span className="animate-spin">⏳</span> Reading...
                      </span>
                    ) : (
                      "📖 Read File"
                    )}
                  </Button>
                  {pendingActionId && pendingActionType === 'read_file' && (
                    <Button 
                      onClick={() => pendingActionId && getResultByActionId(pendingActionId, 'read_file')}
                      disabled={loadingRead}
                      className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loadingRead ? (
                        <span className="animate-spin">⏳</span>
                      ) : (
                        "✅ Get Result"
                      )}
                    </Button>
                  )}
                </div>
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
                <div className="flex gap-2">
                  <Button 
                    onClick={runShell}
                    disabled={loadingShell}
                    className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex-1"
                  >
                    {loadingShell ? (
                      <span className="flex items-center gap-2">
                        <span className="animate-spin">⏳</span> Executing...
                      </span>
                    ) : (
                      "⚡ Execute"
                    )}
                  </Button>
                  {pendingActionId && pendingActionType === 'run_shell' && (
                    <Button 
                      onClick={() => pendingActionId && getResultByActionId(pendingActionId, 'run_shell')}
                      disabled={loadingShell}
                      className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loadingShell ? (
                        <span className="animate-spin">⏳</span>
                      ) : (
                        "✅ Get Result"
                      )}
                    </Button>
                  )}
                </div>
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
              <div className="flex gap-2">
                <Button 
                  onClick={checkService}
                  disabled={loadingService}
                  className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex-1"
                >
                  {loadingService ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span> Checking...
                    </span>
                  ) : (
                    "✓ Check Status"
                  )}
                </Button>
                {pendingActionId && pendingActionType === 'service' && (
                  <Button 
                    onClick={() => pendingActionId && getResultByActionId(pendingActionId, 'service')}
                    disabled={loadingService}
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loadingService ? (
                      <span className="animate-spin">⏳</span>
                    ) : (
                      "✅ Get Result"
                    )}
                  </Button>
                )}
              </div>
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

