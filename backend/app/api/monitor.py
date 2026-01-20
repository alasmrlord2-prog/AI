"""Monitoring API endpoints."""
from fastapi import APIRouter, Depends
from app.api.auth import get_current_user
from app.core.config import get_settings
import time

router = APIRouter(prefix="/api/monitor", tags=["monitor"])
settings = get_settings()

# Simple in-memory cache for monitor data (TTL: 5 seconds)
_monitor_cache = {"data": None, "timestamp": 0, "prev_net_io": {}}
CACHE_TTL = 5  # Cache for 5 seconds to reduce load and prevent timeout

# Import monitoring tools
try:
    from app.tools.monitor import run as monitor_run
except ImportError:
    def monitor_run():
        return {
            "error": "Monitor not available",
            "load_avg": {"1min": 0, "5min": 0, "15min": 0},
            "memory": {"total": 0, "available": 0},
            "disk": {"total_gb": 0, "used_gb": 0, "free_gb": 0},
            "services": {},
        }

try:
    from app.tools.network_monitor import run as network_monitor
except ImportError:
    def network_monitor():
        return {"error": "Network monitor not available"}


@router.get("")
async def monitor_status(current_user: dict = Depends(get_current_user)):
    """Get system monitoring status - all data from real endpoints, no hardcoded values."""
    import asyncio
    
    # OPTIMIZED: Use cache to reduce load on frequent requests
    current_time = time.time()
    if _monitor_cache["data"] and (current_time - _monitor_cache["timestamp"]) < CACHE_TTL:
        return _monitor_cache["data"]
    
    # Start with empty structure - will be populated from real endpoints
    base_data = {}
    
    # Get base monitoring data with reasonable timeout (max 3 seconds) - OPTIMIZED
    try:
        loop = asyncio.get_event_loop()
        monitor_result = await asyncio.wait_for(
            loop.run_in_executor(None, monitor_run),
            timeout=3.0  # Reduced to 3 seconds for faster response
        )
        # Use results only if successful
        if isinstance(monitor_result, dict):
            base_data.update(monitor_result)
        else:
            base_data["error"] = "Invalid monitor response"
    except asyncio.TimeoutError:
        base_data["error"] = "Monitor timeout - endpoint not responding"
        print("Monitor timeout - endpoint not responding")
    except Exception as e:
        print(f"Error in monitor_run(): {e}")
        import traceback
        traceback.print_exc()
        base_data["error"] = f"Monitor error: {str(e)}"
    
    # Get network monitoring with reasonable timeout (max 4 seconds) - OPTIMIZED
    # Increased slightly to allow network_monitor to complete
    try:
        loop = asyncio.get_event_loop()
        network_data = await asyncio.wait_for(
            loop.run_in_executor(None, network_monitor),
            timeout=4.0  # Increased to 4 seconds to allow network_monitor to complete
        )
        base_data["network"] = network_data
    except asyncio.TimeoutError:
        base_data["network"] = {"error": "timeout - network endpoint not responding"}
        print("Network monitor timeout - endpoint not responding")
    except Exception as e:
        print(f"Network monitor error: {e}")
        import traceback
        traceback.print_exc()
        base_data["network"] = {"error": str(e)}
    
    # Calculate and add computed fields for Frontend compatibility - only if we have real data
    # CPU percent from load_avg
    if isinstance(base_data.get("load_avg"), dict) and base_data["load_avg"].get("1min") is not None:
        base_data["cpu_percent"] = base_data["load_avg"]["1min"] * 100
    elif "error" not in base_data:
        base_data["cpu_percent"] = None  # Use None instead of 0 to indicate missing data
    
    # Memory percent
    if isinstance(base_data.get("memory"), dict):
        mem_total = base_data["memory"].get("total")
        mem_available = base_data["memory"].get("available")
        
        # Handle string values from /proc/meminfo (e.g., "1234567 kB")
        if isinstance(mem_total, str):
            mem_total = int(mem_total.replace("kB", "").replace(" ", "").strip()) if mem_total.replace("kB", "").replace(" ", "").strip().isdigit() else None
        if isinstance(mem_available, str):
            mem_available = int(mem_available.replace("kB", "").replace(" ", "").strip()) if mem_available.replace("kB", "").replace(" ", "").strip().isdigit() else None
        
        if mem_total and mem_total > 0:
            base_data["memory_percent"] = ((mem_total - (mem_available or 0)) / mem_total) * 100
        else:
            base_data["memory_percent"] = None  # Use None instead of 0
    elif "error" not in base_data:
        base_data["memory_percent"] = None
    
    # Disk percent
    if isinstance(base_data.get("disk"), dict):
        disk_total = base_data["disk"].get("total_gb")
        disk_used = base_data["disk"].get("used_gb")
        if disk_total and disk_total > 0:
            base_data["disk_used_percent"] = (disk_used / disk_total) * 100
        else:
            base_data["disk_used_percent"] = None  # Use None instead of 0
    elif "error" not in base_data:
        base_data["disk_used_percent"] = None
    
    # Network RX/TX
    if isinstance(base_data.get("network"), dict) and "error" not in base_data["network"]:
        network = base_data["network"]
        # Try different possible structures (network_monitor returns stats.total.rx_mbps)
        stats = network.get("stats", {})
        total = stats.get("total", {}) if isinstance(stats, dict) else {}
        base_data["network_rx_mbps"] = total.get("rx_mbps") or network.get("rx_mbps") or network.get("rx")
        base_data["network_tx_mbps"] = total.get("tx_mbps") or network.get("tx_mbps") or network.get("tx")
        connections = network.get("connections", {})
        base_data["network_connections"] = connections.get("total") if isinstance(connections, dict) else None
        
        # Calculate packets per second
        try:
            import psutil
            net_io = psutil.net_io_counters()
            if net_io:
                # Get previous values from cache if available
                prev_cache = _monitor_cache.get("prev_net_io", {})
                prev_packets = prev_cache.get("packets", 0)
                prev_time = prev_cache.get("time", time.time())
                current_packets = net_io.packets_sent + net_io.packets_recv
                time_diff = time.time() - prev_time
                if time_diff > 0 and prev_packets > 0:
                    packets_per_sec = (current_packets - prev_packets) / time_diff
                    base_data["network_packets_per_sec"] = max(0, packets_per_sec)  # Ensure non-negative
                    _monitor_cache["prev_net_io"] = {"packets": current_packets, "time": time.time()}
                else:
                    # First run or no previous data
                    base_data["network_packets_per_sec"] = 0
                    _monitor_cache["prev_net_io"] = {"packets": current_packets, "time": time.time()}
            else:
                base_data["network_packets_per_sec"] = None
        except ImportError:
            # psutil not available
            base_data["network_packets_per_sec"] = None
        except Exception as e:
            print(f"Error calculating network packets per sec: {e}")
            base_data["network_packets_per_sec"] = None
    else:
        base_data["network_rx_mbps"] = None
        base_data["network_tx_mbps"] = None
        base_data["network_connections"] = None
        base_data["network_packets_per_sec"] = None
    
    # Disk I/O (for Frontend compatibility)
    if isinstance(base_data.get("disk"), dict):
        disk = base_data["disk"]
        # Get disk read/write from available data
        base_data["disk_read_mbps"] = disk.get("read_mbps") or disk.get("read")
        base_data["disk_write_mbps"] = disk.get("write_mbps") or disk.get("write")
    else:
        base_data["disk_read_mbps"] = None
        base_data["disk_write_mbps"] = None
    
    # Uptime
    try:
        import psutil
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        base_data["uptime_days"] = uptime_seconds / 86400  # Convert to days
    except Exception as e:
        print(f"Error getting uptime: {e}")
        base_data["uptime_days"] = None
    
    # Kernel Metrics (Context Switches, Interrupts, Processes)
    try:
        from app.services.live_kernel_metrics import get_kernel_metrics
        kernel_metrics = get_kernel_metrics()
        
        # Get context switches and interrupts from /proc/stat
        try:
            with open("/proc/stat", "r") as f:
                for line in f:
                    if line.startswith("ctxt"):
                        # Context switches: ctxt 1234567890
                        parts = line.split()
                        if len(parts) >= 2:
                            base_data.setdefault("kernel_metrics", {})["context_switches"] = int(parts[1])
                    elif line.startswith("intr"):
                        # Interrupts: intr 1234567890 ...
                        parts = line.split()
                        if len(parts) >= 2:
                            base_data.setdefault("kernel_metrics", {})["interrupts"] = int(parts[1])
        except Exception as e:
            print(f"Error reading /proc/stat: {e}")
            base_data.setdefault("kernel_metrics", {})["context_switches"] = None
            base_data.setdefault("kernel_metrics", {})["interrupts"] = None
        
        # Get process count
        try:
            import psutil
            process_count = len(psutil.pids())
            base_data.setdefault("kernel_metrics", {})["processes"] = process_count
        except Exception as e:
            print(f"Error getting process count: {e}")
            base_data.setdefault("kernel_metrics", {})["processes"] = None
            
    except Exception as e:
        print(f"Error getting kernel metrics: {e}")
        base_data["kernel_metrics"] = {
            "context_switches": None,
            "interrupts": None,
            "processes": None
        }
    
    # Update cache
    _monitor_cache["data"] = base_data
    _monitor_cache["timestamp"] = time.time()
    
    return base_data

