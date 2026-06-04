# Phase 7 — Blind Model Comparison

## Requirements
- Send one prompt to 2-4 selected models in parallel.
- Display responses side by side, blind (labels hidden as Model 1/2/3/4).
- Reveal actual model names on click.
- Optional synthesis: merge the best of each response into one.

## Design
- `routes/compare.py`: POST `/api/compare` — body: `{prompt, models: [{provider, model}]}`.
- Dispatches all models concurrently via asyncio.gather.
- Returns JSON with shuffled responses (blind_label → content) + a mapping (sealed until reveal).
- Optional POST `/api/compare/synthesize` — takes the responses + prompt, LLM merges them.
- Frontend: compare page with prompt input, model selector, side-by-side cards, reveal button, synthesize button.
