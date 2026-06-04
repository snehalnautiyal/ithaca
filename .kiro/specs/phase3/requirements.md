# Phase 3 Requirements — Persistent Memory

## REQ-1: Vector storage
- WHEN the app starts, THEN initialize ChromaDB (embedded mode by default, server mode if `CHROMA_HOST` is set in `.env`).
- Embeddings MUST be generated locally via fastembed (ONNX). No external API calls.

## REQ-2: Memory extraction
- AFTER each assistant reply, THEN extract salient facts about the user/tasks and store them as memory entries.
- Each memory entry has: content (text), embedding (vector), metadata (source session, timestamp).

## REQ-3: Memory injection
- BEFORE generating a reply, THEN retrieve the top-K most relevant memories for the user's message.
- Inject retrieved memories into the system prompt context.

## REQ-4: Memory CRUD
- The user MUST be able to view, search, edit, delete memories via `/api/memories`.
- The user MUST be able to import/export all memories as JSON.

## REQ-5: Memory UI
- A Memory page accessible from the header that shows all memories, with search, edit, delete, and import/export buttons.
