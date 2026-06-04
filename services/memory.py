import json
import os
import uuid
from datetime import datetime
from typing import Optional

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

_client: Optional[chromadb.ClientAPI] = None
_collection = None
_embed_fn = None


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        host = os.getenv("CHROMA_HOST")
        if host:
            port = int(os.getenv("CHROMA_PORT", "8000"))
            _client = chromadb.HttpClient(host=host, port=port)
        else:
            _client = chromadb.PersistentClient(path="data/chroma")
    return _client


def _get_embed_fn():
    global _embed_fn
    if _embed_fn is None:
        _embed_fn = ONNXMiniLM_L6_V2()
    return _embed_fn


def _get_collection():
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name="ithaca_memories",
            embedding_function=_get_embed_fn(),
        )
    return _collection


def add_memory(content: str, source_session: str = "", mem_type: str = "fact") -> str:
    collection = _get_collection()
    mem_id = str(uuid.uuid4())
    collection.add(
        ids=[mem_id],
        documents=[content],
        metadatas=[{
            "source_session": source_session,
            "created_at": datetime.utcnow().isoformat(),
            "type": mem_type,
        }],
    )
    return mem_id


def search_memories(query: str, n_results: int = 5) -> list[dict]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_texts=[query], n_results=min(n_results, collection.count()))
    items = []
    for i in range(len(results["ids"][0])):
        items.append({
            "id": results["ids"][0][i],
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else None,
        })
    return items


def list_memories(limit: int = 100, offset: int = 0) -> list[dict]:
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.get(limit=limit, offset=offset, include=["documents", "metadatas"])
    items = []
    for i in range(len(results["ids"])):
        items.append({
            "id": results["ids"][i],
            "content": results["documents"][i],
            "metadata": results["metadatas"][i] if results["metadatas"] else {},
        })
    return items


def update_memory(mem_id: str, content: str) -> bool:
    collection = _get_collection()
    try:
        collection.update(ids=[mem_id], documents=[content])
        return True
    except Exception:
        return False


def delete_memory(mem_id: str) -> bool:
    collection = _get_collection()
    try:
        collection.delete(ids=[mem_id])
        return True
    except Exception:
        return False


def export_memories() -> list[dict]:
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.get(include=["documents", "metadatas"])
    items = []
    for i in range(len(results["ids"])):
        items.append({
            "id": results["ids"][i],
            "content": results["documents"][i],
            "metadata": results["metadatas"][i] if results["metadatas"] else {},
        })
    return items


def import_memories(memories: list[dict]) -> int:
    collection = _get_collection()
    count = 0
    for m in memories:
        mem_id = m.get("id", str(uuid.uuid4()))
        collection.add(
            ids=[mem_id],
            documents=[m["content"]],
            metadatas=[m.get("metadata", {"created_at": datetime.utcnow().isoformat(), "type": "imported"})],
        )
        count += 1
    return count
