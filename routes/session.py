from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import ChatSession, Message, get_db

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionRename(BaseModel):
    title: str


@router.get("")
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    return [
        {"id": s.id, "title": s.title, "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat()}
        for s in sessions
    ]


@router.post("", status_code=201)
def create_session(db: Session = Depends(get_db)):
    s = ChatSession(user_id=1)
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "title": s.title}


@router.patch("/{session_id}")
def rename_session(session_id: str, body: SessionRename, db: Session = Depends(get_db)):
    s = db.query(ChatSession).get(session_id)
    if not s:
        raise HTTPException(404)
    s.title = body.title
    db.commit()
    return {"id": s.id, "title": s.title}


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    s = db.query(ChatSession).get(session_id)
    if not s:
        raise HTTPException(404)
    db.delete(s)
    db.commit()


@router.get("/{session_id}/messages")
def get_messages(session_id: str, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
    return [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in msgs]
