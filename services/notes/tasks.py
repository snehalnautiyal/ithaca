"""Notes & Tasks: quick notes, checklist todos, reminders via ntfy."""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import httpx

NOTES_FILE = Path("data/notes.json")
NTFY_URL = os.getenv("NTFY_URL", "http://localhost:8090")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "ithaca")


def _load_notes() -> list[dict]:
    if not NOTES_FILE.exists():
        return []
    return json.loads(NOTES_FILE.read_text())


def _save_notes(notes: list[dict]):
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    NOTES_FILE.write_text(json.dumps(notes, indent=2))


def list_notes(filter_type: str = None) -> list[dict]:
    notes = _load_notes()
    if filter_type:
        notes = [n for n in notes if n.get("type") == filter_type]
    return sorted(notes, key=lambda n: n.get("created_at", ""), reverse=True)


def create_note(content: str, note_type: str = "note", due: str = None, checklist: list[dict] = None) -> dict:
    notes = _load_notes()
    note = {
        "id": str(uuid.uuid4()),
        "content": content,
        "type": note_type,  # note, task, reminder
        "done": False,
        "due": due,
        "checklist": checklist or [],
        "created_at": datetime.utcnow().isoformat(),
    }
    notes.append(note)
    _save_notes(notes)
    return note


def update_note(note_id: str, **kwargs) -> dict | None:
    notes = _load_notes()
    for n in notes:
        if n["id"] == note_id:
            n.update({k: v for k, v in kwargs.items() if v is not None})
            _save_notes(notes)
            return n
    return None


def toggle_done(note_id: str) -> dict | None:
    notes = _load_notes()
    for n in notes:
        if n["id"] == note_id:
            n["done"] = not n["done"]
            _save_notes(notes)
            return n
    return None


def toggle_checklist_item(note_id: str, item_index: int) -> dict | None:
    notes = _load_notes()
    for n in notes:
        if n["id"] == note_id and n.get("checklist"):
            if 0 <= item_index < len(n["checklist"]):
                n["checklist"][item_index]["done"] = not n["checklist"][item_index]["done"]
                _save_notes(notes)
                return n
    return None


def delete_note(note_id: str) -> bool:
    notes = _load_notes()
    filtered = [n for n in notes if n["id"] != note_id]
    if len(filtered) == len(notes):
        return False
    _save_notes(filtered)
    return True


async def send_notification(title: str, message: str = "") -> bool:
    """Send notification via ntfy."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{NTFY_URL}/{NTFY_TOPIC}",
                content=message,
                headers={"Title": title},
            )
            return resp.status_code == 200
    except Exception:
        return False
