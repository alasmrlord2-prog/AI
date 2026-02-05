#!/usr/bin/env python3
"""
Comprehensive API Check - فحص شامل لجميع الـ APIs
"""
import os
import re
import json
from pathlib import Path

BASE_DIR = Path("/home/ai/ai-agent")
BACKEND_API_DIR = BASE_DIR / "backend/app/api"
FRONTEND_APP_DIR = BASE_DIR / "frontend/app"
MAIN_PY = BASE_DIR / "backend/app/main.py"

def get_all_api_files():
    """Get all API files."""
    api_files = []
    if BACKEND_API_DIR.exists():
        for f in BACKEND_API_DIR.glob("*.py"):
            if f.name != "__init__.py":
                api_files.append(f.stem)
    return sorted(api_files)

def get_routers_in_main():
    """Get all routers included in main.py."""
    routers = []
    if MAIN_PY.exists():
        content = MAIN_PY.read_text(encoding="utf-8")
        # Find all app.include_router calls
        pattern = r'app\.include_router\((\w+)(?:\.router)?\)'
        for match in re.finditer(pattern, content):
            router_name = match.group(1)
            routers.append(router_name)
    return routers

def get_imported_routers():
    """Get all routers imported in main.py."""
    imports = []
    if MAIN_PY.exists():
        content = MAIN_PY.read_text(encoding="utf-8")
        # Find imports
        pattern = r'from app\.api\.(\w+) import|from app\.api import.*?(\w+)'
        for match in re.finditer(pattern, content):
            if match.group(1):
                imports.append(match.group(1))
            elif match.group(2):
                imports.append(match.group(2))
    return imports

def check_api_file(api_file):
    """Check if API file has router definition."""
    file_path = BACKEND_API_DIR / f"{api_file}.py"
    if not file_path.exists():
        return False, "File not found"
    
    content = file_path.read_text(encoding="utf-8")
    
    # Check for router definition
    has_router = bool(re.search(r'router\s*=\s*APIRouter', content))
    
    # Count endpoints
    endpoints = len(re.findall(r'@router\.(get|post|put|delete|patch)', content))
    
    return has_router, endpoints

def main():
    print("=" * 80)
    print("🔍 Comprehensive API Check - فحص شامل لجميع الـ APIs")
    print("=" * 80)
    print()
    
    # Get all API files
    api_files = get_all_api_files()
    print(f"📁 Found {len(api_files)} API files")
    print()
    
    # Get routers in main.py
    routers_in_main = get_routers_in_main()
    print(f"📡 Found {len(routers_in_main)} routers in main.py")
    print()
    
    # Check each API file
    issues = []
    missing_in_main = []
    missing_files = []
    
    print("🔍 Checking API files...")
    print("-" * 80)
    
    for api_file in api_files:
        has_router, endpoint_count = check_api_file(api_file)
        
        # Check if router is in main.py
        router_name = api_file
        if api_file == "settings":
            router_name = "settings_router"
        elif api_file in ["websocket", "security", "filesystem", "prometheus", "agent", 
                          "cicd", "debugger", "monitoring", "audit", "backup", "incidents",
                          "workflows", "visualization", "abac", "ai_threat_detection",
                          "intelligent_log_timeline", "config_drift", "cost_analyzer",
                          "user_behavior", "global_search", "snapshot_rollback",
                          "incident_command_center", "unified_secrets", "service_dependency",
                          "kernel_metrics", "auto_hardening", "shadow_deployment",
                          "ai_performance_tuner", "behavior_alerts", "blueprint_generator",
                          "ai_code_review", "plugin_store", "ai_workflow_builder",
                          "distributed_agent_mesh", "digital_twin", "knowledge"]:
            router_name = f"{api_file}_router"
        
        if router_name not in routers_in_main and f"{router_name}.router" not in str(routers_in_main):
            missing_in_main.append(api_file)
            issues.append({
                "type": "missing_in_main",
                "file": api_file,
                "router_name": router_name
            })
        
        status = "✅" if has_router and endpoint_count > 0 else "⚠️"
        print(f"  {status} {api_file:40s} ({endpoint_count} endpoints)")
    
    print()
    
    # Check for routers in main.py that don't have files
    print("🔍 Checking for orphaned routers in main.py...")
    print("-" * 80)
    
    for router in routers_in_main:
        # Try to find corresponding file
        found = False
        for api_file in api_files:
            if router.replace("_router", "") == api_file or router == api_file:
                found = True
                break
        
        if not found and router not in ["settings_router", "websocket_router", "security_router",
                                        "filesystem_router", "prometheus_router", "agent_router",
                                        "cicd_router", "debugger_router", "monitoring_router",
                                        "audit_router", "backup_router", "incidents_router",
                                        "workflows_router", "visualization_router", "abac_router",
                                        "threat_detection_router", "timeline_router", "config_drift_router",
                                        "cost_analyzer_router", "user_behavior_router", "global_search_router",
                                        "snapshot_rollback_router", "incident_command_center_router",
                                        "unified_secrets_router", "service_dependency_router",
                                        "kernel_metrics_router", "auto_hardening_router", "shadow_deployment_router",
                                        "performance_tuner_router", "behavior_alerts_router",
                                        "blueprint_generator_router", "code_review_router", "plugin_store_router",
                                        "workflow_builder_router", "agent_mesh_router", "digital_twin_router",
                                        "knowledge_router"]:
            print(f"  ⚠️  Router '{router}' in main.py but no corresponding file found")
    
    print()
    
    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✅ Total API files: {len(api_files)}")
    print(f"✅ Total routers in main.py: {len(routers_in_main)}")
    print(f"{'⚠️' if missing_in_main else '✅'} Missing in main.py: {len(missing_in_main)}")
    print(f"{'⚠️' if issues else '✅'} Total issues: {len(issues)}")
    print()
    
    if missing_in_main:
        print("⚠️  FILES NOT IN MAIN.PY:")
        print("-" * 80)
        for file in missing_in_main:
            print(f"  - {file}")
        print()
    
    if not issues:
        print("✅ All APIs are properly registered in main.py!")
    else:
        print("⚠️  Some APIs need to be added to main.py")
    
    print("=" * 80)
    
    # Save report
    report = {
        "total_api_files": len(api_files),
        "total_routers_in_main": len(routers_in_main),
        "missing_in_main": missing_in_main,
        "issues": issues,
        "api_files": api_files,
        "routers_in_main": routers_in_main
    }
    
    report_file = BASE_DIR / "API_CHECK_REPORT.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"💾 Report saved to: {report_file}")

if __name__ == "__main__":
    main()

