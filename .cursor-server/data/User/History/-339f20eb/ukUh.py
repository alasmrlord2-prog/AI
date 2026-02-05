"""Incident Management API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.services.incident_service import incident_service, IncidentStatus
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


class CreateIncidentRequest(BaseModel):
    """Create incident request."""
    title: str
    description: str
    severity: str = "medium"
    root_cause: Optional[str] = None


class UpdateIncidentRequest(BaseModel):
    """Update incident request."""
    status: Optional[str] = None
    root_cause: Optional[str] = None
    actions_taken: Optional[List[Dict]] = None


@router.post("")
async def create_incident(
    req: CreateIncidentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new incident."""
    incident = incident_service.create_incident(
        title=req.title,
        description=req.description,
        severity=req.severity,
        detected_by=current_user.get("email", "unknown"),
        root_cause=req.root_cause
    )
    
    return incident


@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get incident by ID."""
    incident = incident_service.get_incident(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident


@router.put("/{incident_id}")
async def update_incident(
    incident_id: str,
    req: UpdateIncidentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update incident."""
    incident = incident_service.update_incident(
        incident_id=incident_id,
        status=req.status,
        root_cause=req.root_cause,
        actions_taken=req.actions_taken,
        user=current_user.get("email", "unknown")
    )
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident


@router.get("")
async def list_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List incidents."""
    return {
        "incidents": incident_service.list_incidents(
            status=status,
            severity=severity,
            limit=limit
        )
    }


@router.get("/stats/today")
async def get_today_incidents_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get today's incidents statistics - optimized with SQL query and timeout protection."""
    from datetime import datetime, date
    import sqlite3
    import asyncio
    
    try:
        # Use direct SQL query for better performance with timeout protection
        db_path = incident_service.db_path
        
        # Run database query in executor with timeout (max 3 seconds)
        loop = asyncio.get_event_loop()
        
        def query_db():
            conn = sqlite3.connect(db_path, timeout=2.0)  # 2 second connection timeout
            cursor = conn.cursor()
            
            # Get today's date as string (YYYY-MM-DD)
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            
            # Query incidents detected today using SQL LIKE for date matching
            # This is much faster than loading all incidents and filtering in Python
            # Use COALESCE to handle NULL values from SUM
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_today,
                    COALESCE(SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END), 0) as resolved_today
                FROM incidents
                WHERE detected_at LIKE ?
            """, (f"{today_str}%",))
            
            row = cursor.fetchone()
            total_today = int(row[0]) if row and row[0] is not None else 0
            resolved_today = int(row[1]) if row and row[1] is not None else 0
            open_today = total_today - resolved_today
            
            conn.close()
            return {
                "total_today": total_today,
                "resolved_today": resolved_today,
                "open_today": open_today
            }
        
        # Execute with reasonable timeout (max 10 seconds)
        result = await asyncio.wait_for(
            loop.run_in_executor(None, query_db),
            timeout=10.0  # Increased to 10 seconds to allow proper execution
        )
        return result
        
    except asyncio.TimeoutError:
        # Return error on timeout, not default values
        print("Timeout getting today's stats - endpoint not responding")
        return {
            "error": "timeout - database endpoint not responding",
            "total_today": None,
            "resolved_today": None,
            "open_today": None
        }
    except Exception as e:
        # Return actual error, not default values
        print(f"Error getting today's stats: {e}")
        return {
            "error": str(e),
            "total_today": None,
            "resolved_today": None,
            "open_today": None
        }


@router.post("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    root_cause: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Resolve an incident."""
    incident = incident_service.update_incident(
        incident_id=incident_id,
        status=IncidentStatus.RESOLVED.value,
        root_cause=root_cause,
        user=current_user.get("email", "unknown")
    )
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident

