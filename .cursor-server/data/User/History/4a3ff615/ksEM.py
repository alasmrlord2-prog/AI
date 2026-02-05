"""Policy Service - Zanzibar-style policy engine."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.policy.models import RelationTuple, PolicyRule
from app.policy.schemas import RelationTupleCreate, PolicyRuleCreate, PolicyCheckRequest


class PolicyService:
    """Service for managing Zanzibar-style policies."""

    @staticmethod
    def create_relation_tuple(
        db: Session,
        tuple_data: RelationTupleCreate
    ) -> RelationTuple:
        """Create a relation tuple."""
        relation_tuple = RelationTuple(
            subject_type=tuple_data.subject_type,
            subject_id=tuple_data.subject_id,
            object_type=tuple_data.object_type,
            object_id=tuple_data.object_id,
            relation=tuple_data.relation,
            tenant_id=tuple_data.tenant_id,
            conditions=tuple_data.conditions,
            expires_at=tuple_data.expires_at,
            is_active=True
        )
        db.add(relation_tuple)
        db.commit()
        db.refresh(relation_tuple)
        return relation_tuple

    @staticmethod
    def check_relation(
        db: Session,
        check_request: PolicyCheckRequest
    ) -> Dict[str, Any]:
        """Check if a relation exists (Zanzibar-style check)."""
        now = datetime.utcnow()

        # Build query
        query = db.query(RelationTuple).filter(
            RelationTuple.subject_type == check_request.subject_type,
            RelationTuple.subject_id == check_request.subject_id,
            RelationTuple.object_type == check_request.object_type,
            RelationTuple.object_id == check_request.object_id,
            RelationTuple.relation == check_request.relation,
            RelationTuple.is_active == True,
            or_(
                RelationTuple.expires_at.is_(None),
                RelationTuple.expires_at > now
            )
        )

        # Filter by tenant if provided
        if check_request.tenant_id:
            query = query.filter(
                or_(
                    RelationTuple.tenant_id == check_request.tenant_id,
                    RelationTuple.tenant_id.is_(None)  # Global relations
                )
            )

        matched_tuples = query.all()

        # Check conditions if any
        allowed = False
        matched_tuple_ids = []
        for tuple_obj in matched_tuples:
            if tuple_obj.conditions:
                # Evaluate conditions (simplified - in production use proper evaluator)
                # For now, if conditions exist, we assume they pass
                pass
            allowed = True
            matched_tuple_ids.append(str(tuple_obj.id))

        return {
            "allowed": allowed,
            "reason": "Relation found" if allowed else "No matching relation",
            "matched_tuples": matched_tuple_ids
        }

    @staticmethod
    def get_relations_for_subject(
        db: Session,
        subject_type: str,
        subject_id: str,
        tenant_id: Optional[UUID] = None
    ) -> List[RelationTuple]:
        """Get all relations for a subject."""
        query = db.query(RelationTuple).filter(
            RelationTuple.subject_type == subject_type,
            RelationTuple.subject_id == subject_id,
            RelationTuple.is_active == True,
            or_(
                RelationTuple.expires_at.is_(None),
                RelationTuple.expires_at > datetime.utcnow()
            )
        )

        if tenant_id:
            query = query.filter(
                or_(
                    RelationTuple.tenant_id == tenant_id,
                    RelationTuple.tenant_id.is_(None)
                )
            )

        return query.all()

    @staticmethod
    def get_relations_for_object(
        db: Session,
        object_type: str,
        object_id: str,
        tenant_id: Optional[UUID] = None
    ) -> List[RelationTuple]:
        """Get all relations for an object."""
        query = db.query(RelationTuple).filter(
            RelationTuple.object_type == object_type,
            RelationTuple.object_id == object_id,
            RelationTuple.is_active == True,
            or_(
                RelationTuple.expires_at.is_(None),
                RelationTuple.expires_at > datetime.utcnow()
            )
        )

        if tenant_id:
            query = query.filter(
                or_(
                    RelationTuple.tenant_id == tenant_id,
                    RelationTuple.tenant_id.is_(None)
                )
            )

        return query.all()

    @staticmethod
    def create_policy_rule(
        db: Session,
        rule_data: PolicyRuleCreate
    ) -> PolicyRule:
        """Create a policy rule."""
        import json
        policy_rule = PolicyRule(
            name=rule_data.name,
            description=rule_data.description,
            rule_definition=json.dumps(rule_data.rule_definition) if isinstance(rule_data.rule_definition, dict) else rule_data.rule_definition,
            tenant_id=rule_data.tenant_id,
            resource_type=rule_data.resource_type,
            priority=rule_data.priority,
            is_active=True
        )
        db.add(policy_rule)
        db.commit()
        db.refresh(policy_rule)
        return policy_rule

    @staticmethod
    def evaluate_policy_rules(
        db: Session,
        subject_type: str,
        subject_id: str,
        object_type: str,
        object_id: str,
        action: str,
        tenant_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Evaluate policy rules (ABAC-style)."""
        # Get relevant rules
        query = db.query(PolicyRule).filter(
            PolicyRule.is_active == True
        )

        if tenant_id:
            query = query.filter(
                or_(
                    PolicyRule.tenant_id == tenant_id,
                    PolicyRule.tenant_id.is_(None)  # Global rules
                )
            )

        if object_type:
            query = query.filter(
                or_(
                    PolicyRule.resource_type == object_type,
                    PolicyRule.resource_type.is_(None)  # Rules for all resources
                )
            )

        rules = query.order_by(PolicyRule.priority.desc()).all()

        # Evaluate rules (simplified - in production use proper rule engine)
        matched_rules = []
        allowed = False

        for rule in rules:
            # Simple evaluation (in production, use proper rule engine like pyke, durable_rules, etc.)
            # For now, we'll just check if rule exists
            matched_rules.append(rule.name)
            # In real implementation, evaluate rule_definition JSON

        return {
            "allowed": allowed,
            "reason": "Policy evaluation",
            "matched_rules": matched_rules
        }

