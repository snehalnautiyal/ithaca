# Ithaca — Product

**Tagline:** Your data, finally home.

## Goal
Ithaca is a self-hosted web app where a single user chats with local or API LLMs, with persistent memory, a document editor, and an autonomous agent. Everything runs on the user's own hardware.

## Principles
- **Local-first:** all data stays on-device by default; no cloud sync unless the user explicitly configures a cloud model API.
- **Privacy-first:** no telemetry, no analytics, no phoning home. Ever.
- **Auth-gated:** single-user for now; all routes protected by cookie-based auth.
- **Primary target:** Apple Silicon Mac (M-series). Must run natively for Metal GPU access.

## Non-goals
- Multi-user / SaaS
- Public internet exposure (treat it like an admin console)
- vLLM (Linux/CUDA only — not supported on Mac)
