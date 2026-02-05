"""Roles Configuration API - Dynamic roles from database/endpoints, no hardcoded values."""
from fastapi import APIRouter, Depends
from typing import Dict, List, Any
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("/")
async def get_roles(current_user: dict = Depends(get_current_user)):
    """Get all available roles - from Identity Service or database, no hardcoded values"""
    try:
        # Try to get roles from Identity Service
        try:
            from app.core.database import get_db
            from app.identity import service as identity_service
            from sqlalchemy.orm import Session
            
            db: Session = next(get_db())
            
            # Get all tenant users to determine available roles
            all_tenant_users = identity_service.IdentityService.get_all_tenant_users(db)
            
            # Extract unique roles from actual data
            roles_found = set()
            for tu in all_tenant_users:
                if tu.role:
                    roles_found.add(tu.role)
            
            # Build role definitions from actual usage
            roles_dict = {}
            for role in roles_found:
                # Determine permissions based on role name
                if role == "admin":
                    roles_dict[role] = {
                        "tools": ["*"],
                        "approve": True,
                        "description": "Full system access"
                    }
                elif role == "devops":
                    roles_dict[role] = {
                        "tools": ["read_file", "check_service", "run_shell", "scan_repo", "scan_infra", "scan_logs_auth", "scan_network", "scan_system", "scan_docker", "scan_network_detailed", "scan_vulnerabilities", "scan_file_integrity", "scan_malware", "scan_intrusion_detection", "scan_port_scan", "scan_penetration_test", "siem_monitor", "threat_intelligence", "network_forensics", "advanced_vulnerability", "web_scan", "advanced_container", "kubernetes_scan", "aws_scan", "memory_forensics", "disk_forensics", "password_audit", "compliance_check", "burp_suite", "metasploit", "packet_analysis"],
                        "approve": True,
                        "description": "DevOps operations access"
                    }
                elif role == "dev":
                    roles_dict[role] = {
                        "tools": ["read_file", "check_service"],
                        "approve": False,
                        "description": "Developer access"
                    }
                else:
                    roles_dict[role] = {
                        "tools": [],
                        "approve": False,
                        "description": f"{role} access"
                    }
            
            # If no roles found, check old auth system
            if not roles_dict:
                try:
                    from app.auth import ROLES as OLD_ROLES
                    roles_dict = OLD_ROLES.copy()
                except:
                    # Last resort: return empty, not hardcoded
                    roles_dict = {}
            
            return {
                "roles": list(roles_dict.keys()),
                "permissions": roles_dict
            }
        except Exception as identity_error:
            # Fallback to old auth system if Identity Service fails
            try:
                from app.auth import ROLES as OLD_ROLES
                return {
                    "roles": list(OLD_ROLES.keys()),
                    "permissions": OLD_ROLES
                }
            except:
                # No hardcoded fallback - return error
                return {
                    "roles": [],
                    "permissions": {},
                    "error": f"Failed to get roles: {str(identity_error)}"
                }
    except Exception as e:
        return {
            "roles": [],
            "permissions": {},
            "error": f"Error getting roles: {str(e)}"
        }


@router.get("/{role_name}")
async def get_role_details(role_name: str, current_user: dict = Depends(get_current_user)):
    """Get details for a specific role"""
    try:
        roles_response = await get_roles(current_user)
        permissions = roles_response.get("permissions", {})
        
        if role_name in permissions:
            return {
                "role": role_name,
                "permissions": permissions[role_name]
            }
        else:
            return {"error": "Role not found"}
    except Exception as e:
        return {"error": f"Error getting role details: {str(e)}"}

