"""Chats — one conversation, usually over a subject's materials.

A chat owns its title, teaching style, model and message history. Many chats
share one subject, so switching between them costs nothing: the books and the
Chroma collection belong to the subject.

`subject_id` may be None — an **unfiled** chat, started before deciding where it
belongs. It has no materials, so it cannot answer until it is filed into a
subject; the query endpoint says so rather than guessing.

Two files, deliberately:

  storage/chats.json            metadata for every chat — what the sidebar needs
  storage/messages/{id}.json    the turns

Metadata changes on every turn (`updated_at`, `turn_count`). Keeping it out of
subjects.json means a turn doesn't rewrite the book registry, and keeping it out
of the message files means drawing the sidebar doesn't open all of them.
"""
import json
import uuid
from datetime import datetime, timezone

from . import config


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if config.CHATS_FILE.exists():
        return json.loads(config.CHATS_FILE.read_text())
    return {"chats": {}}


def _save(state: dict) -> None:
    config.CHATS_FILE.write_text(json.dumps(state, indent=2))


def _message_file(chat_id: str):
    config.MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
    return config.MESSAGES_DIR / f"{chat_id}.json"


# --- registry ---

def create(subject_id: str | None, instructions: str = "", model: str | None = None) -> dict:
    """Start a chat. Style and model are COPIED in, never referenced.

    That copy is what makes the style fixed: changing the subject's defaults
    later cannot retroactively alter a conversation that has already started.
    """
    state = _load()
    chat_id = uuid.uuid4().hex[:12]
    chat = {
        "id": chat_id,
        "subject_id": subject_id,
        "title": None,               # filled in from the first exchange
        "title_generated": False,
        "instructions": (instructions or "").strip(),
        "model": config.resolve_model(model) if model else None,
        "created_at": _now(),
        "updated_at": _now(),
        "turn_count": 0,
    }
    state["chats"][chat_id] = chat
    _save(state)
    return chat


def get(chat_id: str) -> dict | None:
    return _load()["chats"].get(chat_id)


def _decorate(found: list[dict]) -> list[dict]:
    """Most recently used first, each with the style chip shown in the sidebar."""
    found.sort(key=lambda c: c.get("updated_at") or "", reverse=True)
    return [{**c, "style_label": config.style_label(c.get("instructions"))} for c in found]


def list_for_subject(subject_id: str) -> list[dict]:
    return _decorate([c for c in _load()["chats"].values() if c.get("subject_id") == subject_id])


def list_unfiled() -> list[dict]:
    """Chats not in any subject yet."""
    return _decorate([c for c in _load()["chats"].values() if not c.get("subject_id")])


def move(chat_id: str, subject_id: str | None) -> dict | None:
    """File a chat into a subject, or drag it back out (subject_id=None).

    Materials come from the subject, so moving a chat changes what its *next*
    answers can draw on. Turns already in the thread are left alone — they cite
    what they actually used.
    """
    state = _load()
    chat = state["chats"].get(chat_id)
    if chat is None:
        return None
    chat["subject_id"] = subject_id or None
    _save(state)
    return chat


def update(chat_id: str, title: str | None = None, model: str | None = None) -> dict | None:
    """Rename or re-model a chat.

    `instructions` is deliberately absent: a chat's teaching style is fixed for
    its lifetime, and changing style means starting a new chat on the same
    subject.
    """
    state = _load()
    chat = state["chats"].get(chat_id)
    if not chat:
        return None
    if title is not None and title.strip():
        chat["title"] = title.strip()
        chat["title_generated"] = True   # a rename must not be overwritten later
    if model is not None:
        chat.pop("model", None)
        chat["model"] = config.resolve_model(model) if model.strip() else None
    _save(state)
    return chat


def set_generated_title(chat_id: str, title: str) -> dict | None:
    """Set the auto-generated title, unless the user already named this chat."""
    state = _load()
    chat = state["chats"].get(chat_id)
    if not chat or chat.get("title_generated"):
        return None
    chat["title"] = title.strip()[:80]
    chat["title_generated"] = True
    _save(state)
    return chat


def delete(chat_id: str) -> bool:
    state = _load()
    if chat_id not in state["chats"]:
        return False
    del state["chats"][chat_id]
    _save(state)
    f = _message_file(chat_id)
    if f.exists():
        f.unlink()
    return True


def unfile_for_subject(subject_id: str) -> int:
    """Detach a subject's chats instead of deleting them. Returns how many.

    Deleting a subject removes its books and search index, but the
    conversations are the user's work — they survive as unfiled chats and can be
    dragged into another subject.
    """
    state = _load()
    moved = [c for c in state["chats"].values() if c.get("subject_id") == subject_id]
    for c in moved:
        c["subject_id"] = None
    if moved:
        _save(state)
    return len(moved)


# --- messages ---

def messages(chat_id: str) -> list[dict]:
    f = _message_file(chat_id)
    return json.loads(f.read_text()) if f.exists() else []


def set_scores(chat_id: str, log_id: str, scores: dict, experiment_id: str) -> bool:
    """Attach grader scores to the turn that produced span `log_id`.

    Stored with the turn so a score survives a reload: grading costs a real
    experiment run, and re-running it just because someone reopened the chat
    would be paying twice for the same answer.
    """
    turns = messages(chat_id)
    for turn in turns:
        if (turn.get("trace") or {}).get("log_id") == log_id:
            turn["scores"] = scores
            turn["experiment_id"] = experiment_id
            _message_file(chat_id).write_text(json.dumps(turns, indent=2))
            return True
    return False


def append(chat_id: str, turn: dict) -> None:
    turns = messages(chat_id)
    turns.append(turn)
    _message_file(chat_id).write_text(json.dumps(turns, indent=2))
    state = _load()
    chat = state["chats"].get(chat_id)
    if chat:
        chat["updated_at"] = _now()
        chat["turn_count"] = len(turns)
        _save(state)
