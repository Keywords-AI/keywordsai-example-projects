"""Retrieval span (`rag._log_retrieval`).

Retrieval runs against local Chroma, so it never produces a gateway span. We
post one ourselves so the retrieve step is visible in Respan alongside the LLM
steps. It is telemetry: it must never delay or break an answer.
"""
from types import SimpleNamespace

import pytest

from backend import config, rag


@pytest.fixture
def captured(monkeypatch):
    """Capture what would be POSTed, and run the pool inline so it's assertable."""
    sent = []
    monkeypatch.setattr(rag, "_post_retrieval_span", lambda payload: sent.append(payload))
    monkeypatch.setattr(rag._span_pool, "submit",
                        lambda fn, *a, **kw: fn(*a, **kw) or SimpleNamespace())
    monkeypatch.setattr(config, "RESPAN_API_KEY", "sk-respan-test")
    return sent


def test_posts_a_task_span_named_retrieve(captured):
    rag._log_retrieval({"name": "AP Biology"}, "the query", "the context", 0.031, "req-1", 3)
    assert len(captured) == 1
    p = captured[0]
    assert p["log_type"] == "task"
    assert p["span_name"] == "retrieve"


def test_span_carries_the_query_and_retrieved_context(captured):
    # Input/output are what the retrieval-step graders read.
    rag._log_retrieval({"name": "X"}, "where is the stroma?", "[Campbell, p. 1] ...", 0.02, "req-1", 2)
    p = captured[0]
    assert p["input"] == "where is the stroma?"
    assert p["output"] == "[Campbell, p. 1] ..."


def test_correlates_with_the_generation_span_via_request_id(captured):
    # There's no trace linkage available (the gateway logs generation itself and
    # respan_params has no trace id), so request_id is how the two spans meet.
    rag._log_retrieval({"name": "X"}, "q", "ctx", 0.01, "req-abc", 1)
    assert captured[0]["metadata"]["request_id"] == "req-abc"


def test_returns_the_id_it_supplied(captured):
    span_id = rag._log_retrieval({"name": "X"}, "q", "ctx", 0.01, "req-1", 1)
    assert span_id == captured[0]["unique_id"]
    assert len(span_id) == 32


def test_ids_are_unique_per_call(captured):
    a = rag._log_retrieval({"name": "X"}, "q", "ctx", 0.01, "req-1", 1)
    b = rag._log_retrieval({"name": "X"}, "q", "ctx", 0.01, "req-2", 1)
    assert a != b


def test_latency_and_chunk_count_are_recorded(captured):
    rag._log_retrieval({"name": "X"}, "q", "ctx", 0.0313, "req-1", 7)
    p = captured[0]
    assert p["latency"] == pytest.approx(0.0313)
    assert p["metadata"]["chunks"] == "7"


def test_skipped_entirely_without_an_api_key(monkeypatch):
    monkeypatch.setattr(config, "RESPAN_API_KEY", None)
    monkeypatch.setattr(rag._span_pool, "submit",
                        lambda *a, **kw: pytest.fail("posted without a key"))
    assert rag._log_retrieval({"name": "X"}, "q", "ctx", 0.01, "req-1", 1) is None


def test_a_failing_post_never_raises(monkeypatch):
    """The real _post_retrieval_span swallows everything — telemetry must not
    take an answer down with it."""
    def boom(url, *a, **kw):
        raise ConnectionError("respan unreachable")
    monkeypatch.setattr(rag.urllib.request, "urlopen", boom)
    monkeypatch.setattr(config, "RESPAN_API_KEY", "sk-respan-test")
    rag._post_retrieval_span({"unique_id": "x"})   # must not raise
