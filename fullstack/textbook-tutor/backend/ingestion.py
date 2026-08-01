"""Modular ingestion: parse -> caption figures -> chunk -> index (per tutor).

Text chunks carry content_type="text". The caption stage (the old `enrich` seam,
now realized) extracts figures from the PDF, captions each with a vision model,
and adds them as content_type="figure_caption" chunks — so diagrams become
retrievable/answerable with no change to retrieval, citations, or the prompt.
"""
import base64
from io import BytesIO

import anthropic
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

from . import config, store

_META_KEYS = ["tutor_id", "source", "display_title", "page", "content_type"]

if config.USE_GATEWAY:
    _client = anthropic.Anthropic(api_key=config.RESPAN_API_KEY, base_url=config.RESPAN_GATEWAY_URL)
else:
    _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

_CAPTION_PROMPT = (
    "This image is a figure from a textbook. In 1-3 sentences, describe what it "
    "depicts — include any title, axis labels, or terms visible in it — so that a "
    "student's question could retrieve it. If the image is decorative, a logo, or "
    "has no meaningful instructional content, reply with exactly: NONE"
)


def _parse(path):
    """Parse a PDF into one Document per page (layout-aware if LlamaParse is set)."""
    if config.LLAMA_CLOUD_API_KEY:
        from llama_parse import LlamaParse

        parser = LlamaParse(api_key=config.LLAMA_CLOUD_API_KEY, result_type="markdown", split_by_page=True)
        parsed = parser.load_data(str(path))
        return [
            Document(text=d.text, metadata={"page": d.metadata.get("page") or i + 1, "content_type": "text"})
            for i, d in enumerate(parsed)
        ]

    raw = SimpleDirectoryReader(input_files=[str(path)]).load_data()
    return [
        Document(text=d.text, metadata={"page": d.metadata.get("page_label", "?"), "content_type": "text"})
        for d in raw
    ]


def _caption_one(png_b64: str) -> str:
    kwargs = dict(
        model=config.CAPTION_MODEL,
        max_tokens=220,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": png_b64}},
            {"type": "text", "text": _CAPTION_PROMPT},
        ]}],
    )
    if config.USE_GATEWAY:
        kwargs["metadata"] = {"respan_params": {"metadata": {"app": "textbook-tutor", "kind": "caption"}}}
    resp = _client.messages.create(**kwargs)
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def _caption_figures(path) -> list[Document]:
    """Extract raster figures from the PDF and caption each with a vision model."""
    docs = []
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
    except Exception:
        return docs
    for pnum, page in enumerate(reader.pages, 1):
        try:
            images = list(page.images)
        except Exception:
            continue
        for img in images:
            try:
                pil = img.image
                if pil.width < 60 or pil.height < 60:  # skip icons / bullets / rules
                    continue
                buf = BytesIO()
                pil.convert("RGB").save(buf, format="PNG")
                caption = _caption_one(base64.standard_b64encode(buf.getvalue()).decode())
            except Exception:
                continue
            if caption and caption.strip().upper() != "NONE":
                docs.append(Document(
                    text=f"Figure (page {pnum}): {caption}",
                    metadata={"page": pnum, "content_type": "figure_caption"},
                ))
    return docs


def ingest(path, tutor_id: str, title: str) -> dict:
    """Run the full pipeline for one PDF and add it to a tutor's collection."""
    text_docs = _parse(path)
    fig_docs = _caption_figures(path) if config.CAPTION_IMAGES else []
    docs = text_docs + fig_docs
    for d in docs:
        d.metadata["tutor_id"] = tutor_id
        d.metadata["source"] = path.name
        d.metadata["display_title"] = title
        d.metadata.setdefault("content_type", "text")
        d.excluded_embed_metadata_keys = _META_KEYS
        d.excluded_llm_metadata_keys = _META_KEYS

    splitter = SentenceSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    nodes = splitter.get_nodes_from_documents(docs)
    store.get_index(tutor_id).insert_nodes(nodes)
    # The book's chunks just changed; drop any stale BM25 index for it so hybrid
    # search rebuilds from what was actually indexed.
    store.invalidate_keyword_cache(tutor_id, path.name)
    return {"pages": len(text_docs), "chunks": len(nodes), "figures": len(fig_docs)}
