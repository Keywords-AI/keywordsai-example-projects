"""Subject registry — a body of material and the books in it.

A subject owns the books, the uploads directory and the Chroma collection.
Conversations live in chats.py and point back here by `subject_id`; many chats
can share one subject without re-embedding anything.

Persisted as storage/subjects.json:
{
  "subjects": {
    "<id>": {
      "id", "name", "created_at",
      "default_instructions", "default_model",   # copied into new chats
      "books": [{"filename", "title", "pages", "chunks", "added_at"}]
    }
  }
}
"""
import json
import uuid
from datetime import datetime, timezone

from . import config, store


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if config.SUBJECTS_FILE.exists():
        return json.loads(config.SUBJECTS_FILE.read_text())
    return {"subjects": {}}


def _save(state: dict) -> None:
    config.SUBJECTS_FILE.write_text(json.dumps(state, indent=2))


def _summary(s: dict) -> dict:
    return {
        "id": s["id"],
        "name": s["name"],
        "default_instructions": s.get("default_instructions", ""),
        "default_model": s.get("default_model"),
        "book_count": len(s.get("books", [])),
        "created_at": s["created_at"],
    }


def list_subjects() -> list[dict]:
    subjects = _load()["subjects"].values()
    return sorted((_summary(s) for s in subjects), key=lambda x: x["created_at"])


def get(subject_id: str) -> dict | None:
    return _load()["subjects"].get(subject_id)


def create(name: str, default_instructions: str = "") -> dict:
    state = _load()
    subject_id = uuid.uuid4().hex[:12]
    subject = {
        "id": subject_id,
        "name": name.strip() or "Untitled subject",
        "created_at": _now(),
        "default_instructions": (default_instructions or "").strip(),
        "default_model": None,
        "books": [],
    }
    state["subjects"][subject_id] = subject
    _save(state)
    return subject


def update(subject_id: str, name: str | None = None,
           default_instructions: str | None = None,
           default_model: str | None = None) -> dict | None:
    """Update a subject's own fields.

    Defaults are copied into a chat when it is created, never referenced, so
    changing them here does NOT rewrite existing chats — that is what makes a
    chat's teaching style fixed for its lifetime.
    """
    state = _load()
    subject = state["subjects"].get(subject_id)
    if not subject:
        return None
    if name is not None and name.strip():
        subject["name"] = name.strip()
    if default_instructions is not None:
        subject["default_instructions"] = default_instructions.strip()
    if default_model is not None:
        subject.pop("default_model", None)
        subject["default_model"] = config.resolve_model(default_model) if default_model.strip() else None
    _save(state)
    return subject


def upsert_book(subject_id: str, book: dict) -> dict | None:
    """Add a book, or replace every existing entry with the same filename.

    Re-uploading a PDF used to append a *second* entry, so one file could be
    registered N times: N identical retrieval queries and N sets of chunks in
    Chroma with distinct node ids, invisible to the node-id dedup.

    The entry keeps its original position and `added_at`; a replacement also
    gets `updated_at`. Any extra duplicates are collapsed away.
    """
    state = _load()
    subject = state["subjects"].get(subject_id)
    if not subject:
        return None
    books = subject.get("books", [])
    prior = next((b for b in books if b["filename"] == book["filename"]), None)
    entry = {**book, "added_at": (prior or {}).get("added_at") or _now()}
    if prior:
        entry["updated_at"] = _now()

    rebuilt, placed = [], False
    for b in books:
        if b["filename"] != book["filename"]:
            rebuilt.append(b)
        elif not placed:          # keep the first slot, drop any further dupes
            rebuilt.append(entry)
            placed = True
    if not placed:
        rebuilt.append(entry)
    subject["books"] = rebuilt
    _save(state)
    return subject


def rename_book(subject_id: str, filename: str, title: str) -> dict | None:
    state = _load()
    subject = state["subjects"].get(subject_id)
    if not subject:
        return None
    for b in subject.get("books", []):
        if b["filename"] == filename and title.strip():
            b["title"] = title.strip()
    _save(state)
    return subject


def remove_book(subject_id: str, filename: str) -> dict | None:
    state = _load()
    subject = state["subjects"].get(subject_id)
    if not subject:
        return None
    subject["books"] = [b for b in subject.get("books", []) if b["filename"] != filename]
    _save(state)
    return subject


def delete(subject_id: str) -> bool:
    """Delete a subject and everything under it.

    Chats are removed by the caller (app.py) so this module doesn't have to
    import chats.py and create a cycle.
    """
    state = _load()
    if subject_id not in state["subjects"]:
        return False
    del state["subjects"][subject_id]
    _save(state)
    store.delete_index(subject_id)
    return True
