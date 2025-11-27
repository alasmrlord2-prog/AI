"""Incident Management Service."""
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum


class IncidentStatus(Enum):
    """Incident status."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentService:
    """Incident management service."""
    
    def __init__(self, db_path: str = "incidents.db"):
        """Initialize incident service."""
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize incidents database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                severity TEXT,
                detected_at TEXT NOT NULL,
                resolved_at TEXT,
                root_cause TEXT,
                actions_taken TEXT,
                detected_by TEXT,
                resolved_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on detected_at for faster date queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_detected_at 
            ON incidents(detected_at)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incident_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                user TEXT,
                details TEXT,
                FOREIGN KEY (incident_id) REFERENCES incidents(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_incident(
        self,
        title: str,
        description: str,
        severity: str = "medium",
        detected_by: str = "system",
        root_cause: Optional[str] = None
    ) -> Dict:
        """Create a new incident."""
        incident_id = f"inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        detected_at = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO incidents (id, title, description, status, severity, detected_at, detected_by, root_cause)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (incident_id, title, description, IncidentStatus.OPEN.value, severity, detected_at, detected_by, root_cause))
        
        # Add timeline entry
        cursor.execute("""
            INSERT INTO incident_timeline (incident_id, timestamp, action, user, details)
            VALUES (?, ?, ?, ?, ?)
        """, (incident_id, detected_at, "incident_created", detected_by, json.dumps({"title": title})))
        
        conn.commit()
        conn.close()
        
        return self.get_incident(incident_id)
    
    def get_incident(self, incident_id: str) -> Optional[Dict]:
        """Get incident by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        incident = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "severity": row["severity"],
            "detected_at": row["detected_at"],
            "resolved_at": row["resolved_at"],
            "root_cause": row["root_cause"],
            "actions_taken": json.loads(row["actions_taken"]) if row["actions_taken"] else [],
            "detected_by": row["detected_by"],
            "resolved_by": row["resolved_by"],
            "created_at": row["created_at"]
        }
        
        # Get timeline
        cursor.execute("""
            SELECT * FROM incident_timeline WHERE incident_id = ? ORDER BY timestamp
        """, (incident_id,))
        timeline_rows = cursor.fetchall()
        
        timeline = []
        for t_row in timeline_rows:
            timeline.append({
                "timestamp": t_row["timestamp"],
                "action": t_row["action"],
                "user": t_row["user"],
                "details": json.loads(t_row["details"]) if t_row["details"] else {}
            })
        
        incident["timeline"] = timeline
        
        conn.close()
        return incident
    
    def update_incident(
        self,
        incident_id: str,
        status: Optional[str] = None,
        root_cause: Optional[str] = None,
        actions_taken: Optional[List[Dict]] = None,
        user: str = "system"
    ) -> Dict:
        """Update incident."""
        incident = self.get_incident(incident_id)
        if not incident:
            return {"success": False, "error": "Incident not found"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if status:
            updates.append("status = ?")
            params.append(status)
            
            if status == IncidentStatus.RESOLVED.value:
                updates.append("resolved_at = ?")
                params.append(datetime.now().isoformat())
                updates.append("resolved_by = ?")
                params.append(user)
        
        if root_cause:
            updates.append("root_cause = ?")
            params.append(root_cause)
        
        if actions_taken:
            updates.append("actions_taken = ?")
            params.append(json.dumps(actions_taken))
        
        if updates:
            params.append(incident_id)
            query = f"UPDATE incidents SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            # Add timeline entry
            timeline_details = {}
            if status:
                timeline_details["status"] = status
            if root_cause:
                timeline_details["root_cause"] = root_cause
            if actions_taken:
                timeline_details["actions_taken"] = actions_taken
            
            cursor.execute("""
                INSERT INTO incident_timeline (incident_id, timestamp, action, user, details)
                VALUES (?, ?, ?, ?, ?)
            """, (incident_id, datetime.now().isoformat(), "incident_updated", user, json.dumps(timeline_details)))
            
            conn.commit()
        
        conn.close()
        
        return self.get_incident(incident_id)
    
    def list_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """List incidents."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM incidents WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        query += " ORDER BY detected_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        incidents = []
        for row in rows:
            incident = {
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "status": row["status"],
                "severity": row["severity"],
                "detected_at": row["detected_at"],
                "resolved_at": row["resolved_at"],
                "root_cause": row["root_cause"],
                "actions_taken": json.loads(row["actions_taken"]) if row["actions_taken"] else [],
                "detected_by": row["detected_by"],
                "resolved_by": row["resolved_by"]
            }
            incidents.append(incident)
        
        conn.close()
        return incidents


# Global instance
incident_service = IncidentService()

