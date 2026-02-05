"""Monitoring API endpoints."""
from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(prefix="/api/monitor", tags=["monitor"])
settings = get_settings()

# Import monitoring tools
try:
    from tools.monitor import run as monitor_run
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
    from tools.network_monitor import run as network_monitor
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
    
    return base_data

