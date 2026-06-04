# ◈ Ithaca

**Your data, finally home.** A self-hosted, local-first AI workspace.

Chat with local or cloud LLMs, with persistent memory, a document editor, an autonomous agent, deep research, model comparison, and productivity tools — all running on your own hardware. No telemetry. No cloud dependency. Privacy-first.

---

## Features

| Feature | Description |
|---------|-------------|
| 💬 **Chat** | Stream responses from Ollama, OpenAI, OpenRouter, or Anthropic |
| 🧠 **Memory** | Persistent vector memory (ChromaDB) — Ithaca remembers across sessions |
| 📄 **Documents** | Multi-format editor (Markdown/HTML/CSV) with AI-assisted writing |
| 🤖 **Agent** | Autonomous agent with tools: web search, file ops, shell, memory |
| 🔬 **Deep Research** | Multi-step research pipeline with citations and source extraction |
| ⚖️ **Compare** | Blind A/B model comparison with reveal and synthesis |
| 📦 **Cookbook** | Hardware-aware model manager — see what fits your machine |
| 📋 **Notes & Tasks** | Quick notes, checklists, calendar events, ntfy notifications |
| 📱 **PWA** | Installable as a Progressive Web App, fully responsive |

---

## Requirements

- **macOS** (Apple Silicon recommended) or Linux
- **Python 3.11+**
- **Ollama** (for local models) — [ollama.com](https://ollama.com)
- **Docker Desktop** (optional, for SearXNG/ChromaDB server/ntfy)

---

## Quick Start (macOS native)

This is the recommended way to run on Mac — gives you Metal GPU acceleration for local models.

```bash
# Clone
git clone https://github.com/snehalnautiyal/ithaca.git
cd ithaca

# Install Ollama and pull a model
brew install --cask ollama
open /Applications/Ollama.app
ollama pull llama3.2

# Start Ithaca
./start-macos.sh

# First boot prints your admin password in the terminal.
# Open http://127.0.0.1:7860
```

### Manual setup (if you prefer)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — set a real SECRET_KEY (the script generates one for you)

mkdir -p data
python app.py
```

---

## Docker Compose

Runs the full stack: Ithaca + ChromaDB + SearXNG (web search) + ntfy (notifications).

```bash
docker-compose up -d
# Open http://127.0.0.1:7860
```

> ⚠️ Docker on Mac **cannot** access Metal GPU. Use the native start script above for local model inference. Docker is best for the supporting services.

---

## Configuration

All settings via `.env` (copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_BIND` | `127.0.0.1` | Bind address |
| `APP_PORT` | `7860` | Port (7860 avoids macOS AirPlay on 7000) |
| `SECRET_KEY` | — | **Required.** HMAC signing key for auth cookies |
| `AUTH_ENABLED` | `true` | Set `false` to disable login |
| `DATABASE_URL` | `sqlite:///data/app.db` | SQLite path |
| `CHROMA_HOST` | *(empty)* | Set for external ChromaDB server |
| `CHROMA_PORT` | `8000` | ChromaDB server port |
| `SEARXNG_URL` | `http://localhost:8080` | SearXNG instance for web search |
| `NTFY_URL` | `http://localhost:8090` | ntfy server for notifications |

---

## Adding Model Providers

1. Open Ithaca → click **⚙ Settings**
2. Add a provider:
   - **Ollama** (default): `http://localhost:11434/v1` (no API key)
   - **OpenAI**: `https://api.openai.com/v1` + your API key
   - **OpenRouter**: `https://openrouter.ai/api/v1` + your API key
   - **Anthropic** (via OpenAI-compat): use OpenRouter or a proxy
3. Select the active model

---

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn, SQLAlchemy + SQLite
- **Memory:** ChromaDB + ONNX MiniLM (local embeddings, no API calls)
- **Frontend:** Vanilla JS/HTML/CSS (no build step)
- **Local models:** Ollama (Metal GPU on Apple Silicon)
- **Web search:** SearXNG (self-hosted metasearch)
- **Packaging:** Docker Compose + native macOS script

---

## Project Structure

```
app.py                   FastAPI entry point
core/                    Auth, database, config, middleware
src/llm_core/            Model provider abstraction
src/agent_loop/          Autonomous agent
src/agent_tools/         Tools: web, file, shell, memory
src/search/              SearXNG client + page fetcher
src/chat_processor/      Memory extraction/injection hooks
routes/                  API endpoints
services/                Memory, docs, research, calendar, notes, email, cookbook
static/                  Frontend (HTML/CSS/JS, PWA)
tests/                   47 tests
data/                    Runtime data (gitignored)
```

---

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

---

## Security Notes

- Binds to `127.0.0.1` by default — **not** exposed to the network
- Auth enabled by default (cookie-based with HMAC signing)
- Agent shell/file tools require explicit confirmation
- Never expose to the public internet without HTTPS + additional auth
- Treat it like an admin console

---

## Inspired By

Built following patterns from [Odysseus](https://github.com/pewdiepie-archdaemon/odysseus) (MIT licensed, released May 2026). Ithaca is an independent implementation, built from scratch.

---

## License

MIT
