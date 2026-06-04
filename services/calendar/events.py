"""Calendar service: local-first events with .ics import/export."""
import json
import uuid
from datetime import datetime
from pathlib import Path

CALENDAR_FILE = Path("data/calendar.json")


def _load_events() -> list[dict]:
    if not CALENDAR_FILE.exists():
        return []
    return json.loads(CALENDAR_FILE.read_text())


def _save_events(events: list[dict]):
    CALENDAR_FILE.parent.mkdir(parents=True, exist_ok=True)
    CALENDAR_FILE.write_text(json.dumps(events, indent=2))


def list_events(start: str = None, end: str = None) -> list[dict]:
    events = _load_events()
    if start:
        events = [e for e in events if e.get("start", "") >= start]
    if end:
        events = [e for e in events if e.get("start", "") <= end]
    return sorted(events, key=lambda e: e.get("start", ""))


def create_event(title: str, start: str, end: str = None, description: str = "", location: str = "") -> dict:
    events = _load_events()
    event = {
        "id": str(uuid.uuid4()),
        "title": title,
        "start": start,
        "end": end or start,
        "description": description,
        "location": location,
        "created_at": datetime.utcnow().isoformat(),
    }
    events.append(event)
    _save_events(events)
    return event


def update_event(event_id: str, **kwargs) -> dict | None:
    events = _load_events()
    for e in events:
        if e["id"] == event_id:
            e.update({k: v for k, v in kwargs.items() if v is not None})
            _save_events(events)
            return e
    return None


def delete_event(event_id: str) -> bool:
    events = _load_events()
    filtered = [e for e in events if e["id"] != event_id]
    if len(filtered) == len(events):
        return False
    _save_events(filtered)
    return True


def export_ics() -> str:
    """Export all events as .ics format."""
    events = _load_events()
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Ithaca//EN"]
    for e in events:
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{e['id']}",
            f"DTSTART:{_to_ics_date(e['start'])}",
            f"DTEND:{_to_ics_date(e.get('end', e['start']))}",
            f"SUMMARY:{e['title']}",
            f"DESCRIPTION:{e.get('description', '')}",
            f"LOCATION:{e.get('location', '')}",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def import_ics(ics_content: str) -> int:
    """Import events from .ics content."""
    events = _load_events()
    count = 0
    in_event = False
    current = {}

    for line in ics_content.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if line == "BEGIN:VEVENT":
            in_event = True
            current = {"id": str(uuid.uuid4()), "created_at": datetime.utcnow().isoformat()}
        elif line == "END:VEVENT" and in_event:
            if "title" in current and "start" in current:
                events.append(current)
                count += 1
            in_event = False
        elif in_event:
            if line.startswith("SUMMARY:"):
                current["title"] = line[8:]
            elif line.startswith("DTSTART"):
                current["start"] = _from_ics_date(line.split(":", 1)[-1])
            elif line.startswith("DTEND"):
                current["end"] = _from_ics_date(line.split(":", 1)[-1])
            elif line.startswith("DESCRIPTION:"):
                current["description"] = line[12:]
            elif line.startswith("LOCATION:"):
                current["location"] = line[9:]

    _save_events(events)
    return count


def _to_ics_date(dt_str: str) -> str:
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y%m%dT%H%M%S")
    except Exception:
        return dt_str.replace("-", "").replace(":", "").replace(" ", "T")[:15]


def _from_ics_date(ics: str) -> str:
    try:
        if len(ics) >= 15:
            return f"{ics[:4]}-{ics[4:6]}-{ics[6:8]}T{ics[9:11]}:{ics[11:13]}:{ics[13:15]}"
        return ics
    except Exception:
        return ics
