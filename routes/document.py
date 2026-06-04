from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.docs import create_doc, get_doc, update_doc, delete_doc, list_docs
from src.llm_core.provider import get_provider

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocCreate(BaseModel):
    title: str
    content_type: str = "markdown"
    content: str = ""


class DocUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class AssistRequest(BaseModel):
    doc_id: str
    selection: str
    action: str  # suggest, continue, rewrite
    context: str = ""


ASSIST_PROMPTS = {
    "suggest": "Suggest improvements to this text. Return only the improved version:\n\n{selection}",
    "continue": "Continue writing from where this text ends. Return only the continuation:\n\n{selection}",
    "rewrite": "Rewrite this text to be clearer and more concise. Return only the rewritten version:\n\n{selection}",
}


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    return list_docs(db)


@router.post("", status_code=201)
def create_document(body: DocCreate, db: Session = Depends(get_db)):
    doc = create_doc(db, body.title, body.content_type, body.content)
    return {"id": doc.id, "title": doc.title, "content_type": doc.content_type}


@router.get("/{doc_id}")
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = get_doc(db, doc_id)
    if not doc:
        raise HTTPException(404)
    return doc


@router.put("/{doc_id}")
def update_document(doc_id: str, body: DocUpdate, db: Session = Depends(get_db)):
    doc = update_doc(db, doc_id, title=body.title, content=body.content)
    if not doc:
        raise HTTPException(404)
    return doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    if not delete_doc(db, doc_id):
        raise HTTPException(404)


@router.post("/assist")
async def ai_assist(body: AssistRequest, db: Session = Depends(get_db)):
    if body.action not in ASSIST_PROMPTS:
        raise HTTPException(400, "action must be: suggest, continue, or rewrite")

    prompt = ASSIST_PROMPTS[body.action].format(selection=body.selection)
    if body.context:
        prompt = f"Document context:\n{body.context}\n\n{prompt}"

    messages = [
        {"role": "system", "content": "You are a writing assistant. Return only the requested text, no explanations."},
        {"role": "user", "content": prompt},
    ]

    try:
        provider = get_provider()
        suggestion = ""
        async for token in provider.stream_chat(messages):
            suggestion += token
        return {"original": body.selection, "suggestion": suggestion.strip()}
    except Exception as e:
        raise HTTPException(502, f"AI provider error: {str(e)}")
