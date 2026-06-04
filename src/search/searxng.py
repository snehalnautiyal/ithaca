"""SearXNG search client."""
import os
import httpx

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8080")


async def search(query: str, num_results: int = 5) -> list[dict]:
    """Search SearXNG, return list of {title, url, snippet}."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{SEARXNG_URL}/search", params={
                "q": query, "format": "json", "categories": "general"
            })
            if resp.status_code != 200:
                return []
            data = resp.json()
            results = []
            for r in data.get("results", [])[:num_results]:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:300],
                })
            return results
    except Exception:
        return []
