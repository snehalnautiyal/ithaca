"""Web search tool via SearXNG."""
import os
import httpx
from src.agent_tools.registry import register_tool

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8080")


async def web_search(query: str, num_results: int = 5) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{SEARXNG_URL}/search", params={
                "q": query, "format": "json", "categories": "general"
            })
            if resp.status_code != 200:
                return f"Search failed (HTTP {resp.status_code})"
            data = resp.json()
            results = data.get("results", [])[:num_results]
            if not results:
                return "No results found."
            lines = []
            for r in results:
                lines.append(f"- {r.get('title', 'Untitled')}\n  {r.get('url', '')}\n  {r.get('content', '')[:150]}")
            return "\n".join(lines)
    except httpx.ConnectError:
        return "SearXNG is not running. Start it with Docker to enable web search."
    except Exception as e:
        return f"Search error: {str(e)}"


register_tool(
    name="web_search",
    description="Search the web using SearXNG. Returns titles, URLs, and snippets.",
    parameters={"query": "string", "num_results": "int (optional, default 5)"},
    handler=web_search,
)
