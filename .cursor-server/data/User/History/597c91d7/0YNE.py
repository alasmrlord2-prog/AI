"""
Live Kernel Metrics API
واجهات API لمقاييس kernel
"""
from fastapi import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.services.live_kernel_metrics import get_kernel_metrics
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/kernel/metrics", tags=["kernel-metrics"])


@router.get("/io-latency")
async def get_io_latency(current_user: dict = Depends(get_current_user)):
    """مقاييس IO latency"""
    try:
        check_action_permission("monitoring.view", current_user)
    except HTTPException:
        pass
    
    metrics = get_kernel_metrics()
    result = metrics.get_io_latency()
    
    return result


@router.get("/scheduling")
async def get_scheduling(current_user: dict = Depends(get_current_user)):
    """مقاييس kernel scheduling"""
    try:
        check_action_permission("monitoring.view", current_user)
    except HTTPException:
        pass
    
    metrics = get_kernel_metrics()
    result = metrics.get_kernel_scheduling()
    
    return result


@router.get("/packet-drops")
async def get_packet_drops(current_user: dict = Depends(get_current_user)):
    """مقاييس packet drops"""
    try:
        check_action_permission("monitoring.view", current_user)
    except HTTPException:
        pass
    
    metrics = get_kernel_metrics()
    result = metrics.get_network_packet_drops()
    
    return result


@router.get("/cgroup-throttling")
async def get_cgroup_throttling(current_user: dict = Depends(get_current_user)):
    """مقاييس cgroup throttling"""
    try:
        check_action_permission("monitoring.view", current_user)
    except HTTPException:
        pass
    
    metrics = get_kernel_metrics()
    result = metrics.get_cgroup_throttling()
    
    return result


@router.get("/disk-queues")
async def get_disk_queues(current_user: dict = Depends(get_current_user)):
    """مقاييس disk queues"""
    try:
        check_action_permission("monitoring.view", current_user)
    except HTTPException:
        pass
    
    metrics = get_kernel_metrics()
    result = metrics.get_disk_queues()
    
    return result


@router.get("/all")
async def get_all_metrics(current_user: dict = Depends(get_current_user)):
    """جميع مقاييس kernel"""
    try:
        check_action_permission("monitoring.view", current_user)
    except HTTPException:
        pass
    
    metrics = get_kernel_metrics()
    result = metrics.get_all_metrics()
    
    return result

