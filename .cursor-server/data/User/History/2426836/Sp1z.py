"""Backup API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.backup_service import backup_service, BackupType
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/backup", tags=["backup"])


class BackupPostgreSQLRequest(BaseModel):
    """PostgreSQL backup request."""
    db_name: str
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: Optional[str] = None


class BackupMySQLRequest(BaseModel):
    """MySQL backup request."""
    db_name: str
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: Optional[str] = None


class BackupDockerVolumeRequest(BaseModel):
    """Docker volume backup request."""
    volume_name: str


@router.post("/postgresql")
async def backup_postgresql(
    req: BackupPostgreSQLRequest,
    current_user: dict = Depends(get_current_user)
):
    """Backup PostgreSQL database."""
    result = backup_service.backup_postgresql(
        db_name=req.db_name,
        host=req.host,
        port=req.port,
        user=req.user,
        password=req.password
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Backup failed"))
    
    return result


@router.post("/mysql")
async def backup_mysql(
    req: BackupMySQLRequest,
    current_user: dict = Depends(get_current_user)
):
    """Backup MySQL database."""
    result = backup_service.backup_mysql(
        db_name=req.db_name,
        host=req.host,
        port=req.port,
        user=req.user,
        password=req.password
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Backup failed"))
    
    return result


@router.post("/docker-volume")
async def backup_docker_volume(
    req: BackupDockerVolumeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Backup Docker volume."""
    result = backup_service.backup_docker_volume(req.volume_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Backup failed"))
    
    return result


@router.get("/list")
async def list_backups(
    backup_type: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List backups."""
    backup_type_enum = None
    if backup_type:
        try:
            backup_type_enum = BackupType(backup_type)
        except ValueError:
            pass
    
    return {
        "backups": backup_service.list_backups(backup_type=backup_type_enum, limit=limit)
    }


@router.get("/verify/{backup_id}")
async def verify_backup(
    backup_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Verify backup integrity."""
    result = backup_service.verify_backup(backup_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Verification failed"))
    
    return result


@router.delete("/{backup_id}")
async def delete_backup(
    backup_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a backup."""
    result = backup_service.delete_backup(backup_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Delete failed"))
    
    return result

