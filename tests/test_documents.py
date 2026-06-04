import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

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

    # Patch docs dir
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
async def test_create_document(cookies):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.post("/api/documents", cookies=cookies,
                           json={"title": "Test Doc", "content_type": "markdown", "content": "# Hello"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test Doc"
        assert "id" in data


@pytest.mark.anyio
async def test_get_document(cookies):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        create = await c.post("/api/documents", cookies=cookies,
                             json={"title": "T", "content_type": "markdown", "content": "body"})
        doc_id = create.json()["id"]

        resp = await c.get(f"/api/documents/{doc_id}", cookies=cookies)
        assert resp.status_code == 200
        assert resp.json()["content"] == "body"


@pytest.mark.anyio
async def test_update_document(cookies):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        create = await c.post("/api/documents", cookies=cookies,
                             json={"title": "U", "content_type": "markdown", "content": "old"})
        doc_id = create.json()["id"]

        resp = await c.put(f"/api/documents/{doc_id}", cookies=cookies,
                          json={"content": "new content"})
        assert resp.status_code == 200
        assert resp.json()["content"] == "new content"


@pytest.mark.anyio
async def test_delete_document(cookies):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        create = await c.post("/api/documents", cookies=cookies,
                             json={"title": "D", "content_type": "html", "content": "<p>hi</p>"})
        doc_id = create.json()["id"]

        resp = await c.delete(f"/api/documents/{doc_id}", cookies=cookies)
        assert resp.status_code == 204

        resp = await c.get(f"/api/documents/{doc_id}", cookies=cookies)
        assert resp.status_code == 404


@pytest.mark.anyio
async def test_list_documents(cookies):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        await c.post("/api/documents", cookies=cookies,
                    json={"title": "A", "content_type": "markdown"})
        await c.post("/api/documents", cookies=cookies,
                    json={"title": "B", "content_type": "csv"})

        resp = await c.get("/api/documents", cookies=cookies)
        assert resp.status_code == 200
        assert len(resp.json()) == 2
