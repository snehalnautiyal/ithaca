"""File read/write tools — sandboxed to data/ directory."""
from pathlib import Path
from src.agent_tools.registry import register_tool

SANDBOX = Path("data").resolve()


def _safe_path(filepath: str) -> Path:
    p = (SANDBOX / filepath).resolve()
    if not str(p).startswith(str(SANDBOX)):
        raise PermissionError(f"Access denied: path outside data/ sandbox")
    return p


async def file_read(filepath: str) -> str:
    p = _safe_path(filepath)
    if not p.exists():
        return f"File not found: {filepath}"
    return p.read_text(encoding="utf-8")[:10000]  # limit to 10k chars


async def file_write(filepath: str, content: str) -> str:
    p = _safe_path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {filepath}"


register_tool(
    name="file_read",
    description="Read a file from the data/ directory.",
    parameters={"filepath": "string (relative to data/)"},
    handler=file_read,
)

register_tool(
    name="file_write",
    description="Write content to a file in the data/ directory. Requires confirmation.",
    parameters={"filepath": "string (relative to data/)", "content": "string"},
    handler=file_write,
    requires_confirm=True,
    admin_only=True,
)
