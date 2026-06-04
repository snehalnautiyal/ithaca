# Phase 1 Requirements — Ithaca Skeleton

## REQ-1: Server
- WHEN the app starts, THEN it binds to `127.0.0.1:7860` by default.
- IF `APP_BIND` or `APP_PORT` are set in `.env`, THEN use those values instead.
- WHEN `/health` is requested, THEN return `{"status": "ok"}` with HTTP 200.

## REQ-2: Database
- WHEN the app starts, THEN SQLAlchemy creates `data/app.db` (SQLite) if it does not exist.
- The database MUST have models: `User`, `Session`, `Message`.

## REQ-3: First-boot admin
- WHEN no users exist in the database, THEN create an admin user with a random 12-char password and print it to the terminal.
- WHEN the admin user already exists, THEN skip creation silently.

## REQ-4: Authentication
- WHEN `AUTH_ENABLED=true` (default), THEN all routes except `/login`, `/logout`, and `/static/*` require a valid session cookie.
- WHEN a user POSTs valid credentials to `/login`, THEN set a signed session cookie and redirect to `/`.
- WHEN a user POSTs to `/logout`, THEN clear the session cookie and redirect to `/login`.
- IF `AUTH_ENABLED=false`, THEN all routes are accessible without a cookie.

## REQ-5: Shell UI
- WHEN an authenticated user visits `/`, THEN serve `static/index.html`.
- The page MUST display the wordmark **Ithaca** in the header.
- The layout MUST have a left sidebar (sessions list, empty for now) and a main panel.
- The theme MUST be dark.

## REQ-6: Config
- WHEN the app starts, THEN load settings from `.env` via `python-dotenv`.
- A `.env.example` MUST document all supported variables.
