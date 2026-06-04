# Phase 1 Tasks — Ithaca Skeleton

- [x] 1. Create `.kiro/specs/phase1/requirements.md`
- [x] 2. Create `.kiro/specs/phase1/design.md`
- [ ] 3. Create `requirements.txt` and `.env.example`
- [ ] 4. Create `README.md` with project name and run instructions
- [ ] 5. Implement `core/config.py` — Pydantic Settings from `.env`
- [ ] 6. Implement `core/database.py` — engine, Base, models (User, Session, Message), `get_db()`
- [ ] 7. Implement `core/auth.py` — hash/verify password, sign/verify cookie, login/logout routes, first-boot admin
- [ ] 8. Implement `core/middleware.py` — `AuthMiddleware` skipping public paths
- [ ] 9. Implement `app.py` — app factory, lifespan (first-boot), mount static, include routers, `/health`
- [ ] 10. Implement `static/index.html`, `static/style.css`, `static/app.js` — dark shell with Ithaca header
- [ ] 11. Write `tests/test_auth.py` and `tests/test_models.py`
- [ ] 12. Run app, log in, verify empty Ithaca shell loads ✅
