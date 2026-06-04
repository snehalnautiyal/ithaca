# Phase 6 Design — Deep Research

## Architecture
```
src/search/
├── searxng.py        # SearXNG query client
└── fetcher.py        # Fetch + extract text from URLs

services/research.py  # Pipeline orchestrator (async generator yielding SSE events)
routes/research.py    # POST /api/research (SSE stream)
```

## Pipeline steps

1. **Decompose**: LLM breaks question into 3-5 search sub-queries (JSON array).
2. **Search**: For each sub-query, query SearXNG → collect top 3 results per query.
3. **Fetch**: For each unique URL, fetch page and extract text (first 3000 chars).
4. **Synthesize**: Send all extracted content + original question to LLM → produce structured Markdown report.
5. **Save**: Auto-save report as a document in the workspace.

## SSE events
```
event: status    data: {"phase": "decompose", "message": "Breaking down question..."}
event: queries   data: {"queries": ["q1", "q2", "q3"]}
event: status    data: {"phase": "search", "message": "Searching: q1"}
event: sources   data: {"count": 8, "urls": ["..."]}
event: status    data: {"phase": "fetch", "message": "Reading 8 sources..."}
event: status    data: {"phase": "synthesize", "message": "Writing report..."}
event: report    data: {"content": "# Report\n...", "doc_id": "uuid"}
event: done      data: {}
```

## API
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/research | Start research. Body: `{query}`. Returns SSE stream. |
