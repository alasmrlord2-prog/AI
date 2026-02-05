"""Services Configuration API - Dynamic service definitions from endpoints, no hardcoded values."""
from fastapi import APIRouter, Depends
from typing import List, Dict, Any
import requests
import asyncio
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("/list")
async def get_services_list(current_user: dict = Depends(get_current_user)):
    """Get all available services - dynamically from capabilities endpoint"""
    try:
        # Get services from capabilities endpoint
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.get("http://localhost:8000/api/capabilities", timeout=3)
        )
        if response.status_code == 200:
            capabilities_data = response.json()
            capabilities = capabilities_data.get("capabilities", [])
            
            # Build service categories from actual capabilities
            services_by_category = {}
            
            for cap in capabilities:
                category = cap.get("category", "OTHER")
                if category not in services_by_category:
                    services_by_category[category] = []
                
                service_item = {
                    "id": cap.get("name", "").lower().replace(" ", "-"),
                    "name": cap.get("name", ""),
                    "href": f"/{cap.get('name', '').lower().replace(' ', '-')}",
                    "icon": cap.get("icon", "🔧"),
                    "description": cap.get("description", "")
                }
                services_by_category[category].append(service_item)
            
            # Convert to array format
            result = []
            for category, items in services_by_category.items():
                result.append({
                    "category": category,
                    "items": items
                })
            
            return {
                "services": result,
                "count": sum(len(cat["items"]) for cat in result)
            }
        else:
            # If capabilities endpoint fails, try to get from registered routes
            try:
                from app.main import app as main_app
                unique_prefixes = set()
                for route in main_app.routes:
                    if hasattr(route, 'path') and route.path.startswith('/api/'):
                        parts = route.path.split('/')
                        if len(parts) >= 3 and parts[1] == 'api':
                            unique_prefixes.add(parts[2])
                
                # Build basic service list from routes
                services = []
                for prefix in unique_prefixes:
                    if prefix not in ['auth', 'services']:
                        services.append({
                            "id": prefix,
                            "name": prefix.replace('-', ' ').title(),
                            "href": f"/{prefix}",
                            "icon": "🔧"
                        })
                
                return {
                    "services": [{
                        "category": "AVAILABLE",
                        "items": services
                    }],
                    "count": len(services)
                }
            except Exception as e:
                return {
                    "services": [],
                    "count": 0,
                    "error": f"Failed to get services: {str(e)}"
                }
    except Exception as e:
        return {
            "services": [],
            "count": 0,
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
                    # Try to get additional info from capabilities
                    try:
                        loop = asyncio.get_event_loop()
                        response = await loop.run_in_executor(
                            None,
                            lambda: requests.get(f"http://localhost:8000/api/capabilities/check/{service_id}", timeout=2)
                        )
                        if response.status_code == 200:
                            cap_data = response.json()
                            service["available"] = cap_data.get("available", False)
                    except:
                        pass
                    
                    return service
        
        return {"error": "Service not found"}
    except Exception as e:
        return {"error": f"Error getting service details: {str(e)}"}

