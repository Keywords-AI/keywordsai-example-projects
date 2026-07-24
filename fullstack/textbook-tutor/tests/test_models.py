"""Per-chat model selection (`config.resolve_model`, `chats.update`).

The chosen id is sent straight to the API, so it comes from an allowlist rather
than free text — a typo would otherwise 404 every question in the chat.
"""
import pytest

from backend import chats, config, subjects


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SUBJECTS_FILE", tmp_path / "subjects.json")
    monkeypatch.setattr(config, "CHATS_FILE", tmp_path / "chats.json")
    monkeypatch.setattr(config, "MESSAGES_DIR", tmp_path / "messages")


# --- resolve_model ---

@pytest.mark.parametrize("model", [m["id"] for m in config.AVAILABLE_MODELS])
def test_allowlisted_models_pass_through(model):
    assert config.resolve_model(model) == model


@pytest.mark.parametrize("bad", ["", None, "gpt-4o", "claude-opus-4-8-20260101", "  "])
def test_anything_else_falls_back_to_the_default(bad):
    assert config.resolve_model(bad) == config.GENERATION_MODEL


def test_every_listed_model_has_a_label():
    for m in config.AVAILABLE_MODELS:
        assert m["id"] and m["label"]


def test_default_model_is_selectable():
    # Otherwise the picker would show a "Default" option users can't get back to.
    assert config.GENERATION_MODEL in {m["id"] for m in config.AVAILABLE_MODELS}


def test_thinking_is_derived_per_selected_model(monkeypatch):
    # Picking Haiku from the UI must not send adaptive thinking to a pre-4.6
    # model, which would 400 every request.
    monkeypatch.setattr(config, "THINKING_ON", True)
    assert config.thinking_config(config.resolve_model("claude-haiku-4-5")) is None
    assert config.thinking_config(config.resolve_model("claude-opus-4-8")) == {"type": "adaptive"}


# --- persistence ---

def _chat():
    """A chat on a fresh subject — model lives on the chat."""
    subject = subjects.create("AP Biology")
    return chats.create(subject["id"])["id"]


def test_model_is_none_until_set():
    assert chats.get(_chat())["model"] is None


def test_setting_a_model_persists_it():
    tid = _chat()
    chats.update(tid, model="claude-sonnet-5")
    assert chats.get(tid)["model"] == "claude-sonnet-5"


def test_empty_string_clears_back_to_default():
    tid = _chat()
    chats.update(tid, model="claude-sonnet-5")
    chats.update(tid, model="")
    assert chats.get(tid)["model"] is None


def test_unknown_model_is_not_stored_verbatim():
    tid = _chat()
    chats.update(tid, model="totally-made-up")
    assert chats.get(tid)["model"] == config.GENERATION_MODEL


def test_renaming_leaves_the_model_alone():
    tid = _chat()
    chats.update(tid, model="claude-haiku-4-5")
    chats.update(tid, title="Photosynthesis")
    c = chats.get(tid)
    assert c["title"] == "Photosynthesis" and c["model"] == "claude-haiku-4-5"
