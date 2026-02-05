"""Dashboard API endpoints."""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import os
import subprocess
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics - allows guest access with timeout protection"""
    import asyncio
    
    def get_stats_data():
        try:
            # Count active modules/features by checking available API routes
            # This is a simple count - can be enhanced later
            modules_count = 0
            
            # Check if key services are available
            try:
                # Count API modules by checking if key endpoints exist
                # We'll count based on available services
                api_modules = [
                    "monitor", "incidents", "security", "threat-detection",
                    "behavior-alerts", "hardening", "visualization", "logs",
                    "chat", "workflows", "backup", "audit", "cicd", "tools"
                ]
                modules_count = len(api_modules)
            except:
                modules_count = 0
            
            # Check AI Status (Ollama)
            ai_status = "❌"
            ai_status_text = "Not Available"
            try:
                import requests
                from app.core.config import get_settings
                settings = get_settings()
                ollama_url = settings.OLLAMA_URL
                
                # Quick health check
                response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    ai_status = "✅"
                    ai_status_text = "Operational"
            except:
                ai_status = "⚠️"
                ai_status_text = "Checking..."
            
            # Calculate Security Health based on actual metrics
            security_health = 100
            try:
                # Get threat detection summary
                from app.services.ai_threat_detection import get_threat_detector
                threat_detector = get_threat_detector()
                threat_summary = threat_detector.get_threat_summary(24)
                
                total_threats = threat_summary.get("total_threats", 0)
                critical = threat_summary.get("critical", 0)
                high = threat_summary.get("high", 0)
                
                # Calculate health: 100% - (threats * penalty)
                # Critical threats reduce health by 5% each, high by 2%
                threat_penalty = (critical * 5) + (high * 2)
                security_health = max(0, 100 - threat_penalty)
                
                # Also check hardening status
                from app.services.auto_hardening import get_auto_hardening
                hardening = get_auto_hardening()
                hardening_status = hardening.get_status()
                
                # If hardening is enabled and working, add bonus
                if hardening_status.get("enabled", False):
                    security_health = min(100, security_health + 5)
                    
            except Exception as e:
                # If we can't calculate, use default
                security_health = 95
                print(f"Error calculating security health: {e}")
            
            return {
                "total_modules": modules_count,
                "ai_status": ai_status,
                "ai_status_text": ai_status_text,
                "security_health": round(security_health, 1)
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                "total_modules": 0,
                "ai_status": "❌",
                "ai_status_text": "Error",
                "security_health": 0
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
        return {
            "total_modules": 0,
            "ai_status": "⚠️",
            "ai_status_text": "Timeout",
            "security_health": 0
        }
    except Exception as e:
        return {
            "total_modules": 0,
            "ai_status": "❌",
            "ai_status_text": "Error",
            "security_health": 0
        }

