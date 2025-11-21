"""Audit Trail Service - Track all system actions."""
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum


class ActionType(Enum):
    """Action types for audit trail."""
    API_CALL = "api_call"
    SHELL_COMMAND = "shell_command"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    SETTINGS_CHANGE = "settings_change"
    LOGIN = "login"
    LOGOUT = "logout"
    WORKFLOW_RUN = "workflow_run"
    DEPLOYMENT = "deployment"
    BACKUP = "backup"
    RESTORE = "restore"
    OTHER = "other"


class AuditService:
    """Audit trail service for tracking all system actions."""
    
    def __init__(self, db_path: str = "audit.db"):
        """Initialize audit service."""
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize audit database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                payload TEXT,
                ip TEXT,
                status TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user ON audit_logs(user)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_action ON audit_logs(action)
        """)
        
        conn.commit()
        conn.close()
    
    def log_action(
        self,
        user: str,
        action: ActionType,
        payload: Optional[Dict] = None,
        ip: Optional[str] = None,
        status: str = "success"
    ) -> int:
        """Log an action."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        payload_json = json.dumps(payload) if payload else None
        
        cursor.execute("""
            INSERT INTO audit_logs (timestamp, user, action, payload, ip, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, user, action.value, payload_json, ip, status))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def get_logs(
        self,
        user: Optional[str] = None,
        action: Optional[ActionType] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Get audit logs with filters."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if user:
            query += " AND user = ?"
            params.append(user)
        
        if action:
            query += " AND action = ?"
            params.append(action.value)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            log = {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "user": row["user"],
                "action": row["action"],
                "payload": json.loads(row["payload"]) if row["payload"] else None,
                "ip": row["ip"],
                "status": row["status"],
                "created_at": row["created_at"]
            }
            logs.append(log)
        
        conn.close()
        return logs
    
    def get_log_count(
        self,
        user: Optional[str] = None,
        action: Optional[ActionType] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> int:
        """Get count of audit logs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM audit_logs WHERE 1=1"
        params = []
        
        if user:
            query += " AND user = ?"
            params.append(user)
        
        if action:
            query += " AND action = ?"
            params.append(action.value)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def export_logs(
        self,
        output_file: str,
        user: Optional[str] = None,
        action: Optional[ActionType] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """Export logs to JSON file."""
        try:
            logs = self.get_logs(
                user=user,
                action=action,
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Large limit for export
            )
            
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "file": str(output_path),
                "count": len(logs)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
audit_service = AuditService()

