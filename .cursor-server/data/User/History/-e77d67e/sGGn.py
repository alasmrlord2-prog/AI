"""Dashboard API endpoints."""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import os
import subprocess
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics - all data from real endpoints, no hardcoded values"""
    import asyncio
    import requests
    from app.core.config import get_settings
    from fastapi import FastAPI
    from app.main import app as main_app
    
    def get_stats_data():
        try:
            # Count active modules by checking actual registered routes in the app
            modules_count = None
            try:
                # Get all unique route prefixes from registered routes
                unique_prefixes = set()
                for route in main_app.routes:
                    if hasattr(route, 'path') and route.path.startswith('/api/'):
                        # Extract prefix (e.g., /api/monitor -> monitor)
                        parts = route.path.split('/')
                        if len(parts) >= 3 and parts[1] == 'api':
                            unique_prefixes.add(parts[2])
                modules_count = len(unique_prefixes)
            except Exception as e:
                print(f"Error counting modules: {e}")
                # Try to get from capabilities endpoint if available
                try:
                    response = requests.get("http://localhost:8000/api/capabilities", timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        modules_count = len(data.get("capabilities", []))
                except:
                    modules_count = None  # Keep as None if all methods fail
            
            # Check AI Status (Ollama) - real endpoint check
            ai_status = "❌"
            ai_status_text = "Not Available"
            try:
                settings = get_settings()
                ollama_url = settings.OLLAMA_URL
                
                # Quick health check
                response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    ai_status = "✅"
                    ai_status_text = "Operational"
                else:
                    ai_status = "⚠️"
                    ai_status_text = "Unavailable"
            except Exception as e:
                ai_status = "⚠️"
                ai_status_text = f"Error: {str(e)[:30]}"
            
            # Calculate Security Health from real threat detection endpoint
            security_health = None
            try:
                # Get threat detection summary from actual endpoint
                response = requests.get("http://localhost:8000/api/security/threat-detection/summary?hours=24", timeout=3)
                if response.status_code == 200:
                    threat_summary = response.json()
                    
                    total_threats = threat_summary.get("total_threats", 0)
                    critical = threat_summary.get("critical", 0)
                    high = threat_summary.get("high", 0)
                    
                    # Calculate health: 100% - (threats * penalty)
                    # Critical threats reduce health by 5% each, high by 2%
                    threat_penalty = (critical * 5) + (high * 2)
                    security_health = max(0, 100 - threat_penalty)
                    
                    # Also check hardening status from real endpoint
                    try:
                        hardening_response = requests.get("http://localhost:8000/api/security/hardening/status", timeout=2)
                        if hardening_response.status_code == 200:
                            hardening_status = hardening_response.json()
                            # If hardening is enabled and working, add bonus
                            if hardening_status.get("enabled", False):
                                security_health = min(100, security_health + 5)
                    except:
                        pass  # If hardening endpoint fails, continue without bonus
                else:
                    # If endpoint fails, try direct service call
                    from app.services.ai_threat_detection import get_threat_detector
                    threat_detector = get_threat_detector()
                    threat_summary = threat_detector.get_threat_summary(24)
                    
                    total_threats = threat_summary.get("total_threats", 0)
                    critical = threat_summary.get("critical", 0)
                    high = threat_summary.get("high", 0)
                    
                    threat_penalty = (critical * 5) + (high * 2)
                    security_health = max(0, 100 - threat_penalty)
                    
            except Exception as e:
                print(f"Error calculating security health: {e}")
                # If all methods fail, keep as None to indicate error
                security_health = None
            
            return {
                "total_modules": modules_count,
                "ai_status": ai_status,
                "ai_status_text": ai_status_text,
                "security_health": round(security_health, 1) if security_health is not None else None
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            # Return error indicators, not default values
            return {
                "total_modules": None,
                "ai_status": "❌",
                "ai_status_text": f"Error: {str(e)[:50]}",
                "security_health": None
            }
    
    try:
        # Run with timeout (max 5 seconds)
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, get_stats_data),
            timeout=5.0
        )
        return result
    except asyncio.TimeoutError:
        # Return timeout error, not default values
        return {
            "total_modules": None,
            "ai_status": "⚠️",
            "ai_status_text": "Timeout - endpoints not responding",
            "security_health": None
        }
    except Exception as e:
        # Return actual error, not default values
        return {
            "total_modules": None,
            "ai_status": "❌",
            "ai_status_text": f"Error: {str(e)[:50]}",
            "security_health": None
        }

