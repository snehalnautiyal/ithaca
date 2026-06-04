"""Productivity routes: email, calendar, notes & tasks."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from services.calendar.events import (
    list_events, create_event, update_event, delete_event, export_ics, import_ics
)
from services.notes.tasks import (
    list_notes, create_note, update_note, toggle_done,
    toggle_checklist_item, delete_note, send_notification
)

router = APIRouter(prefix="/api", tags=["productivity"])


# --- Calendar ---

class EventCreate(BaseModel):
    title: str
    start: str
    end: str = None
    description: str = ""
    location: str = ""


class EventUpdate(BaseModel):
    title: str = None
    start: str = None
    end: str = None
    description: str = None
    location: str = None


@router.get("/calendar")
def get_events(start: str = None, end: str = None):
    return list_events(start, end)


@router.post("/calendar", status_code=201)
def add_event(body: EventCreate):
    return create_event(body.title, body.start, body.end, body.description, body.location)


@router.put("/calendar/{event_id}")
def edit_event(event_id: str, body: EventUpdate):
    r = update_event(event_id, **body.model_dump(exclude_none=True))
    if not r:
        raise HTTPException(404)
    return r


@router.delete("/calendar/{event_id}", status_code=204)
def remove_event(event_id: str):
    if not delete_event(event_id):
        raise HTTPException(404)


@router.get("/calendar/export")
def export_calendar():
    return PlainTextResponse(export_ics(), media_type="text/calendar")


@router.post("/calendar/import")
async def import_calendar(body: dict):
    count = import_ics(body.get("ics", ""))
    return {"imported": count}


# --- Notes & Tasks ---

class NoteCreate(BaseModel):
    content: str
    type: str = "note"
    due: str = None
    checklist: list[dict] = None


class NoteUpdate(BaseModel):
    content: str = None
    due: str = None
    done: bool = None


@router.get("/notes")
def get_notes(type: str = None):
    return list_notes(type)


@router.post("/notes", status_code=201)
def add_note(body: NoteCreate):
    return create_note(body.content, body.type, body.due, body.checklist)


@router.put("/notes/{note_id}")
def edit_note(note_id: str, body: NoteUpdate):
    r = update_note(note_id, **body.model_dump(exclude_none=True))
    if not r:
        raise HTTPException(404)
    return r


@router.post("/notes/{note_id}/toggle")
def toggle_note(note_id: str):
    r = toggle_done(note_id)
    if not r:
        raise HTTPException(404)
    return r


@router.post("/notes/{note_id}/checklist/{idx}")
def toggle_check(note_id: str, idx: int):
    r = toggle_checklist_item(note_id, idx)
    if not r:
        raise HTTPException(404)
    return r


@router.delete("/notes/{note_id}", status_code=204)
def remove_note(note_id: str):
    if not delete_note(note_id):
        raise HTTPException(404)


@router.post("/notify")
async def notify(body: dict):
    ok = await send_notification(body.get("title", "Ithaca"), body.get("message", ""))
    return {"sent": ok}
