"""
Distributed Agent Mesh - 100% Local
شبكة agents موزعة
"""
import socket
import threading
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning, log_error


class AgentNode:
    """عقدة agent"""
    def __init__(
        self,
        node_id: str,
        host: str,
        port: int,
        capabilities: List[str],
        status: str = "active"
    ):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.capabilities = capabilities
        self.status = status  # "active", "inactive", "failed"
        self.last_heartbeat: Optional[datetime] = None
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "metadata": self.metadata
        }


class DistributedAgentMesh:
    """
    شبكة agents موزعة
    Agents صغيرة على كل سيرفر، يتواصلوا مع بعض، كل واحد يراقب الثاني
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.nodes: Dict[str, AgentNode] = {}
        self.local_node_id: Optional[str] = None
        self.mesh_port = 9999
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 60  # seconds
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.message_queue: List[Dict[str, Any]] = []
        
        # إنشاء local node
        self._create_local_node()
    
    def _create_local_node(self):
        """إنشاء local node"""
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self.local_node_id = f"node_{hostname}_{local_ip}"
        
        local_node = AgentNode(
            node_id=self.local_node_id,
            host=local_ip,
            port=self.mesh_port,
            capabilities=["monitoring", "security", "deployment"],
            status="active"
        )
        local_node.last_heartbeat = datetime.now()
        
        self.nodes[self.local_node_id] = local_node
        log_info(f"Created local agent node: {self.local_node_id}")
    
    def start(self):
        """بدء شبكة agents"""
        if self.running:
            return
        
        self.running = True
        
        # بدء server للاستماع
        self._start_server()
        
        # بدء heartbeat thread
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        # بدء discovery thread
        discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        discovery_thread.start()
        
        log_info("Distributed Agent Mesh started")
    
    def stop(self):
        """إيقاف شبكة agents"""
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
        
        log_info("Distributed Agent Mesh stopped")
    
    def _start_server(self):
        """بدء server للاستماع"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.mesh_port))
            self.server_socket.settimeout(1.0)
            
            # thread للاستماع
            listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            listen_thread.start()
        except Exception as e:
            log_error(f"Error starting mesh server: {e}")
    
    def _listen_loop(self):
        """حلقة الاستماع للرسائل"""
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(4096)
                message = json.loads(data.decode())
                self._handle_message(message, addr)
            except socket.timeout:
                continue
            except Exception as e:
                log_warning(f"Error in listen loop: {e}")
    
    def _handle_message(self, message: Dict[str, Any], addr: tuple):
        """معالجة رسالة واردة"""
        msg_type = message.get("type")
        
        if msg_type == "heartbeat":
            self._handle_heartbeat(message, addr)
        elif msg_type == "task":
            self._handle_task(message, addr)
        elif msg_type == "discovery":
            self._handle_discovery(message, addr)
    
    def _handle_heartbeat(self, message: Dict[str, Any], addr: tuple):
        """معالجة heartbeat"""
        node_id = message.get("node_id")
        if node_id and node_id != self.local_node_id:
            if node_id not in self.nodes:
                # node جديد
                node = AgentNode(
                    node_id=node_id,
                    host=addr[0],
                    port=message.get("port", self.mesh_port),
                    capabilities=message.get("capabilities", []),
                    status="active"
                )
                self.nodes[node_id] = node
                log_info(f"Discovered new node: {node_id} at {addr[0]}")
            
            self.nodes[node_id].last_heartbeat = datetime.now()
            self.nodes[node_id].status = "active"
    
    def _handle_task(self, message: Dict[str, Any], addr: tuple):
        """معالجة task"""
        task = message.get("task")
        if task and task.get("target") == self.local_node_id:
            # task موجه لنا
            log_info(f"Received task: {task.get('action')}")
            # يمكن إضافة منطق لتنفيذ المهمة
    
    def _handle_discovery(self, message: Dict[str, Any], addr: tuple):
        """معالجة discovery request"""
        # إرسال response مع معلومات local node
        response = {
            "type": "discovery_response",
            "node_id": self.local_node_id,
            "host": self.nodes[self.local_node_id].host,
            "port": self.mesh_port,
            "capabilities": self.nodes[self.local_node_id].capabilities
        }
        
        self._send_message(response, addr)
    
    def _send_message(self, message: Dict[str, Any], addr: tuple):
        """إرسال رسالة"""
        try:
            data = json.dumps(message).encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data, addr)
            sock.close()
        except Exception as e:
            log_warning(f"Error sending message: {e}")
    
    def _heartbeat_loop(self):
        """حلقة إرسال heartbeat"""
        while self.running:
            try:
                # إرسال heartbeat لجميع nodes المعروفة
                for node_id, node in self.nodes.items():
                    if node_id != self.local_node_id:
                        heartbeat = {
                            "type": "heartbeat",
                            "node_id": self.local_node_id,
                            "host": self.nodes[self.local_node_id].host,
                            "port": self.mesh_port,
                            "capabilities": self.nodes[self.local_node_id].capabilities,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        self._send_message(heartbeat, (node.host, node.port))
                
                # تحديث local node heartbeat
                self.nodes[self.local_node_id].last_heartbeat = datetime.now()
                
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                log_warning(f"Error in heartbeat loop: {e}")
                time.sleep(self.heartbeat_interval)
    
    def _discovery_loop(self):
        """حلقة discovery"""
        while self.running:
            try:
                # إرسال discovery broadcast
                discovery = {
                    "type": "discovery",
                    "node_id": self.local_node_id,
                    "host": self.nodes[self.local_node_id].host,
                    "port": self.mesh_port
                }
                
                # Broadcast على الشبكة المحلية
                broadcast_addr = ('255.255.255.255', self.mesh_port)
                self._send_message(discovery, broadcast_addr)
                
                time.sleep(60)  # كل دقيقة
            except Exception as e:
                log_warning(f"Error in discovery loop: {e}")
                time.sleep(60)
    
    def check_failed_nodes(self):
        """التحقق من nodes فاشلة"""
        now = datetime.now()
        failed_nodes = []
        
        for node_id, node in self.nodes.items():
            if node_id == self.local_node_id:
                continue
            
            if node.last_heartbeat:
                time_since_heartbeat = (now - node.last_heartbeat).total_seconds()
                if time_since_heartbeat > self.heartbeat_timeout:
                    node.status = "failed"
                    failed_nodes.append(node_id)
                    log_warning(f"Node {node_id} marked as failed (no heartbeat for {time_since_heartbeat:.0f}s)")
        
        return failed_nodes
    
    def get_available_node(self, capability: str) -> Optional[AgentNode]:
        """الحصول على node متاح بقدرة معينة"""
        active_nodes = [
            node for node in self.nodes.values()
            if node.status == "active"
            and capability in node.capabilities
            and node.node_id != self.local_node_id
        ]
        
        if active_nodes:
            # اختيار node عشوائي (يمكن تحسينه)
            return active_nodes[0]
        
        return None
    
    def send_task(self, target_node_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """إرسال task لـnode"""
        if target_node_id not in self.nodes:
            return {"success": False, "error": "Node not found"}
        
        node = self.nodes[target_node_id]
        
        message = {
            "type": "task",
            "from": self.local_node_id,
            "task": {
                "target": target_node_id,
                **task
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self._send_message(message, (node.host, node.port))
        
        return {"success": True, "message": f"Task sent to {target_node_id}"}
    
    def get_mesh_status(self) -> Dict[str, Any]:
        """الحصول على حالة الشبكة"""
        active_nodes = [n for n in self.nodes.values() if n.status == "active"]
        failed_nodes = [n for n in self.nodes.values() if n.status == "failed"]
        
        return {
            "local_node_id": self.local_node_id,
            "total_nodes": len(self.nodes),
            "active_nodes": len(active_nodes),
            "failed_nodes": len(failed_nodes),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "running": self.running
        }


# Global instance
_agent_mesh: Optional[DistributedAgentMesh] = None


def get_agent_mesh() -> DistributedAgentMesh:
    """الحصول على مثيل شبكة agents"""
    global _agent_mesh
    if _agent_mesh is None:
        _agent_mesh = DistributedAgentMesh()
    return _agent_mesh

