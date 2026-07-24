"""Lecture mode: neighbour expansion and reading order (`rag._in_reading_order`).

Q&A retrieval wants the best-matching fragments. A lecture wants the passage the
idea lives in, which top-K by similarity actively destroys: it returns three
disconnected pieces of a section and drops the sentences joining them.

So lecture pulls the chunks either side of each hit and presents the result in
the order the book reads. The two things that would break silently are ordering
(a lecture built from shuffled excerpts still *looks* fine) and the budget
dropping a hit in favour of a neighbour, so both are pinned here.
"""
from types import SimpleNamespace

import pytest

from backend import config, rag


def node(node_id, source="axler.pdf", text="text"):
    """Shaped like a retrieved NodeWithScore, minus everything unused here."""
    return SimpleNamespace(
        node=SimpleNamespace(node_id=node_id, metadata={"source": source},
                             get_content=lambda: text),
        score=0.5)


def ids(nodes):
    return [n.node.node_id for n in nodes]


# --- ordering ---

def test_excerpts_come_back_in_reading_order():
    hits = [node("c5"), node("c1")]                    # retrieved, best score first
    extra = [node("c0"), node("c2"), node("c4"), node("c6")]
    positions = {"c0": 0, "c1": 1, "c2": 2, "c4": 4, "c5": 5, "c6": 6}
    assert ids(rag._in_reading_order(hits, extra, positions, 20)) == \
        ["c0", "c1", "c2", "c4", "c5", "c6"]


def test_books_are_kept_apart():
    """Interleaving two books would read as one incoherent lecture."""
    hits = [node("b1", source="raven.pdf"), node("a1", source="axler.pdf")]
    extra = [node("a0", source="axler.pdf"), node("b0", source="raven.pdf")]
    positions = {"a0": 0, "a1": 1, "b0": 0, "b1": 1}
    out = [n.node.metadata["source"] for n in rag._in_reading_order(hits, extra, positions, 20)]
    assert out == ["axler.pdf", "axler.pdf", "raven.pdf", "raven.pdf"]


def test_a_chunk_with_no_known_position_sorts_last_not_first():
    hits = [node("c1")]
    extra = [node("mystery")]
    out = ids(rag._in_reading_order(hits, extra, {"c1": 1}, 20))
    assert out == ["c1", "mystery"]


# --- the budget ---

def test_neighbours_are_dropped_before_hits():
    """A hit is why the lecture is about this topic at all."""
    hits = [node(f"h{i}") for i in range(4)]
    extra = [node(f"n{i}") for i in range(10)]
    positions = {f"h{i}": i * 10 for i in range(4)} | {f"n{i}": i for i in range(10)}
    out = ids(rag._in_reading_order(hits, extra, positions, 6))
    assert len(out) == 6
    assert all(f"h{i}" in out for i in range(4)), "a hit was dropped for a neighbour"


def test_the_budget_is_respected_exactly():
    hits = [node("h0")]
    extra = [node(f"n{i}") for i in range(50)]
    positions = {"h0": 0} | {f"n{i}": i + 1 for i in range(50)}
    assert len(rag._in_reading_order(hits, extra, positions, config.LECTURE_MAX_CHUNKS)) \
        == config.LECTURE_MAX_CHUNKS


def test_a_neighbour_that_is_already_a_hit_is_not_duplicated():
    hits = [node("c1")]
    extra = [node("c1"), node("c2")]          # the store may return an overlap
    assert ids(rag._in_reading_order(hits, extra, {"c1": 1, "c2": 2}, 20)) == ["c1", "c2"]


# --- mode selection ---

def test_lecture_uses_the_lecture_prompt():
    assert "TAUGHT the concept" in rag.LECTURE_TEMPLATE
    assert "Never add outside knowledge" in rag.LECTURE_TEMPLATE


def test_an_image_forces_solve_whatever_mode_is_selected():
    """Pointing at an exercise is not a request for a lecture."""
    import inspect
    src = inspect.getsource(rag.answer_stream)
    assert 'effective_mode = "solve" if image else mode' in src


@pytest.mark.parametrize("requested,expected", [
    ("lecture", "lecture"), ("qa", "qa"), ("solve", "qa"), ("", "qa"), (None, "qa"),
    ("../etc", "qa"),
])
def test_only_known_modes_reach_prompt_selection(requested, expected):
    # The value picks a system prompt, so an unknown one must fall back rather
    # than reaching the template lookup.
    assert config.resolve_mode(requested) == expected
