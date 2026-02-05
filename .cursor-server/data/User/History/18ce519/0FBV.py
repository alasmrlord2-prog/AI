"""Settings-related models."""
from pydantic import BaseModel
from typing import List


class SettingsModel(BaseModel):
    """Settings model."""
    allow_shell: bool = False
    allow_read_file: bool = True
    allow_doc_search: bool = True
    allow_logs: bool = True
    long_memory_enabled: bool = True
    agent_mode: str = "devops"
    memory_mode: str = "short"
    require_approval: List[str] = ["run_shell"]

