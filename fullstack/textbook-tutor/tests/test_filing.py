"""Filing chats into subjects, and back out (`chats.move`, `unfile_for_subject`).

A chat can exist with no subject at all. That is the whole point of the unfiled
zone: start typing first, decide which material it belongs to later. The rules
worth pinning down are that an unfiled chat is a first-class chat, and that
deleting a subject destroys its *books*, never its conversations.
"""
import pytest

from backend import chats, config, subjects


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SUBJECTS_FILE", tmp_path / "subjects.json")
    monkeypatch.setattr(config, "CHATS_FILE", tmp_path / "chats.json")
    monkeypatch.setattr(config, "MESSAGES_DIR", tmp_path / "messages")


@pytest.fixture
def bio():
    return subjects.create("AP Biology")["id"]


def _ids(found):
    return [c["id"] for c in found]


# --- unfiled chats ---

def test_a_chat_can_start_with_no_subject(bio):
    chat = chats.create(None)
    assert chat["subject_id"] is None
    assert _ids(chats.list_unfiled()) == [chat["id"]]
    assert chats.list_for_subject(bio) == []


def test_unfiled_chats_keep_their_style_and_history(bio):
    chat = chats.create(None, instructions="Socratic — ask, don't tell.")
    chats.append(chat["id"], {"role": "user", "content": "why is the sky blue?"})
    assert chats.get(chat["id"])["instructions"].startswith("Socratic")
    assert len(chats.messages(chat["id"])) == 1


def test_unfiled_listing_carries_the_style_chip():
    chats.create(None, instructions="Socratic — ask, don't tell.")
    assert chats.list_unfiled()[0]["style_label"]


# --- dragging between zones ---

def test_move_files_a_chat_into_a_subject(bio):
    chat = chats.create(None)
    chats.move(chat["id"], bio)
    assert _ids(chats.list_for_subject(bio)) == [chat["id"]]
    assert chats.list_unfiled() == []


def test_move_drags_a_chat_back_out(bio):
    chat = chats.create(bio)
    chats.move(chat["id"], None)
    assert chats.list_for_subject(bio) == []
    assert _ids(chats.list_unfiled()) == [chat["id"]]


def test_move_between_two_subjects_leaves_the_old_one_empty(bio):
    chem = subjects.create("Chemistry")["id"]
    chat = chats.create(bio)
    chats.move(chat["id"], chem)
    assert chats.list_for_subject(bio) == []
    assert _ids(chats.list_for_subject(chem)) == [chat["id"]]


def test_moving_keeps_the_transcript(bio):
    chat = chats.create(None)
    chats.append(chat["id"], {"role": "user", "content": "hello"})
    chats.move(chat["id"], bio)
    assert len(chats.messages(chat["id"])) == 1


def test_move_of_an_unknown_chat_returns_none(bio):
    assert chats.move("nope", bio) is None


# --- deleting a subject keeps the conversations ---

def test_deleting_a_subject_unfiles_its_chats_rather_than_deleting_them(bio):
    a, b = chats.create(bio)["id"], chats.create(bio)["id"]
    assert chats.unfile_for_subject(bio) == 2
    assert sorted(_ids(chats.list_unfiled())) == sorted([a, b])
    assert chats.get(a) is not None and chats.get(b) is not None


def test_unfiling_leaves_other_subjects_alone(bio):
    chem = subjects.create("Chemistry")["id"]
    kept = chats.create(chem)["id"]
    chats.create(bio)
    chats.unfile_for_subject(bio)
    assert _ids(chats.list_for_subject(chem)) == [kept]


def test_unfiling_a_subject_with_no_chats_is_a_no_op(bio):
    assert chats.unfile_for_subject(bio) == 0
