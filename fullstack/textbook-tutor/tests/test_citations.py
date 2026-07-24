"""Citation rendering: which title and page an answer is told to cite.

The title comes from the registry at answer time, not from metadata frozen at
ingest, so renaming a book updates citations in answers already on screen.

Whether the citations an answer *emits* are valid is graded on the platform by
the `RAG · citation validity` grader, not here.
"""
from backend.rag import _citations, _title_map, _title_page


def test_title_comes_from_the_registry_not_frozen_metadata(tutor, node):
    # Renaming a book must update citations live, without re-ingesting.
    tm = _title_map(tutor)
    title, page = _title_page(node("n1", source="campbell.pdf", page=7), tm)
    assert (title, page) == ("Campbell", "7")


def test_falls_back_to_display_title_then_source(node):
    n = node("n1", source="unknown.pdf", page=2, display_title="Stale Title")
    assert _title_page(n, {})[0] == "Stale Title"
    n2 = node("n2", source="orphan.pdf", page=2)
    assert _title_page(n2, {})[0] == "orphan.pdf"


def test_citations_are_deduped_by_title_and_page(tutor, node):
    tm = _title_map(tutor)
    nodes = [
        node("a", source="campbell.pdf", page=1),
        node("b", source="campbell.pdf", page=1),   # different chunk, same page
        node("c", source="raven.pdf", page=2),
    ]
    assert _citations(nodes, tm) == ["Campbell, p. 1", "Raven, p. 2"]
