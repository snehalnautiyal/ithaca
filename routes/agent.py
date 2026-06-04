from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core.auth import get_user_id_from_cookie
from src.agent_loop.loop import run_agent

router = APIRouter(prefix="/api", tags=["agent"])


class AgentRequest(BaseModel):
    task: str
    confirmed_tools: list[str] = []


@router.post("/agent")
async def agent_endpoint(body: AgentRequest, request: Request):
    # Admin-only check
    uid = get_user_id_from_cookie(request)
    if not uid:
        return StreamingResponse(_err("Unauthorized"), media_type="text/event-stream")

    return StreamingResponse(run_agent(body.task, body.confirmed_tools), media_type="text/event-stream")


async def _err(detail: str):
    import json
    yield f"event: error\ndata: {json.dumps({'detail': detail})}\n\n"
