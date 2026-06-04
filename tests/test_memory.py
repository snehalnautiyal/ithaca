import pytest
import os
import tempfile
from unittest.mock import patch

# Override chroma path before importing
_tmp_dir = tempfile.mkdtemp()
os.environ["CHROMA_HOST"] = ""  # force embedded mode


def setup_module():
    """Reset memory module globals for clean test."""
    import services.memory as mem
    mem._client = None
    mem._collection = None


@pytest.fixture(autouse=True)
def reset_chroma(tmp_path, monkeypatch):
    import services.memory as mem
    mem._client = None
    mem._collection = None
    monkeypatch.setattr("services.memory._get_client",
        lambda: __import__("chromadb").PersistentClient(path=str(tmp_path / "chroma")))
    mem._collection = None


def test_add_and_search():
    from services.memory import add_memory, search_memories
    mem_id = add_memory("User's favorite language is Python", source_session="s1")
    assert mem_id
    results = search_memories("what programming language")
    assert len(results) >= 1
    assert "Python" in results[0]["content"]


def test_list_memories():
    from services.memory import add_memory, list_memories
    add_memory("Fact one")
    add_memory("Fact two")
    items = list_memories()
    assert len(items) == 2


def test_update_memory():
    from services.memory import add_memory, update_memory, list_memories
    mem_id = add_memory("Old fact")
    update_memory(mem_id, "New fact")
    items = list_memories()
    contents = [i["content"] for i in items]
    assert "New fact" in contents


def test_delete_memory():
    from services.memory import add_memory, delete_memory, list_memories
    mem_id = add_memory("To delete")
    delete_memory(mem_id)
    items = list_memories()
    assert len(items) == 0


def test_export_import():
    from services.memory import add_memory, export_memories, import_memories, list_memories
    add_memory("Export test")
    exported = export_memories()
    assert len(exported) == 1

    # Clear and reimport
    from services.memory import delete_memory
    for m in exported:
        delete_memory(m["id"])
    assert len(list_memories()) == 0

    count = import_memories(exported)
    assert count == 1
    assert len(list_memories()) == 1
