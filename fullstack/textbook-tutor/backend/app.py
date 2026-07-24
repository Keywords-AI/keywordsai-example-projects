"""FastAPI app — subjects and chats.

A **subject** owns the books, the uploads directory and the Chroma collection.
A **chat** is one conversation over a subject: its own title, teaching style,
model and history. Many chats share a subject without re-embedding anything.

Generation routes through the Respan gateway (see rag.py), so calls are traced.
"""
import base64
import json
import queue
import threading
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import chats, config, experiments, ingestion, rag, store, subjects

app = FastAPI(title="Ask the Textbook — subjects & chats")
store.init_settings()

_FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
_INDEX = _FRONTEND_DIR / "index.html"


class _RevalidatingStatics(StaticFiles):
    """Static files that must be revalidated, never reused blind.

    Starlette sends etag + last-modified but no Cache-Control, so browsers fall
    back to heuristic caching and can serve a stale asset without asking. That
    produced a real bug: after the theme CSS changed, a browser with the old
    tokens.css kept it, so the new toggle appeared but nothing changed colour.

    `no-cache` still allows caching — it just requires a revalidation first, and
    an unchanged file answers 304 with no body.
    """

    def file_response(self, *args, **kwargs):
        resp = super().file_response(*args, **kwargs)
        resp.headers["Cache-Control"] = "no-cache"
        return resp


