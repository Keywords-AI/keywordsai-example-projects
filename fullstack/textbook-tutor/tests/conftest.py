"""Shared test fixtures.

These tests are deliberately offline: they exercise the pure logic around
retrieval and citation, never the Claude API. `backend.rag` builds an Anthropic
client at import time, so a dummy key is planted before import to keep the suite
runnable in CI without credentials.
"""
import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("RESPAN_API_KEY", "sk-respan-test-not-a-real-key")


class FakeNode:
    """Stands in for a LlamaIndex NodeWithScore.

    Only the surface `rag.py` actually touches: `.score`, `.node.node_id`,
    `.node.metadata`, `.node.get_content()`.
    """

    def __init__(self, node_id, score=0.5, source="book.pdf", page=1,
                 text="some text", content_type="text", display_title=None):
        metadata = {"source": source, "page": page, "content_type": content_type}
        if display_title:
            metadata["display_title"] = display_title
        self.score = score
        self.node = SimpleNamespace(
            node_id=node_id,
            metadata=metadata,
            get_content=lambda: text,
        )


@pytest.fixture
def node():
    return FakeNode


@pytest.fixture
def tutor():
    return {
        "id": "t1",
        "name": "AP Biology",
        "books": [
            {"filename": "campbell.pdf", "title": "Campbell"},
            {"filename": "raven.pdf", "title": "Raven"},
        ],
    }
