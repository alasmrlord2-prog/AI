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

    # Check services - with timeout to prevent hanging
    services = ["ssh", "nginx", "docker"]
    status = {}
    
    import subprocess
    import signal

    for s in services:
        try:
            # Use subprocess with timeout instead of os.popen to prevent hanging
            result_proc = subprocess.run(
                ["systemctl", "is-active", s],
                capture_output=True,
                text=True,
                timeout=2  # 2 second timeout per service
            )
            status[s] = result_proc.stdout.strip() if result_proc.returncode == 0 else "inactive"
        except subprocess.TimeoutExpired:
            status[s] = "timeout"
        except Exception:
            status[s] = "unknown"

    result["services"] = status

    return result
