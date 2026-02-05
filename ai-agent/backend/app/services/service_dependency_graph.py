"""
Service Dependency Graph - 100% Local
خريطة التبعيات بين الخدمات
"""
import os
import json
import subprocess
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from collections import defaultdict
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class ServiceNode:
    """عقدة خدمة"""
    def __init__(
        self,
        service_id: str,
        name: str,
        service_type: str,
        status: str = "unknown"
    ):
        self.service_id = service_id
        self.name = name
        self.service_type = service_type  # "container", "api", "database", "queue"
        self.status = status  # "running", "stopped", "error"
        self.dependencies: Set[str] = set()  # service_ids
        self.dependents: Set[str] = set()  # service_ids
        self.ports: List[int] = []
        self.connections: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "name": self.name,
            "type": self.service_type,
            "status": self.status,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "ports": self.ports,
            "connections": self.connections,
            "metadata": self.metadata
        }


class ServiceDependencyGraph:
    """
    خريطة التبعيات بين الخدمات
    يكتشف تلقائياً: Containers, Databases, Ports, Connections, HTTP calls
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.services: Dict[str, ServiceNode] = {}
        self.connections: List[Dict[str, Any]] = []
    
    def discover_services(self) -> Dict[str, Any]:
        """اكتشاف الخدمات تلقائياً"""
        discovered = []
        
        # اكتشاف Docker containers
        docker_services = self._discover_docker_services()
        discovered.extend(docker_services)
        
        # اكتشاف systemd services
        systemd_services = self._discover_systemd_services()
        discovered.extend(systemd_services)
        
        # اكتشاف databases
        db_services = self._discover_databases()
        discovered.extend(db_services)
        
        # بناء الـgraph
        for service_data in discovered:
            service = ServiceNode(
                service_id=service_data["id"],
                name=service_data["name"],
                service_type=service_data["type"],
                status=service_data.get("status", "unknown")
            )
            service.ports = service_data.get("ports", [])
            service.metadata = service_data.get("metadata", {})
            
            self.services[service.service_id] = service
        
        # اكتشاف التبعيات
        self._discover_dependencies()
        
        log_info(f"Discovered {len(self.services)} services")
        
        return {
            "services_discovered": len(self.services),
            "services": [s.to_dict() for s in self.services.values()]
        }
    
    def _discover_docker_services(self) -> List[Dict[str, Any]]:
        """اكتشاف Docker containers"""
        services = []
        
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    
                    parts = line.split('|')
                    if len(parts) >= 2:
                        name = parts[0]
                        status_str = parts[1]
                        ports_str = parts[2] if len(parts) > 2 else ""
                        
                        # تحليل الحالة
                        status = "running" if "Up" in status_str else "stopped"
                        
                        # تحليل المنافذ
                        ports = []
                        if ports_str:
                            # مثال: "0.0.0.0:8080->8080/tcp"
                            for port_part in ports_str.split(','):
                                if '->' in port_part:
                                    try:
                                        port = int(port_part.split(':')[1].split('-')[0])
                                        ports.append(port)
                                    except:
                                        pass
                        
                        service_id = f"docker_{name}"
                        services.append({
                            "id": service_id,
                            "name": name,
                            "type": "container",
                            "status": status,
                            "ports": ports,
                            "metadata": {
                                "docker_status": status_str,
                                "container_name": name
                            }
                        })
        except Exception as e:
            log_warning(f"Error discovering Docker services: {e}")
        
        return services
    
    def _discover_systemd_services(self) -> List[Dict[str, Any]]:
        """اكتشاف systemd services"""
        services = []
        
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--no-pager", "--format=json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        name = data.get("unit", "")
                        active = data.get("active", "unknown")
                        sub = data.get("sub", "unknown")
                        
                        if name.endswith(".service"):
                            service_id = f"systemd_{name}"
                            services.append({
                                "id": service_id,
                                "name": name,
                                "type": "systemd",
                                "status": "running" if active == "active" else "stopped",
                                "metadata": {
                                    "active": active,
                                    "sub": sub
                                }
                            })
                    except:
                        pass
        except Exception as e:
            log_warning(f"Error discovering systemd services: {e}")
        
        return services
    
    def _discover_databases(self) -> List[Dict[str, Any]]:
        """اكتشاف databases"""
        services = []
        
        # اكتشاف PostgreSQL
        try:
            result = subprocess.run(
                ["pg_isready"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                services.append({
                    "id": "db_postgresql",
                    "name": "PostgreSQL",
                    "type": "database",
                    "status": "running",
                    "ports": [5432],
                    "metadata": {"db_type": "postgresql"}
                })
        except:
            pass
        
        # اكتشاف MySQL
        try:
            result = subprocess.run(
                ["mysqladmin", "ping"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                services.append({
                    "id": "db_mysql",
                    "name": "MySQL",
                    "type": "database",
                    "status": "running",
                    "ports": [3306],
                    "metadata": {"db_type": "mysql"}
                })
        except:
            pass
        
        # اكتشاف Redis
        try:
            result = subprocess.run(
                ["redis-cli", "ping"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                services.append({
                    "id": "db_redis",
                    "name": "Redis",
                    "type": "database",
                    "status": "running",
                    "ports": [6379],
                    "metadata": {"db_type": "redis"}
                })
        except:
            pass
        
        return services
    
    def _discover_dependencies(self):
        """اكتشاف التبعيات بين الخدمات"""
        # تحليل المنافذ والاتصالات
        for service_id, service in self.services.items():
            # البحث عن خدمات تستخدم نفس المنافذ
            for other_id, other_service in self.services.items():
                if service_id == other_id:
                    continue
                
                # إذا كانت هناك منافذ مشتركة
                common_ports = set(service.ports) & set(other_service.ports)
                if common_ports:
                    service.dependencies.add(other_id)
                    other_service.dependents.add(service_id)
        
        # اكتشاف اتصالات HTTP (من logs أو network)
        self._discover_http_connections()
    
    def _discover_http_connections(self):
        """اكتشاف اتصالات HTTP بين الخدمات"""
        # يمكن تحسين هذا بقراءة logs أو network traffic
        # للبساطة، سنبحث عن patterns شائعة
        
        # مثال: إذا كان هناك service اسمه "api" و service اسمه "database"
        api_services = [s for s in self.services.values() if "api" in s.name.lower()]
        db_services = [s for s in self.services.values() if s.service_type == "database"]
        
        for api_service in api_services:
            for db_service in db_services:
                api_service.dependencies.add(db_service.service_id)
                db_service.dependents.add(api_service.service_id)
    
    def add_connection(
        self,
        from_service: str,
        to_service: str,
        connection_type: str = "http",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """إضافة اتصال يدوياً"""
        if from_service in self.services and to_service in self.services:
            self.services[from_service].dependencies.add(to_service)
            self.services[to_service].dependents.add(from_service)
            
            self.connections.append({
                "from": from_service,
                "to": to_service,
                "type": connection_type,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            })
    
    def get_graph(self) -> Dict[str, Any]:
        """الحصول على الـgraph الكامل"""
        return {
            "services": [s.to_dict() for s in self.services.values()],
            "connections": self.connections,
            "total_services": len(self.services),
            "total_connections": len(self.connections)
        }
    
    def get_service_dependencies(self, service_id: str) -> Dict[str, Any]:
        """الحصول على تبعيات خدمة"""
        if service_id not in self.services:
            return {"error": "Service not found"}
        
        service = self.services[service_id]
        
        # جمع جميع التبعيات (مباشرة وغير مباشرة)
        all_dependencies = set()
        to_check = [service_id]
        
        while to_check:
            current_id = to_check.pop(0)
            if current_id not in self.services:
                continue
            
            current_service = self.services[current_id]
            for dep_id in current_service.dependencies:
                if dep_id not in all_dependencies:
                    all_dependencies.add(dep_id)
                    to_check.append(dep_id)
        
        return {
            "service": service.to_dict(),
            "direct_dependencies": [self.services[d].to_dict() for d in service.dependencies if d in self.services],
            "all_dependencies": [self.services[d].to_dict() for d in all_dependencies if d in self.services],
            "dependents": [self.services[d].to_dict() for d in service.dependents if d in self.services]
        }
    
    def get_impact_analysis(self, service_id: str) -> Dict[str, Any]:
        """تحليل التأثير عند توقف خدمة"""
        if service_id not in self.services:
            return {"error": "Service not found"}
        
        # جميع الخدمات المتأثرة
        affected_services = set()
        to_check = [service_id]
        
        while to_check:
            current_id = to_check.pop(0)
            if current_id not in self.services:
                continue
            
            current_service = self.services[current_id]
            for dependent_id in current_service.dependents:
                if dependent_id not in affected_services:
                    affected_services.add(dependent_id)
                    to_check.append(dependent_id)
        
        return {
            "service": self.services[service_id].to_dict(),
            "affected_services": [self.services[s].to_dict() for s in affected_services if s in self.services],
            "impact_count": len(affected_services),
            "severity": "critical" if len(affected_services) > 5 else "high" if len(affected_services) > 0 else "low"
        }


# Global instance
_dependency_graph: Optional[ServiceDependencyGraph] = None


def get_dependency_graph() -> ServiceDependencyGraph:
    """الحصول على مثيل خريطة التبعيات"""
    global _dependency_graph
    if _dependency_graph is None:
        _dependency_graph = ServiceDependencyGraph()
    return _dependency_graph

