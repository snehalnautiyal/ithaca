"""Document persistence: DB metadata + filesystem content."""
from pathlib import Path
from sqlalchemy.orm import Session

from core.database import Document

DOCS_DIR = Path("data/personal_docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

EXT_MAP = {"markdown": "md", "html": "html", "csv": "csv"}


def _file_path(doc_id: str, content_type: str) -> Path:
    ext = EXT_MAP.get(content_type, "md")
    return DOCS_DIR / f"{doc_id}.{ext}"


def create_doc(db: Session, title: str, content_type: str, content: str = "") -> Document:
    doc = Document(title=title, content_type=content_type)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    _file_path(doc.id, content_type).write_text(content, encoding="utf-8")
    return doc


def get_doc(db: Session, doc_id: str) -> dict | None:
    doc = db.query(Document).get(doc_id)
    if not doc:
        return None
    fp = _file_path(doc.id, doc.content_type)
    content = fp.read_text(encoding="utf-8") if fp.exists() else ""
    return {
        "id": doc.id,
        "title": doc.title,
        "content_type": doc.content_type,
        "content": content,
        "created_at": doc.created_at.isoformat(),
        "updated_at": doc.updated_at.isoformat(),
    }


def update_doc(db: Session, doc_id: str, title: str | None = None, content: str | None = None) -> dict | None:
    doc = db.query(Document).get(doc_id)
    if not doc:
        return None
    if title is not None:
        doc.title = title
    if content is not None:
        _file_path(doc.id, doc.content_type).write_text(content, encoding="utf-8")
    db.commit()
    db.refresh(doc)
    return get_doc(db, doc_id)


def delete_doc(db: Session, doc_id: str) -> bool:
    doc = db.query(Document).get(doc_id)
    if not doc:
        return False
    fp = _file_path(doc.id, doc.content_type)
    if fp.exists():
        fp.unlink()
    db.delete(doc)
    db.commit()
    return True


def list_docs(db: Session) -> list[dict]:
    docs = db.query(Document).order_by(Document.updated_at.desc()).all()
    return [
        {"id": d.id, "title": d.title, "content_type": d.content_type, "updated_at": d.updated_at.isoformat()}
        for d in docs
    ]
