# Ithaca — Tech standards

- Language: Python 3.11+. Style: type hints, small focused modules, no god-files.
- Web: FastAPI + Uvicorn. SSE for streaming. SQLAlchemy + SQLite (`data/app.db`).
- Memory: ChromaDB + fastembed (ONNX). No external embedding calls by default.
- Frontend: vanilla JS/HTML/CSS, modular files under `static/js/`. No build step.
- Models: OpenAI-compatible interface for all providers (Ollama default at `http://localhost:11434/v1`).
- Security: bind `127.0.0.1` by default; auth on (`AUTH_ENABLED=true`); shell/file tools admin-only with explicit per-run confirmation.
- Secrets & `data/`: gitignored, never logged.
- Tests required for every route and core module.
- Port: `7860` by default (avoids macOS AirPlay on 7000). Configurable via `.env`.
- Docker Compose for SearXNG, ChromaDB server, ntfy — but run the Python app natively on Mac for Metal GPU access.
