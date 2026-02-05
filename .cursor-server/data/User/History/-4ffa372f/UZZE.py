"""CI/CD API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.services.cicd_service import cicd_service
from app.services.deploy_engine import deploy_engine
from app.api.auth import get_current_user
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/cicd", tags=["cicd"])


class CloneRepoRequest(BaseModel):
    """Clone repository request."""
    repo_url: str
    repo_name: str
    branch: str = "main"


class PullRepoRequest(BaseModel):
    """Pull repository request."""
    repo_name: str
    branch: str = "main"


class RunPipelineRequest(BaseModel):
    """Run pipeline request."""
    repo_name: str
    pipeline_script: str = ".shiftwave/pipeline.sh"
    env_vars: Optional[Dict[str, str]] = None


@router.post("/clone")
async def clone_repo(
    req: CloneRepoRequest,
    current_user: dict = Depends(get_current_user)
):
    """Clone a repository."""
    result = cicd_service.clone_repo(
        repo_url=req.repo_url,
        repo_name=req.repo_name,
        branch=req.branch
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Clone failed"))
    
    return result


@router.post("/pull")
async def pull_repo(
    req: PullRepoRequest,
    current_user: dict = Depends(get_current_user)
):
    """Pull latest changes from repository."""
    result = cicd_service.pull_repo(
        repo_name=req.repo_name,
        branch=req.branch
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Pull failed"))
    
    return result


@router.get("/repos")
async def list_repos(current_user: dict = Depends(get_current_user)):
    """List all repositories."""
    return {
        "repos": cicd_service.list_repos()
    }


@router.get("/repos/{repo_name}")
async def get_repo_info(
    repo_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get repository information."""
    info = cicd_service.get_repo_info(repo_name)
    
    if not info.get("exists"):
        raise HTTPException(status_code=404, detail=info.get("error", "Repository not found"))
    
    return info


@router.post("/run")
async def run_pipeline(
    req: RunPipelineRequest,
    current_user: dict = Depends(get_current_user)
):
    """Run a pipeline."""
    try:
        pipeline_id = await cicd_service.run_pipeline(
            repo_name=req.repo_name,
            pipeline_script=req.pipeline_script,
            env_vars=req.env_vars
        )
        
        return {
            "pipeline_id": pipeline_id,
            "status": "started",
            "message": "Pipeline started successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(e)}")


@router.get("/status/{pipeline_id}")
async def get_pipeline_status(
    pipeline_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get pipeline status."""
    status = cicd_service.get_pipeline_status(pipeline_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return status


@router.get("/logs/{pipeline_id}")
async def get_pipeline_logs(
    pipeline_id: str,
    tail: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get pipeline logs."""
    logs = cicd_service.get_pipeline_logs(pipeline_id, tail=tail)
    
    if logs is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return {
        "pipeline_id": pipeline_id,
        "logs": logs,
        "total_lines": len(logs)
    }


@router.get("/pipelines")
async def list_pipelines(
    repo_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all pipelines."""
    return {
        "pipelines": cicd_service.list_pipelines(repo_name=repo_name)
    }


@router.post("/rollback/{pipeline_id}")
async def rollback_pipeline(
    pipeline_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Rollback to a previous successful pipeline."""
    result = cicd_service.rollback_pipeline(pipeline_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Rollback failed"))
    
    return result


# ===== Deploy Endpoints =====

class DeployDockerComposeRequest(BaseModel):
    """Deploy Docker Compose request."""
    compose_file: str
    project_name: Optional[str] = None
    services: Optional[List[str]] = None


class DeployKubernetesRequest(BaseModel):
    """Deploy Kubernetes request."""
    manifest_file: str
    namespace: str = "default"
    apply: bool = True


class DeployRSyncRequest(BaseModel):
    """Deploy RSync request."""
    source: str
    destination: str
    host: Optional[str] = None
    user: Optional[str] = None
    exclude: Optional[List[str]] = None
    delete: bool = False


@router.post("/deploy/docker-compose")
async def deploy_docker_compose(
    req: DeployDockerComposeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Deploy using Docker Compose."""
    result = deploy_engine.deploy_docker_compose(
        compose_file=req.compose_file,
        project_name=req.project_name,
        services=req.services
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Deployment failed"))
    
    return result


@router.post("/deploy/kubernetes")
async def deploy_kubernetes(
    req: DeployKubernetesRequest,
    current_user: dict = Depends(get_current_user)
):
    """Deploy to Kubernetes."""
    result = deploy_engine.deploy_kubernetes(
        manifest_file=req.manifest_file,
        namespace=req.namespace,
        apply=req.apply
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Deployment failed"))
    
    return result


@router.post("/deploy/rsync")
async def deploy_rsync(
    req: DeployRSyncRequest,
    current_user: dict = Depends(get_current_user)
):
    """Deploy using RSync."""
    result = deploy_engine.deploy_rsync(
        source=req.source,
        destination=req.destination,
        host=req.host,
        user=req.user,
        exclude=req.exclude,
        delete=req.delete
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Deployment failed"))
    
    return result


@router.get("/deploy/status")
async def get_deployment_status(
    deployment_type: str,
    identifier: str,
    current_user: dict = Depends(get_current_user)
):
    """Get deployment status."""
    result = deploy_engine.get_deployment_status(
        deployment_type=deployment_type,
        identifier=identifier
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to get status"))
    
    return result

