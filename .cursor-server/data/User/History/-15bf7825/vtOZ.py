import os
import shutil

def run(_=None):
    result = {}

    # CPU load
    try:
        load1, load5, load15 = os.getloadavg()
        result["load_avg"] = {"1min": load1, "5min": load5, "15min": load15}
    except:
        result["load_avg"] = "not supported"

    # RAM
    try:
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                key, val = line.split(":")[0], line.split(":")[1].strip()
                mem[key] = val
        result["memory"] = {
            "total": mem.get("MemTotal", "unknown"),
            "available": mem.get("MemAvailable", "unknown")
        }
    except:
        result["memory"] = "cannot read /proc/meminfo"

    # Disk
    try:
        total, used, free = shutil.disk_usage("/")
        result["disk"] = {
            "total_gb": total // (1024**3),
            "used_gb": used // (1024**3),
            "free_gb": free // (1024**3)
        }
    except:
        result["disk"] = "error"

    # Check services - skip systemctl in Docker containers (it doesn't work)
    # Instead, check if processes are running - OPTIMIZED: faster checks with shorter timeouts
    services = ["ssh", "nginx", "docker"]
    status = {}
    
    import subprocess
    import os

    # Check if we're in a Docker container
    is_docker = os.path.exists("/.dockerenv") or (os.path.exists("/proc/1/cgroup") and "docker" in open("/proc/1/cgroup").read())
    
    for s in services:
        try:
            if is_docker:
                # In Docker, check if process exists instead of using systemctl - FASTER
                result_proc = subprocess.run(
                    ["pgrep", "-f", s],
                    capture_output=True,
                    text=True,
                    timeout=0.5  # Reduced to 0.5 seconds for faster response
                )
                status[s] = "active" if result_proc.returncode == 0 else "inactive"
            else:
                # On host system, use systemctl - FASTER
                result_proc = subprocess.run(
                    ["systemctl", "is-active", s],
                    capture_output=True,
                    text=True,
                    timeout=1  # Reduced to 1 second per service
                )
                status[s] = result_proc.stdout.strip() if result_proc.returncode == 0 else "inactive"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            status[s] = "unknown"
        except Exception as e:
            # Log the error for debugging
            print(f"Error checking service {s}: {e}")
            status[s] = "unknown"

    result["services"] = status

    return result
