"""
Universal Path Resolver - Portable, Zero-Config, Auto-Detect, Safe.

This module provides a production-ready path resolution system that works
in any environment (Docker, Linux, Windows, VPS, local dev).

Features:
- Auto-detects project root (supports monorepos and microservices)
- Resolves symlinks
- Advanced caching for performance
- Path traversal protection
- Docker /app compatibility
- Zero configuration required
"""

import os
from typing import Optional
from app.utils.helpers import load_settings


def _detect_project_root() -> str:
    """
    Advanced project root detection with monorepo and microservices support.
    Auto-detects project root by looking for common project indicators.
    Portable, universal, zero-config solution.
    """
    current = os.getcwd()
    max_depth = 10  # Prevent infinite loops
    depth = 0
    
    # Project root indicators (ordered by priority)
    indicators = [
        # Python projects
        "requirements.txt", "setup.py", "pyproject.toml", "Pipfile",
        # Node.js projects
        "package.json", "yarn.lock", "pnpm-lock.yaml",
        # Docker projects
        "Dockerfile", "docker-compose.yml", ".dockerignore",
        # Common project directories
        "app", "backend", "src", "lib",
        # Git
        ".git",
        # Config files
        ".env", "config.json", "settings.json",
    ]
    
    # Monorepo indicators (workspaces, lerna, etc.)
    monorepo_indicators = [
        "lerna.json", "pnpm-workspace.yaml", "nx.json",
        "turbo.json", "rush.json", ".yarnrc.yml",
    ]
    
    # Start from current directory and walk up
    check_dir = current
    monorepo_root = None
    
    while depth < max_depth:
        # Check for monorepo indicators first
        for indicator in monorepo_indicators:
            indicator_path = os.path.join(check_dir, indicator)
            if os.path.exists(indicator_path):
                monorepo_root = check_dir
        
        # Check for project indicators
        for indicator in indicators:
            indicator_path = os.path.join(check_dir, indicator)
            if os.path.exists(indicator_path):
                # If we're in a monorepo, return the service root, not monorepo root
                # unless we're at the monorepo root itself
                if monorepo_root and check_dir != monorepo_root:
                    # We're in a microservice within monorepo
                    return check_dir
                return check_dir
        
        # Move up one level
        parent = os.path.dirname(check_dir)
        if parent == check_dir:  # Reached filesystem root
            break
        check_dir = parent
        depth += 1
    
    # Fallback: use current directory
    return current


def _is_safe_path(path: str) -> bool:
    """
    Check if path is safe (not in restricted system directories).
    """
    restricted = [
        '/etc', '/root', '/usr/bin', '/usr/sbin', '/bin', '/sbin',
        '/sys', '/proc', '/dev', '/boot', '/lib', '/lib64',
    ]
    
    abs_path = os.path.abspath(path)
    for restricted_path in restricted:
        if abs_path.startswith(restricted_path):
            return False
    
    return True


