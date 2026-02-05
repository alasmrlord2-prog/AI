from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import json
from datetime import datetime, timedelta
import traceback

# Set OLLAMA_URL before importing (already imported os above, but ensure it's set)
if "OLLAMA_URL" not in os.environ:
    os.environ["OLLAMA_URL"] = os.getenv("OLLAMA_URL", "http://localhost:11434")

try:
    from agent.think_and_act import think_and_act
except ImportError as e:
    error_msg = str(e)
    print(f"Warning: Could not import think_and_act: {error_msg}")
    def think_and_act(message: str) -> str:
        return f"Agent not available: {error_msg}"
except Exception as e:
    error_msg = str(e)
    print(f"Warning: Error importing think_and_act: {error_msg}")
    def think_and_act(message: str) -> str:
        return f"Agent error: {error_msg}"

try:
    # Add app directory to path to find tools
    import sys
    import os
    app_dir = os.path.dirname(os.path.abspath(__file__))
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    from tools.monitor import run as monitor_run
    from tools.read_file import run as read_file_run
    from tools.run_shell import run as run_shell_run
    from tools.check_service import run as check_service_run
    print("✅ Tools imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import some tools: {e}")
    import traceback
    traceback.print_exc()
    # Create dummy functions
    def monitor_run():
        return {"error": "Monitor not available"}
    def read_file_run(path):
        return "File read not available"
    def run_shell_run(cmd):
        return "Shell not available"
    def check_service_run(name):
        return "Service check not available"

# Import auth
try:
    from auth import (
        authenticate_user, create_user, verify_token, create_access_token,
        check_permission, can_approve, ROLES, load_users
    )
    AUTH_ENABLED = True
except ImportError as e:
    print(f"Warning: Auth not available: {e}")
    AUTH_ENABLED = False
    def authenticate_user(*args, **kwargs):
        return None
    def create_user(*args, **kwargs):
        return {}
    def verify_token(*args, **kwargs):
        return None
    def create_access_token(*args, **kwargs):
        return ""
    def check_permission(*args, **kwargs):
        return True
    def can_approve(*args, **kwargs):
        return True
    ROLES = {}
    load_users = lambda: {}

# Security - Use auto_error=False to allow optional auth
security = HTTPBearer(auto_error=False)

# ===== Configuration =====
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
CHAT_LOG_FILE = os.path.join(LOG_DIR, "chat.log")
SETTINGS_FILE = os.path.join("memory", "settings.json")

