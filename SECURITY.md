# Security Policy

## Reporting Vulnerabilities

If you discover a security issue, please report it privately:

- **Email:** snehalnautiyal@github (or open a private security advisory on this repo)
- **Do not** open a public issue for security vulnerabilities.

## Security Model

Ithaca is designed as a **single-user, self-hosted admin console**. It is not designed for multi-tenant or public-facing deployments.

### Assumptions

- The app runs on `127.0.0.1` by default (localhost only)
- Auth is enabled by default (cookie-based HMAC)
- Agent shell/file tools require explicit confirmation
- Non-admin users get no shell/file access
- All data stays on-device unless you configure cloud model APIs

### What to keep private

- `.env` (contains SECRET_KEY)
- `data/` directory (contains DB, memories, documents, settings)
- API keys configured in Settings
- Any logs that might contain auth tokens

### Hardening for network access

If you bind to `0.0.0.0` for LAN/Tailscale access:

1. Keep `AUTH_ENABLED=true`
2. Use a strong SECRET_KEY
3. Prefer HTTPS via a reverse proxy (Caddy, nginx, Cloudflare Tunnel)
4. Do not expose the raw port to the public internet
5. Keep supporting services (ChromaDB, SearXNG, ntfy, Ollama) internal-only
