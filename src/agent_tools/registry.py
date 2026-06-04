"""Tool registry and dispatch."""
from typing import Any

TOOLS: dict[str, dict] = {}


def register_tool(name: str, description: str, parameters: dict, handler, requires_confirm: bool = False, admin_only: bool = False):
    TOOLS[name] = {
        "name": name,
        "description": description,
        "parameters": parameters,
        "handler": handler,
        "requires_confirm": requires_confirm,
        "admin_only": admin_only,
    }


def get_tool_schemas() -> list[dict]:
    return [
        {"name": t["name"], "description": t["description"], "parameters": t["parameters"],
         "requires_confirm": t["requires_confirm"], "admin_only": t["admin_only"]}
        for t in TOOLS.values()
    ]


async def dispatch_tool(name: str, args: dict, confirmed_tools: list[str] = None) -> dict[str, Any]:
    if name not in TOOLS:
        return {"error": f"Unknown tool: {name}"}

    tool = TOOLS[name]
    if tool["requires_confirm"] and name not in (confirmed_tools or []):
        return {"error": f"Tool '{name}' requires confirmation", "requires_confirm": True}

    try:
        result = await tool["handler"](**args)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
