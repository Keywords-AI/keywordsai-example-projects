"""Per-tutor vector store. Each tutor gets its own Chroma collection so a query
to one tutor can never retrieve another tutor's chunks.

LlamaIndex is used only for the RAG machinery (embedding, storage, retrieval);
generation happens directly via the Anthropic SDK in rag.py.
"""
import re

import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from . import config

_client = None
_indexes: dict[str, VectorStoreIndex] = {}
# BM25 is built from a book's chunks and reused across queries. Keyed by
# (tutor_id, filename) so re-ingesting or deleting one book invalidates only it.
_bm25_cache: dict[tuple[str, str], tuple] = {}


def init_settings() -> None:
    """Configure global LlamaIndex settings. Call once at startup."""
    Settings.embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
    Settings.llm = None  # generation is done via the Anthropic SDK, not LlamaIndex
    Settings.node_parser = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )


def _chroma() -> "chromadb.ClientAPI":
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return _client


def collection_name(tutor_id: str) -> str:
    return f"tutor_{tutor_id}"


def get_index(tutor_id: str) -> VectorStoreIndex:
    """Return the persistent index for one tutor, building the handle on first use."""
    if tutor_id not in _indexes:
        collection = _chroma().get_or_create_collection(
            collection_name(tutor_id),
            metadata={"hnsw:space": "cosine"},
        )
        vector_store = ChromaVectorStore(chroma_collection=collection)
        _indexes[tutor_id] = VectorStoreIndex.from_vector_store(vector_store)
    return _indexes[tutor_id]


def neighbours(tutor_id: str, wanted: dict[str, set[str]], window: int) -> list:
    """Chunks that sit next to `wanted` in reading order, as retrievable nodes.

    `wanted` maps a book filename to the node ids retrieved from it. For each
    hit this returns the chunks `window` positions either side, so a lecture can
    be built from a continuous run of the book rather than a scatter of
    best-matching fragments.

    Reading order, not page arithmetic: page metadata is a mix of ints and
    strings ('i', 'ii', 'C1' for front matter), so `page + 1` is not defined.
    Chroma returns a collection in insertion order, and chunks are inserted
    sequentially per document, so position in that list IS reading order.

    Returns (extra_nodes, positions). `extra_nodes` are NodeWithScore with
    `score=None`, because they are context rather than matches and scoring them
    would misrepresent why they are here. `positions` maps node id to position
    in the book for the hits *and* the neighbours, so the caller can order the
    merged set as the book reads.
    """
    from llama_index.core.schema import NodeWithScore, TextNode

    collection = _chroma().get_or_create_collection(collection_name(tutor_id))
    picked: list = []
    positions: dict[str, int] = {}
    for source, hit_ids in wanted.items():
        got = collection.get(where={"source": source}, include=["documents", "metadatas"])
        ids = got.get("ids") or []
        by_id = {i: n for n, i in enumerate(ids)}
        take: set[int] = set()
        for hid in hit_ids:
            pos = by_id.get(hid)
            if pos is None:
                continue
            for off in range(-window, window + 1):
                if 0 <= pos + off < len(ids):
                    take.add(pos + off)
        for pos in sorted(take):                    # sorted = reading order
            positions[ids[pos]] = pos
            if ids[pos] in hit_ids:
                continue                            # already retrieved
            meta = dict((got["metadatas"] or [{}] * len(ids))[pos] or {})
            meta.pop("_node_content", None)         # LlamaIndex bookkeeping
            meta.pop("_node_type", None)
            picked.append(NodeWithScore(
                node=TextNode(id_=ids[pos], text=(got["documents"] or [""] * len(ids))[pos] or "",
                              metadata=meta),
                score=None))
    return picked, positions


def _tokenize(text: str) -> list[str]:
    r"""Lowercase word tokens, Unicode-aware so Greek letters (λ, μ) survive.

    BM25's whole value here is literal matching of terms dense embeddings blur:
    "injective", "invertible", theorem numbers, single-letter operators. `\w+`
    under Unicode keeps λ and μ as tokens; it drops bare symbols like ∈, which
    carry no lexical signal on their own anyway.
    """
    return re.findall(r"\w+", (text or "").lower(), re.UNICODE)


