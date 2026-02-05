"""AI Debugger - Watcher, Analyzer, and Auto Patch."""
import os
import subprocess
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class LogWatcher(FileSystemEventHandler):
    """Watch log files for changes."""
    
    def __init__(self, callback):
        """Initialize watcher."""
        self.callback = callback
        self.last_lines = {}
    
    def on_modified(self, event):
        """Handle file modification."""
        if event.is_directory:
            return
        
        if event.src_path.endswith('.log'):
            self._check_file(event.src_path)
    
    def _check_file(self, file_path: str):
        """Check file for new errors."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Get last 50 lines
            recent_lines = lines[-50:] if len(lines) > 50 else lines
            
            # Check for errors
            error_patterns = [
                r'ERROR',
                r'FATAL',
                r'Exception',
                r'Traceback',
                r'Failed',
                r'Error:',
                r'error:',
            ]
            
            errors = []
            for i, line in enumerate(recent_lines):
                for pattern in error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        errors.append({
                            "line_number": len(lines) - len(recent_lines) + i + 1,
                            "content": line.strip(),
                            "file": file_path
                        })
            
            if errors:
                self.callback(file_path, errors)
                
        except Exception as e:
            print(f"Error checking file {file_path}: {e}")


class AIDebugger:
    """AI-powered debugger for analyzing and fixing errors."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize AI Debugger."""
        self.ollama_url = ollama_url
        self.observer = None
        self.watchers = {}
        self.error_history = []
        self.auto_fix_enabled = False
    
    def start_watching(self, log_dirs: List[str]):
        """Start watching log directories."""
        if self.observer and self.observer.is_alive():
            return {"status": "already_watching"}
        
        self.observer = Observer()
        
        for log_dir in log_dirs:
            log_path = Path(log_dir)
            if log_path.exists() and log_path.is_dir():
                handler = LogWatcher(self._on_error_detected)
                self.observer.schedule(handler, str(log_path), recursive=True)
                self.watchers[log_dir] = handler
        
        self.observer.start()
        
        return {
            "status": "started",
            "watching_dirs": log_dirs
        }
    
    def stop_watching(self):
        """Stop watching logs."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        return {"status": "stopped"}
    
    def _on_error_detected(self, file_path: str, errors: List[Dict]):
        """Handle detected errors."""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "errors": errors,
            "context": self._get_log_context(file_path, 50)
        }
        
        self.error_history.append(error_data)
        
        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
        
        # Analyze with AI
        analysis = self.analyze_error(error_data)
        
        # Auto fix if enabled and safe
        if self.auto_fix_enabled and analysis.get("safe_to_fix", False):
            self.auto_patch(analysis)
    
    def _get_log_context(self, file_path: str, lines: int = 50) -> str:
        """Get log context (last N lines)."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception:
            return ""
    
    def analyze_error(self, error_data: Dict) -> Dict:
        """Analyze error using LLM."""
        try:
            # Prepare prompt
            prompt = f"""Analyze this error and provide:
1. Root cause
2. Location where it occurred
3. How to fix it
4. Is it safe to auto-fix? (yes/no)

Error data:
File: {error_data['file']}
Errors: {json.dumps(error_data['errors'], indent=2)}
Context:
{error_data['context']}

Respond in JSON format:
{{
    "root_cause": "...",
    "location": "...",
    "solution": "...",
    "safe_to_fix": true/false,
    "fix_commands": ["command1", "command2"]
}}"""
            
            # Call Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get("response", "")
                
                # Try to parse JSON from response
                try:
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                    else:
                        # Fallback: create structured response
                        analysis = {
                            "root_cause": "Unable to parse AI response",
                            "location": error_data['file'],
                            "solution": analysis_text,
                            "safe_to_fix": False,
                            "fix_commands": []
                        }
                except json.JSONDecodeError:
                    analysis = {
                        "root_cause": "Error parsing AI response",
                        "location": error_data['file'],
                        "solution": analysis_text,
                        "safe_to_fix": False,
                        "fix_commands": []
                    }
                
                analysis["timestamp"] = datetime.now().isoformat()
                analysis["error_data"] = error_data
                
                return analysis
            else:
                return {
                    "root_cause": "Failed to call AI",
                    "location": error_data['file'],
                    "solution": "Manual investigation required",
                    "safe_to_fix": False,
                    "fix_commands": [],
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "root_cause": f"Analysis error: {str(e)}",
                "location": error_data['file'],
                "solution": "Manual investigation required",
                "safe_to_fix": False,
                "fix_commands": []
            }
    
    def auto_patch(self, analysis: Dict) -> Dict:
        """Auto patch based on analysis."""
        if not analysis.get("safe_to_fix", False):
            return {
                "success": False,
                "reason": "Not safe to auto-fix"
            }
        
        fix_commands = analysis.get("fix_commands", [])
        
        if not fix_commands:
            return {
                "success": False,
                "reason": "No fix commands provided"
            }
        
        results = []
        
        for cmd in fix_commands:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                results.append({
                    "command": cmd,
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr
                })
            except Exception as e:
                results.append({
                    "command": cmd,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": all(r["success"] for r in results),
            "results": results,
            "analysis": analysis
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Get recent errors."""
        return self.error_history[-limit:]
    
    def check_docker_logs(self, container_name: str) -> Dict:
        """Check Docker container logs for errors."""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", "50", container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            logs = result.stdout
            errors = []
            
            error_patterns = [r'ERROR', r'FATAL', r'Exception', r'Traceback']
            for line in logs.split('\n'):
                for pattern in error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        errors.append(line)
                        break
            
            return {
                "success": True,
                "container": container_name,
                "errors": errors,
                "logs": logs
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_service_status(self, service_name: str) -> Dict:
        """Check systemd service status."""
        try:
            result = subprocess.run(
                ["systemctl", "status", service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            is_active = "active (running)" in result.stdout.lower()
            is_failed = "failed" in result.stdout.lower() or result.returncode != 0
            
            return {
                "success": True,
                "service": service_name,
                "active": is_active,
                "failed": is_failed,
                "status": result.stdout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
ai_debugger = AIDebugger()

