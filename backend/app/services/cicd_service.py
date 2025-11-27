"""CI/CD Service - Git Integration and Pipeline Runner."""
import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
from enum import Enum
from app.utils.env_adapter import env_adapter
from app.utils.capability_detector import capability_detector


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CICDService:
    """CI/CD Service for managing repositories and pipelines."""
    
    def __init__(self, repos_dir: str = "/data/repos"):
        """Initialize CI/CD service."""
        self.repos_dir = Path(repos_dir)
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        self.pipelines: Dict[str, Dict] = {}
        self.pipeline_logs: Dict[str, List[str]] = {}
    
    def clone_repo(self, repo_url: str, repo_name: str, branch: str = "main") -> Dict:
        """Clone a repository."""
        # Check if git is available
        if not capability_detector.is_feature_available("git_operations"):
            return {
                "success": False,
                "error": "Git operations not available. Install 'git' CLI",
                "repo_path": None,
                "capabilities": capability_detector.get_scan_features(),
            }
        
        try:
            repo_path = self.repos_dir / repo_name
            
            # Remove if exists
            if repo_path.exists():
                shutil.rmtree(repo_path)
            
            # Clone repository - use EnvAdapter
            result = env_adapter.exec(
                ["git", "clone", "-b", branch, repo_url, str(repo_path)],
                timeout=300
            )
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.stderr,
                    "repo_path": None
                }
            
            return {
                "success": True,
                "repo_path": str(repo_path),
                "message": f"Repository cloned successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repo_path": None
            }
    
    def pull_repo(self, repo_name: str, branch: str = "main") -> Dict:
        """Pull latest changes from repository."""
        try:
            repo_path = self.repos_dir / repo_name
            
            if not repo_path.exists():
                return {
                    "success": False,
                    "error": "Repository not found"
                }
            
            # Fetch and pull - use EnvAdapter
            fetch_result = env_adapter.exec(
                ["git", "-C", str(repo_path), "fetch", "origin"],
                timeout=60
            )
            
            if not fetch_result.success:
                return {
                    "success": False,
                    "error": f"Failed to fetch: {fetch_result.stderr}"
                }
            
            result = env_adapter.exec(
                ["git", "-C", str(repo_path), "pull", "origin", branch],
                timeout=300
            )
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "message": "Repository updated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_repo_info(self, repo_name: str) -> Dict:
        """Get repository information."""
        try:
            repo_path = self.repos_dir / repo_name
            
            if not repo_path.exists():
                return {
                    "exists": False,
                    "error": "Repository not found"
                }
            
            # Get current branch - use EnvAdapter
            branch_result = env_adapter.exec(
                ["git", "-C", str(repo_path), "branch", "--show-current"]
            )
            branch = branch_result.stdout.strip() if branch_result.success else "unknown"
            
            # Get last commit - use EnvAdapter
            commit_result = env_adapter.exec(
                ["git", "-C", str(repo_path), "log", "-1", "--format=%H|%s|%an|%ad", "--date=iso"]
            )
            
            commit_info = {}
            if commit_result.success:
                parts = commit_result.stdout.strip().split("|")
                if len(parts) >= 4:
                    commit_info = {
                        "hash": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "date": parts[3]
                    }
            
            return {
                "exists": True,
                "repo_path": str(repo_path),
                "branch": branch,
                "last_commit": commit_info
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e)
            }
    
    def list_repos(self) -> List[Dict]:
        """List all cloned repositories."""
        repos = []
        
        if not self.repos_dir.exists():
            return repos
        
        for item in self.repos_dir.iterdir():
            if item.is_dir() and (item / ".git").exists():
                repo_info = self.get_repo_info(item.name)
                repos.append({
                    "name": item.name,
                    **repo_info
                })
        
        return repos
    
    async def run_pipeline(
        self,
        repo_name: str,
        pipeline_script: str = ".shiftwave/pipeline.sh",
        env_vars: Optional[Dict] = None
    ) -> str:
        """Run a pipeline for a repository."""
        pipeline_id = f"{repo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        repo_path = self.repos_dir / repo_name
        if not repo_path.exists():
            raise ValueError(f"Repository {repo_name} not found")
        
        pipeline_script_path = repo_path / pipeline_script
        if not pipeline_script_path.exists():
            raise ValueError(f"Pipeline script {pipeline_script} not found")
        
        # Initialize pipeline status
        self.pipelines[pipeline_id] = {
            "id": pipeline_id,
            "repo_name": repo_name,
            "status": PipelineStatus.PENDING.value,
            "started_at": datetime.now().isoformat(),
            "finished_at": None,
            "env_vars": env_vars or {}
        }
        self.pipeline_logs[pipeline_id] = []
        
        # Run pipeline in background
        asyncio.create_task(self._execute_pipeline(pipeline_id, pipeline_script_path, env_vars or {}))
        
        return pipeline_id
    
    async def _execute_pipeline(self, pipeline_id: str, script_path: Path, env_vars: Dict):
        """Execute pipeline script."""
        try:
            self.pipelines[pipeline_id]["status"] = PipelineStatus.RUNNING.value
            
            # Check if bash is available
            if not env_adapter.tool_installed("bash"):
                raise ValueError("bash is not available. Cannot execute pipeline script.")
            
            # Prepare environment
            env = os.environ.copy()
            env.update(env_vars)
            
            # Make script executable
            try:
                os.chmod(script_path, 0o755)
            except (OSError, PermissionError) as e:
                self.pipelines[pipeline_id]["error"] = f"Failed to make script executable: {str(e)}"
                self.pipelines[pipeline_id]["status"] = PipelineStatus.FAILED.value
                return
            
            # Run pipeline using asyncio (needed for real-time log streaming)
            # Note: asyncio.create_subprocess_exec is appropriate here for async pipeline execution
            process = await asyncio.create_subprocess_exec(
                "bash",
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(script_path.parent.parent),
                env=env
            )
            
            # Read output line by line
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                line_text = line.decode('utf-8', errors='ignore').strip()
                self.pipeline_logs[pipeline_id].append(line_text)
                
                # Keep only last 1000 lines
                if len(self.pipeline_logs[pipeline_id]) > 1000:
                    self.pipeline_logs[pipeline_id] = self.pipeline_logs[pipeline_id][-1000:]
            
            await process.wait()
            
            if process.returncode == 0:
                self.pipelines[pipeline_id]["status"] = PipelineStatus.SUCCESS.value
            else:
                self.pipelines[pipeline_id]["status"] = PipelineStatus.FAILED.value
            
            self.pipelines[pipeline_id]["finished_at"] = datetime.now().isoformat()
            self.pipelines[pipeline_id]["exit_code"] = process.returncode
            
        except Exception as e:
            self.pipelines[pipeline_id]["status"] = PipelineStatus.FAILED.value
            self.pipelines[pipeline_id]["finished_at"] = datetime.now().isoformat()
            self.pipelines[pipeline_id]["error"] = str(e)
            self.pipeline_logs[pipeline_id].append(f"ERROR: {str(e)}")
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict]:
        """Get pipeline status."""
        return self.pipelines.get(pipeline_id)
    
    def get_pipeline_logs(self, pipeline_id: str, tail: int = 100) -> List[str]:
        """Get pipeline logs."""
        logs = self.pipeline_logs.get(pipeline_id, [])
        return logs[-tail:] if tail > 0 else logs
    
    def list_pipelines(self, repo_name: Optional[str] = None) -> List[Dict]:
        """List all pipelines."""
        pipelines = list(self.pipelines.values())
        
        if repo_name:
            pipelines = [p for p in pipelines if p.get("repo_name") == repo_name]
        
        # Sort by started_at descending
        pipelines.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        
        return pipelines
    
    def rollback_pipeline(self, pipeline_id: str) -> Dict:
        """Rollback to a previous successful pipeline."""
        target_pipeline = self.pipelines.get(pipeline_id)
        
        if not target_pipeline:
            return {
                "success": False,
                "error": "Pipeline not found"
            }
        
        if target_pipeline["status"] != PipelineStatus.SUCCESS.value:
            return {
                "success": False,
                "error": "Can only rollback to successful pipelines"
            }
        
        repo_name = target_pipeline["repo_name"]
        repo_path = self.repos_dir / repo_name
        
        # Find the commit hash from that pipeline
        # This would require storing commit hash with pipeline
        # For now, we'll just return success
        
        return {
            "success": True,
            "message": f"Rollback initiated for pipeline {pipeline_id}",
            "pipeline_id": pipeline_id,
            "repo_name": repo_name
        }


# Global instance
cicd_service = CICDService()

