# Ithaca

───────────────────────────────────────────────
 ⊹ ࣪ ˖ ◈ Ithaca · Your data, finally home.
───────────────────────────────────────────────

A self-hosted AI workspace — meant to be the self-hosted version of the UI experience you get from ChatGPT and Claude. Running on your own hardware, with your own data — local-first, privacy-first, and no telemetry.

## Features

**Chat** — chat with any local model or API; adding them is super simple.
　Ollama · OpenAI · OpenRouter · Anthropic · any OpenAI-compatible endpoint

**Agent** — hand it tools and let it run the whole task itself.
　web search · file read/write · shell exec · memory · MCP support · safety gates

**Cookbook** — Scans your hardware, recommends models, click to download and serve. Easy!
　Apple Silicon aware · Metal GPU · unified memory detection · fit scoring · Ollama serving

**Deep Research** — multi-step runs that gather, read, and synthesize sources into a nice visual report.
　decompose → search → fetch → synthesize · citations · auto-save to docs

**Compare** — a fun tool to compare models side by side. Test completely blind, no bias!
　multi-model · blind labels · reveal · synthesis

**Documents** — YOU write the text, AI is there to assist, not the opposite.
　multi-tab editor · markdown · HTML · CSV · AI edits · suggestions · inline diff

**Memory** — Persistent memory, your assistant evolves over time as it better understands you and your tasks!
　ChromaDB · ONNX embeddings (local) · vector + keyword retrieval · import/export

**Email** — IMAP/SMTP inbox with AI triage built in: urgency flags, auto-tag, auto-summary, reply drafts.
　IMAP · SMTP · per-account config

**Notes & Tasks** — Quick notes with reminders, a todo list, and scheduled tasks the agent can act on.
　checklist · reminders · ntfy notifications

**Calendar** — Local-first calendar with .ics import/export.
　events CRUD · .ics export/import · agent-aware

**Works on mobile** — looks and runs great on your phone, not just desktop.
　responsive · installable (PWA) · touch gestures

---

## Quick Start

Defaults work out of the box: clone, run, then configure models/search/email inside Settings. Only edit `.env` for deployment-level overrides like `APP_BIND`, `APP_PORT`, `AUTH_ENABLED`, `DATABASE_URL`, or a pre-seeded admin password.

On first start, Ithaca creates an admin account and prints a temporary password in the terminal. Use that for the first login, then change it in Settings.

### Docker (recommended for full stack)

```bash
git clone https://github.com/snehalnautiyal/ithaca.git
cd ithaca
cp .env.example .env
docker compose up -d --build
```

Open http://localhost:7860 when the containers are healthy. Docker Compose binds all services to `127.0.0.1` by default.

### Native Linux / macOS

```bash
git clone https://github.com/snehalnautiyal/ithaca.git
cd ithaca
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data
python app.py
```

Requirements: Python 3.11+.

### Apple Silicon

Docker on macOS cannot use the Metal GPU. For GPU-accelerated local models on an M-series Mac, run Ithaca natively:

```bash
git clone https://github.com/snehalnautiyal/ithaca.git
cd ithaca
./start-macos.sh
```

It launches at http://127.0.0.1:7860. The script creates a venv, installs deps, generates a secret key, and starts the server.

To expose to your phone over a trusted LAN/VPN (e.g. Tailscale), set `APP_BIND=0.0.0.0` in `.env`.

Keep `AUTH_ENABLED=true` (the default) before binding outside loopback. **Do not expose this port directly to the public internet.**

---

## Configuration

Most setup is done inside the app via Settings. Use `.env` for deployment-level defaults and secrets.

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_BIND` | `127.0.0.1` | Bind address. Use `0.0.0.0` for LAN access. |
| `APP_PORT` | `7860` | Web UI port (avoids macOS AirPlay on 7000) |
| `SECRET_KEY` | *generated* | HMAC signing key for auth cookies |
| `AUTH_ENABLED` | `true` | Enable/disable login |
| `DATABASE_URL` | `sqlite:///data/app.db` | Database connection string |
| `CHROMA_HOST` | *(empty)* | ChromaDB host. Empty = embedded mode. |
| `CHROMA_PORT` | `8000` | ChromaDB port |
| `SEARXNG_URL` | `http://localhost:8080` | SearXNG instance for web search |
| `NTFY_URL` | `http://localhost:8090` | ntfy server for notifications |

---

## Adding Model Providers

1. Open Ithaca → click **⚙ Settings**
2. Add a provider:
   - **Ollama** (default): `http://localhost:11434/v1` — no API key needed
   - **OpenAI**: `https://api.openai.com/v1` + your API key
   - **OpenRouter**: `https://openrouter.ai/api/v1` + your API key
   - **Anthropic** (via OpenAI-compat proxy): use OpenRouter
3. Select the active model from the dropdown

---

## Security Notes

Ithaca is a self-hosted workspace with powerful local tools: shell access, file read/write, web research, email integrations, and model management. Treat it like an admin console.

- Keep `AUTH_ENABLED=true` for any network-accessible deployment.
- Do not expose it directly to the public internet without HTTPS and a trusted reverse proxy.
- Agent shell/file tools require explicit per-run confirmation.
- Non-admin users get no shell/file access.
- Keep `.env`, `data/`, databases, uploads, and API keys out of Git (ignored by default).
- Prefer binding to `127.0.0.1`; bind to `0.0.0.0` only for intentional LAN/VPN access.
- Keep ChromaDB, SearXNG, ntfy, Ollama, and model APIs internal-only.

---

## Architecture

```
app.py                   # FastAPI entry point
core/                    # Auth, database, middleware, config
src/llm_core/            # Model provider abstraction
src/agent_loop/          # Autonomous agent (plan + execute)
src/agent_tools/         # Tools: web, file, shell, memory
src/search/              # SearXNG client + page fetcher
src/chat_processor/      # Memory extraction/injection hooks
routes/                  # API endpoints (chat, session, document, memory, model, agent, research, compare, cookbook, productivity)
services/                # Memory, docs, research, calendar, notes, email, cookbook
static/                  # Frontend (HTML/CSS/JS, PWA, no build step)
tests/                   # 47 tests
data/                    # Runtime data (gitignored)
```

### Data

All user data lives in `data/` (gitignored): `app.db` (sessions, messages, documents, users), `chroma/` (vector memory), `personal_docs/`, `settings.json`, `calendar.json`, `notes.json`.

---

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Database | SQLite via SQLAlchemy |
| Memory/Vectors | ChromaDB + ONNX MiniLM (all local, no API) |
| Frontend | Vanilla JS + HTML + CSS (no framework, no build step) |
| Local models | Ollama (Metal GPU on Apple Silicon) |
| Cloud models | OpenAI, OpenRouter, Anthropic APIs |
| Web search | SearXNG (self-hosted metasearch) |
| Notifications | ntfy |
| Packaging | Docker Compose + native macOS script |

---

## Contributing

Help is welcome. Best entry points: fresh-install testing, provider bugs, mobile/editor polish, and docs.

---

## License

MIT — see [LICENSE](LICENSE).

```
                                  |
                                 |||
                                |||||
                  |    |    |   |||||||
                 )_)  )_)  )_)   ~|~
                )___))___))___)\  |
               )____)____)_____)\\|
             _____|____|____|_____\\\__
             \                       /
       ~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~
           ~^~  your data, finally home  ~^~
       ~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~
```