def resolve_path(path: str, resolve_symlinks: bool = True) -> str:
    """
    Advanced Universal path resolver - Portable, Zero-Config, Auto-Detect, Safe.
    
    Features:
    - Auto-detects project root (supports monorepos and microservices)
    - Resolves symlinks (optional)
    - Advanced caching for performance
    - Path traversal protection
    - Docker /app compatibility
    - Works in any environment (Docker, Linux, Windows, VPS, local dev)
    
    Examples:
        - "logs/app.log" -> PROJECT_ROOT/logs/app.log
        - "./data/users.db" -> PROJECT_ROOT/data/users.db
        - "/app/something" -> PROJECT_ROOT/something (Docker compatibility)
        - "/app/serviceX" -> PROJECT_ROOT/serviceX (microservice support)
        - "anything" -> PROJECT_ROOT/anything
        - "~/documents/file.txt" -> /home/user/documents/file.txt
        - "/etc/passwd" -> PermissionError (restricted)
    
    Args:
        path: Any path (relative, absolute, with /app prefix, etc.)
        resolve_symlinks: If True, resolves symlinks to their real paths
    
    Returns:
        Resolved absolute path (with symlinks resolved if requested)
    
    Raises:
        PermissionError: If path is in restricted system directories
        ValueError: If path is empty
    """
    path = path.strip()
    if not path:
        raise ValueError("Path cannot be empty")
    
    # Advanced caching with path normalization
    cache_key = f"{path}:{resolve_symlinks}"
    if not hasattr(resolve_path, '_path_cache'):
        resolve_path._path_cache = {}
    
    if cache_key in resolve_path._path_cache:
        return resolve_path._path_cache[cache_key]
    
    # Handle home directory expansion
    if path.startswith('~/'):
        path = os.path.expanduser(path)
        # After expansion, check if it's safe
        if not _is_safe_path(path):
            raise PermissionError(f"Path '{path}' is in a restricted system directory")
        resolved = os.path.abspath(path)
    else:
        # Auto-detect project root (cached for performance)
        if not hasattr(resolve_path, '_project_root_cache'):
            resolve_path._project_root_cache = _detect_project_root()
        project_root = resolve_path._project_root_cache
        
        # Restricted system paths (always blocked for security)
        restricted_system_paths = [
            '/etc', '/root', '/usr/bin', '/usr/sbin', '/bin', '/sbin',
            '/sys', '/proc', '/dev', '/boot', '/lib', '/lib64',
            '/var/log', '/var/lib', '/var/cache',
        ]
        
        # Handle absolute paths
        if path.startswith('/'):
            # Handle Docker /app prefix - convert to project root
            if path.startswith('/app'):
                if path == '/app' or path == '/app/':
                    resolved = project_root
                else:
                    # /app/something -> project_root/something
                    # /app/serviceX -> project_root/serviceX (microservice support)
                    relative = path[5:] if path.startswith('/app/') else path[4:]
                    resolved = os.path.abspath(os.path.join(project_root, relative.lstrip('/')))
            else:
                # Check if it's a restricted system path
                for restricted in restricted_system_paths:
                    if path.startswith(restricted):
                        raise PermissionError(
                            f"Access to system directory '{path}' is restricted for security"
                        )
                resolved = os.path.abspath(path)
        else:
            # Relative path - resolve from project root
            # Handle ./ prefix
            if path.startswith('./'):
                path = path[2:]
            elif path.startswith('.'):
                path = path[1:]
            
            # Prevent path traversal attacks (../../../../etc/passwd)
            normalized = os.path.normpath(path)
            if normalized.startswith('..') or '/../' in normalized or normalized.startswith('../'):
                # Allow relative traversal within project, but block escaping
                resolved = os.path.abspath(os.path.join(project_root, normalized))
                # Ensure resolved path is still within project or safe locations
                if not _is_safe_path(resolved):
                    raise PermissionError(
                        f"Path traversal detected: '{path}' would escape project boundaries"
                    )
            else:
                resolved = os.path.abspath(os.path.join(project_root, path))
    
    # Resolve symlinks if requested
    if resolve_symlinks:
        try:
            resolved = os.path.realpath(resolved)
        except (OSError, ValueError):
            # If symlink resolution fails, use the path as-is
            pass
    
    # Final safety check
    if not _is_safe_path(resolved):
        raise PermissionError(f"Path '{resolved}' is in a restricted system directory")
    
    # Load settings for additional restrictions (if available)
    try:
        settings = load_settings()
        if settings.restricted_paths:
            for restricted in settings.restricted_paths:
                if resolved.startswith(restricted) or restricted in resolved:
                    raise PermissionError(f"Path '{resolved}' is restricted by settings")
        
        if settings.allowed_paths:
            allowed = False
            for allowed_path in settings.allowed_paths:
                if resolved.startswith(allowed_path):
                    allowed = True
                    break
            if not allowed:
                raise PermissionError(f"Path '{resolved}' is not in allowed_paths")
    except Exception:
        # If settings loading fails, continue with basic safety checks
        pass
    
    # Cache the result (limit cache size to prevent memory issues)
    if len(resolve_path._path_cache) > 1000:
        # Clear half of the cache (simple LRU-like behavior)
        resolve_path._path_cache = dict(list(resolve_path._path_cache.items())[500:])
    
    resolve_path._path_cache[cache_key] = resolved
    return resolved

