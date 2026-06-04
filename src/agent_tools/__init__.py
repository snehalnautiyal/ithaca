# Load all tools on import
from src.agent_tools import web_search, file_ops, shell, memory_tools  # noqa: F401
from src.agent_tools.registry import get_tool_schemas, dispatch_tool  # noqa: F401
