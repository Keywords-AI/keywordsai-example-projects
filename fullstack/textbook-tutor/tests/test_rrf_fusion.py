"""Reciprocal Rank Fusion (`rag._rrf_fuse`).

Hybrid retrieval combines a dense ranking and a BM25 ranking. RRF is the merge:
a node's score is the sum of 1/(k + rank) over the lists it appears in, so rank
(not raw, incomparable cosine-vs-BM25 magnitudes) is all that matters, and a node
both rankers like beats one only a single ranker likes. These pin that contract
without a live index — the whole point of splitting the function out.
"""
from backend.rag import _rrf_fuse


def _ids(nodes):
    return [n.node.node_id for n in nodes]


def test_agreement_beats_a_single_strong_placement(node):
    # "b" is #2 in both lists; "a" and "c" are #1 in one list but absent from the
    # other. RRF at k=60: b = 2/62 ≈ .0323 > a = 1/61 ≈ .0164. Consensus wins.
    dense = [node("a"), node("b")]
    lexical = [node("c"), node("b")]
    out = _rrf_fuse([dense, lexical], k=60, top_n=10)
    assert _ids(out)[0] == "b"


def test_score_is_reciprocal_rank_sum(node):
    dense = [node("x"), node("y")]
    lexical = [node("x")]
    out = _rrf_fuse([dense, lexical], k=60, top_n=10)
    by_id = {n.node.node_id: n.score for n in out}
    # x: rank 1 in both -> 1/61 + 1/61 ; y: rank 2 in one -> 1/62
    assert by_id["x"] == 1 / 61 + 1 / 61
    assert by_id["y"] == 1 / 62
    assert by_id["x"] > by_id["y"]


def test_dedupes_across_lists(node):
    dense = [node("dup"), node("other")]
    lexical = [node("dup")]
    out = _rrf_fuse([dense, lexical], k=60, top_n=10)
    assert _ids(out).count("dup") == 1


def test_respects_top_n(node):
    dense = [node(f"d{i}") for i in range(10)]
    out = _rrf_fuse([dense], k=60, top_n=3)
    assert len(out) == 3


def test_higher_k_flattens_rank_advantage(node):
    # With a large k the gap between rank 1 and rank 2 shrinks toward zero, so a
    # node that appears in both lists (even at rank 2) overtakes a rank-1 loner
    # more easily. Sanity-check the damping direction: rank-1-only vs both-lists.
    dense = [node("solo"), node("both")]
    lexical = [node("both")]
    small_k = _rrf_fuse([dense, lexical], k=1, top_n=10)
    large_k = _rrf_fuse([dense, lexical], k=1000, top_n=10)
    assert _ids(small_k)[0] == "both"
    assert _ids(large_k)[0] == "both"


def test_empty_lists_fuse_to_nothing(node):
    assert _rrf_fuse([[], []], k=60, top_n=5) == []


def test_single_list_preserves_its_order(node):
    dense = [node("first"), node("second"), node("third")]
    out = _rrf_fuse([dense], k=60, top_n=10)
    assert _ids(out) == ["first", "second", "third"]
