"""Monitoring API endpoints."""
from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(prefix="/api/monitor", tags=["monitor"])
settings = get_settings()

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
async def monitor_status():
    """Get system monitoring status - optimized for speed with timeout protection."""
    import asyncio
    
    # Default response structure - return immediately if operations are slow
    base_data = {
        "load_avg": {"1min": 0, "5min": 0, "15min": 0},
        "memory": {"total": 0, "available": 0},
        "disk": {"total_gb": 0, "used_gb": 0, "free_gb": 0},
        "services": {},
        "cpu_percent": 0,
        "memory_percent": 0,
        "disk_used_percent": 0,
        "network_rx_mbps": 0,
        "network_tx_mbps": 0,
        "disk_read_mbps": 0,
        "disk_write_mbps": 0,
        "network": {"error": "timeout"}
    }
    
    # Get base monitoring data with very aggressive timeout (max 1 second)
    # If it takes longer, return default data immediately
    try:
        loop = asyncio.get_event_loop()
        monitor_result = await asyncio.wait_for(
            loop.run_in_executor(None, monitor_run),
            timeout=1.0  # Very aggressive - 1 second max
        )
        # Merge results if successful
        if isinstance(monitor_result, dict):
            base_data.update(monitor_result)
    except asyncio.TimeoutError:
        print("Monitor timeout - using default data")
        # Keep default structure - return immediately
    except Exception as e:
        print(f"Error in monitor_run(): {e}")
        # Keep default structure - return immediately
    
    # Skip network monitoring if base monitoring timed out - return immediately
    # Only try network monitoring if we have time (very short timeout)
    try:
        loop = asyncio.get_event_loop()
        network_data = await asyncio.wait_for(
            loop.run_in_executor(None, network_monitor),
            timeout=0.5  # Very short timeout - 0.5 seconds max
        )
        base_data["network"] = network_data
    except (asyncio.TimeoutError, Exception) as e:
        # Ignore network errors - it's optional
        base_data["network"] = {"error": "timeout" if isinstance(e, asyncio.TimeoutError) else str(e)}
    
    # Calculate and add computed fields for Frontend compatibility
    # CPU percent from load_avg
    if isinstance(base_data.get("load_avg"), dict) and base_data["load_avg"].get("1min"):
        base_data["cpu_percent"] = base_data["load_avg"]["1min"] * 100
    else:
        base_data["cpu_percent"] = 0
    
    # Memory percent
    if isinstance(base_data.get("memory"), dict):
        mem_total = base_data["memory"].get("total", 0)
        mem_available = base_data["memory"].get("available", 0)
        
        # Handle string values from /proc/meminfo (e.g., "1234567 kB")
        if isinstance(mem_total, str):
            mem_total = int(mem_total.replace("kB", "").replace(" ", "").strip()) if mem_total.replace("kB", "").replace(" ", "").strip().isdigit() else 0
        if isinstance(mem_available, str):
            mem_available = int(mem_available.replace("kB", "").replace(" ", "").strip()) if mem_available.replace("kB", "").replace(" ", "").strip().isdigit() else 0
        
        if mem_total > 0:
            base_data["memory_percent"] = ((mem_total - mem_available) / mem_total) * 100
        else:
            base_data["memory_percent"] = 0
    else:
        base_data["memory_percent"] = 0
    
    # Disk percent
    if isinstance(base_data.get("disk"), dict):
        disk_total = base_data["disk"].get("total_gb", 0)
        disk_used = base_data["disk"].get("used_gb", 0)
        if disk_total > 0:
            base_data["disk_used_percent"] = (disk_used / disk_total) * 100
        else:
            base_data["disk_used_percent"] = 0
    else:
        base_data["disk_used_percent"] = 0
    
    # Network RX/TX
    if isinstance(base_data.get("network"), dict):
        network = base_data["network"]
        # Try different possible structures (network_monitor returns stats.total.rx_mbps)
        stats = network.get("stats", {})
        total = stats.get("total", {}) if isinstance(stats, dict) else {}
        base_data["network_rx_mbps"] = total.get("rx_mbps") or network.get("rx_mbps") or network.get("rx") or 0
        base_data["network_tx_mbps"] = total.get("tx_mbps") or network.get("tx_mbps") or network.get("tx") or 0
        base_data["network_connections"] = network.get("connections", {}).get("total", 0) if isinstance(network.get("connections"), dict) else 0
    else:
        base_data["network_rx_mbps"] = 0
        base_data["network_tx_mbps"] = 0
        base_data["network_connections"] = 0
    
    # Disk I/O (for Frontend compatibility)
    if isinstance(base_data.get("disk"), dict):
        disk = base_data["disk"]
        # Calculate disk read/write from available data or use defaults
        base_data["disk_read_mbps"] = disk.get("read_mbps") or disk.get("read") or 0
        base_data["disk_write_mbps"] = disk.get("write_mbps") or disk.get("write") or 0
    else:
        base_data["disk_read_mbps"] = 0
        base_data["disk_write_mbps"] = 0
    
    return base_data