app.mount("/static", _RevalidatingStatics(directory=_FRONTEND_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    # Same reasoning as the statics: the shell must not be served from a stale
    # cache, or it will reference assets that no longer exist.
    return HTMLResponse(_INDEX.read_text(), headers={"Cache-Control": "no-cache"})


@app.get("/api/config")
def app_config() -> dict:
    """What the UI needs to know before rendering."""
    return {
        "gateway": config.USE_GATEWAY,
        "default_model": config.GENERATION_MODEL,
        "models": config.AVAILABLE_MODELS,
        "styles": config.TEACHING_STYLES,
        "modes": config.MODES,
    }


def _require_subject(subject_id: str) -> dict:
    subject = subjects.get(subject_id)
    if not subject:
        raise HTTPException(404, "subject not found")
    return subject


def _require_chat(chat_id: str) -> tuple[dict, dict | None]:
    """The chat, and the subject it is filed under — None if it is unfiled."""
    chat = chats.get(chat_id)
    if not chat:
        raise HTTPException(404, "chat not found")
    return chat, subjects.get(chat.get("subject_id")) if chat.get("subject_id") else None


# --- subjects ---

class CreateSubject(BaseModel):
    name: str
    default_instructions: str = ""


class UpdateSubject(BaseModel):
    name: str | None = None
    default_instructions: str | None = None
    default_model: str | None = None


@app.get("/api/sidebar")
def sidebar() -> dict:
    """The whole sidebar in one request: subjects with their chats, plus the
    unfiled chats that don't belong to a subject yet."""
    return {
        "subjects": [{**s, "chats": chats.list_for_subject(s["id"])}
                     for s in subjects.list_subjects()],
        "unfiled": chats.list_unfiled(),
    }


@app.post("/api/subjects")
def create_subject(body: CreateSubject) -> dict:
    return subjects.create(body.name, body.default_instructions)


@app.get("/api/subjects/{subject_id}")
def get_subject(subject_id: str) -> dict:
    subject = _require_subject(subject_id)
    return {**subject, "chats": chats.list_for_subject(subject_id)}


@app.patch("/api/subjects/{subject_id}")
def update_subject(subject_id: str, body: UpdateSubject) -> dict:
    subject = subjects.update(subject_id, body.name, body.default_instructions, body.default_model)
    if not subject:
        raise HTTPException(404, "subject not found")
    return subject


@app.delete("/api/subjects/{subject_id}")
def delete_subject(subject_id: str) -> dict:
    """Delete a subject and its materials — but keep its conversations.

    The books and the search index go; the chats are the user's work, so they
    survive as unfiled and can be dragged into another subject.
    """
    _require_subject(subject_id)
    unfiled = chats.unfile_for_subject(subject_id)
    subjects.delete(subject_id)
    return {"status": "deleted", "id": subject_id, "chats_unfiled": unfiled}


# --- books ---

class RenameBook(BaseModel):
    filename: str
    title: str


@app.post("/api/subjects/{subject_id}/books")
def upload_book(subject_id: str, file: UploadFile = File(...), title: str = Form(None)) -> dict:
    subject = _require_subject(subject_id)

    # file.filename is client-controlled and Starlette does not sanitize it —
    # "../../../backend/rag.py" would escape the uploads dir and overwrite source.
    safe_name = Path(file.filename or "").name
    if not safe_name or safe_name in (".", ".."):
        raise HTTPException(400, "invalid filename")

    # Re-uploading a file replaces that book rather than adding a second copy.
    prior = next((b for b in subject.get("books", []) if b["filename"] == safe_name), None)
    # Keep the existing citation title unless a new one was supplied.
    display_title = (title or (prior or {}).get("title") or Path(safe_name).stem).strip()

    dest_dir = config.UPLOADS_DIR / subject_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / safe_name
    dest.write_bytes(file.file.read())

    # Drop the old chunks BEFORE re-ingesting — delete_book matches on
    # {"source": filename}, so doing it after would also remove the new ones.
    if prior:
        store.delete_book(subject_id, safe_name)

    result = ingestion.ingest(dest, subject_id, display_title)
    subjects.upsert_book(subject_id, {"filename": safe_name, "title": display_title, **result})
    return {"status": "ok", "title": display_title, "replaced": bool(prior), **result}


@app.patch("/api/subjects/{subject_id}/books")
def rename_book(subject_id: str, body: RenameBook) -> dict:
    _require_subject(subject_id)
    subjects.rename_book(subject_id, body.filename, body.title)
    return {"status": "ok", "title": body.title}


@app.delete("/api/subjects/{subject_id}/books")
def remove_book(subject_id: str, filename: str) -> dict:
    subject = _require_subject(subject_id)
    if not any(b["filename"] == filename for b in subject.get("books", [])):
        raise HTTPException(404, "book not found")
    store.delete_book(subject_id, filename)
    subjects.remove_book(subject_id, filename)
    try:
        (config.UPLOADS_DIR / subject_id / filename).unlink()
    except Exception:
        pass
    return {"status": "removed", "filename": filename}


# --- chats ---

class CreateChat(BaseModel):
    instructions: str | None = None
    model: str | None = None


class UpdateChat(BaseModel):
    """No `instructions` on purpose — a chat's teaching style is fixed for its
    lifetime. Changing style means starting a new chat on the same subject."""
    title: str | None = None
    model: str | None = None


@app.post("/api/subjects/{subject_id}/chats")
def create_chat(subject_id: str, body: CreateChat) -> dict:
    subject = _require_subject(subject_id)
    # Unspecified style/model inherit the subject's defaults, by copy.
    instructions = body.instructions if body.instructions is not None else subject.get("default_instructions", "")
    model = body.model if body.model is not None else subject.get("default_model")
    return chats.create(subject_id, instructions, model)


@app.post("/api/chats")
def create_unfiled_chat(body: CreateChat) -> dict:
    """A chat with no subject yet — file it by dragging it onto one."""
    return chats.create(None, body.instructions or "", body.model)


class MoveChat(BaseModel):
    """null files the chat out of every subject."""
    subject_id: str | None = None


@app.post("/api/chats/{chat_id}/move")
def move_chat(chat_id: str, body: MoveChat) -> dict:
    if body.subject_id:
        _require_subject(body.subject_id)
    chat = chats.move(chat_id, body.subject_id)
    if not chat:
        raise HTTPException(404, "chat not found")
    return chat


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str) -> dict:
    chat, subject = _require_chat(chat_id)
    return {**chat,
            "subject": ({"id": subject["id"], "name": subject["name"],
                         "books": subject.get("books", [])} if subject else None),
            "messages": chats.messages(chat_id)}


@app.patch("/api/chats/{chat_id}")
def update_chat(chat_id: str, body: UpdateChat) -> dict:
    chat = chats.update(chat_id, body.title, body.model)
    if not chat:
        raise HTTPException(404, "chat not found")
    return chat


@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: str) -> dict:
    if not chats.delete(chat_id):
        raise HTTPException(404, "chat not found")
    return {"status": "deleted", "id": chat_id}


# --- asking ---

def _maybe_title(chat: dict, subject: dict, question: str, answer: str) -> str | None:
    """Name an untitled chat from its first exchange. Returns the new title.

    Skipped once a chat has a title, so a rename is never overwritten, and
    best-effort: a failed naming call must not fail the answer.
    """
    if chat.get("title_generated") or chat.get("title"):
        return None
    title = rag.generate_title(subject, question, answer)
    if not title:
        return None
    return title if chats.set_generated_title(chat["id"], title) else None


def _persist_turns(chat_id: str, question: str, had_image: bool, result: dict) -> None:
    """Append the user turn and the tutor's answer once an answer is complete."""
    user_text = result.get("query") or question or "(uploaded exercise)"
    chats.append(chat_id, {"role": "user", "content": user_text, "citations": [], "has_image": had_image})
    chats.append(chat_id, {
        "role": "tutor",
        "content": result["answer"],
        "citations": result["citations"],
        "trace": result.get("trace"),
    })


