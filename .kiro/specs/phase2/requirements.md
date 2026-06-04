# Phase 2 Requirements — Chat + Model Providers

## REQ-1: Provider abstraction
- WHEN a provider is configured, THEN it MUST use the OpenAI-compatible `/v1/chat/completions` interface.
- The system MUST support: Ollama (default, `http://localhost:11434/v1`), OpenAI, OpenRouter, Anthropic (via OpenAI-compat proxy).
- IF a provider is unreachable, THEN return a graceful error message to the frontend (not a crash).

## REQ-2: Settings persistence
- WHEN a user adds/edits a provider or selects a model, THEN persist to `data/settings.json`.
- Settings UI MUST allow: add provider (name, base_url, api_key), select active model.

## REQ-3: Streaming chat
- WHEN a user sends a message, THEN the `/chat` endpoint streams tokens via Server-Sent Events.
- Messages MUST be saved per-session in the Message table (both user and assistant).
- Multi-turn context: all session messages sent as conversation history.

## REQ-4: Sessions
- WHEN the user clicks "New chat", THEN create a new session.
- The sidebar MUST list all sessions (most recent first), with rename and delete.
- WHEN a session is clicked, THEN load its message history.

## REQ-5: Markdown rendering
- WHEN an assistant message contains markdown, THEN render it with syntax-highlighted code blocks.
- Code blocks MUST have a copy button.

## REQ-6: Error handling
- IF the model/provider is unreachable or returns an error, THEN display the error inline in the chat (not a browser alert).
