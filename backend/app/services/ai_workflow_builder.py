"""
AI Workflow Builder - 100% Local
باني workflows ذكي
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class WorkflowStep:
    """خطوة في workflow"""
    def __init__(
        self,
        step_id: str,
        step_type: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        condition: Optional[str] = None
    ):
        self.step_id = step_id
        self.step_type = step_type  # "action", "condition", "loop", "parallel"
        self.action = action
        self.parameters = parameters or {}
        self.condition = condition
        self.next_steps: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "type": self.step_type,
            "action": self.action,
            "parameters": self.parameters,
            "condition": self.condition,
            "next_steps": self.next_steps
        }


class Workflow:
    """Workflow"""
    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.start_step: Optional[str] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_step(self, step: WorkflowStep):
        """إضافة خطوة"""
        self.steps[step.step_id] = step
        if not self.start_step:
            self.start_step = step.step_id
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "steps": {sid: step.to_dict() for sid, step in self.steps.items()},
            "start_step": self.start_step,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class AIWorkflowBuilder:
    """
    باني workflows ذكي
    Auto-complete steps, اقتراح sequence based on logs, Debug workflows
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.workflows: Dict[str, Workflow] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.max_history = 10000
        
        # قوالب steps شائعة
        self.common_steps = {
            "deploy": {"action": "deploy", "type": "action"},
            "build": {"action": "build", "type": "action"},
            "test": {"action": "test", "type": "action"},
            "backup": {"action": "backup", "type": "action"},
            "notify": {"action": "notify", "type": "action"}
        }
    
    def create_workflow(
        self,
        name: str,
        description: str
    ) -> Workflow:
        """إنشاء workflow جديد"""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.workflows)}"
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description
        )
        
        self.workflows[workflow_id] = workflow
        
        log_info(f"Created workflow: {name} ({workflow_id})")
        return workflow
    
    def suggest_next_step(
        self,
        workflow_id: str,
        current_step: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """اقتراح الخطوة التالية"""
        if workflow_id not in self.workflows:
            return []
        
        workflow = self.workflows[workflow_id]
        
        # إذا لم تكن هناك خطوات، اقتراح خطوة أولى
        if not workflow.steps:
            return [
                {"action": "build", "description": "Build the application"},
                {"action": "test", "description": "Run tests"},
                {"action": "deploy", "description": "Deploy to environment"}
            ]
        
        # تحليل الخطوات الحالية واقتراح التالية
        current_actions = [step.action for step in workflow.steps.values()]
        
        suggestions = []
        
        # إذا كان build موجود، اقتراح test
        if "build" in current_actions and "test" not in current_actions:
            suggestions.append({"action": "test", "description": "Run tests after build"})
        
        # إذا كان test موجود، اقتراح deploy
        if "test" in current_actions and "deploy" not in current_actions:
            suggestions.append({"action": "deploy", "description": "Deploy after tests pass"})
        
        # إذا كان deploy موجود، اقتراح notify
        if "deploy" in current_actions and "notify" not in current_actions:
            suggestions.append({"action": "notify", "description": "Notify team after deployment"})
        
        return suggestions
    
    def auto_complete_step(
        self,
        workflow_id: str,
        partial_action: str
    ) -> List[Dict[str, Any]]:
        """Auto-complete للخطوة"""
        completions = []
        
        for step_template in self.common_steps.values():
            action = step_template["action"]
            if action.startswith(partial_action.lower()):
                completions.append({
                    "action": action,
                    "type": step_template["type"],
                    "description": f"Complete action: {action}"
                })
        
        return completions
    
    def add_step(
        self,
        workflow_id: str,
        step_type: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        condition: Optional[str] = None
    ) -> Dict[str, Any]:
        """إضافة خطوة للـworkflow"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        step_id = f"step_{len(workflow.steps) + 1}"
        
        step = WorkflowStep(
            step_id=step_id,
            step_type=step_type,
            action=action,
            parameters=parameters or {},
            condition=condition
        )
        
        workflow.add_step(step)
        
        return {
            "success": True,
            "step": step.to_dict(),
            "workflow": workflow.to_dict()
        }
    
    def debug_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Debug workflow"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        
        issues = []
        
        # التحقق من وجود start step
        if not workflow.start_step:
            issues.append({
                "type": "missing_start",
                "severity": "high",
                "message": "No start step defined"
            })
        
        # التحقق من steps معزولة (بدون connections)
        for step_id, step in workflow.steps.items():
            if step_id != workflow.start_step and not any(step_id in s.next_steps for s in workflow.steps.values()):
                issues.append({
                    "type": "isolated_step",
                    "severity": "medium",
                    "message": f"Step {step_id} is isolated (not connected)",
                    "step_id": step_id
                })
        
        # التحقق من cycles (مثال بسيط)
        # يمكن إضافة منطق أكثر تعقيداً
        
        return {
            "workflow_id": workflow_id,
            "issues": issues,
            "total_issues": len(issues),
            "workflow": workflow.to_dict()
        }
    
    def get_execution_map(self, workflow_id: str) -> Dict[str, Any]:
        """الحصول على execution map"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        
        # بناء graph
        nodes = []
        edges = []
        
        for step_id, step in workflow.steps.items():
            nodes.append({
                "id": step_id,
                "label": step.action,
                "type": step.step_type
            })
            
            for next_step_id in step.next_steps:
                edges.append({
                    "from": step_id,
                    "to": next_step_id
                })
        
        return {
            "workflow_id": workflow_id,
            "nodes": nodes,
            "edges": edges,
            "start_node": workflow.start_step
        }
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على workflow"""
        if workflow_id in self.workflows:
            return self.workflows[workflow_id].to_dict()
        return None
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """قائمة workflows"""
        return [w.to_dict() for w in self.workflows.values()]


# Global instance
_workflow_builder: Optional[AIWorkflowBuilder] = None


def get_workflow_builder() -> AIWorkflowBuilder:
    """الحصول على مثيل باني workflows"""
    global _workflow_builder
    if _workflow_builder is None:
        _workflow_builder = AIWorkflowBuilder()
    return _workflow_builder

