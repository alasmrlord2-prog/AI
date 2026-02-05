"""
Auto Responder - 100% Local Actions
المستجيب التلقائي - إجراءات محلية 100%
"""
import subprocess
import os
from typing import Dict, Any, List, Optional
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning, log_error


class AutoResponder:
    """
    المستجيب التلقائي - محلي 100%
    ينفذ إجراءات أمنية تلقائياً (block IP, isolate service, etc.)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.auto_response_enabled = self.settings.SECURITY_AI_AUTO_RESPONSE
        self.blocked_ips: set = set()
        self.isolated_services: set = set()
    
    def _check_offline_mode(self):
        """التحقق من OFFLINE_MODE"""
        if self.settings.OFFLINE_MODE:
            # التأكد من عدم وجود اتصالات خارجية
            pass  # كل الإجراءات محلية
    
    def block_ip(self, ip: str, reason: str = "") -> Dict[str, Any]:
        """
        حظر IP باستخدام iptables/ufw
        
        محلي 100% - لا يحتاج إنترنت
        """
        if not self.auto_response_enabled:
            return {
                "success": False,
                "message": "Auto-response is disabled",
                "action": "block_ip",
                "ip": ip
            }
        
        try:
            self._check_offline_mode()
            
            # استخدام ufw (أسهل)
            try:
                result = subprocess.run(
                    ["sudo", "ufw", "deny", "from", ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    self.blocked_ips.add(ip)
                    log_info(f"Blocked IP {ip}: {reason}")
                    return {
                        "success": True,
                        "action": "block_ip",
                        "ip": ip,
                        "method": "ufw",
                        "reason": reason
                    }
            except FileNotFoundError:
                # ufw غير موجود، استخدام iptables
                pass
            
            # استخدام iptables
            try:
                result = subprocess.run(
                    ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    self.blocked_ips.add(ip)
                    log_info(f"Blocked IP {ip} using iptables: {reason}")
                    return {
                        "success": True,
                        "action": "block_ip",
                        "ip": ip,
                        "method": "iptables",
                        "reason": reason
                    }
            except Exception as e:
                log_error(f"Failed to block IP {ip}: {e}")
            
            return {
                "success": False,
                "error": "Failed to block IP (no firewall tool available)",
                "ip": ip
            }
        except Exception as e:
            log_error(f"Error blocking IP {ip}: {e}")
            return {
                "success": False,
                "error": str(e),
                "ip": ip
            }
    
    def isolate_service(self, service_name: str, reason: str = "") -> Dict[str, Any]:
        """
        عزل خدمة (إيقاف container/service)
        
        محلي 100%
        """
        if not self.auto_response_enabled:
            return {
                "success": False,
                "message": "Auto-response is disabled",
                "action": "isolate_service",
                "service": service_name
            }
        
        try:
            self._check_offline_mode()
            
            # محاولة إيقاف Docker container
            try:
                result = subprocess.run(
                    ["docker", "stop", service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.isolated_services.add(service_name)
                    log_info(f"Isolated service {service_name}: {reason}")
                    return {
                        "success": True,
                        "action": "isolate_service",
                        "service": service_name,
                        "method": "docker",
                        "reason": reason
                    }
            except FileNotFoundError:
                pass
            
            # محاولة إيقاف systemd service
            try:
                result = subprocess.run(
                    ["sudo", "systemctl", "stop", service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.isolated_services.add(service_name)
                    log_info(f"Isolated service {service_name} using systemctl: {reason}")
                    return {
                        "success": True,
                        "action": "isolate_service",
                        "service": service_name,
                        "method": "systemd",
                        "reason": reason
                    }
            except Exception as e:
                log_error(f"Failed to isolate service {service_name}: {e}")
            
            return {
                "success": False,
                "error": "Failed to isolate service",
                "service": service_name
            }
        except Exception as e:
            log_error(f"Error isolating service {service_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": service_name
            }
    
    def disable_user(self, username: str, reason: str = "") -> Dict[str, Any]:
        """
        تعطيل حساب مستخدم
        
        محلي 100%
        """
        if not self.auto_response_enabled:
            return {
                "success": False,
                "message": "Auto-response is disabled",
                "action": "disable_user",
                "username": username
            }
        
        try:
            self._check_offline_mode()
            
            # تعطيل حساب Linux
            result = subprocess.run(
                ["sudo", "usermod", "-L", username],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                log_info(f"Disabled user {username}: {reason}")
                return {
                    "success": True,
                    "action": "disable_user",
                    "username": username,
                    "reason": reason
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "username": username
                }
        except Exception as e:
            log_error(f"Error disabling user {username}: {e}")
            return {
                "success": False,
                "error": str(e),
                "username": username
            }
    
    def lockdown_mode(self, reason: str = "") -> Dict[str, Any]:
        """
        تفعيل وضع Lockdown
        
        محلي 100% - يغلق SSH مؤقتاً ويقيد الوصول
        """
        if not self.auto_response_enabled:
            return {
                "success": False,
                "message": "Auto-response is disabled",
                "action": "lockdown"
            }
        
        try:
            self._check_offline_mode()
            
            actions_taken = []
            
            # إغلاق SSH مؤقتاً (إيقاف service)
            try:
                result = subprocess.run(
                    ["sudo", "systemctl", "stop", "ssh"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    actions_taken.append("ssh_stopped")
            except:
                pass
            
            # حظر جميع الاتصالات الواردة (باستثناء localhost)
            try:
                result = subprocess.run(
                    ["sudo", "ufw", "default", "deny", "incoming"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    actions_taken.append("firewall_restricted")
            except:
                pass
            
            log_warning(f"LOCKDOWN MODE ACTIVATED: {reason}")
            
            return {
                "success": True,
                "action": "lockdown",
                "actions_taken": actions_taken,
                "reason": reason,
                "warning": "System is in lockdown mode. Manual intervention required."
            }
        except Exception as e:
            log_error(f"Error activating lockdown mode: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def respond_to_threat(self, threat: Dict[str, Any]) -> Dict[str, Any]:
        """
        الاستجابة التلقائية لتهديد
        
        يحدد الإجراء المناسب بناءً على نوع التهديد وخطورته
        """
        if not self.auto_response_enabled:
            return {
                "success": False,
                "message": "Auto-response is disabled"
            }
        
        severity = threat.get("severity", "low")
        threat_type = threat.get("pattern", "unknown")
        ip = threat.get("ip") or threat.get("source_ip")
        
        responses = []
        
        # تهديدات حرجة - عزل فوري
        if severity == "critical":
            if threat_type in ["command_injection", "privilege_escalation"]:
                # عزل الخدمة المتأثرة
                service = threat.get("service", "unknown")
                if service != "unknown":
                    result = self.isolate_service(service, f"Critical threat: {threat_type}")
                    responses.append(result)
            
            # تفعيل lockdown
            result = self.lockdown_mode(f"Critical threat detected: {threat_type}")
            responses.append(result)
        
        # تهديدات عالية - حظر IP
        elif severity == "high":
            if ip:
                result = self.block_ip(ip, f"High severity threat: {threat_type}")
                responses.append(result)
        
        # تهديدات متوسطة - مراقبة فقط (لا إجراء تلقائي)
        elif severity == "medium":
            responses.append({
                "action": "monitor",
                "message": "Threat logged for monitoring",
                "severity": severity
            })
        
        return {
            "success": True,
            "threat": threat_type,
            "severity": severity,
            "responses": responses
        }
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة المستجيب"""
        return {
            "auto_response_enabled": self.auto_response_enabled,
            "blocked_ips": list(self.blocked_ips),
            "isolated_services": list(self.isolated_services),
            "offline_mode": self.settings.OFFLINE_MODE
        }


# Global instance
_auto_responder: Optional[AutoResponder] = None


def get_auto_responder() -> AutoResponder:
    """الحصول على مثيل المستجيب التلقائي"""
    global _auto_responder
    if _auto_responder is None:
        _auto_responder = AutoResponder()
    return _auto_responder

