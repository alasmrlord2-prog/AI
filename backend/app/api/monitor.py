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
def monitor_status():
    """Get system monitoring status."""
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
        network_data = network_monitor()
        base_data["network"] = network_data
    except Exception as e:
        print(f"Network monitor error: {e}")
        base_data["network"] = {"error": str(e)}
    
    # Calculate and add computed fields for Frontend compatibility
    # CPU percent from load_avg
    if isinstance(base_data.get("load_avg"), dict) and base_data["load_avg"].get("1min"):
        base_data["cpu_percent"] = base_data["load_avg"]["1min"] * 100
    
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
    
    # Disk percent
    if isinstance(base_data.get("disk"), dict):
        disk_total = base_data["disk"].get("total_gb", 0)
        disk_used = base_data["disk"].get("used_gb", 0)
        if disk_total > 0:
            base_data["disk_used_percent"] = (disk_used / disk_total) * 100
    
    # Network RX/TX
    if isinstance(base_data.get("network"), dict):
        network = base_data["network"]
        # Try different possible structures (network_monitor returns stats.total.rx_mbps)
        stats = network.get("stats", {})
        total = stats.get("total", {}) if isinstance(stats, dict) else {}
        base_data["network_rx_mbps"] = total.get("rx_mbps") or network.get("rx_mbps") or network.get("rx") or 0
        base_data["network_tx_mbps"] = total.get("tx_mbps") or network.get("tx_mbps") or network.get("tx") or 0
        base_data["network_connections"] = network.get("connections", {}).get("total", 0) if isinstance(network.get("connections"), dict) else 0
    
    return base_data

