"""
Auto-Hardening Mode - 100% Local
وضع التحصين التلقائي
"""
import os
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning, log_error


class AutoHardening:
    """
    وضع التحصين التلقائي
    يطفئ ports, يفعل firewall rules, يحصن SSH, يتحقق من permissions
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.hardening_applied = False
        self.backup_configs: Dict[str, str] = {}
        self.actions_history: List[Dict[str, Any]] = []  # Track all hardening actions
    
    def _check_offline_mode(self):
        """التحقق من OFFLINE_MODE"""
        if self.settings.OFFLINE_MODE:
            # كل الإجراءات محلية
            pass
    
    def apply_hardening(self) -> Dict[str, Any]:
        """
        تطبيق التحصين التلقائي
        
        Actions:
        - إغلاق ports غير ضرورية
        - تفعيل firewall rules
        - تحصين SSH
        - التحقق من permissions
        - OS security baseline
        - حذف packages غير ضرورية
        - إغلاق root login
        """
        if self.hardening_applied:
            return {"success": False, "message": "Hardening already applied"}
        
        self._check_offline_mode()
        
        actions_taken = []
        errors = []
        
        try:
            # 1. إغلاق ports غير ضرورية
            result = self._close_unnecessary_ports()
            if result.get("success"):
                actions_taken.append("closed_unnecessary_ports")
            else:
                errors.append(result.get("error"))
            
            # 2. تفعيل firewall rules
            result = self._enable_firewall()
            if result.get("success"):
                actions_taken.append("enabled_firewall")
            else:
                errors.append(result.get("error"))
            
            # 3. تحصين SSH
            result = self._harden_ssh()
            if result.get("success"):
                actions_taken.append("hardened_ssh")
            else:
                errors.append(result.get("error"))
            
            # 4. التحقق من permissions
            result = self._check_permissions()
            if result.get("success"):
                actions_taken.append("checked_permissions")
            else:
                errors.append(result.get("error"))
            
            # 5. OS security baseline
            result = self._apply_os_baseline()
            if result.get("success"):
                actions_taken.append("applied_os_baseline")
            else:
                errors.append(result.get("error"))
            
            # 6. إغلاق root login
            result = self._disable_root_login()
            if result.get("success"):
                actions_taken.append("disabled_root_login")
            else:
                errors.append(result.get("error"))
            
            self.hardening_applied = True
            
            # Track this hardening action
            self.actions_history.append({
                "timestamp": datetime.now().isoformat(),
                "actions_taken": actions_taken,
                "count": len(actions_taken)
            })
            
            log_warning("AUTO-HARDENING MODE ACTIVATED")
            
            return {
                "success": True,
                "actions_taken": actions_taken,
                "errors": errors,
                "timestamp": datetime.now().isoformat(),
                "message": "System hardening applied successfully"
            }
        except Exception as e:
            log_error(f"Error applying hardening: {e}")
            return {
                "success": False,
                "error": str(e),
                "actions_taken": actions_taken
            }
    
    def _close_unnecessary_ports(self) -> Dict[str, Any]:
        """إغلاق ports غير ضرورية"""
        try:
            # استخدام ufw لإغلاق جميع المنافذ الواردة افتراضياً
            result = subprocess.run(
                ["sudo", "ufw", "default", "deny", "incoming"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {"success": True}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _enable_firewall(self) -> Dict[str, Any]:
        """تفعيل firewall"""
        try:
            # تفعيل ufw
            result = subprocess.run(
                ["sudo", "ufw", "--force", "enable"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {"success": True}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _harden_ssh(self) -> Dict[str, Any]:
        """تحصين SSH"""
        try:
            ssh_config_path = "/etc/ssh/sshd_config"
            
            if not os.path.exists(ssh_config_path):
                return {"success": False, "error": "SSH config not found"}
            
            # قراءة config الحالي
            with open(ssh_config_path, 'r') as f:
                config = f.read()
            
            # حفظ backup
            backup_path = f"{ssh_config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_path, 'w') as f:
                f.write(config)
            self.backup_configs["ssh"] = backup_path
            
            # تطبيق إعدادات أمنية
            hardening_rules = [
                "PermitRootLogin no",
                "PasswordAuthentication no",  # استخدام keys فقط
                "Protocol 2",
                "MaxAuthTries 3",
                "ClientAliveInterval 300",
                "ClientAliveCountMax 2"
            ]
            
            # إضافة القواعد إذا لم تكن موجودة
            new_config = config
            for rule in hardening_rules:
                key = rule.split()[0]
                if key not in new_config:
                    new_config += f"\n{rule}\n"
            
            # كتابة config جديد
            with open(ssh_config_path, 'w') as f:
                f.write(new_config)
            
            # إعادة تحميل SSH
            subprocess.run(["sudo", "systemctl", "reload", "ssh"], capture_output=True)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_permissions(self) -> Dict[str, Any]:
        """التحقق من permissions"""
        try:
            issues = []
            
            # التحقق من ملفات مهمة
            critical_files = [
                "/etc/passwd",
                "/etc/shadow",
                "/etc/sudoers"
            ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    mode = oct(stat.st_mode)[-3:]
                    
                    # التحقق من أن permissions آمنة
                    if file_path == "/etc/passwd" and mode != "644":
                        issues.append(f"{file_path} has insecure permissions: {mode}")
                    elif file_path == "/etc/shadow" and mode != "640":
                        issues.append(f"{file_path} has insecure permissions: {mode}")
            
            if issues:
                return {"success": False, "error": "; ".join(issues)}
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _apply_os_baseline(self) -> Dict[str, Any]:
        """تطبيق OS security baseline"""
        try:
            actions = []
            
            # تعطيل services غير ضرورية
            unnecessary_services = ["telnet", "rsh", "rlogin", "rexec"]
            
            for service in unnecessary_services:
                try:
                    result = subprocess.run(
                        ["sudo", "systemctl", "stop", service],
                        capture_output=True
                    )
                    if result.returncode == 0:
                        subprocess.run(
                            ["sudo", "systemctl", "disable", service],
                            capture_output=True
                        )
                        actions.append(f"disabled_{service}")
                except:
                    pass
            
            return {"success": True, "actions": actions}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _disable_root_login(self) -> Dict[str, Any]:
        """إغلاق root login"""
        try:
            # استخدام passwd لإغلاق root
            result = subprocess.run(
                ["sudo", "passwd", "-l", "root"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {"success": True}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة التحصين"""
        # Count actions applied today
        today = datetime.now().date()
        today_actions = 0
        for action in self.actions_history:
            action_date = datetime.fromisoformat(action["timestamp"]).date()
            if action_date == today:
                today_actions += action.get("count", 0)
        
        return {
            "hardening_applied": self.hardening_applied,
            "backup_configs": list(self.backup_configs.keys()),
            "actions_today": today_actions,
            "total_actions": sum(a.get("count", 0) for a in self.actions_history),
            "timestamp": datetime.now().isoformat()
        }


# Global instance
_auto_hardening: Optional[AutoHardening] = None


def get_auto_hardening() -> AutoHardening:
    """الحصول على مثيل Auto-Hardening"""
    global _auto_hardening
    if _auto_hardening is None:
        _auto_hardening = AutoHardening()
    return _auto_hardening

