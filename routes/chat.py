import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import ChatSession, Message, get_db
from src.llm_core.provider import get_provider
from src.chat_processor.memory_hooks import extract_memories, inject_memories

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    content: str


@router.post("/chat")
async def chat(body: ChatRequest, db: Session = Depends(get_db)):
    # Save user message
    session = db.query(ChatSession).get(body.session_id)
    if not session:
        return StreamingResponse(_error_stream("Session not found"), media_type="text/event-stream")

    user_msg = Message(session_id=body.session_id, role="user", content=body.content)
    db.add(user_msg)
    db.commit()

    # Auto-title on first message
    if session.title == "New chat":
        session.title = body.content[:50].strip() or "New chat"
        db.commit()

    # Build conversation history
    messages = db.query(Message).filter(Message.session_id == body.session_id).order_by(Message.created_at).all()
    history = [{"role": m.role, "content": m.content} for m in messages]

    # Inject relevant memories into context
    history = inject_memories(body.content, history)

    return StreamingResponse(_stream_response(history, body.session_id, body.content, db), media_type="text/event-stream")


async def _stream_response(history: list[dict], session_id: str, user_content: str, db: Session):
    full_response = ""
    try:
        provider = get_provider()
        async for token in provider.stream_chat(history):
            full_response += token
            yield f"event: token\ndata: {json.dumps({'content': token})}\n\n"
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"
        return
    finally:
        # Save assistant message
        if full_response:
            assistant_msg = Message(session_id=session_id, role="assistant", content=full_response)
            db.add(assistant_msg)
            db.commit()

    # Extract memories from this exchange (fire-and-forget)
    if full_response:
        try:
            await extract_memories(user_content, full_response, session_id)
        except Exception:
            pass

    yield "event: done\ndata: {}\n\n"


async def _error_stream(detail: str):
    yield f"event: error\ndata: {json.dumps({'detail': detail})}\n\n"
