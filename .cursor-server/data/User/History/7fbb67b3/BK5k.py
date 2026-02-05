#!/usr/bin/env python3
"""
Comprehensive System Check - فحص شامل للنظام
Checks all APIs, endpoints, frontend-backend connections, and service functionality
"""
import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import subprocess

BASE_DIR = Path("/home/ai/ai-agent")
BACKEND_API_DIR = BASE_DIR / "backend/app/api"
FRONTEND_APP_DIR = BASE_DIR / "frontend/app"
MAIN_PY = BASE_DIR / "backend/app/main.py"

def get_all_api_files() -> List[str]:
    """Get all API files."""
    api_files = []
    if BACKEND_API_DIR.exists():
        for f in BACKEND_API_DIR.glob("*.py"):
            if f.name != "__init__.py":
                api_files.append(f.stem)
    return sorted(api_files)

def get_routers_from_main() -> Dict[str, str]:
    """Get all routers from main.py with their variable names."""
    routers = {}
    if not MAIN_PY.exists():
        return routers
    
    content = MAIN_PY.read_text(encoding="utf-8")
    
    # Find imports
    import_pattern = r'from app\.api\.(\w+) import router as (\w+)'
    for match in re.finditer(import_pattern, content):
        module_name = match.group(1)
        router_var = match.group(2)
        routers[module_name] = router_var
    
    # Also check for direct imports
    direct_pattern = r'from app\.api import.*?(\w+)'
    for match in re.finditer(direct_pattern, content):
        module_name = match.group(1)
        if module_name not in routers:
            routers[module_name] = module_name
    
    return routers

def get_included_routers() -> List[str]:
    """Get all routers included in app."""
    routers = []
    if not MAIN_PY.exists():
        return routers
    
    content = MAIN_PY.read_text(encoding="utf-8")
    # Match both app.include_router(router) and app.include_router(module.router)
    pattern = r'app\.include_router\((\w+)(?:\.router)?\)'
    for match in re.finditer(pattern, content):
        router_name = match.group(1)
        routers.append(router_name)
    return routers

def check_api_file_endpoints(api_file: str) -> Tuple[bool, int, List[str]]:
    """Check API file for router and endpoints."""
    file_path = BACKEND_API_DIR / f"{api_file}.py"
    if not file_path.exists():
        return False, 0, []
    
    content = file_path.read_text(encoding="utf-8")
    
    # Check for router
    has_router = bool(re.search(r'router\s*=\s*APIRouter', content))
    
    # Find router prefix
    prefix_match = re.search(r'router\s*=\s*APIRouter\(prefix=["\']([^"\']+)["\']', content)
    prefix = prefix_match.group(1) if prefix_match else ""
    
    # Find all endpoints
    endpoints = []
    route_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']'
    for match in re.finditer(route_pattern, content):
        method = match.group(1).upper()
        path = match.group(2)
        if path:
            full_path = f"{prefix}{path}" if path.startswith("/") else f"{prefix}/{path}"
        else:
            full_path = prefix
        endpoints.append(f"{method} {full_path}")
    
    return has_router, len(endpoints), endpoints

def find_frontend_api_calls() -> Dict[str, List[str]]:
    """Find all API calls in frontend pages."""
    page_api_map = {}
    
    if not FRONTEND_APP_DIR.exists():
        return page_api_map
    
    for page_file in FRONTEND_APP_DIR.rglob("page.tsx"):
        rel_path = page_file.relative_to(FRONTEND_APP_DIR)
        if rel_path.parent.name == "app":
            page_path = "/"
        else:
            page_path = "/" + str(rel_path.parent).replace("\\", "/")
        
        try:
            content = page_file.read_text(encoding="utf-8")
            api_calls = set()
            
            # Find apiRequest calls
            api_request_pattern = r'apiRequest\(["\']([^"\']+)["\']'
            for match in re.finditer(api_request_pattern, content):
                endpoint = match.group(1)
                api_calls.add(endpoint.split("?")[0])  # Remove query params
            
            # Find fetch calls
            fetch_pattern = r'fetch\([^,]+["\']([^"\']*\/api\/[^"\']+)["\']'
            for match in re.finditer(fetch_pattern, content):
                endpoint = match.group(1)
                api_calls.add(endpoint.split("?")[0])
            
            if api_calls:
                page_api_map[page_path] = sorted(list(api_calls))
        except Exception as e:
            print(f"Error reading {page_file}: {e}")
    
    return page_api_map

