"""Settings API endpoints."""
from fastapi import APIRouter
from app.models.settings import SettingsModel
from app.utils.helpers import load_settings, save_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
def get_settings_endpoint():
    """Get current settings."""
    return load_settings().dict()


@router.put("")
def update_settings_endpoint(new_settings: SettingsModel):
    """Update settings."""
    save_settings(new_settings)
    return {"ok": True}

