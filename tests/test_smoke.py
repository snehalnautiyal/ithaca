"""Smoke test: verify all endpoints are reachable and app boots correctly."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from core.database import Base, User
from core.auth import hash_password, make_session_cookie, COOKIE_NAME


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("core.database.engine", engine)
    monkeypatch.setattr("core.database.SessionLocal", TestSession)

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    monkeypatch.setattr("services.docs.DOCS_DIR", docs_dir)

    db = TestSession()
    db.add(User(username="admin", hashed_password=hash_password("test"), is_admin=True))
    db.commit()
    db.close()


@pytest.fixture
def cookies():
    return {COOKIE_NAME: make_session_cookie(1)}


@pytest.mark.anyio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_all_api_endpoints_reachable(cookies):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Sessions
        resp = await c.get("/api/sessions", cookies=cookies)
        assert resp.status_code == 200

        # Models settings
        resp = await c.get("/api/models/settings", cookies=cookies)
        assert resp.status_code == 200

        # Memories
        resp = await c.get("/api/memories", cookies=cookies)
        assert resp.status_code == 200

        # Documents
        resp = await c.get("/api/documents", cookies=cookies)
        assert resp.status_code == 200


@pytest.mark.anyio
async def test_static_assets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.get("/static/manifest.json")
        assert resp.status_code == 200
        assert "Ithaca" in resp.text

        resp = await c.get("/static/sw.js")
        assert resp.status_code == 200

        resp = await c.get("/static/style.css")
        assert resp.status_code == 200


@pytest.mark.anyio
async def test_pwa_manifest_valid():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.get("/static/manifest.json")
        data = resp.json()
        assert data["name"] == "Ithaca"
        assert data["display"] == "standalone"
        assert data["theme_color"] == "#7c6af7"
