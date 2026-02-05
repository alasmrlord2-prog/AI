import os
import subprocess

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

def run(svc):
    try:
        # Try systemctl first (if available)
        try:
            result = subprocess.run(
                ["systemctl", "status", svc, "--no-pager", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout
            elif result.stderr:
                # systemctl exists but service not found, try alternative methods
                pass
        except FileNotFoundError:
            # systemctl not found, use alternative methods
            pass
        
        # Alternative: Check if process is running using psutil (if available)
        if PSUTIL_AVAILABLE:
            try:
                # Map common service names to process names
                process_map = {
                    "ssh": "sshd",
                    "docker": "dockerd",
                    "nginx": "nginx",
                    "apache": "apache2",
                    "apache2": "apache2",
                    "mysql": "mysqld",
                    "postgresql": "postgres",
                    "redis": "redis-server",
                    "systemd": "systemd",
                }
                
                process_name = process_map.get(svc.lower(), svc)
                
                # Check if process is running
                found = False
                process_info = []
                
                for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if process_name.lower() in proc_name or proc_name in process_name.lower():
                            found = True
                            process_info.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'status': proc.info['status'],
                                'cpu': proc.info['cpu_percent'],
                                'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 2)
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if found:
                    info_lines = [f"Service '{svc}' is running:\n"]
                    for proc in process_info:
                        info_lines.append(f"  PID: {proc['pid']}")
                        info_lines.append(f"  Name: {proc['name']}")
                        info_lines.append(f"  Status: {proc['status']}")
                        info_lines.append(f"  CPU: {proc['cpu']}%")
                        info_lines.append(f"  Memory: {proc['memory_mb']} MB")
                        info_lines.append("")
                    return "\n".join(info_lines)
                else:
                    # Try pgrep as last resort
                    try:
                        pgrep_result = subprocess.run(
                            ["pgrep", "-f", svc],
                            capture_output=True,
                            text=True,
                            timeout=3
                        )
                        if pgrep_result.returncode == 0:
                            pids = pgrep_result.stdout.strip().split('\n')
                            return f"Service '{svc}' appears to be running (PIDs: {', '.join(pids)})\n\nNote: Using process detection. For detailed status, use systemctl if available."
                    except:
                        pass
                    
                    return f"Service '{svc}' not found or not running.\n\nChecked:\n- Process name: {process_name}\n- systemctl: Not available\n\n💡 Try checking manually:\n- ps aux | grep {svc}\n- pgrep -f {svc}"
            except Exception as e:
                # If psutil fails for any reason, fall through to basic ps command
                pass
        
        # Fallback: use basic ps command if psutil not available or failed
        try:
            # psutil not available, use basic ps command
            try:
                ps_result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                if ps_result.returncode == 0:
                    lines = ps_result.stdout.split('\n')
                    matching = [line for line in lines if svc.lower() in line.lower()]
                    if matching:
                        return f"Service '{svc}' appears in process list:\n\n" + "\n".join(matching[:5])
                    else:
                        return f"Service '{svc}' not found in running processes.\n\n💡 This system doesn't use systemd. Try:\n- ps aux | grep {svc}\n- Check if service is running manually"
            except:
                return f"Unable to check service '{svc}' status.\n\nSystem information:\n- systemctl: Not available\n- psutil: Not available\n\n💡 This system may not use standard service management."
        
    except subprocess.TimeoutExpired:
        return f"Timeout while checking service '{svc}' status."
    except Exception as e:
        return f"Error checking service '{svc}': {str(e)}"
