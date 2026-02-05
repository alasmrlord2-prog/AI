"""Tools-related models."""
from pydantic import BaseModel


class ToolReadFile(BaseModel):
    """Read file tool request."""
    path: str


class ToolRunShell(BaseModel):
    """Run shell tool request."""
    cmd: str


class ToolService(BaseModel):
    """Service check tool request."""
    name: str

