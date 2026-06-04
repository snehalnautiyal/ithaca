# Phase 2 Tasks — Chat + Model Providers

- [ ] 1. Implement `src/llm_core/settings.py` — load/save `data/settings.json`
- [ ] 2. Implement `src/llm_core/provider.py` — LLMProvider with async stream_chat
- [ ] 3. Implement `routes/session.py` — CRUD endpoints
- [ ] 4. Implement `routes/chat.py` — SSE streaming endpoint
- [ ] 5. Implement `routes/model.py` — provider/model settings endpoints
- [ ] 6. Update `app.py` to mount new routers under `/api`
- [ ] 7. Update frontend: sessions sidebar, chat view, markdown rendering, settings modal
- [ ] 8. Write tests for provider and chat endpoint
- [ ] 9. Run app, verify streaming chat with Ollama ✅
