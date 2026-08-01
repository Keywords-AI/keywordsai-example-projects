"""Per-difficulty slicing of experiment scores.

The whole-set average hides retrieval quality: easy questions pin the retrieval
graders to the ceiling and drown out the hard ones. `averages_by` splits scores
into buckets and `_slice_label` names them, so a hard-answerable slice can be read
apart from an easy control. These pin that split offline (no platform calls)."""
from backend.experiments import averages_by
from scripts.run_experiment import _slice_label


def _span(input_, evaluator, value):
    return {"input": input_, "scores": {evaluator: {"evaluator_name": evaluator, "numerical_value": value}}}


def test_slice_label_buckets():
    assert _slice_label({"kind": "answerable", "difficulty": "easy"}) == "answerable/easy"
    assert _slice_label({"kind": "answerable", "difficulty": "medium"}) == "answerable/medium"
    assert _slice_label({"kind": "answerable"}) == "answerable/plain"
    assert _slice_label({"kind": "partial"}) == "partial"
    assert _slice_label({"kind": "out-of-corpus"}) == "out-of-corpus"
    # Lecture mode wins over kind: it retrieves differently, so it grades apart.
    assert _slice_label({"kind": "answerable", "mode": "lecture"}) == "lecture"


def test_averages_by_groups_by_bucket_and_evaluator():
    meta = {"qA": {"kind": "answerable", "difficulty": "easy"},
            "qB": {"kind": "answerable", "difficulty": "medium"},
            "qC": {"kind": "answerable", "difficulty": "medium"}}
    found = [
        _span("qA", "ctx-rel", 1.0),
        _span("qB", "ctx-rel", 0.2),
        _span("qC", "ctx-rel", 0.4),
    ]
    out = averages_by(found, lambda s: meta.get(s["input"]), _slice_label)
    assert out["ctx-rel"]["answerable/easy"] == [1.0]
    assert sorted(out["ctx-rel"]["answerable/medium"]) == [0.2, 0.4]


def test_averages_by_drops_unresolved_spans():
    found = [_span("known", "cite", 0.9), _span("orphan", "cite", 0.1)]
    meta = {"known": {"kind": "partial"}}
    out = averages_by(found, lambda s: meta.get(s["input"]), _slice_label)
    # The orphan span (no metadata) is dropped, not bucketed as a mystery slice.
    assert out["cite"] == {"partial": [0.9]}


def test_averages_by_bucket_returning_none_skips():
    found = [_span("x", "ground", 0.5)]
    out = averages_by(found, lambda s: {"kind": "answerable"}, lambda m: None)
    assert out == {}
