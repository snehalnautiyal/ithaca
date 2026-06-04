# Phase 1 Design — Ithaca Skeleton

## Components

```
app.py              FastAPI app factory, mounts routes, lifespan (first-boot)
core/config.py      Pydantic Settings loaded from .env
core/database.py    SQLAlchemy engine, Base, get_db(), User/Session/Message models
core/auth.py        password hashing, login/logout handlers, session cookie helpers
core/middleware.py  AuthMiddleware (Starlette BaseHTTPMiddleware)
static/             index.html, style.css, app.js
```

## Data models

### User
| column | type | notes |
|--------|------|-------|
| id | Integer PK | |
| username | String | unique |
| hashed_password | String | bcrypt |
| is_admin | Boolean | default true for first user |
| created_at | DateTime | |

### Session
| column | type | notes |
|--------|------|-------|
| id | String PK | uuid4 |
| user_id | FK → User | |
| title | String | default "New chat" |
| created_at | DateTime | |
| updated_at | DateTime | |

### Message
| column | type | notes |
|--------|------|-------|
| id | Integer PK | |
| session_id | FK → Session | |
| role | String | "user" \| "assistant" \| "system" |
| content | Text | |
| created_at | DateTime | |

## Auth flow
- Cookie name: `ithaca_session`
- Value: HMAC-signed `user_id:timestamp` (using `SECRET_KEY` from config)
- Middleware checks cookie on every request; skips `/login`, `/logout`, `/static/*`, `/health`
- `AUTH_ENABLED=false` bypasses the check entirely

## API surface (Phase 1)
| method | path | description |
|--------|------|-------------|
| GET | /health | liveness check |
| GET | / | serve index.html (auth required) |
| GET | /login | serve login page |
| POST | /login | validate creds, set cookie, redirect |
| POST | /logout | clear cookie, redirect |

## Frontend layout
```
┌─────────────────────────────────┐
│  ◈ Ithaca          [logout]     │  ← header
├──────────┬──────────────────────┤
│ Sessions │                      │
│ (empty)  │   (main panel)       │
│          │   "Start a new chat" │
└──────────┴──────────────────────┘
```
Dark theme: background `#0f0f0f`, surface `#1a1a1a`, accent `#7c6af7`.
