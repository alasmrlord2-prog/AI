"""Workflow Builder Service - Node-based workflow execution."""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import subprocess
import asyncio


class NodeType(Enum):
    """Node types."""
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    TRANSFORM = "transform"


class WorkflowService:
    """Workflow builder and executor service."""
    
    def __init__(self):
        """Initialize workflow service."""
        self.workflows: Dict[str, Dict] = {}
        self.executions: Dict[str, Dict] = {}
    
    def create_workflow(self, name: str, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """Create a new workflow."""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow = {
            "id": workflow_id,
            "name": name,
            "nodes": nodes,
            "edges": edges,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.workflows[workflow_id] = workflow
        
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow by ID."""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Dict]:
        """List all workflows."""
        return list(self.workflows.values())
    
    def delete_workflow(self, workflow_id: str) -> Dict:
        """Delete a workflow."""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            return {"success": True, "message": f"Workflow {workflow_id} deleted"}
        return {"success": False, "error": "Workflow not found"}
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Optional[Dict] = None) -> Dict:
        """Execute a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": "Workflow not found"}
        
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "finished_at": None,
            "steps": [],
            "result": None,
            "error": None
        }
        
        self.executions[execution_id] = execution
        
        try:
            # Find trigger node
            trigger_node = next((n for n in workflow["nodes"] if n.get("type") == NodeType.TRIGGER.value), None)
            
            if not trigger_node:
                execution["status"] = "failed"
                execution["error"] = "No trigger node found"
                execution["finished_at"] = datetime.now().isoformat()
                return execution
            
            # Execute workflow
            result = await self._execute_nodes(workflow, trigger_node, trigger_data or {}, execution)
            
            execution["status"] = "success"
            execution["result"] = result
            execution["finished_at"] = datetime.now().isoformat()
            
        except Exception as e:
            execution["status"] = "failed"
            execution["error"] = str(e)
            execution["finished_at"] = datetime.now().isoformat()
        
        return execution
    
    async def _execute_nodes(
        self,
        workflow: Dict,
        start_node: Dict,
        initial_data: Dict,
        execution: Dict
    ) -> Any:
        """Execute workflow nodes."""
        current_data = initial_data
        current_node = start_node
        
        while current_node:
            # Execute node
            step_result = await self._execute_node(current_node, current_data)
            
            execution["steps"].append({
                "node_id": current_node.get("id"),
                "node_type": current_node.get("type"),
                "result": step_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update data
            if step_result.get("output"):
                current_data.update(step_result["output"])
            
            # Find next node
            next_edge = next(
                (e for e in workflow["edges"] if e.get("source") == current_node.get("id")),
                None
            )
            
            if not next_edge:
                break
            
            next_node_id = next_edge.get("target")
            current_node = next((n for n in workflow["nodes"] if n.get("id") == next_node_id), None)
        
        return current_data
    
    async def _execute_node(self, node: Dict, input_data: Dict) -> Dict:
        """Execute a single node."""
        node_type = node.get("type")
        node_config = node.get("config", {})
        
        if node_type == NodeType.TRIGGER.value:
            return {"output": input_data}
        
        elif node_type == NodeType.ACTION.value:
            action_type = node_config.get("action_type")
            
            if action_type == "restart_service":
                service_name = node_config.get("service_name") or input_data.get("service_name")
                result = subprocess.run(
                    ["systemctl", "restart", service_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "output": {
                        "service": service_name,
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr
                    }
                }
            
            elif action_type == "run_shell":
                command = node_config.get("command") or input_data.get("command")
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return {
                    "output": {
                        "command": command,
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr
                    }
                }
            
            elif action_type == "send_notification":
                message = node_config.get("message") or input_data.get("message")
                # Placeholder for notification
                return {
                    "output": {
                        "notification_sent": True,
                        "message": message
                    }
                }
            
            elif action_type == "backup_database":
                db_name = node_config.get("db_name") or input_data.get("db_name")
                # Placeholder for backup
                return {
                    "output": {
                        "backup_created": True,
                        "database": db_name
                    }
                }
        
        elif node_type == NodeType.CONDITION.value:
            condition = node_config.get("condition")
            value = input_data.get(condition.get("field"))
            operator = condition.get("operator")
            expected = condition.get("value")
            
            result = False
            if operator == "equals":
                result = value == expected
            elif operator == "greater_than":
                result = value > expected
            elif operator == "less_than":
                result = value < expected
            
            return {
                "output": {
                    "condition_result": result
                }
            }
        
        return {"output": input_data}
    
    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution by ID."""
        return self.executions.get(execution_id)
    
    def list_executions(self, workflow_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """List executions."""
        executions = list(self.executions.values())
        
        if workflow_id:
            executions = [e for e in executions if e.get("workflow_id") == workflow_id]
        
        executions.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        return executions[:limit]


# Global instance
workflow_service = WorkflowService()

