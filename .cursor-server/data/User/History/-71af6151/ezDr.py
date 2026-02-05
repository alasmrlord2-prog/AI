#!/usr/bin/env python3
"""
Comprehensive endpoint and page verification script
فحص شامل لجميع الـ endpoints والصفحات
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Base paths
BASE_DIR = Path("/home/ai/ai-agent")
BACKEND_API_DIR = BASE_DIR / "backend/app/api"
FRONTEND_APP_DIR = BASE_DIR / "frontend/app"

# Expected mappings: Frontend Page -> Backend Endpoint
EXPECTED_MAPPINGS = {
    # Core
    "/": ["/api/monitor", "/api/chat"],
    "/monitor": ["/api/monitor"],
    "/monitoring": ["/api/monitor"],
    "/global-search": ["/api/search"],
    "/debugger": ["/api/debugger"],
    
    # Observability
    "/logs": ["/api/logs"],
    "/incidents": ["/api/incidents"],
    "/incident-center": ["/api/incidents/command-center"],
    "/visualization": ["/api/visualization"],
    
    # AI & Automation
    "/tools": ["/api/tools"],
    "/threat-detection": ["/api/security/threat-detection"],
    "/abac": ["/api/abac"],
    "/behavior-alerts": ["/api/alerts/behavior"],
    "/digital-twin": ["/api/digital-twin"],
    "/agent-mesh": ["/api/agents/mesh"],
    "/code-review": ["/api/code/review"],
    "/workflow-builder": ["/api/workflows/builder"],
    "/workflows": ["/api/workflows"],
    "/snapshots": ["/api/snapshots"],
    "/blueprints": ["/api/blueprints"],
    "/plugins": ["/api/plugins"],
    
    # Security
    "/security": ["/api/security", "/api/security/threat-detection", "/api/alerts/behavior", "/api/secrets", "/api/security/hardening"],
    "/siem": ["/api/security/siem"],
    "/secrets": ["/api/secrets"],
    "/hardening": ["/api/security/hardening"],
    
    # DevOps
    "/cicd": ["/api/cicd", "/api/backup", "/api/deployment/shadow"],
    "/backup": ["/api/backup"],
    "/cost-analyzer": ["/api/cost"],
    "/performance-tuner": ["/api/performance/tuner"],
    
    # Platform
    "/tenants": ["/api/billing"],
    "/billing": ["/api/billing"],
    "/approvals": ["/api/pending-actions"],
    "/knowledge": ["/api/knowledge"],
    "/audit": ["/api/audit"],
    "/settings": ["/api/settings"],
}

def find_backend_routers() -> Dict[str, str]:
    """Find all backend API routers and their prefixes."""
    routers = {}
    
    if not BACKEND_API_DIR.exists():
        return routers
    
    for api_file in BACKEND_API_DIR.glob("*.py"):
        if api_file.name == "__init__.py":
            continue
            
        try:
            content = api_file.read_text(encoding="utf-8")
            # Find router prefix
            match = re.search(r'router\s*=\s*APIRouter\(prefix=["\']([^"\']+)["\']', content)
            if match:
                prefix = match.group(1)
                routers[api_file.stem] = prefix
        except Exception as e:
            print(f"Error reading {api_file}: {e}")
    
    return routers

def find_backend_endpoints() -> Set[str]:
    """Find all backend endpoints from router files."""
    endpoints = set()
    
    if not BACKEND_API_DIR.exists():
        return endpoints
    
    for api_file in BACKEND_API_DIR.glob("*.py"):
        if api_file.name == "__init__.py":
            continue
            
        try:
            content = api_file.read_text(encoding="utf-8")
            
            # Find router prefix
            prefix_match = re.search(r'router\s*=\s*APIRouter\(prefix=["\']([^"\']+)["\']', content)
            if not prefix_match:
                continue
                
            prefix = prefix_match.group(1)
            
            # Find all route decorators
            route_patterns = [
                r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']',
                r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']',
            ]
            
            for pattern in route_patterns:
                for match in re.finditer(pattern, content):
                    route_path = match.group(2)
                    if route_path:
                        full_path = f"{prefix}{route_path}" if route_path.startswith("/") else f"{prefix}/{route_path}"
                        endpoints.add(full_path)
                    else:
                        # Empty route means root of prefix
                        endpoints.add(prefix)
        except Exception as e:
            print(f"Error reading {api_file}: {e}")
    
    return endpoints

def find_frontend_pages() -> List[str]:
    """Find all frontend pages."""
    pages = []
    
    if not FRONTEND_APP_DIR.exists():
        return pages
    
    for page_file in FRONTEND_APP_DIR.rglob("page.tsx"):
        # Get relative path from app directory
        rel_path = page_file.relative_to(FRONTEND_APP_DIR)
        # Convert to URL path
        if rel_path.parent.name == "app":
            path = "/"
        else:
            path = "/" + str(rel_path.parent).replace("\\", "/")
        pages.append(path)
    
    return sorted(set(pages))

def find_frontend_api_calls(page_path: str) -> Set[str]:
    """Find all API calls in a frontend page."""
    api_calls = set()
    
    page_file = FRONTEND_APP_DIR / page_path.lstrip("/") / "page.tsx"
    if page_path == "/":
        page_file = FRONTEND_APP_DIR / "page.tsx"
    
    if not page_file.exists():
        return api_calls
    
    try:
        content = page_file.read_text(encoding="utf-8")
        
        # Find apiRequest calls
        api_request_pattern = r'apiRequest\(["\']([^"\']+)["\']'
        for match in re.finditer(api_request_pattern, content):
            endpoint = match.group(1)
            api_calls.add(endpoint)
        
        # Find fetch calls to API
        fetch_pattern = r'fetch\([^,]+["\']([^"\']*\/api\/[^"\']+)["\']'
        for match in re.finditer(fetch_pattern, content):
            endpoint = match.group(1)
            api_calls.add(endpoint)
    except Exception as e:
        print(f"Error reading {page_file}: {e}")
    
    return api_calls

def check_service_connections() -> Dict[str, bool]:
    """Check external service connections."""
    services = {
        "Ollama": "http://localhost:11434",
        "Prometheus": "http://localhost:9090",
        "Grafana": "http://localhost:3001",
    }
    
    import urllib.request
    import urllib.error
    
    results = {}
    for name, url in services.items():
        try:
            req = urllib.request.Request(url, method="GET")
            urllib.request.urlopen(req, timeout=2)
            results[name] = True
        except:
            results[name] = False
    
    return results

def main():
    print("=" * 80)
    print("🔍 Comprehensive System Verification - فحص شامل للنظام")
    print("=" * 80)
    print()
    
    # 1. Find backend routers
    print("📡 Finding Backend API Routers...")
    backend_routers = find_backend_routers()
    print(f"   Found {len(backend_routers)} API routers")
    print()
    
    # 2. Find backend endpoints
    print("🔗 Finding Backend Endpoints...")
    backend_endpoints = find_backend_endpoints()
    print(f"   Found {len(backend_endpoints)} endpoints")
    print()
    
    # 3. Find frontend pages
    print("📄 Finding Frontend Pages...")
    frontend_pages = find_frontend_pages()
    print(f"   Found {len(frontend_pages)} pages")
    print()
    
    # 4. Check each page's API calls
    print("🔍 Checking Page-to-Endpoint Mappings...")
    page_endpoint_map = {}
    issues = []
    
    for page in frontend_pages:
        api_calls = find_frontend_api_calls(page)
        page_endpoint_map[page] = api_calls
        
        # Check if endpoints exist in backend
        for endpoint in api_calls:
            # Normalize endpoint (remove query params)
            normalized = endpoint.split("?")[0]
            if normalized not in backend_endpoints and not any(normalized.startswith(e.rstrip("/")) for e in backend_endpoints):
                issues.append({
                    "type": "missing_endpoint",
                    "page": page,
                    "endpoint": endpoint,
                    "severity": "error"
                })
    
    print(f"   Checked {len(page_endpoint_map)} pages")
    print(f"   Found {len(issues)} potential issues")
    print()
    
    # 5. Check service connections
    print("🔌 Checking External Services...")
    services = check_service_connections()
    for name, status in services.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {name}: {'Connected' if status else 'Not Connected'}")
    print()
    
    # 6. Generate report
    print("=" * 80)
    print("📊 VERIFICATION REPORT")
    print("=" * 80)
    print()
    
    print(f"✅ Backend Routers: {len(backend_routers)}")
    print(f"✅ Backend Endpoints: {len(backend_endpoints)}")
    print(f"✅ Frontend Pages: {len(frontend_pages)}")
    print(f"{'⚠️' if issues else '✅'} Issues Found: {len(issues)}")
    print()
    
    if issues:
        print("⚠️ ISSUES DETECTED:")
        print("-" * 80)
        for issue in issues[:20]:  # Show first 20
            print(f"  {issue['type']}: {issue['page']} -> {issue['endpoint']}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
        print()
    
    # 7. Backend routers summary
    print("📡 BACKEND API ROUTERS:")
    print("-" * 80)
    for router_name, prefix in sorted(backend_routers.items()):
        print(f"  {prefix:40s} ({router_name})")
    print()
    
    # 8. Frontend pages summary
    print("📄 FRONTEND PAGES:")
    print("-" * 80)
    for page in sorted(frontend_pages):
        endpoints = page_endpoint_map.get(page, set())
        endpoint_count = len(endpoints)
        print(f"  {page:40s} ({endpoint_count} API calls)")
    print()
    
    # 9. Save detailed report
    report = {
        "backend_routers": backend_routers,
        "backend_endpoints": sorted(list(backend_endpoints)),
        "frontend_pages": frontend_pages,
        "page_endpoint_map": {k: list(v) for k, v in page_endpoint_map.items()},
        "service_status": services,
        "issues": issues,
        "summary": {
            "total_routers": len(backend_routers),
            "total_endpoints": len(backend_endpoints),
            "total_pages": len(frontend_pages),
            "total_issues": len(issues),
        }
    }
    
    report_file = BASE_DIR / "SYSTEM_VERIFICATION_REPORT.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"💾 Detailed report saved to: {report_file}")
    print()
    
    print("=" * 80)
    if issues:
        print("⚠️  Some issues detected. Please review the report above.")
    else:
        print("✅ All checks passed! System is properly connected.")
    print("=" * 80)

if __name__ == "__main__":
    main()

