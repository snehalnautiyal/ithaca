# Phase 2 Design — Chat + Model Providers

## Architecture

```
src/llm_core/
├── __init__.py
├── provider.py       # Base class + factory
└── settings.py       # Load/save data/settings.json

routes/
├── session.py        # /api/sessions CRUD
├── chat.py           # /api/chat (SSE)
└── model.py          # /api/models (list providers, set active)
```

## Provider abstraction (`src/llm_core/provider.py`)

All providers use OpenAI-compatible chat completions:

```python
class LLMProvider:
    name: str
    base_url: str
    api_key: str | None
    
    async def stream_chat(messages: list[dict], model: str) -> AsyncGenerator[str, None]:
        """Yield token strings from streaming response."""
```

Factory reads `data/settings.json` → instantiates the active provider.

## Settings schema (`data/settings.json`)

```json
{
  "providers": [
    {"name": "Ollama", "base_url": "http://localhost:11434/v1", "api_key": null}
  ],
  "active_provider": "Ollama",
  "active_model": "llama3.2"
}
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/sessions | List sessions (newest first) |
| POST | /api/sessions | Create new session |
| PATCH | /api/sessions/{id} | Rename session |
| DELETE | /api/sessions/{id} | Delete session + messages |
| GET | /api/sessions/{id}/messages | Get message history |
| POST | /api/chat | SSE stream; body: `{session_id, content}` |
| GET | /api/models | List providers + available models |
| GET | /api/models/settings | Get current settings |
| PUT | /api/models/settings | Update settings |

## SSE format

```
event: token
data: {"content": "Hello"}

event: done
data: {}

event: error
data: {"detail": "Connection refused"}
```

## Frontend additions

- `static/js/chat.js` — send message, consume SSE, render markdown
- `static/js/sessions.js` — sidebar CRUD
- `static/js/settings.js` — settings modal
- `static/js/markdown.js` — marked.js + highlight.js (CDN) + copy button
- Sidebar becomes live; main panel becomes the chat view
