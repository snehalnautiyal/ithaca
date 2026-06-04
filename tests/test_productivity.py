import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def tmp_data(tmp_path, monkeypatch):
    monkeypatch.setattr("services.calendar.events.CALENDAR_FILE", tmp_path / "calendar.json")
    monkeypatch.setattr("services.notes.tasks.NOTES_FILE", tmp_path / "notes.json")


def test_calendar_crud():
    from services.calendar.events import create_event, list_events, update_event, delete_event
    e = create_event("Meeting", "2026-06-04T14:00:00", "2026-06-04T15:00:00")
    assert e["title"] == "Meeting"
    assert len(list_events()) == 1

    update_event(e["id"], title="Updated Meeting")
    events = list_events()
    assert events[0]["title"] == "Updated Meeting"

    delete_event(e["id"])
    assert len(list_events()) == 0


def test_ics_export_import():
    from services.calendar.events import create_event, export_ics, import_ics, list_events
    create_event("Test", "2026-06-04T10:00:00")
    ics = export_ics()
    assert "BEGIN:VCALENDAR" in ics
    assert "Test" in ics

    # Clear and reimport
    from services.calendar.events import _save_events
    _save_events([])
    assert len(list_events()) == 0
    count = import_ics(ics)
    assert count == 1
    assert list_events()[0]["title"] == "Test"


def test_notes_crud():
    from services.notes.tasks import create_note, list_notes, toggle_done, delete_note
    n = create_note("Buy milk", note_type="task")
    assert n["done"] is False
    assert len(list_notes()) == 1

    toggle_done(n["id"])
    notes = list_notes()
    assert notes[0]["done"] is True

    delete_note(n["id"])
    assert len(list_notes()) == 0


def test_checklist():
    from services.notes.tasks import create_note, toggle_checklist_item
    n = create_note("Shopping", checklist=[
        {"text": "Apples", "done": False},
        {"text": "Bread", "done": False},
    ])
    result = toggle_checklist_item(n["id"], 0)
    assert result["checklist"][0]["done"] is True
    assert result["checklist"][1]["done"] is False