def get_all_backend_endpoints() -> Set[str]:
    """Get all backend endpoints."""
    endpoints = set()
    
    for api_file in get_all_api_files():
        _, _, file_endpoints = check_api_file_endpoints(api_file)
        for endpoint in file_endpoints:
            # Extract path from "METHOD /path"
            path = endpoint.split(" ", 1)[1] if " " in endpoint else endpoint
            endpoints.add(path)
    
    return endpoints

def check_backend_health() -> bool:
    """Check if backend is running."""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8000/health", method="GET")
        urllib.request.urlopen(req, timeout=2)
        return True
    except:
        return False

def verify_endpoint_exists(endpoint: str, backend_endpoints: Set[str]) -> bool:
    """Verify if an endpoint exists in backend."""
    # Remove query params
    clean_endpoint = endpoint.split("?")[0]
    
    # Normalize trailing slashes - FastAPI handles both
    clean_endpoint_normalized = clean_endpoint.rstrip("/")
    if not clean_endpoint_normalized:
        clean_endpoint_normalized = "/"
    
    # Check exact match
    if clean_endpoint in backend_endpoints:
        return True
    
    # Check normalized version
    for be_endpoint in backend_endpoints:
        be_normalized = be_endpoint.rstrip("/")
        if not be_normalized:
            be_normalized = "/"
        
        if clean_endpoint_normalized == be_normalized:
            return True
        
        # Check if it matches a pattern endpoint (with {param})
        # Convert {param} to regex pattern
        pattern = re.sub(r'\{[^}]+\}', r'[^/]+', be_normalized)
        if re.match(f"^{pattern}$", clean_endpoint_normalized):
            return True
    
    return False

