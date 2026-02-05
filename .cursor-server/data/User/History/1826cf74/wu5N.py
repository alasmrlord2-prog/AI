"""Alert Manager - Telegram and Dashboard alerts."""
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertManager:
    """Alert manager for sending notifications."""
    
    def __init__(self, telegram_bot_token: Optional[str] = None, telegram_chat_id: Optional[str] = None):
        """Initialize alert manager."""
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.dashboard_alerts: List[Dict] = []
        self.max_dashboard_alerts = 100
    
    def send_telegram_alert(
        self,
        message: str,
        level: AlertLevel = AlertLevel.INFO
    ) -> Dict:
        """Send alert to Telegram."""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return {
                "success": False,
                "error": "Telegram not configured"
            }
        
        try:
            # Format message with emoji based on level
            emoji_map = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.ERROR: "❌",
                AlertLevel.CRITICAL: "🚨"
            }
            
            formatted_message = f"{emoji_map.get(level, 'ℹ️')} {message}"
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": formatted_message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Alert sent to Telegram"
                }
            else:
                return {
                    "success": False,
                    "error": f"Telegram API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_dashboard_alert(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        source: Optional[str] = None
    ) -> Dict:
        """Add alert to dashboard."""
        alert = {
            "id": f"alert_{datetime.now().timestamp()}",
            "title": title,
            "message": message,
            "level": level.value,
            "source": source or "system",
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        
        self.dashboard_alerts.append(alert)
        
        # Keep only last N alerts
        if len(self.dashboard_alerts) > self.max_dashboard_alerts:
            self.dashboard_alerts = self.dashboard_alerts[-self.max_dashboard_alerts:]
        
        return alert
    
    def send_alert(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        source: Optional[str] = None,
        send_telegram: bool = True
    ) -> Dict:
        """Send alert to both Telegram and Dashboard."""
        # Add to dashboard
        alert = self.add_dashboard_alert(title, message, level, source)
        
        # Send to Telegram if enabled
        telegram_result = None
        if send_telegram:
            telegram_message = f"<b>{title}</b>\n{message}"
            telegram_result = self.send_telegram_alert(telegram_message, level)
        
        return {
            "dashboard_alert": alert,
            "telegram": telegram_result
        }
    
    def get_dashboard_alerts(
        self,
        level: Optional[AlertLevel] = None,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Get dashboard alerts."""
        alerts = self.dashboard_alerts.copy()
        
        # Filter by level
        if level:
            alerts = [a for a in alerts if a["level"] == level.value]
        
        # Filter unread
        if unread_only:
            alerts = [a for a in alerts if not a.get("read", False)]
        
        # Sort by timestamp descending
        alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit
        return alerts[:limit]
    
    def mark_alert_read(self, alert_id: str) -> Dict:
        """Mark alert as read."""
        for alert in self.dashboard_alerts:
            if alert["id"] == alert_id:
                alert["read"] = True
                return {
                    "success": True,
                    "alert": alert
                }
        
        return {
            "success": False,
            "error": "Alert not found"
        }
    
    def clear_alerts(self, level: Optional[AlertLevel] = None) -> Dict:
        """Clear alerts."""
        if level:
            self.dashboard_alerts = [a for a in self.dashboard_alerts if a["level"] != level.value]
        else:
            self.dashboard_alerts = []
        
        return {
            "success": True,
            "message": "Alerts cleared"
        }


# Global instance (will be configured from settings)
alert_manager = AlertManager()

