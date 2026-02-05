"""Subscription API Routes - Plans, Subscriptions, Usage."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.subscription import service as subscription_service
from app.subscription import schemas

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


# Plans
@router.post("/plans", response_model=schemas.PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: schemas.PlanCreate,
    db: Session = Depends(get_db)
):
    """Create a new plan."""
    plan = subscription_service.SubscriptionService.create_plan(db, plan_data)
    return schemas.PlanResponse.from_orm(plan)


@router.get("/plans", response_model=List[schemas.PlanResponse])
async def get_plans(
    plan_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all active plans."""
    plans = subscription_service.SubscriptionService.get_active_plans(db, plan_type=plan_type)
    return [schemas.PlanResponse.from_orm(p) for p in plans]


@router.get("/plans/{plan_id}", response_model=schemas.PlanResponse)
async def get_plan(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """Get plan by ID."""
    plan = subscription_service.SubscriptionService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return schemas.PlanResponse.from_orm(plan)


# Subscriptions
@router.post("/subscriptions", response_model=schemas.SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: schemas.SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Create a new subscription."""
    subscription = subscription_service.SubscriptionService.create_subscription(db, subscription_data)
    return schemas.SubscriptionResponse.from_orm(subscription)


@router.get("/tenants/{tenant_id}/subscription", response_model=schemas.SubscriptionStatusResponse)
async def get_subscription_status(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get subscription status for tenant."""
    status_info = subscription_service.SubscriptionService.check_subscription_status(db, tenant_id)
    
    if not status_info["subscription"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription")

    # Get usage
    usage = subscription_service.SubscriptionService.get_usage(
        db, status_info["subscription"].id
    )

    # Get limits from plan
    limits = {}
    if status_info["subscription"].plan:
        plan = status_info["subscription"].plan
        limits = {
            "requests": plan.max_requests,
            "requests_daily": plan.max_requests_daily,
            "tokens": plan.max_tokens,
            "storage_gb": plan.max_storage_gb,
            "workflow_runs": plan.max_workflow_runs,
            "agents": plan.max_agents,
            "log_volume_gb": plan.max_log_volume_gb,
            "devices": plan.max_devices,
            "log_retention_days": plan.log_retention_days,
        }

    return {
        **status_info,
        "subscription": schemas.SubscriptionResponse.from_orm(status_info["subscription"]),
        "usage": usage,
        "limits": limits
    }


@router.post("/subscriptions/{subscription_id}/usage/increment")
async def increment_usage(
    subscription_id: UUID,
    resource_type: str,
    amount: int = 1,
    db: Session = Depends(get_db)
):
    """Increment usage counter."""
    counter = subscription_service.SubscriptionService.increment_usage(
        db, subscription_id, resource_type, amount
    )
    return {"message": "Usage incremented", "counter": schemas.UsageCounterResponse.from_orm(counter)}


@router.get("/subscriptions/{subscription_id}/usage", response_model=dict)
async def get_usage(
    subscription_id: UUID,
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get usage for subscription."""
    usage = subscription_service.SubscriptionService.get_usage(db, subscription_id, resource_type)
    return usage


@router.post("/subscriptions/{subscription_id}/usage/check")
async def check_usage_limit(
    subscription_id: UUID,
    resource_type: str,
    requested_amount: int = 1,
    db: Session = Depends(get_db)
):
    """Check if usage is within limits."""
    result = subscription_service.SubscriptionService.check_usage_limit(
        db, subscription_id, resource_type, requested_amount
    )
    return result

