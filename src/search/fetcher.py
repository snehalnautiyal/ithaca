"""Fetch and extract text from URLs."""
import re
import httpx


async def fetch_page_text(url: str, max_chars: int = 3000) -> str:
    """Fetch a URL and return extracted text content."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Ithaca-Research/1.0"})
            if resp.status_code != 200:
                return ""
            html = resp.text
            # Strip tags for basic text extraction
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:max_chars]
    except Exception:
        return ""


async def fetch_multiple(urls: list[str], max_chars: int = 3000) -> dict[str, str]:
    """Fetch multiple URLs concurrently. Returns {url: text}."""
    import asyncio
    results = {}
    tasks = [fetch_page_text(url, max_chars) for url in urls[:10]]  # cap at 10
    texts = await asyncio.gather(*tasks, return_exceptions=True)
    for url, text in zip(urls[:10], texts):
        if isinstance(text, str) and text:
            results[url] = text
    return results
