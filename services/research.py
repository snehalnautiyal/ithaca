"""Deep Research pipeline: decompose → search → fetch → synthesize."""
import json
from typing import AsyncGenerator

from src.llm_core.provider import get_provider
from src.search.searxng import search
from src.search.fetcher import fetch_multiple


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _llm_generate(messages: list[dict]) -> str:
    provider = get_provider()
    result = ""
    async for token in provider.stream_chat(messages):
        result += token
    return result


async def run_research(query: str) -> AsyncGenerator[str, None]:
    """Run the research pipeline, yielding SSE events."""

    # Step 1: Decompose
    yield _sse("status", {"phase": "decompose", "message": "Breaking down question..."})

    decompose_prompt = f"""Break this research question into 3-5 focused search queries.
Return ONLY a JSON array of strings, nothing else.

Question: {query}"""

    raw = await _llm_generate([
        {"role": "system", "content": "You generate search queries. Return only a JSON array."},
        {"role": "user", "content": decompose_prompt},
    ])

    # Parse queries
    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        sub_queries = json.loads(raw[start:end]) if start != -1 else [query]
    except Exception:
        sub_queries = [query]

    sub_queries = sub_queries[:5]
    yield _sse("queries", {"queries": sub_queries})

    # Step 2: Search
    all_results = []
    for q in sub_queries:
        yield _sse("status", {"phase": "search", "message": f"Searching: {q}"})
        results = await search(q, num_results=3)
        all_results.extend(results)

    # Deduplicate URLs
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    urls = [r["url"] for r in unique_results[:10]]
    yield _sse("sources", {"count": len(urls), "urls": urls})

    # Step 3: Fetch
    source_texts = {}
    if urls:
        yield _sse("status", {"phase": "fetch", "message": f"Reading {len(urls)} sources..."})
        source_texts = await fetch_multiple(urls)

    # Step 4: Synthesize
    yield _sse("status", {"phase": "synthesize", "message": "Writing report..."})

    # Build context from sources
    source_context = ""
    for i, (url, text) in enumerate(source_texts.items(), 1):
        title = next((r["title"] for r in unique_results if r["url"] == url), url)
        source_context += f"\n[Source {i}] {title}\nURL: {url}\nContent: {text[:2000]}\n"

    if not source_context:
        # Fallback: no sources available (SearXNG down)
        source_context = "(No web sources available. Answer from your knowledge.)"

    synth_prompt = f"""Write a comprehensive research report answering this question:

"{query}"

Use the following sources. Cite them as [Source N] in the text.

{source_context}

Format as Markdown with:
- A clear title (# heading)
- Organized sections (## headings)
- Key findings with citations
- A "## Sources" section at the end listing all URLs"""

    report = await _llm_generate([
        {"role": "system", "content": "You are a research analyst. Write clear, well-structured reports with citations."},
        {"role": "user", "content": synth_prompt},
    ])

    # Step 5: Save as document
    from core.database import SessionLocal
    from services.docs import create_doc

    db = SessionLocal()
    try:
        doc = create_doc(db, title=f"Research: {query[:50]}", content_type="markdown", content=report)
        doc_id = doc.id
    finally:
        db.close()

    yield _sse("report", {"content": report, "doc_id": doc_id})
    yield _sse("done", {})
