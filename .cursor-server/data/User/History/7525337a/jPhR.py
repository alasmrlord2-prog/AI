"""Policy Models - Zanzibar-style relation tuples for fine-grained access control."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class RelationTuple(Base):
    """RelationTuple model - Zanzibar-style relation for ABAC."""
    __tablename__ = "relation_tuples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Subject (who)
    subject_type = Column(String(100), nullable=False)  # "user", "group", "role"
    subject_id = Column(String(255), nullable=False)  # UUID or identifier
    
    # Object (what)
    object_type = Column(String(100), nullable=False)  # "project", "workflow", "agent", "tenant"
    object_id = Column(String(255), nullable=False)  # UUID or identifier
    
    # Relation (how)
    relation = Column(String(100), nullable=False)  # "owner", "member", "viewer", "editor"
    
    # Context
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    
    # Metadata
    conditions = Column(Text, nullable=True)  # JSON conditions for ABAC
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Temporary relations

    # Relationships
    tenant = relationship("Tenant")

    # Composite index for efficient lookups
    __table_args__ = (
        Index("idx_relation_tuple_lookup", "subject_type", "subject_id", "object_type", "object_id", "relation"),
        Index("idx_relation_tuple_object", "object_type", "object_id", "relation"),
        Index("idx_relation_tuple_subject", "subject_type", "subject_id"),
    )

    def __repr__(self):
        return f"<RelationTuple(subject={self.subject_type}:{self.subject_id}, relation={self.relation}, object={self.object_type}:{self.object_id})>"


class PolicyRule(Base):
    """PolicyRule model - ABAC-style policy rules."""
    __tablename__ = "policy_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule definition (JSON)
    rule_definition = Column(Text, nullable=False)  # JSON: conditions, actions, effects
    
    # Scope
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)  # NULL = global rule
    resource_type = Column(String(100), nullable=True)  # Specific resource type or NULL for all
    
    # Priority (higher = evaluated first)
    priority = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<PolicyRule(id={self.id}, name={self.name}, priority={self.priority})>"

