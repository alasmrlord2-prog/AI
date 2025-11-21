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

    # Check services
    services = ["ssh", "nginx", "docker"]
    status = {}

    for s in services:
        try:
            out = os.popen(f"systemctl is-active {s}").read().strip()
            status[s] = out
        except:
            status[s] = "unknown"

    result["services"] = status

    return result
