"""
Live Kernel Metrics - 100% Local
مقاييس kernel مباشرة
"""
import os
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class KernelMetrics:
    """
    مقاييس kernel مباشرة
    IO latency, Kernel scheduling, Network packet drops, cgroup throttling, Disk queues
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.proc_path = Path("/proc")
    
    def get_io_latency(self) -> Dict[str, Any]:
        """حساب IO latency"""
        try:
            # قراءة من /proc/diskstats
            diskstats_path = self.proc_path / "diskstats"
            if not diskstats_path.exists():
                return {"error": "diskstats not available"}
            
            io_data = {}
            with open(diskstats_path, 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 14:
                        device = parts[2]
                        # قراءة operations, sectors, time
                        read_ios = int(parts[3])
                        read_merges = int(parts[4])
                        read_sectors = int(parts[5])
                        read_time = int(parts[6])
                        write_ios = int(parts[7])
                        write_merges = int(parts[8])
                        write_sectors = int(parts[9])
                        write_time = int(parts[10])
                        
                        total_ios = read_ios + write_ios
                        total_time = read_time + write_time
                        
                        avg_latency = (total_time / total_ios * 1000) if total_ios > 0 else 0  # milliseconds
                        
                        io_data[device] = {
                            "read_ios": read_ios,
                            "write_ios": write_ios,
                            "read_time_ms": read_time,
                            "write_time_ms": write_time,
                            "avg_latency_ms": avg_latency,
                            "total_ios": total_ios
                        }
            
            return {"io_latency": io_data, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            log_warning(f"Error reading IO latency: {e}")
            return {"error": str(e)}
    
    def get_kernel_scheduling(self) -> Dict[str, Any]:
        """مقاييس kernel scheduling"""
        try:
            # قراءة من /proc/stat
            stat_path = self.proc_path / "stat"
            if not stat_path.exists():
                return {"error": "stat not available"}
            
            cpu_stats = {}
            with open(stat_path, 'r') as f:
                for line in f:
                    if line.startswith("cpu"):
                        parts = line.split()
                        cpu_name = parts[0]
                        
                        if cpu_name == "cpu":
                            # Overall CPU
                            user = int(parts[1])
                            nice = int(parts[2])
                            system = int(parts[3])
                            idle = int(parts[4])
                            iowait = int(parts[5]) if len(parts) > 5 else 0
                            irq = int(parts[6]) if len(parts) > 6 else 0
                            softirq = int(parts[7]) if len(parts) > 7 else 0
                            
                            total = user + nice + system + idle + iowait + irq + softirq
                            
                            cpu_stats["overall"] = {
                                "user": user,
                                "nice": nice,
                                "system": system,
                                "idle": idle,
                                "iowait": iowait,
                                "irq": irq,
                                "softirq": softirq,
                                "total": total,
                                "idle_percent": (idle / total * 100) if total > 0 else 0,
                                "system_percent": (system / total * 100) if total > 0 else 0
                            }
            
            return {"scheduling": cpu_stats, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            log_warning(f"Error reading kernel scheduling: {e}")
            return {"error": str(e)}
    
    def get_network_packet_drops(self) -> Dict[str, Any]:
        """حساب packet drops"""
        try:
            # قراءة من /proc/net/dev
            netdev_path = self.proc_path / "net" / "dev"
            if not netdev_path.exists():
                return {"error": "net/dev not available"}
            
            packet_stats = {}
            with open(netdev_path, 'r') as f:
                for line in f:
                    if ':' in line:
                        parts = line.split(':')
                        interface = parts[0].strip()
                        data = parts[1].split()
                        
                        if len(data) >= 16:
                            rx_packets = int(data[0])
                            rx_drops = int(data[4])
                            tx_packets = int(data[8])
                            tx_drops = int(data[12])
                            
                            total_packets = rx_packets + tx_packets
                            total_drops = rx_drops + tx_drops
                            
                            drop_rate = (total_drops / total_packets * 100) if total_packets > 0 else 0
                            
                            packet_stats[interface] = {
                                "rx_packets": rx_packets,
                                "rx_drops": rx_drops,
                                "tx_packets": tx_packets,
                                "tx_drops": tx_drops,
                                "total_drops": total_drops,
                                "drop_rate_percent": drop_rate
                            }
            
            return {"packet_drops": packet_stats, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            log_warning(f"Error reading packet drops: {e}")
            return {"error": str(e)}
    
    def get_cgroup_throttling(self) -> Dict[str, Any]:
        """مقاييس cgroup throttling"""
        try:
            cgroup_path = Path("/sys/fs/cgroup")
            if not cgroup_path.exists():
                return {"error": "cgroup not available"}
            
            throttling_data = {}
            
            # البحث عن cgroups
            for cgroup_dir in cgroup_path.iterdir():
                if cgroup_dir.is_dir():
                    cpu_stat = cgroup_dir / "cpu.stat"
                    if cpu_stat.exists():
                        try:
                            with open(cpu_stat, 'r') as f:
                                stats = {}
                                for line in f:
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        stats[key.strip()] = int(value.strip())
                                
                                throttling_data[cgroup_dir.name] = stats
                        except:
                            pass
            
            return {"cgroup_throttling": throttling_data, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            log_warning(f"Error reading cgroup throttling: {e}")
            return {"error": str(e)}
    
    def get_disk_queues(self) -> Dict[str, Any]:
        """مقاييس disk queues"""
        try:
            disk_io = psutil.disk_io_counters(perdisk=True)
            
            queue_data = {}
            for device, io in disk_io.items():
                queue_data[device] = {
                    "read_count": io.read_count,
                    "write_count": io.write_count,
                    "read_bytes": io.read_bytes,
                    "write_bytes": io.write_bytes,
                    "read_time": io.read_time,
                    "write_time": io.write_time,
                    "read_avg_time": (io.read_time / io.read_count * 1000) if io.read_count > 0 else 0,
                    "write_avg_time": (io.write_time / io.write_count * 1000) if io.write_count > 0 else 0
                }
            
            return {"disk_queues": queue_data, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            log_warning(f"Error reading disk queues: {e}")
            return {"error": str(e)}
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """الحصول على جميع المقاييس"""
        return {
            "io_latency": self.get_io_latency(),
            "kernel_scheduling": self.get_kernel_scheduling(),
            "network_packet_drops": self.get_network_packet_drops(),
            "cgroup_throttling": self.get_cgroup_throttling(),
            "disk_queues": self.get_disk_queues(),
            "timestamp": datetime.now().isoformat()
        }


# Global instance
_kernel_metrics: Optional[KernelMetrics] = None


def get_kernel_metrics() -> KernelMetrics:
    """الحصول على مثيل مقاييس kernel"""
    global _kernel_metrics
    if _kernel_metrics is None:
        _kernel_metrics = KernelMetrics()
    return _kernel_metrics

