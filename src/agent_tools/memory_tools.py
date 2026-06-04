"""Memory read/write tools for the agent."""
from src.agent_tools.registry import register_tool
from services.memory import search_memories, add_memory


async def memory_read(query: str, n_results: int = 5) -> str:
    results = search_memories(query, n_results=n_results)
    if not results:
        return "No relevant memories found."
    return "\n".join(f"- {m['content']}" for m in results)


async def memory_write(content: str) -> str:
    mem_id = add_memory(content, mem_type="agent")
    return f"Memory stored (id: {mem_id})"


register_tool(
    name="memory_read",
    description="Search user memories for relevant information.",
    parameters={"query": "string", "n_results": "int (optional, default 5)"},
    handler=memory_read,
)

register_tool(
    name="memory_write",
    description="Store a new fact/memory for later retrieval.",
    parameters={"content": "string"},
    handler=memory_write,
)
