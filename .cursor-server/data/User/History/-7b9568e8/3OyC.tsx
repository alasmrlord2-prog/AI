"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

import { API_URL } from "@/lib/api";

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
  
  // Track pending action IDs for polling
  const [pendingActionId, setPendingActionId] = useState<string | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const getAuthToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  };

  const runReadFile = async () => {
    setLoadingRead(true);
    setError("");
    setFileContent("");
    
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/tools/read_file`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token && { "Authorization": `Bearer ${token}` }),
        },
        body: JSON.stringify({ path }),
      });
      
      const data = await res.json();
      console.log("Read File Response:", JSON.stringify(data, null, 2));
      
      // Check response status and data
      if (res.ok) {
        // Check if there's an error in the response
        if (data.error) {
          // Handle error object (approval pending, etc.)
          if (typeof data.error === 'object' && data.error.status === 'pending') {
            const errorObj = data.error;
            const actionId = errorObj.action_id || 'N/A';
            setFileContent(`⏳ Action requires approval\n\nAction ID: ${actionId}\nMessage: ${errorObj.message || 'Please approve this action in the Approvals page.'}\n\n💡 Go to Approvals page to approve this action.\n\n🔄 Checking for result automatically...`);
            setError("Action pending approval");
            // Start polling for this action
            if (actionId !== 'N/A') {
              setPendingActionId(actionId);
            }
            return;
          }
          
          // Handle string error
          const errorMsg = typeof data.error === 'string' ? data.error : JSON.stringify(data.error);
          setFileContent(`❌ Error: ${errorMsg}\n\n💡 Tip: ${errorMsg.includes("disabled") ? 'Enable "Allow Read File" in Settings page' : 'Check the error message above'}`);
          setError(errorMsg);
          return;
        }
        
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
      } else {
        const errorMsg = data.error || data.detail || "Failed to read file";
        setFileContent(`❌ Error: ${errorMsg}\n\n💡 Tip: ${errorMsg.includes("disabled") ? 'Enable "Allow Read File" in Settings page' : 'Check backend logs'}`);
        setError(errorMsg);
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
    
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/tools/run_shell`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token && { "Authorization": `Bearer ${token}` }),
        },
        body: JSON.stringify({ cmd }),
      });
      
      const data = await res.json();
      console.log("Run Shell Response:", JSON.stringify(data, null, 2));
      
      if (res.ok) {
        // Check if there's an error in the response
        if (data.error) {
          // Handle error object (approval pending, etc.)
          if (typeof data.error === 'object' && data.error.status === 'pending') {
            const errorObj = data.error;
            const actionId = errorObj.action_id || 'N/A';
            setCmdOutput(`⏳ Action requires approval\n\nAction ID: ${actionId}\nMessage: ${errorObj.message || 'Please approve this action in the Approvals page.'}\n\n💡 Go to Approvals page to approve this action.\n\n🔄 Checking for result automatically...`);
            setError("Action pending approval");
            // Start polling for this action
            if (actionId !== 'N/A') {
              setPendingActionId(actionId);
            }
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
      } else {
        const errorMsg = data.error || data.detail || "Failed to execute command";
        setCmdOutput(`❌ Error: ${errorMsg}\n\n💡 Tip: ${errorMsg.includes("disabled") ? 'Enable "Allow Shell" in Settings page' : 'Check backend logs'}`);
        setError(errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to execute command";
      setCmdOutput(`Error: ${errorMsg}`);
      setError(errorMsg);
    } finally {
      setLoadingShell(false);
    }
  };

  // Poll for action result when pending
  useEffect(() => {
    if (!pendingActionId) return;
    
    const checkActionResult = async () => {
      try {
        const token = getAuthToken();
        if (!token) return;
        
        const res = await fetch(`${API_URL}/api/pending-actions`, {
          headers: { "Authorization": `Bearer ${token}` },
        });
        
        if (!res.ok) return;
        
        const data = await res.json();
        const action = data.actions?.find((a: any) => a.id === pendingActionId);
        
        if (action) {
          if (action.status === "approved" && action.execution_result) {
            // Action was approved and executed
            setPendingActionId(null);
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
            
            // Display result based on tool type
            if (action.tool_name === "run_shell") {
              setCmdOutput(`✅ Command executed successfully:\n\n${action.execution_result}`);
              setError("");
            } else if (action.tool_name === "read_file") {
              setFileContent(`✅ File read successfully:\n\n${action.execution_result}`);
              setError("");
            }
            
            return;
          } else if (action.status === "approved" && action.execution_error) {
            // Action was approved but execution failed
            setPendingActionId(null);
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
            
            const errorMsg = `❌ Execution failed: ${action.execution_error}`;
            if (action.tool_name === "run_shell") {
              setCmdOutput(errorMsg);
            } else if (action.tool_name === "read_file") {
              setFileContent(errorMsg);
            }
            setError(action.execution_error);
            return;
          } else if (action.status === "rejected") {
            // Action was rejected
            setPendingActionId(null);
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
            
            const rejectMsg = `❌ Action was rejected${action.rejection_reason ? `: ${action.rejection_reason}` : ''}`;
            if (action.tool_name === "run_shell") {
              setCmdOutput(rejectMsg);
            } else if (action.tool_name === "read_file") {
              setFileContent(rejectMsg);
            }
            setError("Action rejected");
            return;
          }
        }
      } catch (err) {
        console.error("Error checking action result:", err);
      }
    };
    
    // Check immediately
    checkActionResult();
    
    // Then poll every 2 seconds
    pollingIntervalRef.current = setInterval(checkActionResult, 2000);
    
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [pendingActionId]);

  const checkService = async () => {
    setLoadingService(true);
    setError("");
    setSvcStatus("");
    
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/tools/service`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token && { "Authorization": `Bearer ${token}` }),
        },
        body: JSON.stringify({ name: svc }),
      });
      
      const data = await res.json();
      console.log("Service Status Response:", JSON.stringify(data, null, 2));
      
      if (res.ok) {
        // Check if there's an error in the response
        if (data.error) {
          // Handle error object (approval pending, etc.)
          if (typeof data.error === 'object' && data.error.status === 'pending') {
            const errorObj = data.error;
            const actionId = errorObj.action_id || 'N/A';
            setSvcStatus(`⏳ Action requires approval\n\nAction ID: ${actionId}\nMessage: ${errorObj.message || 'Please approve this action in the Approvals page.'}\n\n💡 Go to Approvals page to approve this action.\n\n🔄 Checking for result automatically...`);
            setError("Action pending approval");
            // Start polling for this action
            if (actionId !== 'N/A') {
              setPendingActionId(actionId);
            }
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
                <Button 
                  onClick={runReadFile}
                  disabled={loadingRead}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loadingRead ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span> Reading...
                    </span>
                  ) : (
                    "📖 Read File"
                  )}
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
                  disabled={loadingShell}
                  className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loadingShell ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span> Executing...
                    </span>
                  ) : (
                    "⚡ Execute"
                  )}
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
                disabled={loadingService}
                className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loadingService ? (
                  <span className="flex items-center gap-2">
                    <span className="animate-spin">⏳</span> Checking...
                  </span>
                ) : (
                  "✓ Check Status"
                )}
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

