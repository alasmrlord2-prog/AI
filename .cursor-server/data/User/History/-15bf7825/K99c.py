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

    # Check services - dynamically discover common services instead of hardcoded list
    # Skip systemctl in Docker containers (it doesn't work)
    # Instead, check if processes are running - OPTIMIZED: faster checks with shorter timeouts
    status = {}
    
    import subprocess
    import os

    # Check if we're in a Docker container
    is_docker = os.path.exists("/.dockerenv") or (os.path.exists("/proc/1/cgroup") and "docker" in open("/proc/1/cgroup").read())
    
    # Dynamically discover services by checking common process names
    # This avoids hardcoded service lists and adapts to the actual system
    common_services_to_check = []
    
    # Try to get list of services from systemd if available (not in Docker)
    if not is_docker:
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager", "--no-legend"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # Extract service names from systemctl output
                for line in result.stdout.split('\n'):
                    if line.strip():
                        # Format: service_name.service ... 
                        service_name = line.split()[0].replace('.service', '')
                        if service_name and len(service_name) < 50:  # Filter out very long names
                            common_services_to_check.append(service_name)
        except:
            pass
    
    # If no services found from systemd, or in Docker, check common processes
    if not common_services_to_check:
        # Check for common services by process name (works in Docker too)
        common_processes = ["ssh", "sshd", "nginx", "apache", "docker", "dockerd", "postgres", "mysql", "redis"]
        for proc_name in common_processes:
            try:
                result_proc = subprocess.run(
                    ["pgrep", "-f", proc_name],
                    capture_output=True,
                    text=True,
                    timeout=0.3
                )
                if result_proc.returncode == 0:
                    # Normalize service name
                    if proc_name in ["sshd"]:
                        common_services_to_check.append("ssh")
                    elif proc_name in ["dockerd"]:
                        common_services_to_check.append("docker")
                    elif proc_name not in common_services_to_check:
                        common_services_to_check.append(proc_name)
            except:
                continue
    
    # Limit to top 10 services to avoid timeout
    services = list(set(common_services_to_check))[:10]
    
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