def _build_bm25(tutor_id: str, filename: str):
    """(nodes, BM25Okapi) for one book, built from its chunks in reading order."""
    from rank_bm25 import BM25Okapi
    from llama_index.core.schema import TextNode

    collection = _chroma().get_or_create_collection(collection_name(tutor_id))
    got = collection.get(where={"source": filename}, include=["documents", "metadatas"])
    ids = got.get("ids") or []
    nodes, corpus = [], []
    for i, nid in enumerate(ids):
        text = (got["documents"] or [""] * len(ids))[i] or ""
        meta = dict((got["metadatas"] or [{}] * len(ids))[i] or {})
        meta.pop("_node_content", None)
        meta.pop("_node_type", None)
        nodes.append(TextNode(id_=nid, text=text, metadata=meta))
        corpus.append(_tokenize(text))
    bm25 = BM25Okapi(corpus) if corpus else None
    return nodes, bm25


def keyword_hits(tutor_id: str, filename: str, query: str, top_n: int) -> list:
    """Top-`top_n` BM25 matches for one book, as scored NodeWithScore.

    Returns only positive-score hits (BM25 gives 0 to chunks sharing no query
    term), so a query with no lexical overlap contributes nothing to fusion
    rather than padding it with noise.
    """
    from llama_index.core.schema import NodeWithScore

    key = (tutor_id, filename)
    if key not in _bm25_cache:
        _bm25_cache[key] = _build_bm25(tutor_id, filename)
    nodes, bm25 = _bm25_cache[key]
    if not bm25:
        return []
    scores = bm25.get_scores(_tokenize(query))
    ranked = sorted(range(len(nodes)), key=lambda i: scores[i], reverse=True)
    out = []
    for i in ranked[:top_n]:
        if scores[i] <= 0:
            break
        out.append(NodeWithScore(node=nodes[i], score=float(scores[i])))
    return out


_reranker = None


def _get_reranker():
    """The cross-encoder, loaded once and reused. Import-local so the model (and
    its download) is only touched when reranking is actually turned on."""
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder(config.RERANK_MODEL, max_length=512)
    return _reranker


def _ranked_by_scores(nodes: list, scores: list, top_n: int) -> list:
    """Reorder `nodes` by paired `scores` (desc), set each node's score, keep top_n.

    Pure and model-free so the rerank ordering is unit tested without loading a
    cross-encoder. The score is overwritten with the cross-encoder's, which is a
    better cross-book relevance signal than cosine for the downstream merge."""
    paired = sorted(zip(nodes, scores), key=lambda ns: ns[1], reverse=True)
    out = []
    for nw, sc in paired[:top_n]:
        nw.score = float(sc)
        out.append(nw)
    return out


def rerank(query: str, nodes: list, top_n: int) -> list:
    """Cross-encoder rerank of `nodes` against `query`, keeping the top_n."""
    if not nodes:
        return []
    scores = _get_reranker().predict([(query, n.node.get_content()) for n in nodes])
    return _ranked_by_scores(nodes, list(scores), top_n)


def invalidate_keyword_cache(tutor_id: str, filename: str | None = None) -> None:
    """Drop cached BM25 indexes so the next query rebuilds from current chunks.

    Called whenever a book's chunks change (ingest, re-ingest, delete). `filename`
    invalidates one book; omit it to clear the whole tutor.
    """
    if filename is not None:
        _bm25_cache.pop((tutor_id, filename), None)
    else:
        for key in [k for k in _bm25_cache if k[0] == tutor_id]:
            _bm25_cache.pop(key, None)


def delete_index(tutor_id: str) -> None:
    """Drop a tutor's collection (used when a tutor is deleted)."""
    try:
        _chroma().delete_collection(collection_name(tutor_id))
    except Exception:
        pass
    _indexes.pop(tutor_id, None)
    invalidate_keyword_cache(tutor_id)


def delete_book(tutor_id: str, filename: str) -> None:
    """Remove all chunks belonging to one book from a tutor's collection."""
    try:
        collection = _chroma().get_or_create_collection(collection_name(tutor_id))
        collection.delete(where={"source": filename})
    except Exception:
        pass
    invalidate_keyword_cache(tutor_id, filename)
