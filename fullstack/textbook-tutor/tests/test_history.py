"""Conversation-memory windowing (`rag._history_messages`).

The window is a slice of a stored chat log, so it can start mid-exchange and can
contain turns the UI wrote but the model must not choke on. The API requires the
replayed prefix to begin with a user turn.
"""
from backend.rag import _history_messages


def _u(text):
    return {"role": "user", "content": text}


def _t(text):
    return {"role": "tutor", "content": text}


def test_maps_tutor_role_to_assistant():
    out = _history_messages([_u("what is the Calvin cycle?"), _t("it fixes carbon")], 6)
    assert [m["role"] for m in out] == ["user", "assistant"]
    assert out[1]["content"] == "it fixes carbon"


def test_drops_leading_assistant_turn():
    # A window can land mid-exchange; a prefix starting on assistant is invalid.
    out = _history_messages([_t("orphaned answer"), _u("why?"), _t("because")], 6)
    assert out[0]["role"] == "user"
    assert "orphaned" not in out[0]["content"]


def test_empty_and_whitespace_turns_are_skipped():
    out = _history_messages([_u("   "), _u("real question"), _t("answer")], 6)
    assert [m["content"] for m in out] == ["real question", "answer"]


def test_missing_content_key_does_not_crash():
    out = _history_messages([{"role": "user"}, _u("q"), _t("a")], 6)
    assert [m["role"] for m in out] == ["user", "assistant"]


def test_consecutive_same_role_turns_are_merged():
    out = _history_messages([_u("first"), _u("second"), _t("answer")], 6)
    assert len(out) == 2
    assert out[0]["content"] == "first\n\nsecond"


def test_limit_keeps_the_most_recent_turns():
    turns = [_u("old q"), _t("old a"), _u("new q"), _t("new a")]
    out = _history_messages(turns, 2)
    assert [m["content"] for m in out] == ["new q", "new a"]


def test_zero_limit_disables_memory():
    assert _history_messages([_u("q"), _t("a")], 0) == []


def test_negative_limit_disables_memory():
    # Guards against a stray HISTORY_TURNS=-1 slicing from the wrong end.
    assert _history_messages([_u("q"), _t("a")], -1) == []


def test_empty_history():
    assert _history_messages([], 6) == []


def test_result_always_starts_with_user_or_is_empty():
    cases = [
        [],
        [_t("only an answer")],
        [_u("only a question")],
        [_t("a"), _t("b")],
        [_u("q"), _t("a"), _u("q2")],
    ]
    for turns in cases:
        out = _history_messages(turns, 6)
        assert not out or out[0]["role"] == "user", turns


def test_stored_extras_are_not_replayed():
    # Turns also carry citations/trace/has_image; only text should reach Claude.
    turns = [
        {"role": "user", "content": "q", "has_image": True},
        {"role": "tutor", "content": "a", "citations": ["Campbell, p. 1"], "trace": {"x": 1}},
    ]
    out = _history_messages(turns, 6)
    assert all(set(m) == {"role", "content"} for m in out)
