"""
Environment Adapter - Abstraction layer for cross-platform compatibility
يوفر طبقة تجريد للتوافق مع مختلف البيئات (Linux, Mac, Containers, VMs, Cloud, On-prem)
"""
import subprocess
import shutil
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import os
import platform


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    stdout: str
    stderr: str
    returncode: int
    command: List[str]
    execution_time: float = 0.0


class EnvAdapter:
    """
    Environment Adapter - Unified interface for command execution
    يدعم Fallback تلقائي للأدوات البديلة
    """
    
    def __init__(self):
        """Initialize environment adapter"""
        self._tool_cache: Dict[str, Optional[str]] = {}
        self._system_info = self._detect_system()
    
    def _detect_system(self) -> Dict[str, str]:
        """Detect system information"""
        return {
            "os": platform.system().lower(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }
    
    def tool_installed(self, tool_name: str) -> bool:
        """
        Check if a tool is installed (with caching)
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool is available, False otherwise
        """
        if tool_name in self._tool_cache:
            return self._tool_cache[tool_name] is not None
        
        tool_path = shutil.which(tool_name)
        self._tool_cache[tool_name] = tool_path
        return tool_path is not None
    
    def find_tool(self, *tool_names: str) -> Optional[str]:
        """
        Find first available tool from list (with fallback)
        
        Args:
            *tool_names: List of tool names to try
            
        Returns:
            Path to first available tool, or None
        """
        for tool_name in tool_names:
            if self.tool_installed(tool_name):
                return self._tool_cache[tool_name]
        return None
    
    def exec(
        self,
        cmd: List[str],
        timeout: int = 30,
        capture_output: bool = True,
        text: bool = True,
        check: bool = False,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> CommandResult:
        """
        Execute command with unified interface
        
        Args:
            cmd: Command to execute
            timeout: Timeout in seconds
            capture_output: Capture stdout/stderr
            text: Return text instead of bytes
            check: Raise exception on non-zero return
            cwd: Working directory
            env: Environment variables
            
        Returns:
            CommandResult object
        """
        import time
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=text,
                timeout=timeout,
                check=check,
                cwd=cwd,
                env=env or os.environ.copy(),
            )
            
            execution_time = time.time() - start_time
            
            return CommandResult(
                success=result.returncode == 0,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                returncode=result.returncode,
                command=cmd,
                execution_time=execution_time,
            )
        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            return CommandResult(
                success=False,
                stdout=e.stdout.decode() if e.stdout and text else "",
                stderr=f"Command timed out after {timeout}s",
                returncode=-1,
                command=cmd,
                execution_time=execution_time,
            )
        except FileNotFoundError:
            execution_time = time.time() - start_time
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Command not found: {cmd[0]}",
                returncode=-1,
                command=cmd,
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                success=False,
                stdout="",
                stderr=str(e),
                returncode=-1,
                command=cmd,
                execution_time=execution_time,
            )
    
    def exec_with_fallback(
        self,
        primary_cmd: List[str],
        fallback_cmd: List[str],
        timeout: int = 30,
        **kwargs
    ) -> CommandResult:
        """
        Execute command with automatic fallback
        
        Args:
            primary_cmd: Primary command to try
            fallback_cmd: Fallback command if primary fails
            timeout: Timeout in seconds
            **kwargs: Additional arguments for exec()
            
        Returns:
            CommandResult from first successful command
        """
        # Try primary first
        if self.tool_installed(primary_cmd[0]):
            result = self.exec(primary_cmd, timeout=timeout, **kwargs)
            if result.success:
                return result
        
        # Try fallback
        if self.tool_installed(fallback_cmd[0]):
            result = self.exec(fallback_cmd, timeout=timeout, **kwargs)
            return result
        
        # Both failed
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Neither {primary_cmd[0]} nor {fallback_cmd[0]} is available",
            returncode=-1,
            command=primary_cmd,
        )
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        return self._system_info.copy()
    
    def is_linux(self) -> bool:
        """Check if running on Linux"""
        return self._system_info["os"] == "linux"
    
    def is_mac(self) -> bool:
        """Check if running on macOS"""
        return self._system_info["os"] == "darwin"
    
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return self._system_info["os"] == "windows"
    
    def is_container(self) -> bool:
        """Check if running in container"""
        # Check common container indicators
        return (
            Path("/.dockerenv").exists() or
            Path("/proc/1/cgroup").exists() and "docker" in Path("/proc/1/cgroup").read_text() or
            os.environ.get("container") is not None
        )
    
    def is_cloud(self) -> bool:
        """Check if running in cloud environment"""
        # Check for cloud metadata services
        cloud_indicators = [
            "/sys/class/dmi/id/product_name",
            "/sys/hypervisor/uuid",
            "/var/lib/cloud",
        ]
        
        for indicator in cloud_indicators:
            if Path(indicator).exists():
                return True
        
        # Check environment variables
        cloud_env_vars = ["AWS_EXECUTION_ENV", "GOOGLE_CLOUD_PROJECT", "AZURE_INSTANCE_METADATA"]
        return any(os.environ.get(var) for var in cloud_env_vars)


# Global instance
env_adapter = EnvAdapter()

