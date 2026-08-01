"""Auto-generated chat titles (`chats.set_generated_title`, `rag.generate_title`).

A chat is named from its first exchange. The rule that matters: a title the user
typed must never be overwritten by the generator.
"""
from types import SimpleNamespace

import pytest

from backend import chats, config, rag, subjects


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SUBJECTS_FILE", tmp_path / "subjects.json")
    monkeypatch.setattr(config, "CHATS_FILE", tmp_path / "chats.json")
    monkeypatch.setattr(config, "MESSAGES_DIR", tmp_path / "messages")


@pytest.fixture
def chat_id():
    return chats.create(subjects.create("AP Biology")["id"])["id"]


def _stub_model(monkeypatch, text):
    monkeypatch.setattr(rag, "_client", SimpleNamespace(messages=SimpleNamespace(
        create=lambda **kw: SimpleNamespace(
            content=[SimpleNamespace(type="text", text=text)]))))


# --- storage rule ---

def test_new_chats_start_untitled(chat_id):
    c = chats.get(chat_id)
    assert c["title"] is None and c["title_generated"] is False


def test_generated_title_is_stored(chat_id):
    chats.set_generated_title(chat_id, "Calvin cycle phases")
    c = chats.get(chat_id)
    assert c["title"] == "Calvin cycle phases" and c["title_generated"] is True


def test_a_user_rename_is_never_overwritten(chat_id):
    chats.update(chat_id, title="My notes")
    assert chats.set_generated_title(chat_id, "Something else") is None
    assert chats.get(chat_id)["title"] == "My notes"


def test_generation_only_happens_once(chat_id):
    chats.set_generated_title(chat_id, "First")
    assert chats.set_generated_title(chat_id, "Second") is None
    assert chats.get(chat_id)["title"] == "First"


def test_renaming_after_generation_still_works(chat_id):
    chats.set_generated_title(chat_id, "Generated")
    chats.update(chat_id, title="Mine")
    assert chats.get(chat_id)["title"] == "Mine"


def test_overlong_titles_are_truncated(chat_id):
    chats.set_generated_title(chat_id, "x" * 300)
    assert len(chats.get(chat_id)["title"]) <= 80


# --- generation ---

def test_title_is_cleaned_of_quotes_and_periods(monkeypatch):
    _stub_model(monkeypatch, '"Calvin cycle phases."')
    assert rag.generate_title({"name": "Bio"}, "q", "a") == "Calvin cycle phases"


def test_blank_generation_yields_none(monkeypatch):
    _stub_model(monkeypatch, "   ")
    assert rag.generate_title({"name": "Bio"}, "q", "a") is None


def test_a_failing_call_never_raises(monkeypatch):
    def boom(**kw):
        raise ConnectionError("gateway down")
    monkeypatch.setattr(rag, "_client", SimpleNamespace(messages=SimpleNamespace(create=boom)))
    # Naming is cosmetic; it must not take an answer down with it.
    assert rag.generate_title({"name": "Bio"}, "q", "a") is None


def test_titles_use_the_cheap_model(monkeypatch):
    seen = {}

    def capture(**kw):
        seen.update(kw)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="A title")])

    monkeypatch.setattr(rag, "_client", SimpleNamespace(messages=SimpleNamespace(create=capture)))
    rag.generate_title({"name": "Bio"}, "q", "a")
    assert seen["model"] == config.REWRITE_MODEL
    assert seen["max_tokens"] <= 64, "naming shouldn't get a generation-sized budget"


def test_the_answer_informs_the_title(monkeypatch):
    """Questions are often 'can you explain this?' — the answer says what was
    actually covered, so both go to the namer."""
    seen = {}

    def capture(**kw):
        seen.update(kw)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="T")])

    monkeypatch.setattr(rag, "_client", SimpleNamespace(messages=SimpleNamespace(create=capture)))
    rag.generate_title({"name": "Bio"}, "can you explain this?", "The Calvin cycle fixes carbon.")
    prompt = seen["messages"][0]["content"]
    assert "can you explain this?" in prompt
    assert "Calvin cycle fixes carbon" in prompt
