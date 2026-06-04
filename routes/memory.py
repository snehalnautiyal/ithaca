from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.memory import (
    add_memory, search_memories, list_memories,
    update_memory, delete_memory, export_memories, import_memories,
)

router = APIRouter(prefix="/api/memories", tags=["memories"])


class MemoryCreate(BaseModel):
    content: str
    type: str = "manual"


class MemoryUpdate(BaseModel):
    content: str


class MemoryImport(BaseModel):
    memories: list[dict]


@router.get("")
def get_memories(limit: int = 100, offset: int = 0):
    return list_memories(limit=limit, offset=offset)


@router.get("/search")
def search(q: str, n: int = 10):
    return search_memories(q, n_results=n)


@router.post("", status_code=201)
def create_memory(body: MemoryCreate):
    mem_id = add_memory(body.content, mem_type=body.type)
    return {"id": mem_id, "content": body.content}


@router.put("/{mem_id}")
def edit_memory(mem_id: str, body: MemoryUpdate):
    if not update_memory(mem_id, body.content):
        raise HTTPException(404, "Memory not found")
    return {"id": mem_id, "content": body.content}


@router.delete("/{mem_id}", status_code=204)
def remove_memory(mem_id: str):
    if not delete_memory(mem_id):
        raise HTTPException(404, "Memory not found")


@router.get("/export")
def export_all():
    return export_memories()


@router.post("/import")
def import_all(body: MemoryImport):
    count = import_memories(body.memories)
    return {"imported": count}
