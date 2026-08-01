"""Coverage-first merge (`rag._merge_source_diverse`).

The reason this exists: plain top-k over the whole corpus lets one strong book
crowd out a weaker one, so the tutor can only ever cite a single source and
"synthesise across books" silently degrades to "quote one book".
"""
from backend.rag import _merge_source_diverse


def _ids(nodes):
    return [n.node.node_id for n in nodes]


def test_every_book_contributes_its_best_chunk(node):
    # Campbell outscores Raven on every chunk; Raven must still get in.
    campbell = [node("c1", 0.9), node("c2", 0.85), node("c3", 0.8)]
    raven = [node("r1", 0.3), node("r2", 0.2)]
    out = _merge_source_diverse([campbell, raven], max_chunks=3)
    assert "c1" in _ids(out)
    assert "r1" in _ids(out), "weak book lost its guaranteed slot"


def test_remaining_budget_is_filled_by_score(node):
    campbell = [node("c1", 0.9), node("c2", 0.85)]
    raven = [node("r1", 0.3), node("r2", 0.25)]
    out = _merge_source_diverse([campbell, raven], max_chunks=3)
    # c1 + r1 guaranteed, then the best leftover (c2 at 0.85) takes the last slot.
    assert _ids(out) == ["c1", "r1", "c2"]


def test_duplicate_node_ids_are_deduped(node):
    # The same chunk can surface in two per-book queries; it must appear once.
    shared = node("dup", 0.9)
    out = _merge_source_diverse([[shared, node("c2", 0.5)], [shared]], max_chunks=5)
    assert _ids(out).count("dup") == 1


def test_respects_max_chunks(node):
    books = [[node(f"b{b}c{c}", 0.9 - c / 10) for c in range(4)] for b in range(4)]
    out = _merge_source_diverse(books, max_chunks=5)
    assert len(out) == 5


def test_more_books_than_budget_still_truncates(node):
    # 6 books each guaranteed a slot, but the budget is 3 — the cap must win,
    # otherwise the context blows past MAX_CONTEXT_CHUNKS.
    books = [[node(f"b{b}", 0.1 * b)] for b in range(6)]
    out = _merge_source_diverse(books, max_chunks=3)
    assert len(out) == 3
    # Truncation keeps the highest scoring of the guaranteed picks.
    assert _ids(out) == ["b5", "b4", "b3"]


def test_books_with_no_hits_are_skipped(node):
    out = _merge_source_diverse([[], [node("r1", 0.4)], []], max_chunks=5)
    assert _ids(out) == ["r1"]


def test_no_hits_at_all(node):
    assert _merge_source_diverse([[], []], max_chunks=5) == []


def test_none_scores_do_not_crash(node):
    # Some retrievers return score=None; sorting must not raise.
    out = _merge_source_diverse([[node("a", None), node("b", None)]], max_chunks=2)
    assert len(out) == 2