app = FastAPI(
    title="AI-Agent Backend",
    version="0.1.0",
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Global Exception Handler =====
# Handle HTTPException (already has CORS from middleware, but ensure it's there)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensure CORS headers on HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Handle unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are always sent, even on unhandled errors"""
    import traceback
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "traceback": traceback.format_exc() if os.getenv("DEBUG", "false").lower() == "true" else None
    }
    print(f"Unhandled exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content=error_detail,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# ===== Models =====
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: Optional[str] = None
    reply: str

class SettingsModel(BaseModel):
    allow_shell: bool = False
    allow_read_file: bool = True
    allow_doc_search: bool = True
    allow_logs: bool = True
    long_memory_enabled: bool = True
    agent_mode: str = "devops"
    memory_mode: str = "short"
    require_approval: List[str] = ["run_shell"]

class ToolReadFile(BaseModel):
    path: str

class ToolRunShell(BaseModel):
    cmd: str

class ToolService(BaseModel):
    name: str

# ===== Auth Models =====
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "viewer"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# ===== Auth Helpers =====
def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user from JWT token"""
    # If auth is disabled, return guest user
    if not AUTH_ENABLED:
        return {"email": "guest", "name": "Guest", "role": "admin"}
    
    # If no credentials provided, check if we can allow guest access
    if credentials is None:
        # Try to verify if auth module is actually working
        try:
            # If verify_token function exists but credentials are None, allow guest in dev mode
            # This handles the case where auth module exists but we want to allow testing
            return {"email": "guest", "name": "Guest", "role": "admin"}
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

def require_role(allowed_roles: List[str]):
    """Decorator to require specific role"""
    def decorator(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return decorator

# ===== Helpers =====
def log_chat(role: str, session_id: Optional[str], content: str, meta: dict = None):
    """يسجل كل رسالة في chat.log كسطر JSON"""
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "role": role,
        "session_id": session_id,
        "content": content,
        "meta": meta or {},
    }
    with open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def load_settings() -> SettingsModel:
    if not os.path.exists(SETTINGS_FILE):
        return SettingsModel()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SettingsModel(**data)
    except Exception:
        return SettingsModel()

def save_settings(s: SettingsModel):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s.dict(), f, ensure_ascii=False, indent=2)

# ===== Authentication Endpoints =====
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Login endpoint"""
    try:
        if not AUTH_ENABLED:
            # Development mode - bypass auth
            token = create_access_token({"email": req.email, "role": "admin"})
            return TokenResponse(
                access_token=token,
                user={"email": req.email, "name": "Guest", "role": "admin"}
            )
        
        user = authenticate_user(req.email, req.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        access_token = create_access_token({"email": user["email"], "role": user["role"]})
        return TokenResponse(
            access_token=access_token,
            user=user
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Login error: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@app.post("/api/auth/register")
async def register(req: RegisterRequest, current_user: dict = Depends(require_role(["admin"]))):
    """Register new user (admin only)"""
    if not AUTH_ENABLED:
        return {"error": "Auth not enabled"}
    
    try:
        user = create_user(req.email, req.password, req.name, req.role)
        return {"message": "User created", "email": user["email"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@app.get("/api/auth/roles")
async def get_roles():
    """Get available roles"""
    return {"roles": list(ROLES.keys()), "permissions": ROLES}

# ===== Health Check =====
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "ai-backend"}

# ===== REST API: /api/chat =====
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        session_id = req.session_id or "default"
        # سجل رسالة المستخدم
        log_chat("user", session_id, req.message)
        
        # Update Prometheus metrics
        if PROMETHEUS_ENABLED:
            chat_requests_total.inc()
        
        # نداء الـ agent
        try:
            reply = think_and_act(req.message)
        except Exception as e:
            import traceback
            error_msg = f"Agent error: {str(e)}\n{traceback.format_exc()}"
            log_chat("error", session_id, error_msg)
            if PROMETHEUS_ENABLED:
                chat_errors_total.inc()
            reply = f"خطأ في الـ Agent: {str(e)}"
        
        # سجل رد الـ agent
        log_chat("assistant", session_id, reply)
        
        return ChatResponse(session_id=session_id, reply=reply)
    except Exception as e:
        import traceback
        error_msg = f"Chat endpoint error: {str(e)}\n{traceback.format_exc()}"
        log_chat("error", None, error_msg)
        return ChatResponse(
            session_id=req.session_id or "default",
            reply=f"خطأ في السيرفر: {str(e)}"
        )

# ===== Logs API: /api/logs =====
@app.get("/api/logs")
async def get_logs(limit: int = 100):
    """يرجع آخر N أسطر من chat.log للـ Dashboard"""
    if not os.path.exists(CHAT_LOG_FILE):
        return []
    
    with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    lines = lines[-limit:]
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    
    return items

# ===== Settings API =====
@app.get("/api/settings")
def get_settings():
    return load_settings().dict()

@app.put("/api/settings")
def update_settings(new_settings: SettingsModel):
    save_settings(new_settings)
    return {"ok": True}

# ===== Monitor API =====
@app.get("/api/monitor")
def monitor_status():
    try:
        base_data = monitor_run()
    except Exception as e:
        import traceback
        print(f"Error in monitor_run(): {e}")
        traceback.print_exc()
        base_data = {
            "error": f"Monitor error: {str(e)}",
            "load_avg": {"1min": 0, "5min": 0, "15min": 0},
            "memory": {"total": 0, "available": 0},
            "disk": {"total_gb": 0, "used_gb": 0, "free_gb": 0},
            "services": {},
        }
    
    # Add network monitoring
    try:
        from tools.network_monitor import run as network_monitor
        network_data = network_monitor()
        base_data["network"] = network_data
    except Exception as e:
        print(f"Network monitor error: {e}")
        base_data["network"] = {"error": str(e)}
    
    return base_data

# ===== Prometheus Metrics =====
try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
    from prometheus_client import REGISTRY
    
    # Metrics
    chat_requests_total = Counter('chat_requests_total', 'Total chat requests')
    chat_errors_total = Counter('chat_errors_total', 'Total chat errors')
    active_users = Gauge('active_users', 'Active users')
    system_cpu_load = Gauge('system_cpu_load', 'CPU load average')
    system_memory_used = Gauge('system_memory_used_bytes', 'Memory used in bytes')
    system_disk_used = Gauge('system_disk_used_bytes', 'Disk used in bytes')
    
    # Network metrics
    network_rx_bytes = Gauge('network_rx_bytes_total', 'Network RX bytes')
    network_tx_bytes = Gauge('network_tx_bytes_total', 'Network TX bytes')
    network_rx_mbps = Gauge('network_rx_mbps', 'Network RX Mbps')
    network_tx_mbps = Gauge('network_tx_mbps', 'Network TX Mbps')
    network_connections_total = Gauge('network_connections_total', 'Total network connections')
    
    PROMETHEUS_ENABLED = True
except ImportError:
    PROMETHEUS_ENABLED = False
    print("Warning: prometheus_client not available")

@app.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    if not PROMETHEUS_ENABLED:
        return {"error": "Prometheus not enabled"}
    
    # Update metrics from monitor
    try:
        mon_data = monitor_run()
        if "load_avg" in mon_data and isinstance(mon_data["load_avg"], dict):
            system_cpu_load.set(mon_data["load_avg"].get("1min", 0))
        
        if "memory" in mon_data:
            mem = mon_data["memory"]
            if isinstance(mem, dict) and "total" in mem and "available" in mem:
                try:
                    total_kb = int(str(mem["total"]).replace(" kB", "").replace(" ", ""))
                    avail_kb = int(str(mem["available"]).replace(" kB", "").replace(" ", ""))
                    used_kb = total_kb - avail_kb
                    system_memory_used.set(used_kb * 1024)  # Convert to bytes
                except (ValueError, AttributeError):
                    pass
        
        if "disk" in mon_data:
            disk = mon_data["disk"]
            if isinstance(disk, dict) and "used_gb" in disk:
                try:
                    system_disk_used.set(int(disk["used_gb"]) * 1024 * 1024 * 1024)  # Convert to bytes
                except (ValueError, TypeError):
                    pass
        
        # Update network metrics
        if "network" in mon_data and isinstance(mon_data["network"], dict):
            net_data = mon_data["network"]
            if "stats" in net_data and isinstance(net_data["stats"], dict):
                net_stats = net_data["stats"]
                if "total" in net_stats and isinstance(net_stats["total"], dict):
                    total = net_stats["total"]
                    try:
                        network_rx_bytes.set(int(total.get("rx_bytes", 0)))
                        network_tx_bytes.set(int(total.get("tx_bytes", 0)))
                        network_rx_mbps.set(float(total.get("rx_mbps", 0)))
                        network_tx_mbps.set(float(total.get("tx_mbps", 0)))
                    except (ValueError, TypeError):
                        pass
            
            if "connections" in net_data and isinstance(net_data["connections"], dict):
                try:
                    network_connections_total.set(int(net_data["connections"].get("total", 0)))
                except (ValueError, TypeError):
                    pass
    except Exception as e:
        print(f"Error updating metrics: {e}")
        import traceback
        traceback.print_exc()
    
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

# ===== Security Analysis API =====
@app.post("/api/security/scan_repo")
async def api_scan_repo(
    path: str = "/app",
    max_files: int = 1000,
    current_user: dict = Depends(get_current_user)
):
    """Scan repository for secrets"""
    if not check_permission(current_user.get("role", "viewer"), "scan_repo"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_repo
        return scan_repo(path, max_files)
    except ImportError:
        return {"error": "Security scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_infra")
async def api_scan_infra(
    path: str = "/app",
    current_user: dict = Depends(get_current_user)
):
    """Scan infrastructure files"""
    if not check_permission(current_user.get("role", "viewer"), "scan_infra"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_infra
        return scan_infra(path)
    except ImportError:
        return {"error": "Security scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_logs")
async def api_scan_logs(
    path: str = "/app/logs",
    lines: int = 1000,
    current_user: dict = Depends(get_current_user)
):
    """Scan logs for authentication issues"""
    if not check_permission(current_user.get("role", "viewer"), "scan_logs_auth"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_logs_auth
        return scan_logs_auth(path, lines)
    except ImportError:
        return {"error": "Security scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_network")
async def api_scan_network(
    current_user: dict = Depends(get_current_user)
):
    """Scan network for security issues"""
    if not check_permission(current_user.get("role", "viewer"), "scan_network"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_network_security
        return scan_network_security()
    except ImportError:
        return {"error": "Network security scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_system")
async def api_scan_system(
    current_user: dict = Depends(get_current_user)
):
    """Scan system for security issues (OS, services, processes)"""
    if not check_permission(current_user.get("role", "viewer"), "scan_system"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_system_security
        return scan_system_security()
    except ImportError:
        return {"error": "System security scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_docker")
async def api_scan_docker(
    current_user: dict = Depends(get_current_user)
):
    """Scan Docker configuration for security issues"""
    if not check_permission(current_user.get("role", "viewer"), "scan_docker"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_docker_security
        return scan_docker_security()
    except ImportError:
        return {"error": "Docker security scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_network_detailed")
async def api_scan_network_detailed(
    current_user: dict = Depends(get_current_user)
):
    """Detailed network security scan"""
    if not check_permission(current_user.get("role", "viewer"), "scan_network_detailed"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_network_security_detailed
        return scan_network_security_detailed()
    except ImportError:
        return {"error": "Detailed network scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_vulnerabilities")
async def api_scan_vulnerabilities(
    current_user: dict = Depends(get_current_user)
):
    """Scan for vulnerabilities"""
    if not check_permission(current_user.get("role", "viewer"), "scan_vulnerabilities"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_vulnerabilities
        return scan_vulnerabilities()
    except ImportError:
        return {"error": "Vulnerability scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_file_integrity")
async def api_scan_file_integrity(
    path: str = "/etc",
    current_user: dict = Depends(get_current_user)
):
    """Scan file integrity"""
    if not check_permission(current_user.get("role", "viewer"), "scan_file_integrity"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_file_integrity
        return scan_file_integrity(path)
    except ImportError:
        return {"error": "File integrity scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_malware")
async def api_scan_malware(
    path: str = "/tmp",
    current_user: dict = Depends(get_current_user)
):
    """Scan for malware"""
    if not check_permission(current_user.get("role", "viewer"), "scan_malware"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_malware
        return scan_malware(path)
    except ImportError:
        return {"error": "Malware scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_intrusion_detection")
async def api_scan_intrusion_detection(
    current_user: dict = Depends(get_current_user)
):
    """Intrusion Detection System scan"""
    if not check_permission(current_user.get("role", "viewer"), "scan_intrusion_detection"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_intrusion_detection
        return scan_intrusion_detection()
    except ImportError:
        return {"error": "IDS scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_port_scan")
async def api_scan_port_scan(
    target: str = "localhost",
    current_user: dict = Depends(get_current_user)
):
    """Port scanning"""
    if not check_permission(current_user.get("role", "viewer"), "scan_port_scan"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_port_scan
        return scan_port_scan(target)
    except ImportError:
        return {"error": "Port scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/scan_penetration_test")
async def api_scan_penetration_test(
    current_user: dict = Depends(get_current_user)
):
    """Penetration testing scan"""
    if not check_permission(current_user.get("role", "viewer"), "scan_penetration_test"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.security_scan import scan_penetration_test
        return scan_penetration_test()
    except ImportError:
        return {"error": "Penetration test not available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/security/siem")
async def api_siem_monitor(
    current_user: dict = Depends(get_current_user)
):
    """SIEM monitoring dashboard data"""
    if not check_permission(current_user.get("role", "viewer"), "siem_monitor"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.siem_monitor import run as siem_monitor
        return siem_monitor()
    except ImportError:
        return {"error": "SIEM monitor not available"}
    except Exception as e:
        return {"error": str(e)}

# ===== Advanced Security Tools API =====

@app.post("/api/security/advanced/threat_intelligence")
async def api_threat_intelligence(
    ip: str,
    current_user: dict = Depends(get_current_user)
):
    """Threat intelligence scan"""
    if not check_permission(current_user.get("role", "viewer"), "threat_intelligence"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import threat_intelligence_scan
        return threat_intelligence_scan(ip)
    except ImportError:
        return {"error": "Threat intelligence not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/network_forensics")
async def api_network_forensics(
    current_user: dict = Depends(get_current_user)
):
    """Network forensics analysis"""
    if not check_permission(current_user.get("role", "viewer"), "network_forensics"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import network_traffic_analysis
        return network_traffic_analysis()
    except ImportError:
        return {"error": "Network forensics not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/vulnerability")
async def api_advanced_vulnerability(
    current_user: dict = Depends(get_current_user)
):
    """Advanced vulnerability scanning"""
    if not check_permission(current_user.get("role", "viewer"), "advanced_vulnerability"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import advanced_vulnerability_scan
        return advanced_vulnerability_scan()
    except ImportError:
        return {"error": "Advanced vulnerability scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/web_scan")
async def api_web_scan(
    url: str,
    current_user: dict = Depends(get_current_user)
):
    """Web application vulnerability scan"""
    if not check_permission(current_user.get("role", "viewer"), "web_scan"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import web_vulnerability_scan
        return web_vulnerability_scan(url)
    except ImportError:
        return {"error": "Web scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/container")
async def api_advanced_container(
    current_user: dict = Depends(get_current_user)
):
    """Advanced container security scan"""
    if not check_permission(current_user.get("role", "viewer"), "advanced_container"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import advanced_container_scan
        return advanced_container_scan()
    except ImportError:
        return {"error": "Advanced container scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/kubernetes")
async def api_kubernetes_scan(
    current_user: dict = Depends(get_current_user)
):
    """Kubernetes security scan"""
    if not check_permission(current_user.get("role", "viewer"), "kubernetes_scan"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import kubernetes_security_scan
        return kubernetes_security_scan()
    except ImportError:
        return {"error": "Kubernetes scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/aws")
async def api_aws_scan(
    current_user: dict = Depends(get_current_user)
):
    """AWS security scan"""
    if not check_permission(current_user.get("role", "viewer"), "aws_scan"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import aws_security_scan
        return aws_security_scan()
    except ImportError:
        return {"error": "AWS scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/memory_forensics")
async def api_memory_forensics(
    current_user: dict = Depends(get_current_user)
):
    """Memory forensics analysis"""
    if not check_permission(current_user.get("role", "viewer"), "memory_forensics"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import memory_forensics
        return memory_forensics()
    except ImportError:
        return {"error": "Memory forensics not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/disk_forensics")
async def api_disk_forensics(
    path: str = "/",
    current_user: dict = Depends(get_current_user)
):
    """Disk forensics analysis"""
    if not check_permission(current_user.get("role", "viewer"), "disk_forensics"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import disk_forensics
        return disk_forensics(path)
    except ImportError:
        return {"error": "Disk forensics not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/password_audit")
async def api_password_audit(
    current_user: dict = Depends(get_current_user)
):
    """Password security audit"""
    if not check_permission(current_user.get("role", "viewer"), "password_audit"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import password_audit
        return password_audit()
    except ImportError:
        return {"error": "Password audit not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/compliance")
async def api_compliance_check(
    standard: str = "CIS",
    current_user: dict = Depends(get_current_user)
):
    """Compliance checking"""
    if not check_permission(current_user.get("role", "viewer"), "compliance_check"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import compliance_check
        return compliance_check(standard)
    except ImportError:
        return {"error": "Compliance check not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/burp_suite")
async def api_burp_suite(
    url: str,
    current_user: dict = Depends(get_current_user)
):
    """Burp Suite-like web vulnerability scanning"""
    if not check_permission(current_user.get("role", "viewer"), "burp_suite"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import burp_suite_scan
        return burp_suite_scan(url)
    except ImportError:
        return {"error": "Burp Suite scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/metasploit")
async def api_metasploit(
    target: str = "localhost",
    port: int = None,
    current_user: dict = Depends(get_current_user)
):
    """Metasploit-like vulnerability and exploit scanning"""
    if not check_permission(current_user.get("role", "viewer"), "metasploit"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import metasploit_scan
        return metasploit_scan(target, port)
    except ImportError:
        return {"error": "Metasploit scan not available"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/security/advanced/packet_analysis")
async def api_packet_analysis(
    file_path: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Advanced packet capture analysis"""
    if not check_permission(current_user.get("role", "viewer"), "packet_analysis"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        from tools.advanced_security_tools import advanced_packet_analysis
        return advanced_packet_analysis(file_path)
    except ImportError:
        return {"error": "Packet analysis not available"}
    except Exception as e:
        return {"error": str(e)}

# ===== File Explorer API =====
@app.get("/api/fs/list")
async def api_fs_list(path: str = ""):
    """List directory contents"""
    try:
        from tools.file_explorer import list_dir
        settings = load_settings()
        if not settings.allow_read_file:
            return {"error": "File operations disabled from settings"}
        return list_dir(path)
    except ImportError:
        # Fallback if file_explorer doesn't exist
        return {"error": "File explorer not available"}

@app.get("/api/fs/read")
async def api_fs_read(path: str, limit: int = 10000):
    """Read file content"""
    try:
        from tools.file_explorer import read_file
        settings = load_settings()
        if not settings.allow_read_file:
            return {"error": "File operations disabled from settings"}
        return read_file(path, limit=limit)
    except ImportError:
        return {"error": "File explorer not available"}

@app.get("/api/fs/tail")
async def api_fs_tail(path: str, lines: int = 50):
    """Read last N lines of a file"""
    try:
        from tools.file_explorer import tail_file
        settings = load_settings()
        if not settings.allow_read_file:
            return {"error": "File operations disabled from settings"}
        return tail_file(path, lines=lines)
    except ImportError:
        return {"error": "File explorer not available"}

# Import pending actions
try:
    from pending_actions import (
        add_pending_action, approve_action, reject_action,
        get_pending_actions, get_action_by_id
    )
    PENDING_ACTIONS_AVAILABLE = True
except ImportError:
    PENDING_ACTIONS_AVAILABLE = False
    def add_pending_action(*args, **kwargs):
        return {}
    def approve_action(*args, **kwargs):
        return None
    def reject_action(*args, **kwargs):
        return None
    def get_pending_actions():
        return []
    def get_action_by_id(*args, **kwargs):
        return None

# ===== Tools API =====
@app.post("/api/tools/read_file")
def api_read_file(payload: ToolReadFile, current_user: dict = Depends(get_current_user)):
    settings = load_settings()
    if not settings.allow_read_file:
        return {"error": "read_file disabled from settings"}
    
    # Check permission
    if not check_permission(current_user.get("role", "viewer"), "read_file"):
        return {"error": "Permission denied"}
    
    try:
        return {"content": read_file_run(payload.path)}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/tools/run_shell")
async def api_run_shell(payload: ToolRunShell, current_user: dict = Depends(get_current_user)):
    settings = load_settings()
    if not settings.allow_shell:
        return {"error": "run_shell disabled from settings"}
    
    # Check if approval required
    if "run_shell" in settings.require_approval:
        # Check if user can approve
        if not can_approve(current_user.get("role", "viewer")):
            # Create pending action
            if PENDING_ACTIONS_AVAILABLE:
                action = add_pending_action(
                    user_email=current_user.get("email", "unknown"),
                    tool_name="run_shell",
                    tool_args={"cmd": payload.cmd},
                    reason="Requires approval"
                )
                return {
                    "status": "pending",
                    "action_id": action["id"],
                    "message": "Action requires approval"
                }
            else:
                return {"error": "Action requires approval but approval system not available"}
    
    # Check permission
    if not check_permission(current_user.get("role", "viewer"), "run_shell"):
        return {"error": "Permission denied"}
    
    try:
        return {"output": run_shell_run(payload.cmd)}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/tools/service")
def api_service(payload: ToolService, current_user: dict = Depends(get_current_user)):
    # Check permission
    if not check_permission(current_user.get("role", "viewer"), "check_service"):
        return {"error": "Permission denied"}
    
    try:
        return {"status": check_service_run(payload.name)}
    except Exception as e:
        return {"error": str(e)}

# ===== Pending Actions API =====
@app.get("/api/pending-actions")
async def get_pending_actions_list(current_user: dict = Depends(require_role(["admin", "devops"]))):
    """Get all pending actions (admin/devops only)"""
    if not PENDING_ACTIONS_AVAILABLE:
        return {"error": "Pending actions not available"}
    return {"actions": get_pending_actions()}

@app.post("/api/pending-actions/{action_id}/approve")
async def approve_pending_action(
    action_id: str,
    current_user: dict = Depends(require_role(["admin", "devops"]))
):
    """Approve a pending action"""
    if not PENDING_ACTIONS_AVAILABLE:
        return {"error": "Pending actions not available"}
    
    action = approve_action(action_id, current_user.get("email", "unknown"))
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # Execute the action if approved
    if action["tool_name"] == "run_shell":
        try:
            output = run_shell_run(action["tool_args"]["cmd"])
            action["execution_result"] = output
            action["executed_at"] = datetime.utcnow().isoformat()
        except Exception as e:
            action["execution_error"] = str(e)
    
    return {"status": "approved", "action": action}

class RejectRequest(BaseModel):
    reason: str = ""

@app.post("/api/pending-actions/{action_id}/reject")
async def reject_pending_action(
    action_id: str,
    req: RejectRequest = RejectRequest(reason=""),
    current_user: dict = Depends(require_role(["admin", "devops"]))
):
    """Reject a pending action"""
    if not PENDING_ACTIONS_AVAILABLE:
        return {"error": "Pending actions not available"}
    
    action = reject_action(action_id, current_user.get("email", "unknown"), req.reason)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return {"status": "rejected", "action": action}

# ===== WebSocket Manager =====
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for chat
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            session_id = data.get("session_id") or "default"
            message = data.get("message") or ""
            
            # سجل رسالة المستخدم
            log_chat("user", session_id, message)
            
            # أرسل إشارة بداية
            await manager.send_json(websocket, {
                "type": "start",
                "session_id": session_id,
            })
            
            # نداء الـ Agent
            reply = think_and_act(message)
            
            # سجل رد الـ Agent
            log_chat("assistant", session_id, reply)
            
            # chunk واحد
            await manager.send_json(websocket, {
                "type": "chunk",
                "session_id": session_id,
                "text": reply,
            })
            
            # إشارة نهاية
            await manager.send_json(websocket, {
                "type": "end",
                "session_id": session_id,
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        log_chat("error", None, f"WebSocket error: {e}")
        try:
            await manager.send_json(websocket, {
                "type": "error",
                "error": str(e),
            })
        except Exception:
            pass

# Legacy endpoint for compatibility
@app.websocket("/ws/agent")
async def websocket_agent(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            reply = think_and_act(data)
            await ws.send_text(reply)
    except WebSocketDisconnect:
        pass

@app.post("/api/agent/run")
def run_agent(q: ChatRequest):
    result = think_and_act(q.message)
    return {"result": result}

# Billing API endpoints
@app.get("/api/billing/invoices")
def get_invoices(current_user: dict = Depends(get_current_user)):
    """Get all invoices"""
    # Mock data for now - replace with actual database queries
    invoices = [
        {
            "id": "inv_001",
            "tenant_id": "tenant_1",
            "tenant_name": "Acme Corp",
            "amount": 1500.00,
            "currency": "USD",
            "status": "paid",
            "due_date": "2024-01-15",
            "created_at": "2024-01-01T00:00:00Z",
            "items": [
                {"description": "Basic Plan - January", "quantity": 1, "price": 1500.00}
            ]
        },
        {
            "id": "inv_002",
            "tenant_id": "tenant_2",
            "tenant_name": "Tech Solutions",
            "amount": 2500.00,
            "currency": "USD",
            "status": "pending",
            "due_date": "2024-02-15",
            "created_at": "2024-02-01T00:00:00Z",
            "items": [
                {"description": "Pro Plan - February", "quantity": 1, "price": 2500.00}
            ]
        },
        {
            "id": "inv_003",
            "tenant_id": "tenant_3",
            "tenant_name": "Startup Inc",
            "amount": 500.00,
            "currency": "USD",
            "status": "overdue",
            "due_date": "2024-01-10",
            "created_at": "2023-12-15T00:00:00Z",
            "items": [
                {"description": "Starter Plan - December", "quantity": 1, "price": 500.00}
            ]
        }
    ]
    return {"invoices": invoices}

@app.get("/api/billing/subscriptions")
def get_subscriptions(current_user: dict = Depends(get_current_user)):
    """Get all subscriptions"""
    # Mock data for now - replace with actual database queries
    subscriptions = [
        {
            "id": "sub_001",
            "tenant_id": "tenant_1",
            "tenant_name": "Acme Corp",
            "plan": "Basic",
            "status": "active",
            "current_period_start": "2024-01-01",
            "current_period_end": "2024-02-01",
            "amount": 1500.00,
            "currency": "USD"
        },
        {
            "id": "sub_002",
            "tenant_id": "tenant_2",
            "tenant_name": "Tech Solutions",
            "plan": "Pro",
            "status": "active",
            "current_period_start": "2024-02-01",
            "current_period_end": "2024-03-01",
            "amount": 2500.00,
            "currency": "USD"
        },
        {
            "id": "sub_003",
            "tenant_id": "tenant_3",
            "tenant_name": "Startup Inc",
            "plan": "Starter",
            "status": "cancelled",
            "current_period_start": "2023-12-01",
            "current_period_end": "2024-01-01",
            "amount": 500.00,
            "currency": "USD"
        }
    ]
    return {"subscriptions": subscriptions}

@app.get("/api/billing/payment-methods")
def get_payment_methods(current_user: dict = Depends(get_current_user)):
    """Get payment methods"""
    # Mock data for now - replace with actual database queries
    payment_methods = [
        {
            "id": "pm_001",
            "type": "card",
            "last4": "4242",
            "brand": "Visa",
            "expiry_month": 12,
            "expiry_year": 2025,
            "is_default": True
        },
        {
            "id": "pm_002",
            "type": "card",
            "last4": "8888",
            "brand": "Mastercard",
            "expiry_month": 6,
            "expiry_year": 2026,
            "is_default": False
        },
        {
            "id": "pm_003",
            "type": "manual",
            "is_default": False,
            "account_name": "Cash Payment",
            "account_number": "N/A"
        },
        {
            "id": "pm_004",
            "type": "electronic",
            "is_default": False,
            "provider": "Payment Gateway API",
            "account_name": "Electronic Payment",
            "account_number": "EP-2024-001"
        },
        {
            "id": "pm_005",
            "type": "bank_transfer",
            "is_default": False,
            "bank_name": "البنك المركزي",
            "account_name": "Company Account",
            "account_number": "1234567890"
        },
        {
            "id": "pm_006",
            "type": "sham_cash",
            "is_default": False,
            "account_name": "Sham Cash Wallet",
            "account_number": "SC-987654321"
        }
    ]
    return {"payment_methods": payment_methods}

@app.post("/api/billing/payment-methods/{payment_method_id}/set-default")
def set_default_payment_method(payment_method_id: str, current_user: dict = Depends(get_current_user)):
    """Set a payment method as default"""
    # Mock implementation - in real app, update database
    # For now, just return success
    return {"success": True, "message": f"Payment method {payment_method_id} set as default"}

# ===== Include New Feature Routers =====
try:
    from app.api.cicd import router as cicd_router
    app.include_router(cicd_router)
    print("✅ CI/CD router loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load CI/CD router: {e}")

try:
    from app.api.debugger import router as debugger_router
    app.include_router(debugger_router)
    print("✅ Debugger router loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load Debugger router: {e}")

try:
    from app.api.monitoring import router as monitoring_router
    app.include_router(monitoring_router)
    print("✅ Monitoring router loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load Monitoring router: {e}")

try:
    from app.api.audit import router as audit_router
    app.include_router(audit_router)
    print("✅ Audit router loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load Audit router: {e}")

try:
    from app.api.backup import router as backup_router
    app.include_router(backup_router)
    print("✅ Backup router loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load Backup router: {e}")

try:
    from app.api.incidents import router as incidents_router
    app.include_router(incidents_router)
    print("✅ Incidents router loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load Incidents router: {e}")

try:
    from app.api.workflows import router as workflows_router
    app.include_router(workflows_router)
    print("✅ Workflows router loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load Workflows router: {e}")

try:
    from app.api.visualization import router as visualization_router
    app.include_router(visualization_router)
    print("✅ Visualization router loaded")
except Exception as e:
    print(f"⚠️ Warning: Could not load Visualization router: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

