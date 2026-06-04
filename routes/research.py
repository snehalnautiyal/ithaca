from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.research import run_research

router = APIRouter(prefix="/api", tags=["research"])


class ResearchRequest(BaseModel):
    query: str


@router.post("/research")
async def research_endpoint(body: ResearchRequest):
    return StreamingResponse(run_research(body.query), media_type="text/event-stream")
