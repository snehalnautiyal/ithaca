# Phase 3 Design — Persistent Memory

## Architecture

```
services/memory.py      ChromaDB client, add/search/delete/export/import
src/chat_processor/     (new) memory extraction + injection hooks
routes/memory.py        /api/memories CRUD + search + import/export
```

## ChromaDB setup
- Embedded mode: `chromadb.PersistentClient(path="data/chroma")`
- Server mode (if `CHROMA_HOST` set): `chromadb.HttpClient(host, port)`
- Collection name: `ithaca_memories`
- Embedding function: `chromadb.utils.embedding_functions.ONNXMiniLM_L6_V2()` (fastembed/ONNX, local)

## Memory entry schema
```json
{
  "id": "uuid",
  "content": "User prefers Python over JavaScript",
  "metadata": {
    "source_session": "session-uuid",
    "created_at": "2026-06-04T...",
    "type": "preference"
  }
}
```

## Extraction logic (after each exchange)
- Send the last user+assistant exchange to the LLM with a system prompt:
  "Extract facts worth remembering about the user. Return JSON array of strings. Return [] if nothing notable."
- Store each extracted fact as a memory entry.

## Injection logic (before reply)
- Query ChromaDB with the user's latest message, get top 5 results.
- Prepend to system prompt: "Relevant memories: ..."

## API endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/memories | List all (paginated) |
| GET | /api/memories/search?q=... | Semantic search |
| POST | /api/memories | Add manually |
| PUT | /api/memories/{id} | Edit |
| DELETE | /api/memories/{id} | Delete |
| GET | /api/memories/export | Export all as JSON |
| POST | /api/memories/import | Import JSON |

## Frontend
- "Memory" button in header → navigates to memory page
- Memory page: list view with search bar, each item editable/deletable
- Import/export buttons
