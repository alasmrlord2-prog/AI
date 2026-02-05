"""
Capabilities API - Expose system capabilities and recommendations
"""
from fastapi import APIRouter
from app.utils.capability_detector import capability_detector
from app.utils.env_adapter import env_adapter

router = APIRouter(prefix="/api/capabilities", tags=["capabilities"])


@router.get("/")
async def get_capabilities():
    """Get all available capabilities and tools"""
    return {
        "capabilities": capability_detector.detect_all(),
        "scan_features": capability_detector.get_scan_features(),
        "system_info": env_adapter.get_system_info(),
        "is_container": env_adapter.is_container(),
        "is_cloud": env_adapter.is_cloud(),
    }


@router.get("/tools")
async def get_available_tools(category: str = None):
    """Get list of available tools"""
    tools = capability_detector.get_available_tools(category)
    return {
        "category": category or "all",
        "tools": tools,
        "count": len(tools),
    }


@router.get("/features")
async def get_scan_features():
    """Get available scan features"""
    return {
        "features": capability_detector.get_scan_features(),
    }


@router.get("/recommendations")
async def get_recommendations():
    """Get recommended tools to install for full functionality"""
    return {
        "recommendations": capability_detector.get_recommended_tools(),
    }


@router.get("/check/{feature}")
async def check_feature(feature: str):
    """Check if a specific feature is available"""
    is_available = capability_detector.is_feature_available(feature)
    return {
        "feature": feature,
        "available": is_available,
    }

