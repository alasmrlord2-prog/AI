"""Policy API Routes - Zanzibar-style policies."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.policy import service as policy_service
from app.policy import schemas

router = APIRouter(prefix="/api/policy", tags=["Policy"])


# Relation Tuples
@router.get("/relations", response_model=List[schemas.RelationTupleResponse])
async def get_relations(
    subject_type: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    object_type: Optional[str] = Query(None),
    object_id: Optional[str] = Query(None),
    tenant_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all relations with optional filters."""
    relations = policy_service.PolicyService.get_all_relations(
        db, subject_type, subject_id, object_type, object_id, tenant_id
    )
    return [schemas.RelationTupleResponse.from_orm(r) for r in relations]


@router.post("/relations", response_model=schemas.RelationTupleResponse, status_code=status.HTTP_201_CREATED)
async def create_relation_tuple(
    tuple_data: schemas.RelationTupleCreate,
    db: Session = Depends(get_db)
):
    """Create a relation tuple."""
    relation_tuple = policy_service.PolicyService.create_relation_tuple(db, tuple_data)
    return schemas.RelationTupleResponse.from_orm(relation_tuple)


@router.post("/check", response_model=schemas.PolicyCheckResponse)
async def check_relation(
    check_request: schemas.PolicyCheckRequest,
    db: Session = Depends(get_db)
):
    """Check if a relation exists."""
    result = policy_service.PolicyService.check_relation(db, check_request)
    return result


@router.post("/relations/check", response_model=schemas.PolicyCheckResponse)
async def check_relation_alt(
    check_request: schemas.PolicyCheckRequest,
    db: Session = Depends(get_db)
):
    """Check if a relation exists (alternative endpoint)."""
    result = policy_service.PolicyService.check_relation(db, check_request)
    return result


@router.get("/relations/subject/{subject_type}/{subject_id}", response_model=List[schemas.RelationTupleResponse])
async def get_relations_for_subject(
    subject_type: str,
    subject_id: str,
    tenant_id: UUID = None,
    db: Session = Depends(get_db)
):
    """Get all relations for a subject."""
    relations = policy_service.PolicyService.get_relations_for_subject(
        db, subject_type, subject_id, tenant_id
    )
    return [schemas.RelationTupleResponse.from_orm(r) for r in relations]


@router.get("/relations/object/{object_type}/{object_id}", response_model=List[schemas.RelationTupleResponse])
async def get_relations_for_object(
    object_type: str,
    object_id: str,
    tenant_id: UUID = None,
    db: Session = Depends(get_db)
):
    """Get all relations for an object."""
    relations = policy_service.PolicyService.get_relations_for_object(
        db, object_type, object_id, tenant_id
    )
    return [schemas.RelationTupleResponse.from_orm(r) for r in relations]


# Policy Rules
@router.get("/rules", response_model=List[schemas.PolicyRuleResponse])
async def get_policy_rules(
    tenant_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all policy rules."""
    rules = policy_service.PolicyService.get_all_policy_rules(db, tenant_id)
    return [schemas.PolicyRuleResponse.from_orm(r) for r in rules]


@router.post("/rules", response_model=schemas.PolicyRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_policy_rule(
    rule_data: schemas.PolicyRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a policy rule."""
    rule = policy_service.PolicyService.create_policy_rule(db, rule_data)
    return schemas.PolicyRuleResponse.from_orm(rule)


@router.post("/rules/evaluate")
async def evaluate_policy_rules(
    subject_type: str,
    subject_id: str,
    object_type: str,
    object_id: str,
    action: str,
    tenant_id: UUID = None,
    db: Session = Depends(get_db)
):
    """Evaluate policy rules."""
    result = policy_service.PolicyService.evaluate_policy_rules(
        db, subject_type, subject_id, object_type, object_id, action, tenant_id
    )
    return result

