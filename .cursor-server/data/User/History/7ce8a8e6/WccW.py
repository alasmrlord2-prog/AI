"""Health check utilities."""
from typing import Dict, Any
from datetime import datetime
import psutil
from app.core.config import get_settings
from app.core.database import engine
from sqlalchemy import text

settings = get_settings()


def check_database() -> Dict[str, Any]:
    """Check database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Database error: {str(e)}"}


def check_disk_space() -> Dict[str, Any]:
    """Check disk space."""
    try:
        disk = psutil.disk_usage('/')
        free_percent = (disk.free / disk.total) * 100
        status = "healthy" if free_percent > 10 else "warning" if free_percent > 5 else "critical"
        return {
            "status": status,
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "free_percent": round(free_percent, 2)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_memory() -> Dict[str, Any]:
    """Check memory usage."""
    try:
        memory = psutil.virtual_memory()
        status = "healthy" if memory.percent < 80 else "warning" if memory.percent < 90 else "critical"
        return {
            "status": status,
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent": memory.percent
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_cpu() -> Dict[str, Any]:
    """Check CPU usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        status = "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 90 else "critical"
        return {
            "status": status,
            "percent": cpu_percent,
            "load_avg": load_avg
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_health_status() -> Dict[str, Any]:
    """Get overall health status."""
    checks = {
        "database": check_database(),
        "disk": check_disk_space(),
        "memory": check_memory(),
        "cpu": check_cpu(),
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Determine overall status
    statuses = [check.get("status") for check in checks.values() if isinstance(check, dict)]
    if "error" in statuses or "critical" in statuses:
        overall_status = "unhealthy"
    elif "warning" in statuses:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    checks["status"] = overall_status
    return checks

