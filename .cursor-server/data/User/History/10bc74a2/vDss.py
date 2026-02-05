"""Policy Engine - Graph-based evaluation for Zanzibar-style policies."""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from uuid import UUID
import json

from app.policy.models import RelationTuple, PolicyRule


class PolicyEngine:
    """Graph-based policy evaluation engine (Zanzibar-style)."""

    @staticmethod
    def build_relation_graph(
        db: Session,
        subject_type: str,
        subject_id: str,
        tenant_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Build a relation graph starting from a subject."""
        graph = {
            "nodes": {},
            "edges": [],
            "paths": []
        }

        # Get all relations for this subject
        relations = db.query(RelationTuple).filter(
            RelationTuple.subject_type == subject_type,
            RelationTuple.subject_id == subject_id,
            RelationTuple.is_active == True,
            RelationTuple.tenant_id == tenant_id if tenant_id else True,
            RelationTuple.expires_at > datetime.utcnow() if RelationTuple.expires_at else True
        ).all()

        # Add subject as root node
        subject_key = f"{subject_type}:{subject_id}"
        graph["nodes"][subject_key] = {
            "type": subject_type,
            "id": subject_id,
            "relations": []
        }

        # Build graph from relations
        for relation in relations:
            object_key = f"{relation.object_type}:{relation.object_id}"
            
            # Add object node
            if object_key not in graph["nodes"]:
                graph["nodes"][object_key] = {
                    "type": relation.object_type,
                    "id": relation.object_id,
                    "relations": []
                }

            # Add edge
            graph["edges"].append({
                "from": subject_key,
                "to": object_key,
                "relation": relation.relation,
                "conditions": relation.conditions
            })

            # Add relation to subject
            graph["nodes"][subject_key]["relations"].append({
                "object": object_key,
                "relation": relation.relation
            })

        return graph

    @staticmethod
    def find_path(
        db: Session,
        subject_type: str,
        subject_id: str,
        object_type: str,
        object_id: str,
        relation: str,
        tenant_id: Optional[UUID] = None,
        max_depth: int = 5
    ) -> List[List[str]]:
        """Find all paths from subject to object with given relation."""
        paths = []
        visited = set()

        def dfs(current_type: str, current_id: str, path: List[str], depth: int):
            if depth > max_depth:
                return

            current_key = f"{current_type}:{current_id}"
            if current_key in visited:
                return
            visited.add(current_key)

            # Check if we reached the target
            if current_type == object_type and current_id == object_id:
                # Check if the last relation matches
                if path and path[-1] == relation:
                    paths.append(path[:])
                return

            # Get relations from current node
            relations = db.query(RelationTuple).filter(
                RelationTuple.subject_type == current_type,
                RelationTuple.subject_id == current_id,
                RelationTuple.is_active == True,
                RelationTuple.tenant_id == tenant_id if tenant_id else True,
                RelationTuple.expires_at > datetime.utcnow() if RelationTuple.expires_at else True
            ).all()

            for rel in relations:
                next_key = f"{rel.object_type}:{rel.object_id}"
                if next_key not in visited:
                    new_path = path + [rel.relation]
                    dfs(rel.object_type, rel.object_id, new_path, depth + 1)
                    visited.remove(next_key)

        dfs(subject_type, subject_id, [], 0)
        return paths

    @staticmethod
    def check_access(
        db: Session,
        subject_type: str,
        subject_id: str,
        object_type: str,
        object_id: str,
        relation: str,
        tenant_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Check if subject has access to object via relation (graph-based)."""
        # Direct relation check
        direct = db.query(RelationTuple).filter(
            RelationTuple.subject_type == subject_type,
            RelationTuple.subject_id == subject_id,
            RelationTuple.object_type == object_type,
            RelationTuple.object_id == object_id,
            RelationTuple.relation == relation,
            RelationTuple.is_active == True,
            RelationTuple.tenant_id == tenant_id if tenant_id else True,
            RelationTuple.expires_at > datetime.utcnow() if RelationTuple.expires_at else True
        ).first()

        if direct:
            return {
                "allowed": True,
                "reason": "Direct relation found",
                "path": [relation],
                "relation_type": "direct"
            }

        # Graph-based path finding
        paths = PolicyEngine.find_path(
            db, subject_type, subject_id, object_type, object_id, relation, tenant_id
        )

        if paths:
            return {
                "allowed": True,
                "reason": f"Path found via {len(paths)} path(s)",
                "paths": paths,
                "relation_type": "indirect"
            }

        return {
            "allowed": False,
            "reason": "No relation path found",
            "paths": [],
            "relation_type": "none"
        }

    @staticmethod
    def evaluate_conditions(
        conditions: Optional[str],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate ABAC conditions (simplified)."""
        if not conditions:
            return True

        try:
            cond = json.loads(conditions) if isinstance(conditions, str) else conditions
            
            # Simple condition evaluation
            # In production, use proper rule engine
            for key, value in cond.items():
                if key in context:
                    if context[key] != value:
                        return False
                else:
                    return False

            return True
        except:
            return False

    @staticmethod
    def get_allowed_objects(
        db: Session,
        subject_type: str,
        subject_id: str,
        object_type: str,
        relation: str,
        tenant_id: Optional[UUID] = None
    ) -> List[str]:
        """Get all objects of a type that subject has relation to."""
        # Direct relations
        direct = db.query(RelationTuple).filter(
            RelationTuple.subject_type == subject_type,
            RelationTuple.subject_id == subject_id,
            RelationTuple.object_type == object_type,
            RelationTuple.relation == relation,
            RelationTuple.is_active == True,
            RelationTuple.tenant_id == tenant_id if tenant_id else True,
            RelationTuple.expires_at > datetime.utcnow() if RelationTuple.expires_at else True
        ).all()

        object_ids = [f"{rel.object_type}:{rel.object_id}" for rel in direct]

        # TODO: Add indirect relations via graph traversal

        return object_ids

