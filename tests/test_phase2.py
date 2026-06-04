import json
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app import app
from core.database import Base, create_tables, SessionLocal, User, ChatSession
from core.auth import hash_password, make_session_cookie, COOKIE_NAME
from src.llm_core.settings import load_settings, save_settings, SETTINGS_PATH


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    """Use a temp DB and settings for each test."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("core.config.settings.database_url", f"sqlite:///{db_path}")

    # Reinitialize engine for tests
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    monkeypatch.setattr("core.database.engine", engine)
    monkeypatch.setattr("core.database.SessionLocal", TestSession)

    # Create admin user
    db = TestSession()
    user = User(username="admin", hashed_password=hash_password("test"), is_admin=True)
    db.add(user)
    db.commit()
    db.close()

    # Settings
    settings_path = tmp_path / "settings.json"
    monkeypatch.setattr("src.llm_core.settings.SETTINGS_PATH", settings_path)


@pytest.fixture
def auth_cookie():
    return {COOKIE_NAME: make_session_cookie(1)}


@pytest.mark.anyio
async def test_create_session(auth_cookie):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/sessions", cookies=auth_cookie)
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["title"] == "New chat"


@pytest.mark.anyio
async def test_list_sessions(auth_cookie):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/sessions", cookies=auth_cookie)
        resp = await client.get("/api/sessions", cookies=auth_cookie)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


@pytest.mark.anyio
async def test_settings_crud(auth_cookie, tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"
    monkeypatch.setattr("src.llm_core.settings.SETTINGS_PATH", settings_path)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/models/settings", cookies=auth_cookie)
        assert resp.status_code == 200
        data = resp.json()
        assert data["active_provider"] == "Ollama"

        resp = await client.put(
            "/api/models/settings",
            cookies=auth_cookie,
            json={"active_model": "mistral"},
        )
        assert resp.status_code == 200
        assert resp.json()["active_model"] == "mistral"


def test_provider_creation():
    from src.llm_core.provider import LLMProvider
    p = LLMProvider(name="Test", base_url="http://localhost:11434/v1", api_key=None)
    assert p.name == "Test"
    assert p.base_url == "http://localhost:11434/v1"
