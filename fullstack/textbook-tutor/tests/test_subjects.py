"""Book registry (`subjects.upsert_book`).

Regression guard for the duplication bug: re-uploading a PDF used to append a
second registry entry, so one file could be registered N times — N identical
retrieval queries, N sets of chunks in Chroma, and a silently changed title.
"""
import pytest

from backend import config, subjects


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path, monkeypatch):
    """Point the registry at a temp file so tests never touch storage/."""
    monkeypatch.setattr(config, "SUBJECTS_FILE", tmp_path / "subjects.json")


@pytest.fixture
def subject_id():
    return subjects.create("AP Biology")["id"]


def _book(filename, title, chunks=2):
    return {"filename": filename, "title": title, "pages": 2, "chunks": chunks}


def _books(subject_id):
    return subjects.get(subject_id)["books"]


def test_new_books_are_appended(subject_id):
    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell"))
    subjects.upsert_book(subject_id, _book("raven.pdf", "Raven"))
    assert [b["filename"] for b in _books(subject_id)] == ["campbell.pdf", "raven.pdf"]


def test_reupload_replaces_instead_of_duplicating(subject_id):
    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell", chunks=2))
    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell", chunks=5))
    books = _books(subject_id)
    assert len(books) == 1, "re-upload added a duplicate entry"
    assert books[0]["chunks"] == 5, "registry kept the stale ingestion result"


def test_reupload_keeps_position(subject_id):
    for f, t in [("a.pdf", "A"), ("b.pdf", "B"), ("c.pdf", "C")]:
        subjects.upsert_book(subject_id, _book(f, t))
    subjects.upsert_book(subject_id, _book("b.pdf", "B v2"))
    assert [b["filename"] for b in _books(subject_id)] == ["a.pdf", "b.pdf", "c.pdf"]
    assert _books(subject_id)[1]["title"] == "B v2"


def test_reupload_preserves_added_at_and_stamps_updated_at(subject_id):
    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell"))
    first_added = _books(subject_id)[0]["added_at"]
    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell"))
    entry = _books(subject_id)[0]
    assert entry["added_at"] == first_added
    assert "updated_at" in entry


def test_first_upload_has_no_updated_at(subject_id):
    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell"))
    assert "updated_at" not in _books(subject_id)[0]


def test_collapses_preexisting_duplicates(subject_id):
    # Simulates a registry already corrupted by the old add_book behaviour:
    # three entries for one file, as seen on the real AP Biology subject.
    state = subjects._load()
    state["subjects"][subject_id]["books"] = [
        _book("campbell.pdf", "Campbell"),
        _book("raven.pdf", "Raven"),
        _book("campbell.pdf", "Campbell Biology"),
        _book("campbell.pdf", "Campbell Biology"),
    ]
    subjects._save(state)

    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell", chunks=2))
    books = _books(subject_id)
    assert [b["filename"] for b in books] == ["campbell.pdf", "raven.pdf"]
    assert books[0]["title"] == "Campbell"


def test_other_books_are_untouched(subject_id):
    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell"))
    subjects.upsert_book(subject_id, _book("raven.pdf", "Raven"))
    subjects.upsert_book(subject_id, _book("campbell.pdf", "Campbell v2"))
    raven = [b for b in _books(subject_id) if b["filename"] == "raven.pdf"]
    assert len(raven) == 1 and raven[0]["title"] == "Raven"


def test_unknown_tutor_returns_none():
    assert subjects.upsert_book("nope", _book("campbell.pdf", "Campbell")) is None
