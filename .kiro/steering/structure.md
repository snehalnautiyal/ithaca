# Ithaca — Project structure

```
ithaca/
├── app.py                   # FastAPI entry point
├── core/
│   ├── auth.py              # Login/logout, middleware
│   ├── database.py          # SQLAlchemy engine, session, models
│   ├── middleware.py        # Auth middleware, CORS
│   └── config.py            # Load .env, settings
├── src/
│   ├── llm_core/            # Model provider abstraction
│   ├── agent_loop/          # Agent planning and execution
│   ├── agent_tools/         # Tools: web, file, shell, memory
│   ├── chat_processor/      # Chat logic, context assembly
│   └── search/              # SearXNG integration
├── routes/
│   ├── chat.py              # /chat (SSE streaming)
│   ├── session.py           # /sessions (list, create, delete)
│   ├── document.py          # /documents (CRUD)
│   ├── memory.py            # /memories (CRUD, search)
│   └── model.py             # /models (list providers, settings)
├── services/
│   ├── docs.py              # Document persistence
│   ├── memory.py            # ChromaDB + fastembed
│   └── search.py            # SearXNG client
├── static/
│   ├── index.html           # Single-page shell with 'Ithaca' header
│   ├── style.css            # Dark theme
│   ├── app.js               # Main wiring
│   └── js/                  # Modular frontend: chat.js, sessions.js, etc.
├── data/                    # gitignored
│   ├── app.db               # SQLite
│   ├── chroma/              # ChromaDB persistence
│   ├── uploads/             # User files
│   ├── personal_docs/       # Documents workspace
│   └── settings.json        # User settings
├── .env                     # gitignored
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Rules
- Keep all secrets and `data/` out of git.
- Small, focused modules — no single file over ~300 lines.
- Use the name **Ithaca** in page titles, the app header, and the README.
