"""Streamed answers (`rag.answer_stream`) and the blocking wrapper on top.

`answer()` is implemented by draining `answer_stream()`, so the two can't drift.
These tests pin the event contract the SSE endpoint and the UI depend on:
meta once retrieval lands, then deltas, then exactly one done.
"""
from types import SimpleNamespace

import pytest

from backend import rag


class _FakeStream:
    """Stands in for the SDK's streaming context manager."""

    def __init__(self, chunks, stop_reason="end_turn", log_id="log-abc"):
        self._chunks = chunks
        self._stop = stop_reason
        self.response = SimpleNamespace(headers={"x-respan-log-id": log_id})

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    @property
    def text_stream(self):
        return iter(self._chunks)

    def get_final_message(self):
        return SimpleNamespace(stop_reason=self._stop)


@pytest.fixture
def stub(monkeypatch, node):
    """Retrieval returns one chunk; generation streams whatever we hand it."""
    def install(chunks, stop_reason="end_turn"):
        monkeypatch.setattr(rag, "_retrieve",
                            lambda t, q: [node("n1", 0.9, source="campbell.pdf", page=1,
                                               text="Photosynthesis happens.")])
        monkeypatch.setattr(rag, "_client", SimpleNamespace(
            messages=SimpleNamespace(stream=lambda **kw: _FakeStream(chunks, stop_reason))))
    return install


@pytest.fixture
def subject_with_book():
    return {"id": "t1", "name": "AP Biology",
            "books": [{"filename": "campbell.pdf", "title": "Campbell"}]}


@pytest.fixture
def chat():
    """Style and model live on the chat now, not the subject."""
    return {"id": "c1", "subject_id": "t1", "title": None, "instructions": "", "model": None}


def _events(subject, chat, **kw):
    return list(rag.answer_stream(subject, chat, kw.pop("q", "what is photosynthesis?"), **kw))


# --- event ordering ---

def test_meta_then_deltas_then_one_done(stub, subject_with_book, chat):
    stub(["Photo", "synthesis ", "happens."])
    evs = _events(subject_with_book, chat)
    kinds = [e["type"] for e in evs]
    assert kinds[0] == "meta", "sources should arrive before any text"
    assert kinds[-1] == "done"
    assert kinds.count("done") == 1
    assert set(kinds[1:-1]) == {"delta"}


def test_meta_carries_citations_and_the_retrieve_trace(stub, subject_with_book, chat):
    stub(["x"])
    meta = _events(subject_with_book, chat)[0]
    assert meta["citations"] == ["Campbell, p. 1"]
    assert meta["retrieve"]["count"] == 1
    assert meta["retrieve"]["chunks"][0]["title"] == "Campbell"


def test_deltas_concatenate_to_the_final_answer(stub, subject_with_book, chat):
    stub(["Photo", "synthesis ", "happens."])
    evs = _events(subject_with_book, chat)
    streamed = "".join(e["text"] for e in evs if e["type"] == "delta")
    assert streamed.strip() == evs[-1]["answer"]


def test_done_carries_the_log_id_from_the_stream_headers(stub, subject_with_book, chat):
    stub(["x"])
    done = _events(subject_with_book, chat)[-1]
    assert done["log_id"] == "log-abc"
    assert done["trace"]["log_id"] == "log-abc"


def test_trace_records_model_and_stop_reason(stub, subject_with_book, chat):
    stub(["x"])
    gen = _events(subject_with_book, chat)[-1]["trace"]["generate"]
    assert gen["stop_reason"] == "end_turn"
    assert gen["model"]


# --- truncation ---

def test_truncated_answer_is_marked_and_the_marker_is_streamed(stub, subject_with_book, chat):
    # A cut-off answer must not read as a complete one, in the stream or after.
    stub(["A partial expl"], stop_reason="max_tokens")
    evs = _events(subject_with_book, chat)
    done = evs[-1]
    assert "cut off" in done["answer"]
    streamed = "".join(e["text"] for e in evs if e["type"] == "delta")
    assert "cut off" in streamed, "the marker never reached the reader"


# --- early exits ---

def test_subject_without_books_yields_one_done_and_no_meta():
    evs = _events({"id": "t1", "name": "X", "books": []}, {"id": "c1", "instructions": "", "model": None})
    assert [e["type"] for e in evs] == ["done"]
    assert "no materials yet" in evs[0]["answer"]


def test_nothing_retrieved_refuses_without_calling_the_model(monkeypatch, subject_with_book, chat):
    monkeypatch.setattr(rag, "_retrieve", lambda t, q: [])
    monkeypatch.setattr(rag, "_client", SimpleNamespace(
        messages=SimpleNamespace(stream=lambda **kw: pytest.fail("model was called"))))
    evs = _events(subject_with_book, chat)
    assert [e["type"] for e in evs] == ["done"]
    assert evs[0]["answer"] == "The course materials don't cover this."


def test_empty_question_is_rejected_before_retrieval(monkeypatch, subject_with_book, chat):
    monkeypatch.setattr(rag, "_retrieve", lambda t, q: pytest.fail("retrieval ran"))
    evs = _events(subject_with_book, chat, q="   ")
    assert [e["type"] for e in evs] == ["done"]


# --- the blocking wrapper ---

def test_answer_returns_the_final_done_payload(stub, subject_with_book, chat):
    stub(["Photo", "synthesis."])
    res = rag.answer(subject_with_book, chat, "what is photosynthesis?")
    assert res["answer"] == "Photosynthesis."
    assert res["citations"] == ["Campbell, p. 1"]
    assert res["log_id"] == "log-abc"
    assert "type" not in res, "the event discriminator leaked into the API payload"


def test_answer_matches_the_stream(stub, subject_with_book, chat):
    """Same pipeline, same result — ignoring the fields that are meant to vary
    per call (a fresh request_id, measured latency)."""
    def stable(d):
        d = {k: v for k, v in d.items() if k not in ("type", "request_id")}
        t = dict(d["trace"])
        t.pop("request_id", None)
        # Measured latencies and the per-call retrieval span id are meant to differ.
        t["generate"] = {k: v for k, v in t["generate"].items() if k != "latency_ms"}
        t["retrieve"] = {k: v for k, v in t["retrieve"].items()
                         if k not in ("latency_ms", "log_id")}
        return {**d, "trace": t}

    stub(["one ", "two ", "three"])
    streamed_done = _events(subject_with_book, chat)[-1]
    stub(["one ", "two ", "three"])
    blocking = rag.answer(subject_with_book, chat, "what is photosynthesis?")
    assert stable(blocking) == stable(streamed_done)


def test_answer_still_works_on_the_early_exit_path():
    res = rag.answer({"id": "t1", "name": "X", "books": []}, {"id": "c1", "instructions": "", "model": None}, "q")
    assert "no materials yet" in res["answer"]
    assert res["trace"] is None
