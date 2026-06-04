import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.anyio
async def test_searxng_search_handles_failure():
    from src.search.searxng import search
    # SearXNG not running — should return empty list gracefully
    results = await search("test query")
    assert isinstance(results, list)


@pytest.mark.anyio
async def test_fetcher_handles_bad_url():
    from src.search.fetcher import fetch_page_text
    text = await fetch_page_text("http://localhost:99999/nonexistent")
    assert text == ""


@pytest.mark.anyio
async def test_fetcher_multiple_handles_failures():
    from src.search.fetcher import fetch_multiple
    results = await fetch_multiple(["http://localhost:99999/bad1", "http://localhost:99999/bad2"])
    assert isinstance(results, dict)
    assert len(results) == 0


@pytest.mark.anyio
async def test_research_pipeline_with_mocked_search(tmp_path, monkeypatch):
    """Test research pipeline with mocked search and LLM."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from core.database import Base, User
    from core.auth import hash_password

    # Setup test DB
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("core.database.engine", engine)
    monkeypatch.setattr("core.database.SessionLocal", TestSession)

    db = TestSession()
    db.add(User(username="admin", hashed_password=hash_password("test"), is_admin=True))
    db.commit()
    db.close()

    # Patch docs dir
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    monkeypatch.setattr("services.docs.DOCS_DIR", docs_dir)

    # Mock search to return empty (SearXNG not running)
    monkeypatch.setattr("src.search.searxng.search", AsyncMock(return_value=[]))

    # Mock LLM to return predictable responses
    call_count = [0]
    async def mock_generate(messages):
        call_count[0] += 1
        if call_count[0] == 1:
            return '["query 1", "query 2", "query 3"]'
        else:
            return "# Research Report\n\nThis is the synthesized report."

    monkeypatch.setattr("services.research._llm_generate", mock_generate)

    from services.research import run_research
    events = []
    async for event in run_research("test question"):
        events.append(event)

    # Should have status events + queries + report + done
    event_text = "".join(events)
    assert "decompose" in event_text
    assert "queries" in event_text
    assert "report" in event_text
    assert "done" in event_text
    assert "Research Report" in event_text