# An unfiled chat has no books, so there is nothing to ground an answer in.
# Say so plainly rather than refusing as though the materials didn't cover it.
_UNFILED = ("This chat isn't in a subject yet, so it has no materials to answer from. "
            "Drag it onto a subject in the sidebar to give it books.")


def _unfiled_reply(question: str) -> dict:
    return {"answer": _UNFILED, "citations": [], "trace": None,
            "query": question, "log_id": None, "request_id": None}


def _read_image(image: UploadFile | None) -> dict | None:
    if image is None:
        return None
    raw = image.file.read()
    if not raw:
        return None
    return {"data": base64.standard_b64encode(raw).decode(),
            "media_type": image.content_type or "image/png"}


# Deliberately sync, NOT `async def`: rag.answer() blocks on the embedding, the
# Chroma query, and 1-2 HTTP calls to Claude. In an async endpoint that runs on
# the event loop and freezes the whole server for the 10-40s an answer takes.
@app.post("/api/chats/{chat_id}/query")
def query_chat(chat_id: str, question: str = Form(""), mode: str = Form("qa"),
               image: UploadFile = File(None)) -> dict:
    chat, subject = _require_chat(chat_id)
    if subject is None:
        return _unfiled_reply(question)
    img = _read_image(image)
    # Load BEFORE appending, so history is the conversation prior to this turn.
    result = rag.answer(subject, chat, question, image=img,
                        history=chats.messages(chat_id), mode=config.resolve_mode(mode))
    _persist_turns(chat_id, question, bool(img), result)
    title = _maybe_title(chat, subject, result.get("query") or question, result["answer"])
    if title:
        result["title"] = title
    return result


# Also sync: StreamingResponse iterates a sync generator in the threadpool, so
# the blocking Claude call still stays off the event loop.
@app.post("/api/chats/{chat_id}/query/stream")
def query_chat_stream(chat_id: str, question: str = Form(""), mode: str = Form("qa"),
                      image: UploadFile = File(None)):
    """Server-sent events: `meta` once retrieval lands, then `delta`s, then `done`."""
    chat, subject = _require_chat(chat_id)
    if subject is None:
        payload = {"type": "done", **_unfiled_reply(question)}
        return StreamingResponse(iter([f"data: {json.dumps(payload)}\n\n"]),
                                 media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache"})
    img = _read_image(image)
    history = chats.messages(chat_id)

    def events():
        final = None
        try:
            for event in rag.answer_stream(subject, chat, question, image=img, history=history,
                                           mode=config.resolve_mode(mode)):
                if event["type"] == "done":
                    final = {k: v for k, v in event.items() if k != "type"}
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            # The stream already has a 200 header, so errors have to travel as
            # an event rather than a status code.
            yield f"data: {json.dumps({'type': 'error', 'detail': type(e).__name__})}\n\n"
            return
        if final:
            _persist_turns(chat_id, question, bool(img), final)
            # Named after the answer lands, so the title reflects what was
            # actually covered. Emitted so the sidebar updates without a reload.
            title = _maybe_title(chat, subject, final.get("query") or question, final["answer"])
            if title:
                yield f"data: {json.dumps({'type': 'title', 'title': title, 'chat_id': chat_id})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# --- evaluation ---

@app.get("/api/chats/{chat_id}/evaluate")
def evaluate(chat_id: str, log_id: str, label: str = ""):
    """Grade one answer by running it as a one-row experiment on Respan.

    Server-sent events, because the round trip is 20-60s: create a dataset, wait
    for the async insert, run five graders, wait for the last score to attach.
    A silent spinner for that long reads as a hang.

    The grading itself is blocking, so it runs on a worker thread and reports
    through a queue — the generator has to be free to yield while the work is
    still going, or the progress all arrives at the end and means nothing.

    Emits `step` events, then one `done` carrying {status, scores, experiment_id}.
    """
    def events():
        q: queue.Queue = queue.Queue()
        box: dict = {}

        def work():
            try:
                result = experiments.evaluate_answer(
                    log_id, label or log_id, on_progress=lambda m: q.put(("step", m)))
                if result.get("status") == "ready":
                    # Kept with the turn so reopening the chat shows the score
                    # instead of paying for a second experiment.
                    chats.set_scores(chat_id, log_id, result["scores"],
                                     result.get("experiment_id", ""))
                box["result"] = result
            except Exception as e:
                box["result"] = {"status": "error", "scores": {},
                                 "detail": type(e).__name__}
            finally:
                q.put(("done", None))

        threading.Thread(target=work, daemon=True).start()
        while True:
            kind, message = q.get()
            if kind == "done":
                break
            yield f"data: {json.dumps({'type': 'step', 'message': message})}\n\n"
        yield f"data: {json.dumps({'type': 'done', **box['result']})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
