"""Prometheus metrics API endpoints."""
from fastapi import APIRouter, Response
from app.core.config import get_settings

router = APIRouter(tags=["metrics"])
settings = get_settings()

# Import Prometheus
try:
    from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
    PROMETHEUS_ENABLED = True
    
    # Metrics - defined globally to avoid redefinition
    if not hasattr(router, '_metrics_initialized'):
        chat_requests_total = Counter('chat_requests_total', 'Total chat requests')
        chat_errors_total = Counter('chat_errors_total', 'Total chat errors')
        active_users = Gauge('active_users', 'Active users')
        system_cpu_load = Gauge('system_cpu_load', 'CPU load average')
        system_memory_used = Gauge('system_memory_used_bytes', 'Memory used in bytes')
        system_disk_used = Gauge('system_disk_used_bytes', 'Disk used in bytes')
        
        # Network metrics
        network_rx_bytes = Gauge('network_rx_bytes_total', 'Network RX bytes')
        network_tx_bytes = Gauge('network_tx_bytes_total', 'Network TX bytes')
        network_rx_mbps = Gauge('network_rx_mbps', 'Network RX Mbps')
        network_tx_mbps = Gauge('network_tx_mbps', 'Network TX Mbps')
        network_connections_total = Gauge('network_connections_total', 'Total network connections')
        router._metrics_initialized = True
except ImportError:
    PROMETHEUS_ENABLED = False
    chat_requests_total = None
    chat_errors_total = None
    active_users = None
    system_cpu_load = None
    system_memory_used = None
    system_disk_used = None
    network_rx_bytes = None
    network_tx_bytes = None
    network_rx_mbps = None
    network_tx_mbps = None
    network_connections_total = None


@router.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint."""
    if not PROMETHEUS_ENABLED or not settings.PROMETHEUS_ENABLED:
        return {"error": "Prometheus not enabled"}
    
    # Update metrics from monitor
    try:
        from tools.monitor import run as monitor_run
        mon_data = monitor_run()
        
        if system_cpu_load and "load_avg" in mon_data and isinstance(mon_data["load_avg"], dict):
            system_cpu_load.set(mon_data["load_avg"].get("1min", 0))
        
        if system_memory_used and "memory" in mon_data:
            mem = mon_data["memory"]
            if isinstance(mem, dict) and "total" in mem and "available" in mem:
                try:
                    total_kb = int(str(mem["total"]).replace(" kB", "").replace(" ", ""))
                    avail_kb = int(str(mem["available"]).replace(" kB", "").replace(" ", ""))
                    used_kb = total_kb - avail_kb
                    system_memory_used.set(used_kb * 1024)
                except (ValueError, AttributeError):
                    pass
        
        if system_disk_used and "disk" in mon_data:
            disk = mon_data["disk"]
            if isinstance(disk, dict) and "used_gb" in disk:
                try:
                    system_disk_used.set(int(disk["used_gb"]) * 1024 * 1024 * 1024)
                except (ValueError, TypeError):
                    pass
        
        # Update network metrics
        if "network" in mon_data and isinstance(mon_data["network"], dict):
            net_data = mon_data["network"]
            if network_rx_bytes and network_tx_bytes and "stats" in net_data and isinstance(net_data["stats"], dict):
                net_stats = net_data["stats"]
                if "total" in net_stats and isinstance(net_stats["total"], dict):
                    total = net_stats["total"]
                    try:
                        network_rx_bytes.set(int(total.get("rx_bytes", 0)))
                        network_tx_bytes.set(int(total.get("tx_bytes", 0)))
                        if network_rx_mbps and network_tx_mbps:
                            network_rx_mbps.set(float(total.get("rx_mbps", 0)))
                            network_tx_mbps.set(float(total.get("tx_mbps", 0)))
                    except (ValueError, TypeError):
                        pass
            
            if network_connections_total and "connections" in net_data and isinstance(net_data["connections"], dict):
                try:
                    network_connections_total.set(int(net_data["connections"].get("total", 0)))
                except (ValueError, TypeError):
                    pass
    except Exception as e:
        import traceback
        print(f"Error updating metrics: {e}")
        traceback.print_exc()
    
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

