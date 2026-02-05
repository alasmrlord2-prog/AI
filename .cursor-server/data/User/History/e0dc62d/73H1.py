"""File system API endpoints."""
from fastapi import APIRouter
from app.utils.helpers import load_settings

router = APIRouter(prefix="/api/fs", tags=["filesystem"])

# Import file explorer
try:
    from app.tools.file_explorer import list_dir, read_file, tail_file
except ImportError:
    def list_dir(path):
        return {"error": "File explorer not available"}
    def read_file(path, limit=10000):
        return {"error": "File explorer not available"}
    def tail_file(path, lines=50):
        return {"error": "File explorer not available"}


@router.get("/list")
async def api_fs_list(path: str = ""):
    """List directory contents."""
    try:
        settings = load_settings()
        if not settings.allow_read_file:
            return {"error": "File operations disabled from settings"}
        return list_dir(path)
    except Exception as e:
        return {"error": str(e)}


@router.get("/read")
async def api_fs_read(path: str, limit: int = 10000):
    """Read file content."""
    try:
        settings = load_settings()
        if not settings.allow_read_file:
            return {"error": "File operations disabled from settings"}
        return read_file(path, limit=limit)
    except Exception as e:
        return {"error": str(e)}


@router.get("/tail")
async def api_fs_tail(path: str, lines: int = 50):
    """Read last N lines of a file."""
    try:
        settings = load_settings()
        if not settings.allow_read_file:
            return {"error": "File operations disabled from settings"}
        return tail_file(path, lines=lines)
    except Exception as e:
        return {"error": str(e)}

