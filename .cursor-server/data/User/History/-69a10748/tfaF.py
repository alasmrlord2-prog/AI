"""Policy Schemas - Zanzibar-style policy schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# RelationTuple Schemas
class RelationTupleBase(BaseModel):
    subject_type: str  # "user", "group", "role"
    subject_id: str
    object_type: str  # "project", "workflow", "agent"
    object_id: str
    relation: str  # "owner", "member", "viewer", "editor"
    tenant_id: Optional[UUID] = None
    conditions: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class RelationTupleCreate(RelationTupleBase):
    pass


class RelationTupleUpdate(BaseModel):
    relation: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class RelationTupleResponse(RelationTupleBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# PolicyRule Schemas
class PolicyRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_definition: Dict[str, Any]  # JSON rule definition
    tenant_id: Optional[UUID] = None
    resource_type: Optional[str] = None
    priority: int = 0


class PolicyRuleCreate(PolicyRuleBase):
    pass


class PolicyRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rule_definition: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class PolicyRuleResponse(PolicyRuleBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Policy Check Request
class PolicyCheckRequest(BaseModel):
    subject_type: str
    subject_id: str
    object_type: str
    object_id: str
    relation: str
    tenant_id: Optional[UUID] = None


class PolicyCheckResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    matched_rules: List[str] = []
    matched_tuples: List[str] = []

