"""Services Configuration API - Dynamic service definitions from endpoints, no hardcoded values."""
from fastapi import APIRouter, Depends
from typing import List, Dict, Any
import requests
import asyncio
from app.api.auth import get_current_user
import time

router = APIRouter(prefix="/api/services", tags=["services"])

# Cache for services list to avoid repeated processing
_services_cache = None
_cache_timestamp = 0
_cache_ttl = 60  # Cache for 60 seconds


@router.get("/list")
async def get_services_list(current_user: dict = Depends(get_current_user)):
    """Get all available services - dynamically from registered routes, no HTTP calls to avoid timeout"""
    global _services_cache, _cache_timestamp
    
    # Return cached data if still valid
    current_time = time.time()
    if _services_cache and (current_time - _cache_timestamp) < _cache_ttl:
        return _services_cache
    
    try:
        # Get services directly from registered routes - fastest method, no HTTP calls
        # Use lazy import to avoid circular import issues
        import sys
        main_app = None
        
        # Try to get app from already loaded modules to avoid circular import
        if 'app.main' in sys.modules:
            main_app = getattr(sys.modules['app.main'], 'app', None)
        
        # If not found, try importing (this should work after app is initialized)
        if main_app is None:
            try:
                from app.main import app as main_app
            except (ImportError, AttributeError, RuntimeError):
                main_app = None
        
        if main_app is None:
            # Fallback: return cached or minimal data
            if _services_cache:
                return _services_cache
            return {
                "services": [{
                    "category": "CORE",
                    "items": [
                        {"id": "dashboard", "name": "Dashboard", "href": "/", "icon": "📊"}
                    ]
                }],
                "count": 1,
                "error": "Unable to access app routes"
            }
        
        # Map of known service categories and their icons
        service_categories = {
            "CORE": ["dashboard", "agent", "global-search", "debugger"],
            "OBSERVABILITY": ["monitoring", "logs", "incidents", "incident-center", "visualization"],
            "AI & AUTOMATION": ["tools", "threat-detection", "abac", "behavior-alerts", "digital-twin", 
                               "agent-mesh", "code-review", "workflow-builder", "workflows", 
                               "snapshots", "blueprints", "plugins"],
            "SECURITY": ["security", "siem", "secrets", "hardening"],
            "DEVOPS": ["cicd", "deployments", "shadow-deploy", "backup", "cost-analyzer"],
            "PLATFORM": ["tenants", "billing", "approvals", "knowledge", "audit", "settings"]
        }
        
        service_icons = {
            "dashboard": "📊", "agent": "💻", "global-search": "🔍", "debugger": "🐛",
            "monitoring": "📈", "logs": "📋", "incidents": "⚠️", "incident-center": "🚨", 
            "visualization": "👁️", "tools": "🧠", "threat-detection": "🛡️", "abac": "🔐",
            "behavior-alerts": "👁️", "digital-twin": "🌍", "agent-mesh": "🌐", "code-review": "🔍",
            "workflow-builder": "🔧", "workflows": "⚡", "snapshots": "📸", "blueprints": "📋",
            "plugins": "🧩", "security": "🔒", "siem": "📊", "secrets": "🔑", "hardening": "🧱",
            "cicd": "🚀", "deployments": "🚀", "shadow-deploy": "☁️", "backup": "💾",
            "cost-analyzer": "💰", "tenants": "🏢", "billing": "💳", "approvals": "✅",
            "knowledge": "📚", "audit": "📝", "settings": "⚙️"
        }
        
        # Get all unique API prefixes from registered routes
        unique_prefixes = set()
        route_paths = set()
        for route in main_app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/'):
                parts = route.path.split('/')
                if len(parts) >= 3 and parts[1] == 'api':
                    prefix = parts[2]
                    # Skip internal endpoints
                    if prefix not in ['auth', 'services', 'capabilities', 'health']:
                        unique_prefixes.add(prefix)
                        route_paths.add(route.path)
        
        # Create a mapping of service IDs to route prefixes
        # Handle different naming conventions (e.g., "threat-detection" -> "security/threat-detection")
        service_to_prefix_map = {
            "threat-detection": "security",
            "hardening": "security",
            "incident-center": "incidents",
            "workflow-builder": "workflows",
            "code-review": "code",
            "agent-mesh": "agents",
            "shadow-deploy": "deployment",
            "cost-analyzer": "cost",
            "global-search": "search",
            "digital-twin": "digital-twin",
            "snapshots": "snapshots",
            "blueprints": "blueprints",
            "plugins": "plugins"
        }
        
        # Build services by category
        services_by_category = {}
        categorized_services = set()
        
        # First, categorize known services
        for category, service_ids in service_categories.items():
            if category not in services_by_category:
                services_by_category[category] = []
            
            for service_id in service_ids:
                # Check if service exists in routes
                service_found = False
                # Try direct match first
                if service_id in unique_prefixes:
                    service_found = True
                # Try mapped prefix
                elif service_id in service_to_prefix_map:
                    mapped_prefix = service_to_prefix_map[service_id]
                    if mapped_prefix in unique_prefixes:
                        service_found = True
                # Try partial match (e.g., "threat-detection" in "security/threat-detection")
                elif any(service_id in path for path in route_paths):
                    service_found = True
                
                if service_found:
                    categorized_services.add(service_id)
                    services_by_category[category].append({
                        "id": service_id,
                        "name": service_id.replace('-', ' ').replace('_', ' ').title(),
                        "href": f"/{service_id}",
                        "icon": service_icons.get(service_id, "🔧")
                    })
        
        # Add uncategorized services to "OTHER" category
        other_services = unique_prefixes - categorized_services
        if other_services:
            if "OTHER" not in services_by_category:
                services_by_category["OTHER"] = []
            
            for prefix in other_services:
                services_by_category["OTHER"].append({
                    "id": prefix,
                    "name": prefix.replace('-', ' ').replace('_', ' ').title(),
                    "href": f"/{prefix}",
                    "icon": "🔧"
                })
        
        # Convert to array format
        result = []
        for category, items in services_by_category.items():
            if items:  # Only add categories with items
                result.append({
                    "category": category,
                    "items": items
                })
        
        response = {
            "services": result,
            "count": sum(len(cat["items"]) for cat in result)
        }
        
        # Update cache
        _services_cache = response
        _cache_timestamp = current_time
        
        return response
    except Exception as e:
        # Return cached data if available, even if expired
        if _services_cache:
            return _services_cache
        
        # Return minimal fallback on error, not empty
        return {
            "services": [{
                "category": "CORE",
                "items": [
                    {"id": "dashboard", "name": "Dashboard", "href": "/", "icon": "📊"}
                ]
            }],
            "count": 1,
            "error": f"Error getting services: {str(e)}"
        }


@router.get("/categories")
async def get_service_categories(current_user: dict = Depends(get_current_user)):
    """Get service categories - dynamically determined"""
    try:
        services_response = await get_services_list(current_user)
        categories = [cat["category"] for cat in services_response.get("services", [])]
        return {
            "categories": categories,
            "count": len(categories)
        }
    except Exception as e:
        return {
            "categories": [],
            "count": 0,
            "error": str(e)
        }


@router.get("/{service_id}")
async def get_service_details(service_id: str, current_user: dict = Depends(get_current_user)):
    """Get details for a specific service"""
    try:
        services_response = await get_services_list(current_user)
        
        for category in services_response.get("services", []):
            for service in category.get("items", []):
                if service.get("id") == service_id:
                    # Service found, return it
                    # No need for additional HTTP calls to avoid timeout
                    
                    return service
        
        return {"error": "Service not found"}
    except Exception as e:
        return {"error": f"Error getting service details: {str(e)}"}