def main():
    print("=" * 80)
    print("🔍 Comprehensive System Check - فحص شامل للنظام")
    print("=" * 80)
    print()
    
    # 1. Check backend health
    print("🏥 Checking Backend Health...")
    backend_healthy = check_backend_health()
    status_icon = "✅" if backend_healthy else "❌"
    print(f"   {status_icon} Backend: {'Running' if backend_healthy else 'Not Running'}")
    print()
    
    # 2. Get all API files
    print("📁 Analyzing API Files...")
    api_files = get_all_api_files()
    print(f"   Found {len(api_files)} API files")
    print()
    
    # 3. Get routers from main.py
    print("📡 Analyzing Routers in main.py...")
    routers_from_main = get_routers_from_main()
    included_routers = get_included_routers()
    print(f"   Found {len(routers_from_main)} router imports")
    print(f"   Found {len(included_routers)} router includes")
    print()
    
    # 4. Check each API file
    print("🔍 Checking API Files and Endpoints...")
    print("-" * 80)
    api_issues = []
    total_endpoints = 0
    
    for api_file in api_files:
        has_router, endpoint_count, endpoints = check_api_file_endpoints(api_file)
        total_endpoints += endpoint_count
        
        # Check if router is included
        # Some routers are included directly (e.g., auth.router, chat.router)
        # Others are included with _router suffix (e.g., backup_router)
        # Special case: settings is imported as settings_router
        router_var = routers_from_main.get(api_file)
        is_included = False
        
        if router_var:
            # Check if the router variable is in included routers
            is_included = router_var in included_routers
        else:
            # Check if the module name itself is in included routers (for direct imports like auth, chat)
            is_included = api_file in included_routers
            
            # Special case for settings (imported as settings_router)
            if api_file == "settings" and "settings_router" in included_routers:
                is_included = True
        
        status = "✅" if has_router and is_included else "⚠️"
        if not has_router:
            api_issues.append(f"{api_file}: No router defined")
        elif not is_included:
            api_issues.append(f"{api_file}: Router not included in main.py")
        
        print(f"  {status} {api_file:40s} ({endpoint_count:3d} endpoints)")
    
    print()
    
    # 5. Get all backend endpoints
    print("🔗 Collecting Backend Endpoints...")
    backend_endpoints = get_all_backend_endpoints()
    print(f"   Found {len(backend_endpoints)} unique endpoints")
    print()
    
    # 6. Check frontend pages
    print("📄 Analyzing Frontend Pages...")
    frontend_api_map = find_frontend_api_calls()
    print(f"   Found {len(frontend_api_map)} pages with API calls")
    print()
    
    # 7. Verify frontend-backend connections
    print("🔗 Verifying Frontend-Backend Connections...")
    print("-" * 80)
    connection_issues = []
    total_frontend_calls = 0
    verified_calls = 0
    
    for page, api_calls in sorted(frontend_api_map.items()):
        total_frontend_calls += len(api_calls)
        page_issues = []
        
        for endpoint in api_calls:
            if verify_endpoint_exists(endpoint, backend_endpoints):
                verified_calls += 1
            else:
                page_issues.append(endpoint)
                connection_issues.append({
                    "page": page,
                    "endpoint": endpoint,
                    "type": "missing_endpoint"
                })
        
        status = "✅" if not page_issues else "⚠️"
        print(f"  {status} {page:40s} ({len(api_calls)} calls, {len(page_issues)} issues)")
        if page_issues:
            for issue_endpoint in page_issues[:3]:  # Show first 3
                print(f"      ⚠️  Missing: {issue_endpoint}")
            if len(page_issues) > 3:
                print(f"      ... and {len(page_issues) - 3} more")
    
    print()
    
    # 8. Summary
    print("=" * 80)
    print("📊 COMPREHENSIVE SYSTEM REPORT")
    print("=" * 80)
    print()
    
    print("✅ Backend Status:")
    print(f"   - API Files: {len(api_files)}")
    print(f"   - Total Endpoints: {total_endpoints}")
    print(f"   - Unique Endpoints: {len(backend_endpoints)}")
    print(f"   - Routers Imported: {len(routers_from_main)}")
    print(f"   - Routers Included: {len(included_routers)}")
    print(f"   - Backend Health: {'✅ Running' if backend_healthy else '❌ Not Running'}")
    print()
    
    print("✅ Frontend Status:")
    print(f"   - Pages with API Calls: {len(frontend_api_map)}")
    print(f"   - Total API Calls: {total_frontend_calls}")
    print(f"   - Verified Calls: {verified_calls}")
    print(f"   - Connection Issues: {len(connection_issues)}")
    print()
    
    print("⚠️ Issues Summary:")
    print(f"   - API File Issues: {len(api_issues)}")
    print(f"   - Connection Issues: {len(connection_issues)}")
    print()
    
    if api_issues:
        print("⚠️ API File Issues:")
        print("-" * 80)
        for issue in api_issues[:10]:
            print(f"   - {issue}")
        if len(api_issues) > 10:
            print(f"   ... and {len(api_issues) - 10} more")
        print()
    
    if connection_issues:
        print("⚠️ Frontend-Backend Connection Issues:")
        print("-" * 80)
        for issue in connection_issues[:10]:
            print(f"   - {issue['page']}: {issue['endpoint']}")
        if len(connection_issues) > 10:
            print(f"   ... and {len(connection_issues) - 10} more")
        print()
    
    # 9. Save detailed report
    report = {
        "backend": {
            "healthy": backend_healthy,
            "api_files": api_files,
            "total_endpoints": total_endpoints,
            "unique_endpoints": sorted(list(backend_endpoints)),
            "routers_imported": routers_from_main,
            "routers_included": included_routers,
            "api_issues": api_issues
        },
        "frontend": {
            "pages_with_api_calls": len(frontend_api_map),
            "total_api_calls": total_frontend_calls,
            "verified_calls": verified_calls,
            "page_api_map": frontend_api_map
        },
        "connections": {
            "total_issues": len(connection_issues),
            "issues": connection_issues
        },
        "summary": {
            "backend_status": "healthy" if backend_healthy else "unhealthy",
            "frontend_backend_connection": "good" if len(connection_issues) == 0 else "issues_found",
            "overall_status": "excellent" if backend_healthy and len(api_issues) == 0 and len(connection_issues) == 0 else "needs_attention"
        }
    }
    
    report_file = BASE_DIR / "COMPREHENSIVE_SYSTEM_CHECK.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"💾 Detailed report saved to: {report_file}")
    print()
    
    # 10. Final verdict
    print("=" * 80)
    if backend_healthy and len(api_issues) == 0 and len(connection_issues) == 0:
        print("✅ EXCELLENT: All systems are properly connected and working!")
    elif backend_healthy and len(api_issues) + len(connection_issues) < 5:
        print("✅ GOOD: System is mostly working with minor issues.")
    else:
        print("⚠️  ATTENTION NEEDED: Some issues detected. Please review above.")
    print("=" * 80)

if __name__ == "__main__":
    main()

