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
    """Get today's incidents statistics - allows guest access."""
    """Get today's incidents statistics."""
    from datetime import datetime, timedelta
    
    # Get all incidents
    all_incidents = incident_service.list_incidents(limit=1000)
    
    # Filter today's incidents
    today = datetime.now().date()
    today_incidents = []
    resolved_today = 0
    
    for incident in all_incidents:
        detected_at = incident.get("detected_at")
        if detected_at:
            try:
                # Parse ISO format datetime
                if isinstance(detected_at, str):
                    incident_date = datetime.fromisoformat(detected_at.replace('Z', '+00:00')).date()
                else:
                    incident_date = detected_at.date() if hasattr(detected_at, 'date') else today
                
                if incident_date == today:
                    today_incidents.append(incident)
                    if incident.get("status") == "resolved":
                        resolved_today += 1
            except Exception:
                continue
    
    return {
        "total_today": len(today_incidents),
        "resolved_today": resolved_today,
        "open_today": len(today_incidents) - resolved_today
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

