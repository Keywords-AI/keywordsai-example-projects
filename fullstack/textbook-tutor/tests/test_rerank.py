"""Cross-encoder rerank reordering (`store._ranked_by_scores`).

The model itself (a heavy cross-encoder download) is out of scope for the offline
suite; what must not regress is the pure part around it: reorder by the paired
scores, overwrite each node's score with the cross-encoder's, and keep top_n.
"""
from backend.store import _ranked_by_scores


def _ids(nodes):
    return [n.node.node_id for n in nodes]


def test_reorders_by_score_descending(node):
    # Retrieval order is a,b,c; the cross-encoder disagrees and prefers c,a,b.
    nodes = [node("a"), node("b"), node("c")]
    out = _ranked_by_scores(nodes, [2.0, -5.0, 9.0], top_n=3)
    assert _ids(out) == ["c", "a", "b"]


def test_node_score_is_overwritten_with_rerank_score(node):
    nodes = [node("a", score=0.99), node("b", score=0.98)]
    out = _ranked_by_scores(nodes, [1.5, 7.25], top_n=2)
    by_id = {n.node.node_id: n.score for n in out}
    assert by_id["b"] == 7.25 and by_id["a"] == 1.5


def test_truncates_to_top_n(node):
    nodes = [node(f"n{i}") for i in range(6)]
    out = _ranked_by_scores(nodes, [float(i) for i in range(6)], top_n=2)
    # highest scores are n5 (5.0) and n4 (4.0)
    assert _ids(out) == ["n5", "n4"]


def test_promotes_a_low_ranked_candidate(node):
    # The whole point: a chunk retrieval put last can win after reranking.
    nodes = [node("first"), node("second"), node("buried")]
    out = _ranked_by_scores(nodes, [0.1, 0.2, 8.0], top_n=1)
    assert _ids(out) == ["buried"]


def test_empty_is_safe(node):
    assert _ranked_by_scores([], [], top_n=5) == []
